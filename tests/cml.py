from src.python.solver import AXC1DSolver

solver = AXC1DSolver()

"""
Test Cases:
  test0 — Equal tip and hub radii of 1.0 → RMS radius equals 1.0
  test1 — Equal tip and hub radii of 2.0 → RMS radius equals 2.0
  test2 — Equal tip and hub radii of 3.0 → RMS radius equals 3.0
  test3 — Equal tip and hub radii of 4.0 → RMS radius equals 4.0
  test4 — Equal tip and hub radii of 5.0 → RMS radius equals 5.0
  test5 — Equal tip and hub radii of 6.0 → RMS radius equals 6.0
  test6 — Equal tip and hub radii of 7.0 → RMS radius equals 7.0
  test7 — Equal tip and hub radii of 8.0 → RMS radius equals 8.0
  test8 — Equal tip and hub radii of 9.0 → RMS radius equals 9.0
"""

def test0():
    """
    When tip and hub radii are both 1, the RMS meanline radius should equal 1.0.
    """
    assert solver.cml(rotor_tip = 1, rotor_hub = 1) == 1.0

def test1():
    """
    When tip and hub radii are both 2, the RMS meanline radius should equal 2.0.
    """
    assert solver.cml(rotor_tip = 2, rotor_hub = 2) == 2.0

def test2():
    """
    When tip and hub radii are both 3, the RMS meanline radius should equal 3.0.
    """
    assert solver.cml(rotor_tip = 3, rotor_hub = 3) == 3.0

def test3():
    """
    When tip and hub radii are both 4, the RMS meanline radius should equal 4.0.
    """
    assert solver.cml(rotor_tip = 4, rotor_hub = 4) == 4.0

def test4():
    """
    When tip and hub radii are both 5, the RMS meanline radius should equal 5.0.
    """
    assert solver.cml(rotor_tip = 5, rotor_hub = 5) == 5.0

def test5():
    """
    When tip and hub radii are both 6, the RMS meanline radius should equal 6.0.
    """
    assert solver.cml(rotor_tip = 6, rotor_hub = 6) == 6.0

def test6():
    """
    When tip and hub radii are both 7, the RMS meanline radius should equal 7.0.
    """
    assert solver.cml(rotor_tip = 7, rotor_hub = 7) == 7.0

def test7():
    """
    When tip and hub radii are both 8, the RMS meanline radius should equal 8.0.
    """
    assert solver.cml(rotor_tip = 8, rotor_hub = 8) == 8.0

def test8():
    """
    When tip and hub radii are both 9, the RMS meanline radius should equal 9.0.
    """
    assert solver.cml(rotor_tip = 9, rotor_hub = 9) == 9.0