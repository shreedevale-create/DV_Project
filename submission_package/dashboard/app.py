from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------------------
# Page setup
# ----------------------------------------------------------------------------
st.set_page_config(page_title="Chess at Scale: 6.2M Lichess Games", layout="wide")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# ----------------------------------------------------------------------------
# Palette (validated categorical + sequential ramp — see project's dataviz notes)
# ----------------------------------------------------------------------------
SURFACE = "#fcfcfb"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"

CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
RATING_ORDER = ["<1200", "1200-1600", "1600-2000", "2000+"]
SPEED_ORDER = ["Bullet", "Blitz", "Classical", "Correspondence"]
RATING_RAMP = dict(zip(RATING_ORDER, ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]))  # light -> dark blue

RESULT_COLOR = {"1-0": CAT[0], "0-1": CAT[1], "1/2-1/2": CAT[2]}
RESULT_LABEL = {"1-0": "White win", "0-1": "Black win", "1/2-1/2": "Draw"}
SPEED_COLOR = dict(zip(SPEED_ORDER, CAT[:4]))
OUTCOME_COLOR = {"Checkmate": CAT[0], "Resignation": CAT[1], "Draw": CAT[2], "Time forfeit": CAT[3]}


def style(fig, *, y_pct=False, x_title=None, y_title=None, legend_title=None):
    fig.update_layout(
        plot_bgcolor=SURFACE,
        paper_bgcolor=SURFACE,
        font=dict(family="system-ui, -apple-system, 'Segoe UI', sans-serif", color=INK_PRIMARY, size=13),
        title=dict(font=dict(size=16, color=INK_PRIMARY)),
        legend=dict(title=legend_title, bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=48, l=10, r=10, b=10),
        hoverlabel=dict(bgcolor="white", font_size=12),
    )
    fig.update_xaxes(showgrid=False, linecolor=AXIS, title=x_title, color=INK_SECONDARY)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, linecolor=AXIS, title=y_title, color=INK_SECONDARY,
                      tickformat=".0%" if y_pct else None)
    return fig


@st.cache_data
def load(name):
    return pd.read_csv(DATA_DIR / f"{name}.csv")


kpis = load("kpis").iloc[0]
elo_dist = load("elo_dist")
outcome_by_band = load("outcome_by_band")
winrate_by_gap = load("winrate_by_gap")
opening_by_band = load("opening_by_band")
opening_results = load("opening_results")
speed_outcome = load("speed_outcome")
speed_counts = load("speed_counts")
outcome_type_by_band = load("outcome_type_by_band")
draw_rate = load("draw_rate")
heatmap = load("heatmap")
game_length = load("game_length")
first_move = load("first_move")
rating_diff_gap = load("rating_diff_gap")

# ----------------------------------------------------------------------------
# Header + KPIs
# ----------------------------------------------------------------------------
st.title("Chess at Scale: Analyzing 6.2 Million Lichess Games")
st.caption(
    "6.24M finished games played on Lichess.org in July 2016 — ratings, openings, "
    "time controls, and outcomes. [Source: Kaggle — arevel/chess-games]"
)

k1, k2, k3, k4, k5 = st.columns([1, 1, 1, 1, 1.4])
k1.metric("Games analyzed", f"{int(kpis['TotalGames']):,}")
k2.metric("Avg. rating", f"{kpis['AvgElo']:.0f}")
k3.metric("White win rate", f"{kpis['WhiteWinRate']:.1%}")
k4.metric("Draw rate", f"{kpis['DrawRate']:.1%}")
with k5:
    st.markdown(
        f"""<div style="font-size:0.875rem;color:{INK_SECONDARY};">Most-played opening</div>
        <div style="font-size:1.75rem;font-weight:600;line-height:1.3;color:{INK_PRIMARY};">
        {kpis['TopOpening']}</div>""",
        unsafe_allow_html=True,
    )

st.divider()

# ----------------------------------------------------------------------------
# Sidebar filters — apply to every chart that carries a RatingBand / Speed column
# ----------------------------------------------------------------------------
st.sidebar.header("Filters")
sel_bands = st.sidebar.multiselect("Rating band", RATING_ORDER, default=RATING_ORDER)
sel_speeds = st.sidebar.multiselect("Time control", SPEED_ORDER, default=SPEED_ORDER)
st.sidebar.caption("Filters apply to every chart broken out by rating band or time control.")

bands = sel_bands or RATING_ORDER
speeds = sel_speeds or SPEED_ORDER


def show_table(df, key):
    with st.expander("View as table"):
        st.dataframe(df, use_container_width=True, key=key)


tab1, tab2, tab3, tab4 = st.tabs(
    ["Overview & Ratings", "Openings", "Time & Format", "Endgames & Moves"]
)

