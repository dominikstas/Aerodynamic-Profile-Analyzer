import numpy as np

def interpolate_coefficients(profile_name: str, angle: float, profiles_data: dict) -> tuple[float, float]:
    """
    Interpolates lift (CL) and drag (CD) coefficients for the given angle of attack.
    
    Args:
        profile_name: Name of the NACA profile (e.g., "NACA 2412")
        angle: Angle of attack in degrees
        profiles_data: Dictionary containing aerodynamic data for various profiles
    
    Returns:
        tuple containing (CL, CD) - interpolated lift and drag coefficients
    """
    if profile_name not in profiles_data:
        raise ValueError(f"Profile {profile_name} not found in the provided data")
    
    profile_data = profiles_data[profile_name]
    alpha_values = profile_data["alpha"]
    CL_values = profile_data["CL"]
    CD_values = profile_data["CD"]
    
    # Interpolate CL and CD values for the given angle of attack
    CL = np.interp(angle, alpha_values, CL_values)
    CD = np.interp(angle, alpha_values, CD_values)
    
    return CL, CD

def calculate_forces(CL: float, CD: float, V: float, rho: float, S: float) -> tuple[float, float]:
    """
    Calculates lift (L) and drag (D) forces based on aerodynamic coefficients and flight parameters.
    
    Args:
        CL: Lift coefficient
        CD: Drag coefficient
        V: Airspeed in m/s
        rho: Air density in kg/m³
        S: Wing area in m²
    
    Returns:
        tuple containing (L, D) - lift and drag forces in Newtons
    """
    # Dynamic pressure q = 0.5 * rho * V²
    q = 0.5 * rho * V**2
    
    # Calculate lift and drag forces
    lift = CL * q * S      # L = CL * q * S
    drag = CD * q * S      # D = CD * q * S
    
    return lift, drag

def analyze_airfoil(alpha: float, V: float, rho: float, S: float, profile_name: str, profiles_data: dict) -> dict:
    """
    Performs a complete analysis of an airfoil at given flight conditions.
    
    Args:
        alpha: Angle of attack in degrees
        V: Airspeed in m/s
        rho: Air density in kg/m³
        S: Wing area in m²
        profile_name: Name of the NACA profile
        profiles_data: Dictionary containing aerodynamic data for various profiles
    
    Returns:
        Dictionary containing the analysis results:
        {
            "profile": profile name,
            "alpha": angle of attack,
            "CL": lift coefficient,
            "CD": drag coefficient,
            "lift": lift force in Newtons,
            "drag": drag force in Newtons,
            "L_D_ratio": lift-to-drag ratio
        }
    """
    # Interpolate aerodynamic coefficients
    CL, CD = interpolate_coefficients(profile_name, alpha, profiles_data)
    
    # Calculate forces
    lift, drag = calculate_forces(CL, CD, V, rho, S)
    
    # Calculate lift-to-drag ratio
    L_D_ratio = lift / drag if drag != 0 else float('inf')
    
    # Compile results
    results = {
        "profile": profile_name,
        "alpha": alpha,
        "CL": CL,
        "CD": CD,
        "lift": lift,
        "drag": drag,
        "L_D_ratio": L_D_ratio,
        "dynamic_pressure": 0.5 * rho * V**2
    }
    
    return results

# Example usage
if __name__ == "__main__":
    # This is just for demonstration/testing purposes
    # In a real application, this data would be imported from naca_data.py
    sample_profiles_data = {
        "NACA 2412": {
            "alpha": [-10, -5, 0, 5, 10, 15, 20],
            "CL": [-0.6, -0.1, 0.4, 0.9, 1.3, 1.5, 1.2],
            "CD": [0.035, 0.012, 0.008, 0.012, 0.035, 0.068, 0.12]
        }
    }
    
    # Test the analyze_airfoil function
    result = analyze_airfoil(
        alpha=5.0,
        V=30.0,
        rho=1.225,
        S=15.0,
        profile_name="NACA 2412",
        profiles_data=sample_profiles_data
    )
    
    # Print results
    print("Analysis Results:")
    for key, value in result.items():
        print(f"{key}: {value}")