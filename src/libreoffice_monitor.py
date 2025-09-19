#!/usr/bin/env python3
"""
LibreOffice State Monitoring System for Squirt
Provides real-time monitoring of LibreOffice application state,
dialog detection, and automatic screenshot capture for AI validation.
"""

import subprocess
import time
import os
import json
from datetime import datetime
from pathlib import Path
import base64

class LibreOfficeMonitor:
    """Monitor LibreOffice application state and automate screenshot capture"""

    def __init__(self, screenshot_dir="/home/johnny5/Squirt/validation_screenshots"):
        self.screenshot_dir = Path(screenshot_dir)
        self.screenshot_dir.mkdir(exist_ok=True)
        self.last_state = {}
        self.monitoring_log = []

    def get_libreoffice_state(self):
        """Get current LibreOffice application state"""
        state = {
            'timestamp': datetime.now().isoformat(),
            'processes': self._get_libreoffice_processes(),
            'windows': self._get_libreoffice_windows(),
            'dialogs': self._detect_dialogs(),
            'documents': self._get_open_documents(),
            'errors': self._check_error_conditions()
        }
        return state

    def _get_libreoffice_processes(self):
        """Check for running LibreOffice processes"""
        try:
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True,
                timeout=5
            )
            processes = []
            for line in result.stdout.split('\n'):
                if any(proc in line.lower() for proc in ['soffice', 'libreoffice']):
                    processes.append(line.strip())
            return processes
        except subprocess.TimeoutExpired:
            return ["Error: Process check timeout"]
        except Exception as e:
            return [f"Error: {str(e)}"]

    def _get_libreoffice_windows(self):
        """Get LibreOffice window information"""
        try:
            result = subprocess.run(
                ['wmctrl', '-l'],
                capture_output=True,
                text=True,
                timeout=5
            )
            windows = []
            for line in result.stdout.split('\n'):
                if 'libreoffice' in line.lower() or 'writer' in line.lower():
                    windows.append(line.strip())
            return windows
        except subprocess.TimeoutExpired:
            return ["Error: Window check timeout"]
        except FileNotFoundError:
            return ["Error: wmctrl not available - install with: sudo apt install wmctrl"]
        except Exception as e:
            return [f"Error: {str(e)}"]

    def _detect_dialogs(self):
        """Detect LibreOffice dialog boxes"""
        try:
            result = subprocess.run(
                ['wmctrl', '-l'],
                capture_output=True,
                text=True,
                timeout=5
            )
            dialogs = []
            for line in result.stdout.split('\n'):
                line_lower = line.lower()
                if any(dialog_type in line_lower for dialog_type in [
                    'dialog', 'error', 'warning', 'save as', 'open',
                    'export', 'print', 'properties', 'options'
                ]):
                    dialogs.append({
                        'window_info': line.strip(),
                        'dialog_type': self._classify_dialog(line_lower),
                        'detected_at': datetime.now().isoformat()
                    })
            return dialogs
        except Exception as e:
            return [{'error': f"Dialog detection failed: {str(e)}"}]

    def _classify_dialog(self, window_text):
        """Classify the type of dialog detected"""
        if 'error' in window_text:
            return 'error'
        elif 'warning' in window_text:
            return 'warning'
        elif 'save' in window_text:
            return 'save_dialog'
        elif 'open' in window_text:
            return 'open_dialog'
        elif 'export' in window_text:
            return 'export_dialog'
        elif 'print' in window_text:
            return 'print_dialog'
        else:
            return 'unknown_dialog'

    def _get_open_documents(self):
        """Get list of currently open documents"""
        # This is a simplified implementation
        # In practice, you might parse LibreOffice's recent files or use UNO API
        windows = self._get_libreoffice_windows()
        documents = []
        for window in windows:
            if isinstance(window, str) and not window.startswith('Error:'):
                # Extract document name from window title
                parts = window.split()
                if len(parts) > 3:
                    doc_name = ' '.join(parts[3:])
                    if doc_name and doc_name not in ['LibreOffice', 'Writer']:
                        documents.append(doc_name)
        return documents

    def _check_error_conditions(self):
        """Check for LibreOffice error conditions"""
        errors = []

        # Check for crash recovery files
        recovery_dir = Path.home() / '.config/libreoffice/4/user/backup'
        if recovery_dir.exists():
            recovery_files = list(recovery_dir.glob('*.recovery'))
            if recovery_files:
                errors.append(f"Crash recovery files found: {len(recovery_files)} files")

        # Check for lock files (indicating unsaved work)
        for pattern in ['**/.~lock.*#', '**/~$*']:
            lock_files = list(Path.home().glob(pattern))
            if lock_files:
                errors.append(f"Lock files found: {len(lock_files)} files")

        return errors

    def detect_state_change(self):
        """Detect if LibreOffice state has changed significantly"""
        current_state = self.get_libreoffice_state()

        changes = {
            'processes_changed': False,
            'new_dialogs': [],
            'new_documents': [],
            'new_errors': []
        }

        if self.last_state:
            # Check for process changes
            if current_state['processes'] != self.last_state.get('processes', []):
                changes['processes_changed'] = True

            # Check for new dialogs
            old_dialogs = {d.get('window_info', '') for d in self.last_state.get('dialogs', [])}
            new_dialogs = {d.get('window_info', '') for d in current_state['dialogs']}
            changes['new_dialogs'] = list(new_dialogs - old_dialogs)

            # Check for new documents
            old_docs = set(self.last_state.get('documents', []))
            new_docs = set(current_state['documents'])
            changes['new_documents'] = list(new_docs - old_docs)

            # Check for new errors
            old_errors = set(self.last_state.get('errors', []))
            new_errors = set(current_state['errors'])
            changes['new_errors'] = list(new_errors - old_errors)

        self.last_state = current_state
        return changes, current_state

    def capture_screenshot(self, reason="state_change", additional_info=""):
        """Capture screenshot when LibreOffice state changes"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"libreoffice_{reason}_{timestamp}.png"
        filepath = self.screenshot_dir / filename

        try:
            # Try multiple screenshot methods
            screenshot_methods = [
                ['gnome-screenshot', '-f', str(filepath)],
                ['scrot', str(filepath)],
                ['import', '-window', 'root', str(filepath)],  # ImageMagick
                ['xwd', '-root', '-out', str(filepath)]
            ]

            for method in screenshot_methods:
                try:
                    result = subprocess.run(method, capture_output=True, timeout=10)
                    if result.returncode == 0 and filepath.exists():
                        screenshot_info = {
                            'filepath': str(filepath),
                            'reason': reason,
                            'timestamp': datetime.now().isoformat(),
                            'additional_info': additional_info,
                            'file_size': filepath.stat().st_size,
                            'method_used': method[0]
                        }
                        self.monitoring_log.append(screenshot_info)
                        return screenshot_info
                except FileNotFoundError:
                    continue
                except subprocess.TimeoutExpired:
                    continue

            # If all methods fail, create a placeholder file
            placeholder_info = {
                'filepath': str(filepath),
                'reason': reason,
                'timestamp': datetime.now().isoformat(),
                'additional_info': additional_info,
                'error': 'No screenshot utility available - install gnome-screenshot, scrot, or imagemagick'
            }

            # Create a text placeholder
            with open(filepath.with_suffix('.txt'), 'w') as f:
                f.write(f"Screenshot placeholder - {reason} at {timestamp}\n")
                f.write(f"Additional info: {additional_info}\n")
                f.write("Install a screenshot utility: sudo apt install gnome-screenshot\n")

            return placeholder_info

        except Exception as e:
            return {'error': f"Screenshot error: {str(e)}"}

    def encode_screenshot_for_claude(self, filepath):
        """Encode screenshot as base64 for Claude Vision API"""
        try:
            with open(filepath, 'rb') as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return {
                    'base64': encoded_string,
                    'media_type': 'image/png',
                    'filepath': str(filepath)
                }
        except Exception as e:
            return {'error': f"Encoding failed: {str(e)}"}

    def monitor_and_capture(self, duration_seconds=None):
        """Continuously monitor LibreOffice and capture screenshots on changes"""
        print(f"Starting LibreOffice monitoring...")
        print(f"Screenshots will be saved to: {self.screenshot_dir}")

        start_time = time.time()

        try:
            while True:
                changes, current_state = self.detect_state_change()

                # Check if we should capture a screenshot
                should_capture = False
                capture_reason = ""

                if changes['processes_changed']:
                    should_capture = True
                    capture_reason = "process_change"

                if changes['new_dialogs']:
                    should_capture = True
                    capture_reason = "dialog_detected"

                if changes['new_documents']:
                    should_capture = True
                    capture_reason = "document_opened"

                if changes['new_errors']:
                    should_capture = True
                    capture_reason = "error_detected"

                if should_capture:
                    screenshot_info = self.capture_screenshot(
                        reason=capture_reason,
                        additional_info=json.dumps(changes, indent=2)
                    )
                    print(f"Screenshot captured: {screenshot_info}")

                # Check duration limit
                if duration_seconds and (time.time() - start_time) > duration_seconds:
                    break

                # Wait before next check
                time.sleep(1)

        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        except Exception as e:
            print(f"Monitoring error: {e}")

    def get_monitoring_summary(self):
        """Get summary of monitoring session"""
        return {
            'screenshots_captured': len(self.monitoring_log),
            'current_state': self.get_libreoffice_state(),
            'screenshot_log': self.monitoring_log[-10:]  # Last 10 screenshots
        }

def main():
    """Demo/test the LibreOffice monitoring system"""
    monitor = LibreOfficeMonitor()

    print("LibreOffice State Monitoring Demo")
    print("=" * 50)

    # Get initial state
    state = monitor.get_libreoffice_state()
    print("Current LibreOffice State:")
    print(json.dumps(state, indent=2))

    # Capture a screenshot
    print("\nCapturing test screenshot...")
    screenshot = monitor.capture_screenshot(reason="demo_test")
    print(f"Screenshot result: {screenshot}")

    # Monitor for changes (uncomment to test)
    # print("\nStarting monitoring for 30 seconds...")
    # monitor.monitor_and_capture(duration_seconds=30)

if __name__ == "__main__":
    main()