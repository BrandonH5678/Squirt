#!/usr/bin/env python3
"""
Human-in-the-Loop Validation for 17 Squirt Templates
Uses enhanced session manager to systematically validate all batch-generated templates
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


def validate_17_templates():
    """
    Open all 17 batch-generated templates for human validation
    Addresses the Sprint 4 validation failure by ensuring templates contain different content
    """
    
    print("🔍 SQUIRT TEMPLATE VALIDATION - HUMAN-IN-THE-LOOP")
    print("=" * 60)
    print("📋 Validating 17 templates to prevent Sprint 4 validation failure recurrence")
    print("🎯 Checking: Different content, pricing, materials, and services per template")
    print()
    
    # Find all BATCH_*.odt templates
    template_files = sorted(Path('/home/johnny5/Squirt/test_validation_samples').glob('BATCH_*.odt'))
    
    if not template_files:
        print("❌ No BATCH_*.odt templates found for validation")
        return False
    
    print(f"📄 Found {len(template_files)} templates for validation:")
    for i, template_file in enumerate(template_files, 1):
        template_name = template_file.stem.replace('BATCH_', '')
        print(f"  {i:2d}. {template_name}")
    
    print(f"\n🤔 How would you like to validate these templates?")
    print(f"  1. All at once (comparative validation)")
    print(f"  2. In groups of 4 (systematic validation)")  
    print(f"  3. One by one (detailed validation)")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n⏭️ Validation cancelled")
        return False
    
    with EnhancedDocumentSessionManager(max_concurrent_docs=4) as manager:
        
        if choice == "1":
            # All at once - comparative validation
            return validate_all_comparative(manager, template_files)
            
        elif choice == "2":
            # In groups of 4 - systematic validation
            return validate_in_groups(manager, template_files)
            
        elif choice == "3":
            # One by one - detailed validation
            return validate_individually(manager, template_files)
            
        else:
            print("❌ Invalid choice")
            return False


def validate_all_comparative(manager, template_files):
    """Open all templates for comparative validation (limited by 4-doc rule)"""
    
    print(f"\n🔍 COMPARATIVE VALIDATION MODE")
    print(f"Opening first 4 templates for side-by-side comparison...")
    print(f"⚠️ Note: Limited to 4 docs by session manager rules")
    
    # Use the convenience method for template comparison
    comparison_files = [str(f) for f in template_files[:4]]
    group_id = manager.open_for_template_comparison(
        comparison_files, 
        "sprint4_critical_validation"
    )
    
    if group_id:
        print(f"\n✅ Comparison group created: {group_id}")
        manager.print_session_status()
        
        print(f"\n👁️ VALIDATION CHECKLIST:")
        print(f"  □ Each template shows different services/materials")
        print(f"  □ Pricing varies appropriately between templates") 
        print(f"  □ No hardcoded 'Liam Smith' content appears")
        print(f"  □ Template-specific assumptions and descriptions")
        print(f"  □ Proper category-specific content (irrigation vs lighting vs construction)")
        
        input(f"\nPress Enter when validation is complete...")
        
        print(f"\n🔄 Closing comparison group...")
        manager.close_document_group(group_id, "validation_complete")
        
        # Ask about remaining templates
        remaining = template_files[4:]
        if remaining:
            print(f"\n📋 {len(remaining)} templates remaining for validation")
            continue_choice = input("Continue with remaining templates? (y/n): ").strip().lower()
            if continue_choice in ['y', 'yes']:
                return validate_in_groups(manager, remaining)
        
        return True
    
    return False


def validate_in_groups(manager, template_files):
    """Validate templates in groups of 4"""
    
    print(f"\n📋 GROUP VALIDATION MODE")
    print(f"Processing {len(template_files)} templates in groups of 4...")
    
    # Process in groups of 4
    for group_num, start_idx in enumerate(range(0, len(template_files), 4), 1):
        group_files = template_files[start_idx:start_idx + 4]
        
        print(f"\n🔍 GROUP {group_num}: Validating {len(group_files)} templates")
        for i, template_file in enumerate(group_files):
            template_name = template_file.stem.replace('BATCH_', '')
            print(f"  {i+1}. {template_name}")
        
        # Open group for validation
        comparison_files = [str(f) for f in group_files]
        group_id = manager.open_for_template_comparison(
            comparison_files,
            f"group_{group_num}_validation"
        )
        
        if group_id:
            manager.print_session_status()
            
            print(f"\n👁️ Validate this group and press Enter when done...")
            print(f"   Focus: Content differences, pricing variations, template-specific details")
            
            input()
            
            # Close group
            manager.close_document_group(group_id, f"group_{group_num}_complete")
            print(f"✅ Group {group_num} validation complete")
        else:
            print(f"❌ Failed to open group {group_num}")
            return False
    
    print(f"\n🎉 All {len(template_files)} templates validated in groups!")
    return True


def validate_individually(manager, template_files):
    """Validate templates one by one for detailed inspection"""
    
    print(f"\n📄 INDIVIDUAL VALIDATION MODE")
    print(f"Opening each of {len(template_files)} templates individually for detailed inspection...")
    
    for i, template_file in enumerate(template_files, 1):
        template_name = template_file.stem.replace('BATCH_', '')
        
        print(f"\n📄 TEMPLATE {i}/{len(template_files)}: {template_name}")
        print(f"   File: {template_file.name}")
        
        # Open individual template
        success = manager.open_document_gui(
            str(template_file),
            document_type=f"template_{i}",
            priority=SessionPriority.CRITICAL_VALIDATION,
            context=SessionContext.HUMAN_VALIDATION,
            keep_alive_reason=f"individual_validation_{template_name}"
        )
        
        if success:
            print(f"✅ Template opened for validation")
            print(f"👁️ Check: Content, pricing, materials, services, assumptions")
            
            validation_choice = input("Validation complete? (y/n/skip): ").strip().lower()
            
            if validation_choice in ['y', 'yes']:
                print(f"✅ Template {i} validated successfully")
            elif validation_choice == 'skip':
                print(f"⏭️ Template {i} skipped")
            else:
                print(f"❌ Template {i} needs attention")
            
            # Close current template before opening next
            manager.close_document(str(template_file), f"individual_{i}_complete")
        else:
            print(f"❌ Failed to open template {i}")
            
        if i < len(template_files):
            continue_choice = input(f"\nContinue to next template? (y/n): ").strip().lower()
            if continue_choice not in ['y', 'yes']:
                print(f"⏹️ Validation stopped at template {i}")
                break
    
    print(f"\n🎉 Individual validation process complete!")
    return True


def main():
    """Main validation orchestrator"""
    print("🚀 Starting Squirt Template Validation Process...")
    success = validate_17_templates()
    
    if success:
        print(f"\n🎯 VALIDATION COMPLETE!")
        print(f"✅ All templates have been reviewed for Sprint 4 compliance")
        print(f"📊 Next steps: Address any issues found and regenerate if needed")
    else:
        print(f"\n⚠️ Validation incomplete - please retry or investigate issues")


if __name__ == "__main__":
    main()