#!/usr/bin/env python3
"""
Unified Validation System for Squirt
Consolidates 4 separate validation systems into a single, comprehensive framework.

Previous Systems Consolidated:
1. VisionValidator - Screenshot capture and Claude Vision analysis
2. ScreenshotValidator - GUI screenshot and validation preparation
3. RobustValidator - Fallback validation with error handling
4. AutomatedValidator - Template content and compliance checking
"""

import subprocess
import time
import os
import json
import base64
import zipfile
import xml.etree.ElementTree as ET
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum

class ValidationLevel(Enum):
    """Validation levels for different use cases"""
    BASIC = "basic"           # File structure and content extraction only
    STANDARD = "standard"     # Basic + automated content validation
    COMPREHENSIVE = "comprehensive"  # Standard + visual validation
    PRODUCTION = "production" # Comprehensive + all quality checks

class ValidationResult:
    """Standardized validation result structure"""
    def __init__(self, success: bool, level: ValidationLevel, document_path: str):
        self.success = success
        self.level = level
        self.document_path = document_path
        self.timestamp = datetime.now().isoformat()
        self.checks = {}
        self.errors = []
        self.warnings = []
        self.screenshots = []
        self.metadata = {}

    def add_check(self, name: str, passed: bool, message: str = "", data: Any = None):
        """Add a validation check result"""
        self.checks[name] = {
            'passed': passed,
            'message': message,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }

    def add_error(self, error: str):
        """Add an error to the result"""
        self.errors.append(error)

    def add_warning(self, warning: str):
        """Add a warning to the result"""
        self.warnings.append(warning)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'success': self.success,
            'level': self.level.value,
            'document_path': self.document_path,
            'timestamp': self.timestamp,
            'checks': self.checks,
            'errors': self.errors,
            'warnings': self.warnings,
            'screenshots': self.screenshots,
            'metadata': self.metadata
        }

