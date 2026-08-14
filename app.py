"""
===============================================================================
AI DEVELOPMENT DOCUMENTATION
===============================================================================
AI Tools Used:
- OpenAI ChatGPT / Gemini (AI-Assisted Development / Vibe Coding)

Key Prompts Used:
1. "Act as a senior software engineer and build a Streamlit application for a fluid 
    flow calculator that computes pipe friction and pressure loss using the 
    Darcy-Weisbach equation."
2. "Add dynamic interactive sidebar controls using sliders, selectboxes, and number 
    inputs, along with comprehensive error handling to display warnings for non-positive inputs."
3. "Generate a Plotly chart showing Head Loss vs. Pipe Diameter with the operating point 
    clearly marked, alongside a Pandas summary table."

Most Important Manual Fix / Verification:
- Verified the friction factor calculation by switching from a basic laminar-only formula 
  to the Swamee-Jain explicit equation for turbulent flow conditions, ensuring realistic 
  engineering results across both laminar ($Re < 2300$) and turbulent regimes ($Re \\ge 2300$).
===============================================================================
"""

import math
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Fluid Flow & Pipe Friction Loss Calculator",
    page_icon="🌊",
    layout="wide",
)

# Main Title & Subtitle
st.title("🌊 Darcy-Weisbach Fluid Flow & Friction Loss Calculator")
st.subtitle("Interactive Engineering Tool for Fluid Mechanics & Piping Design")

# Instructions
st.markdown(
    """
### 📋 User Instructions
1. **Configure Parameters:** Use the sidebar on the left to select fluid properties, pipe material, and flow dimensions.
2. **Review Output:** Observe the dynamic updates in the calculated engineering metrics and Pandas summary table below.
3. **Analyze Visualization:** Examine the **Head Loss vs. Pipe Diameter** curve to evaluate trade-offs between pipe sizing and friction loss.
---
"""
)

# -----------------------------------------------------------------------------
# SIDEBAR CONTROLS
# -----------------------------------------------------------------------------
st.sidebar.header("⚙️ Input Parameters")

# 1. Selectbox - Fluid Choice
fluid = st.sidebar.selectbox(
    "1. Select Fluid Type",
    options=["Water (20°C)", "Crude Oil (Light)", "Gasoline", "Custom Fluid"],
)

# Set properties based on fluid selection
if fluid == "Water (20°C)":
    default_density = 998.2  # kg/m^3
    default_viscosity = 0.001002  # Pa.s
elif fluid == "Crude Oil (Light)":
    default_density = 850.0
    default_viscosity = 0.0075
elif fluid == "Gasoline":
    default_density = 740.0
    default_viscosity = 0.0006
else:
    default_density = 1000.0
    default_viscosity = 0.0010

density = st.sidebar.number_input(
    "Fluid Density ρ (kg/m³)",
    value=default_density,
    min_value=1.0,
    max_value=3000.0,
    step=10.0,
)
viscosity = st.sidebar.number_input(
    "Dynamic Viscosity μ (Pa·s)",
    value=default_viscosity,
    min_value=0.00001,
    max_value=1.0,
    format="%.6f",
)

# 2. Selectbox - Pipe Material
material = st.sidebar.selectbox(
    "2. Select Pipe Material",
    options=[
        "Commercial Steel",
        "PVC / Plastic (Smooth)",
        "Cast Iron",
        "Galvanized Iron",
    ],
)

roughness_map = {
    "Commercial Steel": 0.045 / 1000,  # meters
    "PVC / Plastic (Smooth)": 0.0015 / 1000,
    "Cast Iron": 0.26 / 1000,
    "Galvanized Iron": 0.15 / 1000,
}
epsilon = roughness_map[material]

# 3. Slider - Pipe Inner Diameter (mm)
diameter_mm = st.sidebar.slider(
    "3. Pipe Inner Diameter D (mm)",
    min_value=10.0,
    max_value=300.0,
    value=50.0,
    step=5.0,
)

# 4. Number Input - Pipe Length (m)
length = st.sidebar.number_input(
    "4. Pipe Length L (m)", min_value=1.0, max_value=10000.0, value=100.0, step=10.0
)

# 5. Slider - Flow Velocity (m/s)
velocity = st.sidebar.slider(
    "5. Fluid Velocity v (m/s)",
    min_value=0.1,
    max_value=10.0,
    value=2.0,
    step=0.1,
)

