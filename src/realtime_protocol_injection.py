#!/usr/bin/env python3
"""
Real-Time Protocol Injection System for Squirt
Automatically loads and injects protocol context for AI operators during operations.
"""

import json
import time
import threading
import os
import signal
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable

# Try to import watchdog, fallback to manual monitoring if not available
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("📦 watchdog not available - using manual file monitoring")

from protocol_manager import ProtocolManager
from libreoffice_monitor import LibreOfficeMonitor
from unified_validation_system import UnifiedValidationSystem

class ProtocolContext:
    """Container for current protocol context"""

    def __init__(self):
        self.protocols = {}
        self.last_updated = datetime.now()
        self.injection_count = 0
        self.active_operations = []

    def update_context(self, new_protocols: Dict[str, Any]):
        """Update the protocol context"""
        self.protocols = new_protocols
        self.last_updated = datetime.now()
        self.injection_count += 1

    def get_context_for_operation(self, operation_type: str) -> Dict[str, Any]:
        """Get relevant protocol context for specific operation"""
        base_context = {
            'timestamp': datetime.now().isoformat(),
            'context_version': self.injection_count,
            'operation_type': operation_type
        }

        # Add all current protocols
        base_context.update(self.protocols)

        # Add operation-specific protocols
        if operation_type in self.protocols.get('operation_specific', {}):
            base_context['operation_protocols'] = self.protocols['operation_specific'][operation_type]

        return base_context

if WATCHDOG_AVAILABLE:
    class FileWatcher(FileSystemEventHandler):
        """Watches for changes to protocol files and triggers updates"""

        def __init__(self, injection_system):
            self.injection_system = injection_system
            self.watched_files = [
                'SQUIRT_AI_OPERATOR_MANUAL.md',
                'VISUAL_VALIDATION_PROTOCOL.md',
                'VALIDATION_CONFLICT_RESOLUTION.md',
                'validation_rules.json'
            ]

        def on_modified(self, event):
            if not event.is_directory:
                filename = Path(event.src_path).name
                if filename in self.watched_files:
                    print(f"🔄 Protocol file updated: {filename}")
                    self.injection_system.refresh_protocols()
else:
    class FileWatcher:
        """Fallback file watcher using manual polling"""

        def __init__(self, injection_system):
            self.injection_system = injection_system
            self.watched_files = [
                'SQUIRT_AI_OPERATOR_MANUAL.md',
                'VISUAL_VALIDATION_PROTOCOL.md',
                'VALIDATION_CONFLICT_RESOLUTION.md',
                'validation_rules.json'
            ]
            self.file_timestamps = {}

        def check_file_changes(self, base_path):
            """Manually check for file changes"""
            for filename in self.watched_files:
                file_path = Path(base_path) / filename
                if file_path.exists():
                    current_mtime = file_path.stat().st_mtime
                    if filename in self.file_timestamps:
                        if current_mtime > self.file_timestamps[filename]:
                            print(f"🔄 Protocol file updated: {filename}")
                            self.injection_system.refresh_protocols()
                    self.file_timestamps[filename] = current_mtime

