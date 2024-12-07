from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
import datetime

# Helper Functions
def style_headers(sheet, header_cells):
    """Apply bold, centered formatting to header cells and freeze panes."""
    for cell in header_cells:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.fill = PatternFill(start_color="DDDDDD", fill_type="solid")
    # Freeze top two rows (headers + instructions)
    sheet.freeze_panes = sheet['A3']

def auto_adjust_column_widths(sheet):
    """Auto-adjust column widths based on cell contents."""
    for col in sheet.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            val = str(cell.value) if cell.value is not None else ""
            if len(val) > max_length:
                max_length = len(val)
        adjusted_width = max_length + 4
        sheet.column_dimensions[column].width = adjusted_width

def add_instructions_row(sheet, instructions_list):
    """Add a row of instructions below the headers to clarify data entry."""
    for col_num, instr in enumerate(instructions_list, start=1):
        cell = sheet.cell(row=2, column=col_num, value=instr)
        cell.font = Font(italic=True, color="555555")
        cell.alignment = Alignment(wrap_text=True, vertical='top')

# Initialize Workbook
wb = Workbook()
if "Sheet" in wb.sheetnames:
    wb.remove(wb["Sheet"])

# 0. Instructions Sheet
instructions_sheet = wb.create_sheet("Instructions")
instructions_sheet["A1"] = "How to Use This Workbook"
instructions_sheet["A1"].font = Font(bold=True, size=14)
instructions_content = [
    "This workbook is a sample filled with dummy data for a BSFL poultry feed experiment.",
    "",
    "Sheets and Their Purposes:",
    "- Feed Consumption: Daily feed offered, refused, and consumed for each group.",
    "- Weight Measurements: Weekly weights of sampled birds and calculations of average and gain.",
    "- Health Observations: Records of illnesses, mortalities, and actions taken.",
    "- Cost and Inventory: Records of ingredient costs, quantities purchased, and suppliers.",
    "- Protocol and Adjustments: Details of the experiment setup, any changes proposed, and approval status.",
    "",
    "These dummy data entries simulate a scenario about 4 weeks into a 45-day experiment.",
    "You can modify these values, add formulas, or manipulate the data to run simulations."
]

for i, line in enumerate(instructions_content, start=2):
    instructions_sheet.cell(row=i, column=1, value=line)

auto_adjust_column_widths(instructions_sheet)

# 1. Feed Consumption Sheet
feed_sheet = wb.create_sheet("Feed Consumption")
feed_headers = [
    "Date (YYYY-MM-DD)", 
    "Group (Control/25% BSFL/35% BSFL)", 
    "Type of Feed (BSFL/Soy/Mix)", 
    "Amount Offered (kg)",
    "Amount Refused (kg)", 
    "Total Consumed (kg) [=Offered - Refused]", 
    "Notes"
]
feed_instructions = [
    "Enter the date of feeding.",
    "Enter the group name or ID.",
    "Specify the feed type or ratio.",
    "Amount of feed offered.",
    "Amount of feed not consumed by next feeding.",
    "Formula: Offered - Refused.",
    "Any observations (e.g., feed spillage, weather effects)."
]

for col_num, header in enumerate(feed_headers, start=1):
    feed_sheet.cell(row=1, column=col_num, value=header)
add_instructions_row(feed_sheet, feed_instructions)
style_headers(feed_sheet, feed_sheet[1])

# Populate dummy feed data (assume about 2 weeks of daily data for 3 groups)
start_date = datetime.date(2024, 12, 1)
days_of_data = 14
feed_types = {
    "Control": "Soy-based",
    "25% BSFL": "25% BSFL + Soy",
    "35% BSFL": "35% BSFL + Soy"
}
row_index = 3
for i in range(days_of_data):
    current_date = start_date + datetime.timedelta(days=i)
    for group in ["Control", "25% BSFL", "35% BSFL"]:
        offered = 5.0  # 5 kg offered
        refused = round((i % 3) * 0.2, 2)  # some variation in refused feed
        feed_sheet.cell(row=row_index, column=1, value=current_date.isoformat())
        feed_sheet.cell(row=row_index, column=2, value=group)
        feed_sheet.cell(row=row_index, column=3, value=feed_types[group])
        feed_sheet.cell(row=row_index, column=4, value=offered)
        feed_sheet.cell(row=row_index, column=5, value=refused)
        feed_sheet.cell(row=row_index, column=6, value=f"=D{row_index}-E{row_index}")
        note = "Normal feeding" if refused < 0.5 else "Slightly higher refusal today"
        feed_sheet.cell(row=row_index, column=7, value=note)
        row_index += 1

