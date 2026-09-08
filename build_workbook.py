"""
Builds Sales_Analysis.xlsx — a Raw Data sheet of synthetic transactions plus
a Dashboard sheet that summarizes it with live formulas (SUMIFS/AVERAGEIFS)
and two charts (monthly revenue trend, category breakdown).
"""
import random
from datetime import date, timedelta
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.utils import get_column_letter

random.seed(42)

PRODUCTS = {
    "Wireless Earbuds": ("Electronics", 1899),
    "Smart Watch": ("Electronics", 3499),
    "Bluetooth Speaker": ("Electronics", 1499),
    "Cotton T-Shirt": ("Apparel", 499),
    "Denim Jacket": ("Apparel", 2299),
    "Running Shoes": ("Apparel", 2799),
    "Non-stick Pan Set": ("Home & Kitchen", 1699),
    "LED Desk Lamp": ("Home & Kitchen", 899),
    "Ceramic Mug Set": ("Home & Kitchen", 599),
    "Face Serum": ("Beauty", 799),
    "Herbal Shampoo": ("Beauty", 349),
    "Basmati Rice 5kg": ("Grocery", 649),
    "Cold Pressed Oil 1L": ("Grocery", 399),
}
REGIONS = ["North", "South", "East", "West"]
CATEGORIES = ["Electronics", "Apparel", "Home & Kitchen", "Beauty", "Grocery"]

START = date(2026, 1, 1)
DAYS = 181  # Jan 1 - Jun 30 2026

rows = []
current = START
while current <= START + timedelta(days=DAYS - 1):
    n_orders = random.randint(1, 4)
    for _ in range(n_orders):
        product = random.choice(list(PRODUCTS.keys()))
        category, base_price = PRODUCTS[product]
        price = round(base_price * random.uniform(0.92, 1.08))
        units = random.randint(1, 5)
        region = random.choice(REGIONS)
        rows.append([current, product, category, region, units, price])
    current += timedelta(days=1)

# ---------- Workbook ----------
wb = Workbook()

# ---- Raw Data sheet ----
raw = wb.active
raw.title = "Raw Data"
headers = ["Date", "Product", "Category", "Region", "Units", "Unit Price (INR)", "Revenue (INR)", "Month"]
header_fill = PatternFill("solid", fgColor="1C1712")
header_font = Font(color="E9E2D2", bold=True, name="Arial")

for col, h in enumerate(headers, start=1):
    c = raw.cell(row=1, column=col, value=h)
    c.font = header_font
    c.fill = header_fill
    c.alignment = Alignment(horizontal="center")

for i, r in enumerate(rows, start=2):
    raw.cell(row=i, column=1, value=r[0]).number_format = "yyyy-mm-dd"
    raw.cell(row=i, column=2, value=r[1])
    raw.cell(row=i, column=3, value=r[2])
    raw.cell(row=i, column=4, value=r[3])
    raw.cell(row=i, column=5, value=r[4])
    raw.cell(row=i, column=6, value=r[5]).number_format = "#,##0"
    # Revenue as a live formula, never a hardcoded number
    raw.cell(row=i, column=7, value=f"=E{i}*F{i}").number_format = "#,##0"
    # Month helper column, used by Dashboard SUMIFS
    raw.cell(row=i, column=8, value=f'=TEXT(A{i},"mmm-yy")')

last_row = len(rows) + 1
col_widths = [12, 20, 16, 10, 8, 16, 14, 10]
for i, w in enumerate(col_widths, start=1):
    raw.column_dimensions[get_column_letter(i)].width = w
raw.freeze_panes = "A2"

# ---- Dashboard sheet ----
dash = wb.create_sheet("Dashboard")
dash.sheet_view.showGridLines = False

