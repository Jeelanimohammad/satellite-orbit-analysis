"""
Satellite Orbit Analysis & Visualization System
===============================================
An interactive Streamlit application for calculating, analyzing, and visualizing
Keplerian circular satellite orbits around Earth.

Author: Mohammad Jeelani
Technologies: Python, NumPy, Matplotlib, Streamlit, Pandas
"""

import os
import sys
import math
import numpy as np
import pandas as pd
import streamlit as st

# Ensure local src directory is importable
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.orbital_calculations import (
    EARTH_RADIUS_KM,
    EARTH_MU_KM3_S2,
    GEO_ALTITUDE_KM,
    calculate_orbital_radius,
    calculate_orbital_velocity,
    calculate_orbital_period,
    calculate_gravitational_acceleration,
    calculate_orbits_per_day,
    calculate_orbit_summary,
    calculate_orbital_energy,
    compare_orbits,
    get_orbit_regime,
    validate_altitude,
)
from src.visualization import (
    plot_circular_orbit,
    plot_altitude_vs_velocity,
    plot_altitude_vs_period,
    plot_altitude_vs_gravity,
)

# ============================================================================
# PAGE CONFIGURATION & STYLING
# ============================================================================
st.set_page_config(
    page_title="Satellite Orbit Analysis System",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for clean modern aerospace cards and fonts
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #58A6FF;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #8B949E;
        margin-bottom: 1.2rem;
    }
    .metric-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #58A6FF;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #8B949E;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #7EE787;
        margin-top: 3px;
    }
    .info-box {
        background-color: #0D1117;
        border-left: 4px solid #58A6FF;
        padding: 12px 16px;
        border-radius: 4px;
        font-size: 0.92rem;
        color: #C9D1D9;
        margin-bottom: 15px;
    }
    .badge-leo {
        background-color: #238636;
        color: white;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================================
# DATASET LOADER
# ============================================================================
@st.cache_data
def load_sample_dataset() -> pd.DataFrame:
    """Loads reference satellite dataset from CSV."""
    csv_path = os.path.join(current_dir, "data", "sample_orbit_data.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    else:
        # Fallback dummy dataframe if file is somehow missing
        return pd.DataFrame([
            {"Satellite Name": "ISS", "Regime": "LEO", "Altitude_km": 408.0, "Velocity_km_s": 7.664, "Period_min": 92.68},
            {"Satellite Name": "GPS", "Regime": "MEO", "Altitude_km": 20200.0, "Velocity_km_s": 3.873, "Period_min": 719.27},
            {"Satellite Name": "GEO Comsat", "Regime": "GEO", "Altitude_km": 35786.0, "Velocity_km_s": 3.075, "Period_min": 1436.07},
        ])


sample_df = load_sample_dataset()

# ============================================================================
# SIDEBAR CONTROLS
# ============================================================================
st.sidebar.markdown("## 🛰️ Mission Parameters")
st.sidebar.caption("Configure satellite orbital conditions.")

# Preset Selection
orbit_presets = {
    "Custom Altitude": None,
    "ISS (Space Station) — 408 km [LEO]": 408.0,
    "Hubble Space Telescope — 540 km [LEO]": 540.0,
    "Starlink Constellation — 550 km [LEO]": 550.0,
    "Sentinel-6 Earth Observation — 1,336 km [LEO]": 1336.0,
    "GLONASS-M Navigation — 19,100 km [MEO]": 19100.0,
    "GPS Block III Navstar — 20,200 km [MEO]": 20200.0,
    "Galileo FOC Satellite — 23,222 km [MEO]": 23222.0,
    "Geostationary Comsat (GEO) — 35,786 km [GEO]": 35786.0,
    "Chandra X-Ray Observatory — 65,000 km [HEO]": 65000.0,
}

selected_preset = st.sidebar.selectbox("Choose a Mission Preset:", list(orbit_presets.keys()), index=1)

# Default altitude based on preset
default_alt = 408.0 if orbit_presets[selected_preset] is None else orbit_presets[selected_preset]

# Primary Satellite Altitude Input with validation
st.sidebar.markdown("### Primary Orbit (Orbit 1)")
primary_name = st.sidebar.text_input("Satellite Name:", value=selected_preset.split("—")[0].strip() if "—" in selected_preset else "My Satellite")

alt1_input = st.sidebar.number_input(
    "Altitude $h$ (km):",
    min_value=100.0,
    max_value=100000.0,
    value=float(default_alt),
    step=50.0,
    help="Distance between the satellite and Earth's surface in kilometers (minimum 100 km to clear dense atmosphere)."
)

# Optional Satellite Mass
use_mass = st.sidebar.checkbox("Include Satellite Mass (for Energy & Force)", value=True)
sat1_mass = None
if use_mass:
    sat1_mass = st.sidebar.number_input(
        "Satellite Mass $m$ (kg):",
        min_value=1.0,
        max_value=1000000.0,
        value=420000.0 if "ISS" in primary_name else 1200.0,
        step=100.0,
        help="Optional mass of the satellite in kilograms. For reference: ISS is ~420,000 kg, Starlink is ~300 kg."
    )

# Satellite Position Angle on Orbit (interactive animation slider)
sat1_angle = st.sidebar.slider(
    "Satellite Position Angle $\\theta$ (degrees):",
    min_value=0.0,
    max_value=360.0,
    value=45.0,
    step=5.0,
    help="Adjust to rotate the satellite position along its circular path."
)

st.sidebar.markdown("---")
# Comparison Orbit Options
st.sidebar.markdown("### Comparison Orbit (Orbit 2)")
enable_comparison = st.sidebar.checkbox("Compare with a Second Orbit", value=True)

alt2_input = None
primary_name_2 = "Comparison Orbit"
sat2_angle = 180.0
sat2_mass = None

if enable_comparison:
    comparison_preset = st.sidebar.selectbox(
        "Choose Comparison Preset:",
        [k for k in orbit_presets.keys() if orbit_presets[k] is not None],
        index=6  # Default to GPS (20,200 km)
    )
    comp_default_alt = orbit_presets[comparison_preset]
    
    primary_name_2 = st.sidebar.text_input("Comparison Name:", value=comparison_preset.split("—")[0].strip())
    alt2_input = st.sidebar.number_input(
        "Comparison Altitude $h_2$ (km):",
        min_value=100.0,
        max_value=100000.0,
        value=float(comp_default_alt),
        step=100.0
    )
    sat2_angle = st.sidebar.slider(
        "Orbit 2 Position Angle $\\theta_2$:",
        min_value=0.0,
        max_value=360.0,
        value=160.0,
        step=5.0
    )
    if use_mass:
        sat2_mass = st.sidebar.number_input(
            "Orbit 2 Mass (kg):",
            min_value=1.0,
            max_value=1000000.0,
            value=2200.0,
            step=100.0
        )

# Show reference GEO ring toggle
show_geo_ring = st.sidebar.checkbox("Show Geostationary Reference Ring (35,786 km)", value=True)

# ============================================================================
# MAIN APPLICATION INTERFACE
# ============================================================================
st.markdown('<div class="main-title">🛰️ Satellite Orbit Analysis & Visualization System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">A practical astrodynamics tool for Keplerian circular orbit calculation, parameter sensitivity, and mission regime comparison.</div>', unsafe_allow_html=True)

# Assumptions and context banner
st.markdown(
    """
    <div class="info-box">
    <strong>Theoretical Model Assumptions:</strong> This project evaluates ideal <strong>two-body Keplerian circular orbits</strong> ($e = 0$). 
    Earth is modeled as a spherically symmetric body with constant standard gravitational parameter 
    $\\mu = 398,600.4418\\text{ km}^3/\\text{s}^2$ and radius $R_E = 6,378.137\\text{ km}$. Atmospheric drag and perturbation effects ($J_2$, solar radiation pressure) are neglected.
    </div>
    """,
    unsafe_allow_html=True,
)

# Perform Core Calculations
try:
    orbit1_summary = calculate_orbit_summary(alt1_input, sat1_mass)
    if enable_comparison and alt2_input:
        orbit2_summary = calculate_orbit_summary(alt2_input, sat2_mass)
        comparison_results = compare_orbits(alt1_input, alt2_input, sat1_mass, sat2_mass)
    else:
        orbit2_summary = None
        comparison_results = None
except (ValueError, TypeError) as err:
    st.error(f"Input Validation Error: {err}")
    st.stop()

# ============================================================================
# TABS NAVIGATION
# ============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🛰️ Orbit Overview & Trajectory",
    "⚖️ Orbit Comparison & Trends",
    "📊 Reference Satellites Database",
    "📚 Formulas & Physical Principles",
])

