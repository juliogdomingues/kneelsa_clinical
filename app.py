import streamlit as st
import numpy as np
import pandas as pd
from pathlib import Path

# ==========================================
# CONFIGURAÇÃO DO MODELO (carregado de CSV)
# ==========================================
SINGLE_CSV = Path("final_5var_model.csv")


@st.cache_data
def load_model_params():
    """
    Loads the 5-variable model parameters from a single CSV:
    results_final_analysis/final_5var_model.csv
    """
    if not SINGLE_CSV.exists():
        raise FileNotFoundError(
            "Model CSV not found. Please run complete.py to generate:\n"
            f"- {SINGLE_CSV}"
        )

    df = pd.read_csv(SINGLE_CSV)

    intercept_row = df.loc[df["feature"] == "__INTERCEPT__"].iloc[0]
    intercept = float(intercept_row["intercept"])

    features_df = df.loc[
        df["param_type"] == "feature",
        ["feature", "imputer_median", "scaler_mean", "scaler_scale", "coef_on_scaled"],
    ].copy()

    return intercept, features_df


INTERCEPT, MODEL_FEATURES = load_model_params()

# ==========================================
# INTERFACE DO USUÁRIO
# ==========================================
st.set_page_config(page_title="Kneelsa-Clinical", page_icon="🦵")

st.title("Kneelsa-Clinical: KOA Screening Tool")
st.markdown("""
This tool implements the **5-variable clinical screening model** developed in the ELSA-Brasil MSK study.
It estimates the probability of prevalent radiographic Knee Osteoarthritis (KL >= 2) **per knee**.
""")

st.markdown("---")

# Patient Demographics (same for both knees)
st.subheader("Patient Demographics")
col1, col2 = st.columns(2)

with col1:
    age = st.number_input("Age (years)", min_value=30, max_value=100, value=55)

with col2:
    bmi = st.number_input("BMI (kg/m²)", min_value=15.0, max_value=60.0, value=25.0, format="%.1f", step=1.0)

st.markdown("---")

# Knee-specific Clinical Features
st.subheader("Clinical Features per Knee")

# Select which knees to assess
knee_selection = st.radio(
    "Which knee(s) would you like to assess?",
    options=["Left Knee Only", "Right Knee Only", "Both Knees"],
    index=2
)


def knee_svg(knee: str) -> str:
    label = "RIGHT (R)" if knee == "Right" else "LEFT (L)"
    accent = "#1f77b4" if knee == "Right" else "#d62728"
    return "".join(
        [
            f'<svg width="54" height="54" viewBox="0 0 54 54" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{label} knee">',
            f'<rect x="18" y="4" width="18" height="18" rx="6" fill="{accent}" opacity="0.85"/>',
            '<circle cx="27" cy="27" r="9" fill="#f2f2f2" stroke="#666" stroke-width="2"/>',
            f'<rect x="18" y="32" width="18" height="18" rx="6" fill="{accent}" opacity="0.35"/>',
            '<path d="M18 23 C22 17, 32 17, 36 23" fill="none" stroke="#666" stroke-width="2"/>',
            '<path d="M18 31 C22 37, 32 37, 36 31" fill="none" stroke="#666" stroke-width="2"/>',
            "</svg>",
        ]
    )


def knee_badge_html(knee: str, *, show_subtitle: bool = True) -> str:
    # Simple, inline SVG to make side obvious.
    label = "RIGHT (R)" if knee == "Right" else "LEFT (L)"
    subtitle = (
        '<div style="font-size:12px;color:#666;line-height:1.2;">Radiographic view</div>'
        if show_subtitle
        else ""
    )
    return "".join(
        [
            '<div style="display:flex;align-items:center;gap:10px;">',
            knee_svg(knee),
            "<div>",
            f'<div style="font-weight:700;line-height:1;">{label}</div>',
            subtitle,
            "</div>",
            "</div>",
        ]
    )


