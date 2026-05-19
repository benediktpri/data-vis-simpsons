import base64
from pathlib import Path
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st

_DIR = Path(__file__).resolve().parent

# --- COLOR SETTINGS ---
# Change these variables to update the colors for Character 1 and Character 2 throughout the app
CHAR1_COLOR = "#DDAA33"
CHAR2_COLOR = "#BB5566"

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Character Speech Analysis", layout="wide")

# --- CSS OVERRIDES ---
st.markdown(
    """
    <style>
        /* Reduce spacing in the main container */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# --- DATA LOADING ---
@st.cache_data
def load_data():
    df_q1 = pd.read_csv('../../data/clean_data/df_q1.csv')
    df_q2 = pd.read_csv('../../data/clean_data/df_q2.csv')
    df_q3 = pd.read_csv('../../data/clean_data/df_q3.csv')
    df_q4 = pd.read_csv('../../data/clean_data/df_q4.csv')
    return df_q1, df_q2, df_q3, df_q4

df_q1, df_q2, df_q3, df_q4 = load_data()

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Dashboard Controls")

# Streamlit-native Metric Selection
metric_label = st.sidebar.selectbox('Metric:', options=['Word Count', 'Sentence Count'], index=0)
metric_col = 'word_count' if metric_label == 'Word Count' else 'sentence_count'

characters_list = df_q4['character_names'].unique().tolist()
seasons_list = sorted(df_q4['season'].unique().tolist())

char1 = st.sidebar.selectbox('Character 1:', options=characters_list, index=0)
char2 = st.sidebar.selectbox('Character 2:', options=characters_list, index=1 if len(characters_list) > 1 else 0)

season = st.sidebar.selectbox('Season:', options=seasons_list, index=0)

episodes_in_season = sorted(df_q4[df_q4['season'] == season]['number_in_season'].unique().tolist())
episode = st.sidebar.selectbox('Episode:', options=episodes_in_season, index=0)


# --- HEADER SECTION ---
header_col1, header_col2, header_col3 = st.columns(
    [1, 6, 1], vertical_alignment="center"
)

with header_col1:
    try:
        with open(_DIR / "logo.png", "rb") as image_file:
            encoded_logo_img = base64.b64encode(image_file.read()).decode()
        img_html = f"""
            <div style="white-space: nowrap; margin-top: 15px;">
            <img src="data:image/png;base64,{encoded_logo_img}" style="width: 190px; height: 120px; object-fit: contain; image-rendering: high-quality; display: inline-block; vertical-align: middle; margin: 0; padding: 0;">
            </div>
            """
        st.markdown(img_html, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("logo.png not found")

with header_col2:
    st.markdown(
        """
        <div style='text-align: center;'>
            <h3 style='margin-top: 0px; margin-bottom: 0px; padding-bottom: 0px; white-space: nowrap;'>The Simpsons: Character Words and Sentences</h3>
            <p style='margin-top: 2px; margin-bottom: 0px; font-size: 16px;'>Data: <a href="https://www.kaggle.com/datasets/prashant111/the-simpsons-dataset" target="_blank">The Simpsons Dataset (Kaggle)</a></p>
            <p style='margin-top: 2px; margin-bottom: 0px; font-size: 16px;'>By Benedikt Prisett & Stijn Diemel</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with header_col3:
    html_legend = f"""
    <div style="display: flex; flex-direction: column; align-items: flex-start; gap: 6px; padding: 5px 0; margin-top: 15px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="width: 12px; height: 12px; border-radius: 50%; background-color: {CHAR1_COLOR}; display: inline-block; flex-shrink: 0;"></span>
            <span style="font-size: 14px; white-space: nowrap; font-weight: 500;">{char1}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="width: 12px; height: 12px; border-radius: 50%; background-color: {CHAR2_COLOR}; display: inline-block; flex-shrink: 0;"></span>
            <span style="font-size: 14px; white-space: nowrap; font-weight: 500;">{char2}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="width: 12px; height: 12px; border-radius: 50%; background-color: lightgray; display: inline-block; flex-shrink: 0;"></span>
            <span style="font-size: 14px; white-space: nowrap; font-weight: 500;">Other</span>
        </div>
    </div>
    """
    st.markdown(html_legend, unsafe_allow_html=True)

st.markdown(
    "<hr style='margin-top: 0px; margin-bottom: 20px;'>", unsafe_allow_html=True
)

# --- ALTAIR THEME ---
@alt.theme.register("dashboard", enable=True)
def dashboard_theme() -> Any:
    return {
        "config": {
            "title": {"fontSize": 16},
            "axis": {"titleFontSize": 14, "labelFontSize": 12},
        }
    }

# --- COLOR CONDITIONS ---
char_color_scale = alt.Scale(domain=[char1, char2], range=[CHAR1_COLOR, CHAR2_COLOR])

all_chars = df_q1['character_names'].unique().tolist()
highlight_range = [CHAR1_COLOR if c == char1 else CHAR2_COLOR if c == char2 else 'lightgray' for c in all_chars]

highlight_condition = alt.Color(
    'character_names:N',
    scale=alt.Scale(domain=all_chars, range=highlight_range),
    legend=None
)


# ==========================================
# Build the Charts
# ==========================================

# --- Explicitly calculate the sorting order based on the selected metric ---
# This guarantees the Bar Chart and Boxplot are sorted identically
sorted_chars = df_q1.groupby('character_names')[metric_col].sum().sort_values(ascending=False).index.tolist()

# --- Q1: Interactive Bar Chart ---
bar_chart_word = alt.Chart(df_q1).mark_bar().encode(
    y=alt.Y('character_names:N',
            title='Character',
            sort=sorted_chars),
    x=alt.X(f'sum({metric_col}):Q', title='Total Count'),
    color=highlight_condition,
    tooltip=['character_names', f'sum({metric_col}):Q']
).properties(
    height=350,
    title=f"Total {metric_label} per Character"
)

# --- Q1: Interactive Boxplot ---
boxplot_chart_word = alt.Chart(df_q1).mark_boxplot(size=15).encode(
    y=alt.Y('character_names:N',
            title='Character',
            sort=sorted_chars),
    x=alt.X(f'{metric_col}:Q', title='Count in an Episode'),
    color=highlight_condition
).properties(
    height=350,
    title=f"Distribution of {metric_label} per Episode"
)

# --- Q2: Line Chart ---
df_q2_filtered = df_q2[df_q2['character_names'].isin([char1, char2])]
line_chart = alt.Chart(df_q2_filtered).mark_line(
    point=True,
    size=3
).encode(
    x=alt.X('season:O', title='Season'),
    y=alt.Y('word_count:Q', title='Total Word Count'),
    color=alt.Color('character_names:N', title='Character', scale=char_color_scale, legend=None),
    tooltip=['character_names', 'season', 'word_count']
).properties(height=300, title='Word Count Over Seasons') # Height reduced to 250px for a smaller second row

# --- Q3: Bar Chart per Episode ---
df_q3_filtered = df_q3[(df_q3['season'] == season) & (df_q3['character_names'].isin([char1, char2]))]
bar_chart_q3 = alt.Chart(df_q3_filtered).mark_bar().encode(
    x=alt.X('number_in_season:O', title='Episode Number', axis=alt.Axis(labelAngle=0)),
    xOffset='character_names:N',
    y=alt.Y('word_count:Q', title='Total Word Count'),
    color=alt.Color('character_names:N', title='Character', scale=char_color_scale, legend=None),
    tooltip=['character_names', 'season', 'number_in_season', 'word_count']
).properties(height=350, title=f'Word Count per Episode (S{season})')

# --- Q4: Bar Chart per Minute ---
df_q4_filtered = df_q4[(df_q4['season'] == season) &
                       (df_q4['number_in_season'] == episode) &
                       (df_q4['character_names'].isin([char1, char2]))]
bar_chart_q4 = alt.Chart(df_q4_filtered).mark_bar().encode(
    x=alt.X('timestamp_in_min:O', title='Minute of Episode', axis=alt.Axis(labelAngle=-45, labelOverlap=True)),
    xOffset='character_names:N',
    y=alt.Y('word_count:Q', title='Total Word Count'),
    color=alt.Color('character_names:N', title='Character', scale=char_color_scale, legend=None),
    tooltip=['character_names', 'season', 'number_in_season', 'timestamp_in_min', 'word_count']
).properties(height=350, title=f'Word Count per Min (S{season}, E{episode})')


# ==========================================
# Layout the Charts (Exactly 3 Rows)
# ==========================================

# Row 1 (2 Columns)
row1_col1, row1_col2 = st.columns(2, gap="medium")
with row1_col1:
    st.altair_chart(bar_chart_word, width="stretch", theme=None)
with row1_col2:
    st.altair_chart(boxplot_chart_word, width="stretch", theme=None)

# Row 2 (1 Full Width Column, smaller height)
st.altair_chart(line_chart, width="stretch", theme=None)

# Row 3 (2 Columns)
row3_col1, row3_col2 = st.columns(2, gap="medium")
with row3_col1:
    st.altair_chart(bar_chart_q3, width="stretch", theme=None)
with row3_col2:
    st.altair_chart(bar_chart_q4, width="stretch", theme=None)