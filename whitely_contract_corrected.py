#!/usr/bin/env python3
"""
Corrected Whitely Drainage Contract
Matches original spreadsheet math with steel edging substitution
"""

import uno
from com.sun.star.beans import PropertyValue
from com.sun.star.text.ControlCharacter import PARAGRAPH_BREAK
import subprocess
import time
import sys

# Start LibreOffice headless
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

# Helper function for blue heading
def add_blue_heading(text, cursor, heading_text, size=16):
    text.insertString(cursor, heading_text, False)
    cursor.goLeft(len(heading_text), True)
    cursor.CharFontName = "Liberation Sans"
    cursor.CharHeight = size
    cursor.CharWeight = 150
    cursor.CharColor = 0x4472C4  # Blue
    cursor.collapseToEnd()
    text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

def set_para_style(cursor, font_size=11, bold=False):
    cursor.ParaAdjust = 0
    cursor.CharFontName = "Liberation Sans"
    cursor.CharHeight = font_size
    cursor.CharWeight = 150 if bold else 100
    cursor.CharColor = 0x000000

# Title
add_blue_heading(text, cursor, "French Drain Installation Contract", 18)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

# Client info
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
text.insertString(cursor, 'Contractor excavates 9"x9" trench, running approximately 20\' from east to west on northern boundary of backyard, and 20-25\' from north to south.', False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertString(cursor, 'Contractor perforates concrete housing of drainage junction, installs French drain with 1.5" drain rock and 3" ADS, draining into existing drainage junction.', False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertString(cursor, "Contractor disposes of excavation tailings.", False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertString(cursor, "Border Concepts flex steel edging installation included per customer selection.", False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

# Materials Table
add_blue_heading(text, cursor, "Materials", 14)

materials_table = doc.createInstance("com.sun.star.text.TextTable")
materials_table.initialize(7, 4)
text.insertTextContent(cursor, materials_table, False)

# Headers
headers = ["Description", "Unit Cost", "Quantity", "Sub-total"]
for i, header in enumerate(headers):
    cell = materials_table.getCellByPosition(i, 0)
    cell_cursor = cell.createTextCursor()
    cell_cursor.CharWeight = 150
    cell.insertString(cell_cursor, header, False)

# Data (from original spreadsheet)
materials_data = [
    ('1.5" drain rock', "$55", "1 yard", "$55.00"),
    ('3" ADS Corrugated, perforated drain pipe', "$2", "50 lf", "$100.00"),
    ('3" ADS Tee', "$15", "1 each", "$15.00"),
    ("Weed Barrier, Hanes silver, spun", "$0.75", "50 sf", "$37.50"),
    ("Staples", "$0.15", "50 each", "$7.50")
]

for row_idx, row_data in enumerate(materials_data, start=1):
    for col_idx, cell_data in enumerate(row_data):
        cell = materials_table.getCellByPosition(col_idx, row_idx)
        cell_cursor = cell.createTextCursor()
        cell.insertString(cell_cursor, cell_data, False)

# Materials subtotal
cell = materials_table.getCellByPosition(0, 6)
cell_cursor = cell.createTextCursor()
cell_cursor.CharWeight = 150
cell.insertString(cell_cursor, "Materials Sub-total", False)

cell = materials_table.getCellByPosition(3, 6)
cell_cursor = cell.createTextCursor()
cell_cursor.CharWeight = 150
cell.insertString(cell_cursor, "$215.00", False)

text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

# Labor Table
add_blue_heading(text, cursor, "Labor", 14)

labor_table = doc.createInstance("com.sun.star.text.TextTable")
labor_table.initialize(8, 4)
text.insertTextContent(cursor, labor_table, False)

# Headers
for i, header in enumerate(["Description", "Rate", "Hours", "Sub-total"]):
    cell = labor_table.getCellByPosition(i, 0)
    cell_cursor = cell.createTextCursor()
    cell_cursor.CharWeight = 150
    cell.insertString(cell_cursor, header, False)

# Labor data (from original spreadsheet)
labor_data = [
    ("Excavate drainage trench", "$72", "4.0", "$288.00"),
    ("Dispose excavation tailings", "$72", "2.5", "$180.00"),
    ("Haul drain rock", "$72", "1.0", "$72.00"),
    ("Place drain rock", "$72", "2.0", "$144.00"),
    ("Lay, staple fabric, assemble ADS", "$85", "0.75", "$63.75"),
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
cell.insertString(cell_cursor, "$832.75", False)

text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

# Steel Edging (customer selected - replaces benda-board)
# Calculate steel edging for 60 lf (edging option in original)
add_blue_heading(text, cursor, "Border Concepts Flex Steel Edging (Selected by Customer)", 14)

edging_table = doc.createInstance("com.sun.star.text.TextTable")
edging_table.initialize(5, 4)
text.insertTextContent(cursor, edging_table, False)

# Headers
for i, header in enumerate(["Description", "Unit Cost", "Quantity", "Sub-total"]):
    cell = edging_table.getCellByPosition(i, 0)
    cell_cursor = cell.createTextCursor()
    cell_cursor.CharWeight = 150
    cell.insertString(cell_cursor, header, False)

# Steel edging materials & labor for 60 lf
edging_data = [
    ("Border Concepts flex steel, black, 13 gauge, 10'", "$26", "6 each", "$156.00"),
    ("Steel stakes, black", "$3", "22 each", "$66.00"),
    ("Labor: Install steel edging", "$85/hr", "3.0 hrs", "$255.00")
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
cell.insertString(cell_cursor, "$477.00", False)

text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

# Project Totals
add_blue_heading(text, cursor, "Project Totals", 14)
set_para_style(cursor, font_size=12)

# Base project (materials + labor): $1,047.75
# Edging: $477.00
# Subtotal: $1,524.75
# Tax (8.7%): $132.65
# Total: $1,657.40

text.insertString(cursor, "Subtotal: $1,524.75", False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertString(cursor, "Sales Tax (8.7%): $132.65", False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

text.insertString(cursor, "TOTAL: $1,657.40", False)
cursor.goLeft(16, True)
cursor.CharWeight = 150
cursor.CharHeight = 14
cursor.collapseToEnd()
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

# Payment Terms
add_blue_heading(text, cursor, "Payment Terms", 14)
set_para_style(cursor)
text.insertString(cursor, "• 50% deposit ($828.70) required to schedule work", False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertString(cursor, "• Balance due upon completion", False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertString(cursor, "• Contract valid for 30 days from date above", False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

# Terms & Conditions
add_blue_heading(text, cursor, "Terms & Conditions", 14)
set_para_style(cursor)
terms = [
    "Work schedule subject to weather conditions",
    "Customer responsible for marking underground utilities (call 811 before work begins)",
    "Changes to scope of work require written authorization and may affect pricing",
    "Contractor not responsible for damage to unmarked utilities or existing irrigation lines",
    "Customer grants access to property during project duration"
]
for term in terms:
    text.insertString(cursor, f"• {term}", False)
    text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

# Contractor info (corrected)
set_para_style(cursor)
text.insertString(cursor, "Contractor: WaterWizard Landscaping", False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertString(cursor, "Address: 10402 NW 11th Ave, Vancouver, WA 98685", False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertString(cursor, "Phone: 707-845-4714", False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertString(cursor, "Email: waterwizardpdx@gmail.com", False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

# Signature lines
text.insertString(cursor, "_" * 40 + "     " + "_" * 20, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertString(cursor, "Client Signature                                      Date", False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertString(cursor, "_" * 40 + "     " + "_" * 20, False)
text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
text.insertString(cursor, "Contractor Signature                                 Date", False)

# Save
output_path = "/home/johnny5/Downloads/Whitely_Drainage_Contract.odt"
file_url = "file://" + output_path
store_props = (PropertyValue("FilterName", 0, "writer8", 0),)
doc.storeAsURL(file_url, store_props)
print(f"✅ Contract saved: {output_path}")

# Export PDF
pdf_path = "/home/johnny5/Downloads/Whitely_Drainage_Contract.pdf"
pdf_url = "file://" + pdf_path
pdf_props = (PropertyValue("FilterName", 0, "writer_pdf_Export", 0),)
doc.storeToURL(pdf_url, pdf_props)
print(f"✅ PDF exported: {pdf_path}")

print("\n📊 CORRECTED Contract Summary:")
print("   Materials: $215.00")
print("   Labor: $832.75")
print("   Steel Edging: $477.00 (replaces benda-board)")
print("   Subtotal: $1,524.75")
print("   Tax (8.7%): $132.65")
print("   TOTAL: $1,657.40")
print("   Deposit (50%): $828.70")
