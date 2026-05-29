import base64
from pathlib import Path
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st

_DIR = Path(__file__).resolve().parent

# --- COLOR SETTINGS ---
# Okabe-Ito qualitative palette (orange + blue): colorblind-safe pair.
CHAR1_COLOR = "#E69F00"
CHAR2_COLOR = "#0072B2"
OTHER_COLOR = "#999999"


# --- HELPERS ---
def colored_bullet_label(text: str, color: str) -> str:
    """Return an HTML snippet for a sidebar label prefixed with a colored dot."""
    return (
        "<div style='display: flex; align-items: center; gap: 6px; "
        "margin-bottom: 6px; font-size: 14px;'>"
        f"<span style='width: 10px; height: 10px; border-radius: 50%; "
        f"background-color: {color}; display: inline-block;'></span>"
        f"{text}</div>"
    )


def apply_pending(state_key: str, options: list) -> None:
    """Carry a pending value from a chart click into the dropdown's session state.

    Called before the widget is rendered so it reflects the click. Also seeds a
    default the first time the widget runs, or after `options` no longer contains
    the previous value (e.g., after switching seasons).
    """
    pending = st.session_state.pop(f"pending_{state_key}", None)
    if pending is not None and pending in options:
        st.session_state[state_key] = pending
    if state_key not in st.session_state or st.session_state[state_key] not in options:
        st.session_state[state_key] = options[0]


def on_dropdown_change(last_seen_keys: list) -> None:
    """Mark the chart's persisted selections as acknowledged.

    When the user picks a value from the dropdown we want to ignore whatever the
    chart is still holding in its widget state. We can't clear the chart's
    selection (Streamlit doesn't expose a way), so we set a flag that
    `capture_chart_click` reads on the very next run: any chart selection
    reported during that run is treated as already-seen, even if its value
    differs from anything we've recorded. `last_seen_keys` is the list of
    `last_seen_*` keys that should be silenced for this dropdown change (e.g.
    a season change should also acknowledge the Q3 chart's episode selection,
    since that selection was meaningful for the previous season).
    """
    for last_seen_key in last_seen_keys:
        st.session_state[f"acknowledge_next_{last_seen_key}"] = True


def capture_chart_click(
    event, selection_name: str, field: str, current, target_state_key: str
) -> None:
    """If a chart click selected a new value, stash it for the next run and rerun.

    The click is read from `event.selection`. We write the result to
    `pending_<target_state_key>` so `apply_pending` can adopt it on the next run,
    before the dropdown widget is rendered.

    `st.altair_chart` persists its last selection across reruns, so on every run
    `event.selection` reports the same value the user clicked previously — even
    if they didn't interact with the chart this run. To distinguish a fresh
    click from a stale one we track the last selection we processed in
    `st.session_state[f"last_seen_{selection_name}"]`. Two safeguards:

    1. Only fire when the chart's reported value differs from `last_seen`.
       (We also skip when it matches `current`, so a click that re-selects the
       active dropdown value is a no-op.)
    2. The dropdown's `on_change` handler sets an "acknowledge_next" flag. On
       the rerun triggered by the dropdown, we silently absorb whatever the
       chart is holding into `last_seen` and skip firing — this prevents the
       chart's stale selection from snapping the dropdown back.
    """
    last_seen_key = f"last_seen_{selection_name}"
    ack_key = f"acknowledge_next_{last_seen_key}"
    try:
        points = event.selection.get(selection_name, [])  # type: ignore[union-attr]
        value = int(points[0][field]) if points else None
    except (AttributeError, KeyError, IndexError, TypeError, ValueError):
        value = None

    if st.session_state.pop(ack_key, False):
        # Dropdown was just changed; treat whatever the chart reports as seen.
        if value is not None:
            st.session_state[last_seen_key] = value
        return

    last_seen = st.session_state.get(last_seen_key)

    if value is not None and value != last_seen and value != current:
        st.session_state[last_seen_key] = value
        st.session_state[f"pending_{target_state_key}"] = value
        st.rerun()

    # Sync last_seen to the chart's reported value when it has one — so the
    # chart's stable selection is treated as acknowledged. Don't overwrite with
    # None: a transient empty event would otherwise turn the chart's still-
    # persisted selection into a "new" click on the next run.
    if value is not None:
        st.session_state[last_seen_key] = value


# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Character Speech Analysis",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS OVERRIDES ---
st.markdown(
    """
    <style>
        /* Reduce spacing in the main container */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
        }
        header[data-testid="stHeader"] {
            display: none;
        }
        /* Hide the sidebar collapse button so the controls are always visible */
        [data-testid="stSidebarCollapseButton"] {
            display: none;
        }
    </style>
""",
    unsafe_allow_html=True,
)


