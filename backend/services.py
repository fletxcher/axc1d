"""
AXC1D calculation services.

This module ports the 1D meanline stage-stacking solver from the desktop
application (`desktop/src/python/solver.py`) into a form the FastAPI layer can
call, and adds:

  * `run_analysis`      - full performance sweep, returns the API `AnalysisResults`
  * `compute_meanline_radius`, `compute_specific_heat`, `compute_design_point`
                         - the individual sub-calculations exposed as endpoints
  * `default_config`    - the reference ("origin.axc1d") input deck
  * `validate_config`   - lightweight pre-flight checks

The `Solver` class below is a faithful port of `AXC1DSolver`; the physics is
unchanged. Everything else in this file is glue: unit handling and mapping
between the camelCase API schema and the solver's internal dict contract.
"""

from __future__ import annotations

import logging
import math
import time
from datetime import datetime, timezone
from typing import Any, Dict, List

from models import (
    AnalysisConfig,
    AnalysisResults,
    BleedRow,
    CharacteristicPoint,
    DeviationFactors,
    DesignPointResponse,
    DesignPointStage,
    DesignSummary,
    EfficiencyRatioRow,
    MeanlineRadiusResponse,
    OperatingParameters,
    OperatingPoint,
    SpecificHeatResponse,
    StageCharacteristic,
    StageGeometry,
    StageResult,
    ValidationIssue,
)

logger = logging.getLogger("axc1d.solver")
logger.setLevel(logging.WARNING)  # quiet by default; the sweep is chatty at INFO

# === UNIT CONVERSION FACTORS  (solver is internally US customary) === #
LBM_TO_KG = 0.45359237
FT_TO_M = 0.3048
RANKINE_TO_KELVIN = 5.0 / 9.0
PSF_TO_KPA = 0.047880259  # lbf/ft^2 -> kPa
PSF_TO_PSIA = 1.0 / 144.0

# geometry attribute order == STGSTK column order (RT2 RH2 RT3 RH3 BET2M CB2M
# CB2MR CB3MR RK2M RSOLM SK2M). The solver reads these positionally.
_GEOM_ATTRS = [
    "rotorInletTip",
    "rotorInletHub",
    "rotorOutletTip",
    "rotorOutletHub",
    "inletFlowAngle",
    "bladeResetAbs",
    "bladeResetRel",
    "bladeResetOutlet",
    "rotorMetalAngle",
    "rotorSolidity",
    "statorMetalAngle",
]
_GEOM_VARS = [
    "RT2", "RH2", "RT3", "RH3", "BET2M", "CB2M", "CB2MR", "CB3MR", "RK2M", "RSOLM", "SK2M",
]


# === SOLVER === #