title_font = Font(name="Arial", size=18, bold=True, color="1C1712")
label_font = Font(name="Arial", size=10, color="4A423A")
value_font = Font(name="Arial", size=20, bold=True, color="B85C1E")
section_font = Font(name="Arial", size=13, bold=True, color="1C1712")
table_header_font = Font(name="Arial", bold=True, color="FFFFFF")
table_header_fill = PatternFill("solid", fgColor="3E4A38")
thin = Side(style="thin", color="D9D2C2")
border = Border(left=thin, right=thin, top=thin, bottom=thin)

dash["B2"] = "Sales Performance Dashboard"
dash["B2"].font = title_font
dash["B3"] = "Jan – Jun 2026  ·  Source: Raw Data sheet (live formulas)"
dash["B3"].font = label_font

# KPI cards
kpis = [
    ("Total Revenue (INR)", f"=SUM('Raw Data'!G2:G{last_row})", "#,##0"),
    ("Total Units Sold", f"=SUM('Raw Data'!E2:E{last_row})", "#,##0"),
    ("Total Orders", f"=COUNTA('Raw Data'!A2:A{last_row})", "#,##0"),
    ("Avg Order Value (INR)", f"=SUM('Raw Data'!G2:G{last_row})/COUNTA('Raw Data'!A2:A{last_row})", "#,##0"),
]
kpi_col_start = 2
for i, (label, formula, fmt) in enumerate(kpis):
    col = kpi_col_start + i * 2
    letter = get_column_letter(col)
    dash.merge_cells(f"{letter}5:{get_column_letter(col+1)}5")
    dash.merge_cells(f"{letter}6:{get_column_letter(col+1)}7")
    dash[f"{letter}5"] = label
    dash[f"{letter}5"].font = label_font
    dash[f"{letter}6"] = formula
    dash[f"{letter}6"].font = value_font
    dash[f"{letter}6"].number_format = fmt

# Category breakdown table (SUMIF)
dash["B10"] = "Revenue by Category"
dash["B10"].font = section_font
cat_headers = ["Category", "Revenue (INR)", "Units Sold"]
for j, h in enumerate(cat_headers):
    c = dash.cell(row=11, column=2 + j, value=h)
    c.font = table_header_font
    c.fill = table_header_fill
    c.border = border
for i, cat in enumerate(CATEGORIES, start=12):
    dash.cell(row=i, column=2, value=cat).border = border
    f_rev = f"=SUMIF('Raw Data'!$C$2:$C${last_row},B{i},'Raw Data'!$G$2:$G${last_row})"
    f_units = f"=SUMIF('Raw Data'!$C$2:$C${last_row},B{i},'Raw Data'!$E$2:$E${last_row})"
    dash.cell(row=i, column=3, value=f_rev).number_format = "#,##0"
    dash.cell(row=i, column=3).border = border
    dash.cell(row=i, column=4, value=f_units).number_format = "#,##0"
    dash.cell(row=i, column=4).border = border

# Region breakdown table (SUMIF)
region_start_row = 11
dash["F10"] = "Revenue by Region"
dash["F10"].font = section_font
reg_headers = ["Region", "Revenue (INR)"]
for j, h in enumerate(reg_headers):
    c = dash.cell(row=11, column=6 + j, value=h)
    c.font = table_header_font
    c.fill = table_header_fill
    c.border = border
for i, reg in enumerate(REGIONS, start=12):
    dash.cell(row=i, column=6, value=reg).border = border
    f_rev = f"=SUMIF('Raw Data'!$D$2:$D${last_row},F{i},'Raw Data'!$G$2:$G${last_row})"
    dash.cell(row=i, column=7, value=f_rev).number_format = "#,##0"
    dash.cell(row=i, column=7).border = border