# ----------------------------------------------------------------------------
# TAB 1: ORBIT OVERVIEW & TRAJECTORY
# ----------------------------------------------------------------------------
with tab1:
    st.subheader(f"Orbit Parameters: {primary_name} ({orbit1_summary['regime']['name']})")
    
    # KPI Metric Cards Row 1
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="Altitude (h)",
            value=f"{orbit1_summary['altitude_km']:,.1f} km",
            help="Distance above Earth's surface."
        )
    with col2:
        st.metric(
            label="Orbital Radius (r = R + h)",
            value=f"{orbit1_summary['orbital_radius_km']:,.1f} km",
            help=f"Distance from Earth's center. Earth Radius = {EARTH_RADIUS_KM:,.1f} km."
        )
    with col3:
        st.metric(
            label="Orbital Velocity (v)",
            value=f"{orbit1_summary['velocity_km_s']:.3f} km/s",
            delta=f"{orbit1_summary['velocity_km_h']:,.0f} km/h",
            help="Speed required to balance Earth's gravitational pull in a circular path."
        )
    with col4:
        st.metric(
            label="Orbital Period (T)",
            value=f"{orbit1_summary['period_minutes']:.2f} min",
            delta=f"{orbit1_summary['period_hours']:.2f} hours",
            help="Time taken for one full revolution around the Earth."
        )
        
    # KPI Metric Cards Row 2
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric(
            label="Local Gravity g(h)",
            value=f"{orbit1_summary['gravitational_accel_m_s2']:.2f} m/s²",
            delta=f"{orbit1_summary['surface_gravity_percent']:.1f}% of sea level",
            help="Gravitational acceleration experienced at this altitude (sea level = 9.81 m/s²)."
        )
    with col6:
        st.metric(
            label="Orbits per Solar Day",
            value=f"{orbit1_summary['orbits_per_day']:.2f} revs/day",
            help="Number of times the satellite circles Earth in 24 hours (86,400 seconds)."
        )
    with col7:
        if sat1_mass:
            st.metric(
                label="Kinetic Energy (Ek)",
                value=f"{orbit1_summary['energy'].get('kinetic_energy_gj', 0):,.1f} GJ",
                help="Total kinetic energy 0.5 * m * v^2 in GigaJoules."
            )
        else:
            st.metric(
                label="Specific Energy",
                value=f"{orbit1_summary['energy']['specific_total_mj_kg']:.2f} MJ/kg",
                help="Mechanical energy per unit mass: -mu / (2*r)."
            )
    with col8:
        if sat1_mass:
            grav_force_kn = orbit1_summary['energy'].get('gravitational_force_n', 0) / 1000.0
            st.metric(
                label="Gravitational Force",
                value=f"{grav_force_kn:,.2f} kN",
                help="Gravitational pull F = m * g(h) acting on satellite in kiloNewtons."
            )
        else:
            st.metric(
                label="Regime Classification",
                value=orbit1_summary['regime']['code'],
                help="Standard aerospace orbit classification."
            )
            
    st.markdown("---")
    
    # 2D Orbit Visualization & Explanations side-by-side
    vis_col, desc_col = st.columns([1.1, 0.9])
    
    with vis_col:
        st.markdown("#### 2D Trajectory View (Drawn to Scale)")
        fig_orbit = plot_circular_orbit(
            alt1_km=alt1_input,
            name1=primary_name,
            sat1_angle_deg=sat1_angle,
            alt2_km=alt2_input if enable_comparison else None,
            name2=primary_name_2 if enable_comparison else None,
            sat2_angle_deg=sat2_angle,
            show_geo_ring=show_geo_ring,
        )
        st.pyplot(fig_orbit, use_container_width=True)
        st.caption("Figure: Scaled 2D projection showing Earth, atmosphere boundary, orbital path, and instantaneous velocity direction vector $\\vec{v}$.")
        
    with desc_col:
        st.markdown("#### 🔍 Orbital Mechanics Interpretation")
        regime_info = orbit1_summary["regime"]
        st.info(
            f"**Regime Context ({regime_info['name']}):**\n\n"
            f"{regime_info['description']}\n\n"
            f"**Typical Missions:** {regime_info['examples']}"
        )
        
        # Physical Interpretation Explanations
        st.markdown(
            f"""
            - **Why is velocity {orbit1_summary['velocity_km_s']:.2f} km/s?**  
              At $r = {orbit1_summary['orbital_radius_km']:,.0f}\\text{ km}$, Earth's gravity pulls the satellite inward with $g = {orbit1_summary['gravitational_accel_m_s2']:.2f}\\text{ m/s}^2$. 
              To avoid crashing into Earth or escaping into deep space, the satellite's forward centripetal acceleration ($v^2/r$) must exactly match this gravitational pull. 
              Hence, $v = \\sqrt{{\\mu / r}}$.
              
            - **Is there 'Zero Gravity' at this altitude?**  
              **No!** At {alt1_input:,.0f} km altitude, gravity is still **{orbit1_summary['surface_gravity_percent']:.1f}%** of what it is on Earth's surface! 
              The sensation of weightlessness ('microgravity') happens because the satellite and everything inside it are in a **continuous state of free-fall around the curved surface of Earth**.
              
            - **Kepler's Third Law in Action:**  
              The satellite completes one complete orbit every **{orbit1_summary['period_minutes']:.1f} minutes** ({orbit1_summary['period_hours']:.2f} hours). 
              If we raised the altitude, the period would increase at the rate of $r^{{3/2}}$ while orbital velocity would decrease at $1/\\sqrt{{r}}$.
            """
        )

