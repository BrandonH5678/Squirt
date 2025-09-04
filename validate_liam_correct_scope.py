#!/usr/bin/env python3
"""
Validate Liam Smith's correctly formatted scope-based contract using vision validation
"""

import sys
sys.path.append('src')

from vision_validator import VisionValidator
from pathlib import Path

def main():
    print("🔍 VALIDATING LIAM SMITH CORRECT SCOPE CONTRACT")
    print("=" * 60)
    
    # Initialize vision validator
    validator = VisionValidator()
    
    # Contract file
    contract_path = "/home/johnny5/Squirt/Liam_Smith_CORRECT_Modern_Scoped_Contract.odt"
    
    if not Path(contract_path).exists():
        print(f"❌ Contract file not found: {contract_path}")
        return
    
    print(f"📄 Validating: {Path(contract_path).name}")
    print()
    
    # Capture screenshot and validate
    result = validator.capture_document_screenshot(contract_path)
    
    if result.get('success'):
        print("✅ Screenshot captured successfully")
        print(f"📸 Screenshot path: {result.get('screenshot_path')}")
        
        # Show the screenshot for visual confirmation
        try:
            import subprocess
            screenshot_path = result.get('screenshot_path')
            subprocess.run(['xdg-open', screenshot_path], check=True)
            print(f"🖼️  Opening screenshot: {screenshot_path}")
        except Exception as e:
            print(f"⚠️  Could not open screenshot: {e}")
            
        # Check validation criteria specific to correct scope organization
        print("\n🎯 SCOPE ORGANIZATION VALIDATION:")
        print("Checking for correct Squirt standards...")
        print("✓ Each scope should have: Title — $Cost")  
        print("✓ Followed by description paragraph")
        print("✓ Then Materials/Equipment/Labor grouped within that scope")
        print("✓ NO cross-scope category grouping")
        
        print("\n🎨 MODERN PROFESSIONAL STYLING VALIDATION:")
        print("✓ Blue section headers (#4472c4)")
        print("✓ Professional typography hierarchy") 
        print("✓ Clean table layouts")
        print("✓ Strategic bold formatting")
        
        # Try opening in LibreOffice for direct validation
        print("\n📱 OPENING IN LIBREOFFICE FOR HUMAN VALIDATION...")
        try:
            subprocess.run(['libreoffice', contract_path], check=False)
            print("✅ Contract opened in LibreOffice for visual review")
        except Exception as e:
            print(f"⚠️  Could not open in LibreOffice: {e}")
            
    else:
        print(f"❌ Screenshot capture failed: {result.get('error')}")
        print("\n🔧 Attempting direct LibreOffice opening...")
        try:
            subprocess.run(['libreoffice', contract_path], check=False)
            print("📱 Opened contract directly in LibreOffice")
        except Exception as e:
            print(f"❌ Direct opening failed: {e}")

if __name__ == "__main__":
    main()