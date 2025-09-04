#!/usr/bin/env python3
"""
Test script for modern formatting capabilities in Sprint 4
"""

import sys
sys.path.append('src')

from enhanced_pipeline import EnhancedPipeline
import os

def main():
    print("🎨 TESTING MODERN WATERWIZARD FORMATTING - SPRINT 4")
    print("=" * 70)
    print("Demonstrating professional LibreOffice templates vs ASCII formatting")
    print()
    
    # Create modern output directory
    modern_pipeline = EnhancedPipeline("sprint4_modern_output")
    
    # Test with existing sample data
    sample_file = 'sample_projects.csv'
    
    if not os.path.exists(sample_file):
        print(f"❌ Sample file {sample_file} not found")
        print("Creating minimal test data...")
        
        # Create minimal test CSV
        test_data = """client_name,project_name,template_type,head_count,trench_feet,soil_type,client_address,client_city,client_state,client_zip,client_phone,client_email
Premium Estates LLC,Executive Home Front Yard,sprinkler_zone,12,250,rocky,456 Highland Drive,Austin,TX,78704,(512) 555-9876,info@premiumestates.com
Rodriguez Family Trust,Backyard Irrigation,sprinkler_zone,8,180,clay,789 Oak Lane,Austin,TX,78705,(512) 555-3214,rodriguez@family.com"""
        
        with open(sample_file, 'w') as f:
            f.write(test_data)
        print(f"✅ Created {sample_file}")
    
    print(f"\n🚀 Processing {sample_file} with MODERN formatting...")
    
    # Test modern formatting
    results = modern_pipeline.process_worksheet_modern(sample_file, 'contract')
    
    if results['success']:
        print(f"\n✅ MODERN FORMATTING TEST COMPLETE!")
        print(f"📁 Modern documents generated in: {results['output_directory']}")
        
        # Show what was generated
        successful_projects = [p for p in results['projects'] if p['overall_success']]
        print(f"📄 Generated {len(successful_projects)} modern professional documents")
        
        for project in successful_projects:
            client_name = project['client_name']
            files = project.get('modern_files', {})
            print(f"   📋 {client_name}:")
            if 'odt' in files:
                print(f"      - ODT: {files['odt']}")
            if 'pdf' in files:
                print(f"      - PDF: {files['pdf']}")
        
        print(f"\n🎯 KEY IMPROVEMENTS IN SPRINT 4:")
        print("   ✅ Professional LibreOffice templates with proper styling")
        print("   ✅ Modern table layouts replacing ASCII box drawing")
        print("   ✅ Color-coded headers and professional typography")
        print("   ✅ Structured ODT files that convert cleanly to PDF")
        print("   ✅ WaterWizard branding with consistent formatting")
        print("   ✅ Client-ready documents with polished presentation")
        
        print(f"\n🔍 COMPARISON:")
        print("   OLD (Sprint 3): ASCII art (╔═══╗) in plain text files")
        print("   NEW (Sprint 4): Native LibreOffice formatting with professional styling")
        
    else:
        print("❌ Modern formatting test failed")
        if 'error' in results:
            print(f"Error: {results['error']}")

if __name__ == "__main__":
    main()