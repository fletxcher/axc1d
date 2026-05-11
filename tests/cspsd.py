import math
import logging
from src.python.solver import AXC1DSolver

specific_heat_coefficients = [0.23747e+00, 0.21962e-04, -0.87791e-07, 0.13991e-09, -0.78056e-13, 0.15043e-16]

"""
Test Cases:
  test0 — design speed (pctspd = 1.0): dpsis_table slot is zeroed
  test1 — near-design speed within 1% tolerance also zeroes the slot
  test2 — off-design speed (pctspd = 0.80) produces a finite, nonzero shift
  test3 — off-design speed (pctspd = 1.20) produces a finite, nonzero shift
  test4 — um3 = 0 short-circuits the ψ_offdesign computation to 0 - psi_d
  test5 — drdevn = 1.0 applies the rotor-outlet deviation correction
  test6 — multi-stage shifts are independent across stages
  test7 — multi-speed: the design row stays zero while off-design rows shift
  test8 — cspsd returns the dpsis_table with shape (nsta, nspe)
"""

def build_solver(nsta, nspe, phiref, psiref, bet2m, cb3mr, efficiency_ratio_table, um2, um3, area2, area3, cpref, dpsis_table, drdevn = 0.0):
    """
    Build and return a solver for each given scenario.
    """
    s = AXC1DSolver(logger = logging.getLogger("cspsd"))
    s.logger.addHandler(logging.NullHandler())
    s.nsta                       = nsta
    s.nspe                       = nspe
    s.phiref                     = list(phiref)
    s.psiref                     = list(psiref)
    s.bet2m                      = [list(row) for row in bet2m]
    s.cb3mr                      = list(cb3mr)
    s.efficiency_ratio_table     = [list(row) for row in efficiency_ratio_table]
    s.um2                        = list(um2)
    s.um3                        = list(um3)
    s.area2                      = list(area2)
    s.area3                      = list(area3)
    s.cpref                      = list(cpref)
    s.dpsis_table                = [list(row) for row in dpsis_table]
    s.drdevn                     = drdevn
    s.p0                         = 2116.224
    s.t0                         = 518.67
    s.rg                         = 53.34
    s.gj                         = 32.1740 * 778.12
    s.specific_heat_coefficients = list(specific_heat_coefficients)
    return s

def baseline(**overrides):
    """
    Reference: a balanced single-stage configuration with a one-row efficiency
    ratio table.  The pctspd entry is the part that we mutate per test.
    """
    base = dict(
        nsta = 1, nspe = 1,
        phiref = [0.30], psiref = [0.40],
        bet2m = [[0.0]], cb3mr = [0.0],
        efficiency_ratio_table = [[1.0, 1.0]],
        um2 = [500.0], um3 = [500.0],
        area2 = [1.0], area3 = [1.0],
        cpref = [0.24],
        dpsis_table = [[0.0]],
        drdevn = 0.0,
    )
    base.update(overrides)
    return base

def test0():
    """
    Design speed — pctspd = 1.0 zeroes the dpsis_table slot.
    """
    s = build_solver(**baseline(efficiency_ratio_table = [[1.0, 1.0]]))
    result = s.cspsd()
    assert result[0][0] == 0.0

def test1():
    """
    Near-design speed — pctspd within 1% tolerance also zeroes the slot.
    """
    s = build_solver(**baseline(efficiency_ratio_table = [[1.005, 1.0]]))
    result = s.cspsd()
    assert result[0][0] == 0.0

def test2():
    """
    Off-design speed (pctspd = 0.80) produces a finite, nonzero shift.
    """
    s = build_solver(**baseline(efficiency_ratio_table = [[0.80, 1.0]]))
    result = s.cspsd()
    assert math.isfinite(result[0][0])
    assert result[0][0] != 0.0

def test3():
    """
    Off-design speed (pctspd = 1.20) produces a finite, nonzero shift.
    """
    s = build_solver(**baseline(efficiency_ratio_table = [[1.20, 1.0]]))
    result = s.cspsd()
    assert math.isfinite(result[0][0])
    assert result[0][0] != 0.0

def test4():
    """
    um3 = 0 — ψ_offdesign collapses to 0, leaving dpsis = -psi_d.
    """
    psi_d = 0.40
    s = build_solver(**baseline(
        psiref = [psi_d],
        um3 = [0.0],
        efficiency_ratio_table = [[0.80, 1.0]],
    ))
    result = s.cspsd()
    assert result[0][0] == -psi_d

def test5():
    """
    drdevn = 1.0 applies the rotor-outlet deviation correction (b3m shifts).
    """
    s_off = build_solver(**baseline(
        efficiency_ratio_table = [[0.80, 1.0]],
        drdevn = 0.0,
    ))
    s_on = build_solver(**baseline(
        efficiency_ratio_table = [[0.80, 1.0]],
        drdevn = 1.0,
    ))
    off_result = s_off.cspsd()
    on_result  = s_on.cspsd()
    assert off_result[0][0] != on_result[0][0]

def test6():
    """
    Multi-stage — each stage's dpsis_table[i] is computed independently.
    """
    s = build_solver(**baseline(
        nsta = 2,
        phiref = [0.30, 0.32], psiref = [0.40, 0.42],
        bet2m = [[0.0], [0.0]], cb3mr = [0.0, 0.0],
        efficiency_ratio_table = [[0.80, 1.0]],
        um2 = [500.0, 600.0], um3 = [500.0, 600.0],
        area2 = [1.0, 1.0], area3 = [1.0, 1.0],
        cpref = [0.24, 0.24],
        dpsis_table = [[0.0], [0.0]],
    ))
    result = s.cspsd()
    assert math.isfinite(result[0][0])
    assert math.isfinite(result[1][0])
    assert result[0][0] != result[1][0]

def test7():
    """
    Multi-speed — the design row stays zero while off-design rows shift.
    """
    s = build_solver(**baseline(
        nspe = 3,
        efficiency_ratio_table = [[0.80, 0.95], [1.0, 1.0], [1.10, 0.98]],
        dpsis_table = [[0.0, 0.0, 0.0]],
    ))
    result = s.cspsd()
    assert result[0][1] == 0.0
    assert result[0][0] != 0.0
    assert result[0][2] != 0.0

def test8():
    """
    cspsd returns dpsis_table with shape (nsta, nspe).
    """
    nsta, nspe = 2, 3
    s = build_solver(
        nsta = nsta, nspe = nspe,
        phiref = [0.30, 0.32], psiref = [0.40, 0.42],
        bet2m = [[0.0], [0.0]], cb3mr = [0.0, 0.0],
        efficiency_ratio_table = [[0.80, 1.0], [1.0, 1.0], [1.10, 1.0]],
        um2 = [500.0, 500.0], um3 = [500.0, 500.0],
        area2 = [1.0, 1.0], area3 = [1.0, 1.0],
        cpref = [0.24, 0.24],
        dpsis_table = [[0.0] * nspe for _ in range(nsta)],
    )
    result = s.cspsd()
    assert len(result) == nsta
    assert len(result[0]) == nspe
