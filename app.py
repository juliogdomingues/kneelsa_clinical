import streamlit as st
import numpy as np

# ==========================================
# CONFIGURAÇÃO DO MODELO
# ==========================================
# Coeficientes do modelo de Regressão Logística (5 variáveis)
# Fonte: results_final_pipeline/final_5var_model_ORs.csv
INTERCEPT = -10.8707
COEF_AGE = 0.0870
COEF_BMI = 0.1199
COEF_PAIN = 0.3634
COEF_SURGERY = 2.0405
COEF_TRAUMA = 0.7674

# ==========================================
# INTERFACE DO USUÁRIO
# ==========================================
st.set_page_config(page_title="Kneelsa-Clinical", page_icon="🦵")

st.title("Kneelsa-Clinical: KOA Screening Tool")
st.markdown("""
This tool implements the **5-variable clinical prediction model** developed in the ELSA-Brasil MSK study.
It estimates the probability of radiographic Knee Osteoarthritis (KL $\ge$ 2) **per knee**.
""")

st.markdown("---")

# Patient Demographics (same for both knees)
st.subheader("Patient Demographics")
col1, col2 = st.columns(2)

with col1:
    age = st.number_input("Age (years)", min_value=30, max_value=100, value=55)

with col2:
    bmi = st.number_input("BMI (kg/m²)", min_value=15.0, max_value=60.0, value=25.0, format="%.1f")

st.markdown("---")

# Knee-specific Clinical Features
st.subheader("Clinical Features per Knee")

# Select which knees to assess
knee_selection = st.radio(
    "Which knee(s) would you like to assess?",
    options=["Left Knee Only", "Right Knee Only", "Both Knees"],
    index=2
)

# Determine which knees to assess
knees_to_assess = []
if "Left" in knee_selection:
    knees_to_assess.append("Left")
if "Right" in knee_selection:
    knees_to_assess.append("Right")

# Create columns for knee inputs
if len(knees_to_assess) == 1:
    # Single column for one knee
    knee = knees_to_assess[0]
    st.markdown(f"#### {knee} Knee")
    pain = st.checkbox(f"Frequent {knee} Knee Pain?", key=f"pain_{knee}", help="Pain on most days of the last month")
    surgery = st.checkbox(f"History of {knee} Knee Surgery?", key=f"surgery_{knee}")
    trauma = st.checkbox(f"History of {knee} Knee Trauma/Injury?", key=f"trauma_{knee}")
else:
    # Two columns for both knees
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("#### Left Knee")
        pain_left = st.checkbox("Frequent Pain?", key="pain_Left", help="Pain on most days in a month in the last 12 months")
        surgery_left = st.checkbox("History of Surgery?", key="surgery_Left")
        trauma_left = st.checkbox("History of Trauma/Injury?", key="trauma_Left")
    
    with col_right:
        st.markdown("#### Right Knee")
        pain_right = st.checkbox("Frequent Pain?", key="pain_Right", help="Pain on most days in a month in the last 12 months")
        surgery_right = st.checkbox("History of Surgery?", key="surgery_Right")
        trauma_right = st.checkbox("History of Trauma/Injury?", key="trauma_Right")

# ==========================================
# CÁLCULO
# ==========================================
def calculate_probability(age, bmi, pain, surgery, trauma):
    """Calculate the probability of KOA for a single knee."""
    # Equação Logit: z = B0 + B1*X1 + ...
    logit = (
        INTERCEPT +
        (COEF_AGE * age) +
        (COEF_BMI * bmi) +
        (COEF_PAIN * 1 if pain else 0) +
        (COEF_SURGERY * 1 if surgery else 0) +
        (COEF_TRAUMA * 1 if trauma else 0)
    )
    
    # Função Sigmoide: p = 1 / (1 + e^-z)
    probability = 1 / (1 + np.exp(-logit))
    return probability

st.markdown("---")

if st.button("Calculate Probability", type="primary"):
    st.markdown("---")
    st.subheader("Results")
    
    # Display results for each knee
    for knee in knees_to_assess:
        knee_pain = st.session_state.get(f"pain_{knee}", False)
        knee_surgery = st.session_state.get(f"surgery_{knee}", False)
        knee_trauma = st.session_state.get(f"trauma_{knee}", False)
        
        prob = calculate_probability(
            age=age,
            bmi=bmi,
            pain=knee_pain,
            surgery=knee_surgery,
            trauma=knee_trauma
        )
        
        # Create a nice display with metric
        st.metric(
            label=f"{knee} Knee - Estimated Probability of KOA",
            value=f"{prob:.1%}",
            help="Probability of radiographic KOA (KL ≥ 2)"
        )
        
        # Additional context
        st.write(f"This estimate is based on: Age ({age}), BMI ({bmi}), and clinical features specific to the {knee.lower()} knee.")

st.markdown("---")
st.caption("Disclaimer: This tool is for research and educational purposes only. It does not replace professional medical advice.")
