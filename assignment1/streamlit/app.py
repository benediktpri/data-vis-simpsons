import base64
from pathlib import Path
from typing import Any

import altair as alt
import pandas as pd

import streamlit as st

_DIR = Path(__file__).resolve().parent

st.set_page_config(page_title="Simpsons Dashboard", layout="wide")

# reduce margins of streamlit
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
        }
        header[data-testid="stHeader"] {
            display: none;
        }
    </style>
""",
    unsafe_allow_html=True,
)


header_col1, header_col2, header_col3 = st.columns(
    [1, 1, 1], vertical_alignment="center"
)

with header_col1:
    # 1. Read the image in full resolution and encode it
    with open(_DIR / "logo.png", "rb") as image_file:
        encoded_logo_img = base64.b64encode(image_file.read()).decode()
    with open(_DIR / "donut.png", "rb") as image_file:
        encoded_donut_img = base64.b64encode(image_file.read()).decode()
    img_html = f"""
        <div style="white-space: nowrap;">
        <img src="data:image/png;base64,{encoded_logo_img}" style="width: 190px; height: 120px; object-fit: contain; image-rendering: high-quality; display: inline-block; vertical-align: middle; margin: 0; padding: 0;">
        <img src="data:image/png;base64,{encoded_donut_img}" style="width: 90px; height: 90px; object-fit: contain; image-rendering: high-quality; display: inline-block; vertical-align: middle; margin: 0 0 0 20px; padding: 0;">
        </div>
        """
    st.markdown(img_html, unsafe_allow_html=True)


with header_col2:
    # Use HTML instead of st.title/st.write to strip out extra margins
    st.markdown(
        """
        <div style='text-align: center;'>
            <h3 style='margin-top: 0px; margin-bottom: 0px; padding-bottom: 0px; white-space: nowrap;'>The Simpsons: Beyond the Golden Age</h3>
            <p style='margin-top: 5px; margin-bottom: 0px; font-size: 16px;'>Viewership & Ratings · Seasons 1–27 (1989–2016)</p>
            <p style='margin-top: 2px; margin-bottom: 0px; font-size: 16px;'>Data: <a href="https://www.kaggle.com/datasets/prashant111/the-simpsons-dataset" target="_blank">The Simpsons Dataset (Kaggle)</a></p>
            <p style='margin-top: 2px; margin-bottom: 0px; font-size: 16px;'>By Benedikt Prisett & Stijn Diemel</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with header_col3:
    html_legend = """
    <div style="display: flex; justify-content: flex-end;">
        <div style="display: flex; align-items: center; gap: 16px;">
            <div style="display: flex; flex-direction: column; align-items: center; width: 100px;">
                <span style="font-size: 14px; line-height: 1.3; text-align: center;"><span style="white-space: nowrap;">Golden Age</span><br><span style="white-space: nowrap;">Season 1–8</span></span>
                <span style="width: 100%; height: 10px; border-radius: 3px; background-color: #DDAA33; margin-top: 4px; display: block;"></span>
            </div>
            <div style="display: flex; flex-direction: column; align-items: center; width: 100px;">
                <span style="font-size: 14px; line-height: 1.3; text-align: center;"><span style="white-space: nowrap;">Transition</span><br><span style="white-space: nowrap;">Season 9–18</span></span>
                <span style="width: 100%; height: 10px; border-radius: 3px; background-color: #BB5566; margin-top: 4px; display: block;"></span>
            </div>
            <div style="display: flex; flex-direction: column; align-items: center; width: 100px;">
                <span style="font-size: 14px; line-height: 1.3; text-align: center;"><span style="white-space: nowrap;">Decline</span><br><span style="white-space: nowrap;">Season 19–27</span></span>
                <span style="width: 100%; height: 10px; border-radius: 3px; background-color: #004488; margin-top: 4px; display: block;"></span>
            </div>
        </div>
    </div>
    """
    st.markdown(html_legend, unsafe_allow_html=True)

st.markdown(
    "<hr style='margin-top: 0px; margin-bottom: 20px;'>", unsafe_allow_html=True
)


@st.cache_data
def load_data():
    df = pd.read_csv(_DIR / "../data/clean_data/simpsons_episodes_clean.csv")
    df["original_air_date"] = pd.to_datetime(df["original_air_date"])
    df["era"] = pd.cut(
        df["season"],
        bins=[0, 8, 18, 27],
        labels=["Golden Age (S1–8)", "Transition (S9–18)", "Decline (S19–27)"],
    )
    return df


df = load_data()

# Reusable Era Scales
era_domain = ["Golden Age (S1–8)", "Transition (S9–18)", "Decline (S19–27)"]
era_colors = ["#DDAA33", "#BB5566", "#004488"]
era_scale = alt.Scale(domain=era_domain, range=era_colors)


# Global chart styling
@alt.theme.register("dashboard", enable=True)
def dashboard_theme() -> Any:
    return {
        "config": {
            "title": {"fontSize": 16},
            "axis": {"titleFontSize": 14, "labelFontSize": 12},
        }
    }


# ==========================================
# Build the Charts
# ==========================================

