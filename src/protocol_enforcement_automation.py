#!/usr/bin/env python3
"""
Protocol Enforcement Automation System for Squirt
Provides real-time compliance checking and automatic protocol enforcement.
"""

import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import subprocess
import os

from protocol_manager import ProtocolManager
from libreoffice_monitor import LibreOfficeMonitor
from unified_validation_system import UnifiedValidationSystem, ValidationLevel

class ComplianceLevel(Enum):
    """Compliance enforcement levels"""
    ADVISORY = "advisory"       # Log violations, provide warnings
    ENFORCED = "enforced"       # Block operations on violations
    STRICT = "strict"          # Prevent any non-compliant operations

class OperationType(Enum):
    """Types of operations that can be monitored"""
    DOCUMENT_GENERATION = "document_generation"
    TEMPLATE_PROCESSING = "template_processing"
    VISUAL_VALIDATION = "visual_validation"
    FILE_OPERATIONS = "file_operations"
    LIBREOFFICE_OPERATIONS = "libreoffice_operations"

class ComplianceViolation:
    """Represents a protocol compliance violation"""
    def __init__(self, operation: str, violation_type: str, message: str, severity: str = "warning"):
        self.operation = operation
        self.violation_type = violation_type
        self.message = message
        self.severity = severity  # "info", "warning", "error", "critical"
        self.timestamp = datetime.now().isoformat()
        self.resolved = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            'operation': self.operation,
            'violation_type': self.violation_type,
            'message': self.message,
            'severity': self.severity,
            'timestamp': self.timestamp,
            'resolved': self.resolved
        }

