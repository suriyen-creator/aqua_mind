# AquaMind

Weather-first coastal environmental-watch prototype using real Open-Meteo inputs, optional quality-gated Sentinel-2 evidence, an XGBoost expert-rule surrogate, SHAP explanations, and a farmer action rule layer.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://aquamind-d8apywwzzyvy25ydmw8ufh.streamlit.app)

- Live environmental watch: https://aquamind-d8apywwzzyvy25ydmw8ufh.streamlit.app
- Source repository: https://github.com/suriyen-creator/aqua_mind

## Streamlit live watch

The page fetches real Weather/Ocean forecast inputs for Bangsaen and uses the latest quality-controlled Sentinel-2 observation as secondary evidence. It displays a 0–100 **environmental watch index**, not bloom probability or field-validated accuracy. XGBoost learns a disclosed expert-rule score; SHAP explains the score in watch-index points and the rule layer recommends what to verify locally.

```bash
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Project structure

- `backend/`: FastAPI, data adapters, dataset contract, validation gate, and tests
- `frontend/`: Next.js dashboard
- `Model/`: synthetic dataset generator and experimental training scripts
- `AquaMind_Final_ReportV2.md`: final report draft

The watch index works without imagery because Weather/Ocean is primary. A separate operational bloom probability remains disabled until a model passes validation with verified ground truth.
