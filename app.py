"""
When Should I Use Electricity?
Simple Streamlit app for the BDS "From Data to App" assignment.

Run with:
    python -m streamlit run app.py
"""

from datetime import date

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


# -------------------------------------------------------------------
# PAGE SETUP
# -------------------------------------------------------------------
st.set_page_config(
    page_title="When Should I Use Electricity?",
    page_icon="⚡",
    layout="wide",
)

API_URL = "https://api.energy-charts.info/price"

# Public day-ahead bidding zones used in this app.
# Keeping prices in EUR/MWh gives every market one comparable unit.
MARKETS = {
    "DK1": {
        "label": "Denmark — DK1 (West)",
        "timezone": "Europe/Copenhagen",
    },
    "DK2": {
        "label": "Denmark — DK2 (East)",
        "timezone": "Europe/Copenhagen",
    },
    "DE-LU": {
        "label": "Germany & Luxembourg",
        "timezone": "Europe/Berlin",
    },
    "FR": {
        "label": "France",
        "timezone": "Europe/Paris",
    },
    "NL": {
        "label": "Netherlands",
        "timezone": "Europe/Amsterdam",
    },
    "BE": {
        "label": "Belgium",
        "timezone": "Europe/Brussels",
    },
    "AT": {
        "label": "Austria",
        "timezone": "Europe/Vienna",
    },
    "CH": {
        "label": "Switzerland",
        "timezone": "Europe/Zurich",
    },
    "CZ": {
        "label": "Czechia",
        "timezone": "Europe/Prague",
    },
    "HU": {
        "label": "Hungary",
        "timezone": "Europe/Budapest",
    },
    "IT-North": {
        "label": "Northern Italy",
        "timezone": "Europe/Rome",
    },
    "NO2": {
        "label": "Southern Norway — NO2",
        "timezone": "Europe/Oslo",
    },
    "PL": {
        "label": "Poland",
        "timezone": "Europe/Warsaw",
    },
    "SE4": {
        "label": "Southern Sweden — SE4",
        "timezone": "Europe/Stockholm",
    },
    "SI": {
        "label": "Slovenia",
        "timezone": "Europe/Ljubljana",
    },
}

# These are intentionally simple example presets.
# The user can always change the number manually.
APPLIANCE_PRESETS = {
    "EV charging": 20.0,
    "Dishwasher": 1.2,
    "Washing machine": 0.8,
    "Tumble dryer": 2.5,
    "Custom": 5.0,
}


# -------------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------------
def euro(value):
    """Readable euro formatting, including very small or negative values."""
    if abs(value) < 0.01:
        return f"€{value:.3f}"
    return f"€{value:.2f}"


def time_window(timestamp, minutes):
    """Format a pricing interval as HH:MM–HH:MM."""
    end_timestamp = timestamp + pd.Timedelta(minutes=minutes)
    return (
        f"{timestamp:%H:%M}–"
        f"{end_timestamp:%H:%M}"
    )


# -------------------------------------------------------------------
# API
# -------------------------------------------------------------------
@st.cache_data(ttl=900)
def load_today(zone, local_day):
    """
    Load the full day-ahead wholesale price curve for one bidding zone.

    The API's date-only start/end values represent the full local day.
    """

    params = {
        "bzn": zone,
        "start": local_day.isoformat(),
        "end": local_day.isoformat(),
    }

    response = requests.get(
        API_URL,
        params=params,
        timeout=12,
    )

    if response.status_code == 429:
        retry_after = response.headers.get(
            "Retry-After",
            "a short while",
        )
        raise RuntimeError(
            "The public Energy-Charts API is temporarily rate-limiting "
            f"requests. Please wait {retry_after} seconds and try again."
        )

    response.raise_for_status()

    payload = response.json()

    timestamps = payload.get("unix_seconds")
    prices = payload.get("price")
    license_info = payload.get("license_info", "")
    unit = payload.get("unit", "EUR/MWh")

    if timestamps is None or prices is None:
        raise RuntimeError(
            "The API response did not contain the expected electricity prices."
        )

    if len(timestamps) != len(prices):
        raise RuntimeError(
            "The API returned an inconsistent number of timestamps and prices."
        )

    # Keep the public app on data explicitly marked for publication.
    if license_info and "CC BY 4.0" not in license_info:
        raise RuntimeError(
            "This market's price data is not marked CC BY 4.0 "
            "for public display."
        )

    df = pd.DataFrame(
        {
            "timestamp_utc": pd.to_datetime(
                timestamps,
                unit="s",
                utc=True,
            ),
            "price_eur_mwh": pd.to_numeric(
                prices,
                errors="coerce",
            ),
        }
    ).dropna()

    if df.empty:
        return df, unit, license_info

    timezone = MARKETS[zone]["timezone"]

    df["timestamp"] = (
        df["timestamp_utc"]
        .dt.tz_convert(timezone)
    )

    df["local_date"] = (
        df["timestamp"].dt.date
    )

    # The date filter also protects against timezone edge cases.
    df = df[
        df["local_date"] == local_day
    ].copy()

    df["price_eur_kwh"] = (
        df["price_eur_mwh"] / 1000
    )

    return (
        df.sort_values("timestamp"),
        unit,
        license_info,
    )


