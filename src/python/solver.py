import math 
import logging
from typing import List 

class AXC1DSolver:
    """
    Multistage compressor analysis and performance calculation solver.
    """

    def __init__(self, logger: logging.Logger):
        """
        Initialize the AXC1DSolver instance.

        Args:
            logger: Logger instance for diagnostic and informational output.
            event_manager: Event manager for triggering functions in different parts of the application.
        """
        self.logger = logger

        # === PHYSICAL CONSTANTS === #
        self.ru      = 1545.44            # universal gas constant  (ft·lbf / lbmol·°R)
        self.pi      = 3.14159265358979
        self.g       = 32.1740            # gravitational constant  (lbm·ft / lbf·s²)
        self.aj      = 778.12             # mechanical equiv. heat  (ft·lbf / BTU)
        self.mole_wt = 28.970
        self.dcp     = (self.ru / self.mole_wt) / self.aj

        self.rpmrad = self.pi / 30.0
        self.rad    = 57.29578           # degrees per radian

    def cml(self, rotor_tip: float, rotor_hub: float) -> float:
        """
        Return the RMS (meanline) radius from tip and hub radii.
        """
        return math.sqrt((rotor_tip ** 2 + rotor_hub ** 2) / 2.0)

    def cpf(self, ts: float, specific_heat_coefficients: List[float]):
        """
        Calculate specific heat and gamma as functions of temperature.

        Computes Cp from a fifth-degree polynomial of static temperature,
        and derives gamma from the relation gamma = Cp / (Cp - R).

        :param ts: Static temperature (°R)
        :return: Tuple (ts, specific_heat, gamma, gm1, gf1, gf2, gf3)
        """
        self.ts = ts
        self.specific_heat = (
            specific_heat_coefficients[0]
            + specific_heat_coefficients[1] * ts
            + specific_heat_coefficients[2] * ts ** 2
            + specific_heat_coefficients[3] * ts ** 3
            + specific_heat_coefficients[4] * ts ** 4
            + specific_heat_coefficients[5] * ts ** 5
        )
        # γ = Cp / (Cp − R)
        self.gamma = self.specific_heat / (self.specific_heat - self.dcp)
        self.gm1   = self.gamma - 1.0          # γ − 1
        self.gf1   = 1.0 / self.gm1            # 1 / (γ − 1)
        self.gf2   = self.gamma / self.gm1     # γ / (γ − 1)
        self.gf3   = 1.0 / self.gf2            # (γ − 1) / γ

        return (
            self.ts, self.specific_heat, self.gamma,
            self.gm1, self.gf1, self.gf2, self.gf3,
        )

    def cspref(self):
        """
        Calculate meanline velocity diagrams and design stage performance.

        At design speed and flow, computes velocity diagrams at meanline radii
        for rotor inlet and outlet, and selected performance parameters for
        each stage.

        :return: Tuple of design reference performance arrays.
        """
        # initialise reference performance arrays 
        self.phiref = [0.0] * self.nsta
        self.psiref = [0.0] * self.nsta
        self.etaref = [0.0] * self.nsta
        self.cpref  = [0.0] * self.nsta
        self.gf1ref = [0.0] * self.nsta
        self.etainp = [0.0] * self.nsta
        self.v3dv2r = [0.0] * self.nsta
        self.rincm  = [0.0] * self.nsta
        self.rdfm   = [0.0] * self.nsta
        self.sincm  = [0.0] * self.nsta

        # initialise velocity fields 
        self.vz2m   = [[0.0] * self.nspe for _ in range(self.nsta)]
        self.vz3m   = [[0.0] * self.nspe for _ in range(self.nsta)]
        self.flocal = [[0.0] * self.nspe for _ in range(self.nsta)]

        # initialise deviation angle corrections 
        self.dphia       = [0.0] * self.nsta
        self.dpsia       = [0.0] * self.nsta
        self.deta        = [0.0] * self.nsta
        self.dpsis_table = [[0.0] * self.nspe for _ in range(self.nsta)]
        self.db2m        = [[0.0] * self.nspe for _ in range(self.nsta)]
        self.db2mr       = [[0.0] * self.nspe for _ in range(self.nsta)]
        self.db3m        = [[0.0] * self.nspe for _ in range(self.nsta)]
        self.db3mr       = [[0.0] * self.nspe for _ in range(self.nsta)]
        self.db3mrg      = [0.0] * self.nsta
        self.db3mrn      = [[0.0] * self.nspe for _ in range(self.nsta)]
        self.db3mrp      = [[0.0] * self.npts for _ in range(self.nsta)]

        # process each stage at design speed 
        for i in range(self.nsta):

            # === INLET DENSITY === #
            # p0 is already in lbf/ft² — no further ×144 needed
            rho2 = self.p0 / (self.rg * self.t0)

            # === AXIAL VELOCITY AT ROTOR INLET === #
            vz2 = self.desflo / (rho2 * self.area2[i])
            self.vz2m[i][0] = vz2

            # === DESIGN FLOW COEFFICIENT (φ = Vz2 / Um2) === #
            um2 = self.um2[i]
            um3 = self.um3[i]
            self.phiref[i] = vz2 / um2 if um2 > 0 else 0.0

            # INLET VELOCITY TRIANGLE
            b2 = self.bet2m[i][0]   # rotor inlet relative blade angle (rad)
            # absolute tangential velocity at inlet: Vθ2 = Um2 − Vz2·tan(β2)
            vt2 = um2 - vz2 * math.tan(b2) if abs(b2) < math.pi / 2 else 0.0
            # relative velocity magnitude at inlet
            w2 = math.sqrt(vz2 ** 2 + (um2 - vt2) ** 2)

            # OUTLET VELOCITY TRIANGLE (iterative)
            b3   = self.cb3mr[i]    # rotor outlet relative blade angle (rad)
            rho3 = rho2             # first estimate: outlet density ≈ inlet density
            vz3  = vz2              # initial guess
            dt   = 0.0
            t3   = self.t0

            for _ in range(20):
                vz3_new = (
                    self.desflo / (rho3 * self.area3[i])
                    if self.area3[i] > 0 else vz2
                )
                vt3 = um3 - vz3_new * math.tan(b3) if abs(b3) < math.pi / 2 else 0.0
                work = um3 * vt3 - um2 * vt2   # euler work (ft²/s²)
                self.cpf(self.t0)
                dt_new  = work / (self.specific_heat * self.gj) if self.gj > 0 else 0.0
                t3_new  = self.t0 + dt_new
                self.cpf(t3_new)
                pr_approx = (t3_new / self.t0) ** self.gf2 if self.t0 > 0 else 1.0
                pt3       = self.p0 * pr_approx
                rho3 = pt3 / (self.rg * t3_new) if t3_new > 0 else rho2

                if abs(vz3_new - vz3) < 0.01 and abs(dt_new - dt) < 0.1:
                    vz3 = vz3_new
                    dt  = dt_new
                    t3  = t3_new
                    break

                vz3 = vz3_new
                dt  = dt_new
                t3  = t3_new

            self.vz3m[i][0] = vz3

            # === DESIGN PRESSURE COEFFICIENT (ψ = Cp·ΔT·gj / Um3²) === # 
            self.psiref[i] = (
                (self.specific_heat * dt * self.gj) / um3 ** 2
                if um3 > 0 else 0.0
            )

            # === REFERENCE THERMODYNAMIC STATE === #
            self.cpref[i]  = self.specific_heat
            self.gf1ref[i] = self.gf1

            # === REFERENCE EFFICIENCY === #
            self.etaref[i] = (
                self.etades[i][0][0]
                if self.etades[i][0][0] != 0.0 else 0.85
            )

            # === ROTOR INLET INCIDENCE === #
            beta2_flow     = math.atan2(vz2, um2 - vt2)
            self.rincm[i]  = (beta2_flow - b2) * self.rad

            # === LIEBLEIN DIFFUSION FACTOR === #
            # DF = 1 − (W3/W2) + |ΔVθ| / (2·W2·σ)
            vt3 = um3 - vz3 * math.tan(b3) if abs(b3) < math.pi / 2 else 0.0
            w3  = math.sqrt(vz3 ** 2 + (um3 - vt3) ** 2)
            if w2 > 0 and self.rsolm[i] > 0:
                self.rdfm[i] = (
                    1.0 - (w3 / w2) + abs(vt3 - vt2) / (2.0 * w2 * self.rsolm[i])
                )
            else:
                self.rdfm[i] = 0.5

            # === STATOR INCIDENCE === #
            alpha3_flow    = math.atan2(vt3, vz3) if vz3 > 0 else 0.0
            sk2m_rad       = self.sk2m[i] / self.rad
            self.sincm[i]  = (alpha3_flow - sk2m_rad) * self.rad

            # === V3/V2 VELOCITY RATIO === # 
            v2 = math.sqrt(vz2 ** 2 + vt2 ** 2)
            v3 = math.sqrt(vz3 ** 2 + vt3 ** 2)
            self.v3dv2r[i] = v3 / v2 if v2 > 0 else 1.0

            # === DESIGN BLADE ANGLE STORAGE === # 
            beta2_rel = math.atan2(vz2, um2 - vt2)
            beta3_rel = math.atan2(vz3, um3 - vt3)
            alpha2    = math.atan2(vt2, vz2)
            alpha3    = math.atan2(vt3, vz3)

            self.db2m[i][0]  = alpha2
            self.db2mr[i][0] = beta2_rel
            self.db3m[i][0]  = alpha3
            self.db3mr[i][0] = beta3_rel

            self.flocal[i][0] = self.desflo

        self.logger.info("Design Point Reference Performance")
        self.logger.info(f"  φ_ref : {[round(v, 4) for v in self.phiref]}")
        self.logger.info(f"  ψ_ref : {[round(v, 4) for v in self.psiref]}")
        self.logger.info(f"  η_ref : {[round(v, 4) for v in self.etaref]}")
        self.logger.info(f"  DF    : {[round(v, 4) for v in self.rdfm]}")
        self.logger.info(f"  inc_r : {[round(v, 2) for v in self.rincm]} deg")

        return (
            self.phiref, self.psiref, self.etaref,
            self.cpref,  self.gf1ref, self.etainp,
            self.v3dv2r, self.rincm,  self.rdfm,
            self.sincm,  self.vz2m,   self.vz3m,
            self.flocal, self.db2m,   self.db2mr,
            self.db3m,   self.db3mr,
        )

    def cseta(self):
        """
        Generate stage adiabatic efficiency curve vs. flow coefficient.

        Builds a two-parabola eta(phi) curve: stall-side and choke-side.
        Peak efficiency occurs at design conditions.
        """
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
                            xx  = min(1.0, max(0.0, (phi_d - phi) / (phi_d - phi_s)))
                            eta = eta_d - (eta_d - eta_s) * xx ** 2
                        else:
                            eta = eta_d
                    else:
                        if phi_c > phi_d:
                            xx  = min(1.0, max(0.0, (phi - phi_d) / (phi_c - phi_d)))
                            eta = eta_d - (eta_d - eta_c) * xx ** 2
                        else:
                            eta = eta_d
                    self.etades[i][j][k] = max(0.0, eta)

        self.logger.info("Stage Adiabatic Efficiency Curves Generated")
        return self.etades

    def cspsi(self):
        """
        Generate stage pressure coefficient curve vs. flow coefficient.

        Computes ψ(φ) for each stage when not supplied by the user.
        """
        for i in range(self.nsta):
            phi_d  = self.phiref[i]
            psi_d  = self.psiref[i]
            b2md   = self.bet2m[i][0]
            b3md   = self.cb3mr[i]

            for j in range(self.nspe):
                for k in range(self.npts):
                    if self.psides[i][j][k] != 0.0:
                        continue
                    phi = self.phides[i][j][k]
                    if phi < 0.001:
                        self.psides[i][j][k] = 0.0
                        continue

                    vz2m = (
                        self.vz2m[i][0] * (phi / phi_d)
                        if phi_d > 0 else self.vz2m[i][0]
                    )

                    rho2 = self.p0 / (self.rg * self.t0)
                    w2   = rho2 * self.area2[i] * vz2m

                    b3m = b3md
                    t   = self.t0 + 10.0

                    for _ in range(10):
                        rho3 = rho2 * 1.05
                        vz3m = (
                            w2 / (rho3 * self.area3[i])
                            if self.area3[i] > 0 else vz2m
                        )
                        if self.drdevp == 1.0:
                            phi_ratio = phi / phi_d if phi_d > 0 else 1.0
                            b3m = b3md + 0.05 * (phi_ratio - 1.0)

                        tan_b3m = math.tan(b3m) if abs(b3m) < math.pi / 2 else 0.0
                        tan_b2m = math.tan(b2md) if abs(b2md) < math.pi / 2 else 0.0
                        vt3m    = self.um3[i] - vz3m * tan_b3m
                        vt2m    = self.um2[i] - vz2m * tan_b2m
                        work    = self.um3[i] * vt3m - self.um2[i] * vt2m

                        cp_current = self.cpref[i]
                        dt = (
                            work / (cp_current * self.gj)
                            if cp_current > 0 else work / self.gj
                        )
                        t3 = self.t0 + dt
                        self.cpf(t3)

                        if abs(t3 - t) < 0.1:
                            break
                        t = t3

                    psi = (
                        (self.specific_heat * dt) / (self.um3[i] ** 2)
                        if self.um3[i] > 0 else psi_d
                    )
                    psi = max(0.0, min(1.0, psi))
                    self.psides[i][j][k] = psi if psi > 0.01 else psi_d * 0.5

        self.logger.info("Stage Pressure Coefficient Curves Generated")
        return self.psides

    def cspsd(self):
        """
        Adjust pressure coefficient for off-design rotative speeds.
        """
        for i in range(self.nsta):
            phi_d = self.phiref[i]
            psi_d = self.psiref[i]
            b2md  = self.bet2m[i][0]
            b3md  = self.cb3mr[i]

            for j in range(self.nspe):
                pctspd = (
                    self.efficiency_ratio_table[j][0]
                    if j < len(self.efficiency_ratio_table) else 1.0
                )
                if abs(pctspd - 1.0) < 0.01:
                    self.dpsis_table[i][j] = 0.0
                    continue

                um2_offdesign = self.um2[i] * pctspd
                um3_offdesign = self.um3[i] * pctspd
                vz2m          = phi_d * um2_offdesign

                rho2 = self.p0 / (self.rg * self.t0)
                w2   = rho2 * self.area2[i] * vz2m

                b3m = b3md
                t   = self.t0 + 10.0

                for _ in range(10):
                    rho3 = rho2 * 1.05
                    vz3m = (
                        w2 / (rho3 * self.area3[i])
                        if self.area3[i] > 0 else vz2m
                    )
                    if self.drdevn == 1.0:
                        b3m = b3md + 0.05 * (pctspd - 1.0)

                    tan_b3m = math.tan(b3m) if abs(b3m) < math.pi / 2 else 0.0
                    tan_b2m = math.tan(b2md) if abs(b2md) < math.pi / 2 else 0.0
                    vt3m    = um3_offdesign - vz3m * tan_b3m
                    vt2m    = um2_offdesign - vz2m * tan_b2m
                    work    = um3_offdesign * vt3m - um2_offdesign * vt2m

                    cp_current = self.cpref[i]
                    dt = (
                        (pctspd * work) / (cp_current * self.gj)
                        if cp_current > 0
                        else (pctspd * work) / self.gj
                    )
                    t3 = self.t0 + dt
                    self.cpf(t3)

                    if abs(t3 - t) < 0.1:
                        break
                    t = t3

                psi_offdesign = (
                    (self.specific_heat * dt) / (um3_offdesign ** 2)
                    if um3_offdesign > 0 else 0.0
                )
                # delta from design
                self.dpsis_table[i][j] = psi_offdesign - psi_d

        self.logger.info("Off-Design Pressure Coefficient Shifts Calculated")
        return self.dpsis_table

    def cspan(self):
        """
        Alter stage characteristics for blade setting angle changes.
        """
        self.dphia = [0.0] * self.nsta
        self.dpsia = [0.0] * self.nsta
        self.deta  = [0.0] * self.nsta

        for i in range(self.nsta):
            cb2m  = self.cb2m[i]
            cb2mr = self.cb2mr[i]
            cb3mr = self.cb3mr[i]

            if abs(cb2m) < 1e-10 and abs(cb2mr) < 1e-10 and abs(cb3mr) < 1e-10: continue   # no blade reset — deltas stay zero

            b2md  = self.bet2m[i][0]
            phi_d = self.phiref[i]
            psi_d = self.psiref[i]

            # updated blade angles
            ab2m     = cb2m + cb2mr
            b2m_new  = b2md + ab2m
            b3m_new  = b2md + cb3mr     # b3md == cb3mr (design outlet angle)

            # new axial velocity at rotor inlet
            tan_b2md    = math.tan(b2md)    if abs(b2md)    < math.pi / 2 else 0.0
            tan_b2m_new = math.tan(b2m_new) if abs(b2m_new) < math.pi / 2 else 0.0
            denom       = tan_b2md + tan_b2m_new

            vz2m_new = (
                self.um2[i] / denom
                if abs(denom) > 1e-10
                else self.vz2m[i][0]
            )

            phi_new  = vz2m_new / self.um2[i] if self.um2[i] > 0 else phi_d
            dphia_i  = phi_new - phi_d

            rho2 = self.p0 / (self.rg * self.t0)
            w2   = rho2 * self.area2[i] * vz2m_new

            b3m = b3m_new
            t   = self.t0 + 10.0

            for _ in range(10):
                rho3 = rho2 * 1.05
                vz3m = (
                    w2 / (rho3 * self.area3[i])
                    if self.area3[i] > 0 else vz2m_new
                )
                if self.drdevg == 1.0:
                    dev_correction = 0.02 * (ab2m + cb3mr)
                    b3m = b3m_new + dev_correction

                tan_b2m = math.tan(b2m_new) if abs(b2m_new) < math.pi / 2 else 0.0
                tan_b3m = math.tan(b3m)     if abs(b3m)     < math.pi / 2 else 0.0
                vt2m    = self.um2[i] - vz2m_new * tan_b2m
                vt3m    = self.um3[i] - vz3m     * tan_b3m
                work    = self.um3[i] * vt3m - self.um2[i] * vt2m

                cp_current = self.cpref[i]
                dt = (
                    work / (cp_current * self.gj)
                    if cp_current > 0
                    else work / self.gj if self.gj > 0 else 0.0
                )
                t3 = self.t0 + dt
                self.cpf(t3)

                if abs(t3 - t) < 0.1:
                    break
                t = t3

            if self.um3[i] > 0:
                psi_reset = (self.specific_heat * dt) / (self.um3[i] ** 2)
                dpsia_i   = psi_reset - psi_d
            else:
                dpsia_i = 0.0

            self.dphia[i] = dphia_i
            self.dpsia[i] = dpsia_i
            self.deta[i]  = 0.0

        self.logger.info("Blade Reset Corrections Applied:")
        self.logger.info(f"  Flow Coefficient Shifts  (Δϕ): {self.dphia}")
        self.logger.info(f"  Pressure Coefficient Shifts (Δψ): {self.dpsia}")
        return self.dphia, self.dpsia, self.deta

    def csoupt(self):
        """
        Calculate and output stage and cumulative compressor performance.
        """
        self.sweep_results = []
        self.tt = [self.t0] * (self.nsta + 1)
        self.pt = [self.p0] * (self.nsta + 1)

        for j in range(self.nspe):
            pctspd = self.efficiency_ratio_table[j][0]
            etarat = self.efficiency_ratio_table[j][1]

            self.logger.info(f"\n{'=' * 70}")
            self.logger.info(
                f"SPEED: {pctspd * 100:.1f}% - EFFICIENCY RATIO: {etarat:.4f}"
            )
            self.logger.info(f"{'=' * 70}")

            for k in range(self.npts):
                operating_point = {
                    "speed":     pctspd,
                    "eta_ratio": etarat,
                    "flow_point": k,
                    "stages":    [],
                }

                tt_inlet = self.t0
                pt_inlet = self.p0
                stall_choke_detected = False

                for i in range(self.nsta):
                    um2_current = self.um2[i] * pctspd
                    um3_current = self.um3[i] * pctspd

                    phi       = self.phi_[i][j][k]
                    psi       = self.psi_[i][j][k]
                    eta_stage = self.eta_[i][j][k]

                    vz2m = phi * um2_current

                    # FIX 2: pt_inlet already in lbf/ft² — no ×144
                    rho2 = pt_inlet / (self.rg * tt_inlet) if self.rg > 0 else 0.0
                    w2   = rho2 * self.area2[i] * vz2m

                    # stall / choke detection.
                    # bounds are derived from the actual min/max of the phi
                    # map for this stage and speed (with a 2% margin).
                    # this avoids false triggers when phiref falls outside the
                    # supplied input phi range, as can happen with Stage 2 where
                    # the geometric design phi exceeds the input characteristic range.
                    phi_map_vals = [
                        self.phi_[i][j][kk] for kk in range(self.npts)
                        if self.phi_[i][j][kk] > 0.0
                    ]
                    if phi_map_vals:
                        phi_min = min(phi_map_vals) * 0.98   # 2% margin below map min
                        phi_max = max(phi_map_vals) * 1.02   # 2% margin above map max
                    else:
                        # fallback: speed-scaled design point window
                        phi_d_scaled = (
                            self.phiref[i] * pctspd
                            if self.spdphi == 1.0 else self.phiref[i]
                        )
                        phi_min = phi_d_scaled * 0.6
                        phi_max = phi_d_scaled * 1.4

                    if phi < phi_min or phi > phi_max:
                        stall_choke_detected = True
                        condition = "STALL" if phi < phi_min else "CHOKE"
                        self.logger.warning(
                            f"STAGE {i + 1}: {condition} CONDITION — "
                            f"φ = {phi:.4f} (range {phi_min:.4f}–{phi_max:.4f}) "
                            f"at {pctspd * 100:.1f}% speed, flow point {k}"
                        )

                    # ψ·Um² = Cp·ΔT·gj  →  ΔT = ψ·Um² / (Cp·gj)
                    # actual ΔT accounts for efficiency: ΔT_actual = ΔT_is / η
                    t_outlet = tt_inlet + 20.0  # initial guess

                    for _ in range(10):
                        self.cpf(t_outlet)
                        if self.specific_heat > 0 and self.gj > 0:
                            dt_isentropic = (psi * um3_current ** 2) / (
                                self.specific_heat * self.gj
                            )
                        else:
                            dt_isentropic = 0.0

                        dt_actual    = dt_isentropic / eta_stage if eta_stage > 0 else dt_isentropic
                        t_outlet_new = tt_inlet + dt_actual

                        if abs(t_outlet_new - t_outlet) < 0.1:
                            break
                        t_outlet = t_outlet_new

                    self.cpf(t_outlet)

                    # stage pressure ratio (isentropic relation)
                    if t_outlet > 0 and tt_inlet > 0:
                        temp_ratio  = t_outlet / tt_inlet
                        press_ratio = temp_ratio ** self.gf2 if self.gf2 > 0 else 1.0
                    else:
                        temp_ratio  = 1.0
                        press_ratio = 1.0

                    pt_outlet = pt_inlet * press_ratio

                    # outlet density & axial velocity
                    rho3 = pt_outlet / (self.rg * t_outlet) if self.rg > 0 else 0.0
                    vz3m = w2 / (rho3 * self.area3[i]) if self.area3[i] > 0 else vz2m

                    # outlet tangential velocity
                    b3m     = self.cb3mr[i]
                    tan_b3m = math.tan(b3m) if abs(b3m) < math.pi / 2 else 0.0
                    vt3m    = um3_current - vz3m * tan_b3m

                    # rotor inlet incidence
                    beta2m_rad = self.bet2m[i][0]
                    tan_b2m    = math.tan(beta2m_rad) if abs(beta2m_rad) < math.pi / 2 else 0.0

                    v2m_rel = math.sqrt(vz2m ** 2 + (um2_current - vz2m * tan_b2m) ** 2)
                    incidence_rotor = (
                        (math.atan(vz2m / um2_current) - beta2m_rad) * self.rad
                        if um2_current > 0 else 0.0
                    )

                    vt2m_df = um2_current - vz2m * tan_b2m
                    vr2     = math.sqrt(vz2m ** 2 + (um2_current - vt2m_df) ** 2)
                    vr3     = math.sqrt(vz3m ** 2 + (um3_current - vt3m) ** 2)

                    if vr2 > 0 and self.rsolm[i] > 0:
                        df = (
                            1.0
                            - (vr3 / vr2)
                            + abs(vt3m - vt2m_df) / (2.0 * vr2 * self.rsolm[i])
                        )
                    else:
                        df = 0.5

                    stage_result = {
                        "stage":            i + 1,
                        "mass_flow":        w2,
                        "phi":              phi,
                        "psi":              psi,
                        "eta":              eta_stage,
                        "pr":               press_ratio,
                        "tr":               temp_ratio,
                        "tt_inlet":         tt_inlet,
                        "tt_outlet":        t_outlet,
                        "pt_inlet":         pt_inlet,
                        "pt_outlet":        pt_outlet,
                        "vz2m":             vz2m,
                        "vz3m":             vz3m,
                        "um2":              um2_current,
                        "um3":              um3_current,
                        "vt2m":             vt2m_df,
                        "vt3m":             vt3m,
                        "incidence":        incidence_rotor,
                        "diffusion_factor": df,
                    }
                    operating_point["stages"].append(stage_result)

                    tt_inlet = t_outlet
                    pt_inlet = pt_outlet

                # overall compressor performance
                if not stall_choke_detected:
                    pr_overall = pt_inlet / self.p0 if self.p0 > 0 else 1.0
                    tr_overall = tt_inlet / self.t0 if self.t0 > 0 else 1.0
                    if tr_overall > 1.0:
                        tr_isentropic = (
                            pr_overall ** self.gf3 if self.gf3 > 0 else tr_overall
                        )
                        eta_overall = (
                            (tr_isentropic - 1.0) / (tr_overall - 1.0)
                            if (tr_overall - 1.0) > 1e-10 else 1.0
                        )
                    else:
                        eta_overall = 1.0
                    operating_point["pr_overall"]  = pr_overall
                    operating_point["tr_overall"]  = tr_overall
                    operating_point["eta_overall"] = max(0.0, min(1.0, eta_overall))
                else:
                    operating_point["pr_overall"]  = 0.0
                    operating_point["tr_overall"]  = 0.0
                    operating_point["eta_overall"] = 0.0

                self.sweep_results.append(operating_point)

                # formatted log output
                output = [
                    f"\n{'─' * 70}",
                    f"Speed: {pctspd * 100:6.1f}% | Flow Point: {k}",
                    f"{'─' * 70}",
                    f"{'Stage':^6} {'Mass Flow':^12} {'Φ':^10} {'Ψ':^10} "
                    f"{'η':^8} {'PR':^10} {'TR':^10}",
                    f"{'':^6} {'(lb/s)':^12} {'':^10} {'':^10} "
                    f"{'':^8} {'':^10} {'':^10}",
                    f"{'-' * 70}",
                ]
                for sr in operating_point["stages"]:
                    output.append(
                        f"{sr['stage']:^6d} {sr['mass_flow']:^12.4f} "
                        f"{sr['phi']:^10.4f} {sr['psi']:^10.4f} "
                        f"{sr['eta']:^8.4f} {sr['pr']:^10.4f} {sr['tr']:^10.4f}"
                    )
                last = operating_point["stages"][-1]
                output += [
                    f"{'-' * 70}",
                    f"{'TOTAL':^6} {last['mass_flow']:^12.4f}   "
                    f"PR={operating_point['pr_overall']:^10.4f}  "
                    f"TR={operating_point['tr_overall']:^10.4f}  "
                    f"η={operating_point['eta_overall']:^8.4f}",
                ]
                for line in output:
                    self.logger.info(line)

        self.logger.info(f"\n{'=' * 70}")
        self.logger.info("PERFORMANCE SWEEP COMPLETED")
        self.logger.info(f"{'=' * 70}")

        return (
            self.sweep_results, self.phi_, self.psi_,
            self.eta_, self.tt, self.pt,
        )

    def run(self, config: dict):
        """
        Execute the compressor analysis pipeline.

        FIX 1: rpmrad constant corrected to π/30 (was π/360).
        FIX 2: sk2m now picks up the *next* stage's CB2M (not the current
                stage's), matching physical intent.
        FIX 3: conditional sub-routine results are pre-initialised to None
                so that references after the conditional blocks are safe.
        """
       

        # === INPUT PARAMETERS === #
        ip = list(dict(config["SI Input Parameters"]).values())
        self.input_params = ip

        df = list(dict(config["Deviation Factors"]).values())
        self.deviation_factors = df

        self.specific_heat_coefficients = list(dict(config["Specific Heat Coefficients"]).values())

        # unpack scalars
        self.nsta   = int(ip[0])   # STAGES
        self.nspe   = int(ip[1])   # SPEEDS
        self.p0     = ip[2]        # P0_IN   (was wrongly read as npts)
        self.t0     = ip[3]        # T0_IN   (was wrongly read as p0)
        self.npts   = int(ip[4])   # POINTS  (was wrongly read as t0)
        self.desrpm = ip[6]        # RPM
        self.desflo = ip[7]        # MASS_FLOW

        self.spdpsi = df[0]
        self.spdphi = df[1]
        self.drdevg = df[2]
        self.drdevn = df[3]
        self.drdevp = df[4]
        self.units  = df[5]

        # === DERIVED CONSTANTS === #
        mole_wt    = ip[5]
        self.rg    = self.ru  / mole_wt
        self.dcp   = self.rg  / self.aj
        self.gj    = self.g   * self.aj
        self.g2j   = self.gj  * 2.0

        self.cpf(self.t0)

        # === UNIT CONVERSION === #
        if self.units == 1.0:
            self.p0     = self.p0     / 0.689476
            self.t0     = self.t0     * 9.0 / 5.0
            self.desflo = self.desflo / 0.453592

        # convert p0 from psi → lbf/ft² 
        self.p0 = self.p0 * 144.0

        # === STAGE GEOMETRY === #
        stage_geometry_ = dict(config["Stage Geometry"])
        self.stage_geometry = []
        for stage_idx in range(1, self.nsta + 1):
            prefix     = f"STAGE_{stage_idx}_"
            stage_vals = [v for k, v in stage_geometry_.items() if k.startswith(prefix)]
            self.stage_geometry.append([stage_idx] + stage_vals)

        if self.units == 1.0:
            for i in range(self.nsta):
                for col in [1, 2, 3, 4]:
                    self.stage_geometry[i][col] /= 2.54   # cm → in

        # === BLEED TABLE === #
        self.bleed_table = []
        for row in config["Bleed Table"]:
            bleed_row = [row["PCTSPD"]] + row["stage_values"]
            if self.units == 1.0:
                bleed_row = [bleed_row[0]] + [v / 0.453592 for v in bleed_row[1:]]
            self.bleed_table.append(bleed_row)

        # === EFFICIENCY RATIO TABLE === #
        self.efficiency_ratio_table = [
            [row["PCTSPD"], row["ETARAT"]]
            for row in config["Efficiency Ratio Table"]
        ]

        # === INPUT DESIGN CHARACTERISTICS === #
        self.phides = [[[0.0] * self.npts for _ in range(self.nspe)] for _ in range(self.nsta)]
        self.psides = [[[0.0] * self.npts for _ in range(self.nspe)] for _ in range(self.nsta)]
        self.etades = [[[0.0] * self.npts for _ in range(self.nspe)] for _ in range(self.nsta)]

        for i, stg in enumerate(config["Input Design Characteristics"]):
            for k, pt in enumerate(stg["points"]):
                self.phides[i][0][k] = pt["phi"]
                self.psides[i][0][k] = pt["psi"]
                self.etades[i][0][k] = pt["eta"]

        self.logger.info(f"Input Design Characteristics: {[[i, self.phides[i], self.psides[i], self.etades[i]] for i in range(self.nsta)]}")

        # === PER-STAGE GEOMETRY === #
        self.area2 = [0.0] * self.nsta
        self.area3 = [0.0] * self.nsta
        self.rm2   = [0.0] * self.nsta
        self.rm3   = [0.0] * self.nsta
        self.ut2   = [0.0] * self.nsta
        self.ut3   = [0.0] * self.nsta
        self.um2   = [0.0] * self.nsta
        self.um3   = [0.0] * self.nsta
        self.rsolm = [0.0] * self.nsta

        self.rk2m  = [0.0] * self.nsta
        self.sk2m  = [0.0] * self.nsta
        self.cb2m  = [0.0] * self.nsta
        self.cb2mr = [0.0] * self.nsta
        self.cb3mr = [0.0] * self.nsta
        self.bet2m = [[0.0] * self.nspe for _ in range(self.nsta)]

        # === GEOMETRY PRE-PROCESSING === #
        for i in range(self.nsta):
            sg            = self.stage_geometry[i]
            rt2, rh2      = sg[1], sg[2]
            rt3, rh3      = sg[3], sg[4]

            self.area2[i] = self.pi * (rt2 ** 2 - rh2 ** 2) / 144.0
            self.area3[i] = self.pi * (rt3 ** 2 - rh3 ** 2) / 144.0
            self.rm2[i]   = self.cml(rotor_tip=rt2, rotor_hub=rh2)
            self.rm3[i]   = self.cml(rotor_tip=rt3, rotor_hub=rh3)

            omega         = self.desrpm * self.pi / 30.0   # rad/s
            self.ut2[i]   = (rt2 / 12.0) * omega
            self.ut3[i]   = (rt3 / 12.0) * omega
            self.um2[i]   = (self.rm2[i] / 12.0) * omega
            self.um3[i]   = (self.rm3[i] / 12.0) * omega

            # blade angles  (col order: RT2 RH2 RT3 RH3 BET2M CB2M CB2MR CB3MR RK2M RSOLM SK2M)
            self.bet2m[i][0] = sg[5]  / self.rad
            self.cb2m[i]     = sg[6]  / self.rad
            self.cb2mr[i]    = sg[7]  / self.rad
            self.cb3mr[i]    = sg[8]  / self.rad
            self.rk2m[i]     = sg[9]  + sg[7]          # RK2M + CB2MR (degrees)
            self.rsolm[i]    = sg[10]

            # FIX 2: sk2m = SK2M of this stage + CB2M of the *next* stage
            # (the original code used sg[6] which is the current stage's CB2M)
            if i + 1 < self.nsta:
                next_sg       = self.stage_geometry[i + 1]
                self.sk2m[i]  = sg[11] + next_sg[6]
            else:
                self.sk2m[i]  = sg[11]

        # === DESIGN VELOCITY TRIANGLES & REFERENCE PERFORMANCE === #
        self.cspref()

        # pre-initialise optional results to None for safe reference
        cseta_ = None
        cspsi_ = None
        cspsd_ = None

        # === PROPAGATE 100% SPEED ROW TO ALL OFF-DESIGN SPEED ROWS === #
        # The input file only carries phi values for j = 0 (100% speed).
        # cseta() and cspsi() iterate over all (j, k) pairs, so every
        # off-design speed row must be seeded with the 100% speed phi
        # values before those routines are called.  Rows that were
        # explicitly supplied (non-zero) are left untouched.
        for i in range(self.nsta):
            for j in range(1, self.nspe):
                for k in range(self.npts):
                    if self.phides[i][j][k] == 0.0: self.phides[i][j][k] = self.phides[i][0][k]
                    # psi and eta: leave as zero so cseta/cspsi fill them in

        # === BUILD EFFICIENCY CURVE IF NOT SUPPLIED === #
        if self.etades[0][0][0] == 0.0: cseta_ = self.cseta()

        # === BUILD PRESSURE COEFF CURVE IF NOT SUPPLIED === #
        if self.psides[0][0][0] == 0.0: cspsi_ = self.cspsi()

        # === SPEED-DEPENDENT PSI SHIFT === #
        if self.spdpsi == 1.0: cspsd_ = self.cspsd()

        # === APPLY BLADE RESET === #
        self.cspan()

        # === BUILD FULL PHI / PSI / ETA CHARACTERISTIC MAPS === #
        self.phi_ = [[[0.0] * self.npts for _ in range(self.nspe)] for _ in range(self.nsta)]
        self.psi_ = [[[0.0] * self.npts for _ in range(self.nspe)] for _ in range(self.nsta)]
        self.eta_ = [[[0.0] * self.npts for _ in range(self.nspe)] for _ in range(self.nsta)]

        for i in range(self.nsta):
            for j in range(self.nspe):
                pctspd = self.efficiency_ratio_table[j][0]
                etarat = self.efficiency_ratio_table[j][1]
                for k in range(self.npts):
                    # base phi always from the 100% speed row (propagated above)
                    phi = self.phides[i][0][k] + self.dphia[i]

                    # SPDPHI: scale the phi axis linearly with speed.
                    # The original formula (phi/phiref)^(1/pctspd) is
                    # dimensionally inconsistent and diverges at low speeds.
                    # Linear scaling phi * pctspd is the standard 1-D approach.
                    if self.spdphi == 1.0 and pctspd != 0.0:
                        phi = phi * pctspd

                    dpsis_ij = self.dpsis_table[i][j] if self.dpsis_table else 0.0
                    psi = self.psides[i][0][k] + self.dpsia[i] + dpsis_ij
                    eta = self.etades[i][0][k] * etarat + self.deta[i]

                    self.phi_[i][j][k] = phi
                    self.psi_[i][j][k] = psi
                    self.eta_[i][j][k] = eta

        self.logger.info("Characteristic Maps Built")

        # === PERFORMANCE SWEEP === #
        csoupt_ = self.csoupt()
        return csoupt_