def radiographic_view_html() -> str:
    return '<div style="text-align:center;font-size:12px;color:#666;margin:6px 0 10px 0;">Radiographic view</div>'


def both_knees_icons_line_html() -> str:
    # Centered line: RIGHT label + right icon + left icon + LEFT label
    return "".join(
        [
            '<div style="display:flex;justify-content:center;align-items:center;gap:18px;margin-bottom:10px;">',
            '<div style="font-weight:700;">Right knee (R)</div>',
            knee_svg("Right"),
            knee_svg("Left"),
            '<div style="font-weight:700;">Left knee (L)</div>',
            "</div>",
        ]
    )


def knee_column_header_html(knee: str, *, justify: str) -> str:
    label = "RIGHT (R)" if knee == "Right" else "LEFT (L)"
    return (
        f'<div style="display:flex;justify-content:{justify};align-items:center;gap:10px;">'
        f'<div style="font-weight:700;">{label}</div>'
        f'{knee_svg(knee)}'
        "</div>"
    )


def get_knees_to_assess(selection: str) -> list[str]:
    if selection == "Both Knees":
        return ["Left", "Right"]
    if selection == "Left Knee Only":
        return ["Left"]
    if selection == "Right Knee Only":
        return ["Right"]
    return []


knees_to_assess = get_knees_to_assess(knee_selection)

SYMPTOMS_LABEL = "Frequent Symptoms?"
SURGERY_LABEL = "History of Surgery?"
TRAUMA_LABEL = "History of Trauma/Injury?"

# Create inputs for knee-specific variables
if len(knees_to_assess) == 1:
    knee = knees_to_assess[0]
    st.markdown(knee_badge_html(knee).strip(), unsafe_allow_html=True)

    st.checkbox(
        SYMPTOMS_LABEL,
        key=f"symptoms_{knee}",
        help="Pain, discomfort, or stiffness that lasted for most days for at least one month in the last 12 months",
    )
    st.checkbox(
        SURGERY_LABEL,
        key=f"surgery_{knee}",
        help="Ever undergone any type of surgery, including arthroscopy, meniscal or ligament repair?",
    )
    st.checkbox(
        TRAUMA_LABEL,
        key=f"trauma_{knee}",
        help="Ever injured or suffered trauma that caused difficulty walking for at least one week?",
    )
else:
    # Radiographic convention: RIGHT knee on the LEFT side of the screen
    st.markdown(radiographic_view_html(), unsafe_allow_html=True)
    
    # Simple two-column layout (fully responsive, Streamlit-native)
    col_right, col_left = st.columns(2)
    
    with col_right:
        st.markdown(
            f'<div style="text-align:center;margin-bottom:10px;">'
            f'<div style="font-weight:700;">Right knee (R)</div>'
            f'{knee_svg("Right")}'
            f'</div>',
            unsafe_allow_html=True
        )
        st.checkbox(
            SYMPTOMS_LABEL,
            key="symptoms_Right",
            help="Pain, discomfort, or stiffness that lasted for most days for at least one month in the last 12 months"
        )
        st.checkbox(
            SURGERY_LABEL,
            key="surgery_Right",
            help="Ever undergone any type of surgery, including arthroscopy, meniscal or ligament repair?"
        )
        st.checkbox(
            TRAUMA_LABEL,
            key="trauma_Right",
            help="Ever injured or suffered trauma that caused difficulty walking for at least one week?"
        )
    
    with col_left:
        st.markdown(
            f'<div style="text-align:center;margin-bottom:10px;">'
            f'<div style="font-weight:700;">Left knee (L)</div>'
            f'{knee_svg("Left")}'
            f'</div>',
            unsafe_allow_html=True
        )
        st.checkbox(
            SYMPTOMS_LABEL,
            key="symptoms_Left",
            help="Pain, discomfort, or stiffness that lasted for most days for at least one month in the last 12 months"
        )
        st.checkbox(
            SURGERY_LABEL,
            key="surgery_Left",
            help="Ever undergone any type of surgery, including arthroscopy, meniscal or ligament repair?"
        )
        st.checkbox(
            TRAUMA_LABEL,
            key="trauma_Left",
            help="Ever injured or suffered trauma that caused difficulty walking for at least one week?"
        )