# --- Question 1 Chart ---
q1_era_box = (
    alt.Chart(df)
    .mark_boxplot(size=15)
    .encode(
        x=alt.X("season:O", title="Season", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("imdb_rating:Q", title="IMDb Rating", scale=alt.Scale(domain=[4, 10])),
        color=alt.Color(
            "era:N", scale=era_scale, legend=None
        ),
    )
)
q1_era_mean = (
    alt.Chart(df)
    .mark_line(color="black", strokeWidth=2)
    .encode(x=alt.X("season:O"), y=alt.Y("mean(imdb_rating):Q"))
)
q1_era_points = q1_era_mean.mark_point(color="black", filled=True, size=40)
chart1 = (q1_era_box + q1_era_mean + q1_era_points).properties(
    height=350, title="IMDb Ratings Across Seasons"
)

# --- Question 2 Chart ---
q2_era_box = (
    alt.Chart(df)
    .mark_boxplot(size=15)
    .encode(
        x=alt.X("season:O", title="Season", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("us_viewers_in_millions:Q", title="US Viewers (millions)"),
        color=alt.Color(
            "era:N", scale=era_scale, legend=None
        ),
    )
)
q2_era_mean = (
    alt.Chart(df)
    .mark_line(color="black", strokeWidth=2)
    .encode(x=alt.X("season:O"), y=alt.Y("mean(us_viewers_in_millions):Q"))
)
q2_era_points = q2_era_mean.mark_point(color="black", filled=True, size=40)
chart2 = (q2_era_box + q2_era_mean + q2_era_points).properties(
    height=350, title="US Viewership Across Seasons"
)

# --- Question 3 Chart ---
chart3 = (
    alt.Chart(df)
    .mark_circle(size=50, opacity=0.5)
    .encode(
        x=alt.X("us_viewers_in_millions:Q", title="US Viewers (millions)"),
        y=alt.Y("imdb_rating:Q", title="IMDb Rating", scale=alt.Scale(domain=[4, 10])),
        color=alt.Color("era:N", scale=era_scale, legend=None),
        tooltip=[
            "title:N",
            "season:O",
            "era:N",
            "imdb_rating:Q",
            "us_viewers_in_millions:Q",
        ],
    )
    .properties(height=300, title="Viewership vs. Rating Correlation")
)

# --- Question 4 Chart ---
df_thu_sun = df[df["weekday"].isin(["Thursday", "Sunday"])].copy()
thu_sun_labels = ["Thursday (S2–5)", "Sunday (S1 & S6–25)"]
df_thu_sun["weekday_label"] = df_thu_sun["weekday"].map(
    {"Thursday": thu_sun_labels[0], "Sunday": thu_sun_labels[1]}
)
chart4 = (
    alt.Chart(df_thu_sun)
    .mark_boxplot(size=40)
    .encode(
        x=alt.X(
            "weekday_label:O",
            sort=thu_sun_labels,
            title="Day of Week",
            axis=alt.Axis(labelAngle=0, labelAlign="center"),
        ),
        y=alt.Y("us_viewers_in_millions:Q", title="US Viewers (millions)"),
        color=alt.Color(
            "weekday_label:N",
            sort=thu_sun_labels,
            legend=None,
            scale=alt.Scale(domain=thu_sun_labels, range=["#555555"]),
        ),
    )
    .properties(height=300, title="Viewership by Airing Day")
)

# --- Question 5 Chart ---
pos_era_abs = (
    df.groupby(["era", "number_in_season"], observed=True)["us_viewers_in_millions"]
    .agg(["mean", "count"])
    .reset_index()
)
pos_era_abs = pos_era_abs[pos_era_abs["count"] >= 3]
era_avgs = (
    df.groupby("era", observed=True)["us_viewers_in_millions"]
    .mean()
    .reset_index(name="era_mean")
)

base = alt.Chart(pos_era_abs).encode(
    x=alt.X("number_in_season:O", title="Episode Number", axis=alt.Axis(labelAngle=0)),
    y=alt.Y("mean:Q", title="US Viewers (millions)"),
    color=alt.Color("era:N", scale=era_scale, legend=None),
)

q5_lines_points = base.mark_line(
    strokeWidth=2, point=alt.OverlayMarkDef(filled=True, size=35)
).encode(
    tooltip=[
        "era:N",
        "number_in_season:O",
        alt.Tooltip("mean:Q", format=".2f"),
        "count:Q",
    ]
)
q5_refs = (
    alt.Chart(era_avgs)
    .mark_rule(strokeDash=[4, 4], opacity=0.6)
    .encode(y="era_mean:Q", color=alt.Color("era:N", scale=era_scale, legend=None))
)
chart5 = (q5_lines_points + q5_refs).properties(
    height=300, title="Viewership by Episode Number (vs. Era Averages)"
)

# ==========================================
# Layout the Charts
# ==========================================

# Top Row
col1, col2 = st.columns(2, gap="medium")
with col1:
    st.altair_chart(chart1, width="stretch", theme=None)
with col2:
    st.altair_chart(chart2, width="stretch", theme=None)

# Bottom Row
col3, col4, col5 = st.columns([4, 3, 6], gap="medium")
with col3:
    st.altair_chart(chart3, width="stretch", theme=None)
with col4:
    st.altair_chart(chart4, width="stretch", theme=None)
with col5:
    st.altair_chart(chart5, width="stretch", theme=None)
