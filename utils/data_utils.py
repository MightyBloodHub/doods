import pandas as pd
from io import BytesIO

def load_sheets(excel_path):
    try:
        xls = pd.ExcelFile(excel_path)
        sheet_names = xls.sheet_names

        def load_sheet(name):
            return pd.read_excel(excel_path, sheet_name=name) if name in sheet_names else pd.DataFrame()

        feed_df = load_sheet("Feed Consumption")
        weight_df = load_sheet("Weight Measurements")
        health_df = load_sheet("Health Observations")
        cost_df = load_sheet("Cost and Inventory")
        protocol_df = load_sheet("Protocol and Adjustments")
        breakdown_df = load_sheet("Feed Composition Breakdown")  # New sheet

        return feed_df, weight_df, health_df, cost_df, protocol_df, breakdown_df
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame())

def export_to_excel(feed, weight, health, cost, protocol, breakdown):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        if not feed.empty:
            feed.to_excel(writer, sheet_name='Feed Consumption', index=False)
        if not weight.empty:
            weight.to_excel(writer, sheet_name='Weight Measurements', index=False)
        if not health.empty:
            health.to_excel(writer, sheet_name='Health Observations', index=False)
        if not cost.empty:
            cost.to_excel(writer, sheet_name='Cost and Inventory', index=False)
        if not protocol.empty:
            protocol.to_excel(writer, sheet_name='Protocol and Adjustments', index=False)
        if not breakdown.empty:
            breakdown.to_excel(writer, sheet_name='Feed Composition Breakdown', index=False)
    return output.getvalue()
