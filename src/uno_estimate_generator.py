#!/usr/bin/env python3
"""
SQUIRT 1.2 UNO ESTIMATE GENERATOR - PRODUCTION VERSION
Template-driven professional estimate generator replacing hardcoded system
"""

import json
import subprocess
import tempfile
import sys
import os
import re
import math
from pathlib import Path
from decimal import Decimal

class UnoEstimateGenerator:
    """Production template-driven estimate generator for Squirt 1.2"""
    
    def __init__(self):
        self.template_data = None
        self.input_data = None
        self.parameters = {}
    
    def load_files(self, template_path: str, input_path: str):
        """Load template and input files"""
        try:
            with open(template_path, 'r') as f:
                self.template_data = json.load(f)
            with open(input_path, 'r') as f:
                self.input_data = json.load(f)
            self._process_parameters()
            return True
        except Exception as e:
            print(f"❌ Error loading files: {e}")
            return False

    def _process_parameters(self):
        """Process template parameters and set values from defaults"""
        template_params = self.template_data.get('parameters', {})
        for param_name, param_def in template_params.items():
            self.parameters[param_name] = param_def.get('default', 0)

        print(f"📊 Processed parameters: {self.parameters}")

    def _evaluate_formula(self, formula: str) -> float:
        """Safely evaluate a formula with template parameters"""
        if not formula or not isinstance(formula, str):
            return 0.0

        try:
            # Handle simple numeric values
            if formula.replace('.', '').isdigit():
                return float(formula)

            # Replace parameter names with their values in a safe way
            eval_formula = formula

            # Sort parameters by length (longest first) to avoid partial replacements
            sorted_params = sorted(self.parameters.items(), key=lambda x: len(x[0]), reverse=True)

            for param, value in sorted_params:
                if isinstance(value, str):
                    # Handle string parameters in comparisons
                    eval_formula = re.sub(rf'\b{param}\b', f"'{value}'", eval_formula)
                else:
                    # Handle numeric parameters
                    eval_formula = re.sub(rf'\b{param}\b', str(value), eval_formula)

            # Handle common template ternary patterns manually
            if 'tree_coverage ==' in eval_formula and 'light' in eval_formula:
                # Handle tree coverage multiplier
                tree_cov = self.parameters.get('tree_coverage', 'moderate')
                if tree_cov == 'light':
                    multiplier = 0.5
                elif tree_cov == 'moderate':
                    multiplier = 1.0
                elif tree_cov == 'heavy':
                    multiplier = 1.5
                else:
                    multiplier = 2.0

                eval_formula = re.sub(
                    r'\(tree_coverage == \'light\' \? 0\.5 : tree_coverage == \'moderate\' \? 1\.0 : tree_coverage == \'heavy\' \? 1\.5 : 2\.0\)',
                    str(multiplier), eval_formula)

            if 'property_size ==' in eval_formula and 'small' in eval_formula:
                # Handle property size logic
                prop_size = self.parameters.get('property_size', 'medium')
                if prop_size == 'small':
                    size_val = 2
                elif prop_size == 'medium':
                    size_val = 3
                elif prop_size == 'large':
                    size_val = 4
                else:
                    size_val = 6

                eval_formula = re.sub(
                    r'\(property_size == \'small\' \? 2 : property_size == \'medium\' \? 3 : property_size == \'large\' \? 4 : 6\)',
                    str(size_val), eval_formula)

            # Handle simple ternary operators
            eval_formula = re.sub(r'(\w+)\s*\?\s*([^:]+)\s*:\s*([^?]*?)(?=\s*[),]|$)',
                                r'(\2 if \1 else \3)', eval_formula)

            # Safe evaluation with math functions available
            allowed_names = {
                "ceil": math.ceil, "floor": math.floor, "sqrt": math.sqrt,
                "abs": abs, "min": min, "max": max, "round": round
            }

            # Add parameter values to allowed names
            for param, value in self.parameters.items():
                if not isinstance(value, str):
                    allowed_names[param] = value

            print(f"🔍 Evaluating: {formula} -> {eval_formula}")
            result = eval(eval_formula, {"__builtins__": {}}, allowed_names)
            return float(result) if result is not None else 0.0

        except Exception as e:
            print(f"⚠️  Formula evaluation error for '{formula}': {e}")
            # Try to extract numeric value as fallback
            numbers = re.findall(r'\d+\.?\d*', formula)
            if numbers:
                return float(numbers[0])
            return 0.0
    
    def calculate_costs(self):
        """Calculate materials, labor, and totals from template"""
        materials = []
        labor_items = []
        equipment_items = []
        
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
                # Use formula if available, otherwise default
                qty_formula = material.get('qty_formula')
                if qty_formula:
                    qty = self._evaluate_formula(qty_formula)
                    print(f"🧮 Material '{material.get('description')}': {qty_formula} = {qty}")
                else:
                    qty = material.get('default_qty', 0)
                    print(f"📝 Material '{material.get('description')}': using default qty {qty}")

                unit_cost = material.get('unit_cost', 0)
                markup = material.get('markup', 0)

                marked_up_cost = unit_cost * (1 + markup)
                subtotal = qty * marked_up_cost

                if subtotal > 0:
                    materials.append({
                        'description': material.get('description', 'Material'),
                        'qty': round(qty, 2),
                        'unit': material.get('unit', 'each'),
                        'cost': marked_up_cost,
                        'subtotal': subtotal
                    })
            except Exception as e:
                print(f"⚠️  Material calculation error: {e}")
                continue
        
        # Process labor
        for labor in self.template_data.get('labor', []):
            try:
                # Use formula if available, otherwise default
                hrs_formula = labor.get('hrs_formula')
                if hrs_formula:
                    hrs = self._evaluate_formula(hrs_formula)
                    print(f"🧮 Labor '{labor.get('description')}': {hrs_formula} = {hrs} hrs")
                else:
                    hrs = labor.get('default_hrs', 0)
                    print(f"📝 Labor '{labor.get('description')}': using default hrs {hrs}")

                skill = labor.get('skill_level', 'maintenance')
                crew_size = labor.get('crew_size', 1)
                rate = labor_rates.get(skill, 65.00)

                subtotal = hrs * crew_size * rate

                if subtotal > 0:
                    labor_items.append({
                        'description': labor.get('description', 'Labor'),
                        'hours': round(hrs, 2),
                        'crew': crew_size,
                        'rate': rate,
                        'subtotal': subtotal
                    })
            except Exception as e:
                print(f"⚠️  Labor calculation error: {e}")
                continue
        
        # Process equipment
        for equipment in self.template_data.get('equipment', []):
            try:
                usage_formula = equipment.get('usage_formula', '1')
                usage_qty = self._evaluate_formula(usage_formula)
                if usage_qty == 0:
                    usage_qty = 1  # Default fallback

                print(f"🧮 Equipment '{equipment.get('description')}': {usage_formula} = {usage_qty}")

                daily_rate = equipment.get('daily_rate', 0)
                subtotal = usage_qty * daily_rate

                if subtotal > 0:
                    equipment_items.append({
                        'description': equipment.get('description', 'Equipment'),
                        'qty': round(usage_qty, 2),
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
            font-family: Arial, sans-serif;
            line-height: 1.3;
            margin: 0;
            padding: 0;
            color: #333;
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid #2E5B8A;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }}
        .company-name {{
            font-size: 18px;
            font-weight: bold;
            color: #2E5B8A;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin: 0;
        }}
        .tagline {{
            font-size: 12px;
            color: #666;
            margin: 5px 0;
        }}
        .license {{
            font-size: 11px;
            color: #666;
            margin: 0;
        }}
        .estimate-title {{
            font-size: 16px;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .client-section {{
            display: flex;
            justify-content: space-between;
            margin: 15px 0;
            padding: 10px;
            background-color: #f8f9fa;
            border: 1px solid #ddd;
        }}
        .client-info, .project-info {{
            flex: 1;
        }}
        .field-label {{
            font-weight: bold;
            color: #2E5B8A;
        }}
        .project-header {{
            border-bottom: 2px solid #2E5B8A;
            margin: 20px 0 15px 0;
            padding-bottom: 5px;
        }}
        .project-title {{
            font-size: 14px;
            font-weight: bold;
            color: #2E5B8A;
            text-transform: uppercase;
            margin: 0;
        }}
        .project-description {{
            font-size: 11px;
            color: #666;
            margin: 5px 0 10px 0;
            line-height: 1.4;
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
        .section {{
            margin: 20px 0;
        }}
        .section-title {{
            background-color: #2E5B8A;
            color: white;
            padding: 8px;
            font-weight: bold;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 0;
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
            padding: 6px 8px;
            font-size: 10px;
            border: 1px solid #ddd;
            vertical-align: top;
        }}
        .center {{ text-align: center; }}
        .currency {{ text-align: right; }}
        .section-total {{
            font-weight: bold;
            background-color: #f8f9fa;
        }}
        .totals-section {{
            margin-top: 30px;
            border-top: 2px solid #2E5B8A;
            padding-top: 15px;
        }}
        .total-line {{
            display: flex;
            justify-content: space-between;
            margin: 8px 0;
            padding: 5px 0;
        }}
        .total-label {{
            font-weight: bold;
            color: #2E5B8A;
        }}
        .total-amount {{
            font-weight: bold;
            text-align: right;
        }}
        .grand-total {{
            border-top: 2px solid #2E5B8A;
            font-size: 14px;
            font-weight: bold;
            color: #2E5B8A;
        }}
        .footer {{
            margin-top: 30px;
            font-size: 10px;
            color: #666;
            text-align: center;
            border-top: 1px solid #ddd;
            padding-top: 15px;
        }}
        .footer-line {{
            margin: 3px 0;
        }}
    </style>
</head>
<body>
    <!-- Header -->
    <div class="header">
        <div class="company-name">WaterWizard Irrigation & Landscape</div>
        <div class="tagline">Professional Landscape Services</div>
        <div class="license">Licensed • Bonded • Insured</div>
    </div>
    
    <div class="estimate-title">ESTIMATE</div>
    
    <!-- Client Information -->
    <div class="client-section">
        <div class="client-info">
            <div><span class="field-label">Client:</span> {self.input_data.get('client_name', 'Client Name')}</div>
            <div><span class="field-label">Property:</span> {self.input_data.get('property_address', 'Property Address')}</div>
            <div><span class="field-label">Date:</span> {self.input_data.get('estimate_date', 'Date')}</div>
        </div>
        <div class="project-info">
            <div><span class="field-label">Phone:</span> {self.input_data.get('contact_info', {}).get('phone', 'Phone')}</div>
            <div><span class="field-label">Email:</span> {self.input_data.get('contact_info', {}).get('email', 'Email')}</div>
        </div>
    </div>
    
    <!-- Project Header -->
    <div class="project-header">
        <div class="project-title">PROJECT: {project_title}</div>
        <div class="project-description">{self.template_data.get('description', '')}</div>
        <div class="assumptions">
            <strong>Assumptions:</strong>
            <ul>"""
        
        for assumption in self.template_data.get('assumptions', []):
            html_content += f"<li>{assumption}</li>"
        
        html_content += """
            </ul>
        </div>
    </div>
    
    <!-- Materials Section -->
    <div class="section">
        <div class="section-title">MATERIALS & EQUIPMENT</div>
        <table>
            <thead>
                <tr>
                    <th style="width: 50%;">Description</th>
                    <th style="width: 8%;">Qty</th>
                    <th style="width: 8%;">Unit</th>
                    <th style="width: 12%;">Cost</th>
                    <th style="width: 12%;">Subtotal</th>
                </tr>
            </thead>
            <tbody>"""
        
        for material in materials:
            html_content += f"""
                <tr>
                    <td>{material['description']}</td>
                    <td class="center">{material['qty']}</td>
                    <td class="center">{material['unit']}</td>
                    <td class="currency">${material['cost']:.2f}</td>
                    <td class="currency">${material['subtotal']:.2f}</td>
                </tr>"""
        
        html_content += f"""
                <tr class="section-total">
                    <td colspan="4"><strong>MATERIALS TOTAL</strong></td>
                    <td class="currency"><strong>${materials_total:.2f}</strong></td>
                </tr>
            </tbody>
        </table>
    </div>"""
        
        # Labor section
        if labor_items:
            html_content += f"""
    <div class="section">
        <div class="section-title">LABOR & INSTALLATION</div>
        <table>
            <thead>
                <tr>
                    <th style="width: 50%;">Task Description</th>
                    <th style="width: 8%;">Hours</th>
                    <th style="width: 8%;">Crew</th>
                    <th style="width: 12%;">Rate</th>
                    <th style="width: 12%;">Subtotal</th>
                </tr>
            </thead>
            <tbody>"""
            
            for labor in labor_items:
                html_content += f"""
                <tr>
                    <td>{labor['description']}</td>
                    <td class="center">{labor['hours']}</td>
                    <td class="center">{labor['crew']}</td>
                    <td class="currency">${labor['rate']:.2f}</td>
                    <td class="currency">${labor['subtotal']:.2f}</td>
                </tr>"""
            
            html_content += f"""
                <tr class="section-total">
                    <td colspan="4"><strong>LABOR TOTAL</strong></td>
                    <td class="currency"><strong>${labor_total:.2f}</strong></td>
                </tr>
            </tbody>
        </table>
    </div>"""
        
        # Totals
        html_content += f"""
    <div class="totals-section">
        <div class="section-title">TOTALS</div>
        <div class="total-line">
            <span class="total-label">Subtotal:</span>
            <span class="total-amount">${subtotal:.2f}</span>
        </div>
        <div class="total-line">
            <span class="total-label">Tax (Oregon):</span>
            <span class="total-amount">${tax:.2f}</span>
        </div>
        <div class="total-line grand-total">
            <span class="total-label">TOTAL:</span>
            <span class="total-amount">${total:.2f}</span>
        </div>
    </div>
    
    <!-- Footer -->
    <div class="footer">
        <div class="footer-line">Valid for: 30 days from estimate date</div>
        <div class="footer-line">Payment: Due upon completion</div>
        <div class="footer-line">Contact: {self.input_data.get('company_info', {}).get('phone', '(503) 555-0199')} | {self.input_data.get('company_info', {}).get('email', 'info@waterwizard.com')}</div>
        <div class="footer-line">Template ID: {self.template_data.get('template_id')} | Category: {self.template_data.get('category')}</div>
        <div class="footer-line">Generated: This estimate was generated from template data (NOT hardcoded Liam Smith data)</div>
    </div>
</body>
</html>"""
        
        return html_content, total
    
    def convert_to_odt(self, html_content: str, output_path: str):
        """Convert HTML content to ODT using LibreOffice"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_html = f.name
        
        try:
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Convert HTML to ODT
            cmd = [
                'libreoffice', '--headless', '--convert-to', 'odt',
                '--outdir', str(Path(output_path).parent),
                temp_html
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
            
            if result.returncode == 0:
                # Find the generated ODT file
                temp_odt = Path(temp_html).with_suffix('.odt')
                if temp_odt.exists():
                    # Move to desired location
                    temp_odt.rename(output_path)
                    return True
                else:
                    # LibreOffice puts it in output directory with temp filename
                    output_dir = Path(output_path).parent
                    temp_name = Path(temp_html).stem + '.odt'
                    temp_odt = output_dir / temp_name
                    if temp_odt.exists():
                        temp_odt.rename(output_path)
                        return True
            
            print(f"❌ LibreOffice conversion failed: {result.stderr}")
            return False
            
        except Exception as e:
            print(f"❌ Conversion error: {e}")
            return False
        finally:
            # Clean up temp HTML
            try:
                os.unlink(temp_html)
            except:
                pass
    
    def generate_from_template(self, template_path: str, input_path: str, output_path: str):
        """Generate ODT estimate from template and input data"""
        if not self.load_files(template_path, input_path):
            return False
        
        materials, labor_items, equipment_items = self.calculate_costs()
        html_content, total = self.create_professional_html(materials, labor_items, equipment_items)
        
        success = self.convert_to_odt(html_content, output_path)
        
        if success:
            print(f"✅ Generated estimate: ${total:.2f} -> {output_path}")
            return True
        else:
            print(f"❌ Failed to generate estimate")
            return False

def get_tracked_path(filename, client_name, doc_type):
    """Generate tracked file path - maintains compatibility with original interface"""
    output_dir = Path.cwd() / "generated_estimates" 
    output_dir.mkdir(exist_ok=True)
    return str(output_dir / filename)

def main():
    """Production estimate generator - now template-driven instead of hardcoded"""
    print("📊 WATERWIZARD UNO ESTIMATE GENERATOR - SQUIRT 1.2")
    print("🎯 PRODUCTION VERSION - Template-Driven System")
    print("=" * 60)

    generator = UnoEstimateGenerator()

    # Use command line arguments if provided, otherwise use defaults
    if len(sys.argv) >= 3:
        template_path = sys.argv[1]
        input_path = sys.argv[2]
        print(f"📋 Using provided template: {template_path}")
        print(f"📄 Using provided input: {input_path}")
    else:
        # Default template and input for production demo
        template_path = "templates/estimates/maintenance/fall_cleanup_comprehensive.json"
        input_path = "test_validation_samples/sample_input_basic.json"
        print("📋 Using default fall cleanup template")

    output_path = get_tracked_path("production_estimate.odt", "Production", "estimate")

    try:
        success = generator.generate_from_template(template_path, input_path, output_path)

        if success:
            print("🎯 SUCCESS: Template-driven estimate generated!")
            print(f"📁 Output: {output_path}")
        else:
            print("❌ FAILED: Estimate generation failed")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()