class ProtocolEnforcementAutomation:
    """
    Automated protocol enforcement system with real-time compliance checking
    """

    def __init__(self, squirt_root: str = "/home/johnny5/Squirt"):
        self.squirt_root = Path(squirt_root)
        self.compliance_level = ComplianceLevel.ENFORCED
        self.protocol_manager = ProtocolManager(squirt_root)
        self.lo_monitor = LibreOfficeMonitor()
        self.validation_system = UnifiedValidationSystem(squirt_root)

        # Compliance tracking
        self.violations = []
        self.operation_log = []
        self.compliance_rules = {}
        self.active_monitors = {}

        # Performance tracking
        self.performance_metrics = {
            'operations_monitored': 0,
            'violations_detected': 0,
            'compliance_rate': 0.0,
            'average_operation_time': 0.0
        }

        # Load default compliance rules
        self._load_default_compliance_rules()

        # Create compliance log directory
        self.compliance_dir = self.squirt_root / "compliance_logs"
        self.compliance_dir.mkdir(exist_ok=True)

    def _load_default_compliance_rules(self):
        """Load default protocol compliance rules"""

        self.compliance_rules = {
            'document_generation': {
                'mandatory_checks': [
                    'libreoffice_state_check',
                    'template_validation',
                    'immediate_visual_validation'
                ],
                'prohibited_actions': [
                    'skip_validation',
                    'ignore_template_errors',
                    'proceed_without_screenshot'
                ],
                'performance_targets': {
                    'max_generation_time': 30,  # seconds
                    'max_validation_time': 45,  # seconds
                }
            },
            'template_processing': {
                'mandatory_checks': [
                    'json_schema_validation',
                    'template_usage_verification',
                    'content_verification'
                ],
                'prohibited_actions': [
                    'use_hardcoded_content',
                    'skip_template_parsing',
                    'ignore_template_data'
                ],
                'critical_requirements': [
                    'verify_template_data_used',
                    'reject_hardcoded_output'
                ]
            },
            'visual_validation': {
                'mandatory_checks': [
                    'screenshot_capture',
                    'claude_vision_analysis',
                    'professional_formatting_check'
                ],
                'timing_requirements': {
                    'immediate_validation': ['single_document', 'production_document', 'debugging'],
                    'deferred_validation': ['multi_stage_process']
                }
            },
            'libreoffice_operations': {
                'mandatory_monitoring': [
                    'process_state_tracking',
                    'dialog_detection',
                    'error_condition_monitoring'
                ],
                'automatic_responses': [
                    'screenshot_on_dialog',
                    'error_recovery_procedures',
                    'process_cleanup'
                ]
            }
        }

    def enforce_operation_compliance(self,
                                   operation_type: OperationType,
                                   operation_context: Dict[str, Any],
                                   operation_func: Callable,
                                   *args, **kwargs) -> Dict[str, Any]:
        """
        Enforce protocol compliance for an operation

        Args:
            operation_type: Type of operation being performed
            operation_context: Context information about the operation
            operation_func: Function to execute if compliance checks pass
            *args, **kwargs: Arguments for the operation function

        Returns:
            Operation result with compliance information
        """

        operation_start = time.time()
        operation_id = f"{operation_type.value}_{int(operation_start)}"

        print(f"🔧 PROTOCOL ENFORCEMENT: {operation_type.value}")
        print(f"📋 Operation ID: {operation_id}")
        print("=" * 60)

        # Phase 1: Pre-operation compliance check
        pre_compliance = self._check_pre_operation_compliance(operation_type, operation_context)

        if not pre_compliance['compliant'] and self.compliance_level != ComplianceLevel.ADVISORY:
            return {
                'success': False,
                'operation_id': operation_id,
                'compliance_failure': True,
                'violations': pre_compliance['violations'],
                'message': 'Operation blocked due to compliance violations'
            }

        # Phase 2: Execute operation with monitoring
        try:
            # Start real-time monitoring
            monitor_thread = self._start_operation_monitoring(operation_id, operation_type)

            # Execute the operation
            operation_result = operation_func(*args, **kwargs)

            # Stop monitoring
            self._stop_operation_monitoring(operation_id)

            # Phase 3: Post-operation compliance check
            post_compliance = self._check_post_operation_compliance(
                operation_type, operation_context, operation_result
            )

            # Calculate performance metrics
            operation_time = time.time() - operation_start
            self._update_performance_metrics(operation_time, pre_compliance, post_compliance)

            # Log operation
            operation_log = {
                'operation_id': operation_id,
                'operation_type': operation_type.value,
                'operation_time': operation_time,
                'pre_compliance': pre_compliance,
                'post_compliance': post_compliance,
                'result': operation_result,
                'timestamp': datetime.now().isoformat()
            }
            self.operation_log.append(operation_log)

            # Assess overall compliance
            overall_compliant = (pre_compliance['compliant'] and
                               post_compliance['compliant'] and
                               operation_result.get('success', True))

            compliance_result = {
                'success': operation_result.get('success', True),
                'operation_id': operation_id,
                'compliance_success': overall_compliant,
                'operation_time': operation_time,
                'pre_compliance': pre_compliance,
                'post_compliance': post_compliance,
                'violations': pre_compliance['violations'] + post_compliance['violations'],
                'operation_result': operation_result
            }

            # Save compliance log
            self._save_compliance_log(compliance_result)

            print(f"{'✅ OPERATION COMPLIANT' if overall_compliant else '⚠️ COMPLIANCE ISSUES'}")
            print(f"⏱️  Operation time: {operation_time:.2f}s")

            return compliance_result

        except Exception as e:
            operation_time = time.time() - operation_start
            error_result = {
                'success': False,
                'operation_id': operation_id,
                'error': str(e),
                'operation_time': operation_time,
                'compliance_failure': True
            }

            self._stop_operation_monitoring(operation_id)
            print(f"❌ OPERATION FAILED: {e}")

            return error_result

    def _check_pre_operation_compliance(self,
                                      operation_type: OperationType,
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance requirements before operation starts"""

        violations = []
        compliant = True

        rules = self.compliance_rules.get(operation_type.value, {})

        # Check mandatory checks
        mandatory_checks = rules.get('mandatory_checks', [])
        for check in mandatory_checks:
            check_result = self._perform_compliance_check(check, context)
            if not check_result['passed']:
                violation = ComplianceViolation(
                    operation_type.value,
                    f"missing_{check}",
                    check_result['message'],
                    'error'
                )
                violations.append(violation)
                compliant = False

        # Check prohibited actions
        prohibited_actions = rules.get('prohibited_actions', [])
        for action in prohibited_actions:
            if context.get(action, False):
                violation = ComplianceViolation(
                    operation_type.value,
                    f"prohibited_{action}",
                    f"Prohibited action detected: {action}",
                    'error'
                )
                violations.append(violation)
                compliant = False

        # Check timing requirements for visual validation
        if operation_type == OperationType.VISUAL_VALIDATION:
            timing_result = self._check_visual_validation_timing(context)
            if not timing_result['compliant']:
                violations.extend(timing_result['violations'])
                compliant = False

        return {
            'compliant': compliant,
            'violations': [v.to_dict() for v in violations],
            'checks_performed': len(mandatory_checks),
            'timestamp': datetime.now().isoformat()
        }

    def _check_post_operation_compliance(self,
                                       operation_type: OperationType,
                                       context: Dict[str, Any],
                                       operation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance requirements after operation completes"""

        violations = []
        compliant = True

        # Universal post-operation checks
        if not operation_result.get('success', False):
            violation = ComplianceViolation(
                operation_type.value,
                'operation_failure',
                'Operation failed to complete successfully',
                'error'
            )
            violations.append(violation)
            compliant = False

        # Document generation specific checks
        if operation_type == OperationType.DOCUMENT_GENERATION:
            doc_compliance = self._check_document_generation_compliance(context, operation_result)
            violations.extend(doc_compliance['violations'])
            compliant = compliant and doc_compliance['compliant']

        # Template processing specific checks
        if operation_type == OperationType.TEMPLATE_PROCESSING:
            template_compliance = self._check_template_processing_compliance(context, operation_result)
            violations.extend(template_compliance['violations'])
            compliant = compliant and template_compliance['compliant']

        return {
            'compliant': compliant,
            'violations': [v.to_dict() for v in violations],
            'timestamp': datetime.now().isoformat()
        }

    def _perform_compliance_check(self, check_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform a specific compliance check"""

        if check_name == 'libreoffice_state_check':
            lo_state = self.lo_monitor.get_libreoffice_state()
            return {
                'passed': len(lo_state.get('errors', [])) == 0,
                'message': f"LibreOffice state: {len(lo_state.get('errors', []))} errors"
            }

        elif check_name == 'template_validation':
            template_path = context.get('template_path')
            if template_path and Path(template_path).exists():
                try:
                    with open(template_path, 'r') as f:
                        json.load(f)
                    return {'passed': True, 'message': 'Template JSON valid'}
                except:
                    return {'passed': False, 'message': 'Template JSON invalid'}
            else:
                return {'passed': False, 'message': 'Template path not provided or invalid'}

        elif check_name == 'immediate_visual_validation':
            # Check if visual validation is planned or deferred appropriately
            multi_stage = context.get('multi_stage_process', False)
            explicit_defer = context.get('defer_validation', False)

            if not multi_stage and not explicit_defer:
                return {'passed': True, 'message': 'Immediate visual validation required and planned'}
            elif multi_stage:
                return {'passed': True, 'message': 'Visual validation appropriately deferred for multi-stage process'}
            else:
                return {'passed': False, 'message': 'Visual validation improperly deferred'}

        elif check_name == 'json_schema_validation':
            return {'passed': True, 'message': 'JSON schema validation not implemented'}

        elif check_name == 'template_usage_verification':
            return {'passed': True, 'message': 'Template usage verification to be performed post-operation'}

        elif check_name == 'content_verification':
            return {'passed': True, 'message': 'Content verification to be performed post-operation'}

        else:
            return {'passed': True, 'message': f'Check {check_name} not implemented'}

    def _check_visual_validation_timing(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if visual validation timing follows protocol"""

        violations = []

        # Get validation timing requirements
        operation_context = context.get('operation_context', 'single_document')
        multi_stage = context.get('multi_stage_process', False)
        explicit_defer = context.get('defer_validation', False)

        # Immediate validation required for these contexts
        immediate_required = operation_context in [
            'single_document', 'production_document', 'debugging', 'final_iteration'
        ]

        if immediate_required and (multi_stage or explicit_defer):
            violation = ComplianceViolation(
                'visual_validation',
                'inappropriate_deferment',
                f'Visual validation should be immediate for {operation_context}',
                'warning'
            )
            violations.append(violation)

        return {
            'compliant': len(violations) == 0,
            'violations': violations
        }

    def _check_document_generation_compliance(self,
                                            context: Dict[str, Any],
                                            operation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Check document generation specific compliance"""

        violations = []
        compliant = True

        # Check if visual validation was performed
        if not operation_result.get('visual_validation_performed', False):
            if not context.get('multi_stage_process', False):
                violation = ComplianceViolation(
                    'document_generation',
                    'missing_visual_validation',
                    'Visual validation not performed for single document generation',
                    'error'
                )
                violations.append(violation)
                compliant = False

        # Check if template content verification was performed
        if context.get('template_path') and not operation_result.get('template_verification_performed', False):
            violation = ComplianceViolation(
                'document_generation',
                'missing_template_verification',
                'Template content verification not performed',
                'critical'
            )
            violations.append(violation)
            compliant = False

        return {
            'compliant': compliant,
            'violations': violations
        }

    def _check_template_processing_compliance(self,
                                            context: Dict[str, Any],
                                            operation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Check template processing specific compliance"""

        violations = []
        compliant = True

        # CRITICAL: Check for hardcoded content usage
        if operation_result.get('hardcoded_content_detected', False):
            violation = ComplianceViolation(
                'template_processing',
                'hardcoded_content_usage',
                'CRITICAL: Hardcoded content detected instead of template data',
                'critical'
            )
            violations.append(violation)
            compliant = False

        # Check template data usage
        if not operation_result.get('template_data_used', True):
            violation = ComplianceViolation(
                'template_processing',
                'template_data_not_used',
                'Template data not properly utilized in document generation',
                'error'
            )
            violations.append(violation)
            compliant = False

        return {
            'compliant': compliant,
            'violations': violations
        }

    def _start_operation_monitoring(self, operation_id: str, operation_type: OperationType) -> threading.Thread:
        """Start real-time monitoring for an operation"""

        def monitor_operation():
            start_time = time.time()
            while operation_id in self.active_monitors:
                # Monitor LibreOffice state
                lo_state = self.lo_monitor.get_libreoffice_state()

                # Check for dialogs or errors
                if lo_state.get('dialogs') or lo_state.get('errors'):
                    # Capture screenshot if dialogs detected
                    self.lo_monitor.capture_screenshot(
                        reason=f"monitoring_{operation_type.value}",
                        additional_info=f"Operation: {operation_id}"
                    )

                # Check for performance issues
                elapsed = time.time() - start_time
                if elapsed > 60:  # 1 minute timeout
                    print(f"⚠️  Operation {operation_id} taking longer than expected: {elapsed:.1f}s")

                time.sleep(1)  # Monitor every second

        monitor_thread = threading.Thread(target=monitor_operation, daemon=True)
        self.active_monitors[operation_id] = monitor_thread
        monitor_thread.start()

        return monitor_thread

    def _stop_operation_monitoring(self, operation_id: str):
        """Stop monitoring for an operation"""
        if operation_id in self.active_monitors:
            del self.active_monitors[operation_id]

    def _update_performance_metrics(self, operation_time: float, pre_compliance: Dict, post_compliance: Dict):
        """Update system performance metrics"""

        self.performance_metrics['operations_monitored'] += 1

        if not (pre_compliance['compliant'] and post_compliance['compliant']):
            self.performance_metrics['violations_detected'] += 1

        # Update compliance rate
        total_ops = self.performance_metrics['operations_monitored']
        violations = self.performance_metrics['violations_detected']
        self.performance_metrics['compliance_rate'] = (total_ops - violations) / total_ops * 100

        # Update average operation time
        current_avg = self.performance_metrics['average_operation_time']
        self.performance_metrics['average_operation_time'] = (
            (current_avg * (total_ops - 1) + operation_time) / total_ops
        )

    def _save_compliance_log(self, compliance_result: Dict[str, Any]):
        """Save compliance result to log file"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.compliance_dir / f"compliance_{timestamp}.json"

        try:
            with open(log_file, 'w') as f:
                json.dump(compliance_result, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not save compliance log: {e}")

    def get_compliance_summary(self) -> Dict[str, Any]:
        """Get summary of compliance status and performance"""

        return {
            'compliance_level': self.compliance_level.value,
            'performance_metrics': self.performance_metrics,
            'recent_violations': [v.to_dict() for v in self.violations[-10:]],
            'active_monitors': len(self.active_monitors),
            'total_operations_logged': len(self.operation_log),
            'system_status': {
                'enforcement_active': True,
                'monitoring_active': len(self.active_monitors) > 0,
                'last_update': datetime.now().isoformat()
            }
        }

    def set_compliance_level(self, level: ComplianceLevel):
        """Set the compliance enforcement level"""
        self.compliance_level = level
        print(f"🔧 Compliance level set to: {level.value.upper()}")

# Convenience wrapper for common operations
def with_protocol_enforcement(operation_type: OperationType, context: Dict[str, Any] = None):
    """Decorator for enforcing protocols on operations"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            enforcer = ProtocolEnforcementAutomation()
            return enforcer.enforce_operation_compliance(
                operation_type,
                context or {},
                func,
                *args, **kwargs
            )
        return wrapper
    return decorator

# Test the protocol enforcement system
def test_protocol_enforcement():
    """Test the protocol enforcement automation"""

    print("🧪 Testing Protocol Enforcement Automation")
    print("=" * 50)

    enforcer = ProtocolEnforcementAutomation()

    # Test document generation compliance
    def mock_document_generation(doc_path, template_path=None):
        time.sleep(2)  # Simulate work
        return {
            'success': True,
            'document_path': doc_path,
            'visual_validation_performed': True,
            'template_verification_performed': bool(template_path)
        }

    context = {
        'template_path': '/home/johnny5/Squirt/templates/estimates/test.json',
        'operation_context': 'single_document'
    }

    result = enforcer.enforce_operation_compliance(
        OperationType.DOCUMENT_GENERATION,
        context,
        mock_document_generation,
        "/tmp/test.odt",
        template_path=context['template_path']
    )

    compliance_success = result.get('compliance_success', result.get('success', False))
    print(f"\nTest Result: {'✅ PASSED' if compliance_success else '❌ FAILED'}")
    print(f"Operation Time: {result.get('operation_time', 0):.2f}s")
    print(f"Violations: {len(result.get('violations', []))}")

    # Show compliance summary
    summary = enforcer.get_compliance_summary()
    print(f"\nCompliance Summary:")
    print(f"  Compliance Rate: {summary['performance_metrics']['compliance_rate']:.1f}%")
    print(f"  Operations Monitored: {summary['performance_metrics']['operations_monitored']}")
    print(f"  Average Operation Time: {summary['performance_metrics']['average_operation_time']:.2f}s")

    return compliance_success

if __name__ == "__main__":
    test_protocol_enforcement()