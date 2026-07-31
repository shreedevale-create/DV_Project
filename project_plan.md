# Data Visualization Final Project — Chess: 6.2 Million Lichess Games

**Deadline:** 31 July 2026 (no late submissions). Submit public GitHub repo link via Teams.
**Deliverables:** Jupyter notebook (EDA + 12 questions, Plotly only, export PDF/HTML), presentation PDF, Streamlit dashboard on Community Cloud.
**Bonus target:** complex/large dataset — 6.2 million real games (~4 GB raw), requiring memory-aware loading (`usecols`, dtypes), string parsing of move lists, and heavy aggregation.

## Dataset

- **Source:** Kaggle — "Chess Games" by arevel: https://www.kaggle.com/datasets/arevel/chess-games (6.2M Lichess games, one CSV)
- **Columns:** Event (game type), White/Black (player IDs), Result, UTCDate, UTCTime, WhiteElo, BlackElo, WhiteRatingDiff, BlackRatingDiff, ECO, Opening, TimeControl, Termination, AN (the moves as text)
- **Working strategy (two tables):**
  1. **`games`** — all 6.2M rows, loaded WITHOUT the huge `AN` moves column (`usecols`), with small dtypes (`int16` for Elo). Used for most questions.
  2. **`moves_sample`** — random ~500k rows INCLUDING `AN`, for move-based questions (first move, game length via counting move tokens).
- Save cleaned versions as parquet. Dashboard uses pre-aggregated small files (<25 MB for GitHub).

## Cleaning (done 2026-07-22)

- Stripped whitespace from `Event`, derived `Speed` (Bullet/Blitz/Classical/Correspondence)
- Dropped 14,759 unfinished/irregular games (`Result == '*'`, Abandoned/Rules infraction/Unterminated) → 6,241,425 games
- `category` dtype for repetitive text, `int16` Elo → large memory reduction (from 2.9 GB raw)
- Built `StartTime` datetime + `Hour`, `Weekday`; `AvgElo`, `EloDiff`, `RatingBand` (<1200, 1200–1600, 1600–2000, 2000+)

## 12 Analytical Questions

1. What does the rating distribution of online chess players look like? (histogram, White vs Black Elo)
2. How big is White's first-move advantage, and does it grow with rating? (win rate by color across rating bands)
3. How does win probability change with the Elo gap — how often do upsets happen? (line over binned Elo difference)
4. Which openings are most popular, and how does that differ by rating band? (bar, ECO/Opening)
5. Which popular openings actually score best for White and for Black? (win-rate bars, top 20 openings)
6. How is play split across bullet/blitz/rapid/classical, and how do outcomes differ? (mix + draw rates)
7. How do games end — checkmate, resignation, time forfeit — across rating bands? (stacked bars; do beginners play to mate?)
8. How does draw rate change with rating and time control? (lines)
9. When does the world play chess? (heatmap: hour of day × weekday)
10. How long are games (move count) across time controls and rating bands? (box plots, moves_sample)
11. What do players open with — e4 vs d4 vs the rest — and how does each score? (first-move popularity + win rates, moves_sample)
12. How many rating points are gained or lost per game vs opponent strength? (RatingDiff vs Elo gap)

## Timeline

- **Jul 22:** ✅ data downloaded, loader + cleaning pipeline done
- **Jul 23–26:** Q1–Q12 (3/day), each with one Plotly visual + insight note
- **Jul 27–28:** Streamlit dashboard (pre-aggregated data) + deploy to Community Cloud
- **Jul 29:** notebook polish, export PDF/HTML, presentation PDF
- **Jul 30:** final push to GitHub, submit (one-day buffer before Jul 31)

## Workflow

Guide-only mode: Pushpangi writes all code; Claude instructs and reviews. Copy the .ipynb into the connected folder and say "check" for review.

**Dataset pick is FINAL (locked 2026-07-22). No more changes.**
