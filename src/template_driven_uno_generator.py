#!/usr/bin/env python3
"""
Template-Driven UNO Estimate Generator for Squirt 1.2
Processes JSON templates to generate dynamic estimates
"""

import uno
from com.sun.star.beans import PropertyValue
from com.sun.star.text.ControlCharacter import PARAGRAPH_BREAK, LINE_BREAK
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import argparse
import sys
import os
import subprocess
import time
from pathlib import Path

class TemplateProcessor:
    """Processes template JSON files and input data"""
    
    def __init__(self):
        self.template_data = None
        self.input_data = None
    
    def load_template(self, template_path: str):
        """Load and parse template JSON file"""
        try:
            with open(template_path, 'r') as f:
                self.template_data = json.load(f)
            print(f"✅ Loaded template: {self.template_data.get('template_id', 'Unknown')}")
            return True
        except Exception as e:
            print(f"❌ Failed to load template {template_path}: {str(e)}")
            return False
    
    def load_input_data(self, input_path: str):
        """Load client/project input data"""
        try:
            with open(input_path, 'r') as f:
                self.input_data = json.load(f)
            print(f"✅ Loaded input data for: {self.input_data.get('client_name', 'Unknown Client')}")
            return True
        except Exception as e:
            print(f"❌ Failed to load input data {input_path}: {str(e)}")
            return False
    
    def calculate_material_costs(self, parameters: Dict) -> List[Dict]:
        """Calculate material costs based on template and parameters"""
        materials = []
        
        if 'materials' not in self.template_data:
            return materials
            
        for material in self.template_data['materials']:
            try:
                # Get quantity from formula or default
                qty_formula = material.get('qty_formula', '1')
                default_qty = material.get('default_qty', 1)
                
                # Simple formula evaluation (expand this for complex formulas)
                if qty_formula.isdigit():
                    quantity = int(qty_formula)
                else:
                    # Use default for now - would need expression evaluator for complex formulas
                    quantity = default_qty
                
                unit_cost = Decimal(str(material.get('unit_cost', 0)))
                markup = Decimal(str(material.get('markup', 0)))
                
                # Calculate marked up unit cost
                marked_up_cost = unit_cost * (1 + markup)
                subtotal = marked_up_cost * quantity
                
                materials.append({
                    'description': material.get('description', 'Material'),
                    'qty': quantity,
                    'unit': material.get('unit', 'each'),
                    'unit_cost': float(marked_up_cost),
                    'subtotal': float(subtotal)
                })
                
            except Exception as e:
                print(f"⚠️  Error calculating material {material.get('description', 'Unknown')}: {e}")
                continue
        
        return materials
    
    def calculate_labor_costs(self, parameters: Dict) -> List[Dict]:
        """Calculate labor costs based on template and parameters"""
        labor_items = []
        
        if 'labor' not in self.template_data:
            return labor_items
            
        # Default labor rates by skill level
        labor_rates = {
            'maintenance': 45.00,
            'install': 65.00,
            'pruning': 75.00,
            'electrical': 85.00,
            'irrigation_tech': 75.00,
            'certified_applicator': 70.00,
            'carpenter': 80.00,
            'arborist': 95.00,
            'equipment_operator': 70.00,
            'design': 85.00,
            'concrete': 70.00,
            'customer_service': 50.00
        }
        
        for labor in self.template_data['labor']:
            try:
                # Get hours from formula or default
                hrs_formula = labor.get('hrs_formula', '1')
                default_hrs = labor.get('default_hrs', 1)
                
                # Simple evaluation - use default for now
                if hrs_formula.replace('.', '').isdigit():
                    hours = float(hrs_formula)
                else:
                    hours = default_hrs
                
                skill_level = labor.get('skill_level', 'maintenance')
                hourly_rate = labor_rates.get(skill_level, 50.00)
                crew_size = labor.get('crew_size', 1)
                
                subtotal = hours * hourly_rate * crew_size
                
                labor_items.append({
                    'task': labor.get('description', 'Labor task'),
                    'hours': hours,
                    'crew_size': crew_size,
                    'rate': hourly_rate,
                    'subtotal': subtotal
                })
                
            except Exception as e:
                print(f"⚠️  Error calculating labor {labor.get('description', 'Unknown')}: {e}")
                continue
        
        return labor_items
    
    def generate_estimate_data(self) -> Dict:
        """Generate complete estimate data from template and inputs"""
        if not self.template_data or not self.input_data:
            raise ValueError("Template or input data not loaded")
        
        # Use default parameters for now - would need parameter processing for dynamic values
        parameters = self.template_data.get('parameters', {})
        
        # Calculate costs
        materials = self.calculate_material_costs(parameters)
        labor = self.calculate_labor_costs(parameters)
        
        # Calculate totals
        materials_total = sum(item['subtotal'] for item in materials)
        labor_total = sum(item['subtotal'] for item in labor)
        subtotal = materials_total + labor_total
        
        # No sales tax in Oregon
        tax_rate = 0.00
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount
        
        return {
            'client_info': {
                'name': self.input_data.get('client_name', 'Client'),
                'address': self.input_data.get('property_address', ''),
                'phone': self.input_data.get('contact_info', {}).get('phone', ''),
                'email': self.input_data.get('contact_info', {}).get('email', '')
            },
            'project_info': {
                'name': self.template_data.get('title_format', 'Project').format(**{k: v.get('default', '') for k, v in parameters.items()}),
                'description': self.template_data.get('description', ''),
                'date': self.input_data.get('estimate_date', datetime.now().strftime('%Y-%m-%d'))
            },
            'scope_areas': [{
                'title': f"{self.template_data.get('title_format', 'Service').format(**{k: v.get('default', '') for k, v in parameters.items()})} — ${total:.2f}",
                'description': self.template_data.get('description', ''),
                'materials': [{'qty': m['qty'], 'price': m['unit_cost'], 'description': m['description'], 'subtotal': m['subtotal']} for m in materials],
                'labor': [{'task': l['task'], 'subtotal': l['subtotal']} for l in labor],
                'total': total
            }],
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'total': total
        }

