#!/usr/bin/env python3
"""
Generate Liam Smith's Fall 2025 cleanup contract with CORRECT scope-based formatting
Using proper Squirt scope organization standards with modern professional styling
"""

import sys
sys.path.append('src')

from fixed_odt_generator import FixedODTGenerator
from datetime import datetime
from pathlib import Path

def main():
    print("🍂 LIAM SMITH FALL 2025 - CORRECT SCOPE-BASED CONTRACT")
    print("=" * 70)
    print("Applying correct Squirt scope organization with modern styling")
    print()

    # Correct scope organization - each scope contains its own materials/labor breakdown
    client_info = {
        'name': 'Liam Smith',
        'address': '6112 SE 77th Ave',
        'city': 'Portland', 
        'state': 'OR',
        'zip': '97206',
        'phone': '785-979-5599',
        'email': 'lsmith@email.com'
    }
    
    contractor_info = {
        'company': 'WaterWizard Irrigation & Landscape',
        'tagline': 'Professional Landscape Services',
        'phone': '(555) 123-4567',
        'email': 'info@waterwizard.com'
    }
    
    project_info = {
        'title': 'Landscape Maintenance Services – Liam Smith Property',
        'summary': 'Complete fall landscape cleanup and maintenance service including hollyhock removal, Tree of Heaven elimination, pruning services, and comprehensive debris disposal with site restoration.',
        'materials_total': 40.00,
        'equipment_total': 100.00, 
        'labor_total': 637.50,
        'subtotal': 777.50,
        'tax_amount': 0.00,
        'total': 777.50,
        'payment_terms': 'Payment due upon completion of work.'
    }
    
    # CORRECT SCOPE FORMAT: Each scope contains its own breakdown
    scopes_content = """SCOPE OF WORK BY AREA

Hollyhock Removal — $265.00
Deadhead all hollyhocks and remove 80%-90% of existing plants. Includes complete removal of root systems and site preparation.

Materials & Equipment
Qty     Unit Price    Subtotal    Description
1       $40.00       $40.00      Disposal Fee

Labor
Task                                              Subtotal
Dead head, prune                                  $75.00
Dig/remove 80%-90% hollyhocks                     $150.00

Tree of Heaven Removal — $300.00
Complete Tree of Heaven removal including root ball excavation, cutting, and site restoration to prevent regrowth.

Labor
Task                                              Subtotal
Dig and cut root ball                             $225.00
Setup, backfill & cleanup                        $75.00

Laurel Pruning — $37.50
Prune Laurel shrubs away from house structure and clear sideyard travel areas for improved access and plant health.

Labor
Task                                              Subtotal
Prune Laurel                                      $37.50

Site Cleanup & Disposal — $175.00
Complete debris collection, proper disposal of all organic matter, and final site cleanup and restoration.

Equipment & Fees
Qty     Unit Price    Subtotal    Description
1       $100.00      $100.00     Truck fee

Labor
Task                                              Subtotal
Disposal                                          $75.00"""

    # Flatten the data structure to match FixedODTGenerator expectations
    contract_data = {
        # Client information
        'client_name': client_info['name'],
        'client_address': f"{client_info['address']}\n{client_info['city']}, {client_info['state']} {client_info['zip']}\nPhone: {client_info['phone']}\nEmail: {client_info['email']}",
        
        # Contractor information
        'contractor_name': contractor_info['company'],
        'contractor_address': f"{contractor_info['tagline']}\nPhone: {contractor_info['phone']}\nEmail: {contractor_info['email']}",
        
        # Project information
        'company_name': 'WaterWizard',
        'project_description': project_info['summary'],
        'project_date': datetime.now().strftime('%B %d, %Y'),
        'project_location': f"{client_info['address']}, {client_info['city']}, {client_info['state']}",
        
        # Scope content (this is the key fix - putting scope content in the right place)
        'materials_list': scopes_content,  # The complete scope content goes here
        'labor_details': 'See scope details above',
        
        # Financial totals
        'subtotal': f"{project_info['subtotal']:.2f}",
        'tax_amount': f"{project_info['tax_amount']:.2f}",
        'total_amount': f"{project_info['total']:.2f}",
        
        # Terms
        'terms_conditions': """1. Scope of Work: Contractor shall perform the landscape maintenance described above.
2. Price and Payments: The total cost of the project is $777.50. Payment due upon completion.
3. Time of Work: Work to be completed within agreed timeframe, weather permitting.
4. Materials and Labor: Contractor provides all necessary labor, equipment, and disposal.
5. Warranty: Contractor warrants work quality for seasonal landscape maintenance standards.
6. Compliance: All work complies with local waste disposal and safety regulations.
7. Debris Disposal: All organic matter disposed of per Portland area regulations."""
    }
    
    # Generate with modern professional styling and correct scope organization
    generator = FixedODTGenerator()
    output_path = "/home/johnny5/Squirt/Liam_Smith_CORRECT_Modern_Scoped_Contract.odt"
    
    success = generator.create_waterwizard_contract(contract_data, output_path)
    
    if success:
        print(f"✅ Contract generated: {output_path}")
        
        # Convert to PDF
        try:
            import subprocess
            pdf_path = output_path.replace('.odt', '.pdf')
            cmd = ['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', '/home/johnny5/Squirt', output_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"✅ PDF generated: {pdf_path}")
            else:
                print(f"⚠️  PDF conversion failed: {result.stderr}")
        except Exception as e:
            print(f"⚠️  PDF conversion error: {e}")
        
        print(f"\n🎯 CORRECT SCOPE ORGANIZATION APPLIED:")
        print("✅ Each scope contains its own materials/equipment/labor breakdown")
        print("✅ No cross-scope category grouping") 
        print("✅ Modern professional styling with blue headers")
        print("✅ LibreOffice-compatible XML structure")
        
    else:
        print("❌ Contract generation failed")

if __name__ == "__main__":
    main()