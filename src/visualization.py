"""
Visualization Module
====================
Provides clean, publication-ready Matplotlib plots for:
1. 2D Earth and Satellite Orbit Diagram (with satellite marker and velocity vector).
2. Altitude vs. Orbital Velocity Trend Curve.
3. Altitude vs. Orbital Period Trend Curve.
4. Altitude vs. Gravitational Acceleration Curve.
"""

import math
from typing import Optional, Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

from .orbital_calculations import (
    EARTH_RADIUS_KM,
    GEO_ALTITUDE_KM,
    calculate_orbital_radius,
    calculate_orbital_velocity,
    calculate_orbital_period,
    calculate_gravitational_acceleration,
    generate_altitude_sweep,
)

# Styling constants for sleek aerospace visualization
STYLE_CONFIG = {
    "bg_color": "#0E1117",         # Streamlit dark theme matching
    "card_bg": "#1A1C23",
    "text_color": "#E6EDF3",
    "muted_text": "#8B949E",
    "grid_color": "#30363D",
    "earth_color": "#1F6FEB",
    "earth_edge": "#58A6FF",
    "orbit1_color": "#00F0FF",     # Electric Cyan
    "orbit2_color": "#FF7B72",     # Coral Pink
    "geo_color": "#7EE787",        # Soft Green
}


def _apply_dark_style(ax: plt.Axes, fig: plt.Figure) -> None:
    """Helper to apply consistent dark aerospace styling to matplotlib axes."""
    fig.patch.set_facecolor(STYLE_CONFIG["bg_color"])
    ax.set_facecolor(STYLE_CONFIG["card_bg"])
    ax.tick_params(colors=STYLE_CONFIG["text_color"], labelsize=9)
    ax.xaxis.label.set_color(STYLE_CONFIG["text_color"])
    ax.yaxis.label.set_color(STYLE_CONFIG["text_color"])
    ax.title.set_color(STYLE_CONFIG["text_color"])
    for spine in ax.spines.values():
        spine.set_color(STYLE_CONFIG["grid_color"])
        spine.set_linewidth(1.0)
    ax.grid(True, color=STYLE_CONFIG["grid_color"], linestyle="--", linewidth=0.6, alpha=0.7)


