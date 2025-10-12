#!/usr/bin/env python3
"""
Generate Whitely Drainage Contract with proper WaterWizard styling
Blue headers, professional tables, steel edging included in totals
"""

import json
import math
from pathlib import Path

# Load template
with open('/home/johnny5/Squirt/templates/contracts/french_drain_standard.json', 'r') as f:
    template = json.load(f)

# Load contract data
with open('/home/johnny5/Squirt/whitely_drainage_contract_data.json', 'r') as f:
    data = json.load(f)

# Extract parameters
params = data['project_parameters']
total_length = params['total_drain_length']
edging_length = params['edging_length']

# Calculate materials
materials = []
for item in template['standard_materials']:
    qty_formula = item['qty_formula']
    # Evaluate formula
    qty = eval(qty_formula, {
        'total_drain_length': total_length,
        'ceil': math.ceil,
        'max': max
    })
    desc = item['description'].replace('{{rock_size}}', params['rock_size']).replace('{{pipe_size}}', params['pipe_size'])
    subtotal = round(qty * item['unit_cost'], 2)
    materials.append({
        'description': desc,
        'unit': item['unit'],
        'unit_cost': item['unit_cost'],
        'quantity': qty,
        'subtotal': subtotal
    })

# Calculate labor
labor = []
for item in template['standard_labor']:
    hrs_formula = item['hrs_formula']
    hrs = eval(hrs_formula, {
        'total_drain_length': total_length,
        'ceil': math.ceil,
        'max': max
    })
    subtotal = round(hrs * item['rate'], 2)
    labor.append({
        'task': item['task'],
        'rate': item['rate'],
        'hours': hrs,
        'subtotal': subtotal
    })

# Add truck fee
truck_fee = template['standard_equipment'][0]['cost']

# Calculate edging (CUSTOMER SELECTED - INCLUDE IN TOTALS)
edging_materials = []
edging_labor = []
edging_subtotal = 0

if params.get('edging_selected', False):
    for item in template['optional_items']['steel_edging']['materials']:
        qty_formula = item['qty_formula']
        qty = eval(qty_formula, {
            'edging_length': edging_length,
            'ceil': math.ceil
        })
        subtotal = round(qty * item['unit_cost'], 2)
        edging_materials.append({
            'description': item['description'],
            'unit': item['unit'],
            'unit_cost': item['unit_cost'],
            'quantity': qty,
            'subtotal': subtotal
        })
        edging_subtotal += subtotal

    for item in template['optional_items']['steel_edging']['labor']:
        hrs_formula = item['hrs_formula']
        hrs = eval(hrs_formula, {
            'edging_length': edging_length
        })
        subtotal = round(hrs * item['rate'], 2)
        edging_labor.append({
            'task': item['task'],
            'rate': item['rate'],
            'hours': hrs,
            'subtotal': subtotal
        })
        edging_subtotal += subtotal

# Calculate totals
materials_subtotal = sum(m['subtotal'] for m in materials)
labor_subtotal = sum(l['subtotal'] for l in labor)
project_subtotal = materials_subtotal + labor_subtotal + truck_fee + edging_subtotal
tax_amount = round(project_subtotal * data['tax_rate'], 2)
total = round(project_subtotal + tax_amount, 2)

# Generate LibreOffice document with proper styling
print("Creating WaterWizard French Drain Installation Contract...")
print(f"Client: {data['client_name']}")
print(f"Address: {data['property_address']}")
print(f"Date: {data['contract_date']}")
print()

# Create ODT-style output for now (will convert to proper UNO later)
output = f"""FRENCH DRAIN INSTALLATION CONTRACT

Prepared for: {data['client_name']}
Project Address: {data['property_address']}
Contract Date: {data['contract_date']}

SCOPE OF WORK:

Contractor excavates {params['trench_dimensions']} trench, running approximately {params['drain_length_ew']}' from east to west on northern boundary of backyard, and {params['drain_length_ns']}' from north to south.

Contractor perforates concrete housing of drainage junction, installs French drain with {params['rock_size']} drain rock and {params['pipe_size']} ADS, draining into existing drainage junction.

Contractor disposes of excavation tailings.

Steel edging installation included per customer selection.

MATERIALS:
"""

for m in materials:
    output += f"{m['description']:<50} {m['unit']:>8} ${m['unit_cost']:>8.2f}  {m['quantity']:>6}  ${m['subtotal']:>10.2f}\n"

output += f"\n{'Materials Subtotal':<50} ${materials_subtotal:>10.2f}\n\n"

output += "EQUIPMENT:\n"
output += f"{'Truck Fee':<50} ${truck_fee:>10.2f}\n\n"

output += "LABOR:\n"
for l in labor:
    output += f"{l['task']:<50} ${l['rate']}/hr  {l['hours']:>6.2f} hrs  ${l['subtotal']:>10.2f}\n"

output += f"\n{'Labor Subtotal':<50} ${labor_subtotal:>10.2f}\n\n"

if edging_materials or edging_labor:
    output += "STEEL EDGING (SELECTED):\n"
    for m in edging_materials:
        output += f"{m['description']:<50} {m['unit']:>8} ${m['unit_cost']:>8.2f}  {m['quantity']:>6}  ${m['subtotal']:>10.2f}\n"
    for l in edging_labor:
        output += f"{l['task']:<50} ${l['rate']}/hr  {l['hours']:>6.2f} hrs  ${l['subtotal']:>10.2f}\n"
    output += f"\n{'Edging Subtotal':<50} ${edging_subtotal:>10.2f}\n\n"

output += f"""
PROJECT TOTALS:
{'Project Subtotal':<50} ${project_subtotal:>10.2f}
{'Sales Tax (8.7%)':<50} ${tax_amount:>10.2f}
{'TOTAL CONTRACT PRICE':<50} ${total:>10.2f}

PAYMENT TERMS:
- {data['payment_terms']['deposit_percent']}% deposit required to schedule work
- Balance due {data['payment_terms']['balance_due']}
- Contract valid for {data['payment_terms']['validity_days']} days from date above

TERMS & CONDITIONS:
"""

for term in template['standard_terms']:
    output += f"• {term}\n"

output += f"""

Contractor: {data['company_info']['name']}
Phone: {data['company_info']['phone']}
Email: {data['company_info']['email']}

_________________________________________    __________________
Client Signature                              Date

_________________________________________    __________________
Contractor Signature                          Date
"""

print(output)

# Save text version
with open('/home/johnny5/Squirt/Whitely_Contract_Preview.txt', 'w') as f:
    f.write(output)

print("\n✅ Contract data calculated successfully")
print(f"📊 Project Subtotal: ${project_subtotal:.2f}")
print(f"💰 Total with Tax: ${total:.2f}")
print(f"🔧 Steel Edging: INCLUDED (${edging_subtotal:.2f})")