class UnifiedValidationSystem:
    """
    Unified validation system that consolidates all previous validation approaches
    """

    def __init__(self, squirt_root: str = "/home/johnny5/Squirt"):
        self.squirt_root = Path(squirt_root)
        self.screenshot_dir = self.squirt_root / "validation_screenshots"
        self.screenshot_dir.mkdir(exist_ok=True)
        self.validation_history_dir = self.squirt_root / "validation_history"
        self.validation_history_dir.mkdir(exist_ok=True)

    def validate_document(self,
                         document_path: str,
                         validation_level: ValidationLevel = ValidationLevel.STANDARD,
                         template_path: Optional[str] = None,
                         context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Main validation entry point - single method for all validation needs

        Args:
            document_path: Path to document to validate
            validation_level: Level of validation to perform
            template_path: Optional template used to generate document
            context: Additional context for validation

        Returns:
            ValidationResult with comprehensive validation results
        """

        result = ValidationResult(False, validation_level, document_path)

        print(f"🔍 UNIFIED VALIDATION: {Path(document_path).name}")
        print(f"📊 Level: {validation_level.value.upper()}")
        print("=" * 60)

        # Phase 1: Basic validation (always performed)
        if not self._run_basic_validation(result):
            print("❌ Basic validation failed - stopping")
            return result

        # Phase 2: Standard validation (for STANDARD and above)
        if validation_level in [ValidationLevel.STANDARD, ValidationLevel.COMPREHENSIVE, ValidationLevel.PRODUCTION]:
            if not self._run_standard_validation(result, template_path):
                print("⚠️  Standard validation issues found")

        # Phase 3: Comprehensive validation (for COMPREHENSIVE and above)
        if validation_level in [ValidationLevel.COMPREHENSIVE, ValidationLevel.PRODUCTION]:
            if not self._run_comprehensive_validation(result, context):
                print("⚠️  Comprehensive validation issues found")

        # Phase 4: Production validation (for PRODUCTION only)
        if validation_level == ValidationLevel.PRODUCTION:
            if not self._run_production_validation(result, template_path, context):
                print("⚠️  Production validation issues found")

        # Final assessment
        result.success = self._assess_overall_success(result)

        # Save validation history
        self._save_validation_history(result)

        print(f"\n{'✅ VALIDATION PASSED' if result.success else '❌ VALIDATION FAILED'}")
        print(f"📊 Checks: {len([c for c in result.checks.values() if c['passed']])}/{len(result.checks)} passed")

        return result

    def _run_basic_validation(self, result: ValidationResult) -> bool:
        """Phase 1: Basic file structure and accessibility validation"""

        # Check 1: File existence
        if not os.path.exists(result.document_path):
            result.add_error(f"Document not found: {result.document_path}")
            result.add_check("file_exists", False, "Document file not found")
            return False
        result.add_check("file_exists", True, "Document file found")

        # Check 2: ODT file structure
        try:
            with zipfile.ZipFile(result.document_path, 'r') as odt_file:
                files = odt_file.namelist()
                required_files = ['mimetype', 'content.xml', 'styles.xml', 'META-INF/manifest.xml']
                missing_files = [f for f in required_files if f not in files]

                if missing_files:
                    result.add_check("odt_structure", False, f"Missing files: {missing_files}")
                    result.add_error(f"Invalid ODT structure: missing {missing_files}")
                    return False
                else:
                    result.add_check("odt_structure", True, "Valid ODT file structure", files)

        except Exception as e:
            result.add_check("odt_structure", False, f"ODT structure check failed: {e}")
            result.add_error(f"Cannot read ODT file: {e}")
            return False

        # Check 3: Content extraction
        try:
            content = self._extract_odt_content(result.document_path)
            if len(content) < 100:
                result.add_check("content_extraction", False, "Document appears empty or corrupted")
                result.add_warning("Document content is suspiciously short")
            else:
                result.add_check("content_extraction", True, f"Content extracted: {len(content)} characters",
                               {'content_length': len(content), 'preview': content[:200]})
                result.metadata['content_length'] = len(content)

        except Exception as e:
            result.add_check("content_extraction", False, f"Content extraction failed: {e}")
            result.add_error(f"Cannot extract document content: {e}")
            return False

        # Check 4: LibreOffice headless processing
        try:
            test_pdf = self.validation_history_dir / f"test_{int(time.time())}.pdf"
            cmd = ['libreoffice', '--headless', '--convert-to', 'pdf',
                   '--outdir', str(self.validation_history_dir), result.document_path]

            process_result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if process_result.returncode == 0:
                result.add_check("headless_processing", True, "LibreOffice can process document")
                # Clean up test file
                expected_pdf = self.validation_history_dir / f"{Path(result.document_path).stem}.pdf"
                if expected_pdf.exists():
                    expected_pdf.unlink()
            else:
                result.add_check("headless_processing", False, f"Headless processing failed: {process_result.stderr}")
                result.add_warning("LibreOffice headless processing failed")

        except subprocess.TimeoutExpired:
            result.add_check("headless_processing", False, "Headless processing timeout")
            result.add_warning("LibreOffice headless processing timeout")
        except Exception as e:
            result.add_check("headless_processing", False, f"Headless processing error: {e}")
            result.add_warning(f"LibreOffice headless processing error: {e}")

        return True

    def _run_standard_validation(self, result: ValidationResult, template_path: Optional[str]) -> bool:
        """Phase 2: Standard content and compliance validation"""

        content = self._extract_odt_content(result.document_path)

        # Check 1: Currency formatting
        currency_pattern = r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
        currency_matches = re.findall(currency_pattern, content)
        if currency_matches:
            result.add_check("currency_format", True, f"Found {len(currency_matches)} currency values", currency_matches)
        else:
            result.add_check("currency_format", False, "No properly formatted currency found")
            result.add_error("No currency formatting found in document")

        # Check 2: Company information
        company_checks = {
            'company_name': 'waterwizard' in content.lower(),
            'license_number': 'ccb' in content.lower(),
            'phone_number': re.search(r'\(\d{3}\)\s*\d{3}-\d{4}', content) is not None,
            'email': '@' in content
        }

        passed_company_checks = sum(company_checks.values())
        if passed_company_checks >= 3:
            result.add_check("company_info", True, f"Company info present: {passed_company_checks}/4 checks", company_checks)
        else:
            result.add_check("company_info", False, f"Insufficient company info: {passed_company_checks}/4 checks", company_checks)
            result.add_warning("Company information incomplete")

        # Check 3: Required sections
        required_sections = ['materials', 'labor', 'total', 'project']
        found_sections = [section for section in required_sections if section in content.lower()]
        if len(found_sections) >= 3:
            result.add_check("required_sections", True, f"Found {len(found_sections)}/4 sections", found_sections)
        else:
            result.add_check("required_sections", False, f"Missing sections: {len(found_sections)}/4", found_sections)
            result.add_warning("Some required sections missing")

        # Check 4: Template content verification (CRITICAL)
        if template_path:
            template_result = self._verify_template_usage(result.document_path, template_path, content)
            if template_result['used_template']:
                result.add_check("template_usage", True, "Template data appears to be used", template_result)
            else:
                result.add_check("template_usage", False, "CRITICAL: Template data not used - hardcoded content detected", template_result)
                result.add_error("CRITICAL: Document contains hardcoded content instead of template data")

        return len(result.errors) == 0

    def _run_comprehensive_validation(self, result: ValidationResult, context: Optional[Dict[str, Any]]) -> bool:
        """Phase 3: Visual validation and screenshot analysis"""

        # Check 1: GUI opening test
        gui_result = self._test_gui_opening(result.document_path)
        result.add_check("gui_opening", gui_result['success'], gui_result.get('message', ''), gui_result)

        # Check 2: Screenshot capture
        screenshot_result = self._capture_comprehensive_screenshot(result.document_path)
        if screenshot_result['success']:
            result.add_check("screenshot_capture", True, "Screenshot captured successfully", screenshot_result)
            result.screenshots = screenshot_result.get('screenshots', [])
            result.metadata['screenshot_info'] = screenshot_result
        else:
            result.add_check("screenshot_capture", False, f"Screenshot failed: {screenshot_result.get('error')}")
            result.add_warning("Visual validation not possible - screenshot capture failed")

        # Check 3: Visual analysis preparation
        if result.screenshots:
            vision_data = self._prepare_vision_analysis(result.screenshots)
            result.add_check("vision_preparation", True, "Ready for Claude Vision analysis", vision_data)
            result.metadata['vision_data'] = vision_data
        else:
            result.add_check("vision_preparation", False, "No screenshots available for vision analysis")

        return True

    def _run_production_validation(self, result: ValidationResult, template_path: Optional[str], context: Optional[Dict[str, Any]]) -> bool:
        """Phase 4: Production-ready quality assurance"""

        # Check 1: Professional formatting standards
        content = self._extract_odt_content(result.document_path)

        # Advanced formatting checks
        formatting_score = 0
        formatting_checks = {
            'blue_headers': '#4472c4' in content,
            'bold_styling': 'fo:font-weight="bold"' in content,
            'proper_tables': 'table:table' in content,
            'section_headers': 'PROJECT SUMMARY' in content and 'PROJECT TOTALS' in content
        }

        for check, passed in formatting_checks.items():
            if passed:
                formatting_score += 25

        result.add_check("professional_formatting", formatting_score >= 75,
                        f"Formatting score: {formatting_score}/100", formatting_checks)

        # Check 2: Content quality assessment
        quality_indicators = [
            len(content) > 2000,  # Substantial content
            content.count('$') >= 3,  # Multiple price points
            'SCOPE OF WORK' in content.upper(),  # Proper scope definition
            any(word in content.lower() for word in ['installation', 'removal', 'pruning', 'cleanup'])  # Service indicators
        ]

        quality_score = sum(quality_indicators) * 25
        result.add_check("content_quality", quality_score >= 75, f"Quality score: {quality_score}/100", quality_indicators)

        # Check 3: Template consistency (if template provided)
        if template_path:
            consistency_result = self._verify_template_consistency(result.document_path, template_path)
            result.add_check("template_consistency", consistency_result['consistent'],
                           consistency_result['message'], consistency_result)

        # Check 4: Client-ready assessment
        client_ready_checks = [
            result.checks.get('currency_format', {}).get('passed', False),
            result.checks.get('company_info', {}).get('passed', False),
            result.checks.get('professional_formatting', {}).get('passed', False),
            len(result.errors) == 0
        ]

        client_ready = all(client_ready_checks)
        result.add_check("client_ready", client_ready,
                        "Ready for client delivery" if client_ready else "Requires fixes before client delivery",
                        client_ready_checks)

        return client_ready

    def _extract_odt_content(self, odt_path: str) -> str:
        """Extract text content from ODT file"""
        try:
            with zipfile.ZipFile(odt_path, 'r') as z:
                content_xml = z.read('content.xml')
                # Return raw XML for both text extraction and formatting analysis
                return content_xml.decode('utf-8')
        except Exception as e:
            return f"Error reading ODT: {str(e)}"

    def _verify_template_usage(self, document_path: str, template_path: str, content: str) -> Dict[str, Any]:
        """Verify that document actually uses template data (CRITICAL CHECK)"""

        try:
            with open(template_path, 'r') as f:
                template_data = json.load(f)
        except Exception as e:
            return {'used_template': False, 'error': f"Cannot load template: {e}"}

        # Check for template-specific content
        template_indicators = []

        # Check for template description/title elements
        if 'description' in template_data:
            desc_words = template_data['description'].split()
            template_indicators.extend([word for word in desc_words if len(word) > 4])

        # Check for material names from template
        if 'materials' in template_data:
            for material in template_data['materials']:
                if 'name' in material:
                    template_indicators.append(material['name'])

        # Check for labor items from template
        if 'labor' in template_data:
            for labor in template_data['labor']:
                if 'description' in labor:
                    template_indicators.append(labor['description'])

        # Look for template indicators in content
        found_indicators = [indicator for indicator in template_indicators
                           if indicator.lower() in content.lower()]

        # CRITICAL: Check for hardcoded Liam Smith content
        hardcoded_indicators = [
            'liam smith', 'tree of heaven', 'hollyhock removal',
            'laurel hedge pruning', 'site cleanup', '$777.50'
        ]

        found_hardcoded = [indicator for indicator in hardcoded_indicators
                          if indicator.lower() in content.lower()]

        if found_hardcoded:
            return {
                'used_template': False,
                'reason': 'hardcoded_content_detected',
                'hardcoded_content': found_hardcoded,
                'template_indicators_found': found_indicators,
                'message': f"CRITICAL: Hardcoded content detected: {found_hardcoded}"
            }

        if len(found_indicators) >= 2:
            return {
                'used_template': True,
                'template_indicators_found': found_indicators,
                'confidence': len(found_indicators),
                'message': f"Template content found: {found_indicators}"
            }
        else:
            return {
                'used_template': False,
                'reason': 'insufficient_template_content',
                'template_indicators_found': found_indicators,
                'message': f"Insufficient template content found: {found_indicators}"
            }

    def _test_gui_opening(self, document_path: str) -> Dict[str, Any]:
        """Test if document opens in LibreOffice GUI"""
        try:
            process = subprocess.Popen(
                ['libreoffice', '--nologo', '--nolockcheck', document_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            time.sleep(2)
            poll_result = process.poll()

            if poll_result is None:
                return {'success': True, 'message': 'Document opened successfully', 'process_id': process.pid}
            else:
                stdout, stderr = process.communicate()
                return {'success': False, 'message': f"LibreOffice exited: {stderr.decode()}", 'return_code': poll_result}

        except Exception as e:
            return {'success': False, 'message': f"GUI opening test failed: {e}"}

    def _capture_comprehensive_screenshot(self, document_path: str) -> Dict[str, Any]:
        """Capture comprehensive screenshot with multiple methods"""

        try:
            # Method 1: Try direct GUI screenshot
            screenshot_info = self._capture_gui_screenshot(document_path)
            if screenshot_info['success']:
                return screenshot_info

            # Method 2: Try headless screenshot (if GUI fails)
            return self._capture_fallback_screenshot(document_path)

        except Exception as e:
            return {'success': False, 'error': f"Screenshot capture failed: {e}"}

    def _capture_gui_screenshot(self, document_path: str) -> Dict[str, Any]:
        """Capture screenshot by opening document in GUI"""

        try:
            # Kill existing LibreOffice processes
            subprocess.run(['pkill', '-f', 'libreoffice'], capture_output=True)
            time.sleep(1)

            # Open document
            process = subprocess.Popen(['libreoffice', '--writer', document_path],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(3)

            # Generate screenshot filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = self.screenshot_dir / f"unified_validation_{timestamp}.png"

            # Try multiple screenshot methods
            screenshot_methods = [
                ['import', '-window', 'root', str(screenshot_path)],
                ['gnome-screenshot', '-w', '-f', str(screenshot_path)],
                ['scrot', str(screenshot_path)]
            ]

            for method in screenshot_methods:
                try:
                    result = subprocess.run(method, capture_output=True, timeout=10)
                    if result.returncode == 0 and screenshot_path.exists():
                        # Encode for vision analysis
                        with open(screenshot_path, 'rb') as f:
                            base64_image = base64.b64encode(f.read()).decode('utf-8')

                        # Close LibreOffice
                        try:
                            process.terminate()
                            process.wait(timeout=3)
                        except:
                            process.kill()

                        return {
                            'success': True,
                            'screenshots': [{
                                'path': str(screenshot_path),
                                'base64': base64_image,
                                'method': method[0],
                                'timestamp': timestamp
                            }],
                            'method_used': method[0]
                        }
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue

            # Clean up process if screenshot failed
            try:
                process.terminate()
            except:
                process.kill()

            return {'success': False, 'error': 'All screenshot methods failed'}

        except Exception as e:
            return {'success': False, 'error': f"GUI screenshot error: {e}"}

    def _capture_fallback_screenshot(self, document_path: str) -> Dict[str, Any]:
        """Fallback screenshot method"""
        return {'success': False, 'error': 'Fallback screenshot not implemented'}

    def _prepare_vision_analysis(self, screenshots: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare screenshots for Claude Vision analysis"""

        vision_prompt = """Please analyze this WaterWizard document and validate:

**CRITICAL REQUIREMENTS:**
1. **Professional Formatting**: Clean layout, proper spacing, consistent typography
2. **Blue Headers**: Section headers should be blue (#4472c4)
3. **Content Population**: All template data properly populated (no {{PLACEHOLDERS}})
4. **Currency Formatting**: All dollar amounts properly formatted ($X,XXX.XX)
5. **Company Branding**: Consistent WaterWizard professional appearance
6. **Template Usage**: Verify document uses actual template data, not hardcoded content

**ASSESSMENT:**
- Rate each element: PASS/FAIL
- Overall document score: 1-10
- Ready for client delivery: Yes/No
- Specific issues requiring correction"""

        return {
            'ready_for_claude_vision': True,
            'prompt': vision_prompt,
            'screenshots': screenshots,
            'analysis_type': 'comprehensive_document_validation'
        }

    def _verify_template_consistency(self, document_path: str, template_path: str) -> Dict[str, Any]:
        """Verify document is consistent with template specifications"""
        # This would implement advanced template consistency checking
        return {'consistent': True, 'message': 'Template consistency check not fully implemented'}

    def _assess_overall_success(self, result: ValidationResult) -> bool:
        """Assess overall validation success based on level and checks"""

        critical_checks = ['file_exists', 'odt_structure', 'content_extraction']

        # All critical checks must pass
        for check in critical_checks:
            if not result.checks.get(check, {}).get('passed', False):
                return False

        # No critical errors allowed
        if result.errors:
            return False

        # Level-specific requirements
        if result.level == ValidationLevel.PRODUCTION:
            production_checks = ['currency_format', 'company_info', 'client_ready']
            for check in production_checks:
                if not result.checks.get(check, {}).get('passed', False):
                    return False

        return True

    def _save_validation_history(self, result: ValidationResult):
        """Save validation result to history"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_file = self.validation_history_dir / f"unified_validation_{timestamp}.json"

        try:
            with open(history_file, 'w') as f:
                json.dump(result.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save validation history: {e}")

# Convenience functions for common validation scenarios
def validate_document_basic(document_path: str) -> ValidationResult:
    """Quick basic validation for development"""
    validator = UnifiedValidationSystem()
    return validator.validate_document(document_path, ValidationLevel.BASIC)

def validate_document_production(document_path: str, template_path: str = None) -> ValidationResult:
    """Full production validation for client delivery"""
    validator = UnifiedValidationSystem()
    return validator.validate_document(document_path, ValidationLevel.PRODUCTION, template_path)

def validate_with_visual(document_path: str, template_path: str = None) -> ValidationResult:
    """Comprehensive validation with visual analysis"""
    validator = UnifiedValidationSystem()
    return validator.validate_document(document_path, ValidationLevel.COMPREHENSIVE, template_path)

# Test function
def test_unified_validation():
    """Test the unified validation system"""

    print("🧪 Testing Unified Validation System")
    print("=" * 50)

    test_doc = "/home/johnny5/Squirt/test_validation_samples/drip_zone_shrubs.odt"

    if not os.path.exists(test_doc):
        print(f"❌ Test document not found: {test_doc}")
        return False

    validator = UnifiedValidationSystem()

    # Test each validation level
    levels = [ValidationLevel.BASIC, ValidationLevel.STANDARD, ValidationLevel.COMPREHENSIVE]

    for level in levels:
        print(f"\n📊 Testing {level.value.upper()} validation...")
        result = validator.validate_document(test_doc, level)

        print(f"Result: {'✅ PASSED' if result.success else '❌ FAILED'}")
        print(f"Checks: {len([c for c in result.checks.values() if c['passed']])}/{len(result.checks)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Warnings: {len(result.warnings)}")

    return True

if __name__ == "__main__":
    test_unified_validation()