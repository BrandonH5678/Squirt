#!/usr/bin/env python3
"""
Squirt File Tracking System
Ensures all generated and imported files are properly tracked and organized
"""

import os
import shutil
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import hashlib
import time

class FileTrackingSystem:
    """Centralized file tracking and organization system for Squirt"""
    
    def __init__(self, base_dir: str = "/home/johnny5/Squirt"):
        self.base_dir = Path(base_dir)
        self.client_files_dir = self.base_dir / "Client Files"
        self.temp_dir = self.base_dir / "temp_files"
        self.tracking_db = self.base_dir / ".file_tracking.json"
        
        # Create necessary directories
        self.client_files_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        
        # Initialize tracking database
        self.tracked_files = self._load_tracking_db()
        
        # File type mappings
        self.file_categories = {
            '.odt': 'documents',
            '.pdf': 'documents', 
            '.docx': 'documents',
            '.txt': 'documents',
            '.xlsx': 'spreadsheets',
            '.numbers': 'spreadsheets',
            '.csv': 'data',
            '.jpg': 'images',
            '.jpeg': 'images',
            '.png': 'images',
            '.webp': 'images'
        }
        
    def _load_tracking_db(self) -> Dict:
        """Load file tracking database"""
        if self.tracking_db.exists():
            try:
                with open(self.tracking_db, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"tracked_files": {}, "client_mappings": {}, "last_scan": None}
    
    def _save_tracking_db(self):
        """Save file tracking database"""
        with open(self.tracking_db, 'w') as f:
            json.dump(self.tracked_files, f, indent=2, default=str)
    
    def get_client_directory(self, client_name: str) -> Path:
        """Get or create client directory"""
        # Clean client name for filesystem
        safe_name = re.sub(r'[^\w\s-]', '', client_name).strip()
        safe_name = re.sub(r'[-\s]+', ' ', safe_name)
        
        client_dir = self.client_files_dir / safe_name
        client_dir.mkdir(exist_ok=True)
        
        # Create standard subdirectories
        (client_dir / "draft documents").mkdir(exist_ok=True)
        (client_dir / "scripts").mkdir(exist_ok=True)
        
        return client_dir
    
    def get_tracked_output_path(self, 
                               filename: str, 
                               client_name: str = None,
                               document_type: str = "estimate",
                               force_client_dir: bool = True) -> str:
        """
        Get a tracked output path for a new file
        
        Args:
            filename: Desired filename
            client_name: Client name (if known)
            document_type: Type of document (estimate, invoice, contract, etc.)
            force_client_dir: If True, always place in client directory
        
        Returns:
            Absolute path where file should be saved
        """
        # Extract client name from filename if not provided
        if not client_name:
            client_name = self._extract_client_from_filename(filename)
        
        if client_name and force_client_dir:
            client_dir = self.get_client_directory(client_name)
            output_path = client_dir / filename
        else:
            # Use temp directory with tracking
            output_path = self.temp_dir / filename
        
        # Ensure unique filename
        counter = 1
        original_path = output_path
        while output_path.exists():
            stem = original_path.stem
            suffix = original_path.suffix
            output_path = original_path.parent / f"{stem}_{counter:03d}{suffix}"
            counter += 1
        
        # Track this file
        self._track_file(str(output_path), client_name, document_type)
        
        return str(output_path)
    
    def _extract_client_from_filename(self, filename: str) -> Optional[str]:
        """Extract client name from filename patterns"""
        # Common patterns in Squirt filenames
        patterns = [
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)_',  # FirstName LastName_
            r'([A-Z][a-z]+_[A-Z][a-z]+)_',     # FirstName_LastName_
            r'(\w+\s+\w+)_Fall_Cleanup',        # Name Name_Fall_Cleanup
            r'(\w+\s+\w+)_Contract',           # Name Name_Contract
            r'(\w+\s+\w+)_Invoice',            # Name Name_Invoice
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                return match.group(1).replace('_', ' ')
        
        return None
    
    def _track_file(self, file_path: str, client_name: str = None, document_type: str = "unknown"):
        """Add file to tracking database"""
        file_id = hashlib.md5(file_path.encode()).hexdigest()[:8]
        
        self.tracked_files["tracked_files"][file_id] = {
            "path": file_path,
            "client_name": client_name,
            "document_type": document_type,
            "created": datetime.now().isoformat(),
            "last_modified": None
        }
        
        if client_name:
            if client_name not in self.tracked_files["client_mappings"]:
                self.tracked_files["client_mappings"][client_name] = []
            self.tracked_files["client_mappings"][client_name].append(file_id)
        
        self._save_tracking_db()
    
    def scan_and_organize_untracked_files(self) -> List[str]:
        """
        Scan for untracked files and organize them
        Returns list of files that were moved/organized
        """
        organized_files = []
        
        # Scan common locations for untracked files
        scan_locations = [
            self.base_dir,
            Path("/tmp"),
            Path.home() / "Desktop",
            Path.home() / "Downloads"
        ]
        
        for location in scan_locations:
            if not location.exists():
                continue
                
            # Find potential Squirt files
            for file_path in location.iterdir():
                if not file_path.is_file():
                    continue
                
                if self._is_squirt_file(file_path):
                    new_location = self._organize_file(file_path)
                    if new_location:
                        organized_files.append(f"{file_path} -> {new_location}")
        
        self.tracked_files["last_scan"] = datetime.now().isoformat()
        self._save_tracking_db()
        
        return organized_files
    
    def _is_squirt_file(self, file_path: Path) -> bool:
        """Determine if file belongs to Squirt project"""
        # Check if already tracked
        for tracked in self.tracked_files["tracked_files"].values():
            if tracked["path"] == str(file_path):
                return False  # Already tracked
        
        # Check filename patterns
        squirt_indicators = [
            "_Fall_Cleanup",
            "_Contract", 
            "_Invoice",
            "_Estimate",
            "waterwizard",
            "WaterWizard",
            "_uno_",
            "liam_smith",
            "Liam_Smith"
        ]
        
        filename = file_path.name
        return any(indicator in filename for indicator in squirt_indicators)
    
    def _organize_file(self, file_path: Path) -> Optional[str]:
        """Organize a single file into appropriate location"""
        try:
            client_name = self._extract_client_from_filename(file_path.name)
            
            if client_name:
                # Move to client directory
                client_dir = self.get_client_directory(client_name)
                new_path = client_dir / file_path.name
                
                # Handle duplicates
                counter = 1
                while new_path.exists():
                    stem = file_path.stem
                    suffix = file_path.suffix
                    new_path = client_dir / f"{stem}_imported_{counter:03d}{suffix}"
                    counter += 1
                
                shutil.move(str(file_path), str(new_path))
                self._track_file(str(new_path), client_name, "imported")
                return str(new_path)
            
            else:
                # Move to temp directory for manual review
                new_path = self.temp_dir / file_path.name
                
                counter = 1
                while new_path.exists():
                    stem = file_path.stem
                    suffix = file_path.suffix
                    new_path = self.temp_dir / f"{stem}_review_{counter:03d}{suffix}"
                    counter += 1
                
                shutil.move(str(file_path), str(new_path))
                self._track_file(str(new_path), None, "needs_review")
                return str(new_path)
                
        except Exception as e:
            print(f"Error organizing {file_path}: {e}")
            return None
    
    def get_client_files(self, client_name: str) -> List[Dict]:
        """Get all tracked files for a client"""
        files = []
        client_mapping = self.tracked_files["client_mappings"].get(client_name, [])
        
        for file_id in client_mapping:
            file_info = self.tracked_files["tracked_files"].get(file_id)
            if file_info and Path(file_info["path"]).exists():
                files.append(file_info)
        
        return files
    
    def cleanup_temp_files(self, older_than_days: int = 7) -> List[str]:
        """Clean up old temporary files"""
        removed_files = []
        cutoff_date = datetime.now().timestamp() - (older_than_days * 24 * 60 * 60)
        
        for file_path in self.temp_dir.iterdir():
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_date:
                try:
                    file_path.unlink()
                    removed_files.append(str(file_path))
                except Exception as e:
                    print(f"Error removing {file_path}: {e}")
        
        return removed_files
    
    def create_safe_backup(self, file_path: str) -> Optional[str]:
        """Create a backup of an important file"""
        source_path = Path(file_path)
        if not source_path.exists():
            return None
        
        backup_dir = self.base_dir / "file_backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{source_path.stem}_{timestamp}{source_path.suffix}"
        backup_path = backup_dir / backup_name
        
        try:
            shutil.copy2(str(source_path), str(backup_path))
            return str(backup_path)
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None

# Global instance for easy access
file_tracker = FileTrackingSystem()

def get_tracked_path(filename: str, client_name: str = None, document_type: str = "estimate") -> str:
    """Convenient function to get a tracked output path"""
    return file_tracker.get_tracked_output_path(filename, client_name, document_type)

def scan_and_organize() -> List[str]:
    """Convenient function to scan and organize untracked files"""
    return file_tracker.scan_and_organize_untracked_files()

if __name__ == "__main__":
    # Run self-scan when executed directly
    tracker = FileTrackingSystem()
    organized = tracker.scan_and_organize_untracked_files()
    
    if organized:
        print("Organized the following files:")
        for file_move in organized:
            print(f"  {file_move}")
    else:
        print("No untracked files found to organize")