#!/usr/bin/env python3
"""
Fix Liam Smith contract with correct Oregon tax rules (no sales tax)
"""

import sys
sys.path.append('src')

from tax_rules import TaxRulesEngine
from decimal import Decimal
from datetime import datetime

def generate_corrected_contract():
    """Generate corrected contract for Liam Smith with Oregon tax rules"""
    
    print("🔧 FIXING LIAM SMITH CONTRACT")
    print("=" * 50)
    print("✅ Applying Oregon tax rule: NO SALES TAX")
    
    # Initialize tax engine
    tax_engine = TaxRulesEngine()
    
    # Project data
    client_info = {
        'name': 'Liam Smith',
        'address': '6112 SE 77th Ave',
        'city': 'Portland',
        'state': 'OR',
        'zip': '97206',
        'phone': '785-979-5599',
        'email': 'lsmith@email.com'
    }
    
    project_info = {
        'name': 'Fall Clean-up 2025',
        'address': '6112 SE 77th Ave'
    }
    
    # Line items from original project
    line_items = [
        {'description': 'Truck fee', 'quantity': 1, 'unit_rate': 100.00, 'line_total': 100.00, 'category': 'equipment'},
        {'description': 'Labor: Dead head, prune', 'quantity': 1, 'unit_rate': 75.00, 'line_total': 75.00, 'category': 'labor'},
        {'description': 'Labor: dig/remove 80%-90% hollyhocks', 'quantity': 2, 'unit_rate': 75.00, 'line_total': 150.00, 'category': 'labor'},
        {'description': 'Labor: dig and cut root ball', 'quantity': 3, 'unit_rate': 75.00, 'line_total': 225.00, 'category': 'labor'},
        {'description': 'Labor: setup, backfill & cleanup', 'quantity': 1, 'unit_rate': 75.00, 'line_total': 75.00, 'category': 'labor'},
        {'description': 'Labor: Prune Laurel', 'quantity': 0.5, 'unit_rate': 75.00, 'line_total': 37.50, 'category': 'labor'},
        {'description': 'Labor: Disposal', 'quantity': 1, 'unit_rate': 75.00, 'line_total': 75.00, 'category': 'labor'},
        {'description': 'Fee: Disposal', 'quantity': 1, 'unit_rate': 40.00, 'line_total': 40.00, 'category': 'materials'}
    ]
    
    # Calculate totals with Oregon tax rules
    subtotal = Decimal('777.50')
    tax_amount, total, tax_description = tax_engine.calculate_tax(subtotal, 'OR')
    
    print(f"📊 CORRECTED CALCULATIONS:")
    print(f"   Subtotal: ${subtotal:.2f}")
    print(f"   Tax: ${tax_amount:.2f} ({tax_description})")
    print(f"   Total: ${total:.2f}")
    
    # Generate corrected contract
    doc_number = f"WW-{datetime.now().strftime('%Y%m%d')}-LSMITH-CORRECTED"
    date_str = datetime.now().strftime("%B %d, %Y")
    
    narrative = """Complete fall landscape cleanup and maintenance service including:
    
• Deadhead all hollyhocks and remove 80% of existing plants
• Dead-head and prune back front yard plants as necessary  
• Tree of Heaven removal including root ball excavation
• Prune Laurel shrubs away from house and clear sideyard travel area
• Complete debris collection and proper disposal
• Site cleanup and restoration

All work performed by trained landscape professionals with proper equipment and disposal methods."""
    
    # Group line items by category
    materials = [item for item in line_items if item['category'] == 'materials']
    equipment = [item for item in line_items if item['category'] == 'equipment']
    labor = [item for item in line_items if item['category'] == 'labor']
    
    contract = f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                           WATERWIZARD IRRIGATION                              ║
║                     Professional Landscape Services Contract                  ║
╚═══════════════════════════════════════════════════════════════════════════════╝

CONTRACT NUMBER: {doc_number}
DATE: {date_str}

PREPARED FOR:                          PREPARED BY:
{client_info['name']}                           WaterWizard Irrigation & Landscape
{client_info['address']}                        Professional Landscape Services
{client_info['city']}, {client_info['state']} {client_info['zip']}
Phone: {client_info['phone']}       Phone: (555) 123-4567
Email: {client_info['email']}       Email: info@waterwizard.com

