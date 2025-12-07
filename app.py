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

# Limiar de corte (Threshold) para 90% de sensibilidade
# Este valor deve ser calibrado com base na curva ROC do modelo.
# Para fins de demonstração, usaremos um valor ilustrativo que pode ser ajustado.
THRESHOLD = 0.10 

# ==========================================
# INTERFACE DO USUÁRIO
# ==========================================
st.set_page_config(page_title="Kneelsa-Clinical", page_icon="🦵")

st.title("Kneelsa-Clinical: KOA Screening Tool")
st.markdown("""
This tool implements the **5-variable clinical prediction model** developed in the ELSA-Brasil MSK study.
It estimates the probability of radiographic Knee Osteoarthritis (KL $\ge$ 2).
""")

st.markdown("---")

# Colunas para input
col1, col2 = st.columns(2)

with col1:
    st.subheader("Patient Demographics")
    age = st.number_input("Age (years)", min_value=30, max_value=100, value=55)
    bmi = st.number_input("BMI (kg/m²)", min_value=15.0, max_value=60.0, value=25.0, format="%.1f")

with col2:
    st.subheader("Clinical History")
    pain = st.checkbox("Frequent Knee Pain?", help="Pain on most days of the last month")
    surgery = st.checkbox("History of Knee Surgery?")
    trauma = st.checkbox("History of Knee Trauma/Injury?")

# ==========================================
# CÁLCULO
# ==========================================
def calculate_probability(age, bmi, pain, surgery, trauma):
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

if st.button("Calculate Risk", type="primary"):
    prob = calculate_probability(age, bmi, pain, surgery, trauma)
    
    st.markdown("---")
    st.subheader("Results")
    
    # Mostrador visual
    st.metric(label="Estimated Probability of KOA", value=f"{prob:.1%}")
    
    # Lógica de Decisão (Triagem)
    if prob >= THRESHOLD:
        st.error(f"⚠️ **High Risk (Screening Positive)**")
        st.write(f"The estimated probability is above the screening threshold ({THRESHOLD:.0%}).")
        st.write("**Recommendation:** Proceed to radiographic evaluation (X-Ray) or image-based AI analysis.")
    else:
        st.success(f"✅ **Low Risk (Screening Negative)**")
        st.write(f"The estimated probability is below the screening threshold ({THRESHOLD:.0%}).")
        st.write("**Recommendation:** Radiographic evaluation may not be necessary at this moment unless clinical suspicion remains high.")

st.markdown("---")
st.caption("Disclaimer: This tool is for research and educational purposes only. It does not replace professional medical advice.")
