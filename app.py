import streamlit as st
import pandas as pd
import plotly.express as px
import io
from datetime import datetime

st.set_page_config(page_title="BSFL Experiment Dashboard", layout="wide")

# Display Company Logo (ensure doods.png is in the same directory)
try:
    st.image("doods.png", width=150)
except FileNotFoundError:
    st.warning("Logo file 'doods.png' not found. Please ensure it is in the same directory.")

st.title("BSFL Poultry Feed Experiment Dashboard")

uploaded_file = st.file_uploader("Upload the Excel file:", type=["xlsx"])
if uploaded_file is not None:
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names

    expected_sheets = [
        "Instructions", 
        "Feed Consumption", 
        "Weight Measurements", 
        "Health Observations", 
        "Cost and Inventory", 
        "Protocol and Adjustments"
    ]

    def load_sheet(sheet_name):
        if sheet_name not in sheet_names:
            return pd.DataFrame()
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=0)
        # Drop the instruction row (second row) for all sheets except Instructions
        if sheet_name != "Instructions" and not df.empty:
            df = df.iloc[1:].reset_index(drop=True)
        return df

    instructions_df = load_sheet("Instructions")
    feed_df = load_sheet("Feed Consumption")
    weight_df = load_sheet("Weight Measurements")
    health_df = load_sheet("Health Observations")
    cost_df = load_sheet("Cost and Inventory")
    protocol_df = load_sheet("Protocol and Adjustments")

    # Compute Total Consumed (kg) in Python instead of relying on Excel formulas
    # Remove the original "Total Consumed (kg) [=Offered - Refused]" column if it exists
    if not feed_df.empty:
        if "Amount Offered (kg)" in feed_df.columns and "Amount Refused (kg)" in feed_df.columns:
            # Convert to numeric
            feed_df["Amount Offered (kg)"] = pd.to_numeric(feed_df["Amount Offered (kg)"], errors='coerce')
            feed_df["Amount Refused (kg)"] = pd.to_numeric(feed_df["Amount Refused (kg)"], errors='coerce')
            # Compute Total Consumed
            feed_df["Total Consumed (kg)"] = feed_df["Amount Offered (kg)"] - feed_df["Amount Refused (kg)"]
            # Drop the original formula column if it exists
            original_col = "Total Consumed (kg) [=Offered - Refused]"
            if original_col in feed_df.columns:
                feed_df = feed_df.drop(columns=[original_col])
        else:
            st.warning("Feed Consumption sheet missing 'Amount Offered (kg)' or 'Amount Refused (kg)' columns.")
    else:
        st.info("Feed Consumption sheet is empty or not found.")

    # Convert Weight (g) to numeric
    if not weight_df.empty and "Weight (g)" in weight_df.columns:
        weight_df["Weight (g)"] = pd.to_numeric(weight_df["Weight (g)"], errors='coerce')

    # Compute total cost if columns exist
    if not cost_df.empty:
        if "Unit Cost (KWD/ton)" in cost_df.columns and "Quantity Purchased (kg)" in cost_df.columns:
            cost_df["Unit Cost (KWD/ton)"] = pd.to_numeric(cost_df["Unit Cost (KWD/ton)"], errors='coerce')
            cost_df["Quantity Purchased (kg)"] = pd.to_numeric(cost_df["Quantity Purchased (kg)"], errors='coerce')
            cost_df["Computed Total Cost (KWD)"] = (cost_df["Unit Cost (KWD/ton)"]/1000) * cost_df["Quantity Purchased (kg)"]
        else:
            st.warning("Cost and Inventory sheet missing 'Unit Cost (KWD/ton)' or 'Quantity Purchased (kg)' columns.")

    # Store DataFrames in a dictionary for easier referencing and editing
    data_sheets = {
        "Instructions": instructions_df,
        "Feed Consumption": feed_df,
        "Weight Measurements": weight_df,
        "Health Observations": health_df,
        "Cost and Inventory": cost_df,
        "Protocol and Adjustments": protocol_df
    }

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Overview"] + expected_sheets[1:] + ["Data Editor & Export"])

    if page == "Overview":
        st.header("Experiment Overview")

        # Display Instructions
        st.subheader("Instructions")
        if not instructions_df.empty:
            for idx, row in instructions_df.iterrows():
                st.write(row[0])
        else:
            st.write("No instructions found.")

        st.subheader("Key Metrics")
        # Feed Metrics (using our computed "Total Consumed (kg)")
        if not feed_df.empty and "Total Consumed (kg)" in feed_df.columns:
            total_feed_consumed = feed_df["Total Consumed (kg)"].sum(skipna=True)
            st.metric("Total Feed Consumed (all groups)", f"{total_feed_consumed:.2f} kg")
        else:
            st.metric("Total Feed Consumed (all groups)", "No data available")

        # Weight Metrics
        if not weight_df.empty and "Weight (g)" in weight_df.columns:
            avg_final_weight = weight_df["Weight (g)"].mean(skipna=True)
            if pd.notnull(avg_final_weight):
                st.metric("Average Bird Weight (overall)", f"{avg_final_weight:.2f} g")
            else:
                st.metric("Average Bird Weight (overall)", "No data available")
        else:
            st.metric("Average Bird Weight (overall)", "No data available")

        # Health Metrics
        if not health_df.empty and "Observation Type (Illness/Mortality/Behavior)" in health_df.columns:
            mortalities = health_df[health_df["Observation Type (Illness/Mortality/Behavior)"] == "Mortality"]
            st.metric("Total Mortalities Recorded", f"{len(mortalities)}")
        else:
            st.metric("Total Mortalities Recorded", "No data available")

        # Cost Metrics
        if not cost_df.empty and "Computed Total Cost (KWD)" in cost_df.columns:
            total_cost = cost_df["Computed Total Cost (KWD)"].sum(skipna=True)
            if pd.notnull(total_cost):
                st.metric("Total Cost Recorded", f"{total_cost:.2f} KWD")
            else:
                st.metric("Total Cost Recorded", "No data available")
        else:
            st.metric("Total Cost Recorded", "No data available")

    elif page == "Feed Consumption":
        st.header("Feed Consumption")
        if feed_df.empty:
            st.write("No feed data available.")
        else:
            date_col = "Date (YYYY-MM-DD)"
            if date_col in feed_df.columns:
                feed_df["Date"] = pd.to_datetime(feed_df[date_col], errors='coerce')
            else:
                feed_df["Date"] = pd.NaT

            group_col = "Group (Control/25% BSFL/35% BSFL)"
            if group_col in feed_df.columns:
                groups = feed_df[group_col].dropna().unique()
                selected_group = st.selectbox("Select Group:", options=groups) if len(groups) > 0 else None

                if selected_group:
                    group_data = feed_df[feed_df[group_col] == selected_group].copy()
                else:
                    group_data = feed_df.copy()

                st.subheader("Raw Data")
                st.dataframe(group_data.drop(columns=["Date (YYYY-MM-DD)"] if "Date (YYYY-MM-DD)" in group_data.columns else []), height=300)

                # Use our computed "Total Consumed (kg)" column for charts
                if "Total Consumed (kg)" in group_data.columns and "Date" in group_data.columns:
                    chart_data = group_data.dropna(subset=["Date", "Total Consumed (kg)"])
                    if not chart_data.empty:
                        fig = px.line(chart_data, x="Date", y="Total Consumed (kg)", 
                                      title=f"Feed Consumed Over Time - {selected_group}", markers=True)
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("Could not find the Group column in feed data.")

    elif page == "Weight Measurements":
        st.header("Weight Measurements")
        if weight_df.empty:
            st.write("No weight data available.")
        else:
            date_col = "Date (YYYY-MM-DD)"
            if date_col in weight_df.columns:
                weight_df["Date"] = pd.to_datetime(weight_df[date_col], errors='coerce')
            else:
                weight_df["Date"] = pd.NaT

            st.subheader("Raw Data")
            st.dataframe(weight_df.drop(columns=["Date (YYYY-MM-DD)"] if "Date (YYYY-MM-DD)" in weight_df.columns else []), height=300)

            if "Group" in weight_df.columns and "Weight (g)" in weight_df.columns:
                groups = weight_df["Group"].dropna().unique()
                selected_group = st.selectbox("Select Group for Weight Analysis:", options=groups)

                group_data = weight_df[weight_df["Group"] == selected_group].copy()

                st.subheader("Weight Distribution (by Bird)")
                if not group_data.empty:
                    fig = px.box(group_data, x="Group", y="Weight (g)", points="all", 
                                 title=f"Weight Distribution - {selected_group}")
                    st.plotly_chart(fig, use_container_width=True)

                    st.subheader("Average Weight Over Time")
                    avg_over_time = group_data.groupby("Date")["Weight (g)"].mean().reset_index()
                    fig = px.line(avg_over_time, x="Date", y="Weight (g)", 
                                  title=f"Average Weight Over Time - {selected_group}", markers=True)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("Necessary columns missing in weight data.")

    elif page == "Health Observations":
        st.header("Health Observations")
        if health_df.empty:
            st.write("No health data available.")
        else:
            date_col = "Date (YYYY-MM-DD)"
            if date_col in health_df.columns:
                health_df["Date"] = pd.to_datetime(health_df[date_col], errors='coerce')
            else:
                health_df["Date"] = pd.NaT

            st.subheader("Raw Data")
            st.dataframe(health_df.drop(columns=["Date (YYYY-MM-DD)"] if "Date (YYYY-MM-DD)" in health_df.columns else []), height=300)

            obs_type_col = "Observation Type (Illness/Mortality/Behavior)"
            if obs_type_col in health_df.columns:
                event_counts = health_df[obs_type_col].value_counts().reset_index()
                event_counts.columns = ["Type", "Count"]
                fig = px.bar(event_counts, x="Type", y="Count", title="Health Events by Type")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("Observation Type column missing in health data.")

    elif page == "Cost and Inventory":
        st.header("Cost and Inventory")
        if cost_df.empty:
            st.write("No cost data available.")
        else:
            st.subheader("Raw Data")
            st.dataframe(cost_df.drop(columns=["Computed Total Cost (KWD)"] if "Computed Total Cost (KWD)" in cost_df.columns else []), height=300)

            if "Type (Soy/BSFL/Other)" in cost_df.columns and "Computed Total Cost (KWD)" in cost_df.columns:
                cost_by_type = cost_df.groupby("Type (Soy/BSFL/Other)")["Computed Total Cost (KWD)"].sum().reset_index()
                fig = px.pie(cost_by_type, names="Type (Soy/BSFL/Other)", values="Computed Total Cost (KWD)",
                             title="Cost Distribution by Ingredient Type")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("Necessary columns missing in cost data.")

    elif page == "Protocol and Adjustments":
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
                st.write("Approval Status column missing in protocol data.")

    elif page == "Data Editor & Export":
        st.header("Data Editor & Export")
        st.write("Select a sheet to edit. After editing, you can export the updated workbook.")

        editable_sheet = st.selectbox("Select a Sheet to Edit:", options=expected_sheets)
        if editable_sheet not in data_sheets or data_sheets[editable_sheet].empty:
            st.write("No data available for this sheet.")
        else:
            # Create a copy to edit
            edited_df = st.data_editor(data_sheets[editable_sheet].copy(), key=f"editor_{editable_sheet}", num_rows="dynamic")

            st.write("Modify the data above as needed. Then click 'Save Changes to Memory' to update the in-memory data.")
            if st.button("Save Changes to Memory"):
                data_sheets[editable_sheet] = edited_df
                st.success("Changes saved to memory. You can now export the entire workbook.")

            if st.button("Export Updated Workbook"):
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    # Save Instructions as is (without headers)
                    if not instructions_df.empty:
                        instructions_df.to_excel(writer, sheet_name="Instructions", index=False, header=False)
                    # Save other sheets with computed columns
                    for sname, df in data_sheets.items():
                        if sname == "Instructions":
                            continue
                        if not df.empty:
                            # Reinsert a placeholder instructions row
                            headers = df.columns.tolist()
                            instruction_row = ["(Instructions row omitted)"] + [""]*(len(headers)-1)
                            combined_df = pd.concat([pd.DataFrame([instruction_row], columns=headers), df], ignore_index=True)
                            combined_df.to_excel(writer, sheet_name=sname, index=False)
                        else:
                            pd.DataFrame().to_excel(writer, sheet_name=sname)
                # Provide download
                st.download_button(
                    label="Download Updated Excel",
                    data=output.getvalue(),
                    file_name=f"Updated_BSFL_Experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.success("Your updated workbook is ready for download!")
else:
    st.write("Please upload a file to begin.")
