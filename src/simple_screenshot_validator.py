#!/usr/bin/env python3
"""
Simple screenshot validator that uses existing PDFs for validation workflow.
Focus on integrating with Claude vision analysis rather than complex PDF conversion.
"""

import subprocess
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any


class SimpleScreenshotValidator:
    """
    Simple screenshot validator for WaterWizard documents
    """
    
    def __init__(self):
        self.screenshot_dir = Path(__file__).parent.parent / "validation_screenshots"
        self.screenshot_dir.mkdir(exist_ok=True)
    
    def prepare_for_visual_validation(self, odt_path: str) -> Dict[str, Any]:
        """
        Prepare a document for visual validation by creating PDF and opening it.
        Returns information for Claude vision analysis.
        
        Args:
            odt_path: Path to the ODT file
            
        Returns:
            Dictionary with validation information
        """
        
        if not os.path.exists(odt_path):
            return {
                'success': False,
                'error': f'ODT file not found: {odt_path}'
            }
        
        try:
            # Convert to PDF for consistent display
            pdf_path = self._ensure_pdf_exists(odt_path)
            
            if pdf_path:
                # Open the PDF for human review
                self._open_document_for_review(pdf_path)
                
                return {
                    'success': True,
                    'odt_path': odt_path,
                    'pdf_path': pdf_path,
                    'message': 'Document opened for visual validation',
                    'next_steps': [
                        'Document is now open in LibreOffice/PDF viewer',
                        'Human can review visual styling and formatting',
                        'Take screenshot if needed for Claude vision analysis',
                        'Report validation results back to system'
                    ],
                    'validation_checklist': self._get_validation_checklist()
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to create PDF for validation'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Validation preparation failed: {e}'
            }
    
    def _ensure_pdf_exists(self, odt_path: str) -> Optional[str]:
        """Ensure PDF version exists, create if needed"""
        
        odt_path_obj = Path(odt_path)
        pdf_path = odt_path_obj.parent / f"{odt_path_obj.stem}.pdf"
        
        # If PDF already exists and is newer than ODT, use it
        if pdf_path.exists():
            odt_mtime = os.path.getmtime(odt_path)
            pdf_mtime = os.path.getmtime(pdf_path)
            
            if pdf_mtime >= odt_mtime:
                print(f"✅ Using existing PDF: {pdf_path}")
                return str(pdf_path)
        
        # Create new PDF
        try:
            result = subprocess.run([
                'libreoffice', '--headless', '--convert-to', 'pdf',
                '--outdir', str(odt_path_obj.parent), odt_path
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and pdf_path.exists():
                print(f"✅ Created PDF: {pdf_path}")
                return str(pdf_path)
            else:
                print(f"❌ PDF creation failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("❌ LibreOffice PDF conversion timed out")
            return None
        except Exception as e:
            print(f"❌ PDF creation error: {e}")
            return None
    
    def _open_document_for_review(self, document_path: str):
        """Open document for human visual review"""
        
        try:
            # Open document in background
            subprocess.Popen([
                'libreoffice', document_path
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            print(f"📖 Opened document for review: {document_path}")
            
        except Exception as e:
            print(f"❌ Failed to open document: {e}")
    
    def _get_validation_checklist(self) -> Dict[str, str]:
        """Get the validation checklist for WaterWizard documents"""
        
        return {
            'blue_headers': 'PROJECT SUMMARY, PROJECT TOTALS sections should have blue color (#4472c4)',
            'typography': 'Title should be 16pt bold, headers should be 12pt blue',
            'prepared_blocks': 'Prepared for/by blocks should be aligned in table format',
            'content_populated': 'All {{PLACEHOLDER}} text should be replaced with real data',
            'professional_appearance': 'Overall document should look clean and professional',
            'line_breaks': 'Address fields should have proper line breaks (not \\n text)',
            'totals_formatting': 'Dollar amounts should be properly formatted with 2 decimals',
            'branding': 'WaterWizard branding should be consistent throughout'
        }
    
    def create_validation_report(self, validation_results: Dict[str, bool]) -> str:
        """Create a validation report from human feedback"""
        
        total_checks = len(validation_results)
        passed_checks = sum(1 for result in validation_results.values() if result)
        
        report = f"📋 VALIDATION REPORT\n"
        report += f"=" * 50 + "\n"
        report += f"Document validation results: {passed_checks}/{total_checks} checks passed\n\n"
        
        checklist = self._get_validation_checklist()
        
        for check_key, passed in validation_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            description = checklist.get(check_key, check_key)
            report += f"{status}: {description}\n"
        
        report += f"\n" + "=" * 50 + "\n"
        
        if passed_checks == total_checks:
            report += "🎉 DOCUMENT APPROVED: Ready for client delivery!\n"
        else:
            report += f"⚠️  DOCUMENT NEEDS WORK: {total_checks - passed_checks} issues to resolve\n"
        
        return report


def test_simple_validator():
    """Test the simple validation workflow"""
    
    validator = SimpleScreenshotValidator()
    
    # Test with our working ODT file
    test_odt = "/home/johnny5/Squirt/template_reference/fixed_populated_contract.odt"
    
    print("🧪 Testing simple screenshot validator...")
    print(f"📄 Input ODT: {test_odt}")
    
    # Prepare for validation
    result = validator.prepare_for_visual_validation(test_odt)
    
    if result['success']:
        print(f"✅ Validation system ready!")
        print(f"📋 Validation checklist:")
        for key, description in result['validation_checklist'].items():
            print(f"  • {description}")
        
        print(f"\n📖 Document opened for review")
        print(f"🔍 Next steps:")
        for step in result['next_steps']:
            print(f"  → {step}")
        
        # Simulate validation results (in real use, human would provide these)
        sample_results = {
            'blue_headers': True,
            'typography': True, 
            'prepared_blocks': False,  # We know this needs work
            'content_populated': True,
            'professional_appearance': True,
            'line_breaks': True,
            'totals_formatting': True,
            'branding': True
        }
        
        print("\n" + validator.create_validation_report(sample_results))
        
        return True
    else:
        print(f"❌ Validation preparation failed: {result.get('error', 'Unknown error')}")
        return False


if __name__ == "__main__":
    success = test_simple_validator()
    if success:
        print("\n🎉 Simple validation system is working!")
    else:
        print("\n❌ Simple validation system needs debugging")