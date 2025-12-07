# Kneelsa-Clinical: KOA Screening Tool (Streamlit App)

This repository contains the source code for the **Kneelsa-Clinical** web application, a screening tool for Knee Osteoarthritis (KOA) developed as part of the ELSA-Brasil MSK study.

## About

This app implements the **5-variable clinical prediction model** described in our research. It serves as the initial triage step in a serial multimodal pipeline (Clinical -> Image).

**Live Demo:** [https://kneelsa-clinical.streamlit.app/](https://kneelsa-clinical.streamlit.app/)

## Model Details

- **Type:** Logistic Regression
- **Input Variables:**
  1. Age (years)
  2. BMI ($kg/m^2$)
  3. Frequent Knee Pain (Yes/No)
  4. History of Knee Surgery (Yes/No)
  5. History of Knee Trauma (Yes/No)
- **Output:** Probability of Radiographic KOA (KL $\ge$ 2)

## How to Run Locally

1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run app.py
   ```

## Citation

If you use this tool, please cite our work:

> Domingues, J. G., et al. "Cost-Effective Screening for Knee Osteoarthritis: A Serial Clinical-Image AI Pipeline." (2025).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