# -----------------------------------------------------------------------------
# CALCULATIONS & ERROR HANDLING
# -----------------------------------------------------------------------------
g = 9.81  # m/s^2
diameter = diameter_mm / 1000.0  # Convert mm to meters

# Error Handling Validation
if diameter <= 0 or length <= 0 or velocity <= 0 or density <= 0 or viscosity <= 0:
    st.error("⚠️ Invalid Input! All physical values must be strictly greater than zero.")
else:
    # Cross-sectional Area
    area = (math.pi * (diameter**2)) / 4.0
    volumetric_flow_rate = area * velocity  # m^3/s

    # Reynolds Number
    reynolds = (density * velocity * diameter) / viscosity

    # Flow Regime & Friction Factor Calculation
    if reynolds < 2300:
        regime = "Laminar"
        friction_factor = 64.0 / reynolds
    else:
        regime = "Turbulent" if reynolds > 4000 else "Transitional"
        # Swamee-Jain equation approximation for Darcy friction factor
        term = (epsilon / (3.7 * diameter)) + (5.74 / (reynolds**0.9))
        friction_factor = 0.25 / (math.log10(term) ** 2)

    # Darcy-Weisbach Head Loss (m)
    head_loss = friction_factor * (length / diameter) * ((velocity**2) / (2 * g))

    # Pressure Drop (kPa)
    pressure_drop_kpa = (density * g * head_loss) / 1000.0

    # -------------------------------------------------------------------------
    # DISPLAY METRICS & PANDAS RESULTS TABLE
    # -------------------------------------------------------------------------
    st.header("📊 Calculation Results")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Reynolds Number (Re)", f"{reynolds:,.0f}")
    col2.metric("Flow Regime", regime)
    col3.metric("Friction Factor (f)", f"{friction_factor:.4f}")
    col4.metric("Head Loss (hf)", f"{head_loss:.2f} m")

    st.subheader("📋 Results Summary Table")

    summary_df = pd.DataFrame(
        {
            "Parameter": [
                "Fluid Type",
                "Pipe Material",
                "Inner Diameter (mm)",
                "Pipe Length (m)",
                "Flow Velocity (m/s)",
                "Volumetric Flow Rate (m³/h)",
                "Reynolds Number",
                "Flow Regime",
                "Darcy Friction Factor (f)",
                "Head Loss (m)",
                "Pressure Drop (kPa)",
            ],
            "Value": [
                fluid,
                material,
                f"{diameter_mm:.1f}",
                f"{length:.1f}",
                f"{velocity:.2f}",
                f"{volumetric_flow_rate * 3600:.2f}",
                f"{reynolds:,.0f}",
                regime,
                f"{friction_factor:.5f}",
                f"{head_loss:.3f}",
                f"{pressure_drop_kpa:.2f}",
            ],
        }
    )

    st.dataframe(summary_df, use_container_width=True)

    # -------------------------------------------------------------------------
    # PLOTLY CHART: Head Loss vs. Pipe Diameter
    # -------------------------------------------------------------------------
    st.header("📈 Visual Analysis: Head Loss vs. Pipe Diameter")

    # Generate diameter range for plotting (from 10 mm to 300 mm)
    d_range_mm = np.linspace(10.0, 300.0, 100)
    d_range_m = d_range_mm / 1000.0

    head_loss_curve = []
    for d_val in d_range_m:
        re_val = (density * velocity * d_val) / viscosity
        if re_val < 2300:
            f_val = 64.0 / re_val
        else:
            term_val = (epsilon / (3.7 * d_val)) + (5.74 / (re_val**0.9))
            f_val = 0.25 / (math.log10(term_val) ** 2)
        hl_val = f_val * (length / d_val) * ((velocity**2) / (2 * g))
        head_loss_curve.append(hl_val)

    # Create Plotly Figure
    fig = go.Figure()

    # Add Curve
    fig.add_trace(
        go.Scatter(
            x=d_range_mm,
            y=head_loss_curve,
            mode="lines",
            name="Head Loss Curve",
            line=dict(color="#1f77b4", width=3),
        )
    )

    # Add Operating Point
    fig.add_trace(
        go.Scatter(
            x=[diameter_mm],
            y=[head_loss],
            mode="markers",
            name="Current Operating Point",
            marker=dict(color="red", size=12, symbol="diamond"),
        )
    )

    fig.update_layout(
        title=f"Head Loss vs. Pipe Diameter (L = {length} m, v = {velocity} m/s)",
        xaxis_title="Pipe Diameter (mm)",
        yaxis_title="Head Loss (meters)",
        template="plotly_white",
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True)