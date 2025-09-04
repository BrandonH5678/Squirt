#!/usr/bin/env python3
"""
Test the robust validation system on Liam Smith's properly generated scope-based contract
"""

import sys
sys.path.append('src')

from robust_validator import RobustValidator
import json

def main():
    print("🛡️  ROBUST VALIDATION TEST")
    print("=" * 50)
    
    validator = RobustValidator()
    contract_path = "/home/johnny5/Squirt/Liam_Smith_PROPER_Scope_Modern_Contract.odt"
    
    # Run comprehensive validation
    results = validator.validate_document_completely(contract_path)
    
    # Display detailed results
    print("\n📊 DETAILED VALIDATION RESULTS:")
    print("=" * 50)
    
    for validation_type, result in results['validations'].items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"\n{validation_type.upper().replace('_', ' ')}: {status}")
        
        if result['success']:
            if 'message' in result:
                print(f"   📝 {result['message']}")
            if 'scope_indicators_found' in result:
                print(f"   🎯 Scope indicators found: {result['scope_indicators_found']}/5")
            if 'styling_indicators_found' in result:
                print(f"   🎨 Styling indicators found: {result['styling_indicators_found']}/4")
            if 'screenshot_path' in result:
                print(f"   📸 Screenshot: {result['screenshot_path']}")
        else:
            print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
    
    # Overall result
    print(f"\n{'='*50}")
    if results['overall_success']:
        print("🎉 OVERALL VALIDATION: ✅ PASSED")
        print("✅ Document meets all critical validation criteria")
        print("✅ Scope-based organization confirmed")
        print("✅ Modern professional styling confirmed") 
        print("✅ LibreOffice compatibility confirmed")
    else:
        print("🚨 OVERALL VALIDATION: ❌ FAILED")
        print(f"❌ Critical failures: {results['critical_failures']}")
    
    # Show screenshot if available
    screenshot_result = results['validations'].get('screenshot', {})
    if screenshot_result.get('success') and screenshot_result.get('screenshot_path'):
        screenshot_path = screenshot_result['screenshot_path']
        print(f"\n📸 Opening screenshot for visual inspection: {screenshot_path}")
        
        # Display the screenshot
        try:
            import subprocess
            subprocess.run(['xdg-open', screenshot_path])
        except Exception as e:
            print(f"⚠️  Could not open screenshot: {e}")

if __name__ == "__main__":
    main()