class Solver:
    """Multistage compressor analysis and performance calculation solver."""

    def __init__(self) -> None:
        self.logger = logger

        # === PHYSICAL CONSTANTS === #
        self.ru = 1545.44        # universal gas constant (ft.lbf / lbmol.degR)
        self.pi = 3.14159265358979
        self.g = 32.1740         # gravitational constant (lbm.ft / lbf.s^2)
        self.aj = 778.12         # mechanical equivalent of heat (ft.lbf / BTU)
        self.mole_wt = 28.970
        self.dcp = (self.ru / self.mole_wt) / self.aj

        self.rpmrad = self.pi / 30.0
        self.rad = 57.29578      # degrees per radian

    # === SUB-CALCULATIONS === #

    def cml(self, rotor_tip: float, rotor_hub: float) -> float:
        """RMS (meanline) radius from tip and hub radii."""
        return math.sqrt((rotor_tip ** 2 + rotor_hub ** 2) / 2.0)

    def cpf(self, ts: float, specific_heat_coefficients: List[float]):
        """Specific heat and gamma as functions of temperature (ts in degR)."""
        self.ts = ts
        self.specific_heat = (
            specific_heat_coefficients[0]
            + specific_heat_coefficients[1] * ts
            + specific_heat_coefficients[2] * ts ** 2
            + specific_heat_coefficients[3] * ts ** 3
            + specific_heat_coefficients[4] * ts ** 4
            + specific_heat_coefficients[5] * ts ** 5
        )
        self.gamma = self.specific_heat / (self.specific_heat - self.dcp)
        self.gm1 = self.gamma - 1.0
        self.gf1 = 1.0 / self.gm1
        self.gf2 = self.gamma / self.gm1
        self.gf3 = 1.0 / self.gf2
        return (
            self.ts, self.specific_heat, self.gamma,
            self.gm1, self.gf1, self.gf2, self.gf3,
        )

    def cspref(self):
        """Meanline velocity diagrams and design stage performance."""
        self.phiref = [0.0] * self.nsta
        self.psiref = [0.0] * self.nsta
        self.etaref = [0.0] * self.nsta
        self.cpref = [0.0] * self.nsta
        self.gf1ref = [0.0] * self.nsta
        self.etainp = [0.0] * self.nsta
        self.v3dv2r = [0.0] * self.nsta
        self.rincm = [0.0] * self.nsta
        self.rdfm = [0.0] * self.nsta
        self.sincm = [0.0] * self.nsta

        self.vz2m = [[0.0] * self.nspe for _ in range(self.nsta)]
        self.vz3m = [[0.0] * self.nspe for _ in range(self.nsta)]
        self.flocal = [[0.0] * self.nspe for _ in range(self.nsta)]

        self.dphia = [0.0] * self.nsta
        self.dpsia = [0.0] * self.nsta
        self.deta = [0.0] * self.nsta
        self.dpsis_table = [[0.0] * self.nspe for _ in range(self.nsta)]
        self.db2m = [[0.0] * self.nspe for _ in range(self.nsta)]
        self.db2mr = [[0.0] * self.nspe for _ in range(self.nsta)]
        self.db3m = [[0.0] * self.nspe for _ in range(self.nsta)]
        self.db3mr = [[0.0] * self.nspe for _ in range(self.nsta)]

        for i in range(self.nsta):
            rho2 = self.p0 / (self.rg * self.t0)
            vz2 = self.desflo / (rho2 * self.area2[i])
            self.vz2m[i][0] = vz2

            um2 = self.um2[i]
            um3 = self.um3[i]
            self.phiref[i] = vz2 / um2 if um2 > 0 else 0.0

            b2 = self.bet2m[i][0]
            vt2 = um2 - vz2 * math.tan(b2) if abs(b2) < math.pi / 2 else 0.0
            w2 = math.sqrt(vz2 ** 2 + (um2 - vt2) ** 2)

            b3 = self.cb3mr[i]
            rho3 = rho2
            vz3 = vz2
            dt = 0.0
            t3 = self.t0

            for _ in range(20):
                vz3_new = (
                    self.desflo / (rho3 * self.area3[i]) if self.area3[i] > 0 else vz2
                )
                vt3 = um3 - vz3_new * math.tan(b3) if abs(b3) < math.pi / 2 else 0.0
                work = um3 * vt3 - um2 * vt2
                self.cpf(self.t0, self.specific_heat_coefficients)
                dt_new = work / (self.specific_heat * self.gj) if self.gj > 0 else 0.0
                t3_new = self.t0 + dt_new
                self.cpf(t3_new, self.specific_heat_coefficients)
                pr_approx = (t3_new / self.t0) ** self.gf2 if self.t0 > 0 else 1.0
                pt3 = self.p0 * pr_approx
                rho3 = pt3 / (self.rg * t3_new) if t3_new > 0 else rho2

                if abs(vz3_new - vz3) < 0.01 and abs(dt_new - dt) < 0.1:
                    vz3, dt, t3 = vz3_new, dt_new, t3_new
                    break
                vz3, dt, t3 = vz3_new, dt_new, t3_new

            self.vz3m[i][0] = vz3
            self.psiref[i] = (
                (self.specific_heat * dt * self.gj) / um3 ** 2 if um3 > 0 else 0.0
            )
            self.cpref[i] = self.specific_heat
            self.gf1ref[i] = self.gf1
            self.etaref[i] = (
                self.etades[i][0][0] if self.etades[i][0][0] != 0.0 else 0.85
            )

            beta2_flow = math.atan2(vz2, um2 - vt2)
            self.rincm[i] = (beta2_flow - b2) * self.rad

            vt3 = um3 - vz3 * math.tan(b3) if abs(b3) < math.pi / 2 else 0.0
            w3 = math.sqrt(vz3 ** 2 + (um3 - vt3) ** 2)
            if w2 > 0 and self.rsolm[i] > 0:
                self.rdfm[i] = (
                    1.0 - (w3 / w2) + abs(vt3 - vt2) / (2.0 * w2 * self.rsolm[i])
                )
            else:
                self.rdfm[i] = 0.5

            alpha3_flow = math.atan2(vt3, vz3) if vz3 > 0 else 0.0
            sk2m_rad = self.sk2m[i] / self.rad
            self.sincm[i] = (alpha3_flow - sk2m_rad) * self.rad

            v2 = math.sqrt(vz2 ** 2 + vt2 ** 2)
            v3 = math.sqrt(vz3 ** 2 + vt3 ** 2)
            self.v3dv2r[i] = v3 / v2 if v2 > 0 else 1.0

            self.db2m[i][0] = math.atan2(vt2, vz2)
            self.db2mr[i][0] = math.atan2(vz2, um2 - vt2)
            self.db3m[i][0] = math.atan2(vt3, vz3)
            self.db3mr[i][0] = math.atan2(vz3, um3 - vt3)
            self.flocal[i][0] = self.desflo

        return (
            self.phiref, self.psiref, self.etaref, self.cpref, self.gf1ref,
        )

    def cseta(self):
        """Stage adiabatic efficiency curve vs. flow coefficient."""
        phi_stall_fraction = 0.6
        phi_choke_fraction = 1.4
        for i in range(self.nsta):
            phi_d = self.phiref[i]
            eta_d = self.etaref[i]
            phi_s = phi_d * phi_stall_fraction
            phi_c = phi_d * phi_choke_fraction
            eta_s = 0.9 * eta_d
            eta_c = 0.8 * eta_d
            for j in range(self.nspe):
                for k in range(self.npts):
                    if self.etades[i][j][k] != 0.0:
                        continue
                    phi = self.phides[i][j][k]
                    if phi <= phi_d:
                        if phi_d > phi_s:
                            xx = min(1.0, max(0.0, (phi_d - phi) / (phi_d - phi_s)))
                            eta = eta_d - (eta_d - eta_s) * xx ** 2
                        else:
                            eta = eta_d
                    else:
                        if phi_c > phi_d:
                            xx = min(1.0, max(0.0, (phi - phi_d) / (phi_c - phi_d)))
                            eta = eta_d - (eta_d - eta_c) * xx ** 2
                        else:
                            eta = eta_d
                    self.etades[i][j][k] = max(0.0, eta)
        return self.etades

    def cspsi(self):
        """Stage pressure coefficient curve vs. flow coefficient."""
        for i in range(self.nsta):
            phi_d = self.phiref[i]
            psi_d = self.psiref[i]
            b2md = self.bet2m[i][0]
            b3md = self.cb3mr[i]
            for j in range(self.nspe):
                for k in range(self.npts):
                    if self.psides[i][j][k] != 0.0:
                        continue
                    phi = self.phides[i][j][k]
                    if phi < 0.001:
                        self.psides[i][j][k] = 0.0
                        continue
                    vz2m = (
                        self.vz2m[i][0] * (phi / phi_d) if phi_d > 0 else self.vz2m[i][0]
                    )
                    rho2 = self.p0 / (self.rg * self.t0)
                    w2 = rho2 * self.area2[i] * vz2m
                    b3m = b3md
                    t = self.t0 + 10.0
                    dt = 0.0
                    for _ in range(10):
                        rho3 = rho2 * 1.05
                        vz3m = w2 / (rho3 * self.area3[i]) if self.area3[i] > 0 else vz2m
                        if self.drdevp == 1.0:
                            phi_ratio = phi / phi_d if phi_d > 0 else 1.0
                            b3m = b3md + 0.05 * (phi_ratio - 1.0)
                        tan_b3m = math.tan(b3m) if abs(b3m) < math.pi / 2 else 0.0
                        tan_b2m = math.tan(b2md) if abs(b2md) < math.pi / 2 else 0.0
                        vt3m = self.um3[i] - vz3m * tan_b3m
                        vt2m = self.um2[i] - vz2m * tan_b2m
                        work = self.um3[i] * vt3m - self.um2[i] * vt2m
                        cp_current = self.cpref[i]
                        dt = work / (cp_current * self.gj) if cp_current > 0 else work / self.gj
                        t3 = self.t0 + dt
                        self.cpf(t3, self.specific_heat_coefficients)
                        if abs(t3 - t) < 0.1:
                            break
                        t = t3
                    psi = (
                        (self.specific_heat * dt) / (self.um3[i] ** 2)
                        if self.um3[i] > 0 else psi_d
                    )
                    psi = max(0.0, min(1.0, psi))
                    self.psides[i][j][k] = psi if psi > 0.01 else psi_d * 0.5
        return self.psides

    def cspsd(self):
        """Adjust pressure coefficient for off-design rotative speeds."""
        for i in range(self.nsta):
            phi_d = self.phiref[i]
            psi_d = self.psiref[i]
            b2md = self.bet2m[i][0]
            b3md = self.cb3mr[i]
            for j in range(self.nspe):
                pctspd = (
                    self.efficiency_ratio_table[j][0]
                    if j < len(self.efficiency_ratio_table) else 1.0
                )
                if abs(pctspd - 1.0) < 0.01:
                    self.dpsis_table[i][j] = 0.0
                    continue
                um2_od = self.um2[i] * pctspd
                um3_od = self.um3[i] * pctspd
                vz2m = phi_d * um2_od
                rho2 = self.p0 / (self.rg * self.t0)
                w2 = rho2 * self.area2[i] * vz2m
                b3m = b3md
                t = self.t0 + 10.0
                dt = 0.0
                for _ in range(10):
                    rho3 = rho2 * 1.05
                    vz3m = w2 / (rho3 * self.area3[i]) if self.area3[i] > 0 else vz2m
                    if self.drdevn == 1.0:
                        b3m = b3md + 0.05 * (pctspd - 1.0)
                    tan_b3m = math.tan(b3m) if abs(b3m) < math.pi / 2 else 0.0
                    tan_b2m = math.tan(b2md) if abs(b2md) < math.pi / 2 else 0.0
                    vt3m = um3_od - vz3m * tan_b3m
                    vt2m = um2_od - vz2m * tan_b2m
                    work = um3_od * vt3m - um2_od * vt2m
                    cp_current = self.cpref[i]
                    dt = (
                        (pctspd * work) / (cp_current * self.gj)
                        if cp_current > 0 else (pctspd * work) / self.gj
                    )
                    t3 = self.t0 + dt
                    self.cpf(t3, self.specific_heat_coefficients)
                    if abs(t3 - t) < 0.1:
                        break
                    t = t3
                psi_od = (
                    (self.specific_heat * dt) / (um3_od ** 2) if um3_od > 0 else 0.0
                )
                self.dpsis_table[i][j] = psi_od - psi_d
        return self.dpsis_table

    def cspan(self):
        """Alter stage characteristics for blade setting angle changes."""
        self.dphia = [0.0] * self.nsta
        self.dpsia = [0.0] * self.nsta
        self.deta = [0.0] * self.nsta
        for i in range(self.nsta):
            cb2m = self.cb2m[i]
            cb2mr = self.cb2mr[i]
            cb3mr = self.cb3mr[i]
            if abs(cb2m) < 1e-10 and abs(cb2mr) < 1e-10 and abs(cb3mr) < 1e-10:
                continue
            b2md = self.bet2m[i][0]
            phi_d = self.phiref[i]
            psi_d = self.psiref[i]
            ab2m = cb2m + cb2mr
            b2m_new = b2md + ab2m
            b3m_new = b2md + cb3mr
            tan_b2md = math.tan(b2md) if abs(b2md) < math.pi / 2 else 0.0
            tan_b2m_new = math.tan(b2m_new) if abs(b2m_new) < math.pi / 2 else 0.0
            denom = tan_b2md + tan_b2m_new
            vz2m_new = (
                self.um2[i] / denom if abs(denom) > 1e-10 else self.vz2m[i][0]
            )
            phi_new = vz2m_new / self.um2[i] if self.um2[i] > 0 else phi_d
            dphia_i = phi_new - phi_d
            rho2 = self.p0 / (self.rg * self.t0)
            w2 = rho2 * self.area2[i] * vz2m_new
            b3m = b3m_new
            t = self.t0 + 10.0
            dt = 0.0
            for _ in range(10):
                rho3 = rho2 * 1.05
                vz3m = w2 / (rho3 * self.area3[i]) if self.area3[i] > 0 else vz2m_new
                if self.drdevg == 1.0:
                    b3m = b3m_new + 0.02 * (ab2m + cb3mr)
                tan_b2m = math.tan(b2m_new) if abs(b2m_new) < math.pi / 2 else 0.0
                tan_b3m = math.tan(b3m) if abs(b3m) < math.pi / 2 else 0.0
                vt2m = self.um2[i] - vz2m_new * tan_b2m
                vt3m = self.um3[i] - vz3m * tan_b3m
                work = self.um3[i] * vt3m - self.um2[i] * vt2m
                cp_current = self.cpref[i]
                dt = (
                    work / (cp_current * self.gj)
                    if cp_current > 0 else work / self.gj if self.gj > 0 else 0.0
                )
                t3 = self.t0 + dt
                self.cpf(t3, self.specific_heat_coefficients)
                if abs(t3 - t) < 0.1:
                    break
                t = t3
            if self.um3[i] > 0:
                self.dpsia[i] = ((self.specific_heat * dt) / (self.um3[i] ** 2)) - psi_d
            self.dphia[i] = dphia_i
            self.deta[i] = 0.0
        return self.dphia, self.dpsia, self.deta

    def csoupt(self):
        """Stage and cumulative compressor performance across the sweep."""
        self.sweep_results: List[Dict[str, Any]] = []
        for j in range(self.nspe):
            pctspd = self.efficiency_ratio_table[j][0]
            etarat = self.efficiency_ratio_table[j][1]
            for k in range(self.npts):
                op: Dict[str, Any] = {
                    "speed": pctspd,
                    "eta_ratio": etarat,
                    "flow_point": k,
                    "stages": [],
                }
                tt_inlet = self.t0
                pt_inlet = self.p0
                stall_choke = False

                for i in range(self.nsta):
                    um2_c = self.um2[i] * pctspd
                    um3_c = self.um3[i] * pctspd
                    phi = self.phi_[i][j][k]
                    psi = self.psi_[i][j][k]
                    eta_stage = self.eta_[i][j][k]
                    vz2m = phi * um2_c
                    rho2 = pt_inlet / (self.rg * tt_inlet) if self.rg > 0 else 0.0
                    w2 = rho2 * self.area2[i] * vz2m

                    phi_map = [
                        self.phi_[i][j][kk] for kk in range(self.npts)
                        if self.phi_[i][j][kk] > 0.0
                    ]
                    if phi_map:
                        phi_min = min(phi_map) * 0.98
                        phi_max = max(phi_map) * 1.02
                    else:
                        phi_d_scaled = (
                            self.phiref[i] * pctspd if self.spdphi == 1.0 else self.phiref[i]
                        )
                        phi_min = phi_d_scaled * 0.6
                        phi_max = phi_d_scaled * 1.4
                    if phi < phi_min or phi > phi_max:
                        stall_choke = True

                    t_outlet = tt_inlet + 20.0
                    for _ in range(10):
                        self.cpf(t_outlet, self.specific_heat_coefficients)
                        if self.specific_heat > 0 and self.gj > 0:
                            dt_is = (psi * um3_c ** 2) / (self.specific_heat * self.gj)
                        else:
                            dt_is = 0.0
                        dt_actual = dt_is / eta_stage if eta_stage > 0 else dt_is
                        t_new = tt_inlet + dt_actual
                        if abs(t_new - t_outlet) < 0.1:
                            break
                        t_outlet = t_new
                    self.cpf(t_outlet, self.specific_heat_coefficients)

                    if t_outlet > 0 and tt_inlet > 0:
                        temp_ratio = t_outlet / tt_inlet
                        press_ratio = temp_ratio ** self.gf2 if self.gf2 > 0 else 1.0
                    else:
                        temp_ratio = press_ratio = 1.0
                    pt_outlet = pt_inlet * press_ratio

                    rho3 = pt_outlet / (self.rg * t_outlet) if self.rg > 0 else 0.0
                    vz3m = w2 / (rho3 * self.area3[i]) if self.area3[i] > 0 else vz2m
                    b3m = self.cb3mr[i]
                    tan_b3m = math.tan(b3m) if abs(b3m) < math.pi / 2 else 0.0
                    vt3m = um3_c - vz3m * tan_b3m

                    beta2m_rad = self.bet2m[i][0]
                    tan_b2m = math.tan(beta2m_rad) if abs(beta2m_rad) < math.pi / 2 else 0.0
                    incidence_rotor = (
                        (math.atan(vz2m / um2_c) - beta2m_rad) * self.rad
                        if um2_c > 0 else 0.0
                    )
                    vt2m_df = um2_c - vz2m * tan_b2m
                    vr2 = math.sqrt(vz2m ** 2 + (um2_c - vt2m_df) ** 2)
                    vr3 = math.sqrt(vz3m ** 2 + (um3_c - vt3m) ** 2)
                    if vr2 > 0 and self.rsolm[i] > 0:
                        df = 1.0 - (vr3 / vr2) + abs(vt3m - vt2m_df) / (2.0 * vr2 * self.rsolm[i])
                    else:
                        df = 0.5

                    op["stages"].append({
                        "stage": i + 1,
                        "mass_flow": w2,
                        "phi": phi,
                        "psi": psi,
                        "eta": eta_stage,
                        "pr": press_ratio,
                        "tr": temp_ratio,
                        "tt_inlet": tt_inlet,
                        "tt_outlet": t_outlet,
                        "pt_inlet": pt_inlet,
                        "pt_outlet": pt_outlet,
                        "vz2m": vz2m,
                        "vz3m": vz3m,
                        "um2": um2_c,
                        "um3": um3_c,
                        "vt2m": vt2m_df,
                        "vt3m": vt3m,
                        "incidence": incidence_rotor,
                        "diffusion_factor": df,
                    })
                    tt_inlet, pt_inlet = t_outlet, pt_outlet

                if not stall_choke:
                    pr_overall = pt_inlet / self.p0 if self.p0 > 0 else 1.0
                    tr_overall = tt_inlet / self.t0 if self.t0 > 0 else 1.0
                    if tr_overall > 1.0:
                        tr_is = pr_overall ** self.gf3 if self.gf3 > 0 else tr_overall
                        eta_overall = (
                            (tr_is - 1.0) / (tr_overall - 1.0)
                            if (tr_overall - 1.0) > 1e-10 else 1.0
                        )
                    else:
                        eta_overall = 1.0
                    op["pr_overall"] = pr_overall
                    op["tr_overall"] = tr_overall
                    op["eta_overall"] = max(0.0, min(1.0, eta_overall))
                else:
                    op["pr_overall"] = 0.0
                    op["tr_overall"] = 0.0
                    op["eta_overall"] = 0.0

                self.sweep_results.append(op)

        return self.sweep_results

    # === PIPELINE === #

    def run(self, config: dict) -> List[Dict[str, Any]]:
        """Execute the compressor analysis pipeline. Returns `sweep_results`."""
        ip = list(dict(config["SI Input Parameters"]).values())
        df = list(dict(config["Deviation Factors"]).values())
        self.specific_heat_coefficients = list(
            dict(config["Specific Heat Coefficients"]).values()
        )

        self.nsta = int(ip[0])
        self.nspe = int(ip[1])
        self.p0 = ip[2]
        self.t0 = ip[3]
        self.npts = int(ip[4])
        self.desrpm = ip[6]
        self.desflo = ip[7]

        self.spdpsi = df[0]
        self.spdphi = df[1]
        self.drdevg = df[2]
        self.drdevn = df[3]
        self.drdevp = df[4]
        self.units = df[5]

        mole_wt = ip[5]
        self.rg = self.ru / mole_wt
        self.dcp = self.rg / self.aj
        self.gj = self.g * self.aj
        self.g2j = self.gj * 2.0

        self.cpf(self.t0, self.specific_heat_coefficients)

        if self.units == 1.0:
            self.p0 = self.p0 / 0.689476
            self.t0 = self.t0 * 9.0 / 5.0
            self.desflo = self.desflo / 0.453592
        self.p0 = self.p0 * 144.0

        stage_geometry_ = dict(config["Stage Geometry"])
        self.stage_geometry = []
        for stage_idx in range(1, self.nsta + 1):
            prefix = f"STAGE_{stage_idx}_"
            stage_vals = [v for k, v in stage_geometry_.items() if k.startswith(prefix)]
            self.stage_geometry.append([stage_idx] + stage_vals)

        if self.units == 1.0:
            for i in range(self.nsta):
                for col in (1, 2, 3, 4):
                    self.stage_geometry[i][col] /= 2.54

        self.bleed_table = []
        for row in config["Bleed Table"]:
            bleed_row = [row["PCTSPD"]] + list(row["stage_values"])
            if self.units == 1.0:
                bleed_row = [bleed_row[0]] + [v / 0.453592 for v in bleed_row[1:]]
            self.bleed_table.append(bleed_row)

        self.efficiency_ratio_table = [
            [row["PCTSPD"], row["ETARAT"]] for row in config["Efficiency Ratio Table"]
        ]

        self.phides = [[[0.0] * self.npts for _ in range(self.nspe)] for _ in range(self.nsta)]
        self.psides = [[[0.0] * self.npts for _ in range(self.nspe)] for _ in range(self.nsta)]
        self.etades = [[[0.0] * self.npts for _ in range(self.nspe)] for _ in range(self.nsta)]
        for i, stg in enumerate(config["Input Design Characteristics"]):
            for k, pt in enumerate(stg["points"]):
                self.phides[i][0][k] = pt["phi"]
                self.psides[i][0][k] = pt["psi"]
                self.etades[i][0][k] = pt["eta"]

        self.area2 = [0.0] * self.nsta
        self.area3 = [0.0] * self.nsta
        self.rm2 = [0.0] * self.nsta
        self.rm3 = [0.0] * self.nsta
        self.ut2 = [0.0] * self.nsta
        self.ut3 = [0.0] * self.nsta
        self.um2 = [0.0] * self.nsta
        self.um3 = [0.0] * self.nsta
        self.rsolm = [0.0] * self.nsta
        self.rk2m = [0.0] * self.nsta
        self.sk2m = [0.0] * self.nsta
        self.cb2m = [0.0] * self.nsta
        self.cb2mr = [0.0] * self.nsta
        self.cb3mr = [0.0] * self.nsta
        self.bet2m = [[0.0] * self.nspe for _ in range(self.nsta)]

        for i in range(self.nsta):
            sg = self.stage_geometry[i]
            rt2, rh2, rt3, rh3 = sg[1], sg[2], sg[3], sg[4]
            self.area2[i] = self.pi * (rt2 ** 2 - rh2 ** 2) / 144.0
            self.area3[i] = self.pi * (rt3 ** 2 - rh3 ** 2) / 144.0
            self.rm2[i] = self.cml(rotor_tip=rt2, rotor_hub=rh2)
            self.rm3[i] = self.cml(rotor_tip=rt3, rotor_hub=rh3)
            omega = self.desrpm * self.pi / 30.0
            self.ut2[i] = (rt2 / 12.0) * omega
            self.ut3[i] = (rt3 / 12.0) * omega
            self.um2[i] = (self.rm2[i] / 12.0) * omega
            self.um3[i] = (self.rm3[i] / 12.0) * omega
            self.bet2m[i][0] = sg[5] / self.rad
            self.cb2m[i] = sg[6] / self.rad
            self.cb2mr[i] = sg[7] / self.rad
            self.cb3mr[i] = sg[8] / self.rad
            self.rk2m[i] = sg[9] + sg[7]
            self.rsolm[i] = sg[10]
            if i + 1 < self.nsta:
                self.sk2m[i] = sg[11] + self.stage_geometry[i + 1][6]
            else:
                self.sk2m[i] = sg[11]

        self.cspref()

        for i in range(self.nsta):
            for j in range(1, self.nspe):
                for k in range(self.npts):
                    if self.phides[i][j][k] == 0.0:
                        self.phides[i][j][k] = self.phides[i][0][k]

        if self.etades[0][0][0] == 0.0:
            self.cseta()
        if self.psides[0][0][0] == 0.0:
            self.cspsi()
        if self.spdpsi == 1.0:
            self.cspsd()
        self.cspan()

        self.phi_ = [[[0.0] * self.npts for _ in range(self.nspe)] for _ in range(self.nsta)]
        self.psi_ = [[[0.0] * self.npts for _ in range(self.nspe)] for _ in range(self.nsta)]
        self.eta_ = [[[0.0] * self.npts for _ in range(self.nspe)] for _ in range(self.nsta)]
        for i in range(self.nsta):
            for j in range(self.nspe):
                pctspd = self.efficiency_ratio_table[j][0]
                etarat = self.efficiency_ratio_table[j][1]
                for k in range(self.npts):
                    phi = self.phides[i][0][k] + self.dphia[i]
                    if self.spdphi == 1.0 and pctspd != 0.0:
                        phi = phi * pctspd
                    dpsis_ij = self.dpsis_table[i][j] if self.dpsis_table else 0.0
                    self.phi_[i][j][k] = phi
                    self.psi_[i][j][k] = self.psides[i][0][k] + self.dpsia[i] + dpsis_ij
                    self.eta_[i][j][k] = self.etades[i][0][k] * etarat + self.deta[i]

        return self.csoupt()


