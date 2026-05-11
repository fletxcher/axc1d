import logging
from src.python.solver import AXC1DSolver

specific_heat_coefficients = [0.23747e+00, 0.21962e-04, -0.87791e-07, 0.13991e-09, -0.78056e-13, 0.15043e-16]

"""
Test Cases:
  test0 — single stage, single speed, single point: stage record is well-formed
  test1 — within-range phi yields a non-stall result with PR > 1 and TR > 1
  test2 — empty phi map (all zeros) trips the design-window fallback STALL flag
  test3 — multi-speed sweep produces one operating point per (j, k) combination
  test4 — sweep_results length equals nspe * npts after the sweep
  test5 — eta_overall is clamped to the range [0.0, 1.0]
  test6 — tt and pt arrays are initialised at the inlet temperature / pressure
  test7 — multi-stage: each operating point carries one entry per stage
  test8 — csoupt returns a 6-tuple (sweep_results, phi_, psi_, eta_, tt, pt)
"""

def build_solver(nsta, nspe, npts, phi_, psi_, eta_, phiref, efficiency_ratio_table, um2, um3, area2, area3, bet2m, cb3mr, rsolm, spdphi = 0.0):
    """
    Build and return a solver for each given scenario.
    """
    s = AXC1DSolver(logger = logging.getLogger("csoupt"))
    s.logger.addHandler(logging.NullHandler())
    s.nsta                       = nsta
    s.nspe                       = nspe
    s.npts                       = npts
    s.phi_                       = [[[v for v in pt] for pt in stg] for stg in phi_]
    s.psi_                       = [[[v for v in pt] for pt in stg] for stg in psi_]
    s.eta_                       = [[[v for v in pt] for pt in stg] for stg in eta_]
    s.phiref                     = list(phiref)
    s.efficiency_ratio_table     = [list(row) for row in efficiency_ratio_table]
    s.um2                        = list(um2)
    s.um3                        = list(um3)
    s.area2                      = list(area2)
    s.area3                      = list(area3)
    s.bet2m                      = [list(row) for row in bet2m]
    s.cb3mr                      = list(cb3mr)
    s.rsolm                      = list(rsolm)
    s.spdphi                     = spdphi
    s.p0                         = 2116.224
    s.t0                         = 518.67
    s.rg                         = 53.34
    s.gj                         = 32.1740 * 778.12
    s.specific_heat_coefficients = list(specific_heat_coefficients)
    s.cpf(s.t0, s.specific_heat_coefficients)
    return s

def baseline(**overrides):
    """
    Reference: a single-stage, single-speed, single-point compressor map with
    a sane design phi sitting inside the map window so no stall/choke flag
    is raised by default.
    """
    base = dict(
        nsta = 1, nspe = 1, npts = 1,
        phi_ = [[[0.30]]],
        psi_ = [[[0.40]]],
        eta_ = [[[0.85]]],
        phiref = [0.30],
        efficiency_ratio_table = [[1.0, 1.0]],
        um2 = [500.0], um3 = [500.0],
        area2 = [1.0], area3 = [1.0],
        bet2m = [[0.0]], cb3mr = [0.0],
        rsolm = [1.0],
        spdphi = 0.0,
    )
    base.update(overrides)
    return base

def test0():
    """
    Single stage / speed / point — the stage record carries the expected keys.
    """
    s = build_solver(**baseline())
    sweep, *_ = s.csoupt()
    assert len(sweep) == 1
    stage = sweep[0]["stages"][0]
    for key in ("stage", "mass_flow", "phi", "psi", "eta", "pr", "tr", "tt_inlet", "tt_outlet", "pt_inlet", "pt_outlet"):
        assert key in stage

def test1():
    """
    Within-range phi yields a non-stall, non-choke result with PR > 1.
    """
    s = build_solver(**baseline())
    sweep, *_ = s.csoupt()
    op = sweep[0]
    assert op["pr_overall"] > 1.0
    assert op["tr_overall"] > 1.0

