import streamlit as st

# Set page config (must be the first Streamlit command)
st.set_page_config(page_title="Ecom Reports Webapp", layout="wide")

# Sidebar platform selector
st.sidebar.title("🛒 Ecom Reports Webapp")
platform = st.sidebar.selectbox(
    "Select Platform",
    ["Amazon", "Flipkart", "Ajio", "Myntra", "Meesho"]
)

# Helper to load and run script dynamically
def run_script(script_path):
    with open(script_path, "r", encoding="utf-8") as file:
        code = file.read()
    exec(code, globals())

# Routing based on selected platform
if platform == "Amazon":
    run_script("amazon_app.py")
elif platform == "Flipkart":
    run_script("flipkart_app.py")
elif platform == "Ajio":
    run_script("ajio_app.py")
elif platform == "Myntra":
    run_script("myntra_app.py")
elif platform == "Meesho":
    run_script("meesho_app.py")

# Footer credit
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>By <strong>Tech Assasins</strong> | Powered by <strong>Seller Rocket</strong></p>",
    unsafe_allow_html=True
)
