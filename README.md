# Chess at Scale: Analyzing 6.2 Million Lichess Games

Data Visualization final project — EDA notebook (12 analytical questions, Plotly) and
an interactive Streamlit dashboard, built on 6.24M finished games played on Lichess.org
in July 2016.

## Contents
- `DV_Project_.ipynb` — data loading/cleaning + 12 questions, each with a Plotly chart and a data-grounded insight
- `dashboard/app.py` — Streamlit dashboard (4 tabs, KPI tiles, interactive rating-band/time-control filters), built on `dashboard/data/*.csv` — small pre-aggregated tables derived from the full dataset
- `project_plan.md` — project plan, dataset notes, and timeline

## Dataset
[Chess Games (Kaggle) by arevel](https://www.kaggle.com/datasets/arevel/chess-games) —
6.2M Lichess games, ~4GB raw CSV. Not included in this repo (see `.gitignore`); download
it from Kaggle and place it as `chess_games.csv` in the repo root to re-run the notebook
from scratch.

## Live dashboard
(link coming soon)

## Running the dashboard locally
```
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```