# Monthly revenue table (SUMIF using Month helper column)
months = sorted({r[0].strftime("%b-%y") for r in rows},
                key=lambda m: (int(m.split("-")[1]), ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"].index(m.split("-")[0])))
dash["B19"] = "Monthly Revenue Trend"
dash["B19"].font = section_font
dash.cell(row=20, column=2, value="Month").font = table_header_font
dash.cell(row=20, column=2).fill = table_header_fill
dash.cell(row=20, column=2).border = border
dash.cell(row=20, column=3, value="Revenue (INR)").font = table_header_font
dash.cell(row=20, column=3).fill = table_header_fill
dash.cell(row=20, column=3).border = border
for i, m in enumerate(months, start=21):
    dash.cell(row=i, column=2, value=m).border = border
    f_rev = f"=SUMIF('Raw Data'!$H$2:$H${last_row},B{i},'Raw Data'!$G$2:$G${last_row})"
    dash.cell(row=i, column=3, value=f_rev).number_format = "#,##0"
    dash.cell(row=i, column=3).border = border

month_last_row = 20 + len(months)

# Top 5 products by revenue - helper columns off to the side, using formulas
dash["F19"] = "Top Products by Revenue"
dash["F19"].font = section_font
dash.cell(row=20, column=6, value="Product").font = table_header_font
dash.cell(row=20, column=6).fill = table_header_fill
dash.cell(row=20, column=6).border = border
dash.cell(row=20, column=7, value="Revenue (INR)").font = table_header_font
dash.cell(row=20, column=7).fill = table_header_fill
dash.cell(row=20, column=7).border = border

products = list(PRODUCTS.keys())
# Put a helper table (hidden-ish, far right) computing SUMIF per product, then rank with LARGE/INDEX/MATCH
helper_col = 12  # column L
dash.cell(row=1, column=helper_col, value="Product").font = label_font
dash.cell(row=1, column=helper_col + 1, value="Revenue").font = label_font
for i, p in enumerate(products, start=2):
    dash.cell(row=i, column=helper_col, value=p)
    f_rev = f"=SUMIF('Raw Data'!$B$2:$B${last_row},{get_column_letter(helper_col)}{i},'Raw Data'!$G$2:$G${last_row})"
    dash.cell(row=i, column=helper_col + 1, value=f_rev).number_format = "#,##0"
helper_last = 1 + len(products)
helper_rev_range = f"${get_column_letter(helper_col+1)}$2:${get_column_letter(helper_col+1)}${helper_last}"
helper_name_range = f"${get_column_letter(helper_col)}$2:${get_column_letter(helper_col)}${helper_last}"

for i in range(5):
    row = 21 + i
    rank_formula = f"=LARGE({helper_rev_range},{i+1})"
    dash.cell(row=row, column=7, value=rank_formula).number_format = "#,##0"
    dash.cell(row=row, column=7).border = border
    name_formula = f"=INDEX({helper_name_range},MATCH(G{row},{helper_rev_range},0))"
    dash.cell(row=row, column=6, value=name_formula).border = border

# column widths for dashboard
for col, w in zip("BCDEFGHIJKL", [20, 16, 14, 4, 20, 16, 4, 4, 4, 4, 22]):
    dash.column_dimensions[col].width = w

# ---- Charts ----
bar = BarChart()
bar.title = "Monthly Revenue (INR)"
bar.y_axis.title = "Revenue (INR)"
bar.style = 10
data = Reference(dash, min_col=3, min_row=20, max_row=month_last_row)
cats = Reference(dash, min_col=2, min_row=21, max_row=month_last_row)
bar.add_data(data, titles_from_data=True)
bar.set_categories(cats)
bar.width = 16
bar.height = 8
dash.add_chart(bar, "B27")

pie = PieChart()
pie.title = "Revenue Share by Category"
pie_data = Reference(dash, min_col=3, min_row=11, max_row=11 + len(CATEGORIES))
pie_cats = Reference(dash, min_col=2, min_row=12, max_row=11 + len(CATEGORIES))
pie.add_data(pie_data, titles_from_data=True)
pie.set_categories(pie_cats)
pie.width = 13
pie.height = 8
dash.add_chart(pie, "F27")

wb.save("Sales_Analysis.xlsx")
print(f"Workbook built with {len(rows)} transactions across {len(months)} months.")
