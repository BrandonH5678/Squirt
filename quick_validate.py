#!/usr/bin/env python3
import sys
sys.path.append('src')

from vision_validator import VisionValidator
from pathlib import Path

# Quick validation
validator = VisionValidator()
contract_path = "/home/johnny5/Squirt/Liam_Smith_CORRECT_Modern_Scoped_Contract.odt"

print("📸 Taking screenshot of corrected contract...")
result = validator.capture_document_screenshot(contract_path)

if result.get('success'):
    screenshot_path = result.get('screenshot_path')
    print(f"✅ Screenshot saved: {screenshot_path}")
    
    # Display the screenshot
    import subprocess
    subprocess.run(['xdg-open', screenshot_path])
else:
    print(f"❌ Screenshot failed: {result.get('error')}")