# === ADAPTERS: API SCHEMA <-> SOLVER DICT === #


def api_config_to_solver_dict(cfg: AnalysisConfig) -> dict:
    """Map the camelCase API deck to the solver's positional dict contract."""
    p = cfg.parameters
    d = cfg.deviationFactors

    si = {
        "STAGES": float(p.stages),
        "SPEEDS": float(p.speeds),
        "P_0_IN": p.inletPressure,
        "T_0_IN": p.inletTemperature,
        "POINTS": float(p.pointsPerCurve),
        "MOLE_WT": p.molecularWeight,
        "RPM": p.rpm,
        "MASS_FLOW": p.massFlow,
    }
    dev = {
        "SPDPSI": 1.0 if d.speedPsi else 0.0,
        "SPDPHI": 1.0 if d.speedPhi else 0.0,
        "DRDEVG": 1.0 if d.deviationBladeReset else 0.0,
        "DRDEVN": 1.0 if d.deviationSpeed else 0.0,
        "DRDEVP": 1.0 if d.deviationFlow else 0.0,
        "UNITS": 1.0 if d.siUnits else 0.0,
    }
    cp = {f"CPCO_{i + 1}": c for i, c in enumerate(cfg.gasCoefficients)}

    geom: Dict[str, float] = {}
    for idx, g in enumerate(cfg.stageGeometry, start=1):
        for attr, var in zip(_GEOM_ATTRS, _GEOM_VARS):
            geom[f"STAGE_{idx}_{var}"] = float(getattr(g, attr))

    bleed = [
        {"PCTSPD": r.speedFraction, "stage_values": list(r.stageBleed)}
        for r in cfg.bleedTable
    ]
    eff = [
        {"PCTSPD": r.speedFraction, "ETARAT": r.efficiencyRatio}
        for r in cfg.efficiencyRatioTable
    ]
    chars = [
        {"points": [{"phi": pt.phi, "psi": pt.psi, "eta": pt.eta} for pt in c.points]}
        for c in cfg.characteristics
    ]

    return {
        "SI Input Parameters": si,
        "Deviation Factors": dev,
        "Specific Heat Coefficients": cp,
        "Stage Geometry": geom,
        "Bleed Table": bleed,
        "Efficiency Ratio Table": eff,
        "Input Design Characteristics": chars,
    }