st.markdown("---")

# ==========================================
# CÁLCULO
# ==========================================
def calculate_probability(age, bmi, symptoms, surgery, trauma):
    """Calculate the probability of KOA for a single knee using the saved preprocessing + LR params."""
    x = {
        "age": float(age),
        "bmi": float(bmi),
        "history_surgery": 1.0 if surgery else 0.0,
        "frequent_symptoms": 1.0 if symptoms else 0.0,
        "history_trauma": 1.0 if trauma else 0.0,
    }

    logit = float(INTERCEPT)
    for _, row in MODEL_FEATURES.iterrows():
        f = row["feature"]
        val = x.get(f, None)

        # median imputation (only used if val is missing)
        if val is None or (isinstance(val, float) and np.isnan(val)):
            val = float(row["imputer_median"])

        z = (float(val) - float(row["scaler_mean"])) / float(row["scaler_scale"])
        logit += float(row["coef_on_scaled"]) * z

    probability = 1 / (1 + np.exp(-logit))
    return float(probability)

if st.button("Calculate Probability", type="primary"):
    st.markdown("---")
    st.subheader("Results")

    knees_to_display = get_knees_to_assess(knee_selection)

    if not knees_to_display:
        st.error("No knees selected. Please select at least one knee.")
    else:
        def render_knee_result(container, knee: str, *, show_badge: bool) -> None:
            knee_symptoms = st.session_state.get(f"symptoms_{knee}", False)
            knee_surgery = st.session_state.get(f"surgery_{knee}", False)
            knee_trauma = st.session_state.get(f"trauma_{knee}", False)

            prob = calculate_probability(
                age=age,
                bmi=bmi,
                symptoms=knee_symptoms,
                surgery=knee_surgery,
                trauma=knee_trauma,
            )

            with container:
                if show_badge:
                    st.markdown(
                        f"<div style=\"display:flex;justify-content:center;\">{knee_badge_html(knee)}</div>",
                        unsafe_allow_html=True,
                    )
                st.metric(
                    label=(
                        "Probability of KOA"
                        if show_badge
                        else f"{knee} Knee - Probability of KOA"
                    ),
                    value=f"{prob:.1%}",
                    help="Probability of radiographic KOA (KL >= 2)",
                )
                st.write(
                    f"**Input data:** Age {age}y | BMI {bmi:.1f} | "
                    f"Symptoms: {'Yes' if knee_symptoms else 'No'} | "
                    f"Surgery: {'Yes' if knee_surgery else 'No'} | "
                    f"Trauma: {'Yes' if knee_trauma else 'No'}"
                )

        # Side-by-side when both knees are selected (RIGHT shown on LEFT side)
        if set(knees_to_display) == {"Left", "Right"}:
            st.markdown(radiographic_view_html(), unsafe_allow_html=True)
            col_r, col_l = st.columns(2)
            with col_r:
                st.markdown(knee_column_header_html("Right", justify="flex-end"), unsafe_allow_html=True)
                spacer, results = st.columns([1, 3])
                render_knee_result(results, "Right", show_badge=False)

            with col_l:
                st.markdown(knee_column_header_html("Left", justify="flex-start"), unsafe_allow_html=True)
                results, spacer = st.columns([3, 1])
                render_knee_result(results, "Left", show_badge=False)
        else:
            render_knee_result(st.container(), knees_to_display[0], show_badge=True)
        
st.markdown("---")
st.caption("Disclaimer: This tool is for research and educational purposes only. It does not replace professional medical advice.")
