#!/usr/bin/env python3
"""
Test the fixed ODT generation with corrected XML format
"""

import sys
sys.path.append('src')

from modern_document_generator import ModernDocumentGenerator
from decimal import Decimal
from pathlib import Path
from datetime import datetime

def main():
    print("🔧 TESTING FIXED ODT GENERATION")
    print("=" * 50)
    print("Testing corrected XML format and human validation")
    print()

    # Initialize modern generator
    modern_generator = ModernDocumentGenerator()
    
    # Test client data
    client_info = {
        'name': 'Fixed ODT Test Client',
        'address': '123 Validation Street',
        'city': 'Portland',
        'state': 'OR',
        'zip': '97205',
        'phone': '503-555-1234',
        'email': 'test@fixedodt.com'
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
        'name': 'Fixed ODT Generation Test',
        'description': 'Testing the corrected ODT XML format for proper document generation and human validation.',
        'payment_terms': '100% ($350.00) due upon completion of work.',
        'id': 'FIXED001'
    }
    
    # Simple line items for testing
    line_items = [
        {
            'description': 'Test equipment setup',
            'quantity': 1.0,
            'unit_rate': 100.00,
            'line_total': 100.00,
            'category': 'equipment',
            'unit': 'each'
        },
        {
            'description': 'Validation testing work',
            'quantity': 2.5,
            'unit_rate': 75.00,
            'line_total': 187.50,
            'category': 'labor',
            'unit': 'hours'
        },
        {
            'description': 'Document review process',
            'quantity': 1.0,
            'unit_rate': 62.50,
            'line_total': 62.50,
            'category': 'labor',
            'unit': 'hours'
        }
    ]
    
    # Create output directory
    output_dir = Path("fixed_odt_test")
    output_dir.mkdir(exist_ok=True)
    
    try:
        odt_output = str(output_dir / "Fixed_ODT_Test_Contract.odt")
        
        print("📄 Generating contract with corrected XML format...")
        
        # Generate contract - this should create a new, corrected template
        contract_path = modern_generator.generate_modern_professional_contract(
            client_info, contractor_info, project_info, line_items, odt_output
        )
        
        print(f"✅ Contract generated: {contract_path}")
        print()
        print("🎯 The document should now open automatically for human validation!")
        print("Please check if:")
        print("✓ LibreOffice opens without XML format errors")
        print("✓ Blue section headers are visible")
        print("✓ Professional formatting is applied")
        print("✓ Content is properly populated")
        
    except Exception as e:
        print(f"❌ Error in fixed ODT generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()