def plot_circular_orbit(
    alt1_km: float,
    name1: str = "Primary Satellite",
    sat1_angle_deg: float = 45.0,
    alt2_km: Optional[float] = None,
    name2: Optional[str] = "Comparison Satellite",
    sat2_angle_deg: float = 135.0,
    show_geo_ring: bool = False,
) -> plt.Figure:
    """
    Plots a 2D to-scale diagram of Earth and circular satellite orbit(s).
    
    Parameters:
        alt1_km: Altitude of Orbit 1 in km.
        name1: Label for Orbit 1 satellite.
        sat1_angle_deg: Angular position of Satellite 1 along orbit (0 - 360 deg).
        alt2_km: Optional altitude of Orbit 2 in km.
        name2: Label for Orbit 2 satellite.
        sat2_angle_deg: Angular position of Satellite 2 along orbit.
        show_geo_ring: Whether to show the GEO reference ring.
        
    Returns:
        Matplotlib Figure object.
    """
    fig, ax = plt.subplots(figsize=(7.5, 7.5), dpi=120)
    _apply_dark_style(ax, fig)
    
    r1_km = calculate_orbital_radius(alt1_km)
    v1_km_s = calculate_orbital_velocity(alt1_km)
    
    # Draw Earth to scale
    earth = patches.Circle(
        (0, 0),
        EARTH_RADIUS_KM,
        facecolor=STYLE_CONFIG["earth_color"],
        edgecolor=STYLE_CONFIG["earth_edge"],
        linewidth=2.0,
        alpha=0.85,
        label=f"Earth (R = {EARTH_RADIUS_KM:,.0f} km)",
        zorder=3
    )
    ax.add_patch(earth)
    
    # Atmosphere glow ring (first 100 km)
    atmo = patches.Circle(
        (0, 0),
        EARTH_RADIUS_KM + 100,
        facecolor="none",
        edgecolor="#79C0FF",
        linestyle=":",
        linewidth=1.0,
        alpha=0.5,
        label="Atmosphere (~100 km)",
        zorder=2
    )
    ax.add_patch(atmo)
    
    # Draw Primary Orbit 1 Circle
    orbit1_circle = patches.Circle(
        (0, 0),
        r1_km,
        facecolor="none",
        edgecolor=STYLE_CONFIG["orbit1_color"],
        linestyle="-",
        linewidth=2.0,
        alpha=0.9,
        label=f"{name1} Orbit (h={alt1_km:,.0f} km, r={r1_km:,.0f} km)",
        zorder=4
    )
    ax.add_patch(orbit1_circle)
    
    # Satellite 1 Position
    theta1_rad = math.radians(sat1_angle_deg)
    sat1_x = r1_km * math.cos(theta1_rad)
    sat1_y = r1_km * math.sin(theta1_rad)
    ax.scatter(
        [sat1_x], [sat1_y],
        color=STYLE_CONFIG["orbit1_color"],
        s=120,
        edgecolors="#FFFFFF",
        linewidth=1.8,
        zorder=6,
        label=f"{name1} Position"
    )
    
    # Velocity vector arrow for Satellite 1 (tangent to orbit, counter-clockwise)
    # Velocity direction = theta + 90 degrees
    arrow_scale = r1_km * 0.18
    v_dir_x = -math.sin(theta1_rad) * arrow_scale
    v_dir_y = math.cos(theta1_rad) * arrow_scale
    ax.arrow(
        sat1_x, sat1_y, v_dir_x, v_dir_y,
        color=STYLE_CONFIG["orbit1_color"],
        width=r1_km * 0.008,
        head_width=r1_km * 0.04,
        head_length=r1_km * 0.05,
        length_includes_head=True,
        zorder=7
    )
    ax.text(
        sat1_x + v_dir_x * 1.15, sat1_y + v_dir_y * 1.15,
        f" v1 = {v1_km_s:.2f} km/s",
        color=STYLE_CONFIG["orbit1_color"],
        fontsize=9,
        fontweight="bold",
        zorder=8
    )
    
    # Optional Comparison Orbit 2
    if alt2_km is not None and alt2_km > 0:
        r2_km = calculate_orbital_radius(alt2_km)
        v2_km_s = calculate_orbital_velocity(alt2_km)
        
        orbit2_circle = patches.Circle(
            (0, 0),
            r2_km,
            facecolor="none",
            edgecolor=STYLE_CONFIG["orbit2_color"],
            linestyle="--",
            linewidth=2.0,
            alpha=0.9,
            label=f"{name2} Orbit (h={alt2_km:,.0f} km, r={r2_km:,.0f} km)",
            zorder=4
        )
        ax.add_patch(orbit2_circle)
        
        theta2_rad = math.radians(sat2_angle_deg)
        sat2_x = r2_km * math.cos(theta2_rad)
        sat2_y = r2_km * math.sin(theta2_rad)
        ax.scatter(
            [sat2_x], [sat2_y],
            color=STYLE_CONFIG["orbit2_color"],
            s=100,
            marker="s",
            edgecolors="#FFFFFF",
            linewidth=1.6,
            zorder=6,
            label=f"{name2} Position"
        )
        
        # Velocity arrow for satellite 2
        arrow2_scale = r2_km * 0.18
        v2_dir_x = -math.sin(theta2_rad) * arrow2_scale
        v2_dir_y = math.cos(theta2_rad) * arrow2_scale
        ax.arrow(
            sat2_x, sat2_y, v2_dir_x, v2_dir_y,
            color=STYLE_CONFIG["orbit2_color"],
            width=r2_km * 0.008,
            head_width=r2_km * 0.04,
            head_length=r2_km * 0.05,
            length_includes_head=True,
            zorder=7
        )
        ax.text(
            sat2_x + v2_dir_x * 1.15, sat2_y + v2_dir_y * 1.15,
            f" v2 = {v2_km_s:.2f} km/s",
            color=STYLE_CONFIG["orbit2_color"],
            fontsize=9,
            fontweight="bold",
            zorder=8
        )
    
    # Optional GEO ring reference
    if show_geo_ring:
        geo_r = calculate_orbital_radius(GEO_ALTITUDE_KM)
        geo_circle = patches.Circle(
            (0, 0),
            geo_r,
            facecolor="none",
            edgecolor=STYLE_CONFIG["geo_color"],
            linestyle=":",
            linewidth=1.2,
            alpha=0.6,
            label=f"GEO Reference Ring (~{GEO_ALTITUDE_KM:,.0f} km)",
            zorder=3
        )
        ax.add_patch(geo_circle)
    
    # Determine maximum plot boundary with a 20% margin
    max_radius = r1_km
    if alt2_km is not None:
        max_radius = max(max_radius, calculate_orbital_radius(alt2_km))
    if show_geo_ring:
        max_radius = max(max_radius, calculate_orbital_radius(GEO_ALTITUDE_KM))
        
    limit = max(max_radius * 1.25, EARTH_RADIUS_KM * 1.5)
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_aspect("equal", adjustable="box")
    
    ax.set_title("Circular Orbital Trajectory Around Earth (To Scale)", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("X Distance (km)", fontsize=10, labelpad=8)
    ax.set_ylabel("Y Distance (km)", fontsize=10, labelpad=8)
    
    # Format axis tick labels with commas
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda val, loc: f"{int(val):,}"))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, loc: f"{int(val):,}"))
    
    # Clean legend positioned outside or upper-left
    leg = ax.legend(
        loc="upper right",
        facecolor=STYLE_CONFIG["card_bg"],
        edgecolor=STYLE_CONFIG["grid_color"],
        fontsize=8.5,
        labelcolor=STYLE_CONFIG["text_color"]
    )
    leg.get_frame().set_alpha(0.85)
    
    plt.tight_layout()
    return fig


