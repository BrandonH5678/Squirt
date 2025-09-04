#!/usr/bin/env python3
"""
Human-in-the-loop validation helper for Squirt document generators
Provides consistent methods for opening documents for human validation
"""

import subprocess
import os
import time
from typing import Optional, Dict, Any

class HumanValidationHelper:
    """Helper class for consistent human-in-the-loop document validation"""
    
    def __init__(self):
        self.validation_methods = [
            self._try_libreoffice_gui,
            self._try_xdg_open,
            self._try_manual_instructions
        ]
    
    def open_for_validation(self, file_path: str, document_type: str = "document") -> bool:
        """
        Open document for human validation using the most reliable method available
        
        Args:
            file_path: Path to the document to open
            document_type: Type of document (invoice, estimate, contract) for user messaging
            
        Returns:
            bool: True if document was opened or instructions provided, False on error
        """
        
        if not os.path.exists(file_path):
            print(f"❌ Document not found: {file_path}")
            return False
        
        print(f"📄 Opening {document_type} for human validation...")
        print(f"   File: {file_path}")
        
        # Try each method until one works
        for method in self.validation_methods:
            if method(file_path, document_type):
                return True
        
        print("❌ All opening methods failed")
        return False
    
    def _try_libreoffice_gui(self, file_path: str, document_type: str) -> bool:
        """Try to open with LibreOffice GUI"""
        try:
            # Multiple LibreOffice opening approaches
            commands = [
                ['libreoffice', file_path],
                ['libreoffice', '--writer', file_path],
                ['soffice', file_path]
            ]
            
            for cmd in commands:
                try:
                    # Start LibreOffice in background
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        env=dict(os.environ, DISPLAY=':0')
                    )
                    
                    # Give it time to start
                    time.sleep(3)
                    
                    # Check if GUI process is running
                    check_result = subprocess.run(
                        ['pgrep', '-f', 'soffice.*(?!.*headless)'],
                        capture_output=True
                    )
                    
                    if check_result.returncode == 0:
                        print(f"✅ LibreOffice opened with: {' '.join(cmd)}")
                        print(f"👁️ Please validate the {document_type} in LibreOffice")
                        return True
                        
                except Exception:
                    continue
            
            return False
            
        except Exception as e:
            print(f"⚠️ LibreOffice GUI failed: {e}")
            return False
    
    def _try_xdg_open(self, file_path: str, document_type: str) -> bool:
        """Try to open with system default application"""
        try:
            subprocess.Popen(
                ['xdg-open', file_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            print(f"✅ Document opened with system default application")
            print(f"👁️ Please validate the {document_type} in your default ODT viewer")
            return True
            
        except Exception as e:
            print(f"⚠️ xdg-open failed: {e}")
            return False
    
    def _try_manual_instructions(self, file_path: str, document_type: str) -> bool:
        """Provide manual opening instructions as fallback"""
        print(f"📋 MANUAL VALIDATION REQUIRED")
        print(f"   Please manually open: {file_path}")
        print(f"   Commands you can try:")
        print(f"     libreoffice {file_path}")
        print(f"     xdg-open {file_path}")
        print(f"     Or use your file manager to open the document")
        print(f"")
        print(f"👁️ Please validate the {document_type} formatting and content")
        return True
    
    def wait_for_validation_response(self, document_type: str) -> Optional[bool]:
        """
        Wait for human validation response (if interactive terminal available)
        
        Returns:
            True: Document approved
            False: Document needs improvement  
            None: Cannot get interactive response
        """
        try:
            print(f"")
            print(f"🔍 VALIDATION CHECK:")
            response = input(f"   Is the {document_type} ready for client delivery? (y/n/skip): ").strip().lower()
            
            if response in ['y', 'yes']:
                print(f"✅ {document_type.title()} approved by human validator")
                return True
            elif response in ['n', 'no']:
                print(f"❌ {document_type.title()} needs improvement")
                return False
            else:
                print(f"⏭️ Validation response skipped")
                return None
                
        except (EOFError, KeyboardInterrupt):
            print(f"⏭️ Interactive validation not available")
            return None
    
    def get_validation_summary(self, file_path: str, document_type: str, 
                             approved: Optional[bool] = None) -> Dict[str, Any]:
        """Generate validation summary for logging"""
        
        file_size = 0
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
        
        return {
            'file_path': file_path,
            'document_type': document_type,
            'file_size_bytes': file_size,
            'human_approved': approved,
            'validation_timestamp': time.time(),
            'validation_method': 'human-in-the-loop'
        }


def main():
    """Test the human validation helper"""
    print("🧪 TESTING HUMAN VALIDATION HELPER")
    print("=" * 50)
    
    helper = HumanValidationHelper()
    
    # Test with Emily Sorel invoice
    test_file = "/tmp/emily_sorel_invoice_uno.odt"
    
    if os.path.exists(test_file):
        print("Testing with Emily Sorel invoice...")
        success = helper.open_for_validation(test_file, "invoice")
        
        if success:
            approval = helper.wait_for_validation_response("invoice")
            summary = helper.get_validation_summary(test_file, "invoice", approval)
            
            print(f"\n📊 VALIDATION SUMMARY:")
            for key, value in summary.items():
                print(f"   {key}: {value}")
        
    else:
        print(f"Test file not found: {test_file}")
        print("Please run the invoice generator first")

if __name__ == "__main__":
    main()