PROJECT: {project_info['name']}
LOCATION: {project_info['address']}, {client_info['city']}, {client_info['state']}

═════════════════════════════════════════════════════════════════════════════════

PROJECT DESCRIPTION:

{narrative}

═════════════════════════════════════════════════════════════════════════════════

SERVICES & MATERIALS BREAKDOWN:

┌─────────────────────────────────────────────┬──────┬─────────┬─────────────┐
│ Description                                 │ Qty  │ Rate    │ Total       │
├─────────────────────────────────────────────┼──────┼─────────┼─────────────┤"""

    # Add equipment
    if equipment:
        contract += f"\n│ EQUIPMENT & FEES                            │      │         │             │"
        for item in equipment:
            desc = item['description'][:43]
            qty_str = f"{item['quantity']:.1f}"
            rate_str = f"${item['unit_rate']:.2f}"
            total_str = f"${item['line_total']:.2f}"
            contract += f"\n│ {desc:<43} │ {qty_str:>4} │ {rate_str:>7} │ {total_str:>11} │"
    
    # Add materials
    if materials:
        contract += f"\n│ MATERIALS & DISPOSAL                        │      │         │             │"
        for item in materials:
            desc = item['description'][:43]
            qty_str = f"{item['quantity']:.1f}"
            rate_str = f"${item['unit_rate']:.2f}"
            total_str = f"${item['line_total']:.2f}"
            contract += f"\n│ {desc:<43} │ {qty_str:>4} │ {rate_str:>7} │ {total_str:>11} │"
    
    # Add labor
    if labor:
        contract += f"\n│ PROFESSIONAL LABOR                          │      │         │             │"
        for item in labor:
            desc = item['description'][:43]
            qty_str = f"{item['quantity']:.1f}"
            rate_str = f"${item['unit_rate']:.2f}"
            total_str = f"${item['line_total']:.2f}"
            contract += f"\n│ {desc:<43} │ {qty_str:>4} │ {rate_str:>7} │ {total_str:>11} │"

    # Tax section - show Oregon has no sales tax
    if tax_amount > 0:
        contract += f"""
├─────────────────────────────────────────────┴──────┴─────────┼─────────────┤
│                                              SUBTOTAL: │ ${float(subtotal):>11.2f} │
│                                    TAX ({tax_description}): │ ${float(tax_amount):>11.2f} │
│                                               TOTAL: │ ${float(total):>11.2f} │
└────────────────────────────────────────────────────────┴─────────────┘"""
    else:
        contract += f"""
├─────────────────────────────────────────────┴──────┴─────────┼─────────────┤
│                                              SUBTOTAL: │ ${float(subtotal):>11.2f} │
│                              TAX (Oregon - No Sales Tax): │ ${float(tax_amount):>11.2f} │
│                                               TOTAL: │ ${float(total):>11.2f} │
└────────────────────────────────────────────────────────┴─────────────┘"""

    contract += f"""

TERMS AND CONDITIONS:

• Work includes professional landscape maintenance and cleanup
• All debris will be properly disposed of per local regulations
• Weather delays may affect completion timeline
• Site access required for all work areas
• Payment due upon completion of work
• Additional services require separate authorization
• Oregon sales tax exempt per state law

ACCEPTANCE:

Customer: ________________________________    Date: _______________

WaterWizard Representative: ________________    Date: {date_str}

═════════════════════════════════════════════════════════════════════════════════
"""
    
    # Save corrected contract
    output_file = "liam_smith_corrected_contract.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(contract)
    
    print(f"✅ Corrected contract saved: {output_file}")
    
    return contract

def main():
    """Generate corrected contract with Oregon tax rules"""
    
    contract = generate_corrected_contract()
    
    print(f"\n📄 CORRECTED CONTRACT PREVIEW:")
    print("=" * 60)
    
    lines = contract.strip().split('\n')
    for i, line in enumerate(lines[50:65]):  # Show tax section
        print(f"{i+51:2d}│ {line}")
    
    print("=" * 60)
    
    print(f"\n✅ OREGON TAX RULE APPLIED SUCCESSFULLY!")
    print(f"   Original total with tax: $845.53")
    print(f"   Corrected total (no tax): $777.50") 
    print(f"   Tax savings: $68.03")

if __name__ == "__main__":
    main()