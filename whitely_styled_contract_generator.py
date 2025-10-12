#!/usr/bin/env python3
"""
WaterWizard Styled Contract Generator
Creates professional contract with blue headers and table formatting
Matching the Lighting Estimate style
"""

import uno
from com.sun.star.beans import PropertyValue
from com.sun.star.text.ControlCharacter import PARAGRAPH_BREAK
from com.sun.star.table import BorderLine2
from com.sun.star.table.BorderLineStyle import SOLID
import subprocess
import time
import sys

# Start LibreOffice in headless mode if not already running
try:
    subprocess.Popen([
        'libreoffice', '--headless',
        '--accept=socket,host=localhost,port=2002;urp;',
        '--nofirststartwizard'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)
except:
    pass

# Connect to LibreOffice
local_context = uno.getComponentContext()
resolver = local_context.ServiceManager.createInstanceWithContext(
    "com.sun.star.bridge.UnoUrlResolver", local_context
)

try:
    context = resolver.resolve(
        "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext"
    )
    desktop = context.ServiceManager.createInstanceWithContext(
        "com.sun.star.frame.Desktop", context
    )
    print("✅ Connected to LibreOffice")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    sys.exit(1)

# Create new document
doc = desktop.loadComponentFromURL("private:factory/swriter", "_blank", 0, ())
text = doc.Text
cursor = text.createTextCursor()

# Helper function to set paragraph style
def set_para_style(cursor, font_name="Liberation Sans", font_size=11, bold=False, color=0x000000):
    cursor.ParaAdjust = 0  # LEFT align
    cursor.CharFontName = font_name
    cursor.CharHeight = font_size
    cursor.CharWeight = 150 if bold else 100
    cursor.CharColor = color

# Helper function for blue heading
def add_blue_heading(text, cursor, heading_text, size=16):
    text.insertString(cursor, heading_text, False)
    cursor.goLeft(len(heading_text), True)  # Select text
    cursor.CharFontName = "Liberation Sans"
    cursor.CharHeight = size
    cursor.CharWeight = 150  # Bold
    cursor.CharColor = 0x4472C4  # Blue color like in Lighting Estimate
    cursor.collapseToEnd()
    text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

# Title
add_blue_heading(text, cursor, "French Drain Installation Contract", 18)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

# Client info section
set_para_style(cursor)
text.insertString(cursor, "Prepared for: ", False)
cursor.goLeft(14, True)
cursor.CharWeight = 150
cursor.collapseToEnd()
text.insertString(cursor, "Daniel & Elin Whitely", False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

text.insertString(cursor, "Project Address: 9005 Mt Lassen Ave, Vancouver, WA 98664", False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertString(cursor, "Contract Date: October 7, 2025", False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

# Scope of Work
add_blue_heading(text, cursor, "Scope of Work", 14)
set_para_style(cursor)
scope_text = """Contractor excavates 9"x9" trench, running approximately 20' from east to west on northern boundary of backyard, and 23' from north to south. Contractor perforates concrete housing of drainage junction, installs French drain with 1.5" drain rock and 3" ADS, draining into existing drainage junction. Contractor disposes of excavation tailings.

Steel edging installation included per customer selection."""
text.insertString(cursor, scope_text, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

# Materials section with table
add_blue_heading(text, cursor, "Materials", 14)

# Create materials table
table = doc.createInstance("com.sun.star.text.TextTable")
table.initialize(7, 4)  # 7 rows (header + 5 items + subtotal), 4 columns
text.insertTextContent(cursor, table, False)

# Note: Column widths will be auto-adjusted by LibreOffice

# Header row
headers = ["Description", "Unit Cost", "Quantity", "Sub-total"]
for i, header in enumerate(headers):
    cell = table.getCellByPosition(i, 0)
    cell_cursor = cell.createTextCursor()
    cell_cursor.CharWeight = 150
    cell_cursor.CharFontName = "Liberation Sans"
    cell.insertString(cell_cursor, header, False)

# Data rows
materials_data = [
    ("1.5\" drain rock", "$55", "2 yard", "$110.00"),
    ("3\" ADS Corrugated, perforated drain pipe", "$2", "43 lf", "$86.00"),
    ("3\" ADS Tee", "$15", "1 each", "$15.00"),
    ("Weed Barrier, Hanes silver, spun", "$0.75", "43 sf", "$32.25"),
    ("Staples", "$0.15", "43 each", "$6.45")
]

for row_idx, row_data in enumerate(materials_data, start=1):
    for col_idx, cell_data in enumerate(row_data):
        cell = table.getCellByPosition(col_idx, row_idx)
        cell_cursor = cell.createTextCursor()
        cell.insertString(cell_cursor, cell_data, False)

# Subtotal row
cell = table.getCellByPosition(0, 6)
cell_cursor = cell.createTextCursor()
cell_cursor.CharWeight = 150
cell.insertString(cell_cursor, "Material Sub-total", False)

cell = table.getCellByPosition(3, 6)
cell_cursor = cell.createTextCursor()
cell_cursor.CharWeight = 150
cell.insertString(cell_cursor, "$249.70", False)

text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

# Equipment section
add_blue_heading(text, cursor, "Equipment", 14)
set_para_style(cursor)
text.insertString(cursor, "Truck Fee", False)
cursor.goLeft(9, False)
text.insertString(cursor, "\t\t\t$120.00", False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

# Labor section (similar table structure)
add_blue_heading(text, cursor, "Labor", 14)

labor_table = doc.createInstance("com.sun.star.text.TextTable")
labor_table.initialize(8, 4)
text.insertTextContent(cursor, labor_table, False)

# Labor header
labor_headers = ["Description", "Rate", "Hours", "Sub-total"]
for i, header in enumerate(labor_headers):
    cell = labor_table.getCellByPosition(i, 0)
    cell_cursor = cell.createTextCursor()
    cell_cursor.CharWeight = 150
    cell.insertString(cell_cursor, header, False)

# Labor data
labor_data = [
    ("Excavate drainage trench", "$72", "4.3", "$309.60"),
    ("Dispose excavation tailings", "$72", "2.5", "$180.00"),
    ("Haul drain rock", "$72", "1.0", "$72.00"),
    ("Place drain rock", "$72", "1.72", "$123.84"),
    ("Lay, staple fabric, assemble ADS", "$85", "0.65", "$54.83"),
    ("Drill through concrete drainage housing", "$85", "1.0", "$85.00")
]

for row_idx, row_data in enumerate(labor_data, start=1):
    for col_idx, cell_data in enumerate(row_data):
        cell = labor_table.getCellByPosition(col_idx, row_idx)
        cell_cursor = cell.createTextCursor()
        cell.insertString(cell_cursor, cell_data, False)

# Labor subtotal
cell = labor_table.getCellByPosition(0, 7)
cell_cursor = cell.createTextCursor()
cell_cursor.CharWeight = 150
cell.insertString(cell_cursor, "Labor Sub-total", False)

cell = labor_table.getCellByPosition(3, 7)
cell_cursor = cell.createTextCursor()
cell_cursor.CharWeight = 150
cell.insertString(cell_cursor, "$825.27", False)

text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

# Steel Edging section
add_blue_heading(text, cursor, "Steel Edging (Selected by Customer)", 14)

edging_table = doc.createInstance("com.sun.star.text.TextTable")
edging_table.initialize(5, 4)
text.insertTextContent(cursor, edging_table, False)

# Edging header
for i, header in enumerate(["Description", "Unit Cost", "Quantity", "Sub-total"]):
    cell = edging_table.getCellByPosition(i, 0)
    cell_cursor = cell.createTextCursor()
    cell_cursor.CharWeight = 150
    cell.insertString(cell_cursor, header, False)

# Edging data
edging_data = [
    ("Border Concepts flex steel, black, 13 gauge, 10'", "$26", "6 each", "$156.00"),
    ("Steel stakes, black", "$3", "22 each", "$64.80"),
    ("Labor: Install steel edging", "$85/hr", "3.0", "$255.00")
]

for row_idx, row_data in enumerate(edging_data, start=1):
    for col_idx, cell_data in enumerate(row_data):
        cell = edging_table.getCellByPosition(col_idx, row_idx)
        cell_cursor = cell.createTextCursor()
        cell.insertString(cell_cursor, cell_data, False)

# Edging subtotal
cell = edging_table.getCellByPosition(0, 4)
cell_cursor = cell.createTextCursor()
cell_cursor.CharWeight = 150
cell.insertString(cell_cursor, "Edging Sub-total", False)

cell = edging_table.getCellByPosition(3, 4)
cell_cursor = cell.createTextCursor()
cell_cursor.CharWeight = 150
cell.insertString(cell_cursor, "$475.80", False)

text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

# Project Totals
add_blue_heading(text, cursor, "Project Totals", 14)
set_para_style(cursor, font_size=12)

totals_text = """Subtotal: $1,670.77
Sales Tax (8.7%): $145.36"""
text.insertString(cursor, totals_text, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

# Total (bold and larger)
text.insertString(cursor, "TOTAL: $1,816.13", False)
cursor.goLeft(16, True)
cursor.CharWeight = 150
cursor.CharHeight = 14
cursor.collapseToEnd()
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

# Payment Terms
add_blue_heading(text, cursor, "Payment Terms", 14)
set_para_style(cursor)
payment_text = """• 50% deposit ($908.07) required to schedule work
• Balance due upon completion
• Contract valid for 30 days from date above"""
text.insertString(cursor, payment_text, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

# Terms & Conditions
add_blue_heading(text, cursor, "Terms & Conditions", 14)
set_para_style(cursor)
terms_text = """• Work schedule subject to weather conditions
• Customer responsible for marking underground utilities (call 811 before work begins)
• Changes to scope of work require written authorization and may affect pricing
• Contractor not responsible for damage to unmarked utilities or existing irrigation lines
• Customer grants access to property during project duration"""
text.insertString(cursor, terms_text, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

# Contractor info
set_para_style(cursor)
text.insertString(cursor, "Contractor: WaterWizard Landscaping", False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertString(cursor, "Phone: (503) 555-1234", False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertString(cursor, "Email: info@waterwizard.com", False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

# Signature lines
text.insertString(cursor, "_" * 40 + "\t" + "_" * 20, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertString(cursor, "Client Signature\t\t\tDate", False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertString(cursor, "_" * 40 + "\t" + "_" * 20, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertString(cursor, "Contractor Signature\t\t\tDate", False)

# Save document
output_path = "/home/johnny5/Downloads/Whitely_Drainage_Contract.odt"
file_url = "file://" + output_path

store_props = (PropertyValue("FilterName", 0, "writer8", 0),)
doc.storeAsURL(file_url, store_props)

print(f"✅ Contract saved to: {output_path}")

# Export to PDF
pdf_path = "/home/johnny5/Downloads/Whitely_Drainage_Contract.pdf"
pdf_url = "file://" + pdf_path
pdf_props = (PropertyValue("FilterName", 0, "writer_pdf_Export", 0),)
doc.storeToURL(pdf_url, pdf_props)

print(f"✅ PDF exported to: {pdf_path}")
print("\n📊 Contract Summary:")
print("   Client: Daniel & Elin Whitely")
print("   Total: $1,816.13 (includes steel edging)")
print("   Deposit: $908.07")
