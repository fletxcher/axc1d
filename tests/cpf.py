from src.python.solver import AXC1DSolver

solver = AXC1DSolver()

ru        = 1545.44
aj        = 778.12
mole_wt   = 28.970
dcp       = (ru / mole_wt) / aj

"""
Test Cases:
  test0 — Original test — standard sea-level temperature (518.67 R)
  test1 — Cold inlet — 400 R (representative of low-altitude cold-day condition)
  test2 — Moderate compressor inlet — 600 R
  test3 — Hot-day inlet — 700 R
  test4 — High-temperature stage outlet — 800 R
  test5 — Very high temperature — 1000 R (last compressor stage exit)
  test6 — Low fractional temperature — 350 R (extreme cold soak)
  test7 — Non-round temperature — 459.67 R (0 °F in Rankine)
  test8 — Non-round temperature — 671.67 R (212 °F / boiling point in Rankine)
"""

def test0():
    """
    Original test — standard sea-level temperature (518.67 R).
    """
    ts                         = 518.67
    specific_heat_coefficients = [0.23747e+00, 0.21962e-04, -0.87791e-07, 0.13991e-09, -0.78056e-13, 0.15043e-16]
    cp                         = specific_heat_coefficients[0] + specific_heat_coefficients[1]*ts + specific_heat_coefficients[2]*ts**2 + specific_heat_coefficients[3]*ts**3 + specific_heat_coefficients[4]*ts**4 + specific_heat_coefficients[5]*ts**5
    gamma                      = cp / (cp - dcp)
    gm1                        = gamma - 1.0
    assert solver.cpf(ts, specific_heat_coefficients) == (ts, cp, gamma, gm1, 1.0 / gm1, gamma / gm1, 1.0 / (gamma / gm1))

def test1():
    """
    Cold inlet — 400 R (representative of low-altitude cold-day condition).
    """
    ts                         = 400.0
    specific_heat_coefficients = [0.23747e+00, 0.21962e-04, -0.87791e-07, 0.13991e-09, -0.78056e-13, 0.15043e-16]
    cp                         = specific_heat_coefficients[0] + specific_heat_coefficients[1]*ts + specific_heat_coefficients[2]*ts**2 + specific_heat_coefficients[3]*ts**3 + specific_heat_coefficients[4]*ts**4 + specific_heat_coefficients[5]*ts**5
    gamma                      = cp / (cp - dcp)
    gm1                        = gamma - 1.0
    assert solver.cpf(ts, specific_heat_coefficients) == (ts, cp, gamma, gm1, 1.0 / gm1, gamma / gm1, 1.0 / (gamma / gm1))

def test2():
    """
    Moderate compressor inlet — 600 R.
    """
    ts                         = 600.0
    specific_heat_coefficients = [0.23747e+00, 0.21962e-04, -0.87791e-07, 0.13991e-09, -0.78056e-13, 0.15043e-16]
    cp                         = specific_heat_coefficients[0] + specific_heat_coefficients[1]*ts + specific_heat_coefficients[2]*ts**2 + specific_heat_coefficients[3]*ts**3 + specific_heat_coefficients[4]*ts**4 + specific_heat_coefficients[5]*ts**5
    gamma                      = cp / (cp - dcp)
    gm1                        = gamma - 1.0
    assert solver.cpf(ts, specific_heat_coefficients) == (ts, cp, gamma, gm1, 1.0 / gm1, gamma / gm1, 1.0 / (gamma / gm1))

def test3():
    """
    Hot-day inlet — 700 R.
    """
    ts                         = 700.0
    specific_heat_coefficients = [0.23747e+00, 0.21962e-04, -0.87791e-07, 0.13991e-09, -0.78056e-13, 0.15043e-16]
    cp                         = specific_heat_coefficients[0] + specific_heat_coefficients[1]*ts + specific_heat_coefficients[2]*ts**2 + specific_heat_coefficients[3]*ts**3 + specific_heat_coefficients[4]*ts**4 + specific_heat_coefficients[5]*ts**5
    gamma                      = cp / (cp - dcp)
    gm1                        = gamma - 1.0
    assert solver.cpf(ts, specific_heat_coefficients) == (ts, cp, gamma, gm1, 1.0 / gm1, gamma / gm1, 1.0 / (gamma / gm1))

