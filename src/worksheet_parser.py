#!/usr/bin/env python3
"""
WaterWizard Worksheet Parser
Reads CSV/ODS files with project data and returns structured information
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from decimal import Decimal

class WorksheetParser:
    def __init__(self):
        """Initialize the worksheet parser"""
        self.supported_formats = ['.csv', '.ods']
        
    def parse_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse CSV file and return list of project records"""
        projects = []
        
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                # Detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 for header
                    try:
                        # Clean and validate row data
                        cleaned_row = self._clean_row_data(row)
                        if cleaned_row:
                            cleaned_row['_source_row'] = row_num
                            projects.append(cleaned_row)
                    except Exception as e:
                        print(f"Warning: Error parsing row {row_num}: {e}")
                        continue
                        
        except FileNotFoundError:
            raise FileNotFoundError(f"Worksheet file not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error parsing CSV file: {e}")
            
        return projects
    
    def parse_ods(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse ODS file (LibreOffice Calc format)"""
        # For now, suggest saving as CSV from LibreOffice
        # In future sprints, we could add python-odf support
        raise NotImplementedError(
            "ODS parsing not yet implemented. "
            "Please save your LibreOffice Calc file as CSV format for now."
        )
    
    def _clean_row_data(self, row: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Clean and type-convert row data"""
        if not row or all(not str(v).strip() for v in row.values()):
            return None  # Skip empty rows
            
        cleaned = {}
        
        for key, value in row.items():
            if key is None:
                continue
                
            # Clean key name
            clean_key = str(key).strip().lower().replace(' ', '_').replace('-', '_')
            
            # Clean value
            clean_value = str(value).strip() if value is not None else ""
            
            if not clean_value:
                cleaned[clean_key] = None
                continue
                
            # Type conversion based on common field patterns
            if clean_key in ['zone_count', 'head_count', 'valve_count', 'zone_number']:
                try:
                    cleaned[clean_key] = int(clean_value)
                except ValueError:
                    cleaned[clean_key] = clean_value
                    
            elif clean_key in ['trench_feet', 'wiring_feet', 'tax_rate']:
                try:
                    cleaned[clean_key] = float(clean_value)
                except ValueError:
                    cleaned[clean_key] = clean_value
                    
            elif clean_key in ['manifold', 'swing_joint_needed', 'pipe_repair']:
                # Boolean fields
                clean_value_lower = clean_value.lower()
                if clean_value_lower in ['true', 'yes', '1', 'y', 'on']:
                    cleaned[clean_key] = True
                elif clean_value_lower in ['false', 'no', '0', 'n', 'off']:
                    cleaned[clean_key] = False
                else:
                    cleaned[clean_key] = clean_value
                    
            else:
                # String fields - remove quotes if present
                if clean_value.startswith('"') and clean_value.endswith('"'):
                    clean_value = clean_value[1:-1]
                elif clean_value.startswith("'") and clean_value.endswith("'"):
                    clean_value = clean_value[1:-1]
                cleaned[clean_key] = clean_value
                
        return cleaned
    
    def validate_required_fields(self, project: Dict[str, Any], template_type: str) -> List[str]:
        """Validate that required fields are present for a template type"""
        errors = []
        
        # Define required fields by template type
        required_fields = {
            'sprinkler_zone': ['zone_number', 'head_count', 'trench_feet', 'soil_type'],
            'trenching': ['trench_feet', 'soil_type'],
            'valve_install': ['valve_count'],
            'head_replacement': ['head_count']
        }
        
        if template_type not in required_fields:
            errors.append(f"Unknown template type: {template_type}")
            return errors
            
        for field in required_fields[template_type]:
            if field not in project or project[field] is None:
                errors.append(f"Missing required field: {field}")
            elif field in ['zone_number', 'head_count', 'valve_count'] and project[field] <= 0:
                errors.append(f"Field {field} must be greater than 0")
            elif field == 'soil_type' and project[field] not in ['turf', 'rocky', 'clay', 'roots']:
                errors.append(f"Invalid soil_type: {project[field]}. Must be one of: turf, rocky, clay, roots")
                
        return errors
    
    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse worksheet file based on extension"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        suffix = path.suffix.lower()
        
        if suffix == '.csv':
            return self.parse_csv(file_path)
        elif suffix == '.ods':
            return self.parse_ods(file_path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}. Supported: {self.supported_formats}")
    
    def get_project_summary(self, projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics from parsed projects"""
        if not projects:
            return {"total_projects": 0, "errors": ["No projects found"]}
            
        summary = {
            "total_projects": len(projects),
            "template_types": {},
            "clients": set(),
            "total_value_estimate": 0,
            "errors": []
        }
        
        for project in projects:
            # Count template types
            template_type = project.get('template_type', 'unknown')
            summary["template_types"][template_type] = summary["template_types"].get(template_type, 0) + 1
            
            # Collect unique clients
            if project.get('client_name'):
                summary["clients"].add(project['client_name'])
        
        summary["unique_clients"] = len(summary["clients"])
        summary["clients"] = list(summary["clients"])  # Convert set to list for JSON serialization
        
        return summary

def main():
    """Demo the worksheet parser"""
    parser = WorksheetParser()
    
    # Create a sample CSV for testing
    sample_csv = """client_name,template_type,zone_number,head_count,trench_feet,soil_type,project_name
"Smith Family",sprinkler_zone,1,6,120,clay,"Backyard Zone 1"
"Johnson Home",sprinkler_zone,2,8,150,turf,"Front Yard Zone 2"  
"Rodriguez Trust",head_replacement,,,5,,,"Repair Broken Heads"
"Green Acres HOA",trenching,,,200,rocky,"Main Line Extension"
"""
    
    # Save sample CSV
    with open('sample_projects.csv', 'w') as f:
        f.write(sample_csv)
    
    print("📊 WATERWIZARD WORKSHEET PARSER")
    print("=" * 40)
    
    try:
        # Parse the sample file
        projects = parser.parse_file('sample_projects.csv')
        
        print(f"✅ Parsed {len(projects)} projects from CSV")
        print("\n📋 PROJECT DETAILS:")
        
        for i, project in enumerate(projects, 1):
            print(f"\n{i}. {project.get('client_name', 'Unknown Client')}")
            print(f"   Template: {project.get('template_type', 'Not specified')}")
            print(f"   Data: {dict(project)}")
            
            # Validate if template type is specified
            template_type = project.get('template_type')
            if template_type and template_type != 'unknown':
                errors = parser.validate_required_fields(project, template_type)
                if errors:
                    print(f"   ⚠️  Validation errors: {errors}")
                else:
                    print(f"   ✅ Validation: Passed")
        
        # Generate summary
        summary = parser.get_project_summary(projects)
        print(f"\n📈 SUMMARY:")
        print(f"   Total projects: {summary['total_projects']}")
        print(f"   Unique clients: {summary['unique_clients']}")
        print(f"   Template types: {summary['template_types']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()