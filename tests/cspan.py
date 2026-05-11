import math
import logging
from src.python.solver import AXC1DSolver

specific_heat_coefficients = [0.23747e+00, 0.21962e-04, -0.87791e-07, 0.13991e-09, -0.78056e-13, 0.15043e-16]

"""
Test Cases:
  test0 — no blade reset (cb2m = cb2mr = cb3mr = 0) leaves all deltas at zero
  test1 — positive rotor inlet reset (cb2m > 0) yields a nonzero dphia / dpsia
  test2 — positive rotor outlet reset (cb3mr > 0) yields a nonzero dpsia
  test3 — deta always stays at 0.0 (function does not modify efficiency)
  test4 — um2 = 0 falls back to vz2m[i][0] for the new axial velocity
  test5 — drdevg = 1.0 applies the deviation correction (delta differs from off)
  test6 — multi-stage resets are computed independently per stage
  test7 — stages with all-zero resets in a multi-stage array stay zero
  test8 — cspan returns a 3-tuple (dphia, dpsia, deta) of length nsta each
"""

def build_solver(nsta, phiref, psiref, bet2m, cb2m, cb2mr, cb3mr, vz2m, um2, um3, area2, area3, cpref, drdevg = 0.0):
    """
    Build and return a solver for each given scenario.
    """
    s = AXC1DSolver(logger = logging.getLogger("cspan"))
    s.logger.addHandler(logging.NullHandler())
    s.nsta                       = nsta
    s.phiref                     = list(phiref)
    s.psiref                     = list(psiref)
    s.bet2m                      = [list(row) for row in bet2m]
    s.cb2m                       = list(cb2m)
    s.cb2mr                      = list(cb2mr)
    s.cb3mr                      = list(cb3mr)
    s.vz2m                       = [list(row) for row in vz2m]
    s.um2                        = list(um2)
    s.um3                        = list(um3)
    s.area2                      = list(area2)
    s.area3                      = list(area3)
    s.cpref                      = list(cpref)
    s.drdevg                     = drdevg
    s.p0                         = 2116.224
    s.t0                         = 518.67
    s.rg                         = 53.34
    s.gj                         = 32.1740 * 778.12
    s.specific_heat_coefficients = list(specific_heat_coefficients)
    return s

def baseline(**overrides):
    """
    Reference: a single-stage configuration with all blade resets zero so the
    early-return branch of cspan is exercised.  Tests override the resets.
    """
    base = dict(
        nsta = 1,
        phiref = [0.30], psiref = [0.40],
        bet2m = [[0.10]],
        cb2m = [0.0], cb2mr = [0.0], cb3mr = [0.0],
        vz2m = [[150.0]],
        um2 = [500.0], um3 = [500.0],
        area2 = [1.0], area3 = [1.0],
        cpref = [0.24],
        drdevg = 0.0,
    )
    base.update(overrides)
    return base

def test0():
    """
    No blade reset — all three delta arrays remain at zero for every stage.
    """
    s = build_solver(**baseline())
    dphia, dpsia, deta = s.cspan()
    assert dphia[0] == 0.0
    assert dpsia[0] == 0.0
    assert deta[0]  == 0.0

def test1():
    """
    Positive rotor inlet reset (cb2m > 0) yields a nonzero dphia / dpsia.
    """
    s = build_solver(**baseline(cb2m = [0.05]))
    dphia, dpsia, deta = s.cspan()
    assert dphia[0] != 0.0
    assert math.isfinite(dphia[0])
    assert math.isfinite(dpsia[0])

def test2():
    """
    Positive rotor outlet reset (cb3mr > 0) yields a nonzero dpsia.
    """
    s = build_solver(**baseline(cb3mr = [0.05]))
    dphia, dpsia, deta = s.cspan()
    assert math.isfinite(dpsia[0])
    assert dpsia[0] != 0.0

def test3():
    """
    deta is always 0.0 (the function does not modify efficiency).
    """
    s = build_solver(**baseline(cb2m = [0.05], cb2mr = [0.02], cb3mr = [0.03]))
    _, _, deta = s.cspan()
    assert deta[0] == 0.0

def test4():
    """
    um2 = 0 — phi_new collapses to phi_d so dphia stays at 0 for that stage.
    """
    s = build_solver(**baseline(cb2m = [0.05], um2 = [0.0]))
    dphia, _, _ = s.cspan()
    assert dphia[0] == 0.0

def test5():
    """
    drdevg = 1.0 — the rotor-outlet deviation correction shifts dpsia.
    """
    s_off = build_solver(**baseline(cb2m = [0.05], drdevg = 0.0))
    s_on  = build_solver(**baseline(cb2m = [0.05], drdevg = 1.0))
    _, dpsia_off, _ = s_off.cspan()
    _, dpsia_on,  _ = s_on.cspan()
    assert dpsia_off[0] != dpsia_on[0]

def test6():
    """
    Multi-stage — each stage's reset contribution is computed independently.
    """
    s = build_solver(**baseline(
        nsta = 2,
        phiref = [0.30, 0.32], psiref = [0.40, 0.42],
        bet2m = [[0.10], [0.12]],
        cb2m = [0.05, 0.03], cb2mr = [0.0, 0.0], cb3mr = [0.0, 0.0],
        vz2m = [[150.0], [160.0]],
        um2 = [500.0, 600.0], um3 = [500.0, 600.0],
        area2 = [1.0, 1.0], area3 = [1.0, 1.0],
        cpref = [0.24, 0.24],
    ))
    dphia, dpsia, _ = s.cspan()
    assert dphia[0] != 0.0
    assert dphia[1] != 0.0
    assert dphia[0] != dphia[1]

def test7():
    """
    Multi-stage — a stage with all-zero resets leaves its deltas at zero.
    """
    s = build_solver(**baseline(
        nsta = 2,
        phiref = [0.30, 0.32], psiref = [0.40, 0.42],
        bet2m = [[0.10], [0.12]],
        cb2m = [0.05, 0.0], cb2mr = [0.0, 0.0], cb3mr = [0.0, 0.0],
        vz2m = [[150.0], [160.0]],
        um2 = [500.0, 600.0], um3 = [500.0, 600.0],
        area2 = [1.0, 1.0], area3 = [1.0, 1.0],
        cpref = [0.24, 0.24],
    ))
    dphia, dpsia, deta = s.cspan()
    assert dphia[1] == 0.0
    assert dpsia[1] == 0.0
    assert deta[1]  == 0.0

def test8():
    """
    cspan returns a 3-tuple (dphia, dpsia, deta) of length nsta each.
    """
    nsta = 3
    s = build_solver(
        nsta = nsta,
        phiref = [0.30, 0.32, 0.34], psiref = [0.40, 0.42, 0.44],
        bet2m = [[0.10], [0.12], [0.14]],
        cb2m = [0.0, 0.0, 0.0], cb2mr = [0.0, 0.0, 0.0], cb3mr = [0.0, 0.0, 0.0],
        vz2m = [[150.0], [160.0], [170.0]],
        um2 = [500.0, 600.0, 700.0], um3 = [500.0, 600.0, 700.0],
        area2 = [1.0, 1.0, 1.0], area3 = [1.0, 1.0, 1.0],
        cpref = [0.24, 0.24, 0.24],
    )
    result = s.cspan()
    assert len(result) == 3
    assert len(result[0]) == nsta
    assert len(result[1]) == nsta
    assert len(result[2]) == nsta
