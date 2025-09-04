#!/usr/bin/env python3
"""
Test the Human-in-the-Loop Validation System
Demonstrates automatic document opening for visual quality control
"""

import sys
sys.path.append('src')

from modern_document_generator import ModernDocumentGenerator
from decimal import Decimal
from pathlib import Path
from datetime import datetime

def main():
    print("🔍 HUMAN-IN-THE-LOOP VALIDATION TEST")
    print("=" * 60)
    print("Testing automatic document opening for visual quality control")
    print("This demonstrates the new human validation feature in Squirt")
    print()

    # Initialize modern generator
    modern_generator = ModernDocumentGenerator()
    
    # Test client data (privacy-safe)
    client_info = {
        'name': 'Test Validation Client',
        'address': '789 Quality Control St',
        'city': 'Portland',
        'state': 'OR',
        'zip': '97210',
        'phone': '503-555-0789',
        'email': 'test@validationclient.com'
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
        'name': 'Human Validation Test Project',
        'description': 'This is a test project to demonstrate the human-in-the-loop validation system for visual quality control of generated documents.',
        'payment_terms': '100% ($450.00) due upon completion of work.',
        'id': 'VALIDATION001'
    }
    
    # Create test line items
    line_items = [
        {
            'description': 'Equipment setup',
            'quantity': 1.0,
            'unit_rate': 75.00,
            'line_total': 75.00,
            'category': 'equipment',
            'unit': 'each'
        },
        {
            'description': 'Testing materials',
            'quantity': 2.0,
            'unit_rate': 25.00,
            'line_total': 50.00,
            'category': 'materials',
            'unit': 'each'
        },
        {
            'description': 'Quality validation work',
            'quantity': 3.0,
            'unit_rate': 75.00,
            'line_total': 225.00,
            'category': 'labor',
            'unit': 'hours'
        },
        {
            'description': 'Human review process',
            'quantity': 2.0,
            'unit_rate': 50.00,
            'line_total': 100.00,
            'category': 'labor',
            'unit': 'hours'
        }
    ]
    
    # Create output directory
    output_dir = Path("human_validation_test")
    output_dir.mkdir(exist_ok=True)
    
    print("📄 Generating contract with human-in-the-loop validation...")
    print("The document will automatically open for your review.")
    print()
    
    try:
        odt_output = str(output_dir / "Human_Validation_Test_Contract.odt")
        
        # Generate contract with automatic human validation (default behavior)
        contract_path = modern_generator.generate_modern_professional_contract(
            client_info, contractor_info, project_info, line_items, odt_output
            # auto_open_for_review=True is the default
        )
        
        print(f"✅ Contract generated: {contract_path}")
        
        # Also generate PDF and open for review
        try:
            pdf_path = modern_generator.convert_to_pdf(contract_path)
            print(f"✅ PDF generated: {pdf_path}")
            
            # Open PDF for additional validation
            modern_generator.open_document_for_human_review(pdf_path, "PDF version")
            
        except Exception as e:
            print(f"⚠️  PDF conversion note: {e}")
        
        print(f"\n🎯 HUMAN-IN-THE-LOOP VALIDATION SYSTEM FEATURES:")
        print("=" * 50)
        print("✅ Automatic document opening after generation")
        print("✅ Clear validation instructions displayed")
        print("✅ Support for both ODT and PDF review")
        print("✅ Quality control checklist provided")
        print("✅ Can be enabled/disabled per generation call")
        
        print(f"\n📋 VALIDATION CHECKLIST FOR HUMAN REVIEW:")
        print("✓ Blue section headers visible and properly formatted")
        print("✓ Blue italic subsection headers for 'Materials & Equipment'")
        print("✓ Professional typography hierarchy (titles, headers, body text)")
        print("✓ Prepared for/by table layout clean and aligned")
        print("✓ Strategic bold formatting applied correctly")
        print("✓ Overall professional appearance and readability")
        print("✓ All content properly populated (no missing placeholders)")
        print("✓ Tax calculations and totals accurate")
        
        print(f"\n✅ HUMAN-IN-THE-LOOP VALIDATION TEST COMPLETE!")
        print("Documents should now be open for your visual review.")
        
    except Exception as e:
        print(f"❌ Error in validation test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()