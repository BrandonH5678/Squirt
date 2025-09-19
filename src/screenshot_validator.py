#!/usr/bin/env python3
"""
Screenshot-based validation system for WaterWizard document generation.
Automatically captures document screenshots for Claude vision analysis.
"""

import subprocess
import time
import os
from pathlib import Path
from typing import Optional, Dict, Any
import tempfile


class ScreenshotValidator:
    """
    Handles screenshot capture and validation for LibreOffice documents
    """
    
    def __init__(self):
        self.screenshot_dir = Path(__file__).parent.parent / "validation_screenshots"
        self.screenshot_dir.mkdir(exist_ok=True)
    
    def capture_document_screenshot(self, odt_path: str) -> Optional[str]:
        """
        Capture a screenshot of an ODT document by opening it in LibreOffice GUI
        and taking a screenshot directly. This captures error dialogs and actual formatting.
        
        Args:
            odt_path: Path to the ODT file
            
        Returns:
            Path to the screenshot image, or None if failed
        """
        
        if not os.path.exists(odt_path):
            print(f"❌ ODT file not found: {odt_path}")
            return None
        
        try:
            # Open ODT in LibreOffice GUI and capture screenshot
            screenshot_path = self._capture_gui_screenshot(odt_path)
            if not screenshot_path:
                return None
            
            print(f"✅ Screenshot captured: {screenshot_path}")
            return screenshot_path
            
        except Exception as e:
            print(f"❌ Screenshot capture failed: {e}")
            return None
    
    def _capture_gui_screenshot(self, odt_path: str) -> Optional[str]:
        """Capture screenshot by opening ODT in LibreOffice GUI"""
        
        try:
            import subprocess
            import time
            
            # Kill any existing LibreOffice processes to avoid conflicts
            subprocess.run(['pkill', '-f', 'libreoffice'], capture_output=True)
            time.sleep(1)
            
            # Open LibreOffice with the ODT file
            process = subprocess.Popen([
                'libreoffice', '--writer', odt_path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for LibreOffice to fully load
            time.sleep(3)
            
            # Generate screenshot filename
            timestamp = int(time.time() * 1000)
            screenshot_name = f"document_capture_{timestamp}.png"
            screenshot_path = str(self.screenshot_dir / screenshot_name)
            
            # Capture screenshot using gnome-screenshot or scrot
            try:
                # Try gnome-screenshot first (more common on Ubuntu)
                result = subprocess.run([
                    'gnome-screenshot', '--window', '-f', screenshot_path
                ], capture_output=True, timeout=10)
                
                if result.returncode != 0:
                    # Fallback to full screen screenshot with scrot
                    result = subprocess.run([
                        'scrot', '-s', screenshot_path
                    ], capture_output=True, timeout=10)
                    
            except FileNotFoundError:
                # Fallback to ImageMagick import
                result = subprocess.run([
                    'import', screenshot_path
                ], capture_output=True, timeout=15)
            
            # Give a moment for screenshot to be saved
            time.sleep(0.5)
            
            # Close LibreOffice
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
            
            # Verify screenshot was created
            if os.path.exists(screenshot_path):
                return screenshot_path
            else:
                print(f"❌ Screenshot not created at: {screenshot_path}")
                return None
                
        except Exception as e:
            print(f"❌ GUI screenshot error: {e}")
            return None
    
    # Old PDF conversion methods removed - now using direct GUI screenshots for better validation
    
    def validate_with_vision(self, screenshot_path: str, validation_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare validation data for Claude vision analysis
        
        Args:
            screenshot_path: Path to the screenshot
            validation_criteria: What to check for
            
        Returns:
            Validation results structure
        """
        
        if not os.path.exists(screenshot_path):
            return {
                'success': False,
                'error': f'Screenshot not found: {screenshot_path}'
            }
        
        # For now, return the screenshot path and criteria for manual analysis
        # This will be extended to integrate with Claude's vision capabilities
        return {
            'success': True,
            'screenshot_path': screenshot_path,
            'criteria': validation_criteria,
            'ready_for_vision_analysis': True,
            'message': f'Screenshot ready for validation: {screenshot_path}'
        }


def test_screenshot_validator():
    """Test the screenshot validator with our fixed populated contract"""
    
    validator = ScreenshotValidator()
    
    # Test with our working ODT file
    test_odt = "/home/johnny5/Squirt/template_reference/fixed_populated_contract.odt"
    
    print("🧪 Testing screenshot validator...")
    print(f"📄 Input ODT: {test_odt}")
    
    # Capture screenshot
    screenshot_path = validator.capture_document_screenshot(test_odt)
    
    if screenshot_path:
        # Test validation structure
        criteria = {
            'blue_headers': 'Check for blue section headers (#4472c4)',
            'professional_layout': 'Verify clean, professional appearance',
            'content_accuracy': 'Ensure all placeholder data is populated',
            'typography': 'Check font sizes and hierarchy',
            'prepared_for_by': 'Verify prepared for/by table alignment'
        }
        
        validation_result = validator.validate_with_vision(screenshot_path, criteria)
        
        if validation_result['success']:
            print(f"✅ Validation system ready!")
            print(f"📸 Screenshot: {validation_result['screenshot_path']}")
            print(f"🔍 Ready for Claude vision analysis")
            return True
        else:
            print(f"❌ Validation setup failed: {validation_result.get('error', 'Unknown error')}")
            return False
    else:
        print("❌ Screenshot capture failed")
        return False


if __name__ == "__main__":
    success = test_screenshot_validator()
    if success:
        print("\n🎉 Screenshot validation system is ready for integration!")
    else:
        print("\n❌ Screenshot validation system needs debugging")