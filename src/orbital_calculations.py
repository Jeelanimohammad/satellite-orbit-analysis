"""
Orbital Calculations Module
===========================
This module provides standard circular-orbit mechanics calculations based on
Newton's law of universal gravitation and Kepler's laws of planetary motion.

Constants and Units:
- Altitude (h): Kilometers (km)
- Earth Radius (R): 6378.137 km (WGS-84 standard equatorial radius)
- Standard Gravitational Parameter (mu = G * M): 398600.4418 km^3 / s^2
- Earth Mass (M): 5.9722 x 10^24 kg
- Universal Gravitational Constant (G): 6.67430 x 10^-11 m^3 / (kg * s^2)
"""

import math
from typing import Dict, Any, Tuple, Optional
import numpy as np

# ============================================================================
# STANDARD PHYSICAL CONSTANTS
# ============================================================================
# Mean/Equatorial Earth radius in kilometers (WGS-84 model)
EARTH_RADIUS_KM: float = 6378.137

# Earth's standard gravitational parameter (mu = G * M_Earth) in km^3 / s^2
# Using mu directly avoids compounding floating-point rounding errors from G and M.
EARTH_MU_KM3_S2: float = 398600.4418

# Standard acceleration due to gravity at sea level (m / s^2)
G0_M_S2: float = 9.80665

# Earth mass in kilograms (for reference and mass-dependent force/energy)
EARTH_MASS_KG: float = 5.9722e24

# Universal gravitational constant in m^3 / (kg * s^2)
GRAVITATIONAL_CONSTANT_G: float = 6.67430e-11

# Sidereal day length in seconds (time for Earth to rotate 360 degrees relative to stars)
SIDEREAL_DAY_SECONDS: float = 86164.0905

# Standard GEO altitude in km where orbital period equals 1 sidereal day (~35,786 km)
GEO_ALTITUDE_KM: float = 35786.0


# ============================================================================
# VALIDATION UTILITIES
# ============================================================================
def validate_altitude(altitude_km: float, min_altitude: float = 0.0) -> None:
    """
    Validates that the input altitude is numeric and within a physically realistic range.
    
    Parameters:
        altitude_km: Satellite altitude above Earth's surface in kilometers.
        min_altitude: Minimum allowable altitude in kilometers (default 0.0).
        
    Raises:
        TypeError: If altitude is not an int or float.
        ValueError: If altitude is less than min_altitude or excessively large.
    """
    if not isinstance(altitude_km, (int, float, np.number)):
        raise TypeError(f"Altitude must be a number, got {type(altitude_km).__name__}")
    
    if math.isnan(altitude_km) or math.isinf(altitude_km):
        raise ValueError("Altitude must be a finite number.")
        
    if altitude_km < min_altitude:
        raise ValueError(
            f"Altitude must be >= {min_altitude} km. Provided value: {altitude_km} km. "
            "A satellite cannot orbit below Earth's surface or within the dense lower atmosphere."
        )
    
    # Cap at a reasonable interplanetary boundary for Earth-orbit analysis (1,000,000 km)
    if altitude_km > 1000000.0:
        raise ValueError(
            f"Altitude {altitude_km} km exceeds Earth's gravitational sphere of influence "
            "(Hill sphere ~1,500,000 km). Please enter an altitude under 1,000,000 km."
        )


# ============================================================================
# CORE ORBITAL CALCULATIONS (CIRCULAR ORBITS)
# ============================================================================
def calculate_orbital_radius(altitude_km: float) -> float:
    """
    Calculates total orbital radius from Earth's center.
    
    Formula:
        r = R_earth + h
        
    Parameters:
        altitude_km: Height above Earth's surface (h) in km.
        
    Returns:
        Orbital radius (r) from Earth's center in km.
    """
    validate_altitude(altitude_km)
    return EARTH_RADIUS_KM + altitude_km


