#!/usr/bin/env python3
"""
Generate Liam Smith's Fall 2025 cleanup contract using Kim Sherertz scope-based formatting
Transform from item-based to scope-based organization
"""

import sys
sys.path.append('src')

from modern_document_generator import ModernDocumentGenerator
from decimal import Decimal
from pathlib import Path

def main():
    print("🍂 LIAM SMITH FALL 2025 CLEANUP - SCOPE-BASED FORMATTING")
    print("=" * 70)
    print("Using Kim Sherertz contract format with scope-based organization")
    print()

    # Reorganize Liam's work into scope-based sections
    # Based on the original description and line items
    
    scopes = {
        "hollyhock_removal": {
            "title": "Hollyhock Removal — $225.00",
            "description": "Deadhead all hollyhocks and remove 80%-90% of existing plants. Includes complete removal of root systems and site preparation.",
            "materials": [
                {"qty": 1, "price": 40.00, "description": "Disposal Fee", "subtotal": 40.00}
            ],
            "labor": [
                {"task": "Dead head, prune", "subtotal": 75.00},
                {"task": "Dig/remove 80%-90% hollyhocks", "subtotal": 150.00}
            ],
            "total": 265.00
        },
        
        "tree_removal": {
            "title": "Tree of Heaven Removal — $300.00", 
            "description": "Complete Tree of Heaven removal including root ball excavation, cutting, and site restoration to prevent regrowth.",
            "materials": [],
            "labor": [
                {"task": "Dig and cut root ball", "subtotal": 225.00},
                {"task": "Setup, backfill & cleanup", "subtotal": 75.00}
            ],
            "total": 300.00
        },
        
        "laurel_pruning": {
            "title": "Laurel Pruning — $37.50",
            "description": "Prune Laurel shrubs away from house structure and clear sideyard travel areas for improved access and plant health.",
            "materials": [],
            "labor": [
                {"task": "Prune Laurel", "subtotal": 37.50}
            ],
            "total": 37.50
        },
        
        "cleanup_disposal": {
            "title": "Site Cleanup & Disposal — $175.00",
            "description": "Complete debris collection, proper disposal of all organic matter, and final site cleanup and restoration.",
            "materials": [],
            "equipment": [
                {"qty": 1, "price": 100.00, "description": "Truck fee", "subtotal": 100.00}
            ],
            "labor": [
                {"task": "Disposal", "subtotal": 75.00}
            ],
            "total": 175.00
        }
    }
    
    # Client info
    client_info = {
        'name': 'Liam Smith',
        'address': '6112 SE 77th Ave',
        'city': 'Portland',
        'state': 'OR',
        'zip': '97206',
        'phone': '785-979-5599',
        'email': 'lsmith@email.com'
    }
    
    # Calculate totals
    materials_total = 40.00
    equipment_total = 100.00
    labor_total = 637.50
    subtotal = materials_total + equipment_total + labor_total
    tax_amount = 0.00  # Oregon has no sales tax
    total = subtotal
    
    # Generate scope-based contract using Kim Sherertz format
    from datetime import datetime
    doc_number = f"WW-{datetime.now().strftime('%Y%m%d')}-LSMITH001"
    date_str = datetime.now().strftime("%B %d, %Y")
    
    contract = f"""CONSTRUCTION CONTRACT
Landscape Maintenance Services – Liam Smith Property

Prepared for:                                     Prepared by:
Liam Smith                                        WaterWizard Irrigation & Landscape
6112 SE 77th Ave                                  Professional Landscape Services
Portland, OR 97206                                Phone: (555) 123-4567
Phone: 785-979-5599                               Email: info@waterwizard.com
Email: lsmith@email.com

PROJECT SUMMARY
Complete fall landscape cleanup and maintenance service including hollyhock removal, Tree 
of Heaven elimination, pruning services, and comprehensive debris disposal with site 
restoration.

PROJECT TOTALS
Materials & Disposal                              $40.00
Equipment & Fees                                  $100.00
Labor                                             $637.50
Subtotal                                          $777.50
Sales Tax (Oregon - No state sales tax)          $0.00
Total Project Cost                                $777.50

PAYMENT TERMS
Payment due upon completion of work.

SCOPE OF WORK BY AREA

{scopes['hollyhock_removal']['title']}
{scopes['hollyhock_removal']['description']}

Materials & Equipment
Qty     Unit Price    Subtotal    Description
1       $40.00       $40.00      Disposal Fee

Labor
Task                                              Subtotal
Dead head, prune                                  $75.00
Dig/remove 80%-90% hollyhocks                     $150.00

{scopes['tree_removal']['title']}
{scopes['tree_removal']['description']}

Labor
Task                                              Subtotal
Dig and cut root ball                             $225.00
Setup, backfill & cleanup                        $75.00

{scopes['laurel_pruning']['title']}
{scopes['laurel_pruning']['description']}

Labor
Task                                              Subtotal
Prune Laurel                                      $37.50

{scopes['cleanup_disposal']['title']}
{scopes['cleanup_disposal']['description']}

Equipment & Fees
Qty     Unit Price    Subtotal    Description
1       $100.00      $100.00     Truck fee

Labor
Task                                              Subtotal
Disposal                                          $75.00

TERMS & CONDITIONS
1. Scope of Work: Contractor shall perform the landscape maintenance described above.
2. Price and Payments: The total cost of the project is $777.50. Payment due upon completion.
3. Time of Work: Work to be completed within agreed timeframe, weather permitting.
4. Materials and Labor: Contractor provides all necessary labor, equipment, and disposal.
5. Warranty: Contractor warrants work quality for seasonal landscape maintenance standards.
6. Compliance: All work complies with local waste disposal and safety regulations.
7. Debris Disposal: All organic matter disposed of per Portland area regulations.

ACCEPTANCE:

Customer: ________________________________    Date: _______________
Liam Smith

WaterWizard Representative: ________________    Date: {date_str}
"""

    # Create output directory
    output_dir = Path("/home/johnny5/Squirt/Client Files/Liam Smith")
    
    # Save the scope-based contract
    scoped_filename = "Liam_Smith_Fall_Cleanup_Scoped.txt"
    scoped_path = output_dir / scoped_filename
    
    with open(scoped_path, 'w', encoding='utf-8') as f:
        f.write(contract)
    
    print(f"✅ Scope-based contract generated: {scoped_path}")
    
    # Try to convert to PDF
    try:
        import subprocess
        pdf_path = str(scoped_path).replace('.txt', '.pdf')
        cmd = ['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', str(output_dir), str(scoped_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and Path(pdf_path).exists():
            print(f"✅ PDF version: {pdf_path}")
        else:
            print(f"⚠️  PDF conversion available via LibreOffice")
    except Exception as e:
        print(f"⚠️  PDF conversion: {e}")
    
    print(f"\n🎯 SCOPE-BASED FORMATTING RESULTS:")
    print("=" * 50)
    print("✅ Organized by work areas (Kim Sherertz format)")
    print("✅ Each scope has narrative + itemized costs")
    print("✅ Professional contract structure")
    print("✅ Clean section organization")
    
    print(f"\n📊 SCOPE BREAKDOWN:")
    for scope_key, scope_data in scopes.items():
        area_name = scope_data['title'].split('—')[0].strip()
        area_cost = scope_data['title'].split('—')[1].strip()
        print(f"   🔹 {area_name}: {area_cost}")
    
    print(f"\n🔍 FORMAT COMPARISON:")
    print(f"   OLD: All items grouped by category (materials, equipment, labor)")
    print(f"   NEW: Items grouped by work scope with narrative descriptions")
    print(f"   MATCHES: Kim Sherertz zone-based organization structure")
    
    print(f"\n📁 FILES IN CLIENT FOLDER:")
    print(f"   📄 {scoped_filename}")
    if (output_dir / scoped_filename.replace('.txt', '.pdf')).exists():
        print(f"   📄 {scoped_filename.replace('.txt', '.pdf')}")
    
    print(f"\n✅ LIAM SMITH SCOPE-BASED CONTRACT COMPLETE!")

if __name__ == "__main__":
    main()