def _unit_converters(si: bool):
    """Return (flow, temp, pressure, velocity) converters solver -> output units."""
    if si:
        return (
            lambda w: w * LBM_TO_KG,
            lambda t: t * RANKINE_TO_KELVIN,
            lambda p: p * PSF_TO_KPA,
            lambda v: v * FT_TO_M,
        )
    # US customary: keep lbm/s, degR, ft/s; report pressure in psia not lbf/ft^2
    return (lambda w: w, lambda t: t, lambda p: p * PSF_TO_PSIA, lambda v: v)


def _map_sweep_to_results(
    sweep: List[Dict[str, Any]], cfg: AnalysisConfig, runtime_ms: int
) -> AnalysisResults:
    si = cfg.deviationFactors.siUnits
    conv_w, conv_t, conv_p, conv_v = _unit_converters(si)

    points: List[OperatingPoint] = []
    for op in sweep:
        stalled = op["pr_overall"] == 0.0
        stage_results = [
            StageResult(
                stage=s["stage"],
                massFlow=conv_w(s["mass_flow"]),
                phi=s["phi"],
                psi=s["psi"],
                eta=s["eta"],
                pressureRatio=s["pr"],
                temperatureRatio=s["tr"],
                inletTotalTemperature=conv_t(s["tt_inlet"]),
                outletTotalTemperature=conv_t(s["tt_outlet"]),
                inletTotalPressure=conv_p(s["pt_inlet"]),
                outletTotalPressure=conv_p(s["pt_outlet"]),
                axialVelocityInlet=conv_v(s["vz2m"]),
                axialVelocityOutlet=conv_v(s["vz3m"]),
                bladeSpeedInlet=conv_v(s["um2"]),
                bladeSpeedOutlet=conv_v(s["um3"]),
                swirlVelocityInlet=conv_v(s["vt2m"]),
                swirlVelocityOutlet=conv_v(s["vt3m"]),
                incidence=s["incidence"],
                diffusionFactor=s["diffusion_factor"],
            )
            for s in op["stages"]
        ]
        corrected_flow = conv_w(op["stages"][0]["mass_flow"]) if op["stages"] else 0.0
        points.append(
            OperatingPoint(
                speedFraction=op["speed"],
                efficiencyRatio=op["eta_ratio"],
                flowPointIndex=op["flow_point"],
                correctedMassFlow=corrected_flow,
                stages=stage_results,
                overallPressureRatio=op["pr_overall"],
                overallTemperatureRatio=op["tr_overall"],
                overallEfficiency=op["eta_overall"],
                stalled=stalled,
            )
        )

    speeds = sorted({p.speedFraction for p in points}, reverse=True)
    design = _design_summary(points, cfg.parameters.stages)

    return AnalysisResults(
        stub=False,
        generatedAt=datetime.now(timezone.utc).isoformat(),
        runtimeMs=runtime_ms,
        units="SI" if si else "US",
        speeds=speeds,
        operatingPoints=points,
        design=design,
    )


