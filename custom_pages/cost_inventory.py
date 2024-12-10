import streamlit as st
import pandas as pd
import plotly.express as px

def show_cost_inventory(cost_df, breakdown_df):
    st.header("Cost and Inventory")

    if cost_df.empty or breakdown_df.empty:
        st.write("Cost or breakdown data not available.")
        return

    st.subheader("Raw Cost Data")
    st.dataframe(cost_df, height=300)

    st.subheader("Feed Composition Breakdown")
    st.dataframe(breakdown_df, height=300)

    # --- Compute Average Ingredient Costs ---
    # We assume each row in cost_df represents a purchase with a given unit cost and quantity.
    # We'll compute a weighted average cost per ingredient type.

    # Convert Unit Cost to cost per ton (KWD/ton) is already given,
    # but we need cost per gram: 1 ton = 1,000,000 g
    # cost_per_gram = (Unit Cost (KWD/ton)) / 1,000,000

    # Group by ingredient to get weighted average cost
    if all(col in cost_df.columns for col in ["Item/Ingredient", "Unit Cost (KWD/ton)", "Quantity (kg)"]):
        cost_df["Quantity (kg)"] = pd.to_numeric(cost_df["Quantity (kg)"], errors="coerce")
        cost_df["Unit Cost (KWD/ton)"] = pd.to_numeric(cost_df["Unit Cost (KWD/ton)"], errors="coerce")

        # Compute weighted average cost per ingredient:
        # Weighted average (Unit Cost) = sum(UnitCost * Quantity) / sum(Quantity)
        # Then convert to cost per gram:
        # 1 ton = 1000 kg, so Unit Cost (KWD/ton) / 1,000,000 = KWD/g
        avg_cost = (
            cost_df.groupby("Item/Ingredient").apply(
                lambda x: (x["Unit Cost (KWD/ton)"] * x["Quantity (kg)"]).sum() / x["Quantity (kg)"].sum()
            )
            .reset_index(name="Avg Unit Cost (KWD/ton)")
        )

        # Map these average costs to ingredients (BSF, Soy, Carbs)
        # We assume:
        # BSF = "BSF Powder"
        # Soy = "Soy Meal"
        # Carbs = "Corn Mix"
        ingredient_map = {
            "BSF Powder": "BSF",
            "Soy Meal": "Soy",
            "Corn Mix": "Carbs"
        }

        # Filter only known ingredients
        avg_cost = avg_cost[avg_cost["Item/Ingredient"].isin(ingredient_map.keys())]

        # Convert to cost per gram
        avg_cost["Cost (KWD/g)"] = avg_cost["Avg Unit Cost (KWD/ton)"] / 1_000_000

        # Create a dict for easy lookup:
        cost_per_gram = dict(
            zip(
                avg_cost["Item/Ingredient"].map(ingredient_map),
                avg_cost["Cost (KWD/g)"]
            )
        )

        # Check if we have all three ingredients:
        if all(ing in cost_per_gram for ing in ["BSF", "Soy", "Carbs"]):
            # --- Compute Total Feed Cost per Row in Breakdown ---
            breakdown_df["Total Feed Cost (KWD)"] = (
                breakdown_df["BSF Consumed (g)"] * cost_per_gram["BSF"] +
                breakdown_df["Soy Consumed (g)"] * cost_per_gram["Soy"] +
                breakdown_df["Carbs Consumed (g)"] * cost_per_gram["Carbs"]
            )

            # --- Aggregate Costs by Group ---
            cost_by_group = breakdown_df.groupby("Group")["Total Feed Cost (KWD)"].sum().reset_index()
            st.subheader("Total Feed Cost by Group")
            st.dataframe(cost_by_group)

            fig_group_cost = px.bar(
                cost_by_group,
                x="Group",
                y="Total Feed Cost (KWD)",
                title="Total Feed Cost by Group",
                text_auto=True,
                color="Group"
            )
            st.plotly_chart(fig_group_cost, use_container_width=True)

            # --- Detailed Ingredient Cost per Group ---
            # Compute sum of each ingredient cost per group
            breakdown_df["BSF Cost (KWD)"] = breakdown_df["BSF Consumed (g)"] * cost_per_gram["BSF"]
            breakdown_df["Soy Cost (KWD)"] = breakdown_df["Soy Consumed (g)"] * cost_per_gram["Soy"]
            breakdown_df["Carbs Cost (KWD)"] = breakdown_df["Carbs Consumed (g)"] * cost_per_gram["Carbs"]

            ingredient_costs = breakdown_df.groupby("Group")[["BSF Cost (KWD)", "Soy Cost (KWD)", "Carbs Cost (KWD)"]].sum().reset_index()

            st.subheader("Ingredient-Level Feed Costs per Group")
            st.dataframe(ingredient_costs)

            # Melt for stacked bar chart visualization
            cost_melted = ingredient_costs.melt(id_vars="Group", var_name="Ingredient", value_name="Cost (KWD)")
            fig_ingredient = px.bar(
                cost_melted,
                x="Group",
                y="Cost (KWD)",
                color="Ingredient",
                title="Ingredient-wise Cost Distribution per Group",
                text_auto=True
            )
            fig_ingredient.update_layout(barmode='stack')
            st.plotly_chart(fig_ingredient, use_container_width=True)

        else:
            st.warning("Not all ingredients have cost data. Please ensure BSF Powder, Soy Meal, and Corn Mix are recorded in Cost and Inventory.")

    else:
        st.warning("Cost and inventory data does not have the necessary columns for computation.")
