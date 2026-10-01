import time

import pandas as pd
import requests
import streamlit as st


API_BASE_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="StreamSight",
    page_icon="📊",
    layout="wide",
)


def get_json(endpoint: str):
    response = requests.get(
        f"{API_BASE_URL}{endpoint}",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


# -------------------------------------------------
# PAGE HEADER
# -------------------------------------------------

st.title("📊 StreamSight")

st.subheader(
    "Real-Time AI Operations Dashboard"
)

st.caption(
    "Streaming order analytics powered by "
    "Kafka, PostgreSQL, FastAPI, anomaly detection, "
    "and local AI with Ollama."
)


# -------------------------------------------------
# LOAD LIVE DASHBOARD DATA
# -------------------------------------------------

try:
    metrics = get_json(
        "/metrics/summary"
    )

    orders = get_json(
        "/orders/recent?limit=20"
    )

    alerts = get_json(
        "/alerts/recent?limit=20"
    )

except requests.RequestException as exc:

    st.error(
        f"Could not connect to StreamSight API: {exc}"
    )

    st.stop()


# -------------------------------------------------
# KPI SECTION
# -------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Orders",
    f"{metrics['total_orders']:,}",
)

col2.metric(
    "Total Revenue",
    f"${metrics['total_revenue']:,.2f}",
)

col3.metric(
    "Average Order Value",
    f"${metrics['average_order_value']:,.2f}",
)

col4.metric(
    "Total Alerts",
    f"{metrics['total_alerts']:,}",
)


st.divider()


# -------------------------------------------------
# AI OPERATIONAL INSIGHT
# -------------------------------------------------

st.subheader(
    "AI Operational Insight"
)

if "ai_insight" not in st.session_state:

    try:
        ai_response = get_json(
            "/ai/insight"
        )

        st.session_state.ai_insight = (
            ai_response["insight"]
        )

    except requests.RequestException as exc:

        st.session_state.ai_insight = (
            "AI insight is currently unavailable. "
            f"API error: {exc}"
        )


if st.button(
    "Refresh AI Insight"
):

    with st.spinner(
        "Generating new AI operational insight..."
    ):

        try:
            ai_response = get_json(
                "/ai/insight"
            )

            st.session_state.ai_insight = (
                ai_response["insight"]
            )

        except requests.RequestException as exc:

            st.error(
                f"Could not refresh AI insight: {exc}"
            )


st.markdown(
    st.session_state.ai_insight
)


st.divider()


# -------------------------------------------------
# RECENT ORDERS
# -------------------------------------------------

st.subheader(
    "Recent Orders"
)

orders_df = pd.DataFrame(
    orders
)

if not orders_df.empty:

    st.dataframe(
        orders_df,
        width="stretch",
        hide_index=True,
    )

else:

    st.info(
        "No order data available yet."
    )


st.divider()


# -------------------------------------------------
# ORDER STATUS BREAKDOWN
# -------------------------------------------------

st.subheader(
    "Order Status Breakdown"
)

if not orders_df.empty:

    status_counts = (
        orders_df["status"]
        .value_counts()
        .reset_index()
    )

    status_counts.columns = [
        "status",
        "count",
    ]

    st.bar_chart(
        status_counts,
        x="status",
        y="count",
    )

else:

    st.info(
        "No status data available."
    )


st.divider()


# -------------------------------------------------
# REVENUE BY PRODUCT
# -------------------------------------------------

st.subheader(
    "Revenue by Product"
)

if not orders_df.empty:

    product_revenue = (
        orders_df.groupby(
            "product",
            as_index=False,
        )["order_value"]
        .sum()
        .sort_values(
            "order_value",
            ascending=False,
        )
    )

    st.bar_chart(
        product_revenue,
        x="product",
        y="order_value",
    )

else:

    st.info(
        "No product revenue data available."
    )


st.divider()


# -------------------------------------------------
# RECENT ANOMALY ALERTS
# -------------------------------------------------

st.subheader(
    "Recent Anomaly Alerts"
)

alerts_df = pd.DataFrame(
    alerts
)

if not alerts_df.empty:

    st.dataframe(
        alerts_df,
        width="stretch",
        hide_index=True,
    )

else:

    st.success(
        "No anomaly alerts detected."
    )


# -------------------------------------------------
# AUTO REFRESH
# -------------------------------------------------

time.sleep(5)

st.rerun()