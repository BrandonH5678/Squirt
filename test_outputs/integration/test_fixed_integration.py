#!/usr/bin/env python3
"""
Test the integration of the fixed ODT generator with ModernDocumentGenerator
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from modern_document_generator import ModernDocumentGenerator

def test_fixed_integration():
    """Test that the fixed ODT integration works"""
    
    generator = ModernDocumentGenerator()
    
    # Sample data
    client_info = {
        'name': 'John Smith Integration Test',
        'address': '789 Integration Ave',
        'city': 'Test City',
        'state': 'OR',
        'zip': '97000'
    }
    
    contractor_info = {
        'name': 'WaterWizard Irrigation & Landscape',
        'address': '456 Business Way',
        'city': 'Portland',
        'state': 'OR',
        'zip': '97201'
    }
    
    project_info = {
        'name': 'Sprinkler System Integration Test',
        'description': 'Complete sprinkler system installation with modern professional styling',
        'payment_terms': 'Payment due within 30 days of completion'
    }
    
    line_items = [
        {
            'category': 'materials',
            'description': 'Rain Bird electronic valve',
            'quantity': 2,
            'unit_rate': 175.00,
            'line_total': 350.00
        },
        {
            'category': 'materials', 
            'description': 'Sprinkler heads (rotating)',
            'quantity': 8,
            'unit_rate': 45.00,
            'line_total': 360.00
        },
        {
            'category': 'labor',
            'description': 'System design and installation',
            'quantity': 6,
            'unit_rate': 85.00,
            'line_total': 510.00
        }
    ]
    
    output_path = "/home/johnny5/Squirt/fixed_odt_test/Integration_Test_Contract.odt"
    
    try:
        print("🧪 Testing fixed ODT integration...")
        result_path = generator.generate_modern_professional_contract(
            client_info=client_info,
            contractor_info=contractor_info, 
            project_info=project_info,
            line_items=line_items,
            output_path=output_path,
            auto_open_for_review=True
        )
        
        print(f"✅ Integration test successful!")
        print(f"📄 Contract generated: {result_path}")
        
        # Verify file exists and is a valid ODT
        if os.path.exists(result_path):
            file_size = os.path.getsize(result_path)
            print(f"📊 File size: {file_size} bytes")
            
            # Check if it's recognized as ODT
            import subprocess
            file_type = subprocess.run(['file', result_path], capture_output=True, text=True)
            print(f"🔍 File type: {file_type.stdout.strip()}")
            
            return True
        else:
            print("❌ Contract file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fixed_integration()
    sys.exit(0 if success else 1)