def _design_summary(points: List[OperatingPoint], stages: int) -> DesignSummary:
    design_line = [
        p for p in points if abs(p.speedFraction - 1.0) < 1e-9 and not p.stalled
    ]
    if not design_line:
        return DesignSummary(
            pressureRatio=0.0, efficiency=0.0, massFlow=0.0,
            stages=stages, surgeMarginPct=0.0,
        )
    peak = max(design_line, key=lambda p: p.overallEfficiency)
    surge = min(design_line, key=lambda p: p.correctedMassFlow)
    margin = (
        (peak.correctedMassFlow - surge.correctedMassFlow) / peak.correctedMassFlow * 100.0
        if peak.correctedMassFlow > 0 else 0.0
    )
    return DesignSummary(
        pressureRatio=peak.overallPressureRatio,
        efficiency=peak.overallEfficiency,
        massFlow=peak.correctedMassFlow,
        stages=stages,
        surgeMarginPct=margin,
    )


# === PUBLIC SERVICE FUNCTIONS === #


def run_analysis(cfg: AnalysisConfig) -> AnalysisResults:
    """Full stage-stacking performance sweep."""
    start = time.perf_counter()
    sweep = Solver().run(api_config_to_solver_dict(cfg))
    runtime_ms = round((time.perf_counter() - start) * 1000)
    return _map_sweep_to_results(sweep, cfg, runtime_ms)


