import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from calculations import aero_calculations as ac

dummy_data = {
    "NACA0012": {
        "alpha": [-5, 0, 5, 10],
        "CL": [-0.5, 0.0, 0.5, 1.0],
        "CD": [0.05, 0.02, 0.03, 0.07]
    }
}

def test_interpolate():
    cl, cd = ac.interpolate_coefficients("NACA0012", 2.5, dummy_data)
    assert round(cl, 2) == 0.25
    assert round(cd, 3) == 0.025

def test_forces():
    lift, drag = ac.calculate_aerodynamic_forces(CL=0.5, CD=0.02, velocity=30, density=1.2, area=10)
    assert lift > 0
    assert drag > 0

def test_reynolds():
    Re = ac.calculate_reynolds_number(velocity=30, chord=1)
    assert isinstance(Re, float)
    assert Re > 0
