import math
import logging
from src.python.solver import AXC1DSolver

specific_heat_coefficients = [0.23747e+00, 0.21962e-04, -0.87791e-07, 0.13991e-09, -0.78056e-13, 0.15043e-16]

"""
Test Cases:
  test0 — pre-filled psides slot is preserved and not overwritten
  test1 — phi below 0.001 short-circuits to psides = 0.0
  test2 — non-pre-filled slot at design phi is filled with a finite ψ value
  test3 — ψ is clamped to the range [0.0, 1.0]
  test4 — small computed ψ (≤ 0.01) is replaced by psi_d * 0.5
  test5 — phi_d = 0 short-circuits the vz2m scaling (vz2m used directly)
  test6 — um3 = 0 falls back to psi_d for that slot
  test7 — multi-stage: per-stage psides arrays are independent
  test8 — cspsi returns the psides nested list with correct shape
"""

def build_solver(nsta, nspe, npts, phiref, psiref, phides, psides, vz2m, um2, um3, area2, area3, cpref, bet2m, cb3mr):
    """
    Build and return a solver for each given scenario.
    """
    s = AXC1DSolver(logger = logging.getLogger("cspsi"))
    s.logger.addHandler(logging.NullHandler())
    s.nsta                       = nsta
    s.nspe                       = nspe
    s.npts                       = npts
    s.phiref                     = list(phiref)
    s.psiref                     = list(psiref)
    s.phides                     = [[[v for v in pt] for pt in stg] for stg in phides]
    s.psides                     = [[[v for v in pt] for pt in stg] for stg in psides]
    s.vz2m                       = [list(row) for row in vz2m]
    s.um2                        = list(um2)
    s.um3                        = list(um3)
    s.area2                      = list(area2)
    s.area3                      = list(area3)
    s.cpref                      = list(cpref)
    s.bet2m                      = [list(row) for row in bet2m]
    s.cb3mr                      = list(cb3mr)
    s.p0                         = 2116.224
    s.t0                         = 518.67
    s.rg                         = 53.34
    s.drdevp                     = 0.0
    s.gj                         = 32.1740 * 778.12
    s.specific_heat_coefficients = list(specific_heat_coefficients)
    return s

def baseline(**overrides):
    """
    Reference: a balanced single-stage configuration where the inner iteration
    converges quickly (b2 = b3 = 0, um2 = um3).
    """
    base = dict(
        nsta = 1, nspe = 1, npts = 1,
        phiref = [0.30], psiref = [0.40],
        phides = [[[0.30]]], psides = [[[0.0]]],
        vz2m = [[150.0]],
        um2 = [500.0], um3 = [500.0],
        area2 = [1.0], area3 = [1.0],
        cpref = [0.24],
        bet2m = [[0.0]], cb3mr = [0.0],
    )
    base.update(overrides)
    return base

def test0():
    """
    Pre-filled psides slot is preserved and not overwritten.
    """
    s = build_solver(**baseline(psides = [[[0.55]]]))
    result = s.cspsi()
    assert result[0][0][0] == 0.55

def test1():
    """
    phi below 0.001 short-circuits to psides = 0.0.
    """
    s = build_solver(**baseline(phides = [[[0.0005]]]))
    result = s.cspsi()
    assert result[0][0][0] == 0.0

def test2():
    """
    Non-pre-filled slot at design phi is filled with a finite ψ value.
    """
    s = build_solver(**baseline())
    result = s.cspsi()
    assert 0.0 <= result[0][0][0] <= 1.0
    assert result[0][0][0] != 0.0

def test3():
    """
    ψ is clamped to the range [0.0, 1.0] under extreme inputs.
    """
    s = build_solver(**baseline(um3 = [10000.0]))
    result = s.cspsi()
    assert 0.0 <= result[0][0][0] <= 1.0

def test4():
    """
    Small computed ψ (≤ 0.01) is replaced by psi_d * 0.5.
    """
    psi_d = 0.40
    s = build_solver(**baseline(psiref = [psi_d]))
    result = s.cspsi()
    assert result[0][0][0] == psi_d * 0.5

def test5():
    """
    phi_d = 0 short-circuits the vz2m scaling (vz2m used directly).
    """
    s = build_solver(**baseline(phiref = [0.0]))
    result = s.cspsi()
    assert 0.0 <= result[0][0][0] <= 1.0

def test6():
    """
    um3 = 0 falls back to psi_d directly via the `if um3 > 0` guard.
    """
    psi_d = 0.40
    s = build_solver(**baseline(
        psiref = [psi_d],
        um3 = [0.0],
    ))
    result = s.cspsi()
    assert result[0][0][0] == psi_d

def test7():
    """
    Multi-stage — per-stage psides arrays remain independent.
    """
    s = build_solver(**baseline(
        nsta = 2,
        phiref = [0.30, 0.32], psiref = [0.40, 0.42],
        phides = [[[0.30]], [[0.0005]]],
        psides = [[[0.0]], [[0.0]]],
        vz2m = [[150.0], [150.0]],
        um2 = [500.0, 500.0], um3 = [500.0, 500.0],
        area2 = [1.0, 1.0], area3 = [1.0, 1.0],
        cpref = [0.24, 0.24],
        bet2m = [[0.0], [0.0]], cb3mr = [0.0, 0.0],
    ))
    result = s.cspsi()
    assert result[1][0][0] == 0.0           # second stage hit the phi < 0.001 branch
    assert result[0][0][0] != 0.0           # first stage filled normally

def test8():
    """
    cspsi returns the psides nested list with shape (nsta, nspe, npts).
    """
    nsta, nspe, npts = 2, 2, 3
    s = build_solver(
        nsta = nsta, nspe = nspe, npts = npts,
        phiref = [0.30, 0.32], psiref = [0.40, 0.42],
        phides = [[[0.30] * npts for _ in range(nspe)], [[0.30] * npts for _ in range(nspe)]],
        psides = [[[0.0] * npts for _ in range(nspe)], [[0.0] * npts for _ in range(nspe)]],
        vz2m = [[150.0, 150.0], [150.0, 150.0]],
        um2 = [500.0, 500.0], um3 = [500.0, 500.0],
        area2 = [1.0, 1.0], area3 = [1.0, 1.0],
        cpref = [0.24, 0.24],
        bet2m = [[0.0, 0.0], [0.0, 0.0]], cb3mr = [0.0, 0.0],
    )
    result = s.cspsi()
    assert len(result) == nsta
    assert len(result[0]) == nspe
    assert len(result[0][0]) == npts