# --- DATA LOADING ---
@st.cache_data
def load_data():
    df_q1 = pd.read_csv(_DIR / "../data/clean_data/df_q1.csv")
    df_q2 = pd.read_csv(_DIR / "../data/clean_data/df_q2.csv")
    df_q3 = pd.read_csv(_DIR / "../data/clean_data/df_q3.csv")
    df_q4 = pd.read_csv(_DIR / "../data/clean_data/df_q4.csv")
    return df_q1, df_q2, df_q3, df_q4


df_q1, df_q2, df_q3, df_q4 = load_data()

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Dashboard Controls")

# Metric drives the bar/box chart values; characters_list reorders to match.
metric_label = st.sidebar.segmented_control(
    "Metric:",
    options=["Word Count", "Sentence Count"],
    default="Word Count",
    key="metric",
)
# Segmented control allows deselection; fall back to the default in that case.
if metric_label is None:
    metric_label = "Word Count"
metric_col = "word_count" if metric_label == "Word Count" else "sentence_count"

# Order characters by total count (descending) so dropdowns match the bar chart
characters_list = (
    df_q1.groupby("character_names")[metric_col]
    .sum()
    .sort_values(ascending=False)
    .index.tolist()
)
seasons_list = sorted(df_q4["season"].unique().tolist())

st.sidebar.markdown(
    colored_bullet_label("Character 1:", CHAR1_COLOR), unsafe_allow_html=True
)
char1 = st.sidebar.selectbox(
    "Character 1:",
    options=characters_list,
    index=0,
    key="char1",
    label_visibility="collapsed",
)
char2_options = [c for c in characters_list if c != char1]
st.sidebar.markdown(
    colored_bullet_label("Character 2:", CHAR2_COLOR), unsafe_allow_html=True
)
char2 = st.sidebar.selectbox(
    "Character 2:",
    options=char2_options,
    index=0,
    key="char2",
    label_visibility="collapsed",
)

# Q2 clicks update the season; apply any pending click before the widget renders.
# `on_change` acknowledges the chart's stale selection so it can't fire on the
# next run and revert the user's dropdown pick. Picking a new season also
# implicitly acknowledges the Q3 chart's persisted episode selection — that
# selection was meaningful for the previous season, not this one.
apply_pending("season", seasons_list)
season = st.sidebar.selectbox(
    "Season:",
    options=seasons_list,
    key="season",
    on_change=on_dropdown_change,
    args=(["last_seen_q2_season", "last_seen_q3_episode"],),
)

episodes_in_season = sorted(
    df_q4[df_q4["season"] == season]["number_in_season"].unique().tolist()
)

# Q3 clicks update the episode; apply any pending click before the widget renders.
apply_pending("episode", episodes_in_season)
episode = st.sidebar.selectbox(
    "Episode:",
    options=episodes_in_season,
    key="episode",
    on_change=on_dropdown_change,
    args=(["last_seen_q3_episode"],),
)


# --- HEADER SECTION ---
header_col1, header_col2, header_col3 = st.columns(
    [1, 6, 1], vertical_alignment="center"
)

with header_col1:
    try:
        with open(_DIR / "logo.png", "rb") as image_file:
            encoded_logo_img = base64.b64encode(image_file.read()).decode()
        img_html = f"""
<div style="white-space: nowrap;">
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
            <h3 style='margin-top: 0px; margin-bottom: 0px; padding-bottom: 0px; white-space: nowrap;'>The Simpsons: Character Dialogue Across Seasons 1-25</h3>
            <p style='margin-top: 2px; margin-bottom: 0px; font-size: 16px;'>Data: <a href="https://www.kaggle.com/datasets/prashant111/the-simpsons-dataset" target="_blank">The Simpsons Dataset (Kaggle)</a></p>
            <p style='margin-top: 2px; margin-bottom: 0px; font-size: 16px;'>By Benedikt Prisett & Stijn Diemel</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with header_col3:
    html_legend = f"""
    <div style="display: flex; flex-direction: column; align-items: flex-start; gap: 6px; padding: 5px 0;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="width: 12px; height: 12px; border-radius: 50%; background-color: {CHAR1_COLOR}; display: inline-block; flex-shrink: 0;"></span>
            <span style="font-size: 14px; white-space: nowrap; font-weight: 500;">{char1}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="width: 12px; height: 12px; border-radius: 50%; background-color: {CHAR2_COLOR}; display: inline-block; flex-shrink: 0;"></span>
            <span style="font-size: 14px; white-space: nowrap; font-weight: 500;">{char2}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="width: 12px; height: 12px; border-radius: 50%; background-color: {OTHER_COLOR}; display: inline-block; flex-shrink: 0;"></span>
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

