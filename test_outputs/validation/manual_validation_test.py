#!/usr/bin/env python3
"""
Manually test the document opening for validation
"""

import sys
sys.path.append('src')

from modern_document_generator import ModernDocumentGenerator

def main():
    print("🔍 MANUAL DOCUMENT VALIDATION TEST")
    print("=" * 50)
    
    generator = ModernDocumentGenerator()
    
    # Test opening the ODT file
    odt_path = "human_validation_test/Human_Validation_Test_Contract.odt"
    print(f"Attempting to open: {odt_path}")
    
    success = generator.open_document_for_human_review(odt_path, "test contract")
    
    if success:
        print("\n✅ Document opening test PASSED")
    else:
        print("\n❌ Document opening test FAILED")

if __name__ == "__main__":
    main()