# -------------------------------------------------------------------
# HEADER / STORY
# -------------------------------------------------------------------
st.title("⚡ When should I use electricity?")

st.markdown(
    """
**For households and EV owners**

### Should I use electricity now, or wait?

Choose your electricity market and how much energy you expect to use.
The app uses today's **day-ahead wholesale electricity prices** to estimate
the wholesale energy cost **right now** and compare it with the cheapest
remaining pricing interval today.
"""
)


# -------------------------------------------------------------------
# CONTROLS
# -------------------------------------------------------------------
with st.sidebar:

    st.header("Your electricity use")

    selected_zone = st.selectbox(
        "Electricity market",
        options=list(MARKETS.keys()),
        index=0,
        format_func=lambda zone:
        MARKETS[zone]["label"],
    )

    use_case = st.selectbox(
        "What do you want to run?",
        options=list(APPLIANCE_PRESETS.keys()),
        index=0,
    )

    suggested_kwh = (
        APPLIANCE_PRESETS[use_case]
    )

    energy_kwh = st.number_input(
        "Energy you expect to use (kWh)",
        min_value=0.1,
        max_value=100.0,
        value=float(suggested_kwh),
        step=0.1,
        key=f"energy_{use_case}",
        help=(
            "The appliance presets are examples only. "
            "Replace the number with your own expected electricity use."
        ),
    )

    st.caption(
        "Prices are shown in EUR because Energy-Charts supplies "
        "day-ahead prices in EUR/MWh."
    )


# -------------------------------------------------------------------
# CURRENT LOCAL DATE / TIME
# -------------------------------------------------------------------
timezone = (
    MARKETS[selected_zone]["timezone"]
)

now_local = pd.Timestamp.now(
    tz=timezone
)

today_local = now_local.date()


# -------------------------------------------------------------------
# LOAD TODAY'S DATA
# -------------------------------------------------------------------
try:

    with st.spinner(
        "Loading today's electricity prices..."
    ):

        today_df, unit, license_info = (
            load_today(
                selected_zone,
                today_local,
            )
        )

except requests.exceptions.Timeout:

    st.error(
        "Energy-Charts took too long to respond. "
        "Please try again."
    )
    st.stop()

except requests.exceptions.RequestException as error:

    st.error(
        "The Energy-Charts API is temporarily unavailable."
    )
    st.caption(
        f"Technical detail: {error}"
    )
    st.stop()

except RuntimeError as error:

    st.error(
        str(error)
    )
    st.stop()


if today_df.empty:

    st.info(
        "No price data is available for this market today."
    )
    st.stop()


# -------------------------------------------------------------------
# IDENTIFY CURRENT AND REMAINING INTERVALS
# -------------------------------------------------------------------
# Estimate the interval length from the actual API timestamps.
time_differences = (
    today_df["timestamp"]
    .sort_values()
    .diff()
    .dropna()
    .dt.total_seconds()
    / 60
)

if time_differences.empty:
    interval_minutes = 60
else:
    interval_minutes = int(
        round(
            time_differences.median()
        )
    )

# API timestamps mark the beginning of their pricing interval.
started_intervals = today_df[
    today_df["timestamp"] <= now_local
]

if started_intervals.empty:

    # This is unusual, but lets the app fail gracefully before the
    # first pricing timestamp of the day.
    current_row = (
        today_df.iloc[0]
    )

else:

    current_row = (
        started_intervals.iloc[-1]
    )

current_start = (
    current_row["timestamp"]
)

current_price = float(
    current_row["price_eur_mwh"]
)

# Include the current interval among the remaining choices.
remaining_df = today_df[
    today_df["timestamp"] >= current_start
].copy()

if remaining_df.empty:
    remaining_df = today_df.tail(1).copy()

cheapest_index = (
    remaining_df["price_eur_mwh"]
    .idxmin()
)

cheapest_row = (
    remaining_df.loc[
        cheapest_index
    ]
)

cheapest_start = (
    cheapest_row["timestamp"]
)

cheapest_price = float(
    cheapest_row["price_eur_mwh"]
)


# -------------------------------------------------------------------
# COST CALCULATIONS
# -------------------------------------------------------------------
current_cost = (
    energy_kwh
    * current_price
    / 1000
)

cheapest_cost = (
    energy_kwh
    * cheapest_price
    / 1000
)

potential_saving = (
    current_cost
    - cheapest_cost
)

current_price_kwh = (
    current_price / 1000
)

cheapest_price_kwh = (
    cheapest_price / 1000
)


# -------------------------------------------------------------------
# DECISION SUMMARY
# -------------------------------------------------------------------
st.caption(
    f"{MARKETS[selected_zone]['label']} · "
    f"{now_local:%A, %d %B %Y · %H:%M} local time"
)