def plot_altitude_vs_velocity(
    current_alt1_km: float,
    current_alt2_km: Optional[float] = None,
    max_sweep_alt_km: float = 40000.0,
) -> plt.Figure:
    """
    Plots the continuous curve of Orbital Velocity vs. Altitude.
    Highlights current user-selected orbit(s).
    
    Formula: v = sqrt(mu / (R + h))
    """
    sweep_max = max(max_sweep_alt_km, current_alt1_km * 1.25)
    if current_alt2_km:
        sweep_max = max(sweep_max, current_alt2_km * 1.25)
        
    data = generate_altitude_sweep(min_alt_km=100.0, max_alt_km=sweep_max, num_points=400)
    
    fig, ax = plt.subplots(figsize=(7.5, 4.5), dpi=120)
    _apply_dark_style(ax, fig)
    
    # Plot curve
    ax.plot(
        data["altitudes_km"],
        data["velocities_km_s"],
        color=STYLE_CONFIG["orbit1_color"],
        linewidth=2.2,
        label=r"Orbital Velocity: $v = \sqrt{\frac{\mu}{R_E + h}}$"
    )
    
    # Highlight Orbit 1
    v1 = calculate_orbital_velocity(current_alt1_km)
    ax.scatter(
        [current_alt1_km], [v1],
        color=STYLE_CONFIG["orbit1_color"],
        s=110,
        zorder=5,
        edgecolors="#FFFFFF",
        linewidth=1.8,
        label=f"Orbit 1: {v1:.2f} km/s @ {current_alt1_km:,.0f} km"
    )
    # Drop lines to axes
    ax.vlines(current_alt1_km, 0, v1, color=STYLE_CONFIG["orbit1_color"], linestyle=":", alpha=0.7)
    ax.hlines(v1, 0, current_alt1_km, color=STYLE_CONFIG["orbit1_color"], linestyle=":", alpha=0.7)
    
    # Highlight Orbit 2 if present
    if current_alt2_km is not None and current_alt2_km > 0:
        v2 = calculate_orbital_velocity(current_alt2_km)
        ax.scatter(
            [current_alt2_km], [v2],
            color=STYLE_CONFIG["orbit2_color"],
            s=110,
            marker="s",
            zorder=5,
            edgecolors="#FFFFFF",
            linewidth=1.8,
            label=f"Orbit 2: {v2:.2f} km/s @ {current_alt2_km:,.0f} km"
        )
        ax.vlines(current_alt2_km, 0, v2, color=STYLE_CONFIG["orbit2_color"], linestyle=":", alpha=0.7)
        ax.hlines(v2, 0, current_alt2_km, color=STYLE_CONFIG["orbit2_color"], linestyle=":", alpha=0.7)
    
    # Regime boundaries (LEO = 2000 km, GEO = 35786 km)
    if sweep_max >= 2500:
        ax.axvline(2000, color="#8B949E", linestyle="--", linewidth=1.0, alpha=0.6)
        ax.text(2100, 7.2, "LEO / MEO Boundary (2,000 km)", color="#8B949E", fontsize=8)
    if sweep_max >= 36000:
        ax.axvline(GEO_ALTITUDE_KM, color=STYLE_CONFIG["geo_color"], linestyle="--", linewidth=1.0, alpha=0.6)
        ax.text(GEO_ALTITUDE_KM + 500, 3.5, "GEO (35,786 km)", color=STYLE_CONFIG["geo_color"], fontsize=8)
        
    ax.set_title("Altitude vs. Circular Orbital Velocity", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Altitude above Earth surface $h$ (km)", fontsize=10)
    ax.set_ylabel("Orbital Velocity $v$ (km/s)", fontsize=10)
    ax.set_xlim(0, sweep_max)
    ax.set_ylim(0, 8.5)
    
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda val, loc: f"{int(val):,}"))
    
    leg = ax.legend(loc="upper right", facecolor=STYLE_CONFIG["card_bg"], edgecolor=STYLE_CONFIG["grid_color"], fontsize=8.5)
    leg.get_frame().set_alpha(0.85)
    
    plt.tight_layout()
    return fig


