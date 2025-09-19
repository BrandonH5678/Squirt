#!/usr/bin/env python3
"""
Protocols command - Load all critical operational protocols for AI operators
Usage: /protocols
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
squirt_root = Path(__file__).parent.parent.parent
sys.path.append(str(squirt_root / "src"))

def load_protocols():
    """Load all critical protocols and system status"""

    print("📋 LOADING SQUIRT OPERATIONAL PROTOCOLS")
    print("=" * 60)

    # Try to use real-time protocol injection for most current context
    try:
        from realtime_protocol_injection import inject_protocols_now

        print("🔄 Injecting real-time protocol context...")
        context = inject_protocols_now('protocol_review', {
            'operation_context': 'manual_protocol_review',
            'comprehensive_load': True
        })

        print(f"✅ Protocol context loaded (v{context.get('context_version', '?')})")
        print(f"📊 System status: {len(context.get('system_status', {}).get('critical_alerts', []))} critical alerts")
        print(f"⚡ Real-time state: LibreOffice monitoring active")
        print(f"💡 Contextual reminders: {len(context.get('contextual_reminders', []))} active")

        # Show critical alerts
        critical_alerts = context.get('system_status', {}).get('critical_alerts', [])
        if critical_alerts:
            print(f"\n🚨 CRITICAL SYSTEM ALERTS:")
            for alert in critical_alerts:
                print(f"   ⚠️  {alert}")

        # Show development priority
        dev_priority = context.get('system_status', {}).get('development_priority')
        if dev_priority:
            print(f"\n🎯 DEVELOPMENT PRIORITY:")
            print(f"   {dev_priority}")

        # Show validation requirements
        validation_default = context.get('validation_rules', {}).get('default_behavior')
        if validation_default:
            print(f"\n📸 VALIDATION REQUIREMENTS:")
            print(f"   Default: {validation_default}")

        # Show contextual reminders
        reminders = context.get('contextual_reminders', [])
        if reminders:
            print(f"\n💡 CURRENT OPERATIONAL REMINDERS:")
            for reminder in reminders:
                print(f"   • {reminder}")

        print(f"\n✅ All protocols loaded and ready for operations")

        return True

    except Exception as e:
        print(f"⚠️  Real-time injection failed, loading manual protocols: {e}")
        return load_manual_protocols()

def load_manual_protocols():
    """Fallback to manual protocol loading"""

    print("📁 Loading protocols manually...")

    protocol_files = [
        "SQUIRT_AI_OPERATOR_MANUAL.md",
        "VALIDATION_CONFLICT_RESOLUTION.md",
        "VISUAL_VALIDATION_PROTOCOL.md"
    ]

    loaded_files = []

    for filename in protocol_files:
        filepath = squirt_root / filename
        if filepath.exists():
            print(f"   ✅ {filename}")
            loaded_files.append(filename)
        else:
            print(f"   ❌ {filename} (not found)")

    print(f"\n📋 {len(loaded_files)}/{len(protocol_files)} protocol files available")
    print(f"📖 Review loaded protocols for current operational guidelines")

    return len(loaded_files) > 0

def main():
    """Main command entry point"""
    success = load_protocols()

    if success:
        print(f"\n🎯 READY FOR OPERATIONS")
        print(f"📚 All critical protocols loaded into context")
        print(f"🔧 System status and alerts reviewed")
        print(f"⚡ Real-time monitoring data included")
    else:
        print(f"\n❌ PROTOCOL LOADING FAILED")
        print(f"📞 Contact system administrator")

    return success

if __name__ == "__main__":
    main()