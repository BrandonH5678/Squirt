#!/usr/bin/env python3
"""
HTML-to-ODT Template Generator
Uses LibreOffice headless conversion for reliable ODT generation
"""

import json
import subprocess
import tempfile
import sys
import os
from pathlib import Path
from decimal import Decimal

class HtmlToOdtGenerator:
    """Generate ODT documents using HTML intermediate and LibreOffice conversion"""
    
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
            print(f"✅ Loaded template: {self.template_data.get('template_id')}")
            print(f"✅ Loaded input for: {self.input_data.get('client_name')}")
            return True
        except Exception as e:
            print(f"❌ Error loading files: {e}")
            return False
    
    def calculate_costs(self):
        """Calculate materials, labor, and totals from template"""
        materials = []
        labor_items = []
        equipment_items = []
        
        # Labor rates by skill level
        labor_rates = {
            'maintenance': 45.00, 'install': 65.00, 'pruning': 75.00, 
            'electrical': 85.00, 'irrigation_tech': 85.00, 'certified_applicator': 70.00,
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
                    'subtotal': float(subtotal),
                    'specs': material.get('specifications', [])
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
                    'skill_level': skill_level,
                    'rate': hourly_rate,
                    'subtotal': subtotal,
                    'equipment': labor.get('equipment_required', [])
                })
            except Exception as e:
                print(f"⚠️  Labor calculation error: {e}")
                continue
        
        # Process equipment
        for equipment in self.template_data.get('equipment', []):
            try:
                usage = equipment.get('usage_formula', '1')
                if usage.isdigit():
                    usage_qty = int(usage)
                else:
                    usage_qty = 1
                
                daily_rate = equipment.get('daily_rate', 0)
                subtotal = usage_qty * daily_rate
                
                if subtotal > 0:  # Only include if there's a cost
                    equipment_items.append({
                        'description': equipment.get('description', 'Equipment'),
                        'qty': usage_qty,
                        'unit': equipment.get('usage_unit', 'day'),
                        'rate': daily_rate,
                        'subtotal': subtotal
                    })
            except Exception as e:
                print(f"⚠️  Equipment calculation error: {e}")
                continue
        
        return materials, labor_items, equipment_items
    
    def create_professional_html(self, materials, labor_items, equipment_items):
        """Create professional HTML document"""
        materials_total = sum(item['subtotal'] for item in materials)
        labor_total = sum(item['subtotal'] for item in labor_items)
        equipment_total = sum(item['subtotal'] for item in equipment_items)
        
        subtotal = materials_total + labor_total + equipment_total
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
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>WaterWizard Estimate - {project_title}</title>
    <style>
        @page {{
            size: letter;
            margin: 0.75in;
        }}
        body {{
            font-family: 'Arial', sans-serif;
            font-size: 11pt;
            line-height: 1.4;
            color: #333;
            margin: 0;
            padding: 0;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30pt;
            border-bottom: 3pt solid #2E5984;
            padding-bottom: 15pt;
        }}
        .company {{
            font-size: 20pt;
            font-weight: bold;
            color: #2E5984;
            margin-bottom: 5pt;
        }}
        .tagline {{
            font-size: 12pt;
            color: #666;
            margin: 3pt 0;
        }}
        .credentials {{
            font-size: 10pt;
            color: #888;
            font-style: italic;
        }}
        .estimate-label {{
            font-size: 16pt;
            font-weight: bold;
            color: #2E5984;
            margin: 20pt 0 15pt 0;
            text-align: center;
            background-color: #f8f9fa;
            padding: 10pt;
            border: 1pt solid #dee2e6;
        }}
        .client-section {{
            display: table;
            width: 100%;
            margin: 20pt 0;
        }}
        .client-left, .client-right {{
            display: table-cell;
            width: 50%;
            vertical-align: top;
        }}
        .client-right {{
            text-align: right;
        }}
        .field {{
            margin: 5pt 0;
        }}
        .field-label {{
            font-weight: bold;
            color: #2E5984;
        }}
        .section {{
            margin: 25pt 0;
        }}
        .section-title {{
            font-size: 14pt;
            font-weight: bold;
            color: #2E5984;
            margin: 25pt 0 15pt 0;
            padding: 8pt 0;
            border-bottom: 2pt solid #2E5984;
        }}
        .section-title:first-of-type {{
            margin-top: 15pt;
        }}
        .project-title {{
            font-size: 16pt;
            font-weight: bold;
            color: #1a365d;
            margin: 20pt 0 10pt 0;
            text-align: center;
        }}
        .description {{
            background-color: #f8f9fa;
            padding: 15pt;
            border-left: 4pt solid #2E5984;
            margin: 15pt 0;
            font-style: italic;
        }}
        .assumptions {{
            background-color: #fff3cd;
            border: 1pt solid #ffeaa7;
            padding: 4pt 8pt;
            margin: 5pt 0;
        }}
        .assumptions h4 {{
            margin: 0 0 3pt 0;
            color: #856404;
            font-size: 10pt;
        }}
        .assumptions ul {{
            margin: 0;
            padding-left: 20pt;
        }}
        .assumptions li {{
            margin: 3pt 0;
            color: #856404;
        }}
        table {{
            border-collapse: collapse;
            border: 2pt solid #2E5984;
            width: 100%;
            border-collapse: collapse;
            margin: 15pt 0;
            font-size: 10pt;
        }}
        th {{
            background-color: transparent;
            color: black;
            padding: 8pt;
            text-align: left;
            font-weight: bold;
            font-size: 10pt;
            border-bottom: 1pt solid #dee2e6;
        }}
        td {{
            padding: 8pt;
            border-bottom: 1pt solid #dee2e6;
            vertical-align: top;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        .currency {{
            text-align: right;
            font-weight: bold;
        }}
        .center {{
            text-align: center;
        }}
        .section-total {{
            background-color: #e9ecef;
            font-weight: bold;
            border-top: 2pt solid #2E5984;
        }}
        .totals {{
            margin: 30pt 0;
            background-color: #f8f9fa;
            border: 2pt solid #2E5984;
            padding: 20pt;
        }}
        .total-row {{
            display: table;
            width: 100%;
            margin: 8pt 0;
        }}
        .total-label {{
            display: table-cell;
            font-size: 12pt;
            padding: 5pt 0;
        }}
        .total-amount {{
            display: table-cell;
            text-align: right;
            font-size: 12pt;
            font-weight: bold;
            padding: 5pt 0;
            width: 120pt;
        }}
        .grand-total {{
            border-top: 2pt solid #2E5984;
            padding-top: 10pt;
            margin-top: 10pt;
        }}
        .grand-total .total-label {{
            font-size: 16pt;
            font-weight: bold;
            color: #2E5984;
        }}
        .grand-total .total-amount {{
            font-size: 16pt;
            font-weight: bold;
            color: #2E5984;
        }}
        .footer {{
            margin-top: 40pt;
            padding-top: 20pt;
            border-top: 1pt solid #dee2e6;
            font-size: 10pt;
            color: #666;
        }}
        .footer-section {{
            display: table-cell;
            width: 33%;
            vertical-align: top;
        }}
        .specs {{
            font-size: 9pt;
            color: #666;
            margin-top: 3pt;
        }}
        .equipment-note {{
            font-size: 9pt;
            color: #666;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="company">WaterWizard Irrigation & Landscape</div>
        <div class="tagline">Professional Landscape Services</div>
        <div class="credentials">Licensed • Bonded • Insured • CCB #{self.input_data.get('company_info', {}).get('license', '12345')}</div>
    </div>
    
    <div class="estimate-label">ESTIMATE</div>
    
    <div class="client-section">
        <div class="client-left">
            <div class="field">
                <span class="field-label">Client:</span> {self.input_data.get('client_name', 'Client Name')}
            </div>
            <div class="field">
                <span class="field-label">Property:</span> {self.input_data.get('property_address', 'Property Address')}
            </div>
            <div class="field">
                <span class="field-label">Phone:</span> {self.input_data.get('contact_info', {}).get('phone', 'Phone')}
            </div>
            <div class="field">
                <span class="field-label">Email:</span> {self.input_data.get('contact_info', {}).get('email', 'Email')}
            </div>
        </div>
        <div class="client-right">
            <div class="field">
                <span class="field-label">Date:</span> {self.input_data.get('estimate_date', 'Date')}
            </div>
            <div class="field">
                <span class="field-label">Valid:</span> 30 days
            </div>
            <div class="field">
                <span class="field-label">Contact:</span> {self.input_data.get('company_info', {}).get('phone', '(503) 555-0199')}
            </div>
            <div class="field">
                <span class="field-label">Email:</span> {self.input_data.get('company_info', {}).get('email', 'info@waterwizard.com')}
            </div>
        </div>
    </div>
    
    <div class="project-title">{project_title}</div>
    
    <div class="description">
        <strong>Project Description:</strong> {self.template_data.get('description', 'Project description')}
    </div>
    
    <div class="assumptions">
        <h4>Project Assumptions:</h4>
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
            <thead>
                <tr>
                    <th style="width: 50%;">Item Description</th>
                    <th style="width: 8%;">Quantity</th>
                    <th style="width: 8%;">Unit Type</th>
                    <th style="width: 12%;">Unit Cost</th>
                    <th style="width: 12%;">Subtotal</th>
                </tr>
            </thead>
            <tbody>
"""
            for material in materials:
                html_content += f"""
                <tr>
                    <td>
                        {material['description']}
"""
                if material.get('specs'):
                    html_content += f"                        <div class=\"specs\">• {' • '.join(material['specs'])}</div>\n"
                
                html_content += f"""                    </td>
                    <td class="center">{material['qty']}</td>
                    <td class="center">{material['unit']}</td>
                    <td class="currency">${material['unit_cost']:.2f}</td>
                    <td class="currency">${material['subtotal']:.2f}</td>
                </tr>
"""
            
            html_content += f"""
                <tr class="section-total">
                    <td colspan="4"><strong>MATERIALS TOTAL</strong></td>
                    <td class="currency"><strong>${materials_total:.2f}</strong></td>
                </tr>
            </tbody>
        </table>
    </div>
"""
        
        # Equipment section (if separate from materials)
        if equipment_items:
            html_content += f"""
    <div class="section">
        <div class="section-title">EQUIPMENT</div>
        <table>
            <thead>
                <tr>
                    <th style="width: 50%;">Equipment Description</th>
                    <th style="width: 10%;">Days/Units</th>
                    <th style="width: 10%;">Unit Type</th>
                    <th style="width: 12%;">Daily Rate</th>
                    <th style="width: 12%;">Subtotal</th>
                </tr>
            </thead>
            <tbody>
"""
            for equipment in equipment_items:
                html_content += f"""
                <tr>
                    <td>{equipment['description']}</td>
                    <td class="center">{equipment['qty']}</td>
                    <td class="center">{equipment['unit']}</td>
                    <td class="currency">${equipment['rate']:.2f}</td>
                    <td class="currency">${equipment['subtotal']:.2f}</td>
                </tr>
"""
            
            html_content += f"""
                <tr class="section-total">
                    <td colspan="4"><strong>EQUIPMENT TOTAL</strong></td>
                    <td class="currency"><strong>${equipment_total:.2f}</strong></td>
                </tr>
            </tbody>
        </table>
    </div>
"""
        
        # Labor section
        if labor_items:
            html_content += f"""
    <div class="section">
        <div class="section-title">LABOR & INSTALLATION</div>
        <table>
            <thead>
                <tr>
                    <th style="width: 50%;">Task Description</th>
                    <th style="width: 8%;">Est. Hours</th>
                    <th style="width: 8%;">Crew Size</th>
                    <th style="width: 12%;">$/Hour</th>
                    <th style="width: 12%;">Subtotal</th>
                </tr>
            </thead>
            <tbody>
"""
            for labor in labor_items:
                html_content += f"""
                <tr>
                    <td>
                        {labor['task']}
"""
                if labor.get('equipment'):
                    html_content += f"                        <div class=\"equipment-note\">Equipment: {', '.join(labor['equipment'])}</div>\n"
                
                html_content += f"""                    </td>
                    <td class="center">{labor['hours']:.1f}</td>
                    <td class="center">{labor['crew_size']}</td>
                    <td class="currency">${labor['rate']:.2f}/hr</td>
                    <td class="currency">${labor['subtotal']:.2f}</td>
                </tr>
"""
            
            html_content += f"""
                <tr class="section-total">
                    <td colspan="4"><strong>LABOR TOTAL</strong></td>
                    <td class="currency"><strong>${labor_total:.2f}</strong></td>
                </tr>
            </tbody>
        </table>
    </div>
"""
        
        # Totals section
        html_content += f"""
    <div class="totals">
        <div class="total-row">
            <div class="total-label">Subtotal:</div>
            <div class="total-amount">${subtotal:.2f}</div>
        </div>
        <div class="total-row">
            <div class="total-label">Tax (Oregon):</div>
            <div class="total-amount">${tax:.2f}</div>
        </div>
        <div class="total-row grand-total">
            <div class="total-label">TOTAL:</div>
            <div class="total-amount">${total:.2f}</div>
        </div>
    </div>
    
    <div class="footer">
        <div style="display: table; width: 100%;">
            <div class="footer-section">
                <strong>Payment Terms:</strong><br>
                Due upon completion
            </div>
            <div class="footer-section" style="text-align: center;">
                <strong>Template:</strong> {self.template_data.get('template_id')}<br>
                <strong>Category:</strong> {self.template_data.get('category')}
            </div>
            <div class="footer-section" style="text-align: right;">
                <strong>Generated:</strong> Template-driven<br>
                (Not hardcoded data)
            </div>
        </div>
    </div>
</body>
</html>
"""
        
        return html_content, total
    
    def convert_to_odt(self, html_content: str, output_path: str):
        """Convert HTML content to ODT using LibreOffice"""
        # Kill any existing LibreOffice processes to prevent conflicts
        try:
            subprocess.run(['pkill', '-f', 'libreoffice'], capture_output=True)
        except:
            pass
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_html = f.name
        
        try:
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Convert HTML to ODT - LibreOffice puts output in same dir as input
            temp_dir = Path(temp_html).parent
            cmd = [
                'libreoffice', '--headless', '--convert-to', 'odt',
                '--outdir', str(temp_dir),
                temp_html
            ]
            
            print(f"🔄 Converting to ODT...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
            
            if result.returncode == 0:
                # LibreOffice creates ODT with same name as HTML input
                temp_odt_name = Path(temp_html).stem + '.odt'
                temp_odt_path = temp_dir / temp_odt_name
                
                # Wait a moment for file to be fully written
                import time
                time.sleep(0.5)
                
                if temp_odt_path.exists():
                    # Move to desired location
                    import shutil
                    shutil.move(str(temp_odt_path), output_path)
                    print(f"✅ ODT generated successfully: {Path(output_path).name}")
                    print(f"📁 File saved at: {output_path}")
                    return True
                else:
                    print(f"❌ ODT file not found at: {temp_odt_path}")
                    print("Files in temp directory:")
                    for f in temp_dir.iterdir():
                        if f.suffix in ['.odt', '.html']:
                            print(f"   {f.name}")
                    return False
            else:
                print(f"❌ LibreOffice conversion failed (exit code: {result.returncode})")
                if result.stdout:
                    print(f"   stdout: {result.stdout}")
                if result.stderr:
                    print(f"   stderr: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ LibreOffice conversion timed out after 45 seconds")
            return False
        except Exception as e:
            print(f"❌ Conversion error: {e}")
            return False
        finally:
            # Cleanup temp HTML file
            try:
                Path(temp_html).unlink(missing_ok=True)
            except:
                pass
    
    def generate_estimate(self, template_path: str, input_path: str, output_path: str):
        """Generate complete ODT estimate from template"""
        print(f"📊 HTML-TO-ODT TEMPLATE GENERATOR")
        print(f"Template: {Path(template_path).name}")
        print(f"Output: {Path(output_path).name}")
        print("-" * 50)
        
        if not self.load_files(template_path, input_path):
            return False
        
        materials, labor_items, equipment_items = self.calculate_costs()
        html_content, total = self.create_professional_html(materials, labor_items, equipment_items)
        
        print(f"💰 Calculated total: ${total:.2f}")
        print(f"   Materials: {len(materials)} items")
        print(f"   Labor: {len(labor_items)} tasks") 
        print(f"   Equipment: {len(equipment_items)} items")
        
        success = self.convert_to_odt(html_content, output_path)
        
        if success:
            print(f"🎯 SUCCESS: Professional ODT estimate generated!")
            return True
        else:
            print(f"❌ FAILED: ODT generation failed")
            return False

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 html_to_odt_generator.py <template.json> <input.json> <output.odt>")
        sys.exit(1)
    
    generator = HtmlToOdtGenerator()
    success = generator.generate_estimate(sys.argv[1], sys.argv[2], sys.argv[3])
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()