class RealTimeProtocolInjection:
    """
    Real-time protocol injection system that automatically provides
    current protocol context to AI operators
    """

    def __init__(self, squirt_root: str = "/home/johnny5/Squirt"):
        self.squirt_root = Path(squirt_root)
        self.protocol_manager = ProtocolManager(squirt_root)
        self.lo_monitor = LibreOfficeMonitor()
        self.validation_system = UnifiedValidationSystem(squirt_root)

        # Protocol context
        self.current_context = ProtocolContext()
        self.context_cache = {}
        self.auto_refresh_enabled = True
        self.refresh_interval = 30  # seconds

        # File monitoring
        self.file_observer = None
        self.monitoring_thread = None
        self.running = False

        # Session tracking
        self.session_start = datetime.now()
        self.injection_log = []
        self.operation_contexts = {}

        # Load initial protocols
        self.refresh_protocols()

    def start_realtime_injection(self):
        """Start the real-time protocol injection system"""

        print("🚀 Starting Real-Time Protocol Injection System")
        print("=" * 60)

        self.running = True

        # Start file monitoring
        self._start_file_monitoring()

        # Start periodic refresh
        self._start_periodic_refresh()

        # Register signal handlers for clean shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        print("✅ Real-time protocol injection active")
        print("📁 Monitoring protocol file changes")
        print("⏰ Auto-refresh every 30 seconds")
        print("🔧 Ready to inject protocols for AI operations")

    def stop_realtime_injection(self):
        """Stop the real-time protocol injection system"""

        print("🛑 Stopping Real-Time Protocol Injection System")

        self.running = False

        if self.file_observer:
            self.file_observer.stop()
            self.file_observer.join()

        if self.monitoring_thread:
            self.monitoring_thread.join()

        print("✅ Real-time protocol injection stopped")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n📡 Received signal {signum}, shutting down gracefully...")
        self.stop_realtime_injection()
        sys.exit(0)

    def _start_file_monitoring(self):
        """Start monitoring protocol files for changes"""

        if WATCHDOG_AVAILABLE:
            event_handler = FileWatcher(self)
            self.file_observer = Observer()
            self.file_observer.schedule(event_handler, str(self.squirt_root), recursive=True)
            self.file_observer.start()
        else:
            # Use manual polling
            self.file_watcher = FileWatcher(self)
            # File changes will be checked during periodic refresh

    def _start_periodic_refresh(self):
        """Start periodic protocol refresh"""

        def refresh_loop():
            while self.running:
                time.sleep(self.refresh_interval)
                if self.auto_refresh_enabled and self.running:
                    # Check for file changes if using manual monitoring
                    if not WATCHDOG_AVAILABLE and hasattr(self, 'file_watcher'):
                        self.file_watcher.check_file_changes(self.squirt_root)

                    self.refresh_protocols()

        self.monitoring_thread = threading.Thread(target=refresh_loop, daemon=True)
        self.monitoring_thread.start()

    def refresh_protocols(self):
        """Refresh all protocol data from sources"""

        try:
            # Get fresh protocol context
            fresh_context = self.protocol_manager.inject_session_context()

            # Add system status
            fresh_context['system_status'] = self._get_enhanced_system_status()

            # Add operation-specific protocols
            fresh_context['operation_specific'] = self._get_operation_specific_protocols()

            # Add real-time monitoring data
            fresh_context['realtime_monitoring'] = self._get_realtime_monitoring_data()

            # Update context
            self.current_context.update_context(fresh_context)

            # Log the refresh
            self.injection_log.append({
                'action': 'protocol_refresh',
                'timestamp': datetime.now().isoformat(),
                'context_version': self.current_context.injection_count,
                'protocols_loaded': len(fresh_context.keys())
            })

            print(f"🔄 Protocols refreshed (v{self.current_context.injection_count})")

        except Exception as e:
            print(f"❌ Protocol refresh failed: {e}")

    def inject_protocols_for_operation(self,
                                     operation_type: str,
                                     operation_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Inject current protocols for a specific operation

        Args:
            operation_type: Type of operation (document_generation, validation, etc.)
            operation_context: Additional context about the operation

        Returns:
            Complete protocol context for the operation
        """

        # Get base context for operation
        context = self.current_context.get_context_for_operation(operation_type)

        # Add operation-specific context
        if operation_context:
            context['operation_context'] = operation_context

        # Add real-time system state
        context['realtime_state'] = {
            'libreoffice_state': self.lo_monitor.get_libreoffice_state(),
            'system_load': self._get_system_load(),
            'active_operations': len(self.current_context.active_operations),
            'injection_timestamp': datetime.now().isoformat()
        }

        # Add contextual reminders
        context['contextual_reminders'] = self._get_contextual_reminders(operation_type, operation_context)

        # Cache the context for this operation
        operation_id = f"{operation_type}_{int(time.time())}"
        self.operation_contexts[operation_id] = context

        # Log the injection
        self.injection_log.append({
            'action': 'protocol_injection',
            'operation_type': operation_type,
            'operation_id': operation_id,
            'timestamp': datetime.now().isoformat(),
            'context_size': len(str(context))
        })

        print(f"📋 Protocols injected for {operation_type} (ID: {operation_id})")

        return context

    def _get_enhanced_system_status(self) -> Dict[str, Any]:
        """Get enhanced system status with real-time data"""

        base_status = self.protocol_manager._get_system_status()

        # Add real-time enhancements
        enhanced_status = base_status.copy()
        enhanced_status.update({
            'protocol_injection_active': True,
            'last_protocol_refresh': self.current_context.last_updated.isoformat(),
            'protocol_version': self.current_context.injection_count,
            'session_duration': str(datetime.now() - self.session_start),
            'injections_performed': len([log for log in self.injection_log if log['action'] == 'protocol_injection']),
            'file_monitoring_active': self.file_observer is not None and self.file_observer.is_alive()
        })

        return enhanced_status

    def _get_operation_specific_protocols(self) -> Dict[str, Any]:
        """Get protocols specific to different operation types"""

        return {
            'document_generation': {
                'mandatory_steps': [
                    'LibreOffice state check before starting',
                    'Template validation if template provided',
                    'Visual validation immediately after generation',
                    'Content verification for template usage',
                    'Professional formatting verification'
                ],
                'critical_checks': [
                    'Verify template data actually used (not hardcoded content)',
                    'Capture screenshot for visual validation',
                    'Check mathematical accuracy',
                    'Ensure professional presentation standards'
                ],
                'performance_targets': {
                    'generation_time': '< 30 seconds',
                    'validation_time': '< 45 seconds',
                    'total_operation_time': '< 75 seconds'
                }
            },
            'template_processing': {
                'critical_requirements': [
                    'Parse JSON template data',
                    'Use template parameters for calculations',
                    'Generate material/labor lists from template',
                    'Apply formulas and pricing rules',
                    'Produce unique output for different templates'
                ],
                'validation_checks': [
                    'Verify different templates produce different outputs',
                    'Check file sizes for uniqueness',
                    'Confirm template-specific content appears',
                    'Reject hardcoded Liam Smith content'
                ]
            },
            'visual_validation': {
                'immediate_validation_required': [
                    'Single document generation',
                    'Production documents',
                    'Final iterations',
                    'Debugging sessions',
                    'User explicitly requests validation'
                ],
                'validation_criteria': [
                    'Professional appearance and layout',
                    'Blue headers (#4472c4)',
                    'Proper typography and spacing',
                    'Complete content population',
                    'Currency formatting ($X,XXX.XX)',
                    'WaterWizard branding consistency'
                ]
            }
        }

    def _get_realtime_monitoring_data(self) -> Dict[str, Any]:
        """Get real-time monitoring data"""

        lo_state = self.lo_monitor.get_libreoffice_state()

        return {
            'libreoffice_processes': len(lo_state.get('processes', [])),
            'dialogs_detected': len(lo_state.get('dialogs', [])),
            'documents_open': len(lo_state.get('documents', [])),
            'error_conditions': len(lo_state.get('errors', [])),
            'monitoring_active': True,
            'screenshot_directory_status': {
                'exists': self.lo_monitor.screenshot_dir.exists(),
                'writable': os.access(self.lo_monitor.screenshot_dir, os.W_OK),
                'recent_screenshots': len(list(self.lo_monitor.screenshot_dir.glob('*.png')))
            }
        }

    def _get_contextual_reminders(self,
                                operation_type: str,
                                operation_context: Optional[Dict[str, Any]]) -> List[str]:
        """Get contextual reminders based on operation and current state"""

        reminders = []

        # Universal reminders
        if operation_type in ['document_generation', 'template_processing']:
            reminders.append("🔥 CRITICAL: Verify template data is actually used, not hardcoded content")

        # LibreOffice state reminders
        lo_state = self.lo_monitor.get_libreoffice_state()
        if lo_state.get('errors'):
            reminders.append(f"⚠️ LibreOffice has {len(lo_state['errors'])} error conditions")

        if lo_state.get('dialogs'):
            reminders.append("🔔 LibreOffice dialogs detected - screenshot and analyze")

        # Operation-specific reminders
        if operation_type == 'document_generation':
            if not operation_context or not operation_context.get('multi_stage_process'):
                reminders.append("📸 Immediate visual validation required for single document generation")

        if operation_type == 'visual_validation':
            reminders.append("👁️ Capture complete document including all pages")
            reminders.append("🎯 Rate professional appearance, formatting, and content accuracy")

        # Time-based reminders
        session_duration = datetime.now() - self.session_start
        if session_duration > timedelta(hours=1):
            reminders.append("⏰ Long session - consider refreshing protocols and system state")

        return reminders

    def _get_system_load(self) -> Dict[str, Any]:
        """Get current system load information"""

        try:
            # Get basic system info
            load_avg = os.getloadavg()
            return {
                'load_1min': load_avg[0],
                'load_5min': load_avg[1],
                'load_15min': load_avg[2],
                'timestamp': datetime.now().isoformat()
            }
        except:
            return {'error': 'Could not get system load'}

    def get_injection_summary(self) -> Dict[str, Any]:
        """Get summary of protocol injection activity"""

        total_injections = len([log for log in self.injection_log if log['action'] == 'protocol_injection'])
        total_refreshes = len([log for log in self.injection_log if log['action'] == 'protocol_refresh'])

        return {
            'session_start': self.session_start.isoformat(),
            'session_duration': str(datetime.now() - self.session_start),
            'protocol_injections': total_injections,
            'protocol_refreshes': total_refreshes,
            'current_context_version': self.current_context.injection_count,
            'auto_refresh_enabled': self.auto_refresh_enabled,
            'file_monitoring_active': self.file_observer is not None and self.file_observer.is_alive(),
            'cached_operation_contexts': len(self.operation_contexts),
            'realtime_injection_active': self.running
        }

# Convenience functions for AI operators
def inject_protocols_now(operation_type: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Immediately inject current protocols for an operation"""
    injector = RealTimeProtocolInjection()
    return injector.inject_protocols_for_operation(operation_type, context)

def start_protocol_monitoring():
    """Start background protocol monitoring"""
    injector = RealTimeProtocolInjection()
    injector.start_realtime_injection()
    return injector

# Test the real-time injection system
def test_realtime_injection():
    """Test the real-time protocol injection system"""

    print("🧪 Testing Real-Time Protocol Injection System")
    print("=" * 50)

    # Create injection system
    injector = RealTimeProtocolInjection()

    # Test immediate injection
    print("\n📋 Testing immediate protocol injection...")
    context = injector.inject_protocols_for_operation(
        'document_generation',
        {'template_path': '/test/template.json', 'client': 'Test Client'}
    )

    print(f"✅ Context injected with {len(context)} protocol elements")
    print(f"📊 Context version: {context['context_version']}")
    print(f"🔧 System status included: {'system_status' in context}")
    print(f"⚡ Real-time state included: {'realtime_state' in context}")
    print(f"💡 Contextual reminders: {len(context.get('contextual_reminders', []))}")

    # Test protocol refresh
    print("\n🔄 Testing protocol refresh...")
    old_version = injector.current_context.injection_count
    injector.refresh_protocols()
    new_version = injector.current_context.injection_count

    print(f"✅ Protocols refreshed: v{old_version} → v{new_version}")

    # Test injection summary
    print("\n📊 Testing injection summary...")
    summary = injector.get_injection_summary()

    print(f"Session duration: {summary['session_duration']}")
    print(f"Protocol injections: {summary['protocol_injections']}")
    print(f"Protocol refreshes: {summary['protocol_refreshes']}")
    print(f"Auto-refresh enabled: {summary['auto_refresh_enabled']}")

    # Test with different operation types
    print("\n🎯 Testing different operation types...")
    operations = ['template_processing', 'visual_validation', 'file_operations']

    for op_type in operations:
        op_context = injector.inject_protocols_for_operation(op_type)
        print(f"  {op_type}: {len(op_context)} elements, {len(op_context.get('contextual_reminders', []))} reminders")

    print("\n✅ Real-time protocol injection system test completed!")

    return True

if __name__ == "__main__":
    test_realtime_injection()