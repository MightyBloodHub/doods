import streamlit as st
import pandas as pd
import plotly.express as px

def show_company_structure():
    st.header("Doodz Company Structure")
    st.subheader("Where Innovation Meets Execution :rocket:")

    st.markdown("""
    Below is our evolving company structure, represented as a **futuristic, interactive sunburst diagram**. 
    Hover over each section to learn more, and imagine how each role fits into a larger, dynamic ecosystem:
    
    *Your cursor and imagination are your navigation tools. Dive in and explore!* :crystal_ball:
    """)

    data = {
        "names": [
            "Doodz",
            "Ahmad Alothman (CEO)",
            "Omar AlOthman (CSO) ",
            "Hamad Al-Khudor (CMO)",
            "Abdullah Abul (COO)",
            "Team Member 1: [Role]",
            "Team Member 2: [Role]",
            "Team Member 3: [Role]",
            "Team Member 4: [Role]",
            "Team Member 5: [Role]",
            "Team Member 6: [Role]",
        ],
        "parents": [
            "",
            "Doodz",
            "Ahmad Alothman (CEO)",
            "Ahmad Alothman (CEO)",
            "Ahmad Alothman (CEO)",
            "Omar AlOthman (CSO) ",
            "Omar AlOthman (CSO) ",
            "Hamad Al-Khudor (CMO)",
            "Hamad Al-Khudor (CMO)",
            "Abdullah Abul (COO)",
            "Abdullah Abul (COO)",
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

    fig = px.sunburst(
        df,
        names="names",
        parents="parents",
        hover_data=["roles"],
        title="Doodz Hierarchy Sunburst",
        color="parents",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>%{customdata[0]}<extra></extra>",
        marker=dict(line=dict(color='#000000', width=2))
    )
    fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
    st.plotly_chart(fig, use_container_width=True)

    # Additional details in expanders
    st.markdown("### Detailed Roles and Responsibilities")
    with st.expander("Ahmad Alothman (CEO) :crown:"):
        st.write("""
        - Sets the overarching vision and strategic direction for the company.
        - Oversees all operations, ensuring cohesion across departments.
        - Makes high-level decisions and secures resources for long-term growth.
        """)

    with st.expander("Omar AlOthman (CSO)  :microscope:"):
        st.write("""
        - Leads scientific R&D and ensures the integrity of feed formulations.
        - Guides experimental design and data interpretation.
        - Champions innovation, staying at the cutting edge of poultry nutrition science.
        """)

    with st.expander("Hamad Al-Khudor (CMO) :loudspeaker:"):
        st.write("""
        - Develops and executes branding and marketing strategies.
        - Identifies emerging markets and cultivates customer relationships.
        - Communicates product value propositions to stakeholders, ensuring brand recognition.
        """)

    with st.expander("Abdullah Abul (COO) :gear:"):
        st.write("""
        - Oversees daily operations, ensuring products meet quality and efficiency benchmarks.
        - Coordinates logistics, inventory management, and supply chain optimization.
        - Maintains seamless inter-departmental communication.
        """)

    # Placeholder for team members
    team_members = df[df["names"].str.contains("Team Member")]
    for _, row in team_members.iterrows():
        with st.expander(f"{row['names']}"):
            st.write(row["roles"])

    st.markdown("### Organizational Philosophy")
    st.write("""
    At **Doodz**, we believe in a fluid, interconnected structure that promotes innovation,
    rapid decision-making, and a collaborative spirit. Our hierarchy is not just about 
    titles—it's about synergy, shared goals, and pushing boundaries.
    """)

