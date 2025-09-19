#!/usr/bin/env python3
"""
Protocol Manager for Squirt AI Operations
Enforces operational protocols and provides real-time guidance to AI operators.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from libreoffice_monitor import LibreOfficeMonitor

class ProtocolManager:
    """Manages AI operator protocols and enforces compliance"""

    def __init__(self, squirt_root="/home/johnny5/Squirt"):
        self.squirt_root = Path(squirt_root)
        self.protocol_file = self.squirt_root / "SQUIRT_AI_OPERATOR_MANUAL.md"
        self.validation_dir = self.squirt_root / "validation_screenshots"
        self.lo_monitor = LibreOfficeMonitor()
        self.session_log = []

    def inject_session_context(self) -> Dict:
        """Inject current protocols into AI operator context"""
        context = {
            'timestamp': datetime.now().isoformat(),
            'system_status': self._get_system_status(),
            'validation_rules': self._get_validation_rules(),
            'libreoffice_state': self._get_libreoffice_status(),
            'current_protocols': self._get_active_protocols(),
            'performance_targets': self._get_performance_targets(),
            'error_procedures': self._get_error_procedures()
        }

        # Log context injection
        self.session_log.append({
            'action': 'context_injection',
            'timestamp': datetime.now().isoformat(),
            'context_size': len(str(context))
        })

        return context

    def _get_system_status(self) -> Dict:
        """Get current system status with critical alerts"""
        return {
            'template_processing': 'BROKEN - UNO generator uses hardcoded content only',
            'validation_system': 'ACTIVE - Visual validation functional',
            'libreoffice_integration': 'ACTIVE - Monitoring system operational',
            'critical_alerts': [
                'Template JSON files are NOT processed by UNO generator',
                'All generated documents contain identical hardcoded content',
                'Sprint 4 success claims were false positives'
            ],
            'development_priority': 'Fix core template processing in UNO generator'
        }

    def _get_validation_rules(self) -> Dict:
        """Get current validation rules and requirements"""
        return {
            'immediate_validation_required': [
                'Single document generation',
                'Final iteration of multi-step process',
                'Production documents for client delivery',
                'Debugging/troubleshooting sessions',
                'User explicitly requests validation'
            ],
            'validation_can_be_deferred': [
                'Multi-stage development with explicit stages',
                'Batch processing with planned validation checkpoints',
                'User explicitly requests deferment'
            ],
            'default_behavior': 'ALWAYS validate immediately unless explicit multi-stage process',
            'content_verification': 'MANDATORY - verify template data actually used',
            'screenshot_requirements': 'Complete document capture including all pages'
        }

    def _get_libreoffice_status(self) -> Dict:
        """Get LibreOffice application status"""
        lo_state = self.lo_monitor.get_libreoffice_state()
        return {
            'monitoring_active': True,
            'current_state': lo_state,
            'processes_running': len(lo_state['processes']),
            'dialogs_detected': len(lo_state['dialogs']),
            'documents_open': len(lo_state['documents']),
            'error_conditions': len(lo_state['errors']),
            'auto_screenshot': 'Enabled for state changes'
        }

    def _get_active_protocols(self) -> Dict:
        """Get active operational protocols"""
        return {
            'pre_generation': [
                'Load current operational rules',
                'Check LibreOffice state',
                'Verify template JSON compliance',
                'Validate input data completeness'
            ],
            'during_generation': [
                'Monitor LibreOffice state changes',
                'Detect dialogs and errors',
                'Track generation progress',
                'Auto-capture screenshots on events'
            ],
            'post_generation': [
                'Verify template data usage (CRITICAL)',
                'Perform visual validation',
                'Check mathematical accuracy',
                'Validate professional formatting',
                'Organize files properly'
            ],
            'error_recovery': [
                'Screenshot any dialogs immediately',
                'Analyze error conditions',
                'Attempt automatic recovery',
                'Report to user with details'
            ]
        }

    def _get_performance_targets(self) -> Dict:
        """Get performance benchmarks and targets"""
        return {
            'speed_targets': {
                'document_generation': '< 30 seconds',
                'visual_validation': '< 45 seconds',
                'error_recovery': '< 60 seconds'
            },
            'quality_standards': {
                'mathematical_accuracy': '100% - zero calculation errors',
                'template_usage': '100% - templates must drive content',
                'professional_formatting': '95%+ visual quality score',
                'tax_compliance': '100% - state rules correctly applied'
            },
            'consistency_metrics': {
                'protocol_compliance': '95%+ adherence to procedures',
                'error_detection': '100% capture of LibreOffice dialogs',
                'documentation': 'All operations logged and tracked'
            }
        }

    def _get_error_procedures(self) -> Dict:
        """Get standardized error recovery procedures"""
        return {
            'libreoffice_errors': [
                'Screenshot dialog immediately',
                'Analyze dialog content',
                'Attempt standard recovery actions',
                'Report to user if unresolvable'
            ],
            'template_processing_errors': [
                'Verify JSON syntax',
                'Check schema compliance',
                'Test with known working template',
                'Report template processing failure'
            ],
            'file_system_errors': [
                'Check file permissions',
                'Create missing directories',
                'Attempt backup recovery',
                'Provide manual resolution steps'
            ]
        }

    def before_document_generation(self, operation_type: str, template_path: Optional[str] = None) -> Dict:
        """Execute pre-generation protocol enforcement"""
        print("🔧 Executing pre-generation protocols...")

        results = {
            'timestamp': datetime.now().isoformat(),
            'operation_type': operation_type,
            'template_path': template_path,
            'checks_performed': [],
            'warnings': [],
            'errors': []
        }

        # Check 1: LibreOffice state
        try:
            lo_state = self.lo_monitor.get_libreoffice_state()
            if lo_state['errors']:
                results['warnings'].extend(lo_state['errors'])
            results['checks_performed'].append('LibreOffice state checked')
        except Exception as e:
            results['errors'].append(f"LibreOffice state check failed: {e}")

        # Check 2: Template validation (if applicable)
        if template_path and Path(template_path).exists():
            try:
                with open(template_path, 'r') as f:
                    template_data = json.load(f)
                results['checks_performed'].append('Template JSON validated')
            except json.JSONDecodeError as e:
                results['errors'].append(f"Template JSON invalid: {e}")
            except Exception as e:
                results['errors'].append(f"Template validation failed: {e}")

        # Check 3: Screenshot environment
        if not self.validation_dir.exists():
            self.validation_dir.mkdir(parents=True, exist_ok=True)
            results['checks_performed'].append('Screenshot directory created')
        else:
            results['checks_performed'].append('Screenshot directory verified')

        # Log the pre-generation check
        self.session_log.append(results)

        return results

    def after_document_generation(self, document_path: str, template_used: Optional[str] = None) -> Dict:
        """Execute post-generation protocol enforcement"""
        print("🔍 Executing post-generation validation protocols...")

        results = {
            'timestamp': datetime.now().isoformat(),
            'document_path': document_path,
            'template_used': template_used,
            'validations_performed': [],
            'issues_found': [],
            'screenshot_captured': False
        }

        # Validation 1: File existence and basic properties
        doc_path = Path(document_path)
        if doc_path.exists():
            results['validations_performed'].append('Document file exists')
            results['file_size'] = doc_path.stat().st_size
        else:
            results['issues_found'].append('Generated document file not found')
            return results

        # Validation 2: Template content usage check (CRITICAL)
        if template_used:
            # This is where we would verify the document actually uses template data
            # For now, flag as critical check needed
            results['validations_performed'].append('Template usage verification (CRITICAL - MANUAL CHECK NEEDED)')
            results['issues_found'].append('CRITICAL: Cannot verify template data usage - UNO generator may be using hardcoded content')

        # Validation 3: Automatic screenshot
        try:
            screenshot_info = self.lo_monitor.capture_screenshot(
                reason="post_generation_validation",
                additional_info=f"Document: {document_path}"
            )
            if 'error' not in screenshot_info:
                results['screenshot_captured'] = True
                results['screenshot_path'] = screenshot_info.get('filepath')
                results['validations_performed'].append('Screenshot captured for visual validation')
            else:
                results['issues_found'].append(f"Screenshot failed: {screenshot_info['error']}")
        except Exception as e:
            results['issues_found'].append(f"Screenshot capture error: {e}")

        # Log the post-generation validation
        self.session_log.append(results)

        return results

    def validate_operation_compliance(self, operation: str, context: Dict) -> Dict:
        """Check if operation follows current protocols"""
        compliance = {
            'operation': operation,
            'timestamp': datetime.now().isoformat(),
            'compliant': True,
            'violations': [],
            'recommendations': []
        }

        # Check for template processing compliance
        if operation == 'document_generation':
            if not context.get('visual_validation_planned'):
                compliance['violations'].append('Visual validation not planned for document generation')
                compliance['compliant'] = False

            if context.get('template_path') and not context.get('content_verification_planned'):
                compliance['violations'].append('Template content verification not planned')
                compliance['compliant'] = False

        # Check for LibreOffice monitoring compliance
        if operation in ['document_generation', 'document_editing']:
            if not context.get('libreoffice_monitoring_active'):
                compliance['violations'].append('LibreOffice monitoring not active during document operations')
                compliance['compliant'] = False

        # Add recommendations based on violations
        if compliance['violations']:
            compliance['recommendations'].extend([
                'Enable visual validation for all document generation',
                'Verify template content usage before claiming success',
                'Activate LibreOffice monitoring during document operations'
            ])

        return compliance

    def get_protocol_reminder(self, operation_type: str) -> str:
        """Get protocol reminder for specific operation"""
        reminders = {
            'document_generation': """
