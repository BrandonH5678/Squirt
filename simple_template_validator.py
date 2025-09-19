#!/usr/bin/env python3
"""
Simple Template Validator - Opens 2 templates at a time for human review
Direct approach without complex input handling
"""

import sys
import time
from pathlib import Path

sys.path.append('/home/johnny5/Squirt/src')
from document_session_manager_enhanced import (
    EnhancedDocumentSessionManager,
    SessionPriority,
    SessionContext
)


def open_first_template_pair():
    """Open the first 2 templates for human validation"""
    
    print("🔍 SIMPLE TEMPLATE VALIDATOR")
    print("=" * 50)
    print("📋 Opening first 2 templates for human validation")
    print()
    
    # Find all BATCH_*.odt templates
    template_files = sorted(Path('/home/johnny5/Squirt/test_validation_samples').glob('BATCH_*.odt'))
    
    if len(template_files) < 2:
        print("❌ Need at least 2 templates for validation")
        return False
    
    # Take first 2 templates
    first_pair = template_files[:2]
    
    print("📄 Opening templates:")
    for i, template_file in enumerate(first_pair, 1):
        template_name = template_file.stem.replace('BATCH_', '')
        print(f"  {i}. {template_name}")
    
    print("\n🔄 Starting validation session...")
    
    with EnhancedDocumentSessionManager(max_concurrent_docs=2) as manager:
        
        # Open first template
        print(f"📄 Opening: {first_pair[0].stem.replace('BATCH_', '')}")
        success1 = manager.open_document_gui(
            str(first_pair[0]),
            document_type="template_1",
            priority=SessionPriority.CRITICAL_VALIDATION,
            context=SessionContext.HUMAN_VALIDATION,
            keep_alive_reason="sprint4_validation"
        )
        
        if success1:
            print("✅ Template 1 opened")
            time.sleep(4)  # Wait between opens
        
        # Open second template
        print(f"📄 Opening: {first_pair[1].stem.replace('BATCH_', '')}")
        success2 = manager.open_document_gui(
            str(first_pair[1]),
            document_type="template_2", 
            priority=SessionPriority.CRITICAL_VALIDATION,
            context=SessionContext.HUMAN_VALIDATION,
            keep_alive_reason="sprint4_validation"
        )
        
        if success2:
            print("✅ Template 2 opened")
        
        if success1 or success2:
            print("\n🎯 VALIDATION CHECKLIST:")
            print("  □ Different content between templates")
            print("  □ Template-specific materials and services")
            print("  □ Appropriate pricing variations")
            print("  □ No hardcoded 'Liam Smith' content")
            print("  □ Professional formatting and branding")
            
            manager.print_session_status()
            
            print(f"\n👁️ Both templates are now open in LibreOffice")
            print(f"🔍 Please review both documents for content differences")
            print(f"📝 Focus on verifying they contain different services and pricing")
            print(f"⚠️ This addresses the Sprint 4 validation failure")
            
            print(f"\n⏸️  Documents will stay open until you're ready...")
            print(f"   💡 To close them and continue, press Ctrl+C")
            
            try:
                # Keep session alive
                while True:
                    time.sleep(10)
                    # Update activity to prevent auto-closure
                    for session in manager.active_sessions.values():
                        manager.update_session_activity(session.file_path)
                    
                    active_count = len(manager.active_sessions)
                    print(f"   💚 {active_count} template(s) open - validation in progress...")
                    
                    if active_count == 0:
                        print("   ⚠️ Templates were closed manually")
                        break
                        
            except KeyboardInterrupt:
                print(f"\n✅ Validation session ended")
                print(f"🔄 Closing all documents...")
        
        else:
            print("❌ Failed to open templates")
            return False
    
    print(f"\n🎯 First pair validation complete!")
    print(f"📊 What did you find? Are the templates showing different content?")
    return True


def main():
    """Main function"""
    try:
        success = open_first_template_pair()
        
        if success:
            print(f"\n🎉 Template validation session completed!")
            print(f"📋 Ready to continue with remaining templates if needed")
        else:
            print(f"\n⚠️ Template validation failed")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()