auto_adjust_column_widths(feed_sheet)

# 2. Weight Measurements Sheet
weight_sheet = wb.create_sheet("Weight Measurements")
weight_headers = [
    "Date (YYYY-MM-DD)", "Group", "Bird ID", "Weight (g)",
    "Average Weight (Group)", "Cumulative Gain (g)", "Notes"
]
weight_instructions = [
    "Enter the date of weighing.",
    "Group name or ID.",
    "Unique Bird ID.",
    "Bird weight in grams.",
    "After entering all birds for that date and group, calculate group average.",
    "Weight gain since start or last measurement.",
    "Any relevant notes."
]

for col_num, header in enumerate(weight_headers, start=1):
    weight_sheet.cell(row=1, column=col_num, value=header)
add_instructions_row(weight_sheet, weight_instructions)
style_headers(weight_sheet, weight_sheet[1])

# Dummy weight data: Weekly weigh-ins (every 7 days)
weigh_dates = [start_date + datetime.timedelta(days=x) for x in [7, 14, 21, 28]]
bird_ids = [f"Bird_{i:02d}" for i in range(1,11)]  # 10 birds per group
row_index = 3
initial_weights = {"Control": 200, "25% BSFL": 205, "35% BSFL": 210}  # starting weights after first week
growth_per_week = {"Control": 100, "25% BSFL": 110, "35% BSFL": 115}  # incremental growth for simulation

for w_date in weigh_dates:
    for group in ["Control", "25% BSFL", "35% BSFL"]:
        # Simulate weights
        # Weeks since start:
        weeks_elapsed = (w_date - start_date).days // 7
        base_weight = initial_weights[group] + growth_per_week[group]*weeks_elapsed
        weights = [base_weight + (j * 2) for j in range(len(bird_ids))]  # slight variation among birds
        avg_weight_cell = None
        sum_weights = sum(weights)
        avg_weight = sum_weights / len(weights)
        
        for idx, bird in enumerate(bird_ids):
            weight_sheet.cell(row=row_index, column=1, value=w_date.isoformat())
            weight_sheet.cell(row=row_index, column=2, value=group)
            weight_sheet.cell(row=row_index, column=3, value=bird)
            weight_sheet.cell(row=row_index, column=4, value=weights[idx])
            # We'll put the average only on the last bird row for clarity
            notes = "Healthy" if idx % 5 != 0 else "Slight ruffle on feathers"
            if idx == len(bird_ids)-1:
                weight_sheet.cell(row=row_index, column=5, value=avg_weight)
                # Cumulative gain from initial weight (assuming first weigh date is week 1)
                cumulative_gain = avg_weight - initial_weights[group]
                weight_sheet.cell(row=row_index, column=6, value=cumulative_gain)
            weight_sheet.cell(row=row_index, column=7, value=notes)
            row_index += 1

auto_adjust_column_widths(weight_sheet)

# 3. Health Observations Sheet
health_sheet = wb.create_sheet("Health Observations")
health_headers = [
    "Date (YYYY-MM-DD)", "Group", "Bird ID (if applicable)", "Observation Type (Illness/Mortality/Behavior)",
    "Description of Issue", "Action Taken", "Outcome", "Notes"
]
health_instructions = [
    "Date of observation.",
    "Affected group.",
    "If individual bird, record ID; otherwise leave blank.",
    "Type of issue: Illness, Mortality, Behavior.",
    "Description of the issue.",
    "Action taken (treatment, isolation, etc.).",
    "Outcome or follow-up.",
    "Additional notes."
]

for col_num, header in enumerate(health_headers, start=1):
    health_sheet.cell(row=1, column=col_num, value=header)
add_instructions_row(health_sheet, health_instructions)
style_headers(health_sheet, health_sheet[1])

# Dummy health events
health_data = [
    [start_date + datetime.timedelta(days=5), "25% BSFL", "Bird_03", "Illness", "Lethargic, reduced feed intake",
     "Isolated, administered electrolytes", "Monitoring - slightly improved next day", "Mild symptoms"],
    [start_date + datetime.timedelta(days=10), "35% BSFL", "", "Mortality", "One bird found dead in morning",
     "Removed, sent for necropsy", "Awaiting results", "No other birds affected"],
    [start_date + datetime.timedelta(days=12), "Control", "Bird_07", "Behavior",
     "Observed pecking at feathers", "Separated from group temporarily", "Behavior improved after a day",
     "Potential stress or boredom"]
]

