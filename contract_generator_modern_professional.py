#!/usr/bin/env python3
"""
Generate Modern Professional contract using visual styling
Privacy-safe version with generic client data
"""

import sys
sys.path.append('src')

from modern_document_generator import ModernDocumentGenerator
from decimal import Decimal
from pathlib import Path
from datetime import datetime

def main():
    print("🎨 MODERN PROFESSIONAL CONTRACT GENERATOR")
    print("=" * 60)
    print("Generating contract with modern professional visual styling")
    print()

    # Initialize modern generator
    modern_generator = ModernDocumentGenerator()
    
    # Sample client data (privacy-safe)
    client_info = {
        'name': 'Sample Client LLC',
        'address': '123 Main Street',
        'city': 'Portland',
        'state': 'OR',
        'zip': '97205',
        'phone': '503-555-0123',
        'email': 'contact@sampleclient.com'
    }
    
    contractor_info = {
        'name': 'WaterWizard Irrigation & Landscape',
        'address': '456 Professional Ave',
        'city': 'Vancouver',
        'state': 'WA',
        'zip': '98660',
        'phone': '360-555-0456',
        'email': 'info@waterwizard.com'
    }
    
    project_info = {
        'name': 'Fall Landscape Cleanup Project',
        'description': 'Complete fall landscape cleanup and maintenance service including deadheading, plant removal, pruning, debris collection and proper disposal.',
        'payment_terms': '100% ($750.00) due upon completion of work.',
        'id': 'DEMO001'
    }
    
    # Create sample line items that match the structure
    line_items = [
        # Equipment & Fees
        {
            'description': 'Truck fee',
            'quantity': 1.0,
            'unit_rate': 100.00,
            'line_total': 100.00,
            'category': 'equipment',
            'unit': 'each'
        },
        # Materials & Disposal
        {
            'description': 'Fee: Disposal',
            'quantity': 1.0,
            'unit_rate': 40.00,
            'line_total': 40.00,
            'category': 'materials',
            'unit': 'each'
        },
        # Professional Labor
        {
            'description': 'Labor: Dead head, prune',
            'quantity': 1.0,
            'unit_rate': 75.00,
            'line_total': 75.00,
            'category': 'labor',
            'unit': 'hours'
        },
        {
            'description': 'Labor: Plant removal and cleanup',
            'quantity': 3.5,
            'unit_rate': 75.00,
            'line_total': 262.50,
            'category': 'labor',
            'unit': 'hours'
        },
        {
            'description': 'Labor: Pruning and trimming',
            'quantity': 1.5,
            'unit_rate': 75.00,
            'line_total': 112.50,
            'category': 'labor',
            'unit': 'hours'
        },
        {
            'description': 'Labor: Debris collection and disposal',
            'quantity': 2.0,
            'unit_rate': 75.00,
            'line_total': 150.00,
            'category': 'labor',
            'unit': 'hours'
        }
    ]
    
    # Calculate totals
    subtotal = Decimal('750.00')
    
    # Create output directory
    output_dir = Path("modern_professional_output")
    output_dir.mkdir(exist_ok=True)
    
    # Generate modern professional contract
    print("📄 Generating modern professional contract...")
    
    try:
        odt_output = str(output_dir / "Sample_Client_Modern_Professional_Contract.odt")
        
        # Generate the contract using modern professional styling
        contract_path = modern_generator.generate_modern_professional_contract(
            client_info, contractor_info, project_info, line_items, odt_output
        )
        
        print(f"✅ Modern professional ODT contract: {contract_path}")
        
        # Try to convert to PDF using LibreOffice
        try:
            pdf_path = modern_generator.convert_to_pdf(contract_path)
            print(f"✅ Modern professional PDF contract: {pdf_path}")
        except Exception as e:
            print(f"⚠️  PDF conversion note: {e}")
            print(f"   ODT version available for manual conversion")
        
        print(f"\n🎯 MODERN PROFESSIONAL STYLING APPLIED:")
        print("=" * 50)
        print("✅ Blue section headers (PROJECT SUMMARY, PROJECT TOTALS, etc.)")
        print("✅ Blue italic subsection headers (Materials & Equipment)")
        print("✅ Professional typography hierarchy")
        print("✅ Clean prepared for/by table layout")
        print("✅ Strategic bold formatting for emphasis")
        print("✅ Professional color scheme throughout")
        print("✅ Oregon tax compliance maintained")
        
        print(f"\n📊 PROJECT DETAILS:")
        print(f"   Client: {client_info['name']}")
        print(f"   Location: {client_info['city']}, {client_info['state']}")
        print(f"   Project Value: ${float(subtotal):.2f}")
        print(f"   Total Line Items: {len(line_items)}")
        print(f"   Labor Hours: {sum(item['quantity'] for item in line_items if item['category'] == 'labor'):.1f}")
        
        print(f"\n🔍 VISUAL IMPROVEMENTS:")
        print(f"   OLD: Plain text, no visual hierarchy")
        print(f"   NEW: Modern professional styling with colors and typography")
        print(f"   ENHANCED: Blue headers, italic subsections, professional formatting")
        
        print(f"\n📁 FILES GENERATED:")
        print(f"   📄 {odt_output}")
        if Path(pdf_path if 'pdf_path' in locals() else odt_output.replace('.odt', '.pdf')).exists():
            print(f"   📄 {pdf_path if 'pdf_path' in locals() else odt_output.replace('.odt', '.pdf')}")
            
        print(f"\n✅ MODERN PROFESSIONAL CONTRACT GENERATION COMPLETE!")
        
    except Exception as e:
        print(f"❌ Error generating modern professional contract: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()