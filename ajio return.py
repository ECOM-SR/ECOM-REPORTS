import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Ajio Return Report Dashboard", layout="wide")
st.title("📦 Ajio Return Report Analysis")

uploaded_file = st.file_uploader("Upload the Ajio Return Excel Report", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    # Convert date columns
    date_cols = ['Return Created Date', 'Return Delivered Date', 'QC completion date', 'Credit Note Generation Date']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Fill missing numeric columns
    num_cols = ['Return QTY', 'Return Value', 'Credit Note Value', 'Credit Note Pre Tax Value',
                'Credit Note Tax Value', 'CGST AMOUNT', 'SGST AMOUNT', 'IGST AMOUNT']
    for col in num_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)

    # KPIs
    total_returns = len(df)
    total_return_qty = df['Return QTY'].sum()
    total_return_value = df['Return Value'].sum()
    total_credit_value = df['Credit Note Value'].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🔁 Total Returns", total_returns)
    col2.metric("📦 Total Return Qty", int(total_return_qty))
    col3.metric("💸 Total Return Value", f"₹{total_return_value:,.2f}")
    col4.metric("🧾 Credit Note Value", f"₹{total_credit_value:,.2f}")

    # Returns over time
    if 'Return Created Date' in df.columns:
        returns_by_date = df.groupby(df['Return Created Date'].dt.date)['Return QTY'].sum().reset_index()
        fig = px.bar(returns_by_date, x='Return Created Date', y='Return QTY',
                     title='📅 Returns by Date', labels={'Return Created Date': 'Date', 'Return QTY': 'Qty'})
        st.plotly_chart(fig, use_container_width=True)

    # Top Returned SKUs
    top_skus = df.groupby('SELLER SKU')['Return QTY'].sum().sort_values(ascending=False).head(10).reset_index()
    fig2 = px.bar(top_skus, x='SELLER SKU', y='Return QTY',
                  title='📌 Top Returned SKUs', labels={'Return QTY': 'Qty'})
    st.plotly_chart(fig2, use_container_width=True)

    # Top Returned Product Names
    if 'RETURN ORDER NUMBER' in df.columns and 'BRAND' in df.columns:
        st.subheader("📦 Return Details Table")
        st.dataframe(df[['RETURN ORDER NUMBER', 'SELLER SKU', 'Return QTY', 'Return Value', 'Disposition', 'QC Reason coding', 'BRAND']])

    # QC Disposition breakdown
    if 'Disposition' in df.columns:
        qc_disp = df['Disposition'].value_counts().reset_index()
        qc_disp.columns = ['Disposition', 'Count']
        fig3 = px.pie(qc_disp, names='Disposition', values='Count', title='🧪 QC Disposition Breakdown')
        st.plotly_chart(fig3, use_container_width=True)

    # Top QC Reasons
    if 'QC Reason coding' in df.columns:
        qc_reasons = df['QC Reason coding'].value_counts().head(10).reset_index()
        qc_reasons.columns = ['QC Reason', 'Count']
        fig4 = px.bar(qc_reasons, x='QC Reason', y='Count', title='❌ Top QC Reasons')
        st.plotly_chart(fig4, use_container_width=True)

    # Return Status
    if 'Return Status' in df.columns:
        ret_status = df['Return Status'].value_counts().reset_index()
        ret_status.columns = ['Return Status', 'Count']
        fig5 = px.pie(ret_status, names='Return Status', values='Count', title='🚚 Return Status Distribution')
        st.plotly_chart(fig5, use_container_width=True)

    # Carrier performance
    if 'Return Carrier Name' in df.columns:
        carrier_data = df['Return Carrier Name'].value_counts().head(10).reset_index()
        carrier_data.columns = ['Carrier', 'Count']
        fig6 = px.bar(carrier_data, x='Carrier', y='Count', title='🚛 Top Return Carriers')
        st.plotly_chart(fig6, use_container_width=True)

    # Optional: Raw data download
    with st.expander("📄 View Full Data"):
        st.dataframe(df)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "ajio_return_data.csv", "text/csv")