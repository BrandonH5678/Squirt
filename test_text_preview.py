#!/usr/bin/env python3
"""
Test the text preview fallback for human validation when GUI opening fails
"""

import sys
sys.path.append('src')

from modern_document_generator import ModernDocumentGenerator
from pathlib import Path

def main():
    print("📄 TESTING TEXT PREVIEW FALLBACK")
    print("=" * 50)
    
    generator = ModernDocumentGenerator()
    
    # Test with the existing ODT file
    odt_path = "human_validation_test/Human_Validation_Test_Contract.odt"
    
    if Path(odt_path).exists():
        print(f"Testing text preview for: {odt_path}")
        generator._show_odt_text_preview(odt_path)
    else:
        print(f"ODT file not found: {odt_path}")

if __name__ == "__main__":
    main()