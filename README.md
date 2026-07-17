# AquaMind

Technical prototype for an algal-bloom risk-model pipeline using Sentinel-2, environmental forecasts, XGBoost, and SHAP.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://aquamind-d8apywwzzyvy25ydmw8ufh.streamlit.app)

- Live synthetic model demo: https://aquamind-d8apywwzzyvy25ydmw8ufh.streamlit.app
- Source repository: https://github.com/suriyen-creator/aqua_mind

## Streamlit demo

This page is a **Synthetic Technical Demo**. It shows XGBoost probability and SHAP contributions from generated data. It is not the current risk at Bangsaen and is not field-validated accuracy.

```bash
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Project structure

- `backend/`: FastAPI, data adapters, dataset contract, validation gate, and tests
- `frontend/`: Next.js dashboard
- `Model/`: synthetic dataset generator and experimental training scripts
- `AquaMind_Final_ReportV2.md`: final report draft

The operational endpoint deliberately returns no live risk probability until a model passes validation with verified ground truth.
