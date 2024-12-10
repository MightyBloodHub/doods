import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Set the page configuration for a wide layout and appropriate title
st.set_page_config(page_title="BSFL Poultry Feed Dashboard", layout="wide")

# Display the Doodz logo at the top
st.image("doods.png", width=150)
st.title("BSFL Poultry Feed Experiment Dashboard")

# Preload the Excel file by default
excel_file = "BSFL_Experiment_Full_Dummy_Data.xlsx"
if not os.path.exists(excel_file):
    st.error(f"'{excel_file}' file not found. Please make sure it is in the same directory.")
    st.stop()

xls = pd.ExcelFile(excel_file)
sheet_names = xls.sheet_names

def load_sheet(name):
    return pd.read_excel(excel_file, sheet_name=name) if name in sheet_names else pd.DataFrame()

# Load all relevant sheets into DataFrames
feed_df = load_sheet("Feed Consumption")
weight_df = load_sheet("Weight Measurements")
health_df = load_sheet("Health Observations")
cost_df = load_sheet("Cost and Inventory")
protocol_df = load_sheet("Protocol and Adjustments")

# Sidebar navigation
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

# --- Overview Page ---
if page == "Overview":
    st.header("Overview")
    st.write(
        "This dashboard provides insights into the BSFL poultry feed experiment data. "
        "The Excel file only contains raw data; all computations and visualizations are handled by this software."
    )

    st.subheader("Key Metrics")
    # Basic Feed Consumption Metric
    if (
        not feed_df.empty
        and "Feed Offered (g)" in feed_df.columns
        and "Feed Refused (g)" in feed_df.columns
    ):
        feed_df["Feed Offered (g)"] = pd.to_numeric(feed_df["Feed Offered (g)"], errors="coerce")
        feed_df["Feed Refused (g)"] = pd.to_numeric(feed_df["Feed Refused (g)"], errors="coerce")
        feed_df["Consumed (g)"] = feed_df["Feed Offered (g)"] - feed_df["Feed Refused (g)"]
        total_consumed = feed_df["Consumed (g)"].sum()
        st.metric("Total Feed Consumed (all groups)", f"{total_consumed:.2f} g")

    # Basic Weight Metric
    if not weight_df.empty and "Weight (g)" in weight_df.columns:
        weight_df["Weight (g)"] = pd.to_numeric(weight_df["Weight (g)"], errors="coerce")
        avg_weight = weight_df["Weight (g)"].mean()
        st.metric("Average Bird Weight (overall)", f"{avg_weight:.2f} g")

    # Mortality Metric
    if not health_df.empty and "Observation Type" in health_df.columns:
        mortalities = health_df[health_df["Observation Type"] == "Mortality"]
        st.metric("Total Mortalities Recorded", f"{len(mortalities)}")

# --- Feed Consumption Page ---
elif page == "Feed Consumption":
    st.header("Feed Consumption Data")
    if feed_df.empty:
        st.write("No feed consumption data available.")
    else:
        st.subheader("Raw Data")
        st.dataframe(feed_df, height=300)

        if (
            "Feed Offered (g)" in feed_df.columns
            and "Feed Refused (g)" in feed_df.columns
            and "Date" in feed_df.columns
            and "Group" in feed_df.columns
        ):
            feed_df["Feed Offered (g)"] = pd.to_numeric(feed_df["Feed Offered (g)"], errors="coerce")
            feed_df["Feed Refused (g)"] = pd.to_numeric(feed_df["Feed Refused (g)"], errors="coerce")
            feed_df["Consumed (g)"] = feed_df["Feed Offered (g)"] - feed_df["Feed Refused (g)"]

            consumed_summary = feed_df.groupby(["Date", "Group"])["Consumed (g)"].sum().reset_index()
            fig = px.line(
                consumed_summary,
                x="Date",
                y="Consumed (g)",
                color="Group",
                title="Feed Consumed Over Time",
            )
            st.plotly_chart(fig, use_container_width=True)