def compute_design_point(cfg: AnalysisConfig) -> DesignPointResponse:
    """Design-speed reference performance (runs geometry pre-processing + cspref)."""
    solver = Solver()
    solver.run(api_config_to_solver_dict(cfg))  # populates all reference arrays
    si = cfg.deviationFactors.siUnits
    _, _, _, conv_v = _unit_converters(si)
    stages = [
        DesignPointStage(
            stage=i + 1,
            phiRef=solver.phiref[i],
            psiRef=solver.psiref[i],
            etaRef=solver.etaref[i],
            diffusionFactor=solver.rdfm[i],
            rotorIncidence=solver.rincm[i],
            statorIncidence=solver.sincm[i],
            velocityRatioV3V2=solver.v3dv2r[i],
            meanlineRadiusInlet=solver.rm2[i],
            meanlineRadiusOutlet=solver.rm3[i],
            bladeSpeedInlet=conv_v(solver.um2[i]),
            bladeSpeedOutlet=conv_v(solver.um3[i]),
        )
        for i in range(solver.nsta)
    ]
    return DesignPointResponse(units="SI" if si else "US", stages=stages)


def compute_meanline_radius(
    tip: float, hub: float, blade_height_area: bool = True
) -> MeanlineRadiusResponse:
    solver = Solver()
    r = solver.cml(tip, hub)
    area = math.pi * (tip ** 2 - hub ** 2) if blade_height_area else None
    return MeanlineRadiusResponse(meanlineRadius=r, annulusArea=area)


