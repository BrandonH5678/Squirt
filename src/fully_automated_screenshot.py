#!/usr/bin/env python3
"""
Fully Automated Screenshot System for Squirt Visual Validation
Complete automation with dialog handling and file management
"""

import subprocess
import time
import os
import sys
from pathlib import Path

class FullyAutomatedScreenshot:
    def __init__(self, output_dir="/home/johnny5/Squirt/validation_screenshots"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def handle_dialogs(self, action="dismiss"):
        """Automatically handle LibreOffice and system dialogs"""
        try:
            # Find dialog windows using wmctrl
            result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True)

            dialog_keywords = ['Document Recovery', 'Error', 'Warning', 'Save As', 'Open', 'Dialog']

            for line in result.stdout.split('\n'):
                if any(keyword in line for keyword in dialog_keywords):
                    window_id = line.split()[0]

                    if action == "dismiss":
                        # Send Escape key to dismiss
                        subprocess.run(['xdotool', 'key', '--window', window_id, 'Escape'],
                                     check=False, timeout=5)
                    elif action == "accept":
                        # Send Enter key to accept
                        subprocess.run(['xdotool', 'key', '--window', window_id, 'Return'],
                                     check=False, timeout=5)

            # Also try to close any dialogs by window class
            subprocess.run(['wmctrl', '-c', 'Document Recovery'], check=False)

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass

    def take_automated_screenshot(self, filename_prefix="validation"):
        """Take screenshot with full automation - no user interaction required"""
        timestamp = int(time.time())
        temp_xwd = f"/tmp/screenshot_{timestamp}.xwd"
        final_png = self.output_dir / f"{filename_prefix}_{timestamp}.png"

        print(f"📸 Taking fully automated screenshot...")

        # Handle any existing dialogs first
        self.handle_dialogs("dismiss")
        time.sleep(1)

        try:
            # Step 1: Capture screen with xwd
            subprocess.run(['xwd', '-root', '-out', temp_xwd],
                         check=True, timeout=15)

            # Step 2: Convert to PNG with ImageMagick
            subprocess.run(['convert', f'xwd:{temp_xwd}', f'png:{final_png}'],
                         check=True, timeout=15)

            # Step 3: Cleanup temp file
            os.remove(temp_xwd)

            print(f"✅ Screenshot automatically saved: {final_png}")
            return str(final_png)

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            print(f"❌ Screenshot failed: {e}")

            # Cleanup on failure
            if os.path.exists(temp_xwd):
                os.remove(temp_xwd)

            return None

    def wait_for_libreoffice_and_screenshot(self, filename_prefix="libreoffice", timeout=30):
        """Wait for LibreOffice to load, handle dialogs, then take screenshot"""
        print(f"🔄 Waiting for LibreOffice to be ready...")

        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check if LibreOffice is running
            try:
                result = subprocess.run(['pgrep', '-f', 'soffice'], capture_output=True)
                if result.returncode == 0:
                    print("✅ LibreOffice detected")

                    # Handle any dialogs
                    self.handle_dialogs("dismiss")

                    # Wait a bit more for document to fully load
                    time.sleep(3)

                    # Take screenshot
                    return self.take_automated_screenshot(filename_prefix)

            except subprocess.CalledProcessError:
                pass

            time.sleep(1)

        print("❌ LibreOffice timeout - taking screenshot anyway")
        return self.take_automated_screenshot(filename_prefix)

def main():
    """Command line interface"""
    system = FullyAutomatedScreenshot()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--wait-libreoffice":
            prefix = sys.argv[2] if len(sys.argv) > 2 else "libreoffice"
            screenshot_path = system.wait_for_libreoffice_and_screenshot(prefix)
        else:
            prefix = sys.argv[1]
            screenshot_path = system.take_automated_screenshot(prefix)
    else:
        screenshot_path = system.take_automated_screenshot()

    if screenshot_path:
        print(f"🎯 SUCCESS: {screenshot_path}")
        return 0
    else:
        print("❌ FAILED: Could not capture screenshot")
        return 1

if __name__ == "__main__":
    sys.exit(main())