# --- Weight Measurements Page ---
elif page == "Weight Measurements":
    st.header("Weight Measurements")
    if weight_df.empty:
        st.write("No weight data available.")
    else:
        st.subheader("Raw Data")
        st.dataframe(weight_df, height=300)

        if "Weight (g)" in weight_df.columns and "Date" in weight_df.columns and "Group" in weight_df.columns:
            weight_df["Weight (g)"] = pd.to_numeric(weight_df["Weight (g)"], errors="coerce")
            avg_over_time = weight_df.groupby(["Date", "Group"])["Weight (g)"].mean().reset_index()
            fig = px.line(
                avg_over_time,
                x="Date",
                y="Weight (g)",
                color="Group",
                title="Average Weight Over Time",
            )
            st.plotly_chart(fig, use_container_width=True)

# --- Health Observations Page ---
elif page == "Health Observations":
    st.header("Health Observations")
    if health_df.empty:
        st.write("No health observations data available.")
    else:
        st.subheader("Raw Data")
        st.dataframe(health_df, height=300)

        if "Observation Type" in health_df.columns and "Group" in health_df.columns:
            # Show difference between groups
            group_event_counts = (
                health_df.groupby(["Observation Type", "Group"])["Bird ID"]
                .count()
                .reset_index()
            )
            group_event_counts.columns = ["Observation Type", "Group", "Count"]

            # Create a bar chart to show differences by Observation Type and Group
            fig = px.bar(
                group_event_counts,
                x="Observation Type",
                y="Count",
                color="Group",
                barmode="group",
                title="Health Events by Type and Group",
            )
            st.plotly_chart(fig, use_container_width=True)

# --- Cost and Inventory Page ---
elif page == "Cost and Inventory":
    st.header("Cost and Inventory")
    if cost_df.empty:
        st.write("No cost data available.")
    else:
        st.subheader("Raw Data")
        st.dataframe(cost_df, height=300)

        if all(col in cost_df.columns for col in ["Unit Cost (KWD/ton)", "Quantity (kg)"]):
            cost_df["Unit Cost (KWD/ton)"] = pd.to_numeric(cost_df["Unit Cost (KWD/ton)"], errors="coerce")
            cost_df["Quantity (kg)"] = pd.to_numeric(cost_df["Quantity (kg)"], errors="coerce")
            cost_df["Total Cost (KWD)"] = (cost_df["Unit Cost (KWD/ton)"] / 1000) * cost_df["Quantity (kg)"]
            cost_by_item = cost_df.groupby("Item/Ingredient")["Total Cost (KWD)"].sum().reset_index()

            fig = px.pie(
                cost_by_item,
                names="Item/Ingredient",
                values="Total Cost (KWD)",
                title="Cost Distribution by Ingredient",
            )
            st.plotly_chart(fig, use_container_width=True)

# --- Protocol & Adjustments Page ---
elif page == "Protocol & Adjustments":
    st.header("Protocol and Adjustments")
    if protocol_df.empty:
        st.write("No protocol data available.")
    else:
        st.subheader("Raw Data")
        st.dataframe(protocol_df, height=300)