# ----------------------------------------------------------------------------
# TAB 2: ORBIT COMPARISON & SENSITIVITY CURVES
# ----------------------------------------------------------------------------
with tab2:
    st.subheader("⚖️ Side-by-Side Orbit Comparison & Parameter Trends")
    
    if enable_comparison and orbit2_summary is not None:
        # Comparison Table
        st.markdown(f"#### Comparison: {primary_name} vs. {primary_name_2}")
        
        comp_df = pd.DataFrame([
            {
                "Parameter": "Altitude above Earth (h)",
                "Unit": "km",
                primary_name: f"{orbit1_summary['altitude_km']:,.1f}",
                primary_name_2: f"{orbit2_summary['altitude_km']:,.1f}",
                "Difference (Orbit 2 - Orbit 1)": f"{comparison_results['deltas']['altitude_diff_km']:+,.1f} km",
            },
            {
                "Parameter": "Orbital Radius (r)",
                "Unit": "km",
                primary_name: f"{orbit1_summary['orbital_radius_km']:,.1f}",
                primary_name_2: f"{orbit2_summary['orbital_radius_km']:,.1f}",
                "Difference (Orbit 2 - Orbit 1)": f"{comparison_results['deltas']['radius_diff_km']:+,.1f} km",
            },
            {
                "Parameter": "Circular Orbital Velocity (v)",
                "Unit": "km/s",
                primary_name: f"{orbit1_summary['velocity_km_s']:.3f}",
                primary_name_2: f"{orbit2_summary['velocity_km_s']:.3f}",
                "Difference (Orbit 2 - Orbit 1)": f"{comparison_results['deltas']['velocity_diff_km_s']:+.3f} km/s (Ratio: {comparison_results['deltas']['velocity_ratio']:.3f}x)",
            },
            {
                "Parameter": "Orbital Period (T)",
                "Unit": "minutes",
                primary_name: f"{orbit1_summary['period_minutes']:.2f}",
                primary_name_2: f"{orbit2_summary['period_minutes']:.2f}",
                "Difference (Orbit 2 - Orbit 1)": f"{comparison_results['deltas']['period_diff_minutes']:+,.1f} min (Ratio: {comparison_results['deltas']['period_ratio']:.2f}x)",
            },
            {
                "Parameter": "Local Gravity g(h)",
                "Unit": "m/s²",
                primary_name: f"{orbit1_summary['gravitational_accel_m_s2']:.2f}",
                primary_name_2: f"{orbit2_summary['gravitational_accel_m_s2']:.2f}",
                "Difference (Orbit 2 - Orbit 1)": f"{comparison_results['deltas']['gravity_diff_m_s2']:+.2f} m/s²",
            },
            {
                "Parameter": "Orbits Completed Per Day",
                "Unit": "revs / 24h",
                primary_name: f"{orbit1_summary['orbits_per_day']:.2f}",
                primary_name_2: f"{orbit2_summary['orbits_per_day']:.2f}",
                "Difference (Orbit 2 - Orbit 1)": f"{orbit2_summary['orbits_per_day'] - orbit1_summary['orbits_per_day']:+.2f} revs/day",
            },
            {
                "Parameter": "Regime Classification",
                "Unit": "Standard",
                primary_name: orbit1_summary['regime']['name'],
                primary_name_2: orbit2_summary['regime']['name'],
                "Difference (Orbit 2 - Orbit 1)": "—",
            },
        ])
        st.dataframe(comp_df, hide_index=True, use_container_width=True)
    else:
        st.warning("Enable 'Compare with a Second Orbit' in the sidebar to view side-by-side comparison tables.")
        
    st.markdown("---")
    st.markdown("#### 📈 Parameter Sensitivity Curves")
    st.caption("See how orbital velocity, orbital period, and local gravitational acceleration behave as altitude increases from Low Earth Orbit (100 km) to Geostationary Orbit (40,000 km).")
    
    plot_col1, plot_col2 = st.columns(2)
    
    with plot_col1:
        fig_vel = plot_altitude_vs_velocity(
            current_alt1_km=alt1_input,
            current_alt2_km=alt2_input if enable_comparison else None,
            max_sweep_alt_km=40000.0,
        )
        st.pyplot(fig_vel, use_container_width=True)
        st.markdown(
            """
            **Takeaway:** Orbital velocity **decreases** as altitude increases following $v \\propto 1/\\sqrt{r}$. 
            Lower satellites must move faster to stay in orbit because Earth's gravitational pull is stronger close to the surface.
            """
        )
        
    with plot_col2:
        period_unit = st.radio("Period Plot Units:", ["hours", "minutes"], horizontal=True)
        fig_per = plot_altitude_vs_period(
            current_alt1_km=alt1_input,
            current_alt2_km=alt2_input if enable_comparison else None,
            max_sweep_alt_km=40000.0,
            unit=period_unit,
        )
        st.pyplot(fig_per, use_container_width=True)
        st.markdown(
            """
            **Takeaway:** Orbital period **increases** steeply with altitude following Kepler's Third Law ($T \\propto r^{3/2}$). 
            At ~35,786 km, the period reaches exactly 23 hours 56 minutes, matching Earth's rotation!
            """
        )
        
    st.markdown("---")
    st.markdown("#### 🌍 Gravitational Acceleration Decay (Inverse Square Law)")
    fig_grav = plot_altitude_vs_gravity(
        current_alt1_km=alt1_input,
        current_alt2_km=alt2_input if enable_comparison else None,
        max_sweep_alt_km=40000.0,
    )
    st.pyplot(fig_grav, use_container_width=True)

