import math
import logging
from src.python.solver import AXC1DSolver

specific_heat_coefficients = [0.23747e+00, 0.21962e-04, -0.87791e-07, 0.13991e-09, -0.78056e-13, 0.15043e-16]

"""
Test Cases:
  test0 — etaref pass-through: a nonzero etades[0][0][0] becomes etaref[0]
  test1 — etaref default: a zero etades[0][0][0] falls back to 0.85
  test2 — phiref equals vz2 / um2 for a baseline single-stage geometry
  test3 — phiref equals 0.0 when um2 = 0 (degenerate geometry)
  test4 — vz2m[0][0] equals desflo / (rho2 * area2[0])
  test5 — rdfm falls back to 0.5 when rsolm = 0
  test6 — rdfm falls back to 0.5 when desflo = 0 (w2 = 0 with b2 = 0)
  test7 — multi-stage etaref reflects per-stage etades values
  test8 — cspref returns a tuple of 17 reference performance arrays
"""

def build_solver(nsta, nspe, npts, p0, t0, rg, desflo, area2, area3, um2, um3, bet2m, cb3mr, sk2m, rsolm, etades):
    """
    Build and return a solver for each given scenario.
    """
    s = AXC1DSolver(logger = logging.getLogger("cspref"))
    s.logger.addHandler(logging.NullHandler())
    s.nsta                       = nsta
    s.nspe                       = nspe
    s.npts                       = npts
    s.p0                         = p0
    s.t0                         = t0
    s.rg                         = rg
    s.desflo                     = desflo
    s.area2                      = list(area2)
    s.area3                      = list(area3)
    s.um2                        = list(um2)
    s.um3                        = list(um3)
    s.bet2m                      = [list(row) for row in bet2m]
    s.cb3mr                      = list(cb3mr)
    s.sk2m                       = list(sk2m)
    s.rsolm                      = list(rsolm)
    s.etades                     = [[[v for v in pt] for pt in stg] for stg in etades]
    s.gj                         = 32.1740 * 778.12
    s.specific_heat_coefficients = list(specific_heat_coefficients)
    return s

def baseline(**overrides):
    """
    Reference: a balanced single-stage configuration (um2 = um3, b2 = b3 = 0)
    so the iterative outlet solver converges immediately at zero work.
    """
    base = dict(
        nsta = 1, nspe = 1, npts = 1,
        p0 = 2116.224, t0 = 518.67, rg = 53.34, desflo = 10.0,
        area2 = [1.0], area3 = [1.0],
        um2 = [500.0], um3 = [500.0],
        bet2m = [[0.0]], cb3mr = [0.0],
        sk2m = [0.0], rsolm = [1.0],
        etades = [[[0.85]]],
    )
    base.update(overrides)
    return base

def test0():
    """
    etaref pass-through — a nonzero etades[0][0][0] is preserved as etaref[0].
    """
    s = build_solver(**baseline(etades = [[[0.92]]]))
    result = s.cspref()
    assert result[2][0] == 0.92

def test1():
    """
    etaref default — a zero etades[0][0][0] falls back to 0.85.
    """
    s = build_solver(**baseline(etades = [[[0.0]]]))
    result = s.cspref()
    assert result[2][0] == 0.85

def test2():
    """
    phiref equals vz2 / um2 for a baseline single-stage geometry.
    """
    s = build_solver(**baseline())
    result = s.cspref()
    rho2     = s.p0 / (s.rg * s.t0)
    vz2      = s.desflo / (rho2 * s.area2[0])
    expected = vz2 / s.um2[0]
    assert result[0][0] == expected

def test3():
    """
    phiref equals 0.0 when um2 = 0 (degenerate geometry, divide-by-zero guard).
    """
    s = build_solver(**baseline(um2 = [0.0]))
    result = s.cspref()
    assert result[0][0] == 0.0

def test4():
    """
    vz2m[0][0] equals desflo / (rho2 * area2[0]).
    """
    s = build_solver(**baseline())
    result = s.cspref()
    rho2     = s.p0 / (s.rg * s.t0)
    expected = s.desflo / (rho2 * s.area2[0])
    assert result[10][0][0] == expected

def test5():
    """
    rdfm falls back to 0.5 when rsolm = 0 (solidity guard).
    """
    s = build_solver(**baseline(rsolm = [0.0]))
    result = s.cspref()
    assert result[8][0] == 0.5

def test6():
    """
    rdfm falls back to 0.5 when desflo = 0 (w2 = 0 with b2 = 0).
    """
    s = build_solver(**baseline(desflo = 0.0))
    result = s.cspref()
    assert result[8][0] == 0.5

def test7():
    """
    Multi-stage — etaref reflects per-stage etades values.
    """
    s = build_solver(**baseline(
        nsta = 2,
        area2 = [1.0, 1.0], area3 = [1.0, 1.0],
        um2 = [500.0, 500.0], um3 = [500.0, 500.0],
        bet2m = [[0.0], [0.0]], cb3mr = [0.0, 0.0],
        sk2m = [0.0, 0.0], rsolm = [1.0, 1.0],
        etades = [[[0.86]], [[0.0]]],
    ))
    result = s.cspref()
    assert result[2][0] == 0.86
    assert result[2][1] == 0.85

def test8():
    """
    cspref returns a tuple of 17 reference performance arrays.
    """
    s = build_solver(**baseline())
    result = s.cspref()
    assert len(result) == 17