def compute_specific_heat(
    temperature: float, coefficients: List[float], molecular_weight: float, si: bool
) -> SpecificHeatResponse:
    ts = temperature * 9.0 / 5.0 if si else temperature
    solver = Solver()
    solver.dcp = (solver.ru / molecular_weight) / solver.aj
    _, cp, gamma, gm1, _, _, _ = solver.cpf(ts, coefficients)
    return SpecificHeatResponse(
        temperature=ts,
        specificHeat=cp,
        gamma=gamma,
        gammaMinusOne=gm1,
        cpOverR=cp / solver.dcp if solver.dcp else 0.0,
    )


def validate_config(cfg: AnalysisConfig) -> List[ValidationIssue]:
    """Lightweight structural checks mirroring the frontend step validators."""
    issues: List[ValidationIssue] = []
    p = cfg.parameters

    if len(cfg.stageGeometry) != p.stages:
        issues.append(ValidationIssue(
            section="stageGeometry",
            message=f"expected {p.stages} stage geometry entries, got {len(cfg.stageGeometry)}",
        ))
    if len(cfg.characteristics) != p.stages:
        issues.append(ValidationIssue(
            section="characteristics",
            message=f"expected {p.stages} characteristic curves, got {len(cfg.characteristics)}",
        ))
    if len(cfg.efficiencyRatioTable) != p.speeds:
        issues.append(ValidationIssue(
            section="efficiencyRatioTable",
            message=f"expected {p.speeds} speed rows, got {len(cfg.efficiencyRatioTable)}",
        ))
    for i, g in enumerate(cfg.stageGeometry):
        if g.rotorInletTip <= g.rotorInletHub:
            issues.append(ValidationIssue(
                section="stageGeometry",
                message=f"stage {i + 1}: inlet tip radius must exceed hub radius",
            ))
        if g.rotorOutletTip <= g.rotorOutletHub:
            issues.append(ValidationIssue(
                section="stageGeometry",
                message=f"stage {i + 1}: outlet tip radius must exceed hub radius",
            ))
        if g.rotorSolidity <= 0:
            issues.append(ValidationIssue(
                section="stageGeometry",
                message=f"stage {i + 1}: solidity must be positive",
            ))
    for i, curve in enumerate(cfg.characteristics):
        phis = [pt.phi for pt in curve.points]
        if any(b <= a for a, b in zip(phis, phis[1:])):
            issues.append(ValidationIssue(
                section="characteristics",
                message=f"stage {i + 1}: phi values must strictly increase",
            ))
    return issues


