#!/usr/bin/env python3
"""
Create properly styled Whitely Drainage Contract
Matches WaterWizard professional format with blue headers and tables
"""

import subprocess
import time

# Create the ODT file with proper content
content = '''<?xml version="1.0" encoding="UTF-8"?>
This will be a placeholder - we'll use LibreOffice directly via command line
'''

# Use LibreOffice command line to create a simple document first
# Then we'll style it properly

template_text = """French Drain Installation Contract

Prepared for: Daniel & Elin Whitely
Project Address: 9005 Mt Lassen Ave, Vancouver, WA 98664
Contract Date: October 7, 2025

Scope of Work:

Contractor excavates 9"x9" trench, running approximately 20' from east to west on northern boundary of backyard, and 23' from north to south. Contractor perforates concrete housing of drainage junction, installs French drain with 1.5" drain rock and 3" ADS, draining into existing drainage junction. Contractor disposes of excavation tailings.

Steel edging installation included per customer selection.

Materials
Description	Unit Cost	Quantity	Sub-total
1.5" drain rock	$55	2 yard	$110.00
3" ADS Corrugated, perforated drain pipe	$2	43 lf	$86.00
3" ADS Tee	$15	1 each	$15.00
Weed Barrier, Hanes silver, spun	$0.75	43 sf	$32.25
Staples	$0.15	43 each	$6.45

Material Sub-total	$249.70

Equipment
Truck Fee	$120.00

Equipment Sub-total	$120.00

Labor
Description	Rate	Hours	Sub-total
Excavate drainage trench	$72	4.3	$309.60
Dispose excavation tailings	$72	2.5	$180.00
Haul drain rock	$72	1.0	$72.00
Place drain rock	$72	1.72	$123.84
Lay, staple fabric, assemble ADS	$85	0.65	$54.83
Drill through concrete drainage housing	$85	1.0	$85.00

Labor Sub-total	$825.27

Steel Edging (Selected by Customer)
Description	Unit Cost	Quantity	Sub-total
Border Concepts flex steel, black, 13 gauge, 10'	$26	6 each	$156.00
Steel stakes, black	$3	22 each	$64.80

Labor: Install steel edging	$85	3.0	$255.00

Edging Sub-total	$475.80

Project Totals
Subtotal:	$1,670.77
Sales Tax (8.7%):	$145.36
TOTAL:	$1,816.13

Payment Terms
• 50% deposit ($908.07) required to schedule work
• Balance due upon completion
• Contract valid for 30 days from date above

Terms & Conditions
• Work schedule subject to weather conditions
• Customer responsible for marking underground utilities (call 811 before work begins)
• Changes to scope of work require written authorization and may affect pricing
• Contractor not responsible for damage to unmarked utilities or existing irrigation lines
• Customer grants access to property during project duration

Contractor: WaterWizard Landscaping
Phone: (503) 555-1234
Email: info@waterwizard.com


_________________________________________	__________________
Client Signature						Date


_________________________________________	__________________
Contractor Signature					Date
"""

# Write to temp file
with open('/tmp/whitely_contract_content.txt', 'w') as f:
    f.write(template_text)

print("✅ Contract content prepared")
print("📄 Ready to create styled document")
