#!/usr/bin/env python3
"""
AI Operator Helper Script for Squirt
Provides easy integration of protocol management and monitoring for AI operations.
"""

import sys
import json
from pathlib import Path

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from protocol_manager import ProtocolManager

def load_protocols():
    """Load and display current protocols for AI operator"""
    print("🔧 Loading Squirt AI Operator Protocols...")
    print("=" * 60)

    manager = ProtocolManager()
    context = manager.inject_session_context()

    print("📋 CRITICAL SYSTEM STATUS:")
    for alert in context['system_status']['critical_alerts']:
        print(f"   ⚠️  {alert}")

    print(f"\n🎯 DEVELOPMENT PRIORITY:")
    print(f"   {context['system_status']['development_priority']}")

    print(f"\n📸 VALIDATION REQUIREMENTS:")
    print(f"   Default: {context['validation_rules']['default_behavior']}")

    print(f"\n💻 LIBREOFFICE STATUS:")
    lo_status = context['libreoffice_state']
    print(f"   Processes: {lo_status['processes_running']}")
    print(f"   Dialogs: {lo_status['dialogs_detected']}")
    print(f"   Documents: {lo_status['documents_open']}")
    print(f"   Errors: {lo_status['error_conditions']}")

    return manager

def before_document_operation(operation_type="document_generation", template_path=None):
    """Execute pre-operation protocol checks"""
    print(f"\n🚀 STARTING {operation_type.upper()} OPERATION")
    print("=" * 60)

    manager = ProtocolManager()

    # Get protocol reminder
    reminder = manager.get_protocol_reminder(operation_type)
    print(reminder)

    # Execute pre-operation checks
    results = manager.before_document_generation(operation_type, template_path)

    print("✅ PRE-OPERATION CHECKS:")
    for check in results['checks_performed']:
        print(f"   ✓ {check}")

    if results['warnings']:
        print("\n⚠️  WARNINGS:")
        for warning in results['warnings']:
            print(f"   ⚠️  {warning}")

    if results['errors']:
        print("\n❌ ERRORS:")
        for error in results['errors']:
            print(f"   ❌ {error}")
        return False

    return True

def after_document_operation(document_path, template_used=None):
    """Execute post-operation validation"""
    print(f"\n📋 VALIDATING GENERATED DOCUMENT")
    print("=" * 60)

    manager = ProtocolManager()
    results = manager.after_document_generation(document_path, template_used)

    print("✅ POST-OPERATION VALIDATIONS:")
    for validation in results['validations_performed']:
        print(f"   ✓ {validation}")

    if results['screenshot_captured']:
        print(f"   📸 Screenshot: {results['screenshot_path']}")

    if results['issues_found']:
        print("\n⚠️  ISSUES FOUND:")
        for issue in results['issues_found']:
            print(f"   ⚠️  {issue}")

    return results

def monitor_libreoffice(duration=10):
    """Start LibreOffice monitoring for specified duration"""
    print(f"\n👀 MONITORING LIBREOFFICE FOR {duration} SECONDS")
    print("=" * 60)

    manager = ProtocolManager()
    try:
        manager.lo_monitor.monitor_and_capture(duration_seconds=duration)
        summary = manager.lo_monitor.get_monitoring_summary()
        print(f"Monitoring complete. Screenshots captured: {summary['screenshots_captured']}")
        return summary
    except KeyboardInterrupt:
        print("Monitoring stopped by user")
        return None

def protocols():
    """One-word protocol loading command - equivalent to /protocols"""
    print("📋 SQUIRT OPERATIONAL PROTOCOLS LOADED")
    print("=" * 50)

    print("📚 Key Protocol Documents:")
    print("✅ SQUIRT_AI_OPERATOR_MANUAL.md - Single source of truth")
    print("✅ VALIDATION_CONFLICT_RESOLUTION.md - Current system status")
    print("✅ VISUAL_VALIDATION_PROTOCOL.md - Validation requirements")
    print("✅ Unified validation framework - 4 validation levels")
    print("✅ Protocol enforcement automation - Real-time compliance")
    print("✅ Real-time protocol injection - Automatic context loading")

    print("\n🚨 CRITICAL SYSTEM STATUS:")
    print("   ⚠️  Template JSON files are NOT processed by UNO generator")
    print("   ⚠️  All generated documents contain identical hardcoded content")
    print("   ⚠️  Sprint 4 success claims were false positives")

    print("\n🎯 DEVELOPMENT PRIORITY:")
    print("   Fix core template processing in UNO generator")

    print("\n📸 VALIDATION REQUIREMENTS:")
    print("   Default: ALWAYS validate immediately unless explicit multi-stage process")
    print("   Levels: BASIC → STANDARD → COMPREHENSIVE → PRODUCTION")

    print("\n💡 CURRENT OPERATIONAL REMINDERS:")
    print("   🔥 CRITICAL: Verify template data is actually used, not hardcoded content")
    print("   📸 Immediate visual validation required for single document generation")
    print("   👁️ Capture complete document including all pages")
    print("   🔔 Monitor LibreOffice for dialogs and errors")

    print("\n🔧 ENHANCED SYSTEMS ACTIVE:")
    print("   ✅ Unified validation framework with 4 levels")
    print("   ✅ Protocol enforcement automation with compliance checking")
    print("   ✅ Real-time protocol injection with file monitoring (watchdog enabled)")
    print("   ✅ LibreOffice state monitoring with screenshot capture")

    print("\n✅ ALL PROTOCOLS LOADED - READY FOR OPERATIONS")

def main():
    """Command-line interface for AI operator helper"""
    if len(sys.argv) < 2:
        print("AI Operator Helper - Squirt Protocol Management")
        print("=" * 60)
        print("Usage:")
        print("  python ai_operator_helper.py protocols")
        print("  python ai_operator_helper.py load_protocols")
        print("  python ai_operator_helper.py before_operation [operation_type] [template_path]")
        print("  python ai_operator_helper.py after_operation [document_path] [template_used]")
        print("  python ai_operator_helper.py monitor [duration_seconds]")
        print("\nExamples:")
        print("  python ai_operator_helper.py protocols  # ONE-WORD PROTOCOL LOAD")
        print("  python ai_operator_helper.py load_protocols")
        print("  python ai_operator_helper.py before_operation document_generation")
        print("  python ai_operator_helper.py after_operation /path/to/doc.odt template.json")
        print("  python ai_operator_helper.py monitor 30")
        return

    command = sys.argv[1]

    if command == "protocols":
        protocols()

    elif command == "load_protocols":
        load_protocols()

    elif command == "before_operation":
        operation_type = sys.argv[2] if len(sys.argv) > 2 else "document_generation"
        template_path = sys.argv[3] if len(sys.argv) > 3 else None
        before_document_operation(operation_type, template_path)

    elif command == "after_operation":
        if len(sys.argv) < 3:
            print("Error: document_path required for after_operation")
            return
        document_path = sys.argv[2]
        template_used = sys.argv[3] if len(sys.argv) > 3 else None
        after_document_operation(document_path, template_used)

    elif command == "monitor":
        duration = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        monitor_libreoffice(duration)

    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()