import streamlit as st
import pandas as pd
import plotly.express as px

# Set the page configuration at the top

st.title("🛍️ AJIO Reports Dashboard")

# Tabs for Navigation
tab1, tab2 = st.tabs(["📦 Orders", "🔁 Returns"])

# ------------------------ #
# 📦 AJIO ORDER ANALYSIS
# ------------------------ #
with tab1:
    st.header("📦 Ajio Order Report")
    uploaded_order = st.file_uploader("Upload AJIO Order Report (.xlsx)", type=["xlsx"], key="ajio_order")

    if uploaded_order:
        try:
            df = pd.read_excel(uploaded_order)
            df.columns = df.columns.str.strip()

            # Required columns check
            required = ['Status', 'Total Value', 'CGST_AMOUNT', 'SGST_AMOUNT', 'IGST_AMOUNT',
                        'Listing MRP', 'Selling Price', 'Seller SKU', 'Order Qty',
                        'Customer Cancelled QTY', 'Seller Cancelled QTY', 'SLA Status', 'Description']
            if not all(col in df.columns for col in required):
                st.error("Missing required columns in the uploaded file.")
            else:
                # Fill and process
                df.fillna(0, inplace=True)
                if 'Order Date' in df.columns:
                    df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
                    sales_by_day = df.groupby(df['Order Date'].dt.date)['Total Value'].sum()
                    orders_by_day = df.groupby(df['Order Date'].dt.date).size()
                else:
                    sales_by_day = pd.Series([], dtype=float)
                    orders_by_day = pd.Series([], dtype=int)

                # Metrics
                st.metric("📦 Total Orders", len(df))
                st.metric("❌ Cancelled Orders", len(df[df['Status'].str.contains("Cancelled", na=False)]))
                st.metric("💰 Total Sales", f"₹{df['Total Value'].sum():,.2f}")
                st.metric("🧾 Tax", f"₹{df['CGST_AMOUNT'].sum() + df['SGST_AMOUNT'].sum() + df['IGST_AMOUNT'].sum():,.2f}")
                st.metric("🏷️ Discounts", f"₹{df['Listing MRP'].sum() - df['Selling Price'].sum():,.2f}")

                # Top & Slow movers
                top = df.groupby(['Seller SKU', 'Description'])['Order Qty'].sum().sort_values(ascending=False).head(10).reset_index()
                slow = df.groupby(['Seller SKU', 'Description'])['Order Qty'].sum().sort_values().head(10).reset_index()

                st.subheader("🔥 Top-Selling SKUs")
                st.dataframe(top.rename(columns={"Order Qty": "Total Orders"}))

                st.subheader("❄️ Slow-Moving SKUs")
                st.dataframe(slow.rename(columns={"Order Qty": "Total Orders"}))

                # Charts
                if not sales_by_day.empty:
                    st.subheader("📈 Sales by Day")
                    st.line_chart(sales_by_day)
                if not orders_by_day.empty:
                    st.subheader("📅 Orders by Day")
                    st.bar_chart(orders_by_day)

        except Exception as e:
            st.error(f"Error in Order Report: {e}")

# ------------------------ #
# 🔁 AJIO RETURN ANALYSIS
# ------------------------ #
with tab2:
    st.header("🔁 Ajio Return Report")
    uploaded_return = st.file_uploader("Upload AJIO Return Report (.xlsx)", type=["xlsx"], key="ajio_return")

    if uploaded_return:
        try:
            df = pd.read_excel(uploaded_return)
            df.columns = df.columns.str.strip()

            # Convert Dates
            date_cols = ['Return Created Date', 'Return Delivered Date', 'QC completion date', 'Credit Note Generation Date']
            for col in date_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')

            # Fill numeric
            for col in ['Return QTY', 'Return Value', 'Credit Note Value']:
                if col in df.columns:
                    df[col] = df[col].fillna(0)

            # KPIs
            st.metric("🔁 Total Returns", len(df))
            st.metric("📦 Returned Qty", int(df['Return QTY'].sum()))
            st.metric("💸 Return Value", f"₹{df['Return Value'].sum():,.2f}")
            st.metric("🧾 Credit Note", f"₹{df['Credit Note Value'].sum():,.2f}")

            # Charts
            if 'Return Created Date' in df.columns:
                returns_by_date = df.groupby(df['Return Created Date'].dt.date)['Return QTY'].sum().reset_index()
                fig = px.bar(returns_by_date, x='Return Created Date', y='Return QTY', title="📅 Returns Over Time")
                st.plotly_chart(fig, use_container_width=True)

            # Top SKUs
            if 'SELLER SKU' in df.columns:
                top_skus = df.groupby('SELLER SKU')['Return QTY'].sum().sort_values(ascending=False).head(10).reset_index()
                fig2 = px.bar(top_skus, x='SELLER SKU', y='Return QTY', title="📌 Top Returned SKUs")
                st.plotly_chart(fig2, use_container_width=True)

            # QC Reason
            if 'QC Reason coding' in df.columns:
                qc_reasons = df['QC Reason coding'].value_counts().head(10).reset_index()
                qc_reasons.columns = ['QC Reason', 'Count']
                st.bar_chart(qc_reasons.set_index('QC Reason'))

            # Optional Raw Table
            with st.expander("📄 Full Return Table"):
                st.dataframe(df)

        except Exception as e:
            st.error(f"Error in Return Report: {e}")