class TemplateDrivenUnoGenerator:
    """UNO-based estimate generator that uses JSON templates"""
    
    def __init__(self):
        self.context = None
        self.desktop = None
        self.document = None
        self.uno_port = 2002
        self.processor = TemplateProcessor()
        
    def _connect_to_libreoffice(self):
        """Connect to LibreOffice UNO"""
        try:
            # Start headless LibreOffice
            subprocess.run([
                'soffice', '--headless', '--accept=socket,host=localhost,port=2002;urp;'
            ], check=False)
            time.sleep(3)
            
            # Connect
            local_context = uno.getComponentContext()
            resolver = local_context.ServiceManager.createInstanceWithContext(
                "com.sun.star.bridge.UnoUrlResolver", local_context
            )
            
            self.context = resolver.resolve(
                f"uno:socket,host=localhost,port={self.uno_port};urp;StarOffice.ComponentContext"
            )
            self.desktop = self.context.ServiceManager.createInstanceWithContext(
                "com.sun.star.frame.Desktop", self.context
            )
            print("✅ Connected to LibreOffice UNO")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to LibreOffice: {e}")
            return False
    
    def generate_from_template(self, template_path: str, input_path: str, output_path: str = None) -> bool:
        """Generate estimate from template and input files"""
        try:
            print(f"🔄 Processing template: {Path(template_path).name}")
            
            # Load template and input data
            if not self.processor.load_template(template_path):
                return False
            if not self.processor.load_input_data(input_path):
                return False
            
            # Connect to LibreOffice
            if not self._connect_to_libreoffice():
                return False
            
            # Generate estimate data
            estimate_data = self.processor.generate_estimate_data()
            
            # Create document (simplified for now)
            self.document = self.desktop.loadComponentFromURL(
                "private:factory/swriter", "_blank", 0, ()
            )
            
            # Add basic content
            text = self.document.Text
            cursor = text.createTextCursor()
            
            # Title
            cursor.setString(f"WaterWizard Irrigation & Landscape\n")
            cursor.goToEnd(False)
            cursor.setString(f"\nESTIMATE\n\n")
            cursor.goToEnd(False)
            
            # Client info
            cursor.setString(f"Client: {estimate_data['client_info']['name']}\n")
            cursor.goToEnd(False)
            cursor.setString(f"Address: {estimate_data['client_info']['address']}\n")
            cursor.goToEnd(False)
            cursor.setString(f"Date: {estimate_data['project_info']['date']}\n\n")
            cursor.goToEnd(False)
            
            # Project
            cursor.setString(f"Project: {estimate_data['project_info']['name']}\n")
            cursor.goToEnd(False)
            cursor.setString(f"Description: {estimate_data['project_info']['description']}\n\n")
            cursor.goToEnd(False)
            
            # Scope areas
            for scope in estimate_data['scope_areas']:
                cursor.setString(f"{scope['title']}\n")
                cursor.goToEnd(False)
                cursor.setString(f"{scope['description']}\n\n")
                cursor.goToEnd(False)
                
                # Materials
                if scope['materials']:
                    cursor.setString("Materials:\n")
                    cursor.goToEnd(False)
                    for material in scope['materials']:
                        cursor.setString(f"  {material['qty']}x {material['description']} - ${material['subtotal']:.2f}\n")
                        cursor.goToEnd(False)
                    cursor.setString("\n")
                    cursor.goToEnd(False)
                
                # Labor
                if scope['labor']:
                    cursor.setString("Labor:\n")
                    cursor.goToEnd(False)
                    for labor in scope['labor']:
                        cursor.setString(f"  {labor['task']} - ${labor['subtotal']:.2f}\n")
                        cursor.goToEnd(False)
                    cursor.setString("\n")
                    cursor.goToEnd(False)
            
            # Totals
            cursor.setString(f"\nSubtotal: ${estimate_data['subtotal']:.2f}\n")
            cursor.goToEnd(False)
            cursor.setString(f"Tax: ${estimate_data['tax_amount']:.2f}\n")
            cursor.goToEnd(False)
            cursor.setString(f"TOTAL: ${estimate_data['total']:.2f}\n")
            cursor.goToEnd(False)
            
            # Save document
            if not output_path:
                template_name = Path(template_path).stem
                output_path = f"/tmp/{template_name}_estimate.odt"
            
            # Convert to file URL
            if not output_path.startswith('file://'):
                output_path = Path(output_path).absolute().as_uri()
            
            self.document.storeAsURL(output_path, ())
            
            # Convert back to path for display
            if output_path.startswith('file://'):
                display_path = Path(output_path[7:]).as_posix()
            else:
                display_path = output_path
                
            print(f"✅ Generated estimate: {display_path}")
            print(f"   Template: {self.processor.template_data.get('template_id', 'Unknown')}")
            print(f"   Total: ${estimate_data['total']:.2f}")
            
            # Close document
            self.document.close(True)
            
            return True
            
        except Exception as e:
            print(f"❌ Error generating estimate: {e}")
            if self.document:
                self.document.close(True)
            return False

def main():
    """Main entry point for template-driven generator"""
    parser = argparse.ArgumentParser(description='Generate estimates from JSON templates')
    parser.add_argument('template_path', help='Path to template JSON file')
    parser.add_argument('input_path', help='Path to input data JSON file')
    parser.add_argument('--output', '-o', help='Output ODT file path')
    
    args = parser.parse_args()
    
    print("📊 TEMPLATE-DRIVEN UNO ESTIMATE GENERATOR - SQUIRT 1.2")
    print("=" * 60)
    
    generator = TemplateDrivenUnoGenerator()
    success = generator.generate_from_template(args.template_path, args.input_path, args.output)
    
    if success:
        print("🎯 Estimate generation completed successfully!")
        sys.exit(0)
    else:
        print("❌ Estimate generation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()