def test2():
    """
    Empty phi map (all zeros) trips the design-window fallback STALL flag.
    """
    s = build_solver(**baseline(
        phi_ = [[[0.0]]],
        phiref = [0.50],
        spdphi = 1.0,
    ))
    sweep, *_ = s.csoupt()
    op = sweep[0]
    assert op["pr_overall"]  == 0.0
    assert op["tr_overall"]  == 0.0
    assert op["eta_overall"] == 0.0

def test3():
    """
    Multi-speed sweep produces one operating point per (j, k) combination.
    """
    s = build_solver(**baseline(
        nspe = 2,
        phi_ = [[[0.30], [0.30]]],
        psi_ = [[[0.40], [0.40]]],
        eta_ = [[[0.85], [0.85]]],
        efficiency_ratio_table = [[1.0, 1.0], [0.90, 0.95]],
    ))
    sweep, *_ = s.csoupt()
    assert len(sweep) == 2
    assert sweep[0]["speed"] == 1.0
    assert sweep[1]["speed"] == 0.90

def test4():
    """
    sweep_results length equals nspe * npts after the sweep.
    """
    nsta, nspe, npts = 1, 2, 3
    s = build_solver(
        nsta = nsta, nspe = nspe, npts = npts,
        phi_ = [[[0.30] * npts for _ in range(nspe)]],
        psi_ = [[[0.40] * npts for _ in range(nspe)]],
        eta_ = [[[0.85] * npts for _ in range(nspe)]],
        phiref = [0.30],
        efficiency_ratio_table = [[1.0, 1.0], [0.90, 0.98]],
        um2 = [500.0], um3 = [500.0],
        area2 = [1.0], area3 = [1.0],
        bet2m = [[0.0]], cb3mr = [0.0],
        rsolm = [1.0],
    )
    sweep, *_ = s.csoupt()
    assert len(sweep) == nspe * npts

def test5():
    """
    eta_overall is clamped to the range [0.0, 1.0].
    """
    s = build_solver(**baseline())
    sweep, *_ = s.csoupt()
    op = sweep[0]
    assert 0.0 <= op["eta_overall"] <= 1.0

def test6():
    """
    tt and pt arrays are initialised at the inlet temperature / pressure.
    """
    s = build_solver(**baseline())
    _, _, _, _, tt, pt = s.csoupt()
    assert len(tt) == s.nsta + 1
    assert len(pt) == s.nsta + 1
    assert tt[0] == s.t0
    assert pt[0] == s.p0

def test7():
    """
    Multi-stage — each operating point carries one entry per stage.
    """
    nsta = 3
    s = build_solver(
        nsta = nsta, nspe = 1, npts = 1,
        phi_ = [[[0.30]], [[0.30]], [[0.30]]],
        psi_ = [[[0.40]], [[0.40]], [[0.40]]],
        eta_ = [[[0.85]], [[0.85]], [[0.85]]],
        phiref = [0.30, 0.30, 0.30],
        efficiency_ratio_table = [[1.0, 1.0]],
        um2 = [500.0, 500.0, 500.0],
        um3 = [500.0, 500.0, 500.0],
        area2 = [1.0, 1.0, 1.0],
        area3 = [1.0, 1.0, 1.0],
        bet2m = [[0.0], [0.0], [0.0]],
        cb3mr = [0.0, 0.0, 0.0],
        rsolm = [1.0, 1.0, 1.0],
    )
    sweep, *_ = s.csoupt()
    assert len(sweep[0]["stages"]) == nsta
    assert [st["stage"] for st in sweep[0]["stages"]] == [1, 2, 3]

def test8():
    """
    csoupt returns a 6-tuple (sweep_results, phi_, psi_, eta_, tt, pt).
    """
    s = build_solver(**baseline())
    result = s.csoupt()
    assert len(result) == 6
    sweep, phi_, psi_, eta_, tt, pt = result
    assert phi_ is s.phi_
    assert psi_ is s.psi_
    assert eta_ is s.eta_
