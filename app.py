import streamlit as st
import os
import pandas as pd
from io import BytesIO
from utils.data_utils import load_sheets, export_to_excel

st.set_page_config(page_title="BSFL Poultry Feed Dashboard", layout="wide")

st.image("doods.png", width=150)
st.title("BSFL Poultry Feed Experiment Dashboard")

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    [
        "Overview",
        "Feed Consumption",
        "Weight Measurements",
        "Health Observations",
        "Cost and Inventory",
        "Protocol & Adjustments",
        "Company Structure",
    ],
)

st.sidebar.markdown("---")
uploaded_file = st.sidebar.file_uploader("Upload a new 'BSFL_Experiment_Full_Dummy_Data.xlsx' file:", type=["xlsx"])
export_button = st.sidebar.button("Export Current Data as Excel")

if uploaded_file is not None:
    try:
        data = uploaded_file.read()
        excel_data = BytesIO(data)
        feed_df, weight_df, health_df, cost_df, protocol_df, breakdown_df = load_sheets(excel_data)
    except Exception as e:
        st.error(f"Error processing uploaded file: {e}")
        feed_df = weight_df = health_df = cost_df = protocol_df = breakdown_df = pd.DataFrame()
else:
    default_excel = "BSFL_Experiment_Full_Dummy_Data.xlsx"
    if os.path.exists(default_excel):
        feed_df, weight_df, health_df, cost_df, protocol_df, breakdown_df = load_sheets(default_excel)
    else:
        st.error(f"'{default_excel}' file not found. Please upload the Excel file using the uploader below.")
        feed_df = weight_df = health_df = cost_df = protocol_df = breakdown_df = pd.DataFrame()

if export_button:
    if any([not df.empty for df in [feed_df, weight_df, health_df, cost_df, protocol_df, breakdown_df]]):
        excel_file = export_to_excel(feed_df, weight_df, health_df, cost_df, protocol_df, breakdown_df)
        st.sidebar.download_button(
            label="Download Excel File",
            data=excel_file,
            file_name="BSFL_Experiment_Export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.sidebar.success("Export ready! Click the download button.")
    else:
        st.sidebar.warning("No data available to export.")

# Navigation
if page == "Overview":
    from custom_pages.overview import show_overview
    show_overview(feed_df, weight_df, health_df)

elif page == "Feed Consumption":
    from custom_pages.feed_consumption import show_feed_consumption
    show_feed_consumption(feed_df)

elif page == "Weight Measurements":
    from custom_pages.weight_measurements import show_weight_measurements
    show_weight_measurements(weight_df)

elif page == "Health Observations":
    from custom_pages.health_observations import show_health_observations
    show_health_observations(health_df)

elif page == "Cost and Inventory":
    from custom_pages.cost_inventory import show_cost_inventory
    # Pass both cost_df and breakdown_df
    show_cost_inventory(cost_df, breakdown_df)

elif page == "Protocol & Adjustments":
    from custom_pages.protocol_adjustments import show_protocol_adjustments
    show_protocol_adjustments(protocol_df)

elif page == "Company Structure":
    from custom_pages.company_structure import show_company_structure
    show_company_structure()

else:
    st.write("Page not found.")
