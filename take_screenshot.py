#!/usr/bin/env python3
"""
Simple screenshot utility for Squirt visual validation
"""
import subprocess
import time
import sys
import os

def take_screenshot(output_path):
    """Take a screenshot using available system tools"""
    timestamp = int(time.time())

    # Try different screenshot methods
    methods = [
        # Method 1: xwd + convert (if available)
        lambda: subprocess.run([
            'sh', '-c',
            f'xwd -root | convert xwd:- png:{output_path}'
        ], check=True),

        # Method 2: gnome-screenshot (if available)
        lambda: subprocess.run([
            'gnome-screenshot', '-f', output_path
        ], check=True),

        # Method 3: scrot (if available)
        lambda: subprocess.run([
            'scrot', output_path
        ], check=True),

        # Method 4: import from ImageMagick
        lambda: subprocess.run([
            'import', '-window', 'root', output_path
        ], check=True),
    ]

    for i, method in enumerate(methods):
        try:
            print(f"Trying screenshot method {i+1}...")
            method()
            if os.path.exists(output_path):
                print(f"✅ Screenshot saved: {output_path}")
                return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"❌ Method {i+1} failed: {e}")
            continue

    print("❌ All screenshot methods failed")
    return False

if __name__ == "__main__":
    output_path = sys.argv[1] if len(sys.argv) > 1 else f"/home/johnny5/Squirt/validation_screenshots/screenshot_{int(time.time())}.png"
    take_screenshot(output_path)