row_index = 3
for event in health_data:
    for col_num, value in enumerate(event, start=1):
        if isinstance(value, datetime.date):
            health_sheet.cell(row=row_index, column=col_num, value=value.isoformat())
        else:
            health_sheet.cell(row=row_index, column=col_num, value=value)
    row_index += 1

auto_adjust_column_widths(health_sheet)

# 4. Cost and Inventory Sheet
cost_sheet = wb.create_sheet("Cost and Inventory")
cost_headers = [
    "Item/Ingredient", "Type (Soy/BSFL/Other)", "Unit Cost (KWD/ton)",
    "Quantity Purchased (kg)", "Total Cost (KWD) [=(Unit Cost/1000)*Quantity]", "Date of Purchase", "Supplier", "Notes"
]
cost_instructions = [
    "Name of the ingredient or item.",
    "Type/category (Soy, BSFL, etc.).",
    "Cost per ton (1,000 kg).",
    "Quantity in kg purchased.",
    "Formula: (Unit Cost/1000)*Quantity.",
    "Purchase date.",
    "Supplier name.",
    "Any extra notes."
]

for col_num, header in enumerate(cost_headers, start=1):
    cost_sheet.cell(row=1, column=col_num, value=header)
add_instructions_row(cost_sheet, cost_instructions)
style_headers(cost_sheet, cost_sheet[1])

# Dummy cost entries
cost_data = [
    ["BSFL Meal Batch #1", "BSFL", 120, 200, "=C3/1000*D3", "2024-12-01", "InsectFarm Co.", "Good quality, prompt delivery"],
    ["Soy Meal Lot A", "Soy", 230, 300, "=C4/1000*D4", "2024-12-02", "AgroSupplies", "Standard grade"],
    ["Vitamins & Minerals Mix", "Other", 500, 20, "=C5/1000*D5", "2024-12-05", "NutriAdditives", "High quality supplement"],
    ["BSFL Meal Batch #2", "BSFL", 118, 200, "=C6/1000*D6", "2024-12-10", "InsectFarm Co.", "Slightly discounted price"]
]

row_index = 3
for entry in cost_data:
    for col_num, value in enumerate(entry, start=1):
        cost_sheet.cell(row=row_index, column=col_num, value=value)
    row_index += 1

auto_adjust_column_widths(cost_sheet)

# 5. Protocol and Adjustments Sheet
protocol_sheet = wb.create_sheet("Protocol and Adjustments")
protocol_headers = [
    "Parameter/Aspect", "Details/Instructions", "Proposed Changes", "Approval Status", "Notes"
]
protocol_instructions = [
    "Parameter or aspect of the experiment.",
    "Current instructions or set conditions.",
    "Proposed changes for improvement.",
    "Approval status: Approved, Pending, or Rejected.",
    "Additional notes or reasoning."
]

for col_num, header in enumerate(protocol_headers, start=1):
    protocol_sheet.cell(row=1, column=col_num, value=header)
add_instructions_row(protocol_sheet, protocol_instructions)
style_headers(protocol_sheet, protocol_sheet[1])

protocol_data = [
    ["Experiment Duration", "45 days total from day-old chicks", "", "Approved", ""],
    ["Feed Ratios", "Control: 0% BSFL, G1: 25% BSFL, G2: 35% BSFL", "Increase G2 to 40% if growth is superior", "Pending", "Await week 4 data"],
    ["Weighing Schedule", "Weigh 10 birds/group weekly + final all-bird weigh at Day 45", "", "Approved", ""],
    ["Health Checks", "Daily observation, prompt isolation of sick birds", "Implement routine fecal tests", "Pending", "Need budget approval"]
]

row_index = 3
for p_line in protocol_data:
    for col_num, value in enumerate(p_line, start=1):
        protocol_sheet.cell(row=row_index, column=col_num, value=value)
    row_index += 1

auto_adjust_column_widths(protocol_sheet)

# Save the workbook
wb.save("BSFL_Experiment_Completed_Dummy_Data.xlsx")
print("Excel workbook created successfully: BSFL_Experiment_Completed_Dummy_Data.xlsx")

