import copy
import logging
from src.python.solver import AXC1DSolver

"""
Test Cases:
  test0 — stall-side parabola: phi well below design
  test1 — stall boundary: phi exactly at phi_stall (60% of design)
  test2 — stall-side midpoint: phi between stall and design
  test3 — peak: phi exactly at design (eta must equal eta_d)
  test4 — choke-side midpoint: phi between design and choke
  test5 — choke boundary: phi exactly at phi_choke (140% of design)
  test6 — choke-side clamp: phi above choke (xx clamped to 1.0)
  test7 — pre-filled slots are preserved and not overwritten
  test8 — two stages, two speeds (multi-dimensional correctness)
"""

def build_solver(nsta, nspe, npts, phiref, etaref, phides, etades):
    """
    Build and return a solver for each given scenario.
    """
    s = AXC1DSolver(logger = logging.getLogger("cseta"))
    s.logger.addHandler(logging.NullHandler())
    s.nsta    = nsta
    s.nspe    = nspe
    s.npts    = npts
    s.phiref  = list(phiref)
    s.etaref  = list(etaref)
    s.phides  = copy.deepcopy(phides)
    s.etades  = copy.deepcopy(etades)
    return s

def eta_stall_side(phi, phi_d, eta_d):
    """
    Reference: stall-side parabola.
    """
    phi_s = phi_d * 0.6
    eta_s = 0.9 * eta_d
    xx    = min(1.0, max(0.0, (phi_d - phi) / (phi_d - phi_s)))
    return max(0.0, eta_d - (eta_d - eta_s) * xx ** 2)

def eta_choke_side(phi, phi_d, eta_d):
    """
    Reference: choke-side parabola.
    """
    phi_c = phi_d * 1.4
    eta_c = 0.8 * eta_d
    xx    = min(1.0, max(0.0, (phi - phi_d) / (phi_c - phi_d)))
    return max(0.0, eta_d - (eta_d - eta_c) * xx ** 2)

def test0():
    """
    Stall side — phi well below design (phi = 0.20, phi_d = 0.45).
    """
    phi_d, eta_d = 0.45, 0.85
    phi          = 0.20
    s = build_solver(
        nsta = 1, nspe = 1, npts = 1,
        phiref=[phi_d], etaref=[eta_d],
        phides=[[[phi]]],
        etades=[[[0.0]]],
    )
    result = s.cseta()
    expected = eta_stall_side(phi, phi_d, eta_d)
    assert result[0][0][0] == expected

def test1():
    """
    Stall boundary — phi exactly at phi_stall = phi_d * 0.6.
    """
    phi_d, eta_d = 0.45, 0.85
    phi          = phi_d * 0.6      
    s = build_solver(
        nsta = 1, nspe = 1, npts = 1,
        phiref=[phi_d], etaref=[eta_d],
        phides=[[[phi]]],
        etades=[[[0.0]]],
    )
    result = s.cseta()
    expected = eta_stall_side(phi, phi_d, eta_d)
    assert result[0][0][0] == expected

def test2():
    """
    Stall-side midpoint — phi halfway between stall and design.
    """
    phi_d, eta_d = 0.45, 0.85
    phi          = (phi_d * 0.6 + phi_d) / 2.0    
    s = build_solver(
        nsta = 1, nspe = 1, npts = 1,
        phiref=[phi_d], etaref=[eta_d],
        phides=[[[phi]]],
        etades=[[[0.0]]],
    )
    result = s.cseta()
    expected = eta_stall_side(phi, phi_d, eta_d)
    assert result[0][0][0] == expected

def test3():
    """
    Peak — phi exactly at design point must return eta_d unchanged.
    """
    phi_d, eta_d = 0.45, 0.85
    s = build_solver(
        nsta = 1, nspe = 1, npts = 1,
        phiref=[phi_d], etaref=[eta_d],
        phides=[[[phi_d]]],
        etades=[[[0.0]]],
    )
    result = s.cseta()
    assert result[0][0][0] == eta_d


def test4():
    """
    Choke-side midpoint — phi halfway between design and choke.
    """
    phi_d, eta_d = 0.45, 0.85
    phi          = (phi_d + phi_d * 1.4) / 2.0     
    s = build_solver(
        nsta = 1, nspe = 1, npts = 1,
        phiref = [phi_d], etaref = [eta_d],
        phides = [[[phi]]],
        etades = [[[0.0]]],
    )
    result = s.cseta()
    expected = eta_choke_side(phi, phi_d, eta_d)
    assert result[0][0][0] == expected

def test5():
    """
    Choke boundary — phi exactly at phi_choke = phi_d * 1.4.
    """
    phi_d, eta_d = 0.45, 0.85
    phi          = phi_d * 1.4   
    s = build_solver(
        nsta = 1, nspe = 1, npts = 1,
        phiref=[phi_d], etaref=[eta_d],
        phides=[[[phi]]],
        etades=[[[0.0]]],
    )
    result = s.cseta()
    expected = eta_choke_side(phi, phi_d, eta_d)
    assert result[0][0][0] == expected

def test6():
    """
    Beyond choke — phi above choke is clamped (xx = 1, eta stays at eta_c).
    """
    phi_d, eta_d = 0.45, 0.85
    phi          = 0.80             
    s = build_solver(
        nsta = 1, nspe = 1, npts = 1,
        phiref=[phi_d], etaref=[eta_d],
        phides=[[[phi]]],
        etades=[[[0.0]]],
    )
    result = s.cseta()
    # xx is clamped to 1.0 so result equals the choke boundary value
    expected = eta_choke_side(phi, phi_d, eta_d)
    assert result[0][0][0] == expected

def test7():
    """
    Pre-filled etades slots must be preserved and not overwritten.
    """
    phi_d, eta_d   = 0.45, 0.85
    prefilled_eta  = 0.80
    phi_zero       = 0.36           
    s = build_solver(
        nsta = 1, nspe = 1, npts=2,
        phiref=[phi_d], etaref=[eta_d],
        phides=[[[phi_zero, phi_d]]],
        etades=[[[prefilled_eta, 0.0]]], 
    )
    result = s.cseta()
    assert result[0][0][0] == prefilled_eta
    assert result[0][0][1] == eta_d

def test8():
    """
    Two stages, two speeds — every (i, j, k) cell must be correct.
    """
    phiref = [0.40, 0.50]
    etaref = [0.85, 0.87]
    nsta, nspe, npts = 2, 2, 4

    phides = [[[0.28, 0.36, 0.44, 0.56], [0.28, 0.36, 0.44, 0.56]], [[0.35, 0.45, 0.55, 0.65], [0.35, 0.45, 0.55, 0.65]]]
    etades_in = [[[0.0] * npts for _ in range(nspe)],[[0.0] * npts for _ in range(nspe)]]

    s = build_solver(nsta, nspe, npts, phiref, etaref, phides, etades_in)
    result = s.cseta()

    for i in range(nsta):
        phi_d = phiref[i]
        eta_d = etaref[i]
        for j in range(nspe):
            for k in range(npts):
                phi = phides[i][j][k]
                expected = (eta_stall_side(phi, phi_d, eta_d) if phi <= phi_d else eta_choke_side(phi, phi_d, eta_d))
                assert result[i][j][k] == expected, (f"Mismatch at stage = {i} speed = {j} point = {k}:\n phi = {phi}, recieved = {result[i][j][k]}, expected = {expected}")