# ----------------------------------------------------------------------------
# TAB 1 — Overview & Ratings
# ----------------------------------------------------------------------------
with tab1:
    c1, c2 = st.columns(2)

    with c1:
        fig = go.Figure(go.Bar(x=elo_dist["Elo"], y=elo_dist["Games"], marker_color=CAT[0]))
        fig.update_layout(title="Rating Distribution (25-point buckets)")
        style(fig, x_title="Average game rating", y_title="Games")
        st.plotly_chart(fig, use_container_width=True)
        show_table(elo_dist, "t_elo")

    with c2:
        d = outcome_by_band[outcome_by_band["RatingBand"].isin(bands)]
        fig = go.Figure()
        for res in ["1-0", "1/2-1/2", "0-1"]:
            dd = d[d["Result"] == res]
            fig.add_trace(go.Bar(x=dd["RatingBand"], y=dd["Share"], name=RESULT_LABEL[res],
                                  marker_color=RESULT_COLOR[res]))
        fig.update_layout(title="White's Edge: Outcome Share by Rating Band", barmode="group",
                           xaxis=dict(categoryorder="array", categoryarray=RATING_ORDER))
        style(fig, y_pct=True, x_title="Rating band", y_title="Share of games", legend_title="Result")
        st.plotly_chart(fig, use_container_width=True)
        show_table(d, "t_outcome_band")

    c3, c4 = st.columns(2)
    with c3:
        fig = go.Figure(go.Scatter(x=winrate_by_gap["Gap"], y=winrate_by_gap["WhiteWinRate"],
                                    mode="lines+markers", line=dict(color=CAT[0], width=2),
                                    marker=dict(size=8)))
        fig.update_layout(title="Win Probability vs. Rating Gap (White − Black)")
        style(fig, y_pct=True, x_title="Elo gap", y_title="White win rate")
        st.plotly_chart(fig, use_container_width=True)
        show_table(winrate_by_gap, "t_gap")

    with c4:
        fig = go.Figure(go.Scatter(x=rating_diff_gap["Gap"], y=rating_diff_gap["WhiteRatingDiff"],
                                    mode="lines+markers", line=dict(color=CAT[1], width=2),
                                    marker=dict(size=8)))
        fig.add_hline(y=0, line_dash="dot", line_color=INK_MUTED)
        fig.update_layout(title="Rating Points Gained/Lost vs. Opponent Strength")
        style(fig, x_title="Elo gap", y_title="Avg. White rating change")
        st.plotly_chart(fig, use_container_width=True)
        show_table(rating_diff_gap, "t_ratingdiff")

# ----------------------------------------------------------------------------
# TAB 2 — Openings
# ----------------------------------------------------------------------------
with tab2:
    d = opening_by_band[opening_by_band["RatingBand"].isin(bands)]
    order = (d.groupby("OpeningFamily")["Games"].sum().sort_values(ascending=False).index.tolist())
    fig = go.Figure()
    for band in [b for b in RATING_ORDER if b in bands]:
        dd = d[d["RatingBand"] == band]
        fig.add_trace(go.Bar(x=dd["OpeningFamily"], y=dd["Share"], name=band, marker_color=RATING_RAMP[band]))
    fig.update_layout(title="Top Openings: Share of Games by Rating Band", barmode="group",
                       xaxis=dict(categoryorder="array", categoryarray=order))
    style(fig, y_pct=True, x_title=None, y_title="Share within band", legend_title="Rating band")
    fig.update_xaxes(tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)
    show_table(d, "t_openbyband")

    fig = go.Figure()
    ordered = opening_results.sort_values("1-0", ascending=False)
    for res in ["1-0", "1/2-1/2", "0-1"]:
        fig.add_trace(go.Bar(x=ordered["OpeningFamily"], y=ordered[res], name=RESULT_LABEL[res],
                              marker_color=RESULT_COLOR[res]))
    fig.update_layout(title="Result Split for the Top 20 Openings (sorted by White win rate)",
                       barmode="stack")
    style(fig, y_pct=True, y_title="Share of games", legend_title="Result")
    fig.update_xaxes(tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)
    show_table(opening_results, "t_openresults")