# --- Company Structure Page ---
elif page == "Company Structure":
    st.header("Doodz Company Structure")
    st.subheader("Where Innovation Meets Execution :rocket:")

    # Removed the duplicate Organizational Philosophy at the top.
    # We'll only keep it near the end as requested.

    st.markdown("""
    Below is our evolving company structure, represented as a **futuristic, interactive sunburst diagram**. Hover over each section to learn more, and imagine how each role fits into a larger, dynamic ecosystem:
    
    *Your cursor and imagination are your navigation tools. Dive in and explore!* :crystal_ball:
    """)

    # Define hierarchical data for the sunburst chart
    data = {
        "names": [
            "Doodz",
            "CEO: Ahmad Alothman",
            "CSO: Omar AlOthman",
            "CMO: Hamad Al-Khudor",
            "COO: Abdullah Abul",
            "Team Member 1: [Role]",
            "Team Member 2: [Role]",
            "Team Member 3: [Role]",
            "Team Member 4: [Role]",
            "Team Member 5: [Role]",
            "Team Member 6: [Role]",
        ],
        "parents": [
            "",  # Doodz is the root
            "Doodz",  # CEO reports to Doodz
            "CEO: Ahmad Alothman",  # CSO reports to CEO
            "CEO: Ahmad Alothman",  # CMO reports to CEO
            "CEO: Ahmad Alothman",  # COO reports to CEO
            "CSO: Omar AlOthman",  # Team Member 1 reports to CSO
            "CSO: Omar AlOthman",  # Team Member 2 reports to CSO
            "CMO: Hamad Al-Khudor",  # Team Member 3 reports to CMO
            "CMO: Hamad Al-Khudor",  # Team Member 4 reports to CMO
            "COO: Abdullah Abul",    # Team Member 5 reports to COO
            "COO: Abdullah Abul",    # Team Member 6 reports to COO
        ],
        "roles": [
            "Root of innovation and growth",
            "Leads the company with vision and strategy :crown:",
            "Drives scientific R&D and product excellence :microscope:",
            "Forges brand presence and market strategies :loudspeaker:",
            "Optimizes operations and ensures efficient production :gear:",
            "Role description for Team Member 1",
            "Role description for Team Member 2",
            "Role description for Team Member 3",
            "Role description for Team Member 4",
            "Role description for Team Member 5",
            "Role description for Team Member 6",
        ],
    }

    df = pd.DataFrame(data)

    # Create a sunburst chart to visualize company structure
    fig = px.sunburst(
        df,
        names="names",
        parents="parents",
        hover_data=["roles"],
        title="Doodz Hierarchy Sunburst",
        color="parents",  # Color by parent to maintain color consistency
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>%{customdata[0]}<extra></extra>",
        marker=dict(line=dict(color='#000000', width=2))
    )
    fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
    st.plotly_chart(fig, use_container_width=True)

    # Additional details in expanders
    st.markdown("### Detailed Roles and Responsibilities")
    with st.expander("CEO: Ahmad Alothman :crown:"):
        st.write("""
        - Sets the overarching vision and strategic direction for the company.
        - Oversees all operations, ensuring cohesion across departments.
        - Makes high-level decisions and secures resources for long-term growth.
        """)

    with st.expander("CSO: Omar AlOthman :microscope:"):
        st.write("""
        - Leads scientific R&D and ensures the integrity of feed formulations.
        - Guides experimental design and data interpretation.
        - Champions innovation, staying at the cutting edge of poultry nutrition science.
        """)

    with st.expander("CMO: Hamad Al-Khudor :loudspeaker:"):
        st.write("""
        - Develops and executes branding and marketing strategies.
        - Identifies emerging markets and cultivates customer relationships.
        - Communicates product value propositions to stakeholders, ensuring brand recognition.
        """)

    with st.expander("COO: Abdullah Abul :gear:"):
        st.write("""
        - Oversees daily operations, ensuring products meet quality and efficiency benchmarks.
        - Coordinates logistics, inventory management, and supply chain optimization.
        - Maintains seamless inter-departmental communication.
        """)

    # Placeholder for future team members
    team_members = df[df["names"].str.contains("Team Member")]

    for _, row in team_members.iterrows():
        with st.expander(f"{row['names']}"):
            st.write(row["roles"])

    # Organizational Philosophy at the near end
    st.markdown("### Organizational Philosophy")
    st.write("""
    *Our structure is designed not only to define roles but to catalyze cross-pollination of ideas. Each leader, represented here, is a node in a network—empowering teams, driving innovation, and collectively forging the future of sustainable poultry feed solutions.*
    """)

# No file upload prompt since we are preloading the data
