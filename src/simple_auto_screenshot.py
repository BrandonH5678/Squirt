#!/usr/bin/env python3
"""
Simple automated screenshot system using available system tools
"""
import subprocess
import time
import os
from pathlib import Path

def auto_screenshot(filename_prefix="validation"):
    """Take screenshot automatically and save to validation folder"""
    timestamp = int(time.time())
    output_dir = Path("/home/johnny5/Squirt/validation_screenshots")
    final_file = output_dir / f"{filename_prefix}_{timestamp}.png"

    print(f"📸 Taking automated screenshot...")

    # Method: Use mate-screenshot with auto-handling
    try:
        # Start mate-screenshot in background
        proc = subprocess.Popen(['mate-screenshot'])

        # Wait a moment for the dialog to appear
        time.sleep(2)

        # Simulate Enter key press to take screenshot immediately
        subprocess.run(['xdotool', 'key', 'Return'], check=False)

        # Wait for screenshot to be taken
        time.sleep(3)

        # Look for screenshot on desktop
        desktop_screenshots = list(Path('/home/johnny5/Desktop').glob('Screenshot*.png'))
        if desktop_screenshots:
            # Get the newest one
            newest = max(desktop_screenshots, key=lambda p: p.stat().st_mtime)
            # Move it to our validation folder
            newest.rename(final_file)
            print(f"✅ Screenshot automatically saved: {final_file}")
            return str(final_file)

        # If xdotool didn't work, try manual timeout approach
        proc.wait(timeout=30)

    except subprocess.TimeoutExpired:
        proc.terminate()

        # Check for screenshot again
        desktop_screenshots = list(Path('/home/johnny5/Desktop').glob('Screenshot*.png'))
        if desktop_screenshots:
            newest = max(desktop_screenshots, key=lambda p: p.stat().st_mtime)
            newest.rename(final_file)
            print(f"✅ Screenshot saved: {final_file}")
            return str(final_file)

    except FileNotFoundError:
        print("❌ xdotool not available for automation")

    print("❌ Automated screenshot failed")
    return None

if __name__ == "__main__":
    import sys
    prefix = sys.argv[1] if len(sys.argv) > 1 else "validation"
    result = auto_screenshot(prefix)
    sys.exit(0 if result else 1)