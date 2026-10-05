"""
Unit Tests for Orbital Calculations
===================================
Run with pytest:
    python -m pytest tests/
or simply:
    python tests/test_orbital_calculations.py
"""

import math
import unittest
import numpy as np

from src.orbital_calculations import (
    EARTH_RADIUS_KM,
    EARTH_MU_KM3_S2,
    GEO_ALTITUDE_KM,
    calculate_orbital_radius,
    calculate_orbital_velocity,
    calculate_orbital_period,
    calculate_gravitational_acceleration,
    calculate_orbits_per_day,
    get_orbit_regime,
    calculate_orbital_energy,
    calculate_orbit_summary,
    compare_orbits,
    generate_altitude_sweep,
    validate_altitude,
)


class TestOrbitalCalculations(unittest.TestCase):
    """Test suite verifying circular orbit calculations against known astrodynamics values."""

    def test_orbital_radius(self):
        """Test r = R_earth + h."""
        altitude = 400.0
        expected_radius = EARTH_RADIUS_KM + altitude
        actual_radius = calculate_orbital_radius(altitude)
        self.assertAlmostEqual(actual_radius, expected_radius, places=5)

    def test_iss_orbital_velocity(self):
        """
        Verify ISS velocity at ~408 km altitude.
        Expected: ~7.66 km/s (approx 27,600 km/h).
        """
        v_iss = calculate_orbital_velocity(408.0)
        self.assertGreater(v_iss, 7.60)
        self.assertLess(v_iss, 7.72)

    def test_iss_orbital_period(self):
        """
        Verify ISS orbital period at ~408 km.
        Expected: ~92.6 minutes (approx 5,560 seconds).
        """
        t_seconds = calculate_orbital_period(408.0)
        t_minutes = t_seconds / 60.0
        self.assertGreater(t_minutes, 91.0)
        self.assertLess(t_minutes, 94.0)

    def test_geostationary_orbit_characteristics(self):
        """
        Verify GEO altitude (~35,786 km).
        Expected:
        - Orbital period ~ 86,164 seconds (approx 23.93 hours = 1 sidereal day)
        - Orbital velocity ~ 3.075 km/s
        - Orbits per solar day ~ 1.00
        """
        t_geo = calculate_orbital_period(GEO_ALTITUDE_KM)
        t_geo_hours = t_geo / 3600.0
        v_geo = calculate_orbital_velocity(GEO_ALTITUDE_KM)
        orbits_per_day = calculate_orbits_per_day(t_geo)

        # Should be within 0.1 hour of 24 hours
        self.assertAlmostEqual(t_geo_hours, 23.93, delta=0.2)
        # Should be approximately 3.075 km/s
        self.assertAlmostEqual(v_geo, 3.075, delta=0.05)
        # Should complete ~1 orbit per day
        self.assertAlmostEqual(orbits_per_day, 1.0, delta=0.05)

    def test_gravitational_acceleration_at_iss(self):
        """
        Gravity at ISS altitude (408 km) is still ~8.6 to 8.8 m/s^2 (not zero!).
        This is an important physical check for the microgravity concept.
        """
        g_iss = calculate_gravitational_acceleration(408.0)
        self.assertGreater(g_iss, 8.5)
        self.assertLess(g_iss, 9.0)

    def test_keplers_third_law_constancy(self):
        """
        Verify Kepler's Third Law: (T^2 / r^3) = (4 * pi^2 / mu) = constant
        Check across several altitudes (200 km, 1000 km, 20000 km, 35786 km).
        """
        expected_ratio = (4.0 * (math.pi ** 2)) / EARTH_MU_KM3_S2
        test_altitudes = [200.0, 1000.0, 10000.0, 20200.0, 35786.0]

        for alt in test_altitudes:
            r = calculate_orbital_radius(alt)
            t = calculate_orbital_period(alt)
            ratio = (t ** 2) / (r ** 3)
            self.assertAlmostEqual(ratio, expected_ratio, places=7)

    def test_inverse_relationship_velocity_altitude(self):
        """Higher altitude orbits MUST have strictly lower orbital velocity."""
        altitudes = [200, 500, 2000, 20000, 35786]
        velocities = [calculate_orbital_velocity(h) for h in altitudes]
        for i in range(len(velocities) - 1):
            self.assertGreater(
                velocities[i],
                velocities[i + 1],
                f"Velocity at {altitudes[i]} km should be > velocity at {altitudes[i+1]} km"
            )

    def test_input_validation_negative_altitude(self):
        """Negative altitude must raise a ValueError."""
        with self.assertRaises(ValueError):
            calculate_orbital_radius(-100.0)

        with self.assertRaises(ValueError):
            calculate_orbital_velocity(-50.0)

    def test_input_validation_non_numeric(self):
        """Non-numeric input must raise a TypeError."""
        with self.assertRaises(TypeError):
            calculate_orbital_radius("high")  # type: ignore

    def test_input_validation_nan(self):
        """NaN values must raise a ValueError."""
        with self.assertRaises(ValueError):
            validate_altitude(float("nan"))

    def test_orbit_regimes(self):
        """Verify regime classification logic."""
        self.assertEqual(get_orbit_regime(100)["code"], "SUB")
        self.assertEqual(get_orbit_regime(408)["code"], "LEO")
        self.assertEqual(get_orbit_regime(20200)["code"], "MEO")
        self.assertEqual(get_orbit_regime(35786)["code"], "GEO")
        self.assertEqual(get_orbit_regime(60000)["code"], "HEO")

    def test_energy_calculations_with_mass(self):
        """Verify specific and total energy calculations when mass is provided."""
        mass = 1000.0  # 1000 kg satellite
        alt = 500.0
        energy = calculate_orbital_energy(alt, mass)
        
        # Total energy in a bound orbit must be negative
        self.assertLess(energy["specific_total_mj_kg"], 0)
        self.assertLess(energy["total_energy_gj"], 0)
        # Kinetic energy must be positive
        self.assertGreater(energy["specific_kinetic_mj_kg"], 0)
        # Specific KE should equal -0.5 * Specific PE (Virial theorem for 1/r potential)
        self.assertAlmostEqual(
            energy["specific_kinetic_mj_kg"],
            -0.5 * energy["specific_potential_mj_kg"],
            places=4
        )

    def test_altitude_sweep_generation(self):
        """Verify sweep returns matching length numpy arrays with valid data."""
        sweep = generate_altitude_sweep(min_alt_km=200, max_alt_km=1000, num_points=50)
        self.assertEqual(len(sweep["altitudes_km"]), 50)
        self.assertEqual(len(sweep["velocities_km_s"]), 50)
        self.assertEqual(len(sweep["periods_minutes"]), 50)
        self.assertTrue(np.all(sweep["velocities_km_s"] > 0))


if __name__ == "__main__":
    unittest.main()
