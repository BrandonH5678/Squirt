#!/usr/bin/env python3
"""
Automated Screenshot System for Squirt Visual Validation
Handles screenshots, dialogue responses, and file management automatically
"""

import subprocess
import time
import os
import sys
from pathlib import Path
import tempfile
import signal

class AutomatedScreenshotSystem:
    def __init__(self, output_dir="/home/johnny5/Squirt/validation_screenshots"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def take_screenshot_auto(self, filename_prefix="validation"):
        """Take screenshot automatically without user interaction"""
        timestamp = int(time.time())
        temp_file = f"/tmp/screenshot_{timestamp}.png"
        final_file = self.output_dir / f"{filename_prefix}_{timestamp}.png"

        # Method 1: Try xwd + convert approach
        try:
            # Capture screen to XWD format
            subprocess.run(['xwd', '-root', '-out', f'/tmp/screen_{timestamp}.xwd'],
                         check=True, timeout=10)

            # Convert to PNG using netpbm tools if available
            try:
                subprocess.run(['xwdtopnm', f'/tmp/screen_{timestamp}.xwd'],
                             stdout=open(f'/tmp/screen_{timestamp}.pnm', 'w'),
                             check=True, timeout=10)
                subprocess.run(['pnmtopng', f'/tmp/screen_{timestamp}.pnm'],
                             stdout=open(str(final_file), 'w'),
                             check=True, timeout=10)
                # Cleanup temp files
                os.remove(f'/tmp/screen_{timestamp}.xwd')
                os.remove(f'/tmp/screen_{timestamp}.pnm')
                print(f"✅ Screenshot saved: {final_file}")
                return str(final_file)
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        # Method 2: Try mate-screenshot with auto-save
        try:
            # Use mate-screenshot with delayed capture
            result = subprocess.run([
                'mate-screenshot', '--delay=2'
            ], capture_output=True, timeout=30)

            # Look for the saved screenshot
            desktop_screenshots = list(Path('/home/johnny5/Desktop').glob('Screenshot*.png'))
            if desktop_screenshots:
                # Move the newest screenshot
                newest = max(desktop_screenshots, key=lambda p: p.stat().st_mtime)
                newest.rename(final_file)
                print(f"✅ Screenshot saved: {final_file}")
                return str(final_file)

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # Method 3: Use Python automation to trigger screenshot
        try:
            # Install required packages programmatically if needed
            self._ensure_screenshot_deps()

            # Try using pyautogui if available
            import pyautogui
            screenshot = pyautogui.screenshot()
            screenshot.save(str(final_file))
            print(f"✅ Screenshot saved: {final_file}")
            return str(final_file)

        except ImportError:
            pass
        except Exception as e:
            print(f"PyAutoGUI failed: {e}")

        print("❌ All screenshot methods failed")
        return None

    def _ensure_screenshot_deps(self):
        """Install screenshot dependencies if needed"""
        try:
            # Try to install pyautogui if not available
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyautogui'],
                         check=True, capture_output=True)
        except:
            pass

    def handle_libreoffice_dialogs(self, action="dismiss"):
        """Handle LibreOffice dialog windows automatically"""
        try:
            # Get list of LibreOffice windows
            result = subprocess.run(['xwininfo', '-tree', '-root'],
                                  capture_output=True, text=True)

            # Look for dialog windows
            dialog_keywords = ['Document Recovery', 'Error', 'Warning', 'Save', 'Open']
            lines = result.stdout.split('\n')

            for line in lines:
                if any(keyword in line for keyword in dialog_keywords):
                    # Extract window ID
                    if '0x' in line:
                        window_id = line.split()[0]
                        if action == "dismiss":
                            # Send Escape key to dismiss dialog
                            subprocess.run(['xdotool', 'key', '--window', window_id, 'Escape'])
                        elif action == "accept":
                            # Send Enter key to accept
                            subprocess.run(['xdotool', 'key', '--window', window_id, 'Return'])

        except (subprocess.CalledProcessError, FileNotFoundError):
            # xdotool not available, try alternative
            try:
                # Use wmctrl to close dialogs
                subprocess.run(['wmctrl', '-c', 'Document Recovery'], check=False)
                subprocess.run(['wmctrl', '-c', 'LibreOffice'], check=False)
            except FileNotFoundError:
                pass

    def wait_for_libreoffice_ready(self, timeout=30):
        """Wait for LibreOffice to finish loading"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # Check if LibreOffice is responding
                result = subprocess.run(['pgrep', '-f', 'soffice.bin'],
                                      capture_output=True)
                if result.returncode == 0:
                    # LibreOffice is running, wait a bit more for full load
                    time.sleep(3)

                    # Check for dialog windows and handle them
                    self.handle_libreoffice_dialogs("dismiss")
                    time.sleep(1)

                    return True

            except subprocess.CalledProcessError:
                pass

            time.sleep(1)

        return False

    def capture_libreoffice_document(self, filename_prefix="document"):
        """Complete workflow: wait for LibreOffice, handle dialogs, take screenshot"""
        print("🔄 Waiting for LibreOffice to load...")

        if not self.wait_for_libreoffice_ready():
            print("❌ LibreOffice didn't load properly")
            return None

        print("✅ LibreOffice ready")

        # Give extra time for document rendering
        time.sleep(2)

        # Take screenshot
        return self.take_screenshot_auto(filename_prefix)

def main():
    if len(sys.argv) > 1:
        filename_prefix = sys.argv[1]
    else:
        filename_prefix = "validation"

    system = AutomatedScreenshotSystem()

    if len(sys.argv) > 2 and sys.argv[2] == "--wait-libreoffice":
        screenshot_path = system.capture_libreoffice_document(filename_prefix)
    else:
        screenshot_path = system.take_screenshot_auto(filename_prefix)

    if screenshot_path:
        print(f"Screenshot saved to: {screenshot_path}")
        return 0
    else:
        print("Failed to capture screenshot")
        return 1

if __name__ == "__main__":
    sys.exit(main())