def calculate_orbital_velocity(altitude_km: float) -> float:
    """
    Calculates circular orbital velocity (speed required to maintain a circular orbit).
    
    Formula:
        v = sqrt(mu / r)
        
    Derivation:
        Equating gravitational force to centripetal force:
        F_gravity = F_centripetal
        (G * M * m) / r^2 = (m * v^2) / r
        mu / r^2 = v^2 / r  =>  v = sqrt(mu / r)
        
    Parameters:
        altitude_km: Satellite altitude in km.
        
    Returns:
        Orbital speed in kilometers per second (km/s).
    """
    r_km = calculate_orbital_radius(altitude_km)
    velocity_km_s = math.sqrt(EARTH_MU_KM3_S2 / r_km)
    return velocity_km_s


def calculate_orbital_period(altitude_km: float) -> float:
    """
    Calculates the orbital period (time taken for one complete orbit around Earth).
    
    Formula:
        T = 2 * pi * sqrt(r^3 / mu)
        
    Derivation:
        Distance per orbit = 2 * pi * r
        Period T = Distance / Velocity = (2 * pi * r) / sqrt(mu / r)
        T = 2 * pi * sqrt(r^3 / mu)
        (This directly proves Kepler's Third Law: T^2 is proportional to r^3).
        
    Parameters:
        altitude_km: Satellite altitude in km.
        
    Returns:
        Orbital period in seconds.
    """
    r_km = calculate_orbital_radius(altitude_km)
    period_seconds = 2.0 * math.pi * math.sqrt((r_km ** 3) / EARTH_MU_KM3_S2)
    return period_seconds


def calculate_gravitational_acceleration(altitude_km: float) -> float:
    """
    Calculates local gravitational acceleration at the satellite's altitude.
    
    Formula:
        g(h) = mu / r^2  (in km/s^2)
        In standard SI (m/s^2): g = (mu_m3_s2) / (r_m)^2 = (mu * 10^9) / (r * 1000)^2
        Simplifies to: g(m/s^2) = (mu_km3_s2 / r_km^2) * 1000
        
    Parameters:
        altitude_km: Satellite altitude in km.
        
    Returns:
        Local gravitational acceleration in meters per second squared (m/s^2).
    """
    r_km = calculate_orbital_radius(altitude_km)
    g_m_s2 = (EARTH_MU_KM3_S2 / (r_km ** 2)) * 1000.0
    return g_m_s2


def calculate_orbits_per_day(period_seconds: float) -> float:
    """
    Calculates the number of complete orbits the satellite completes in one solar day (24 hours = 86,400 s).
    
    Parameters:
        period_seconds: Orbital period in seconds.
        
    Returns:
        Number of orbits completed per 24-hour day.
    """
    if period_seconds <= 0:
        raise ValueError("Orbital period must be positive.")
    return 86400.0 / period_seconds


def get_orbit_regime(altitude_km: float) -> Dict[str, str]:
    """
    Categorizes the orbit regime based on altitude and gives practical aerospace context.
    
    Regimes:
        - Sub-orbital: < 160 km (atmospheric reentry / rapid decay)
        - Low Earth Orbit (LEO): 160 km to 2,000 km
        - Medium Earth Orbit (MEO): 2,000 km to 35,700 km
        - Geostationary Orbit (GEO): 35,700 km to 35,900 km (~35,786 km)
        - High Earth Orbit (HEO): > 35,900 km
        
    Parameters:
        altitude_km: Satellite altitude in km.
        
    Returns:
        Dictionary with regime code, name, and practical description.
    """
    validate_altitude(altitude_km)
    
    if altitude_km < 160.0:
        return {
            "code": "SUB",
            "name": "Sub-orbital / Extreme Atmospheric Drag",
            "description": "Below 160 km, dense atmospheric drag causes rapid orbital decay within hours or days.",
            "examples": "Sounding rockets, Karman line (100 km), decaying debris."
        }
    elif altitude_km <= 2000.0:
        return {
            "code": "LEO",
            "name": "Low Earth Orbit (LEO)",
            "description": "Fast travel (~7.5-7.8 km/s), short periods (90-120 min). High resolution for Earth observation.",
            "examples": "ISS (408 km), Hubble (540 km), Starlink (~550 km), Earth observation satellites."
        }
    elif altitude_km < 35700.0:
        return {
            "code": "MEO",
            "name": "Medium Earth Orbit (MEO)",
            "description": "Between LEO and GEO. Large coverage footprint, stable environment used for global navigation.",
            "examples": "GPS (~20,200 km), Galileo (~23,222 km), GLONASS (~19,100 km)."
        }
    elif altitude_km <= 35900.0:
        return {
            "code": "GEO",
            "name": "Geostationary / Geosynchronous Orbit (GEO)",
            "description": "Orbital period matches Earth's rotation (23h 56m). Satellite stays fixed relative to a ground point.",
            "examples": "Weather satellites (GOES, INSAT), telecommunications, direct TV broadcast."
        }
    else:
        return {
            "code": "HEO",
            "name": "High Earth Orbit (HEO)",
            "description": "Beyond GEO altitude. Very long periods (> 24 hours), highly specialized scientific missions.",
            "examples": "Chandra X-Ray Observatory (apogee ~133,000 km), Vela satellites, Moon orbit (~384,400 km)."
        }