🔧 DOCUMENT GENERATION PROTOCOL REMINDER:
1. Check LibreOffice state before starting
2. Monitor for dialogs during generation
3. CRITICAL: Verify template data actually used (not hardcoded content)
4. Capture screenshot immediately after generation
5. Perform visual validation with Claude Vision
6. Check mathematical accuracy and formatting
            """,
            'template_validation': """
🔍 TEMPLATE VALIDATION PROTOCOL REMINDER:
1. Verify JSON syntax and schema compliance
2. Test with actual template processing (not hardcoded output)
3. Compare different templates produce different outputs
4. Check file sizes and content uniqueness
5. Visual validation of template-specific content
            """,
            'visual_validation': """
📸 VISUAL VALIDATION PROTOCOL REMINDER:
1. Capture complete document (all pages)
2. Screenshot any LibreOffice dialogs
3. Use Claude Vision for professional assessment
4. Check formatting, content, and presentation
5. Verify template-specific content appears correctly
            """
        }

        return reminders.get(operation_type, "No specific protocol reminder available")

    def get_session_summary(self) -> Dict:
        """Get summary of current session protocols and compliance"""
        return {
            'session_start': self.session_log[0]['timestamp'] if self.session_log else None,
            'total_operations': len(self.session_log),
            'context_injections': len([log for log in self.session_log if log.get('action') == 'context_injection']),
            'system_status': self._get_system_status(),
            'recent_operations': self.session_log[-5:] if len(self.session_log) > 5 else self.session_log,
            'libreoffice_monitoring': self.lo_monitor.get_monitoring_summary()
        }

def main():
    """Demo the protocol manager"""
    manager = ProtocolManager()

    print("Protocol Manager Demo")
    print("=" * 50)

    # Inject session context
    context = manager.inject_session_context()
    print("Session Context Injected:")
    print(json.dumps(context, indent=2))

    print("\n" + "=" * 50)

    # Get protocol reminder
    reminder = manager.get_protocol_reminder('document_generation')
    print("Protocol Reminder:")
    print(reminder)

if __name__ == "__main__":
    main()