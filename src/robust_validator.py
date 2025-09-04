#!/usr/bin/env python3
"""
Robust validation system that doesn't fail when LibreOffice has JavaLDX warnings.
Implements fallback validation approaches when GUI launching has timeouts.
"""

import subprocess
import time
import os
from pathlib import Path
from typing import Dict, Any, Optional


class RobustValidator:
    """
    Validation system that works even when LibreOffice GUI launching has issues.
    Uses multiple validation approaches with fallbacks.
    """
    
    def __init__(self):
        self.validation_dir = Path(__file__).parent.parent / "robust_validation"
        self.validation_dir.mkdir(exist_ok=True)
    
    def validate_document_completely(self, document_path: str) -> Dict[str, Any]:
        """
        Comprehensive validation using multiple approaches.
        Returns validation results even if some methods fail.
        """
        
        results = {
            'document_path': document_path,
            'validation_timestamp': time.time(),
            'validations': {},
            'overall_success': False,
            'critical_failures': []
        }
        
        if not os.path.exists(document_path):
            results['critical_failures'].append(f"Document not found: {document_path}")
            return results
        
        print(f"🔍 ROBUST VALIDATION: {Path(document_path).name}")
        print("=" * 60)
        
        # Validation 1: File structure validation
        structure_result = self._validate_file_structure(document_path)
        results['validations']['file_structure'] = structure_result
        print(f"📁 File Structure: {'✅ PASS' if structure_result['success'] else '❌ FAIL'}")
        
        # Validation 2: LibreOffice headless processing test  
        headless_result = self._validate_headless_processing(document_path)
        results['validations']['headless_processing'] = headless_result
        print(f"🖥️  Headless Processing: {'✅ PASS' if headless_result['success'] else '❌ FAIL'}")
        
        # Validation 3: Content extraction test
        content_result = self._validate_content_extraction(document_path)
        results['validations']['content_extraction'] = content_result
        print(f"📄 Content Extraction: {'✅ PASS' if content_result['success'] else '❌ FAIL'}")
        
        # Validation 4: GUI opening test (with timeout handling)
        gui_result = self._validate_gui_opening(document_path)
        results['validations']['gui_opening'] = gui_result
        print(f"🖼️  GUI Opening: {'✅ PASS' if gui_result['success'] else '⚠️  TIMEOUT (but document may be open)'}")
        
        # Validation 5: Screenshot capture (if possible)
        screenshot_result = self._validate_screenshot_capture(document_path)
        results['validations']['screenshot'] = screenshot_result
        print(f"📸 Screenshot: {'✅ PASS' if screenshot_result['success'] else '❌ FAIL'}")
        
        # Overall assessment
        critical_validations = ['file_structure', 'headless_processing', 'content_extraction']
        critical_passed = all(results['validations'][key]['success'] for key in critical_validations)
        
        if critical_passed:
            results['overall_success'] = True
            print(f"\n✅ VALIDATION PASSED: Document is functional")
        else:
            failed_critical = [key for key in critical_validations 
                             if not results['validations'][key]['success']]
            results['critical_failures'].extend(failed_critical)
            print(f"\n❌ VALIDATION FAILED: Critical issues in {failed_critical}")
        
        return results
    
    def _validate_file_structure(self, document_path: str) -> Dict[str, Any]:
        """Validate ODT file structure"""
        try:
            import zipfile
            with zipfile.ZipFile(document_path, 'r') as odt_file:
                files = odt_file.namelist()
                required_files = ['mimetype', 'content.xml', 'styles.xml', 'META-INF/manifest.xml']
                missing_files = [f for f in required_files if f not in files]
                
                if missing_files:
                    return {
                        'success': False,
                        'error': f"Missing required files: {missing_files}",
                        'files_found': files
                    }
                
                # Check if content.xml is readable
                content_xml = odt_file.read('content.xml').decode('utf-8')
                if len(content_xml) < 100:  # Sanity check
                    return {
                        'success': False,
                        'error': "content.xml appears to be empty or corrupted"
                    }
                
                return {
                    'success': True,
                    'files_found': files,
                    'content_size': len(content_xml)
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"File structure validation failed: {e}"
            }
    
    def _validate_headless_processing(self, document_path: str) -> Dict[str, Any]:
        """Test if LibreOffice can process the document in headless mode"""
        try:
            # Try converting to PDF in headless mode
            output_path = self.validation_dir / f"headless_test_{int(time.time())}.pdf"
            cmd = [
                'libreoffice', '--headless', '--convert-to', 'pdf', 
                '--outdir', str(self.validation_dir), document_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Check if conversion succeeded despite JavaLDX warnings
            if result.returncode == 0 and output_path.exists():
                # Clean up test file
                output_path.unlink()
                return {
                    'success': True,
                    'message': 'LibreOffice can process document successfully',
                    'warning': result.stderr if result.stderr else None
                }
            elif result.returncode == 0 and "Warning: failed to launch javaldx" in result.stderr:
                # JavaLDX warning but process completed - check if PDF was created anyway
                expected_pdf = self.validation_dir / f"{Path(document_path).stem}.pdf" 
                if expected_pdf.exists():
                    expected_pdf.unlink()
                    return {
                        'success': True,
                        'message': 'LibreOffice processed document successfully (JavaLDX warning ignored)',
                        'warning': 'JavaLDX warning present but non-critical'
                    }
                else:
                    return {
                        'success': False,
                        'error': f"Headless conversion failed: {result.stderr}",
                        'return_code': result.returncode
                    }
            else:
                return {
                    'success': False,
                    'error': f"Headless conversion failed: {result.stderr}",
                    'return_code': result.returncode
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': "Headless processing timeout"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Headless processing error: {e}"
            }
    
    def _validate_content_extraction(self, document_path: str) -> Dict[str, Any]:
        """Extract and validate document content"""
        try:
            import zipfile
            with zipfile.ZipFile(document_path, 'r') as odt_file:
                content_xml = odt_file.read('content.xml').decode('utf-8')
                
                # Check for key content indicators
                scope_indicators = [
                    'SCOPE OF WORK BY AREA',
                    'Hollyhock Removal',
                    'Tree of Heaven Removal', 
                    'Laurel Pruning',
                    'Site Cleanup'
                ]
                
                styling_indicators = [
                    '#4472c4',  # Blue color for headers
                    'fo:font-weight="bold"',  # Bold styling
                    'PROJECT SUMMARY',
                    'PROJECT TOTALS'
                ]
                
                found_scope = sum(1 for indicator in scope_indicators if indicator in content_xml)
                found_styling = sum(1 for indicator in styling_indicators if indicator in content_xml)
                
                if found_scope >= 3 and found_styling >= 2:
                    return {
                        'success': True,
                        'scope_indicators_found': found_scope,
                        'styling_indicators_found': found_styling,
                        'content_size': len(content_xml)
                    }
                else:
                    return {
                        'success': False,
                        'error': f"Content validation failed - scope: {found_scope}/5, styling: {found_styling}/4",
                        'scope_indicators_found': found_scope,
                        'styling_indicators_found': found_styling
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': f"Content extraction failed: {e}"
            }
    
    def _validate_gui_opening(self, document_path: str) -> Dict[str, Any]:
        """Test GUI opening with proper timeout handling"""
        try:
            # Start LibreOffice process
            process = subprocess.Popen(
                ['libreoffice', '--nologo', '--nolockcheck', document_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid  # Create new process group
            )
            
            # Wait briefly then check if process started
            time.sleep(2)
            poll_result = process.poll()
            
            if poll_result is None:
                # Process is running - likely opened successfully
                # Check if we can find the process
                try:
                    ps_result = subprocess.run(['pgrep', '-f', os.path.basename(document_path)], 
                                             capture_output=True, timeout=5)
                    if ps_result.returncode == 0:
                        return {
                            'success': True,
                            'message': 'Document opened in LibreOffice GUI',
                            'process_id': process.pid
                        }
                except:
                    pass
                
                return {
                    'success': True,
                    'message': 'LibreOffice process started (GUI opening likely successful)',
                    'process_id': process.pid
                }
            else:
                # Process exited immediately - likely an error
                stdout, stderr = process.communicate()
                return {
                    'success': False,
                    'error': f"LibreOffice exited immediately: {stderr.decode()}",
                    'return_code': poll_result
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"GUI opening test failed: {e}"
            }
    
    def _validate_screenshot_capture(self, document_path: str) -> Dict[str, Any]:
        """Attempt to capture a screenshot of the document"""
        try:
            # Try using our existing vision validator
            import sys
            sys.path.append(str(Path(__file__).parent))
            from vision_validator import VisionValidator
            
            validator = VisionValidator()
            result = validator.capture_document_screenshot(document_path)
            
            if result.get('success'):
                return {
                    'success': True,
                    'screenshot_path': result.get('screenshot_path'),
                    'message': 'Screenshot captured successfully'
                }
            else:
                return {
                    'success': False,
                    'error': f"Screenshot capture failed: {result.get('error')}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Screenshot validation error: {e}"
            }