# === REFERENCE INPUT DECK === #

_DEFAULT_SPEEDS = [1.0, 0.9, 0.8, 0.7, 0.5]
_DEFAULT_ETARAT = [1.0, 1.017, 1.029, 1.017, 1.023]

_STAGE_GEOMETRY = [
    dict(rotorInletTip=25.42, rotorInletHub=9.891, rotorOutletTip=24.628,
         rotorOutletHub=12.088, inletFlowAngle=0.0, bladeResetAbs=0.0,
         bladeResetRel=0.0, bladeResetOutlet=0.0, rotorMetalAngle=56.15,
         rotorSolidity=1.68, statorMetalAngle=36.10),
    dict(rotorInletTip=23.96, rotorInletHub=13.604, rotorOutletTip=23.566,
         rotorOutletHub=14.696, inletFlowAngle=0.0, bladeResetAbs=0.0,
         bladeResetRel=0.0, bladeResetOutlet=0.0, rotorMetalAngle=55.46,
         rotorSolidity=1.57, statorMetalAngle=36.15),
]
_STAGE_PHI = [
    [0.31, 0.35, 0.38, 0.42, 0.43, 0.44, 0.45, 0.46],
    [0.40, 0.42, 0.44, 0.45, 0.46, 0.48, 0.51, 0.53],
]


def default_config() -> AnalysisConfig:
    stages, speeds, points = 2, 5, 8
    return AnalysisConfig(
        parameters=OperatingParameters(
            stages=stages, speeds=speeds, inletPressure=10.135,
            inletTemperature=288.17, pointsPerCurve=points,
            molecularWeight=28.97, rpm=16042.797, massFlow=33.248,
        ),
        deviationFactors=DeviationFactors(),
        gasCoefficients=[
            0.23747, 0.21962e-4, -0.87791e-7, 0.13991e-9, -0.78056e-13, 0.15043e-16,
        ],
        stageGeometry=[StageGeometry(**_STAGE_GEOMETRY[i]) for i in range(stages)],
        efficiencyRatioTable=[
            EfficiencyRatioRow(speedFraction=_DEFAULT_SPEEDS[i], efficiencyRatio=_DEFAULT_ETARAT[i])
            for i in range(speeds)
        ],
        bleedTable=[
            BleedRow(speedFraction=_DEFAULT_SPEEDS[i], stageBleed=[0.0] * stages)
            for i in range(speeds)
        ],
        characteristics=[
            StageCharacteristic(points=[
                CharacteristicPoint(phi=_STAGE_PHI[i][k], psi=0.0, eta=0.0)
                for k in range(points)
            ])
            for i in range(stages)
        ],
    )
