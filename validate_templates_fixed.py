#!/usr/bin/env python3
"""
Fixed Human-in-the-Loop Validation for Squirt Templates
Opens 2 templates at a time with proper error handling and persistence
"""

import sys
import time
import signal
from pathlib import Path

sys.path.append('/home/johnny5/Squirt/src')
from document_session_manager_enhanced import (
    EnhancedDocumentSessionManager,
    SessionPriority,
    SessionContext
)


class TemplateValidator:
    def __init__(self):
        self.manager = EnhancedDocumentSessionManager(max_concurrent_docs=2)
        self.current_group_id = None
        
    def validate_templates_in_pairs(self):
        """Validate templates 2 at a time with proper error handling"""
        
        print("🔍 SQUIRT TEMPLATE VALIDATION - FIXED VERSION")
        print("=" * 60)
        print("📋 Opening templates 2 at a time for human validation")
        print("🔧 Fixed: Persistence, error handling, LibreOffice conflicts")
        print()
        
        # Find all BATCH_*.odt templates
        template_files = sorted(Path('/home/johnny5/Squirt/test_validation_samples').glob('BATCH_*.odt'))
        
        if not template_files:
            print("❌ No BATCH_*.odt templates found")
            return False
        
        print(f"📄 Found {len(template_files)} templates for validation")
        
        # Process in pairs
        for pair_num in range(0, len(template_files), 2):
            pair_files = template_files[pair_num:pair_num + 2]
            
            print(f"\n{'='*50}")
            print(f"📋 PAIR {(pair_num//2)+1}: Opening {len(pair_files)} templates")
            print(f"{'='*50}")
            
            for i, template_file in enumerate(pair_files):
                template_name = template_file.stem.replace('BATCH_', '')
                print(f"  {i+1}. {template_name}")
            
            success = self.open_template_pair(pair_files, pair_num//2 + 1)
            
            if success:
                print(f"\n✅ PAIR {(pair_num//2)+1} opened successfully!")
                print(f"👁️ Please review the templates in LibreOffice")
                print(f"🔍 Validation Focus:")
                print(f"   □ Different content between templates")
                print(f"   □ Template-specific materials and services")  
                print(f"   □ Appropriate pricing variations")
                print(f"   □ No hardcoded 'Liam Smith' content")
                print(f"   □ Professional formatting and branding")
                
                # Wait for user to finish validation
                self.wait_for_validation_completion(pair_num//2 + 1)
                
                # Close current pair before opening next
                if self.current_group_id:
                    self.manager.close_document_group(self.current_group_id, f"pair_{(pair_num//2)+1}_complete")
                    self.current_group_id = None
                
                print(f"✅ Pair {(pair_num//2)+1} validation complete\n")
            else:
                print(f"❌ Failed to open pair {(pair_num//2)+1}")
                # Try to recover by closing any open documents
                self.manager.close_all_documents("error_recovery")
        
        print(f"\n🎉 All template pairs validated!")
        return True
    
    def open_template_pair(self, template_files, pair_num):
        """Open a pair of templates with improved error handling"""
        
        group_id = f"pair_{pair_num}_{int(time.time())}"
        session_ids = []
        
        print(f"\n🔄 Opening template pair {pair_num}...")
        
        # Close any existing documents first
        self.manager.close_all_documents("new_pair_prep")
        time.sleep(2)  # Give LibreOffice time to fully close
        
        # Open templates one by one with delays
        for i, template_file in enumerate(template_files):
            template_name = template_file.stem.replace('BATCH_', '')
            
            print(f"  📄 Opening: {template_name}")
            
            success = self.manager.open_document_gui(
                str(template_file),
                document_type=f"template_pair_{pair_num}_{i+1}",
                priority=SessionPriority.CRITICAL_VALIDATION,
                context=SessionContext.HUMAN_VALIDATION,
                group_id=group_id,
                keep_alive_reason=f"pair_{pair_num}_validation"
            )
            
            if success:
                session_ids.append(self.manager._get_session_id(str(template_file)))
                print(f"  ✅ Opened: {template_name}")
                time.sleep(3)  # Delay between opening documents
            else:
                print(f"  ❌ Failed: {template_name}")
                # Try alternative opening method
                success = self.try_alternative_open(template_file, group_id)
                if success:
                    session_ids.append(self.manager._get_session_id(str(template_file)))
                    print(f"  ✅ Alternative method worked: {template_name}")
        
        # Create group if we have at least one document
        if session_ids:
            if len(session_ids) > 1:
                self.manager.create_document_group(group_id, session_ids, f"template_pair_{pair_num}")
                self.current_group_id = group_id
            
            self.manager.print_session_status()
            return True
        
        return False
    
    def try_alternative_open(self, template_file, group_id):
        """Try alternative methods to open a document"""
        
        print(f"  🔄 Trying alternative opening methods...")
        
        # Method 1: Direct system command
        try:
            import subprocess
            subprocess.Popen(['xdg-open', str(template_file)], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            time.sleep(3)
            
            # Check if LibreOffice is running
            result = subprocess.run(['pgrep', '-f', 'libreoffice'], capture_output=True)
            if result.returncode == 0:
                print(f"  ✅ Alternative method: xdg-open")
                return True
        except:
            pass
        
        # Method 2: Manual instruction
        print(f"  📋 Manual fallback - Please open manually:")
        print(f"      libreoffice '{template_file}'")
        return False
    
    def wait_for_validation_completion(self, pair_num):
        """Wait for user to complete validation with better UX"""
        
        print(f"\n⏸️  VALIDATION IN PROGRESS - PAIR {pair_num}")
        print(f"   📋 Review the open LibreOffice windows")
        print(f"   🔍 Check for content differences and template-specific details")
        print(f"   ⌨️  Press Ctrl+C when you're done reviewing")
        
        try:
            # Keep the session alive and wait for user interrupt
            while True:
                time.sleep(5)
                # Update activity to prevent auto-closure
                for session in self.manager.active_sessions.values():
                    self.manager.update_session_activity(session.file_path)
                
                # Show periodic status
                active_count = len(self.manager.active_sessions)
                if active_count > 0:
                    print(f"   💚 {active_count} template(s) still open - validation in progress...")
                else:
                    print(f"   ⚠️ No templates open - may have been closed manually")
                    break
                    
        except KeyboardInterrupt:
            print(f"\n✅ Validation completed for pair {pair_num}")
        except Exception as e:
            print(f"\n⚠️ Validation interrupted: {e}")
    
    def cleanup(self):
        """Clean up all resources"""
        try:
            self.manager.close_all_documents("cleanup")
        except:
            pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


def main():
    """Main validation function with proper error handling"""
    print("🚀 Starting Fixed Squirt Template Validation...")
    
    try:
        with TemplateValidator() as validator:
            success = validator.validate_templates_in_pairs()
            
            if success:
                print(f"\n🎯 VALIDATION COMPLETE!")
                print(f"✅ All template pairs have been reviewed")
                print(f"📊 Check for any Sprint 4 validation issues found")
            else:
                print(f"\n⚠️ Validation incomplete")
                
    except KeyboardInterrupt:
        print(f"\n⏹️ Validation stopped by user")
    except Exception as e:
        print(f"\n❌ Validation error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()