def calculate_orbital_energy(altitude_km: float, mass_kg: Optional[float] = None) -> Dict[str, float]:
    """
    Calculates specific mechanical energy and (if mass is provided) total mechanical energy.
    
    Formulas:
        Specific Kinetic Energy:    eps_k = 0.5 * v^2               (km^2 / s^2)
        Specific Potential Energy:  eps_p = -mu / r                 (km^2 / s^2)
        Specific Total Energy:      eps   = -mu / (2 * r)           (km^2 / s^2)
        
        If mass is provided (in kg):
        Values converted to Joules (J) or MegaJoules (MJ):
        1 km^2 / s^2 = 10^6 m^2 / s^2 = 10^6 J/kg = 1 MJ/kg.
        
    Parameters:
        altitude_km: Satellite altitude in km.
        mass_kg: Optional satellite mass in kilograms.
        
    Returns:
        Dictionary of energy components.
    """
    r_km = calculate_orbital_radius(altitude_km)
    v_km_s = calculate_orbital_velocity(altitude_km)
    
    # Specific energies (per unit mass)
    specific_ke_mj_kg = 0.5 * (v_km_s ** 2)              # MJ/kg
    specific_pe_mj_kg = -EARTH_MU_KM3_S2 / r_km          # MJ/kg
    specific_total_mj_kg = -EARTH_MU_KM3_S2 / (2.0 * r_km) # MJ/kg
    
    result = {
        "specific_kinetic_mj_kg": specific_ke_mj_kg,
        "specific_potential_mj_kg": specific_pe_mj_kg,
        "specific_total_mj_kg": specific_total_mj_kg,
    }
    
    if mass_kg is not None and mass_kg > 0:
        result["mass_kg"] = float(mass_kg)
        # Total energies in GigaJoules (GJ = 10^9 J = 10^3 MJ)
        result["kinetic_energy_gj"] = (specific_ke_mj_kg * mass_kg) / 1000.0
        result["potential_energy_gj"] = (specific_pe_mj_kg * mass_kg) / 1000.0
        result["total_energy_gj"] = (specific_total_mj_kg * mass_kg) / 1000.0
        
        # Gravitational force in Newtons: F = m * g(h)
        g_val = calculate_gravitational_acceleration(altitude_km)
        result["gravitational_force_n"] = mass_kg * g_val
        
    return result


def calculate_orbit_summary(altitude_km: float, mass_kg: Optional[float] = None) -> Dict[str, Any]:
    """
    Computes a complete, structured summary of all orbital parameters for a given altitude.
    
    Parameters:
        altitude_km: Satellite altitude in km.
        mass_kg: Optional satellite mass in kg.
        
    Returns:
        Dictionary with all primary and derived orbital parameters.
    """
    validate_altitude(altitude_km)
    
    r_km = calculate_orbital_radius(altitude_km)
    v_km_s = calculate_orbital_velocity(altitude_km)
    v_m_s = v_km_s * 1000.0
    v_km_h = v_km_s * 3600.0
    
    t_sec = calculate_orbital_period(altitude_km)
    t_min = t_sec / 60.0
    t_hr = t_sec / 3600.0
    
    g_h = calculate_gravitational_acceleration(altitude_km)
    g_ratio = (g_h / G0_M_S2) * 100.0  # Percentage of surface gravity
    
    orbits_day = calculate_orbits_per_day(t_sec)
    regime = get_orbit_regime(altitude_km)
    energy = calculate_orbital_energy(altitude_km, mass_kg)
    
    return {
        "altitude_km": float(altitude_km),
        "orbital_radius_km": round(r_km, 3),
        "earth_radius_km": EARTH_RADIUS_KM,
        "velocity_km_s": round(v_km_s, 4),
        "velocity_m_s": round(v_m_s, 2),
        "velocity_km_h": round(v_km_h, 2),
        "period_seconds": round(t_sec, 2),
        "period_minutes": round(t_min, 2),
        "period_hours": round(t_hr, 3),
        "gravitational_accel_m_s2": round(g_h, 3),
        "surface_gravity_percent": round(g_ratio, 2),
        "orbits_per_day": round(orbits_day, 2),
        "regime": regime,
        "energy": energy,
    }


