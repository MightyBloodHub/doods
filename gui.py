import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

st.set_page_config(page_title="BSFL Experiment Dashboard", layout="wide")
st.title("BSFL Poultry Feed Experiment Dashboard")

uploaded_file = st.file_uploader("Upload the Excel file:", type=["xlsx"])
if uploaded_file is not None:
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names

    def read_sheet(name):
        return pd.read_excel(uploaded_file, sheet_name=name) if name in sheet_names else pd.DataFrame()

    instructions_df = read_sheet("Instructions")
    feed_df = read_sheet("Feed Consumption")
    weight_df = read_sheet("Weight Measurements")
    health_df = read_sheet("Health Observations")
    cost_df = read_sheet("Cost and Inventory")
    protocol_df = read_sheet("Protocol and Adjustments")

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Overview", "Feed Consumption", "Weight Measurements", "Health Observations", "Cost and Inventory", "Protocol & Adjustments"])

    if page == "Overview":
        st.header("Experiment Overview")

        st.subheader("Instructions")
        if not instructions_df.empty:
            for idx, row in instructions_df.iterrows():
                st.write(row[0])
        else:
            st.write("No instructions data found.")

        st.subheader("Key Metrics")

        # --- FEED METRICS ---
        if not feed_df.empty:
            # Convert Total Consumed column to numeric
            consumed_col = "Total Consumed (kg) [=Offered - Refused]"
            if consumed_col in feed_df.columns:
                feed_df[consumed_col] = pd.to_numeric(feed_df[consumed_col], errors='coerce')
                total_feed_consumed = feed_df[consumed_col].sum()
                if pd.notnull(total_feed_consumed):
                    st.metric("Total Feed Consumed (all groups)", f"{total_feed_consumed:.2f} kg")
                else:
                    st.metric("Total Feed Consumed (all groups)", "No numeric data")
            else:
                st.metric("Total Feed Consumed (all groups)", "Column not found")

        # --- WEIGHT METRICS ---
        if not weight_df.empty and "Weight (g)" in weight_df.columns:
            weight_df["Weight (g)"] = pd.to_numeric(weight_df["Weight (g)"], errors='coerce')
            avg_final_weight = weight_df["Weight (g)"].mean()
            if pd.notnull(avg_final_weight):
                st.metric("Average Bird Weight (overall)", f"{avg_final_weight:.2f} g")
            else:
                st.metric("Average Bird Weight (overall)", "No numeric data")

        # --- HEALTH METRICS ---
        if not health_df.empty and "Observation Type (Illness/Mortality/Behavior)" in health_df.columns:
            mortalities = health_df[health_df["Observation Type (Illness/Mortality/Behavior)"] == "Mortality"]
            st.metric("Total Mortalities Recorded", f"{len(mortalities)}")

        # --- COST METRICS ---
        if not cost_df.empty and all(col in cost_df.columns for col in ["Unit Cost (KWD/ton)", "Quantity Purchased (kg)"]):
            cost_df["Unit Cost (KWD/ton)"] = pd.to_numeric(cost_df["Unit Cost (KWD/ton)"], errors='coerce')
            cost_df["Quantity Purchased (kg)"] = pd.to_numeric(cost_df["Quantity Purchased (kg)"], errors='coerce')
            # Compute total cost from these numeric columns
            cost_df["Computed Total Cost"] = (cost_df["Unit Cost (KWD/ton)"]/1000) * cost_df["Quantity Purchased (kg)"]
            total_cost = cost_df["Computed Total Cost"].sum(skipna=True)
            if pd.notnull(total_cost):
                st.metric("Total Cost Recorded", f"{total_cost:.2f} KWD")
            else:
                st.metric("Total Cost Recorded", "No numeric data")
    # --- FEED CONSUMPTION ---
    elif page == "Feed Consumption":
        st.header("Feed Consumption Data")
        if feed_df.empty:
            st.write("No feed data available.")
        else:
            # Convert dates if possible
            if "Date (YYYY-MM-DD)" in feed_df.columns:
                feed_df["Date"] = pd.to_datetime(feed_df["Date (YYYY-MM-DD)"], errors='coerce')
            else:
                feed_df["Date"] = pd.NaT

            groups = feed_df["Group (Control/25% BSFL/35% BSFL)"].unique()
            selected_group = st.selectbox("Select Group:", options=groups)
            group_data = feed_df[feed_df["Group (Control/25% BSFL/35% BSFL)"] == selected_group].copy()

            st.subheader("Raw Data")
            st.dataframe(group_data, height=300)

            st.subheader("Feed Consumption Over Time")
            # Ensure numeric
            group_data["Consumed"] = pd.to_numeric(group_data["Total Consumed (kg) [=Offered - Refused]"], errors='coerce')
            chart_data = group_data.dropna(subset=["Date", "Consumed"])
            if not chart_data.empty:
                fig = px.line(chart_data, x="Date", y="Consumed", title=f"Feed Consumed Over Time - {selected_group}", markers=True)
                st.plotly_chart(fig, use_container_width=True)

    # --- WEIGHT MEASUREMENTS ---
    elif page == "Weight Measurements":
        st.header("Weight Measurements")
        if weight_df.empty:
            st.write("No weight data available.")
        else:
            if "Date (YYYY-MM-DD)" in weight_df.columns:
                weight_df["Date"] = pd.to_datetime(weight_df["Date (YYYY-MM-DD)"], errors='coerce')
            else:
                weight_df["Date"] = pd.NaT
            
            st.subheader("Raw Data")
            st.dataframe(weight_df, height=300)

            # Group and Bird filters
            groups = weight_df["Group"].dropna().unique()
            selected_group = st.selectbox("Select Group for Weight Analysis:", options=groups)
            group_data = weight_df[weight_df["Group"] == selected_group].copy()

            st.subheader("Weight Distribution (by Bird)")
            fig = px.box(group_data, x="Group", y="Weight (g)", points="all", title=f"Weight Distribution - {selected_group}")
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Average Weight Over Time")
            avg_over_time = group_data.groupby("Date")["Weight (g)"].mean().reset_index()
            fig = px.line(avg_over_time, x="Date", y="Weight (g)", title=f"Average Weight Over Time - {selected_group}", markers=True)
            st.plotly_chart(fig, use_container_width=True)

    # --- HEALTH OBSERVATIONS ---
    elif page == "Health Observations":
        st.header("Health Observations")
        if health_df.empty:
            st.write("No health data available.")
        else:
            if "Date (YYYY-MM-DD)" in health_df.columns:
                health_df["Date"] = pd.to_datetime(health_df["Date (YYYY-MM-DD)"], errors='coerce')
            else:
                health_df["Date"] = pd.NaT

            st.subheader("Raw Data")
            st.dataframe(health_df, height=300)

            # Count events by type
            event_counts = health_df["Observation Type (Illness/Mortality/Behavior)"].value_counts().reset_index()
            event_counts.columns = ["Type", "Count"]
            fig = px.bar(event_counts, x="Type", y="Count", title="Health Events by Type")
            st.plotly_chart(fig, use_container_width=True)

    # --- COST AND INVENTORY ---
    elif page == "Cost and Inventory":
        st.header("Cost and Inventory")
        if cost_df.empty:
            st.write("No cost data available.")
        else:
            st.subheader("Raw Data")
            st.dataframe(cost_df, height=300)

            # Summarize costs by type
            if "Type (Soy/BSFL/Other)" in cost_df.columns and "Unit Cost (KWD/ton)" in cost_df.columns and "Quantity Purchased (kg)" in cost_df.columns:
                cost_copy = cost_df.copy()
                # Recalculate total cost if possible
                cost_copy["Unit Cost"] = pd.to_numeric(cost_copy["Unit Cost (KWD/ton)"], errors='coerce')
                cost_copy["Quantity"] = pd.to_numeric(cost_copy["Quantity Purchased (kg)"], errors='coerce')
                cost_copy["Total Cost"] = (cost_copy["Unit Cost"]/1000)*cost_copy["Quantity"]
                cost_by_type = cost_copy.groupby("Type (Soy/BSFL/Other)")["Total Cost"].sum().reset_index()

                fig = px.pie(cost_by_type, names="Type (Soy/BSFL/Other)", values="Total Cost", title="Cost Distribution by Ingredient Type")
                st.plotly_chart(fig, use_container_width=True)

    # --- PROTOCOL & ADJUSTMENTS ---
    elif page == "Protocol & Adjustments":
        st.header("Protocol and Adjustments")
        if protocol_df.empty:
            st.write("No protocol data available.")
        else:
            st.subheader("Raw Data")
            st.dataframe(protocol_df, height=300)

            if "Approval Status" in protocol_df.columns:
                status_counts = protocol_df["Approval Status"].value_counts().reset_index()
                status_counts.columns = ["Status", "Count"]
                fig = px.bar(status_counts, x="Status", y="Count", title="Proposed Changes Approval Status")
                st.plotly_chart(fig, use_container_width=True)

else:
    st.write("Please upload a file to begin.")