all_chars = df_q1["character_names"].unique().tolist()
highlight_range = [
    CHAR1_COLOR if c == char1 else CHAR2_COLOR if c == char2 else OTHER_COLOR
    for c in all_chars
]

highlight_condition = alt.Color(
    "character_names:N",
    scale=alt.Scale(domain=all_chars, range=highlight_range),
    legend=None,
)


# --- CHART BUILDERS ---
# `characters_list` (defined in the sidebar block) is already sorted by total
# count for the selected metric, so the bar chart and boxplot stay aligned.
sorted_chars = characters_list

# --- Q1: Interactive Bar Chart ---
bar_chart_word = (
    alt.Chart(df_q1)
    .mark_bar()
    .encode(
        y=alt.Y("character_names:N", title="Character", sort=sorted_chars),
        x=alt.X(f"sum({metric_col}):Q", title=f"Total {metric_label}"),
        color=highlight_condition,
        tooltip=["character_names", f"sum({metric_col}):Q"],
    )
    .properties(height=350, title=f"Total {metric_label} per Character")
)

# --- Q1: Interactive Boxplot ---
boxplot_chart_word = (
    alt.Chart(df_q1)
    .mark_boxplot(size=15)
    .encode(
        y=alt.Y("character_names:N", title="Character", sort=sorted_chars),
        x=alt.X(f"{metric_col}:Q", title=f"{metric_label} per Episode"),
        color=highlight_condition,
    )
    .properties(height=350, title=f"Distribution of {metric_label} per Episode")
)

# --- Q2: Line Chart ---
df_q2_filtered = df_q2[df_q2["character_names"].isin([char1, char2])]

q2_season_select = alt.selection_point(
    name="q2_season", fields=["season"], on="click", clear="dblclick"
)

q2_base = alt.Chart(df_q2_filtered).encode(
    x=alt.X("season:O", title="Season", axis=alt.Axis(labelAngle=0)),
    y=alt.Y(f"{metric_col}:Q", title=f"Total {metric_label}"),
    color=alt.Color(
        "character_names:N", title="Character", scale=char_color_scale, legend=None
    ),
)

q2_visible = q2_base.mark_line(
    strokeWidth=2,
    point=alt.OverlayMarkDef(filled=True, size=35),
).encode(tooltip=["character_names", "season", metric_col])

# Light gray background rectangle marking the selected season
q2_selected_bg = (
    alt.Chart(pd.DataFrame({"season": [season]}))
    .mark_rect(color=OTHER_COLOR, opacity=0.15)
    .encode(x=alt.X("season:O"))
)

# Invisible larger hit area to make clicking the line easier
q2_hit_area = (
    q2_base.mark_point(size=600, opacity=0)
    .encode(tooltip=["character_names", "season", metric_col])
    .add_params(q2_season_select)
)

line_chart = (q2_visible + q2_selected_bg + q2_hit_area).properties(
    height=300, title=f"{metric_label} Over Seasons"
)

# --- Q3: Butterfly Chart per episode ---
df_q3_filtered = df_q3[
    (df_q3["season"] == season) & (df_q3["character_names"].isin([char1, char2]))
]

# Symmetric y-domain so both characters share the same visual scale
q3_max = df_q3_filtered[metric_col].max() if not df_q3_filtered.empty else 0

# Click selection: an episode click on Q3 drives Q4.
q3_episode_select = alt.selection_point(
    name="q3_episode", fields=["number_in_season"], on="click", clear="dblclick"
)

butterfly_chart_q3_bars = (
    alt.Chart(df_q3_filtered)
    .mark_bar()
    .encode(
        x=alt.X(
            "number_in_season:O", title="Episode Number", axis=alt.Axis(labelAngle=0)
        ),
        y=alt.Y(
            "signed_metric:Q",
            title=metric_label,
            axis=alt.Axis(labelExpr="abs(datum.value)"),
            scale=alt.Scale(domain=[-q3_max, q3_max]),
        ),
        color=alt.Color(
            "character_names:N", title="Character", scale=char_color_scale, legend=None
        ),
        tooltip=["character_names", "season", "number_in_season", metric_col],
    )
    .transform_calculate(
        signed_metric=f"datum.character_names == '{char2}' ? -datum.{metric_col} : datum.{metric_col}"
    )
    .add_params(q3_episode_select)
)