def plot_altitude_vs_period(
    current_alt1_km: float,
    current_alt2_km: Optional[float] = None,
    max_sweep_alt_km: float = 40000.0,
    unit: str = "hours",  # "hours" or "minutes"
) -> plt.Figure:
    """
    Plots the continuous curve of Orbital Period vs. Altitude (Kepler's 3rd Law).
    Highlights current user-selected orbit(s).
    
    Formula: T = 2 * pi * sqrt((R + h)^3 / mu)
    """
    sweep_max = max(max_sweep_alt_km, current_alt1_km * 1.25)
    if current_alt2_km:
        sweep_max = max(sweep_max, current_alt2_km * 1.25)
        
    data = generate_altitude_sweep(min_alt_km=100.0, max_alt_km=sweep_max, num_points=400)
    
    fig, ax = plt.subplots(figsize=(7.5, 4.5), dpi=120)
    _apply_dark_style(ax, fig)
    
    y_values = data["periods_hours"] if unit == "hours" else data["periods_minutes"]
    unit_label = "Hours" if unit == "hours" else "Minutes"
    scale_factor = 3600.0 if unit == "hours" else 60.0
    
    # Plot curve
    ax.plot(
        data["altitudes_km"],
        y_values,
        color="#A371F7",
        linewidth=2.2,
        label=r"Orbital Period: $T = 2\pi\sqrt{\frac{r^3}{\mu}}$ (Kepler's 3rd Law)"
    )
    
    # Highlight Orbit 1
    t1 = calculate_orbital_period(current_alt1_km) / scale_factor
    ax.scatter(
        [current_alt1_km], [t1],
        color=STYLE_CONFIG["orbit1_color"],
        s=110,
        zorder=5,
        edgecolors="#FFFFFF",
        linewidth=1.8,
        label=f"Orbit 1: {t1:.2f} {unit_label} @ {current_alt1_km:,.0f} km"
    )
    ax.vlines(current_alt1_km, 0, t1, color=STYLE_CONFIG["orbit1_color"], linestyle=":", alpha=0.7)
    ax.hlines(t1, 0, current_alt1_km, color=STYLE_CONFIG["orbit1_color"], linestyle=":", alpha=0.7)
    
    # Highlight Orbit 2
    if current_alt2_km is not None and current_alt2_km > 0:
        t2 = calculate_orbital_period(current_alt2_km) / scale_factor
        ax.scatter(
            [current_alt2_km], [t2],
            color=STYLE_CONFIG["orbit2_color"],
            s=110,
            marker="s",
            zorder=5,
            edgecolors="#FFFFFF",
            linewidth=1.8,
            label=f"Orbit 2: {t2:.2f} {unit_label} @ {current_alt2_km:,.0f} km"
        )
        ax.vlines(current_alt2_km, 0, t2, color=STYLE_CONFIG["orbit2_color"], linestyle=":", alpha=0.7)
        ax.hlines(t2, 0, current_alt2_km, color=STYLE_CONFIG["orbit2_color"], linestyle=":", alpha=0.7)
    
    # Reference GEO line
    if sweep_max >= 36000:
        geo_y = 23.93 if unit == "hours" else 1436.0
        ax.axhline(geo_y, color=STYLE_CONFIG["geo_color"], linestyle="--", linewidth=1.0, alpha=0.6)
        ax.text(sweep_max * 0.05, geo_y * 1.03, f"24-Hour Geostationary Line ({geo_y:.1f} {unit_label})", color=STYLE_CONFIG["geo_color"], fontsize=8)
        
    ax.set_title(f"Altitude vs. Orbital Period ({unit_label})", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Altitude above Earth surface $h$ (km)", fontsize=10)
    ax.set_ylabel(f"Orbital Period $T$ ({unit_label})", fontsize=10)
    ax.set_xlim(0, sweep_max)
    ax.set_ylim(0, max(y_values) * 1.1)
    
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda val, loc: f"{int(val):,}"))
    
    leg = ax.legend(loc="upper left", facecolor=STYLE_CONFIG["card_bg"], edgecolor=STYLE_CONFIG["grid_color"], fontsize=8.5)
    leg.get_frame().set_alpha(0.85)
    
    plt.tight_layout()
    return fig


