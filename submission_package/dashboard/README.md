# Chess at Scale — Streamlit Dashboard

This folder contains a Streamlit dashboard analyzing 6.24M Lichess games (pre-aggregated data).

Quick start (recommended):

1. Create and activate a Python environment (macOS / Linux):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

2. Run the app locally:

```bash
cd dashboard
python3 -m streamlit run app.py
```

Open http://localhost:8501 in your browser.

Docker (build & run):

```bash
cd dashboard
docker build -t chess-dashboard:latest .
docker run -p 8501:8501 chess-dashboard:latest
```

Deploy options:

- Streamlit Cloud: push the `dashboard/` folder to a GitHub repo and connect the app on https://share.streamlit.io. Set the app path to `dashboard/app.py`.
- Heroku: use the provided `Dockerfile` or a `Procfile` (already included) to deploy.

Included files:

- `app.py` — Streamlit app source
- `requirements.txt` — Python dependencies
- `data/` — small pre-aggregated CSVs used by the app
- `Dockerfile`, `.dockerignore`, `Procfile` — deployment helpers

Next steps you might want me to do:
- Polish visuals and accessibility in `app.py` (labels, color contrast, alt text)
- Add a small logo and update page config
- Create CI to run a smoke test on `streamlit run` before deploy

If you want, I can now polish visuals and accessibility in `app.py` — shall I proceed?