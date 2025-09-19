#!/usr/bin/env python3
"""
Squirt File Scan Daemon
Automated routine to detect and organize untracked files
"""

import time
import sys
import os
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from file_tracking_system import FileTrackingSystem

class FileScanDaemon:
    """Daemon for automatic file scanning and organization"""
    
    def __init__(self, scan_interval_minutes: int = 15):
        self.tracker = FileTrackingSystem()
        self.scan_interval = scan_interval_minutes
        self.last_scan_results = []
        
    def run_scan(self):
        """Run a single scan cycle"""
        print(f"\n🔍 Running Squirt file scan at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Scan and organize files
            organized_files = self.tracker.scan_and_organize_untracked_files()
            
            if organized_files:
                print(f"✅ Organized {len(organized_files)} files:")
                for file_move in organized_files:
                    print(f"   📁 {file_move}")
                
                # Create backup log
                self._log_scan_results(organized_files)
            else:
                print("ℹ️  No untracked files found")
            
            self.last_scan_results = organized_files
            
            # Clean up old temp files (weekly)
            if datetime.now().hour == 2 and datetime.now().minute < self.scan_interval:
                self._cleanup_old_files()
                
        except Exception as e:
            print(f"❌ Error during file scan: {e}")
    
    def _log_scan_results(self, results: list):
        """Log scan results for audit trail"""
        log_dir = self.tracker.base_dir / "scan_logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        with open(log_file, 'w') as f:
            f.write(f"Squirt File Scan Results\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Files Organized: {len(results)}\n\n")
            
            for file_move in results:
                f.write(f"{file_move}\n")
    
    def _cleanup_old_files(self):
        """Clean up old temporary files"""
        print("🧹 Running weekly cleanup...")
        removed_files = self.tracker.cleanup_temp_files(older_than_days=7)
        
        if removed_files:
            print(f"🗑️  Removed {len(removed_files)} old temporary files")
        else:
            print("ℹ️  No old files to clean up")
    
    def run_daemon(self):
        """Run the daemon continuously"""
        print(f"🚀 Starting Squirt File Scan Daemon")
        print(f"📅 Scanning every {self.scan_interval} minutes")
        print("Press Ctrl+C to stop")
        
        # Run initial scan
        self.run_scan()
        
        # Keep running
        try:
            while True:
                time.sleep(self.scan_interval * 60)  # Sleep for interval
                self.run_scan()
                
        except KeyboardInterrupt:
            print("\n🛑 File scan daemon stopped")
    
    def run_once(self):
        """Run scan once and exit"""
        self.run_scan()
        return self.last_scan_results

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Squirt File Scan Daemon")
    parser.add_argument("--once", action="store_true", 
                       help="Run scan once and exit")
    parser.add_argument("--interval", type=int, default=15,
                       help="Scan interval in minutes (default: 15)")
    
    args = parser.parse_args()
    
    daemon = FileScanDaemon(scan_interval_minutes=args.interval)
    
    if args.once:
        results = daemon.run_once()
        if results:
            print(f"\n✅ Scan complete. Organized {len(results)} files.")
        else:
            print("\n✅ Scan complete. No files needed organization.")
    else:
        daemon.run_daemon()

if __name__ == "__main__":
    main()