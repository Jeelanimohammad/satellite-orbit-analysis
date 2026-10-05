"""
Satellite Orbit Analysis and Visualization System
Core Source Package
"""

from .orbital_calculations import (
    EARTH_RADIUS_KM,
    EARTH_MU_KM3_S2,
    calculate_orbital_radius,
    calculate_orbital_velocity,
    calculate_orbital_period,
    calculate_gravitational_acceleration,
    calculate_orbits_per_day,
    calculate_orbit_summary,
    compare_orbits,
    get_orbit_regime,
)

__all__ = [
    "EARTH_RADIUS_KM",
    "EARTH_MU_KM3_S2",
    "calculate_orbital_radius",
    "calculate_orbital_velocity",
    "calculate_orbital_period",
    "calculate_gravitational_acceleration",
    "calculate_orbits_per_day",
    "calculate_orbit_summary",
    "compare_orbits",
    "get_orbit_regime",
]
