#!/usr/bin/env python3
"""
Modern HTML>ODT Document Generator
Replacement for legacy generators using the fixed HTML>ODT pipeline
"""

import json
from pathlib import Path
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Any, Optional

try:
    from .html_to_odt_generator import HtmlToOdtGenerator
except ImportError:
    from html_to_odt_generator import HtmlToOdtGenerator
try:
    from .template_processor import TemplateProcessor
    from .tax_rules import TaxRulesEngine
except ImportError:
    # Fallback for direct script execution
    print("⚠️  Template processor not available - using simplified processing")
    TemplateProcessor = None
    TaxRulesEngine = None

class ModernHtmlDocumentGenerator:
    """
    Modern document generator using the fixed HTML>ODT pipeline.
    Replaces legacy ASCII art and manual XML generators.
    """
    
    def __init__(self):
        self.html_generator = HtmlToOdtGenerator()
        self.processor = TemplateProcessor() if TemplateProcessor else None
        self.tax_engine = TaxRulesEngine() if TaxRulesEngine else None
    
    def generate_contract(self, client_info: dict, project_info: dict, 
                         templates_with_params: list, output_path: str) -> bool:
        """Generate a professional contract using HTML>ODT pipeline"""
        
        try:
            # Create a synthetic template based on the project data
            synthetic_template = self._create_synthetic_template(
                templates_with_params, project_type="contract"
            )
            
            # Create synthetic input data
            synthetic_input = self._create_synthetic_input(client_info, project_info)
            
            # Use the fixed HTML>ODT generator
            return self.html_generator.generate_estimate(
                synthetic_template, synthetic_input, output_path
            )
            
        except Exception as e:
            print(f"❌ Contract generation failed: {e}")
            return False
    
    def generate_invoice(self, client_info: dict, project_info: dict,
                        templates_with_params: list, output_path: str) -> bool:
        """Generate a professional invoice using HTML>ODT pipeline"""
        
        try:
            # Create a synthetic template based on the project data
            synthetic_template = self._create_synthetic_template(
                templates_with_params, project_type="invoice"
            )
            
            # Create synthetic input data
            synthetic_input = self._create_synthetic_input(client_info, project_info)
            
            # Use the fixed HTML>ODT generator
            return self.html_generator.generate_estimate(
                synthetic_template, synthetic_input, output_path
            )
            
        except Exception as e:
            print(f"❌ Invoice generation failed: {e}")
            return False
    
    def _create_synthetic_template(self, templates_with_params: list, 
                                  project_type: str = "contract") -> str:
        """Create a synthetic template JSON from legacy template data"""
        
        # Process all templates to extract materials, labor, equipment
        all_materials = []
        all_labor = []
        all_equipment = []
        
        template_id = f"synthetic_{project_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Extract data from template processing
        total_cost = Decimal("0")
        for template_path, params in templates_with_params:
            try:
                processed = self.processor.process_template(template_path, params)
                
                # Add materials
                for material in processed.get('materials', []):
                    all_materials.append({
                        "code": material.get('code', f"MAT_{len(all_materials):03d}"),
                        "description": material.get('description', 'Material'),
                        "unit": material.get('unit', 'each'),
                        "qty_formula": str(material.get('quantity', 1)),
                        "default_qty": float(material.get('quantity', 1)),
                        "unit_cost": float(material.get('unit_cost', 0)),
                        "markup": 0.25
                    })
                
                # Add labor
                for labor in processed.get('labor', []):
                    all_labor.append({
                        "task_code": labor.get('code', f"LAB_{len(all_labor):03d}"),
                        "description": labor.get('description', 'Labor Task'),
                        "hrs_formula": str(labor.get('hours', 1)),
                        "default_hrs": float(labor.get('hours', 1)),
                        "skill_level": labor.get('skill_level', 'install'),
                        "crew_size": int(labor.get('crew_size', 1))
                    })
                
                # Add equipment
                for equipment in processed.get('equipment', []):
                    all_equipment.append({
                        "equipment_code": equipment.get('code', f"EQ_{len(all_equipment):03d}"),
                        "description": equipment.get('description', 'Equipment'),
                        "usage_formula": str(equipment.get('usage', 1)),
                        "usage_unit": equipment.get('usage_unit', 'day'),
                        "daily_rate": float(equipment.get('daily_rate', 0))
                    })
                    
                total_cost += Decimal(str(processed.get('subtotal', 0)))
                
            except Exception as e:
                print(f"⚠️  Warning: Could not process template {template_path}: {e}")
        
        # Create synthetic template structure
        synthetic_template = {
            "template_id": template_id,
            "category": "professional_services",
            "subcategory": project_type,
            "title_format": f"Professional {project_type.title()} Services",
            "description": f"Comprehensive {project_type} for professional services",
            "assumptions": [
                "Professional installation and materials",
                "Standard business conditions apply",
                "Permits and approvals as required"
            ],
            "materials": all_materials,
            "labor": all_labor,
            "equipment": all_equipment,
            "validation_expectations": {
                "required_sections": ["Materials & Equipment", "Labor & Installation"],
                "required_fields": [],
                "math_checks": []
            }
        }
        
        # Write to temporary file
        temp_template_path = Path(f"/tmp/{template_id}.json")
        with open(temp_template_path, 'w') as f:
            json.dump(synthetic_template, f, indent=2)
        
        return str(temp_template_path)
    
    def _create_synthetic_input(self, client_info: dict, project_info: dict) -> str:
        """Create synthetic input JSON from client and project data"""
        
        synthetic_input = {
            "client_name": client_info.get('name', 'Valued Client'),
            "property_address": client_info.get('address', 'Property Address'),
            "estimate_date": datetime.now().strftime('%Y-%m-%d'),
            "project_description": project_info.get('description', 'Professional Services'),
            "contact_info": {
                "phone": client_info.get('phone', ''),
                "email": client_info.get('email', '')
            },
            "company_info": {
                "name": "WaterWizard Irrigation & Landscape",
                "license": "Licensed & Insured",
                "phone": "(555) 123-4567", 
                "email": "info@waterwizard.com"
            }
        }
        
        # Write to temporary file
        temp_input_path = Path(f"/tmp/synthetic_input_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(temp_input_path, 'w') as f:
            json.dump(synthetic_input, f, indent=2)
        
        return str(temp_input_path)

def main():
    """Test the modern HTML document generator"""
    
    # Sample test data
    client_info = {
        'name': 'John Doe',
        'address': '123 Test Street',
        'city': 'Portland',
        'state': 'OR',
        'zip': '97205',
        'phone': '(503) 555-0123',
        'email': 'john@example.com'
    }
    
    project_info = {
        'name': 'Test Project',
        'description': 'Modern document generator test'
    }
    
    templates_with_params = [
        ('test_template.json', {'param1': 'value1'})
    ]
    
    generator = ModernHtmlDocumentGenerator()
    
    # Test contract generation
    contract_path = "test_outputs/modern_test_contract.odt"
    success = generator.generate_contract(
        client_info, project_info, templates_with_params, contract_path
    )
    
    if success:
        print(f"✅ Modern contract generated: {contract_path}")
    else:
        print("❌ Modern contract generation failed")

if __name__ == "__main__":
    main()