#!/usr/bin/env python3
"""
Simple Template-Based Document Generator
Uses LibreOffice headless conversion instead of UNO for reliability
"""

import json
import subprocess
import tempfile
import sys
from pathlib import Path
from decimal import Decimal

class SimpleTemplateGenerator:
    """Generate documents using template data and LibreOffice headless conversion"""
    
    def __init__(self):
        self.template_data = None
        self.input_data = None
    
    def load_files(self, template_path: str, input_path: str):
        """Load template and input files"""
        try:
            with open(template_path, 'r') as f:
                self.template_data = json.load(f)
            with open(input_path, 'r') as f:
                self.input_data = json.load(f)
            return True
        except Exception as e:
            print(f"❌ Error loading files: {e}")
            return False
    
    def calculate_costs(self):
        """Calculate materials, labor, and totals from template"""
        materials = []
        labor_items = []
        
        # Labor rates by skill level
        labor_rates = {
            'maintenance': 45.00, 'install': 65.00, 'pruning': 75.00, 
            'electrical': 85.00, 'irrigation_tech': 75.00, 'certified_applicator': 70.00,
            'carpenter': 80.00, 'arborist': 95.00, 'equipment_operator': 70.00,
            'design': 85.00, 'concrete': 70.00, 'customer_service': 50.00
        }
        
        # Process materials
        for material in self.template_data.get('materials', []):
            try:
                unit_cost = Decimal(str(material.get('unit_cost', 0)))
                default_qty = material.get('default_qty', 1)
                markup = Decimal(str(material.get('markup', 0)))
                
                marked_up_cost = unit_cost * (1 + markup)
                subtotal = marked_up_cost * default_qty
                
                materials.append({
                    'description': material.get('description', 'Material'),
                    'qty': default_qty,
                    'unit': material.get('unit', 'each'),
                    'unit_cost': float(marked_up_cost),
                    'subtotal': float(subtotal)
                })
            except Exception as e:
                print(f"⚠️  Material calculation error: {e}")
                continue
        
        # Process labor
        for labor in self.template_data.get('labor', []):
            try:
                default_hrs = labor.get('default_hrs', 1)
                skill_level = labor.get('skill_level', 'maintenance')
                crew_size = labor.get('crew_size', 1)
                hourly_rate = labor_rates.get(skill_level, 50.00)
                
                subtotal = default_hrs * hourly_rate * crew_size
                
                labor_items.append({
                    'task': labor.get('description', 'Labor task'),
                    'hours': default_hrs,
                    'crew_size': crew_size,
                    'rate': hourly_rate,
                    'subtotal': subtotal
                })
            except Exception as e:
                print(f"⚠️  Labor calculation error: {e}")
                continue
        
        return materials, labor_items
    
    def create_html_document(self, materials, labor_items):
        """Create HTML document that can be converted to ODT"""
        materials_total = sum(item['subtotal'] for item in materials)
        labor_total = sum(item['subtotal'] for item in labor_items)
        subtotal = materials_total + labor_total
        tax = 0.00  # Oregon
        total = subtotal + tax
        
        # Generate title with parameters
        parameters = self.template_data.get('parameters', {})
        title_format = self.template_data.get('title_format', 'Service')
        try:
            format_values = {k: v.get('default', 'N/A') for k, v in parameters.items()}
            project_title = title_format.format(**format_values)
        except:
            project_title = title_format
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>WaterWizard Estimate</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .company {{ font-size: 24px; font-weight: bold; color: #2E5984; }}
        .subtitle {{ font-size: 16px; margin-top: 10px; }}
        .client-info {{ margin: 20px 0; }}
        .section {{ margin: 25px 0; }}
        .section-title {{ font-size: 18px; font-weight: bold; color: #2E5984; margin-bottom: 10px; }}
        .item {{ margin: 5px 0; display: flex; justify-content: space-between; }}
        .item-desc {{ flex: 1; }}
        .item-qty {{ width: 80px; text-align: center; }}
        .item-cost {{ width: 100px; text-align: right; }}
        .totals {{ margin-top: 30px; border-top: 2px solid #2E5984; padding-top: 15px; }}
        .total-line {{ display: flex; justify-content: space-between; margin: 5px 0; }}
        .grand-total {{ font-weight: bold; font-size: 18px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{
            background-color: transparent;
            color: black;
            padding: 8pt;
            text-align: left;
            font-weight: bold;
            font-size: 10pt;
            border-bottom: 1pt solid #dee2e6;
        }}
        .currency {{ text-align: right; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="company">WaterWizard Irrigation & Landscape</div>
        <div class="subtitle">Professional Landscape Services</div>
        <div class="subtitle">Licensed • Bonded • Insured</div>
    </div>
    
    <div class="client-info">
        <strong>ESTIMATE</strong><br>
        <br>
        <strong>Client:</strong> {self.input_data.get('client_name', 'Client Name')}<br>
        <strong>Property:</strong> {self.input_data.get('property_address', 'Property Address')}<br>
        <strong>Date:</strong> {self.input_data.get('estimate_date', 'Date')}<br>
        <strong>Phone:</strong> {self.input_data.get('contact_info', {}).get('phone', 'Phone')}<br>
        <strong>Email:</strong> {self.input_data.get('contact_info', {}).get('email', 'Email')}
    </div>
    
    <div class="section">
        <div class="section-title">PROJECT: {project_title}</div>
        <p><strong>Description:</strong> {self.template_data.get('description', 'Project description')}</p>
        
        <p><strong>Assumptions:</strong></p>
        <ul>
"""
        
        # Add assumptions
        for assumption in self.template_data.get('assumptions', []):
            html_content += f"            <li>{assumption}</li>\n"
        
        html_content += "        </ul>\n    </div>\n"
        
        # Materials section
        if materials:
            html_content += f"""
    <div class="section">
        <div class="section-title">MATERIALS & EQUIPMENT</div>
        <table>
            <tr>
                <th>Description</th>
                <th>Qty</th>
                <th>Unit</th>
                <th>Unit Cost</th>
                <th>Subtotal</th>
            </tr>
"""
            for material in materials:
                html_content += f"""
            <tr>
                <td>{material['description']}</td>
                <td class="currency">{material['qty']}</td>
                <td>{material['unit']}</td>
                <td class="currency">${material['unit_cost']:.2f}</td>
                <td class="currency">${material['subtotal']:.2f}</td>
            </tr>
"""
            html_content += f"""
        </table>
        <div class="total-line"><strong>Materials Total: ${materials_total:.2f}</strong></div>
    </div>
"""
        
        # Labor section
        if labor_items:
            html_content += f"""
    <div class="section">
        <div class="section-title">LABOR & INSTALLATION</div>
        <table>
            <tr>
                <th>Task Description</th>
                <th>Hours</th>
                <th>Crew</th>
                <th>Rate</th>
                <th>Subtotal</th>
            </tr>
"""
            for labor in labor_items:
                html_content += f"""
            <tr>
                <td>{labor['task']}</td>
                <td class="currency">{labor['hours']:.1f}</td>
                <td class="currency">{labor['crew_size']}</td>
                <td class="currency">${labor['rate']:.2f}/hr</td>
                <td class="currency">${labor['subtotal']:.2f}</td>
            </tr>
"""
            html_content += f"""
        </table>
        <div class="total-line"><strong>Labor Total: ${labor_total:.2f}</strong></div>
    </div>
"""
        
        # Totals
        html_content += f"""
    <div class="totals">
        <div class="total-line">Subtotal: <span class="currency">${subtotal:.2f}</span></div>
        <div class="total-line">Tax (Oregon): <span class="currency">${tax:.2f}</span></div>
        <div class="total-line grand-total">TOTAL: <span class="currency">${total:.2f}</span></div>
    </div>
    
    <div class="section">
        <p><strong>Valid for:</strong> 30 days from estimate date</p>
        <p><strong>Payment:</strong> Due upon completion</p>
        <p><strong>Contact:</strong> {self.input_data.get('company_info', {}).get('phone', '(503) 555-0199')} | {self.input_data.get('company_info', {}).get('email', 'info@waterwizard.com')}</p>
    </div>
</body>
</html>
"""
        return html_content, total
    
    def generate_estimate(self, template_path: str, input_path: str, output_path: str):
        """Generate complete estimate document"""
        print(f"🔄 Generating estimate from template: {Path(template_path).name}")
        
        if not self.load_files(template_path, input_path):
            return False
        
        materials, labor_items = self.calculate_costs()
        html_content, total = self.create_html_document(materials, labor_items)
        
        # Create temporary HTML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            temp_html = f.name
        
        try:
            # Convert HTML to ODT using LibreOffice
            cmd = [
                'libreoffice', '--headless', '--convert-to', 'odt',
                '--outdir', str(Path(output_path).parent),
                temp_html
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Move and rename the generated file
                temp_odt = Path(temp_html).with_suffix('.odt')
                if temp_odt.exists():
                    temp_odt.rename(output_path)
                    print(f"✅ Generated: {output_path}")
                    print(f"   Template: {self.template_data.get('template_id')}")
                    print(f"   Total: ${total:.2f}")
                    return True
                else:
                    print(f"❌ ODT file not created: {temp_odt}")
                    return False
            else:
                print(f"❌ LibreOffice conversion failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Conversion error: {e}")
            return False
        finally:
            # Cleanup
            Path(temp_html).unlink(missing_ok=True)

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 simple_template_generator.py <template.json> <input.json> <output.odt>")
        sys.exit(1)
    
    generator = SimpleTemplateGenerator()
    success = generator.generate_estimate(sys.argv[1], sys.argv[2], sys.argv[3])
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()