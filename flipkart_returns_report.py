import streamlit as st
import pandas as pd
import plotly.express as px

st.title("↩️ Flipkart Return Report Dashboard")

uploaded_file = st.file_uploader("Upload Flipkart Return Report (.xlsx or .csv)", type=["xlsx", "csv"])

if uploaded_file:
    # Load file
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith(".xlsx") else pd.read_csv(uploaded_file)

    # Convert relevant dates
    date_columns = [
        "return_requested_date", "return_approval_date", "return_completion_date",
        "return_complete_by_date", "tech_visit_by_date", "tech_visit_completion_datetime",
        "return_cancellation_date"
    ]
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Fill missing titles
    if "product_title" in df.columns:
        df["product_title"] = df["product_title"].fillna("Unknown Product")

    # Metrics
    total_returns = df["return_id"].nunique()
    cancelled_returns = df[df["return_status"].astype(str).str.lower() == "cancelled"].shape[0]
    completed_returns = df[df["return_status"].astype(str).str.lower() == "completed"].shape[0]
    total_quantity = df["quantity"].sum() if "quantity" in df.columns else 0

    tech_breaches = df["tech_visit_completion_breach"].astype(str).str.lower().eq("yes").sum() if "tech_visit_completion_breach" in df.columns else 0
    return_breaches = df["return_completion_breach"].astype(str).str.lower().eq("yes").sum() if "return_completion_breach" in df.columns else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("↩️ Total Returns", f"{total_returns}")
    col2.metric("✅ Completed Returns", f"{completed_returns}")
    col3.metric("❌ Cancelled Returns", f"{cancelled_returns}")
    col4.metric("📦 Total Quantity Returned", f"{total_quantity}")
    col5.metric("⏱️ SLA Breaches", f"{tech_breaches + return_breaches}")

    # 📊 Return Reason Summary
    if "return_reason" in df.columns:
        st.subheader("📋 Return Reason Summary")
        reason_summary = df["return_reason"].value_counts().reset_index()
        reason_summary.columns = ["Return Reason", "Count"]
        st.dataframe(reason_summary, use_container_width=True)

    # 📈 Return Requests Over Time
    if "return_requested_date" in df.columns and df["return_requested_date"].notna().any():
        st.subheader("📅 Return Requests Over Time")
        returns_by_date = df.groupby(df["return_requested_date"].dt.date).size().reset_index(name="Returns")
        fig = px.line(returns_by_date, x="return_requested_date", y="Returns", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    # 🏷️ Top Returned Products
    if {"sku", "product_title", "quantity"}.issubset(df.columns):
        sku_returns = (
            df.groupby(["sku", "product_title"])["quantity"]
            .sum()
            .reset_index()
            .sort_values(by="quantity", ascending=False)
            .rename(columns={"quantity": "Total Returned Quantity"})
        )

        st.subheader("🏷️ Top Returned Products")
        st.dataframe(sku_returns.head(10), use_container_width=True)

    # 📊 SLA Breach Breakdown
    if tech_breaches > 0 or return_breaches > 0:
        st.subheader("📊 SLA Breach Breakdown")
        breach_df = pd.DataFrame({
            "SLA Type": ["Tech Visit SLA", "Return Completion SLA"],
            "Breached": [tech_breaches, return_breaches]
        })
        fig_breach = px.bar(breach_df, x="SLA Type", y="Breached", color="SLA Type", text_auto=True)
        st.plotly_chart(fig_breach, use_container_width=True)

    # 🔍 Raw Data View
    with st.expander("📋 View Raw Return Data"):
        st.dataframe(df.head(50), use_container_width=True)
