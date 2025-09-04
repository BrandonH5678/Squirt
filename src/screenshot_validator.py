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
        Capture a screenshot of an ODT document by converting to PDF first,
        then using Python to create a visual representation.
        
        Args:
            odt_path: Path to the ODT file
            
        Returns:
            Path to the screenshot image, or None if failed
        """
        
        if not os.path.exists(odt_path):
            print(f"❌ ODT file not found: {odt_path}")
            return None
        
        try:
            # Step 1: Convert ODT to PDF using headless LibreOffice
            pdf_path = self._convert_odt_to_pdf(odt_path)
            if not pdf_path:
                return None
            
            # Step 2: Convert PDF to image using Python
            screenshot_path = self._convert_pdf_to_image(pdf_path)
            if not screenshot_path:
                return None
            
            print(f"✅ Screenshot captured: {screenshot_path}")
            return screenshot_path
            
        except Exception as e:
            print(f"❌ Screenshot capture failed: {e}")
            return None
    
    def _convert_odt_to_pdf(self, odt_path: str) -> Optional[str]:
        """Convert ODT to PDF using headless LibreOffice"""
        
        try:
            # Create temporary directory for PDF
            temp_dir = tempfile.mkdtemp()
            
            # Run LibreOffice headless conversion
            result = subprocess.run([
                'libreoffice', '--headless', '--convert-to', 'pdf',
                '--outdir', temp_dir, odt_path
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"❌ LibreOffice conversion failed: {result.stderr}")
                return None
            
            # Find the generated PDF file
            odt_name = Path(odt_path).stem
            pdf_path = os.path.join(temp_dir, f"{odt_name}.pdf")
            
            if os.path.exists(pdf_path):
                return pdf_path
            else:
                print(f"❌ PDF file not created at expected location: {pdf_path}")
                return None
                
        except subprocess.TimeoutExpired:
            print("❌ LibreOffice conversion timed out")
            return None
        except Exception as e:
            print(f"❌ PDF conversion error: {e}")
            return None
    
    def _convert_pdf_to_image(self, pdf_path: str) -> Optional[str]:
        """Convert PDF to image using Python libraries"""
        
        try:
            # Try using pdf2image if available, fallback to basic methods
            try:
                from pdf2image import convert_from_path
                
                # Convert first page of PDF to image
                images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=150)
                
                if images:
                    # Save the image
                    timestamp = int(time.time())
                    screenshot_path = self.screenshot_dir / f"document_screenshot_{timestamp}.png"
                    images[0].save(screenshot_path, 'PNG')
                    return str(screenshot_path)
                    
            except ImportError:
                print("📦 pdf2image not available, trying alternative approach...")
                return self._fallback_pdf_screenshot(pdf_path)
            
        except Exception as e:
            print(f"❌ PDF to image conversion failed: {e}")
            return self._fallback_pdf_screenshot(pdf_path)
    
    def _fallback_pdf_screenshot(self, pdf_path: str) -> Optional[str]:
        """Fallback method for PDF screenshot using system tools"""
        
        # Try using LibreOffice to open and then system screenshot
        try:
            # Start LibreOffice with the PDF
            process = subprocess.Popen([
                'libreoffice', '--draw', pdf_path
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Give it time to open
            time.sleep(3)
            
            # Try Python screenshot of the screen
            try:
                import pyautogui
                timestamp = int(time.time())
                screenshot_path = self.screenshot_dir / f"screen_capture_{timestamp}.png"
                
                # Take a screenshot
                screenshot = pyautogui.screenshot()
                screenshot.save(str(screenshot_path))
                
                # Close LibreOffice
                process.terminate()
                
                return str(screenshot_path)
                
            except ImportError:
                print("📦 pyautogui not available for screen capture")
                process.terminate()
                return None
                
        except Exception as e:
            print(f"❌ Fallback screenshot failed: {e}")
            return None
    
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