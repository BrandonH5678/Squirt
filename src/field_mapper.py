#!/usr/bin/env python3
"""
WaterWizard Field Mapper
Maps worksheet fields to template parameters and generates template inputs
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

class FieldMapper:
    def __init__(self, template_dir: str = "src/templates"):
        """Initialize field mapper with template directory"""
        self.template_dir = template_dir
        self.mapping_rules = self._load_default_mapping_rules()
        
    def _load_default_mapping_rules(self) -> Dict[str, Dict[str, Any]]:
        """Define default field mapping rules for each template type"""
        return {
            "sprinkler_zone": {
                "required_fields": ["zone_number", "head_count", "trench_feet", "soil_type"],
                "optional_fields": ["pipe_size"],
                "field_mappings": {
                    # Direct mappings (worksheet field -> template parameter)
                    "zone_number": "zone_number",
                    "head_count": "head_count", 
                    "trench_feet": "trench_feet",
                    "soil_type": "soil_type",
                    "pipe_size": "pipe_size"
                },
                "default_values": {
                    "pipe_size": "1inch"
                },
                "validation_rules": {
                    "zone_number": {"type": "int", "min": 1, "max": 50},
                    "head_count": {"type": "int", "min": 1, "max": 20},
                    "trench_feet": {"type": "float", "min": 10, "max": 1000},
                    "soil_type": {"type": "string", "options": ["turf", "rocky", "clay", "roots"]}
                }
            },
            
            "trenching": {
                "required_fields": ["trench_feet", "soil_type"],
                "optional_fields": ["depth", "width"],
                "field_mappings": {
                    "trench_feet": "trench_feet",
                    "soil_type": "soil_type",
                    "trench_depth": "depth",
                    "trench_width": "width"
                },
                "default_values": {
                    "depth": "standard",
                    "width": "single"
                },
                "validation_rules": {
                    "trench_feet": {"type": "float", "min": 1, "max": 2000},
                    "soil_type": {"type": "string", "options": ["turf", "rocky", "clay", "roots"]}
                }
            },
            
            "valve_install": {
                "required_fields": ["valve_count"],
                "optional_fields": ["valve_size", "manifold", "wiring_feet"],
                "field_mappings": {
                    "valve_count": "valve_count",
                    "valve_size": "valve_size", 
                    "manifold": "manifold",
                    "wiring_feet": "wiring_feet"
                },
                "default_values": {
                    "valve_size": "1inch",
                    "manifold": False,
                    "wiring_feet": 50
                },
                "validation_rules": {
                    "valve_count": {"type": "int", "min": 1, "max": 10},
                    "manifold": {"type": "bool"}
                }
            },
            
            "head_replacement": {
                "required_fields": ["head_count"],
                "optional_fields": ["head_type", "swing_joint_needed", "pipe_repair"],
                "field_mappings": {
                    "head_count": "head_count",
                    "head_type": "head_type",
                    "swing_joint_needed": "swing_joint_needed",
                    "pipe_repair": "pipe_repair"
                },
                "default_values": {
                    "head_type": "spray",
                    "swing_joint_needed": False,
                    "pipe_repair": False
                },
                "validation_rules": {
                    "head_count": {"type": "int", "min": 1, "max": 50}
                }
            }
        }
    
    def map_project_to_template_params(self, project: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[str]]:
        """
        Map a project record to template parameters
        Returns: (template_path, parameters, errors)
        """
        template_type = project.get('template_type')
        if not template_type:
            return None, {}, ["Missing template_type field"]
            
        if template_type not in self.mapping_rules:
            return None, {}, [f"Unknown template_type: {template_type}"]
        
        rules = self.mapping_rules[template_type]
        parameters = {}
        errors = []
        
        # Map required fields
        for field in rules["required_fields"]:
            worksheet_value = project.get(field)
            if worksheet_value is None or worksheet_value == "":
                errors.append(f"Missing required field: {field}")
                continue
                
            # Apply field mapping (if different name in template)
            template_param = rules["field_mappings"].get(field, field)
            parameters[template_param] = worksheet_value
        
        # Map optional fields
        for field in rules.get("optional_fields", []):
            worksheet_value = project.get(field)
            template_param = rules["field_mappings"].get(field, field)
            
            if worksheet_value is not None and worksheet_value != "":
                parameters[template_param] = worksheet_value
            elif template_param in rules.get("default_values", {}):
                # Apply default value if field is missing
                parameters[template_param] = rules["default_values"][template_param]
        
        # Validate parameters
        validation_errors = self._validate_parameters(parameters, rules.get("validation_rules", {}))
        errors.extend(validation_errors)
        
        # Construct template path
        template_path = f"{self.template_dir}/{template_type}.json"
        
        return template_path, parameters, errors
    
    def _validate_parameters(self, parameters: Dict[str, Any], rules: Dict[str, Dict[str, Any]]) -> List[str]:
        """Validate parameters against validation rules"""
        errors = []
        
        for param_name, param_value in parameters.items():
            if param_name not in rules:
                continue
                
            rule = rules[param_name]
            param_type = rule.get("type", "string")
            
            # Type validation
            if param_type == "int" and not isinstance(param_value, int):
                try:
                    param_value = int(param_value)
                    parameters[param_name] = param_value  # Update with converted value
                except (ValueError, TypeError):
                    errors.append(f"Parameter {param_name} must be an integer")
                    continue
                    
            elif param_type == "float" and not isinstance(param_value, (int, float)):
                try:
                    param_value = float(param_value)
                    parameters[param_name] = param_value  # Update with converted value
                except (ValueError, TypeError):
                    errors.append(f"Parameter {param_name} must be a number")
                    continue
                    
            elif param_type == "bool" and not isinstance(param_value, bool):
                errors.append(f"Parameter {param_name} must be true/false")
                continue
            
            # Range validation
            if "min" in rule and param_value < rule["min"]:
                errors.append(f"Parameter {param_name} must be >= {rule['min']}")
            if "max" in rule and param_value > rule["max"]:
                errors.append(f"Parameter {param_name} must be <= {rule['max']}")
                
            # Options validation
            if "options" in rule and param_value not in rule["options"]:
                errors.append(f"Parameter {param_name} must be one of: {rule['options']}")
        
        return errors
    
    def map_batch_projects(self, projects: List[Dict[str, Any]]) -> List[Tuple[str, Dict[str, Any], Dict[str, Any], List[str]]]:
        """
        Map multiple projects to template parameters
        Returns: List of (template_path, parameters, original_project, errors)
        """
        results = []
        
        for project in projects:
            template_path, parameters, errors = self.map_project_to_template_params(project)
            results.append((template_path, parameters, project, errors))
            
        return results
    
    def generate_mapping_report(self, mapping_results: List[Tuple]) -> Dict[str, Any]:
        """Generate a report of mapping results"""
        total_projects = len(mapping_results)
        successful_mappings = sum(1 for _, _, _, errors in mapping_results if not errors)
        failed_mappings = total_projects - successful_mappings
        
        template_counts = {}
        all_errors = []
        
        for template_path, parameters, project, errors in mapping_results:
            if template_path:
                template_name = Path(template_path).stem
                template_counts[template_name] = template_counts.get(template_name, 0) + 1
            
            if errors:
                project_id = project.get('client_name', f"Row {project.get('_source_row', 'unknown')}")
                all_errors.extend([f"{project_id}: {error}" for error in errors])
        
        return {
            "total_projects": total_projects,
            "successful_mappings": successful_mappings, 
            "failed_mappings": failed_mappings,
            "success_rate": f"{(successful_mappings/total_projects*100):.1f}%" if total_projects > 0 else "0%",
            "template_usage": template_counts,
            "errors": all_errors
        }

def main():
    """Demo the field mapper"""
    from worksheet_parser import WorksheetParser
    
    # Use the sample CSV created by the worksheet parser
    parser = WorksheetParser()
    mapper = FieldMapper()
    
    print("🗺️  WATERWIZARD FIELD MAPPER")
    print("=" * 40)
    
    try:
        # Parse projects from the sample CSV
        projects = parser.parse_file('sample_projects.csv')
        print(f"📊 Loaded {len(projects)} projects from worksheet")
        
        # Map projects to template parameters
        mapping_results = mapper.map_batch_projects(projects)
        
        print("\n📋 MAPPING RESULTS:")
        for i, (template_path, parameters, project, errors) in enumerate(mapping_results, 1):
            client = project.get('client_name', 'Unknown')
            template_type = project.get('template_type', 'Unknown')
            
            print(f"\n{i}. {client} - {template_type}")
            
            if errors:
                print(f"   ❌ Mapping failed:")
                for error in errors:
                    print(f"      • {error}")
            else:
                print(f"   ✅ Mapped to: {Path(template_path).name}")
                print(f"   📝 Parameters: {parameters}")
        
        # Generate summary report
        report = mapper.generate_mapping_report(mapping_results)
        
        print(f"\n📈 MAPPING SUMMARY:")
        print(f"   Total projects: {report['total_projects']}")
        print(f"   Successful: {report['successful_mappings']} ({report['success_rate']})")
        print(f"   Failed: {report['failed_mappings']}")
        print(f"   Template usage: {report['template_usage']}")
        
        if report['errors']:
            print(f"\n⚠️  ERRORS ({len(report['errors'])}):")
            for error in report['errors'][:5]:  # Show first 5 errors
                print(f"   • {error}")
            if len(report['errors']) > 5:
                print(f"   ... and {len(report['errors'])-5} more")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()