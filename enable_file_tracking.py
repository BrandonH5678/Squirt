#!/usr/bin/env python3
"""
Squirt File Tracking Enabler
One-time setup and ongoing maintenance for the file tracking system
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from file_tracking_system import FileTrackingSystem

def setup_file_tracking():
    """Set up the file tracking system"""
    print("🔧 Setting up Squirt File Tracking System...")
    
    tracker = FileTrackingSystem()
    
    print("✅ File tracking system initialized")
    print(f"📁 Client files directory: {tracker.client_files_dir}")
    print(f"📁 Temp files directory: {tracker.temp_dir}")
    print(f"📊 Tracking database: {tracker.tracking_db}")
    
    # Run initial scan
    print("\n🔍 Running initial file scan...")
    organized_files = tracker.scan_and_organize_untracked_files()
    
    if organized_files:
        print(f"✅ Organized {len(organized_files)} files:")
        for file_move in organized_files:
            print(f"   📁 {file_move}")
    else:
        print("ℹ️  No untracked files found")
    
    print("\n📋 File Tracking System Commands:")
    print("   python3 file_scan_daemon.py --once    # Run scan once")
    print("   python3 file_scan_daemon.py          # Run continuous scanning")
    print("")
    print("🎯 Next steps:")
    print("   1. All new files will be automatically saved to tracked locations")
    print("   2. Run periodic scans to catch imported files")
    print("   3. Check temp_files/ directory for files needing manual organization")
    
    return tracker

def show_status():
    """Show current file tracking status"""
    tracker = FileTrackingSystem()
    
    print("📊 Squirt File Tracking Status")
    print(f"   Tracking database: {tracker.tracking_db}")
    print(f"   Database exists: {tracker.tracking_db.exists()}")
    
    if tracker.tracking_db.exists():
        total_tracked = len(tracker.tracked_files.get("tracked_files", {}))
        total_clients = len(tracker.tracked_files.get("client_mappings", {}))
        last_scan = tracker.tracked_files.get("last_scan", "Never")
        
        print(f"   Tracked files: {total_tracked}")
        print(f"   Client directories: {total_clients}")
        print(f"   Last scan: {last_scan}")
        
        # Show client breakdown
        if total_clients > 0:
            print("\n📁 Client Files:")
            for client, file_ids in tracker.tracked_files["client_mappings"].items():
                existing_files = sum(1 for fid in file_ids 
                                   if fid in tracker.tracked_files["tracked_files"] 
                                   and Path(tracker.tracked_files["tracked_files"][fid]["path"]).exists())
                print(f"   {client}: {existing_files} files")
    
    # Check temp directory
    temp_count = len(list(tracker.temp_dir.glob("*"))) if tracker.temp_dir.exists() else 0
    print(f"   Temp files needing review: {temp_count}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Squirt File Tracking Setup")
    parser.add_argument("--status", action="store_true", 
                       help="Show current tracking status")
    parser.add_argument("--setup", action="store_true",
                       help="Set up file tracking system")
    
    args = parser.parse_args()
    
    if args.status:
        show_status()
    elif args.setup:
        setup_file_tracking()
    else:
        # Default: show status and offer setup
        show_status()
        print("\nRun with --setup to initialize file tracking")

if __name__ == "__main__":
    main()