# ----------------------------------------------------------------------------
# TAB 3: REFERENCE SATELLITES DATABASE
# ----------------------------------------------------------------------------
with tab3:
    st.subheader("📊 Reference Operational Satellites Database")
    st.markdown(
        "A curated reference dataset of real-world operational spacecraft across all orbital regimes. "
        "Use this data to cross-check calculations with established space missions."
    )
    
    regime_filter = st.multiselect(
        "Filter by Orbit Regime:",
        options=sample_df["Regime"].unique().tolist(),
        default=sample_df["Regime"].unique().tolist(),
    )
    
    filtered_df = sample_df[sample_df["Regime"].isin(regime_filter)]
    st.dataframe(
        filtered_df,
        column_config={
            "Altitude_km": st.column_config.NumberColumn("Altitude (km)", format="%,.1f km"),
            "Orbital_Radius_km": st.column_config.NumberColumn("Radius (km)", format="%,.1f km"),
            "Velocity_km_s": st.column_config.NumberColumn("Velocity (km/s)", format="%.3f km/s"),
            "Period_min": st.column_config.NumberColumn("Period (min)", format="%.2f min"),
            "Orbits_Per_Day": st.column_config.NumberColumn("Revs/Day", format="%.2f"),
        },
        hide_index=True,
        use_container_width=True,
    )
    
    st.markdown("##### 📌 Dataset Summary Insights:")
    c1, c2, c3 = st.columns(3)
    leo_df = sample_df[sample_df["Regime"] == "LEO"]
    geo_df = sample_df[sample_df["Regime"] == "GEO"]
    with c1:
        st.metric("Avg. LEO Velocity", f"{leo_df['Velocity_km_s'].mean():.2f} km/s", "High kinetic speed")
    with c2:
        st.metric("Avg. LEO Period", f"{leo_df['Period_min'].mean():.1f} min", "~15 orbits / day")
    with c3:
        st.metric("GEO Period", f"{geo_df['Period_min'].iloc[0]:.1f} min", "Exactly 1 sidereal day")