m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "Wholesale price now",
    f"€{current_price_kwh:.3f}/kWh",
    help=(
        f"Equivalent to {current_price:.1f} EUR/MWh."
    ),
)

m2.metric(
    f"Cost now for {energy_kwh:g} kWh",
    euro(current_cost),
    help=(
        "Wholesale electricity component only."
    ),
)

m3.metric(
    "Cheapest remaining time",
    time_window(
        cheapest_start,
        interval_minutes,
    ),
    help=(
        f"{cheapest_price:.1f} EUR/MWh "
        f"({cheapest_price_kwh:.3f} EUR/kWh)."
    ),
)

m4.metric(
    "Potential saving by waiting",
    euro(
        max(
            potential_saving,
            0,
        )
    ),
    help=(
        "Difference in the wholesale energy component "
        "for the selected kWh."
    ),
)


# A simple everyday interpretation.
if cheapest_start == current_start:

    st.success(
        "⚡ **Now is the cheapest remaining pricing interval today** "
        "based on the wholesale day-ahead price."
    )

else:

    lower_quartile = (
        remaining_df["price_eur_mwh"]
        .quantile(0.25)
    )

    if current_price <= lower_quartile:

        st.success(
            "⚡ **Now is already one of the cheaper remaining periods today.** "
            f"The absolute cheapest remaining interval starts at "
            f"**{cheapest_start:%H:%M}**."
        )

    else:

        st.info(
            "🕒 **If your electricity use is flexible, waiting could be cheaper.** "
            f"The cheapest remaining interval starts at "
            f"**{cheapest_start:%H:%M}**, where the wholesale component "
            f"would cost about **{euro(cheapest_cost)}** for "
            f"**{energy_kwh:g} kWh**, compared with "
            f"**{euro(current_cost)}** now."
        )


# -------------------------------------------------------------------
# ONE CLEAR VISUALIZATION
# -------------------------------------------------------------------
st.subheader("Today's electricity price")

plot_df = today_df.copy()

plot_df["label"] = (
    plot_df["timestamp"]
    .dt.strftime("%H:%M")
)

fig = px.line(
    plot_df,
    x="timestamp",
    y="price_eur_mwh",
    markers=True,
    labels={
        "timestamp": "Time",
        "price_eur_mwh":
        "Wholesale day-ahead price (EUR/MWh)",
    },
)

# Mark the current pricing interval.
fig.add_scatter(
    x=[current_start],
    y=[current_price],
    mode="markers+text",
    name="Now",
    text=["Now"],
    textposition="top center",
)

# Mark the cheapest remaining interval.
if cheapest_start != current_start:

    fig.add_scatter(
        x=[cheapest_start],
        y=[cheapest_price],
        mode="markers+text",
        name="Cheapest remaining",
        text=["Cheapest"],
        textposition="bottom center",
    )

fig.update_xaxes(
    tickformat="%H:%M",
)

fig.update_layout(
    height=480,
    margin=dict(
        t=20,
        b=0,
    ),
    legend_title_text="",
)

st.plotly_chart(
    fig,
    use_container_width=True,
)


# -------------------------------------------------------------------
# OPTIONAL DETAIL
# -------------------------------------------------------------------
with st.expander(
    "See today's price data"
):

    detail_df = today_df[
        [
            "timestamp",
            "price_eur_mwh",
            "price_eur_kwh",
        ]
    ].copy()

    detail_df["timestamp"] = (
        detail_df["timestamp"]
        .dt.strftime(
            "%Y-%m-%d %H:%M"
        )
    )

    detail_df[
        "price_eur_mwh"
    ] = (
        detail_df[
            "price_eur_mwh"
        ].round(2)
    )

    detail_df[
        "price_eur_kwh"
    ] = (
        detail_df[
            "price_eur_kwh"
        ].round(4)
    )

    st.dataframe(
        detail_df.rename(
            columns={
                "timestamp":
                "Local time",
                "price_eur_mwh":
                "EUR/MWh",
                "price_eur_kwh":
                "EUR/kWh",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )

st.download_button(
    "Download today's prices (CSV)",
    data=today_df.to_csv(
        index=False
    ).encode("utf-8"),
    file_name=(
        f"electricity_prices_"
        f"{selected_zone}_"
        f"{today_local}.csv"
    ),
    mime="text/csv",
)


# -------------------------------------------------------------------
# LIMITATION / SOURCE
# -------------------------------------------------------------------
st.divider()

st.caption(
    "Data source: Energy-Charts.info day-ahead electricity prices. "
    "Prices are displayed in EUR/MWh and converted to EUR/kWh for the "
    "household cost estimate."
)
st.caption(
    "Limitation: costs use wholesale prices only and exclude taxes, grid tariffs and supplier charges."
)

st.caption("Data: Energy-Charts.info · CC BY 4.0")
