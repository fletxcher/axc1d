from src.python.solver import AXC1DSolver

solver = AXC1DSolver()

"""
Test Cases:
  test0 — XYZ
  test1 — XYZ
  test2 — XYZ
  test3 — XYZ
  test4 — XYZ
  test5 — XYZ
  test6 — XYZ
  test7 — XYZ
  test8 — XYZ
"""

def test0():
    """
    XYZ
    """
    assert solver.cml(rotor_tip = 1, rotor_hub = 1) == 1.0

def test1():
    """
    XYZ
    """
    assert solver.cml(rotor_tip = 2, rotor_hub = 2) == 2.0

def test2():
    """
    XYZ
    """
    assert solver.cml(rotor_tip = 3, rotor_hub = 3) == 3.0

def test3():
    """
    XYZ
    """
    assert solver.cml(rotor_tip = 4, rotor_hub = 4) == 4.0

def test4():
    """
    XYZ
    """
    assert solver.cml(rotor_tip = 5, rotor_hub = 5) == 5.0

def test5():
    """
    XYZ
    """
    assert solver.cml(rotor_tip = 6, rotor_hub = 6) == 6.0

def test6():
    """
    XYZ
    """
    assert solver.cml(rotor_tip = 7, rotor_hub = 7) == 7.0

def test7():
    """
    XYZ
    """
    assert solver.cml(rotor_tip = 8, rotor_hub = 8) == 8.0

def test8():
    """
    XYZ
    """
    assert solver.cml(rotor_tip = 9, rotor_hub = 9) == 9.0