# ----------------------------------------------------------------------------
# TAB 3 — Time & Format
# ----------------------------------------------------------------------------
with tab3:
    c1, c2 = st.columns(2)
    with c1:
        sc = speed_counts[speed_counts["Speed"].isin(speeds)]
        fig = go.Figure(go.Bar(x=sc["Speed"], y=sc["Games"],
                                marker_color=[SPEED_COLOR[s] for s in sc["Speed"]]))
        fig.update_layout(title="Games by Time Control",
                           xaxis=dict(categoryorder="array", categoryarray=SPEED_ORDER))
        style(fig, x_title="Time control", y_title="Games")
        st.plotly_chart(fig, use_container_width=True)
        show_table(sc, "t_speedcounts")

    with c2:
        d = speed_outcome[speed_outcome["Speed"].isin(speeds)]
        fig = go.Figure()
        for res in ["1-0", "1/2-1/2", "0-1"]:
            dd = d[d["Result"] == res]
            fig.add_trace(go.Bar(x=dd["Speed"], y=dd["Share"], name=RESULT_LABEL[res],
                                  marker_color=RESULT_COLOR[res]))
        fig.update_layout(title="Outcomes by Time Control", barmode="group",
                           xaxis=dict(categoryorder="array", categoryarray=SPEED_ORDER))
        style(fig, y_pct=True, x_title="Time control", y_title="Share of games", legend_title="Result")
        st.plotly_chart(fig, use_container_width=True)
        show_table(d, "t_speedoutcome")

    c3, c4 = st.columns(2)
    with c3:
        d = draw_rate[(draw_rate["RatingBand"].isin(bands)) & (draw_rate["Speed"].isin(speeds))]
        fig = go.Figure()
        for spd in [s for s in SPEED_ORDER if s in speeds]:
            dd = d[d["Speed"] == spd].sort_values("RatingBand", key=lambda s: s.map(RATING_ORDER.index))
            fig.add_trace(go.Scatter(x=dd["RatingBand"], y=dd["DrawRate"], mode="lines+markers",
                                      name=spd, line=dict(color=SPEED_COLOR[spd], width=2),
                                      marker=dict(size=8)))
        fig.update_layout(title="Draw Rate by Rating Band and Time Control",
                           xaxis=dict(categoryorder="array", categoryarray=RATING_ORDER))
        style(fig, y_pct=True, x_title="Rating band", y_title="Draw rate", legend_title="Time control")
        st.plotly_chart(fig, use_container_width=True)
        show_table(d, "t_drawrate")

    with c4:
        pivot = heatmap.pivot(index="Weekday", columns="Hour", values="Games")
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        pivot = pivot.reindex(weekday_order)
        fig = go.Figure(go.Heatmap(z=pivot.values, x=pivot.columns, y=pivot.index,
                                    colorscale=[[0, "#cde2fb"], [1, "#0d366b"]],
                                    colorbar=dict(title="Games")))
        fig.update_layout(title="When Does the World Play? (Hour of Day, UTC)")
        style(fig, x_title="Hour (UTC)", y_title=None)
        st.plotly_chart(fig, use_container_width=True)
        show_table(heatmap, "t_heatmap")

# ----------------------------------------------------------------------------
# TAB 4 — Endgames & Moves
# ----------------------------------------------------------------------------
with tab4:
    c1, c2 = st.columns(2)
    with c1:
        d = outcome_type_by_band[outcome_type_by_band["RatingBand"].isin(bands)]
        fig = go.Figure()
        for oc in ["Checkmate", "Resignation", "Time forfeit", "Draw"]:
            dd = d[d["Outcome"] == oc]
            fig.add_trace(go.Bar(x=dd["RatingBand"], y=dd["Share"], name=oc, marker_color=OUTCOME_COLOR[oc]))
        fig.update_layout(title="How Games End, by Rating Band", barmode="stack",
                           xaxis=dict(categoryorder="array", categoryarray=RATING_ORDER))
        style(fig, y_pct=True, x_title="Rating band", y_title="Share of games", legend_title="Outcome")
        st.plotly_chart(fig, use_container_width=True)
        show_table(d, "t_outcometype")

    with c2:
        fig = go.Figure()
        for i, (_, row) in enumerate(first_move.iterrows()):
            fig.add_trace(go.Bar(x=[row["FirstMoveGroup"]], y=[row["Share"]], name="Share",
                                  marker_color=CAT[0], legendgroup="Share", showlegend=(i == 0)))
            fig.add_trace(go.Bar(x=[row["FirstMoveGroup"]], y=[row["WhiteWinRate"]], name="White win rate",
                                  marker_color=CAT[1], legendgroup="WhiteWinRate", showlegend=(i == 0)))
        fig.update_layout(title="First Move: Popularity vs. White Win Rate", barmode="group")
        style(fig, y_pct=True, x_title="First move", y_title=None)
        st.plotly_chart(fig, use_container_width=True)
        show_table(first_move, "t_firstmove")

    d = game_length[(game_length["RatingBand"].isin(bands)) & (game_length["Speed"].isin(speeds))]
    fig = go.Figure()
    for band in [b for b in RATING_ORDER if b in bands]:
        dd = d[d["RatingBand"] == band].sort_values("Speed", key=lambda s: s.map(SPEED_ORDER.index))
        fig.add_trace(go.Box(x=dd["Speed"], q1=dd["Q1"], median=dd["Median"], q3=dd["Q3"],
                              lowerfence=dd["Min"], upperfence=dd["Max"],
                              name=band, marker_color=RATING_RAMP[band]))
    fig.update_layout(title="Game Length (Full Moves) by Time Control and Rating Band", boxmode="group",
                       xaxis=dict(categoryorder="array", categoryarray=SPEED_ORDER))
    style(fig, x_title="Time control", y_title="Moves", legend_title="Rating band")
    st.plotly_chart(fig, use_container_width=True)
    show_table(d, "t_gamelength")

st.divider()
st.caption(
    "Built with Streamlit + Plotly on pre-aggregated data (~13KB total) derived from the "
    "full 6.24M-row dataset. Full analysis notebook: DV_Project_.ipynb."
)