def test4():
    """
    High-temperature stage outlet — 800 R.
    """
    ts                         = 800.0
    specific_heat_coefficients = [0.23747e+00, 0.21962e-04, -0.87791e-07, 0.13991e-09, -0.78056e-13, 0.15043e-16]
    cp                         = specific_heat_coefficients[0] + specific_heat_coefficients[1]*ts + specific_heat_coefficients[2]*ts**2 + specific_heat_coefficients[3]*ts**3 + specific_heat_coefficients[4]*ts**4 + specific_heat_coefficients[5]*ts**5
    gamma                      = cp / (cp - dcp)
    gm1                        = gamma - 1.0
    assert solver.cpf(ts, specific_heat_coefficients) == (ts, cp, gamma, gm1, 1.0 / gm1, gamma / gm1, 1.0 / (gamma / gm1))

def test5():
    """
    Very high temperature — 1000 R (last compressor stage exit).
    """
    ts                         = 1000.0
    specific_heat_coefficients = [0.23747e+00, 0.21962e-04, -0.87791e-07, 0.13991e-09, -0.78056e-13, 0.15043e-16]
    cp                         = specific_heat_coefficients[0] + specific_heat_coefficients[1]*ts + specific_heat_coefficients[2]*ts**2 + specific_heat_coefficients[3]*ts**3 + specific_heat_coefficients[4]*ts**4 + specific_heat_coefficients[5]*ts**5
    gamma                      = cp / (cp - dcp)
    gm1                        = gamma - 1.0
    assert solver.cpf(ts, specific_heat_coefficients) == (ts, cp, gamma, gm1, 1.0 / gm1, gamma / gm1, 1.0 / (gamma / gm1))


def test6():
    """
    Low fractional temperature — 350 R (extreme cold soak).
    """
    ts                         = 350.0
    specific_heat_coefficients = [0.23747e+00, 0.21962e-04, -0.87791e-07, 0.13991e-09, -0.78056e-13, 0.15043e-16]
    cp                         = specific_heat_coefficients[0] + specific_heat_coefficients[1]*ts + specific_heat_coefficients[2]*ts**2 + specific_heat_coefficients[3]*ts**3 + specific_heat_coefficients[4]*ts**4 + specific_heat_coefficients[5]*ts**5
    gamma                      = cp / (cp - dcp)
    gm1                        = gamma - 1.0
    assert solver.cpf(ts, specific_heat_coefficients) == (ts, cp, gamma, gm1, 1.0 / gm1, gamma / gm1, 1.0 / (gamma / gm1))

def test7():
    """
    Non-round temperature — 459.67 R (0 °F in Rankine).
    """
    ts                         = 459.67
    specific_heat_coefficients = [0.23747e+00, 0.21962e-04, -0.87791e-07, 0.13991e-09, -0.78056e-13, 0.15043e-16]
    cp                         = specific_heat_coefficients[0] + specific_heat_coefficients[1]*ts + specific_heat_coefficients[2]*ts**2 + specific_heat_coefficients[3]*ts**3 + specific_heat_coefficients[4]*ts**4 + specific_heat_coefficients[5]*ts**5
    gamma                      = cp / (cp - dcp)
    gm1                        = gamma - 1.0
    assert solver.cpf(ts, specific_heat_coefficients) == (ts, cp, gamma, gm1, 1.0 / gm1, gamma / gm1, 1.0 / (gamma / gm1))

def test8():
    """
    Non-round temperature — 671.67 R (212 °F / boiling point in Rankine).
    """
    ts                         = 671.67
    specific_heat_coefficients = [0.23747e+00, 0.21962e-04, -0.87791e-07, 0.13991e-09, -0.78056e-13, 0.15043e-16]
    cp                         = specific_heat_coefficients[0] + specific_heat_coefficients[1]*ts + specific_heat_coefficients[2]*ts**2 + specific_heat_coefficients[3]*ts**3 + specific_heat_coefficients[4]*ts**4 + specific_heat_coefficients[5]*ts**5
    gamma                      = cp / (cp - dcp)
    gm1                        = gamma - 1.0
    assert solver.cpf(ts, specific_heat_coefficients) == (ts, cp, gamma, gm1, 1.0 / gm1, gamma / gm1, 1.0 / (gamma / gm1))
