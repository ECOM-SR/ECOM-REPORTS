import streamlit as st

st.set_page_config(page_title="📦 Ecom Reports Webapp", layout="wide")
st.sidebar.title("🧭 Ecom Reports Navigation")

platform = st.sidebar.selectbox("Choose Platform", ["Amazon", "Flipkart", "Ajio"])
report_type = st.sidebar.radio("Select Report Type", ["Orders", "Returns", "Inventory"])

def run_script(path):
    with open(path, 'r', encoding='utf-8') as file:
        code = file.read()
        exec(code, globals())

# Route to corresponding files
if platform == "Amazon":
    if report_type == "Orders":
        run_script("amazon_order.py")
    elif report_type == "Returns":
        run_script("amazon_return.py")
    elif report_type == "Inventory":
        run_script("amazon_inventory.py")

elif platform == "Flipkart":
    if report_type == "Orders":
        run_script("flipkart_order.py")
    elif report_type == "Returns":
        run_script("flipkart_returns_report.py")
    elif report_type == "Inventory":
        run_script("flipkart_inventory_report.py")

elif platform == "Ajio":
    if report_type == "Orders":
        run_script("ajio_order.py")
    elif report_type == "Returns":
        run_script("ajio return.py")
    elif report_type == "Inventory":
        run_script("ajio_app.py")