def compare_orbits(alt1_km: float, alt2_km: float, mass1_kg: Optional[float] = None, mass2_kg: Optional[float] = None) -> Dict[str, Any]:
    """
    Compares two satellite orbits at different altitudes.
    
    Parameters:
        alt1_km: Altitude of Orbit 1 in km.
        alt2_km: Altitude of Orbit 2 in km.
        mass1_kg: Optional mass for Orbit 1 satellite.
        mass2_kg: Optional mass for Orbit 2 satellite.
        
    Returns:
        Dictionary containing individual summaries and delta/ratio metrics.
    """
    summary1 = calculate_orbit_summary(alt1_km, mass1_kg)
    summary2 = calculate_orbit_summary(alt2_km, mass2_kg)
    
    delta_alt = alt2_km - alt1_km
    delta_radius = summary2["orbital_radius_km"] - summary1["orbital_radius_km"]
    delta_v = summary2["velocity_km_s"] - summary1["velocity_km_s"]
    v_ratio = summary2["velocity_km_s"] / summary1["velocity_km_s"]
    
    delta_t_min = summary2["period_minutes"] - summary1["period_minutes"]
    t_ratio = summary2["period_seconds"] / summary1["period_seconds"]
    
    delta_g = summary2["gravitational_accel_m_s2"] - summary1["gravitational_accel_m_s2"]
    
    return {
        "orbit_1": summary1,
        "orbit_2": summary2,
        "deltas": {
            "altitude_diff_km": round(delta_alt, 2),
            "radius_diff_km": round(delta_radius, 2),
            "velocity_diff_km_s": round(delta_v, 4),
            "velocity_ratio": round(v_ratio, 4),
            "period_diff_minutes": round(delta_t_min, 2),
            "period_ratio": round(t_ratio, 4),
            "gravity_diff_m_s2": round(delta_g, 3),
        }
    }


def generate_altitude_sweep(min_alt_km: float = 160.0, max_alt_km: float = 40000.0, num_points: int = 400) -> Dict[str, np.ndarray]:
    """
    Generates numpy arrays of altitudes, radii, velocities, periods, and gravitational
    accelerations for plotting trends across orbit regimes.
    
    Parameters:
        min_alt_km: Starting altitude in km.
        max_alt_km: Ending altitude in km.
        num_points: Number of evaluation points.
        
    Returns:
        Dictionary of numpy arrays.
    """
    altitudes = np.linspace(min_alt_km, max_alt_km, num_points)
    radii = EARTH_RADIUS_KM + altitudes
    velocities = np.sqrt(EARTH_MU_KM3_S2 / radii)
    periods_sec = 2.0 * np.pi * np.sqrt((radii ** 3) / EARTH_MU_KM3_S2)
    periods_min = periods_sec / 60.0
    periods_hr = periods_sec / 3600.0
    gravity_m_s2 = (EARTH_MU_KM3_S2 / (radii ** 2)) * 1000.0
    
    return {
        "altitudes_km": altitudes,
        "radii_km": radii,
        "velocities_km_s": velocities,
        "periods_seconds": periods_sec,
        "periods_minutes": periods_min,
        "periods_hours": periods_hr,
        "gravity_m_s2": gravity_m_s2,
    }