# ----------------------------------------------------------------------------
# TAB 4: FORMULAS & PHYSICAL PRINCIPLES
# ----------------------------------------------------------------------------
with tab4:
    st.subheader("📚 Orbital Mechanics Fundamentals & Theoretical Derivations")
    
    st.markdown("### 1. Fundamental Constants Defined")
    constants_df = pd.DataFrame([
        {"Symbol": "R_earth", "Value": f"{EARTH_RADIUS_KM:,.3f} km", "Meaning": "WGS-84 standard equatorial radius of Earth"},
        {"Symbol": "mu (GM)", "Value": f"{EARTH_MU_KM3_S2:,.4f} km^3/s^2", "Meaning": "Earth standard gravitational parameter (G * M_earth)"},
        {"Symbol": "M_earth", "Value": "5.9722 x 10^24 kg", "Meaning": "Total mass of Earth"},
        {"Symbol": "G", "Value": "6.6743 x 10^-11 m^3/(kg*s^2)", "Meaning": "Newtonian universal constant of gravitation"},
        {"Symbol": "g0", "Value": "9.80665 m/s^2", "Meaning": "Standard gravitational acceleration at Earth's sea level"},
    ])
    st.table(constants_df)
    
    st.markdown("### 2. Step-by-Step Mathematical Derivations")
    
    with st.expander("🔹 Derivation 1: Circular Orbital Velocity Formula $v = \\sqrt{\\frac{\\mu}{r}}$", expanded=True):
        st.markdown(
            r"""
            For a satellite of mass $m$ to remain in a stable circular orbit of radius $r$ around Earth (mass $M$), 
            the gravitational force must provide the exact centripetal force required for circular motion:
            
            $$F_{\text{gravity}} = F_{\text{centripetal}}$$
            
            $$\frac{G \cdot M \cdot m}{r^2} = \frac{m \cdot v^2}{r}$$
            
            Cancel satellite mass $m$ from both sides:
            
            $$\frac{G \cdot M}{r^2} = \frac{v^2}{r}$$
            
            Substitute standard gravitational parameter $\mu = G \cdot M$:
            
            $$\frac{\mu}{r} = v^2 \implies v = \sqrt{\frac{\mu}{r}} = \sqrt{\frac{\mu}{R_E + h}}$$
            
            **Key Physical Insight:** Notice that satellite mass $m$ canceled out! 
            A 100-ton Space Station orbits at the exact same circular speed as a 1-kg CubeSat at the same altitude!
            """
        )
        
    with st.expander("🔹 Derivation 2: Orbital Period $T = 2\\pi \\sqrt{\\frac{r^3}{\\mu}}$ (Kepler's 3rd Law)", expanded=True):
        st.markdown(
            r"""
            The distance traveled in one circular revolution is the circumference $C = 2\pi r$.
            
            Because circular orbital speed $v$ is constant:
            
            $$T = \frac{\text{Distance}}{\text{Speed}} = \frac{2\pi r}{v}$$
            
            Substitute $v = \sqrt{\frac{\mu}{r}}$:
            
            $$T = \frac{2\pi r}{\sqrt{\mu / r}} = 2\pi r \cdot \sqrt{\frac{r}{\mu}} = 2\pi \sqrt{\frac{r^3}{\mu}}$$
            
            Squaring both sides yields:
            
            $$T^2 = \left(\frac{4\pi^2}{\mu}\right) r^3$$
            
            This is the exact mathematical statement of **Kepler's Third Law of Planetary Motion**: the square of the orbital period is directly proportional to the cube of the semi-major axis (radius for circular orbit).
            """
        )
        
    with st.expander("🔹 Derivation 3: Gravitational Acceleration at Altitude $g(h) = \\frac{\\mu}{(R_E + h)^2}$", expanded=False):
        st.markdown(
            r"""
            From Newton's second law ($F = m \cdot g$) and universal gravitation ($F = \frac{G M m}{r^2}$):
            
            $$m \cdot g(h) = \frac{G \cdot M \cdot m}{r^2}$$
            
            $$g(h) = \frac{\mu}{r^2} = \frac{\mu}{(R_E + h)^2}$$
            
            This illustrates the **Inverse Square Law**: as distance doubles, gravitational acceleration drops to one-fourth.
            """
        )
        
    st.markdown("### 3. Core Astrodynamics Principles & Physical Insights")
    
    qa_list = [
        (
            "Why do satellites at higher altitudes move slower if more rocket fuel is needed to reach them?",
            "**Explanation:** While more energy is required to lift the satellite to higher altitude against Earth's gravitational potential well (increasing potential energy), Earth's gravitational pull decreases with distance ($g \\propto 1/r^2$). Therefore, less centripetal acceleration ($v^2/r$) is required to balance gravity, resulting in a slower orbital velocity ($v \\propto 1/\\sqrt{r}$). The total orbital energy increases (becomes less negative), but kinetic energy decreases while potential energy increases."
        ),
        (
            "If gravity at the ISS (408 km) is still ~89% of Earth's surface gravity, why are astronauts weightless?",
            "**Explanation:** Astronauts are not in 'zero gravity'—they are in continuous free-fall. Both the ISS and the astronauts are accelerating toward Earth at the exact rate given by $g = \\mu/r^2 \\approx 8.65\\text{ m/s}^2$. Because the station and the astronauts are falling together along the curved path of the orbit, there is no normal reaction force between the astronaut and the floor. This absence of normal contact force produces the sensation of weightlessness (microgravity)."
        ),
        (
            "Why do we use the standard gravitational parameter $\\mu = GM$ instead of calculating $G \\times M$ separately?",
            "**Explanation:** In astrodynamics, the product $\\mu = GM$ can be measured from planetary and satellite tracking observations with astronomical precision (uncertainty $\\sim 10^{-9}$), whereas the universal gravitational constant $G$ alone is notoriously difficult to measure in laboratory experiments (uncertainty $\\sim 10^{-5}$). Using $\\mu$ directly prevents propagating laboratory uncertainty into space mission calculations."
        ),
        (
            "What is the difference between a Geosynchronous Orbit (GSO) and a Geostationary Orbit (GEO)?",
            "**Explanation:** Both have an orbital period of exactly one sidereal day (~23 hours 56 minutes) at an altitude of ~35,786 km. However, a **Geostationary Orbit (GEO)** must have an inclination of $0^\\circ$ (equatorial plane) and zero eccentricity (circular). In GEO, the satellite appears completely motionless in the sky to an observer on Earth. A **Geosynchronous Orbit (GSO)** can be inclined; an observer on Earth would see the satellite trace an analemma (figure-8 path) in the sky over 24 hours."
        ),
        (
            "What are the main limitations and simplifications of this circular model?",
            "**Explanation:** This project uses an unperturbed, spherical, two-body circular model. Real-world space mission analysis must account for: (1) Earth's oblateness ($J_2$ gravitational harmonic causing nodal precession), (2) atmospheric drag in LEO causing orbital decay, (3) solar radiation pressure, (4) third-body gravitational perturbations from the Moon and Sun, and (5) orbital eccentricity ($e > 0$ elliptical orbits)."
        ),
    ]
    
    for q, a in qa_list:
        with st.expander(q):
            st.markdown(a)

# Footer
st.markdown("---")
st.caption("Satellite Orbit Analysis & Visualization System | Developed by Mohammad Jeelani | Python • Streamlit • NumPy • Matplotlib")
