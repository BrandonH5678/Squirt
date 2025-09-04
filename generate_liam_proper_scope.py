#!/usr/bin/env python3
"""
Generate Liam Smith's Fall 2025 cleanup contract using the NEW scope-based ODT generator
This properly supports scope organization without hardcoded category headers
"""

import sys
sys.path.append('src')

from scope_based_odt_generator import ScopeBasedODTGenerator
from datetime import datetime
from pathlib import Path

def main():
    print("🍂 LIAM SMITH FALL 2025 - PROPER SCOPE-BASED CONTRACT")
    print("=" * 70)
    print("Using NEW ScopeBasedODTGenerator with proper scope organization")
    print()

    # Proper scope content as plain text (will be formatted in template)
    scope_content = """Hollyhock Removal — $265.00
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

    # Contract data in format expected by ScopeBasedODTGenerator
    contract_data = {
        # Header information
        'project_title': 'Landscape Maintenance Services – Liam Smith Property',
        
        # Client information  
        'client_name': 'Liam Smith',
        'client_address': '6112 SE 77th Ave\\nPortland, OR 97206\\nPhone: 785-979-5599\\nEmail: lsmith@email.com',
        
        # Contractor information
        'contractor_name': 'WaterWizard Irrigation & Landscape',
        'contractor_address': 'Professional Landscape Services\\nPhone: (555) 123-4567\\nEmail: info@waterwizard.com',
        
        # Project summary
        'project_summary': 'Complete fall landscape cleanup and maintenance service including hollyhock removal, Tree of Heaven elimination, pruning services, and comprehensive debris disposal with site restoration.',
        
        # Financial totals
        'materials_total': '40.00',
        'equipment_total': '100.00',
        'labor_total': '637.50',
        'subtotal': '777.50',
        'tax_amount': '0.00',
        'total_amount': '777.50',
        
        # Payment terms
        'payment_terms': 'Payment due upon completion of work.',
        
        # THE KEY FIX: Scope content goes in dedicated scope_content field
        'scope_content': scope_content,
        
        # Terms and conditions
        'terms_conditions': '''1. Scope of Work: Contractor shall perform the landscape maintenance described above.
2. Price and Payments: The total cost of the project is $777.50. Payment due upon completion.
3. Time of Work: Work to be completed within agreed timeframe, weather permitting.
4. Materials and Labor: Contractor provides all necessary labor, equipment, and disposal.
5. Warranty: Contractor warrants work quality for seasonal landscape maintenance standards.
6. Compliance: All work complies with local waste disposal and safety regulations.
7. Debris Disposal: All organic matter disposed of per Portland area regulations.''',

        # Contract date
        'contract_date': datetime.now().strftime('%B %d, %Y')
    }
    
    # Generate using the scope-based generator
    generator = ScopeBasedODTGenerator()
    output_path = "/home/johnny5/Squirt/Liam_Smith_PROPER_Scope_Modern_Contract.odt"
    
    success = generator.create_scope_based_contract(contract_data, output_path)
    
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
                print(f"⚠️  PDF conversion: {result.stderr}")
        except Exception as e:
            print(f"⚠️  PDF conversion error: {e}")
        
        print(f"\n🎯 PROPER SCOPE-BASED ODT GENERATOR USED:")
        print("✅ No hardcoded 'Materials & Equipment' / 'Labor & Installation' headers")
        print("✅ Dedicated 'SCOPE OF WORK BY AREA' section")
        print("✅ Scope content preserved in original format") 
        print("✅ Modern professional styling with blue headers (#4472c4)")
        print("✅ LibreOffice-compatible XML structure")
        
    else:
        print("❌ Contract generation failed")

if __name__ == "__main__":
    main()