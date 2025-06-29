import numpy as np
from typing import Tuple, Dict, Any

def interpolate_coefficients(profile_name: str, angle: float, profiles_data: Dict) -> Tuple[float, float]:
    """
    Interpolates the lift (CL) and drag (CD) coefficients for a given angle of attack.

    Args:
        profile_name: Name of the NACA airfoil profile
        angle: Angle of attack in degrees
        profiles_data: Dictionary containing aerodynamic profile data

    Returns:
        Tuple (CL, CD) - interpolated lift and drag coefficients

    Raises:
        ValueError: If the profile is not found in the data
    """
    if profile_name not in profiles_data:
        available_profiles = ", ".join(profiles_data.keys())
        raise ValueError(f"Profile '{profile_name}' not found. "
                         f"Available profiles: {available_profiles}")

    profile_data = profiles_data[profile_name]

    # Linear interpolation of coefficients
    CL = np.interp(angle, profile_data["alpha"], profile_data["CL"])
    CD = np.interp(angle, profile_data["alpha"], profile_data["CD"])

    return float(CL), float(CD)

def calculate_aerodynamic_forces(CL: float, CD: float, velocity: float,
                                  density: float, area: float) -> Tuple[float, float]:
    """
    Calculates aerodynamic forces based on coefficients and flight conditions.

    Args:
        CL: Lift coefficient
        CD: Drag coefficient
        velocity: Flight speed [m/s]
        density: Air density [kg/m³]
        area: Wing surface area [m²]

    Returns:
        Tuple (L, D) - lift and drag forces in Newtons
    """
    # Dynamic pressure: q = 0.5 * ρ * V²
    dynamic_pressure = 0.5 * density * velocity**2

    # Aerodynamic forces
    lift_force = CL * dynamic_pressure * area
    drag_force = CD * dynamic_pressure * area

    return lift_force, drag_force

def calculate_reynolds_number(velocity: float, chord: float,
                               kinematic_viscosity: float = 1.48e-5) -> float:
    """
    Calculates the Reynolds number for the airfoil.

    Args:
        velocity: Flight speed [m/s]
        chord: Airfoil chord length [m]
        kinematic_viscosity: Kinematic viscosity of air [m²/s]

    Returns:
        Reynolds number (dimensionless)
    """
    return velocity * chord / kinematic_viscosity

def analyze_airfoil(alpha: float, V: float, rho: float, S: float,
                    profile_name: str, profiles_data: Dict,
                    chord: float = 1.0) -> Dict[str, Any]:
    """
    Performs a complete aerodynamic analysis of the airfoil.

    Args:
        alpha: Angle of attack [°]
        V: Flight speed [m/s]
        rho: Air density [kg/m³]
        S: Wing surface area [m²]
        profile_name: NACA profile name
        profiles_data: Aerodynamic data dictionary
        chord: Chord length of the airfoil [m]

    Returns:
        Dictionary with all calculated aerodynamic results
    """
    if V <= 0:
        raise ValueError("Velocity must be greater than zero.")
    if rho <= 0:
        raise ValueError("Air density must be greater than zero.")
    if S <= 0:
        raise ValueError("Wing area must be greater than zero.")

    # Interpolate aerodynamic coefficients
    CL, CD = interpolate_coefficients(profile_name, alpha, profiles_data)

    # Compute aerodynamic forces
    lift, drag = calculate_aerodynamic_forces(CL, CD, V, rho, S)

    # Lift-to-drag ratio
    L_D_ratio = lift / drag if drag > 0 else float('inf')

    # Reynolds number
    reynolds = calculate_reynolds_number(V, chord)

    # Dynamic pressure
    q = 0.5 * rho * V**2

    return {
        "profile": profile_name,
        "alpha": alpha,
        "CL": CL,
        "CD": CD,
        "lift": lift,
        "drag": drag,
        "L_D_ratio": L_D_ratio,
        "reynolds_number": reynolds,
        "dynamic_pressure": q,
        "velocity": V,
        "density": rho,
        "wing_area": S
    }

def get_stall_angle(profile_name: str, profiles_data: Dict) -> float:
    """
    Estimates the stall angle based on the maximum CL.

    Args:
        profile_name: Name of the airfoil profile
        profiles_data: Dictionary containing aerodynamic data

    Returns:
        Estimated stall angle [°]
    """
    if profile_name not in profiles_data:
        return None

    data = profiles_data[profile_name]
    max_cl_idx = np.argmax(data["CL"])
    stall_angle = data["alpha"][max_cl_idx]

    return stall_angle

def calculate_efficiency_metrics(results: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculates additional efficiency metrics based on analysis results.

    Args:
        results: Output dictionary from `analyze_airfoil`

    Returns:
        Dictionary containing efficiency metrics
    """
    CL = results["CL"]
    CD = results["CD"]

    return {
        "glide_ratio": results["L_D_ratio"],
        "CL_CD_ratio": CL / CD if CD > 0 else float('inf'),
        "drag_efficiency": CL**1.5 / CD if CD > 0 else float('inf'),
        "power_factor": CL**3 / CD**2 if CD > 0 else float('inf')
    }
