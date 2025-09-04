#!/usr/bin/env python3
"""
Squirt File Organizer
Manages client-facing and company-facing file organization for WaterWizard
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class SquirtFileOrganizer:
    def __init__(self, base_path: str = "/home/johnny5/Squirt"):
        self.base_path = Path(base_path)
        self.client_files_path = self.base_path / "Client Files"
        self.company_files_path = self.base_path / "Company Files"
        self.templates_path = self.base_path / "src" / "templates"
        
        # Ensure directories exist
        self._create_directory_structure()
    
    def _create_directory_structure(self):
        """Create the organized directory structure"""
        
        # Client Files - Human readable documents
        self.client_files_path.mkdir(exist_ok=True)
        
        # Company Files - Internal system files
        self.company_files_path.mkdir(exist_ok=True)
        (self.company_files_path / "Accounting CSVs").mkdir(exist_ok=True)
        (self.company_files_path / "System Logs").mkdir(exist_ok=True)
        (self.company_files_path / "Templates").mkdir(exist_ok=True)
        (self.company_files_path / "Worksheets").mkdir(exist_ok=True)
    
    def organize_client_documents(self, client_name: str, project_name: str, 
                                document_files: List[str], copy_files: bool = True) -> str:
        """
        Organize client documents into proper folder structure
        ALL CLIENT DOCUMENTS MUST BE STORED IN THE CLIENT'S INDIVIDUAL FOLDER
        This is the primary rule for client file organization.
        
        Args:
            client_name: Name of the client
            project_name: Name of the project
            document_files: List of file paths to organize
            copy_files: If True, copy files; if False, move files to client folder
            
        Returns:
            Path to organized client folder
        """
        
        # Create client-specific folder - ALL CLIENT DOCUMENTS GO HERE
        client_folder = self.client_files_path / self._sanitize_name(client_name)
        client_folder.mkdir(exist_ok=True)
        
        # IMPORTANT: All documents for a client go directly in their folder
        # No subfolders - makes it easy for humans to find everything for a client
        target_folder = client_folder
        
        # Move/copy files to client folder
        organized_files = []
        for file_path in document_files:
            source_path = Path(file_path)
            if source_path.exists():
                target_path = target_folder / source_path.name
                
                if copy_files:
                    # Copy the file (preserve original for system use)
                    shutil.copy2(source_path, target_path)
                else:
                    # Move the file to client folder
                    shutil.move(str(source_path), str(target_path))
                    
                organized_files.append(str(target_path))
        
        return str(target_folder)
    
    def organize_company_files(self, file_type: str, files: List[str]) -> str:
        """
        Organize company internal files
        
        Args:
            file_type: Type of file (accounting, logs, templates, worksheets)
            files: List of file paths to organize
            
        Returns:
            Path to organized folder
        """
        
        folder_map = {
            'accounting': self.company_files_path / "Accounting CSVs",
            'logs': self.company_files_path / "System Logs", 
            'templates': self.company_files_path / "Templates",
            'worksheets': self.company_files_path / "Worksheets"
        }
        
        target_folder = folder_map.get(file_type.lower())
        if not target_folder:
            raise ValueError(f"Unknown file type: {file_type}")
        
        target_folder.mkdir(exist_ok=True)
        
        organized_files = []
        for file_path in files:
            source_path = Path(file_path)
            if source_path.exists():
                target_path = target_folder / source_path.name
                shutil.move(str(source_path), str(target_path))
                organized_files.append(str(target_path))
        
        return str(target_folder)
    
    def generate_client_index(self) -> str:
        """Generate an index of all client files for easy navigation"""
        
        index_content = [
            "# SQUIRT CLIENT FILES INDEX",
            f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            "",
            "## Active Client Projects",
            ""
        ]
        
        # Walk through client files
        for client_folder in sorted(self.client_files_path.iterdir()):
            if client_folder.is_dir():
                client_name = client_folder.name
                index_content.append(f"### {client_name}")
                
                # List projects for this client
                project_files = []
                for item in client_folder.rglob("*"):
                    if item.is_file():
                        relative_path = item.relative_to(self.client_files_path)
                        project_files.append(str(relative_path))
                
                if project_files:
                    for file_path in sorted(project_files):
                        file_type = self._get_file_type(file_path)
                        index_content.append(f"- {file_path} ({file_type})")
                else:
                    index_content.append("- No files yet")
                
                index_content.append("")
        
        # Save index file
        index_path = self.client_files_path / "CLIENT_INDEX.md"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(index_content))
        
        return str(index_path)
    
    def _sanitize_name(self, name: str) -> str:
        """Convert client/project names to safe folder names"""
        # Replace problematic characters with safe alternatives
        safe_name = name.replace('/', '-').replace('\\', '-').replace(':', '-')
        safe_name = ''.join(c for c in safe_name if c.isalnum() or c in '-_ ')
        return safe_name.strip()
    
    def _get_file_type(self, file_path: str) -> str:
        """Determine human-readable file type"""
        ext = Path(file_path).suffix.lower()
        type_map = {
            '.pdf': 'PDF Document',
            '.odt': 'LibreOffice Document', 
            '.txt': 'Text Contract',
            '.csv': 'Spreadsheet Data',
            '.ods': 'LibreOffice Spreadsheet',
            '.json': 'Data File'
        }
        return type_map.get(ext, 'Unknown File')

def main():
    """Demo the file organizer"""
    
    print("📁 SQUIRT FILE ORGANIZER")
    print("=" * 50)
    
    organizer = SquirtFileOrganizer()
    
    print("✅ Directory structure created:")
    print(f"   Client Files: {organizer.client_files_path}")
    print(f"   Company Files: {organizer.company_files_path}")
    
    # Generate client index
    index_path = organizer.generate_client_index()
    print(f"✅ Client index generated: {index_path}")
    
    print("\n🎯 FOLDER STRUCTURE:")
    print("Client Files/")
    print("├── [Client Name]/")
    print("│   ├── [Project Name]/")
    print("│   │   ├── Contract.pdf")
    print("│   │   ├── Invoice.pdf") 
    print("│   │   └── Receipt.pdf")
    print("│   └── CLIENT_INDEX.md")
    print("└── Company Files/")
    print("    ├── Accounting CSVs/")
    print("    ├── System Logs/")
    print("    ├── Templates/")
    print("    └── Worksheets/")

if __name__ == "__main__":
    main()