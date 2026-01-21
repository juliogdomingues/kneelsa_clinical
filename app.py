import streamlit as st
import numpy as np

# ==========================================
# CONFIGURAÇÃO DO MODELO
# ==========================================
# Coeficientes do modelo de Regressão Logística (5 variáveis)
INTERCEPT = -10.8707
COEF_AGE = 0.0870
COEF_BMI = 0.1199
COEF_SYMPTOMS = 0.3634
COEF_SURGERY = 2.0405
COEF_TRAUMA = 0.7674

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
    
    # Add responsive CSS for smaller screens
    st.markdown(
        """
        <style>
        /* Responsive adjustments for smaller screens */
        @media (max-width: 768px) {
            /* Reduce font size on mobile */
            .stMarkdown p, .stMarkdown div {
                font-size: 0.85rem !important;
            }
            /* Reduce padding */
            .stMarkdown div[style*="padding"] {
                padding: 2px 2px !important;
            }
            /* Make checkboxes slightly smaller */
            div[data-testid="stCheckbox"] {
                transform: scale(0.9);
            }
        }
        @media (max-width: 480px) {
            /* Even smaller on very small screens */
            .stMarkdown p, .stMarkdown div {
                font-size: 0.75rem !important;
            }
            .stMarkdown div[style*="padding"] {
                padding: 1px 1px !important;
            }
            div[data-testid="stCheckbox"] {
                transform: scale(0.85);
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # Use consistent column widths for perfect alignment
    COL_WIDTHS = [35, 10, 10, 45]
    
    # Header row
    col1, col2, col3, col4 = st.columns(COL_WIDTHS)
    with col1:
        st.markdown('<div style="text-align:right; font-weight:700; padding:5px;">Right knee (R)</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div style="text-align:center; padding:5px;">{knee_svg("Right")}</div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div style="text-align:center; padding:5px;">{knee_svg("Left")}</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div style="text-align:left; font-weight:700; padding:5px;">Left knee (L)</div>', unsafe_allow_html=True)
    
    # Row 1: Symptoms
    col1, col2, col3, col4 = st.columns(COL_WIDTHS)
    with col1:
        st.markdown(f'<div style="text-align:right; padding:8px 5px;">{SYMPTOMS_LABEL}</div>', unsafe_allow_html=True)
    with col2:
        st.checkbox(SYMPTOMS_LABEL, key="symptoms_Right", label_visibility="collapsed", help="Pain, discomfort, or stiffness that lasted for most days for at least one month in the last 12 months")
    with col3:
        st.checkbox(SYMPTOMS_LABEL, key="symptoms_Left", label_visibility="collapsed", help="Pain, discomfort, or stiffness that lasted for most days for at least one month in the last 12 months")
    with col4:
        st.markdown(f'<div style="text-align:left; padding:8px 5px;">{SYMPTOMS_LABEL}</div>', unsafe_allow_html=True)
    
    # Row 2: Surgery
    col1, col2, col3, col4 = st.columns(COL_WIDTHS)
    with col1:
        st.markdown(f'<div style="text-align:right; padding:8px 5px;">{SURGERY_LABEL}</div>', unsafe_allow_html=True)
    with col2:
        st.checkbox(SURGERY_LABEL, key="surgery_Right", label_visibility="collapsed", help="Ever undergone any type of surgery, including arthroscopy, meniscal or ligament repair?")
    with col3:
        st.checkbox(SURGERY_LABEL, key="surgery_Left", label_visibility="collapsed", help="Ever undergone any type of surgery, including arthroscopy, meniscal or ligament repair?")
    with col4:
        st.markdown(f'<div style="text-align:left; padding:8px 5px;">{SURGERY_LABEL}</div>', unsafe_allow_html=True)
    
    # Row 3: Trauma
    col1, col2, col3, col4 = st.columns(COL_WIDTHS)
    with col1:
        st.markdown(f'<div style="text-align:right; padding:8px 5px;">{TRAUMA_LABEL}</div>', unsafe_allow_html=True)
    with col2:
        st.checkbox(TRAUMA_LABEL, key="trauma_Right", label_visibility="collapsed", help="Ever injured or suffered trauma that caused difficulty walking for at least one week?")
    with col3:
        st.checkbox(TRAUMA_LABEL, key="trauma_Left", label_visibility="collapsed", help="Ever injured or suffered trauma that caused difficulty walking for at least one week?")
    with col4:
        st.markdown(f'<div style="text-align:left; padding:8px 5px;">{TRAUMA_LABEL}</div>', unsafe_allow_html=True)


st.markdown("---")

# ==========================================
# CÁLCULO
# ==========================================
def calculate_probability(age, bmi, symptoms, surgery, trauma):
    """Calculate the probability of KOA for a single knee."""
    logit = (
        INTERCEPT +
        (COEF_AGE * age) +
        (COEF_BMI * bmi) +
        (COEF_SYMPTOMS * 1 if symptoms else 0) +
        (COEF_SURGERY * 1 if surgery else 0) +
        (COEF_TRAUMA * 1 if trauma else 0)
    )
    probability = 1 / (1 + np.exp(-logit))
    return probability

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
