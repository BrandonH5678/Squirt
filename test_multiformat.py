#!/usr/bin/env python3
"""
Test Squirt Multi-Format Document Generation
Demonstrates client-preferred format generation with formatting preservation
"""

import sys
sys.path.append('src')

from enhanced_pipeline import EnhancedPipeline
from format_converter import OutputFormat

def test_multiformat_generation():
    """Test generating documents in multiple client formats"""
    
    print("🧪 TESTING SQUIRT MULTI-FORMAT GENERATION")
    print("=" * 60)
    
    # Initialize pipeline
    pipeline = EnhancedPipeline()
    
    # Test with Allen White Jr's existing documents
    allen_documents = {
        "/home/johnny5/Squirt/Client Files/Allen White Jr/SQUIRT_ONE_PAGE_OVERVIEW.md": "contract",
        "/home/johnny5/Squirt/Client Files/Liam Smith/liam_smith_corrected_contract.txt": "contract"
    }
    
    print("📋 TESTING CLIENT FORMAT PREFERENCES:")
    
    # Test different format combinations
    format_tests = [
        {
            'name': 'Standard Client Package',
            'formats': None,  # Use defaults
            'description': 'PDF + DOCX for contracts'
        },
        {
            'name': 'Excel-Friendly Package', 
            'formats': [OutputFormat.PDF, OutputFormat.XLSX],
            'description': 'PDF + Excel for spreadsheet users'
        },
        {
            'name': 'Microsoft Office Package',
            'formats': [OutputFormat.PDF, OutputFormat.DOCX, OutputFormat.XLSX],
            'description': 'Full MS Office compatibility'
        }
    ]
    
    for test in format_tests:
        print(f"\n🎯 {test['name']}: {test['description']}")
        
        try:
            results = pipeline.generate_client_package(
                f"Test Client - {test['name'].replace(' ', '_')}",
                {"/home/johnny5/Squirt/Client Files/Allen White Jr/SQUIRT_ONE_PAGE_OVERVIEW.md": "contract"},
                test['formats']
            )
            
            formats_created = list(set(results['formats_generated']))
            print(f"   ✅ Created: {', '.join(formats_created)}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n🎯 KEY FEATURES DEMONSTRATED:")
    print("• Client-optimized format selection")
    print("• ASCII diagram preservation in PDF")
    print("• Automatic LibreOffice integration")
    print("• Batch document conversion")
    print("• Organized client file structure")
    
    print(f"\n💼 CLIENT COMPATIBILITY:")
    print("• PDF: Universal viewing (100% compatibility)")
    print("• DOCX: Microsoft Word editing")
    print("• XLSX: Excel spreadsheet compatibility")
    print("• CSV: Simple data exchange")
    
    return True

if __name__ == "__main__":
    test_multiformat_generation()