def plot_altitude_vs_gravity(
    current_alt1_km: float,
    current_alt2_km: Optional[float] = None,
    max_sweep_alt_km: float = 40000.0,
) -> plt.Figure:
    """
    Plots the continuous curve of Gravitational Acceleration vs. Altitude.
    
    Formula: g(h) = mu / (R + h)^2
    """
    sweep_max = max(max_sweep_alt_km, current_alt1_km * 1.25)
    if current_alt2_km:
        sweep_max = max(sweep_max, current_alt2_km * 1.25)
        
    data = generate_altitude_sweep(min_alt_km=100.0, max_alt_km=sweep_max, num_points=400)
    
    fig, ax = plt.subplots(figsize=(7.5, 4.5), dpi=120)
    _apply_dark_style(ax, fig)
    
    ax.plot(
        data["altitudes_km"],
        data["gravity_m_s2"],
        color="#F2CC60",
        linewidth=2.2,
        label=r"Gravitational Acceleration: $g = \frac{\mu}{(R_E + h)^2}$"
    )
    
    g1 = calculate_gravitational_acceleration(current_alt1_km)
    ax.scatter(
        [current_alt1_km], [g1],
        color=STYLE_CONFIG["orbit1_color"],
        s=110,
        zorder=5,
        edgecolors="#FFFFFF",
        linewidth=1.8,
        label=f"Orbit 1: {g1:.2f} m/s² @ {current_alt1_km:,.0f} km"
    )
    ax.vlines(current_alt1_km, 0, g1, color=STYLE_CONFIG["orbit1_color"], linestyle=":", alpha=0.7)
    ax.hlines(g1, 0, current_alt1_km, color=STYLE_CONFIG["orbit1_color"], linestyle=":", alpha=0.7)
    
    if current_alt2_km is not None and current_alt2_km > 0:
        g2 = calculate_gravitational_acceleration(current_alt2_km)
        ax.scatter(
            [current_alt2_km], [g2],
            color=STYLE_CONFIG["orbit2_color"],
            s=110,
            marker="s",
            zorder=5,
            edgecolors="#FFFFFF",
            linewidth=1.8,
            label=f"Orbit 2: {g2:.2f} m/s² @ {current_alt2_km:,.0f} km"
        )
        ax.vlines(current_alt2_km, 0, g2, color=STYLE_CONFIG["orbit2_color"], linestyle=":", alpha=0.7)
        ax.hlines(g2, 0, current_alt2_km, color=STYLE_CONFIG["orbit2_color"], linestyle=":", alpha=0.7)
        
    ax.set_title("Altitude vs. Gravitational Acceleration (Inverse Square Law)", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Altitude above Earth surface $h$ (km)", fontsize=10)
    ax.set_ylabel("Gravitational Acceleration $g$ (m/s²)", fontsize=10)
    ax.set_xlim(0, sweep_max)
    ax.set_ylim(0, 10.5)
    
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda val, loc: f"{int(val):,}"))
    
    leg = ax.legend(loc="upper right", facecolor=STYLE_CONFIG["card_bg"], edgecolor=STYLE_CONFIG["grid_color"], fontsize=8.5)
    leg.get_frame().set_alpha(0.85)
    
    plt.tight_layout()
    return fig