# Light gray background rectangle marking the selected episode.
# Layered after the bars so the bars' x-scale governs bandwidth and labels.
q3_selected_bg = (
    alt.Chart(pd.DataFrame({"number_in_season": [episode]}))
    .mark_rect(color=OTHER_COLOR, opacity=0.15)
    .encode(x=alt.X("number_in_season:O"))
)

butterfly_chart_q3 = (butterfly_chart_q3_bars + q3_selected_bg).properties(
    height=350, title=f"{metric_label} per Episode in Season {season}"
)

# --- Q4: Butterfly Chart per Minute ---
# df_q4 is already at (character, season, episode, minute) grain with zero-filled
# rows for minutes where a character didn't speak — so missing bars correctly
# show as empty ticks on the x-axis instead of dropping out of the ordinal scale.
#
# 5 episodes in the source Kaggle dataset have corrupted timestamps — every line
# in the episode shares one timestamp_in_ms value, so all dialogue collapses
# onto a single minute. We can't recover per-line timing, so we replace the Q4
# chart with a warning for these episodes.
BROKEN_TIMESTAMP_EPISODES = {
    (7, 10),  # The Simpsons 138th Episode Spectacular
    (7, 12),  # Team Homer
    (16, 6),  # Midnight Rx
    (23, 7),  # The Man in the Blue Flannel Pants
    (23, 19),  # A Totally Fun Thing That Bart Will Never Do Again
}
q4_has_broken_timestamps = (season, episode) in BROKEN_TIMESTAMP_EPISODES

df_q4_filtered = df_q4[
    (df_q4["season"] == season)
    & (df_q4["number_in_season"] == episode)
    & (df_q4["character_names"].isin([char1, char2]))
]

q4_max = df_q4_filtered[metric_col].max() if not df_q4_filtered.empty else 0

butterfly_chart_q4 = (
    alt.Chart(df_q4_filtered)
    .mark_bar()
    .encode(
        x=alt.X(
            "timestamp_in_min:O",
            title="Minute of Episode",
            axis=alt.Axis(labelAngle=0, labelOverlap=True),
        ),
        y=alt.Y(
            "signed_metric:Q",
            title=metric_label,
            axis=alt.Axis(labelExpr="abs(datum.value)"),
            scale=alt.Scale(domain=[-q4_max, q4_max]),
        ),
        color=alt.Color(
            "character_names:N", title="Character", scale=char_color_scale, legend=None
        ),
        tooltip=[
            "character_names",
            "season",
            "number_in_season",
            "timestamp_in_min",
            metric_col,
        ],
    )
    .transform_calculate(
        signed_metric=f"datum.character_names == '{char2}' ? -datum.{metric_col} : datum.{metric_col}"
    )
    .properties(
        height=350,
        title=f"{metric_label} per Minute in Season {season}, Episode {episode}",
    )
)

# --- LAYOUT ---

# Row 1 (2 Columns)
row1_col1, row1_col2 = st.columns(2, gap="medium")
with row1_col1:
    st.altair_chart(bar_chart_word, width="stretch", theme=None)
with row1_col2:
    st.altair_chart(boxplot_chart_word, width="stretch", theme=None)

# Row 2 (1 Full Width Column, smaller height)
q2_event = st.altair_chart(
    line_chart,
    width="stretch",
    theme=None,
    on_select="rerun",
    key="q2_chart",
)
capture_chart_click(q2_event, "q2_season", "season", season, "season")

# Row 3 (2 Columns)
row3_col1, row3_col2 = st.columns(2, gap="medium")
with row3_col1:
    q3_event = st.altair_chart(
        butterfly_chart_q3,
        width="stretch",
        theme=None,
        on_select="rerun",
        key="q3_chart",
    )
capture_chart_click(q3_event, "q3_episode", "number_in_season", episode, "episode")

with row3_col2:
    if q4_has_broken_timestamps:
        st.markdown(
            """
            <div style="height: 350px; display: flex; align-items: center;
                        justify-content: center; border: 1px dashed #999;
                        border-radius: 6px; padding: 20px; text-align: center;
                        color: #555;">
                <div>
                    <div style="font-size: 32px; margin-bottom: 8px;">⚠️</div>
                    <div style="font-size: 16px; font-weight: 500; margin-bottom: 6px;">
                        Per-minute breakdown unavailable
                    </div>
                    <div style="font-size: 13px; max-width: 420px; margin: 0 auto;">
                        The source dataset is missing per-line timestamps for this
                        episode, so dialogue cannot be distributed across the
                        episode's runtime. Pick another episode to see the
                        per-minute breakdown.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.altair_chart(butterfly_chart_q4, width="stretch", theme=None)
