import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64
from pathlib import Path

# ==================================================
# Page Setup
# ==================================================
st.set_page_config(layout="wide")

# Resolve bundled files relative to this script so deployment does not depend
# on the process working directory.
APP_DIR = Path(__file__).resolve().parent
DATA_FILE = APP_DIR / "2027 IFP Projected Rate Changes.xlsx"
LOGO_FILE = APP_DIR / "zizzlhealth_logo.png"

# ---------------------------------------
# Branding
# ---------------------------------------
st.markdown(
    """
    <style>

    .stApp {
        background-color: #FFFFFF;
    }

    h1, h2, h3, h4 {
        color: #000080 !important;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        border-radius: 10px;
        padding: 10px;
    }

    [data-testid="stMetricLabel"] {
        color: #0b89f7 !important;
        font-weight: 1000;
    }

    [data-testid="stMetricValue"] {
        color: #0b89f7 !important;
        font-weight: 700;
    }

    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    h3 {
        color: #0b89f7 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>

    h1 {
        color: #000080 !important;
    }

    h2 {
        color: #000080 !important;
    }

    h3 {
        color: #0b89f7 !important;
    }

    h4 {
        color: #0b89f7 !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("""
<style>

/* KPI title */
[data-testid="stMetricLabel"] p {
    font-size: 22px !important;
    font-weight: 700 !important;
}

/* KPI value */
[data-testid="stMetricValue"] {
    font-size: 34px !important;
    color: #0b89f7 !important;
}

</style>
""", unsafe_allow_html=True)


# ---------------------------------------
# Load Data
# ---------------------------------------
df = pd.read_excel(
    DATA_FILE,
    sheet_name="2027"
)

state_data = (
    df.groupby("State")["Projected Average State Increase"]
    .first()
    .dropna()
    .mul(100)
    .round(1)
    .reset_index()
)

rate_lookup = dict(
    zip(
        state_data["State"],
        state_data["Projected Average State Increase"]
    )
)

# ---------------------------------------
# State Tile Locations
# ---------------------------------------
positions = {
    "AK": (0, 5),
    "WA": (0, 0),
    "OR": (0, 1),
    "CA": (0, 2),
    "ID": (1, 1),
    "NV": (1, 2),
    "AZ": (1, 3),
    "MT": (2, 0),
    "WY": (2, 1),
    "UT": (2, 2),
    "NM": (2, 3),
    "ND": (3, 0),
    "SD": (3, 1),
    "CO": (3, 2),
    "OK": (4, 3),
    "NE": (4, 1),
    "KS": (4, 2),
    "TX": (4, 4),
    "MN": (5, 0),
    "IA": (5, 1),
    "MO": (5, 2),
    "AR": (5, 3),
    "LA": (5, 4),
    "WI": (6, 0),
    "IL": (6, 1),
    "MS": (6, 4),
    "MI": (7, 0),
    "IN": (7, 1),
    "KY": (7, 2),
    "TN": (7, 3),
    "AL": (7, 4),
    "OH": (8, 1),
    "WV": (8, 2),
    "GA": (8, 4),
    "PA": (9, 1),
    "VA": (9, 2),
    "NC": (9, 3),
    "SC": (9, 4),
    "NY": (10, 1),
    "MD": (10, 2),
    "DC": (10, 3),
    "DE": (11, 3),
    "VT": (11, 0),
    "NJ": (11, 2),
    "NH": (12, 0),
    "MA": (12, 1),
    "CT": (12, 2),
    "RI": (12, 3),
    "ME": (13, 0),
    "FL": (9, 5),
    "HI": (1, 5)
}

# ---------------------------------------
# KPI Calculations
# ---------------------------------------
filed_rates = state_data["Projected Average State Increase"]

avg_rate = filed_rates.mean()
max_rate = filed_rates.max()
min_rate = filed_rates.min()

top_5 = (
    state_data.sort_values(
        "Projected Average State Increase",
        ascending=False
    )
    .head(5)
)

bottom_5 = (
    state_data.sort_values(
        "Projected Average State Increase",
        ascending=True
    )
    .head(5)
)

# Highest state
highest_state = state_data.loc[
    state_data["Projected Average State Increase"].idxmax()
]

# Lowest state
lowest_state = state_data.loc[
    state_data["Projected Average State Increase"].idxmin()
]

# ---------------------------------------
# 2026 National Average
# ---------------------------------------
df_2026 = pd.read_excel(
    DATA_FILE,
    sheet_name="2026"
)

national_avg_2026 = (
    df_2026["Projected Average State Increase"]
    .dropna()
    .astype(float)
    .mean()
    * 100
)

# ---------------------------------------
# 2026 vs 2027 State Comparison
# ---------------------------------------

state_data_2026 = (
    df_2026.groupby("State")["Projected Average State Increase"]
    .first()
    .dropna()
    .mul(100)
    .round(1)
    .reset_index()
)

comparison = (
    state_data.rename(
        columns={
            "Projected Average State Increase": "2027 Rate"
        }
    )
    .merge(
        state_data_2026.rename(
            columns={
                "Projected Average State Increase": "2026 Rate"
            }
        ),
        on="State",
        how="inner"
    )
)

lower_states = comparison[
    comparison["2027 Rate"] < comparison["2026 Rate"]
].copy()

lower_states["Change"] = (
    lower_states["2027 Rate"]
    - lower_states["2026 Rate"]
)

lower_count = len(lower_states)

# ---------------------------------------
# Build Plot Data
# ---------------------------------------
x = []
y = []
colors = []
hover_text = []
tile_text = []
text_colors = []

for state, (px, py) in positions.items():

    value = rate_lookup.get(state)

    x.append(px * 1.15)
    y.append(-py)

    if value is None or pd.isna(value):

        colors.append("#A9A9A9")
        text_colors.append("black")

        hover_text.append(
            f"{state}<br>Not Filed"
        )

        tile_text.append(
            f"{state}<br>Not Filed"
        )

    else:

        hover_text.append(
            f"{state}<br>{value:.1f}%"
        )

        tile_text.append(
            f"{state}<br>{value:.1f}%"
        )

        if value < 15:
            colors.append("#0A0A8C")
            text_colors.append("white")
        elif value >= 25:
            colors.append("#FF8C00")
            text_colors.append("black")
        else:
            colors.append("#FFC60B")
            text_colors.append("black")


# ---------------------------------------
# Create Map Figure
# ---------------------------------------
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=x,
        y=y,
        mode="markers+text",
        marker=dict(
            size=55,
            color=colors,
            symbol="square"
        ),
        text=tile_text,
        textposition="middle center",
        textfont=dict(
            color=text_colors,
            size=15
        ),
        hovertext=hover_text,
        hoverinfo="text"
    )
)

fig.update_xaxes(
    visible=False,
    range=[-1, 18],
    fixedrange=True
)

fig.update_yaxes(
    visible=False,
    range=[-6, 0.5],
    fixedrange=True,
    scaleanchor="x"
)

fig.update_layout(
    template="plotly_white",
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    height=500,    # was 500
    margin=dict(
        l=0,
        r=0,
        t=10,
        b=0       # increase bottom margin
    )
)

with LOGO_FILE.open("rb") as f:
    encoded_logo = base64.b64encode(f.read()).decode()

top_left, top_right = st.columns([5, 1])

with top_right:
    st.image(str(LOGO_FILE), width=600)


# ---------------------------------------
# Dashboard Layout
# ---------------------------------------

#----------------------------------------
#Title
st.title("2027 Individual Market Projected Average Rate Increases")
#----------------------------------------

# ---------------------------------------
# Top KPI Row
# ---------------------------------------
kpi1, kpi2, kpi3, kpi4, spacer = st.columns(
    [2, 2, 2, 2, 2]
)

with kpi1:
    st.markdown(
            f"""
            <div style="
                background-color:white;
                padding:7px;
                border-radius:10px;
            ">
                <div style="
                    color:#0b89f7;
                    font-size:22px;
                    font-weight:700;
                ">
                    2027 National Average
                </div>
                <div style="
                    color:#2e8b57;
                    font-size:34px;
                    font-weight:700;
                    marigin-top:0px;
                    marigin-bottom:0px;
                    line-height:1.2;
                ">
                    {avg_rate:.1f}%
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

with kpi2:
    st.markdown(
        f"""
        <div style="
            background-color:white;
            padding:7px;
            border-radius:10px;
        ">
            <div style="
                color:#0b89f7;
                font-size:22px;
                font-weight:700;
            ">
                2026 National Average
            </div>
            <div style="
                color:#ff8c00;
                font-size:34px;
                font-weight:700;
                marigin-top:0px;
                marigin-bottom:0px;
                line-height:1.2;
            ">
                {national_avg_2026:.1f}%
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with kpi3:
    st.metric(
        "Highest Increase",
        f"{highest_state['State']} | {highest_state['Projected Average State Increase']:.1f}%"
    )

with kpi4:
    st.metric(
        "Lowest Increase",
        f"{lowest_state['State']} | {lowest_state['Projected Average State Increase']:.1f}%"
    )

col_map, col_kpi = st.columns([3, 1])

col_map, col_kpi = st.columns([4, 1])

with col_map:

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )

    top_col, bottom_col = st.columns(2)

    with top_col:

        st.subheader("Top 5 Average Increases")

        st.dataframe(
            top_5.rename(
                columns={
                    "Projected Average State Increase": "Increase %"
                }
            ),
            hide_index=True,
            use_container_width=True
        )

    with bottom_col:

        st.subheader("Lowest 5 Average Increases")

        st.dataframe(
            bottom_5.rename(
                columns={
                    "Projected Average State Increase": "Increase %"
                }
            ),
            hide_index=True,
            use_container_width=True
        )




with col_kpi:

    st.markdown(
        """
        <div style="margin-top:-150px;">
            <h3 style="color:#0b89f7;">
                States with Projected Lower Rates than 2026
            </h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.dataframe(
        lower_states[
            ["State", "2026 Rate", "2027 Rate", "Change"]
        ].sort_values("Change"),
        hide_index=True,
        use_container_width=True
    )
