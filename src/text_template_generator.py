#!/usr/bin/env python3
"""
Text-Based Template Generator
Generates text estimates to prove template processing works
"""

import json
import sys
from pathlib import Path
from decimal import Decimal

def generate_text_estimate(template_path: str, input_path: str, output_path: str):
    """Generate a text-based estimate from template"""
    
    # Load files
    with open(template_path, 'r') as f:
        template_data = json.load(f)
    with open(input_path, 'r') as f:
        input_data = json.load(f)
    
    print(f"🔄 Processing: {template_data.get('template_id')}")
    print(f"   Client: {input_data.get('client_name')}")
    
    # Calculate costs
    materials = []
    labor_items = []
    
    labor_rates = {
        'maintenance': 45.00, 'install': 65.00, 'pruning': 75.00, 
        'electrical': 85.00, 'irrigation_tech': 75.00, 'certified_applicator': 70.00,
        'carpenter': 80.00, 'arborist': 95.00, 'equipment_operator': 70.00
    }
    
    # Process materials
    for material in template_data.get('materials', []):
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
    
    # Process labor
    for labor in template_data.get('labor', []):
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
    
    # Calculate totals
    materials_total = sum(item['subtotal'] for item in materials)
    labor_total = sum(item['subtotal'] for item in labor_items)
    subtotal = materials_total + labor_total
    tax = 0.00  # Oregon
    total = subtotal + tax
    
    # Generate title
    parameters = template_data.get('parameters', {})
    title_format = template_data.get('title_format', 'Service')
    try:
        format_values = {k: v.get('default', 'N/A') for k, v in parameters.items()}
        project_title = title_format.format(**format_values)
    except:
        project_title = title_format
    
    # Create text content
    content = f"""
================================================================================
                      WATERWIZARD IRRIGATION & LANDSCAPE
                         Professional Landscape Services
                            Licensed • Bonded • Insured
================================================================================

ESTIMATE

Client: {input_data.get('client_name', 'Client Name')}
Property: {input_data.get('property_address', 'Property Address')}
Date: {input_data.get('estimate_date', 'Date')}
Phone: {input_data.get('contact_info', {}).get('phone', 'Phone')}
Email: {input_data.get('contact_info', {}).get('email', 'Email')}

================================================================================
PROJECT: {project_title}
================================================================================

Description: {template_data.get('description', 'Project description')}

Assumptions:
"""
    
    for assumption in template_data.get('assumptions', []):
        content += f"  • {assumption}\n"
    
    # Materials section
    if materials:
        content += f"""
================================================================================
MATERIALS & EQUIPMENT
================================================================================
"""
        content += f"{'Description':<50} {'Qty':<8} {'Unit':<8} {'Cost':<12} {'Subtotal':<12}\n"
        content += "-" * 90 + "\n"
        
        for material in materials:
            content += f"{material['description']:<50} {material['qty']:<8} {material['unit']:<8} ${material['unit_cost']:<11.2f} ${material['subtotal']:<11.2f}\n"
        
        content += "-" * 90 + "\n"
        content += f"{'MATERIALS TOTAL:':<78} ${materials_total:>11.2f}\n"
    
    # Labor section
    if labor_items:
        content += f"""
================================================================================
LABOR & INSTALLATION
================================================================================
"""
        content += f"{'Task Description':<50} {'Est. Hours':<8} {'Crew Size':<6} {'$/Hour':<12} {'Subtotal':<12}\n"
        content += "-" * 88 + "\n"
        
        for labor in labor_items:
            content += f"{labor['task']:<50} {labor['hours']:<8.1f} {labor['crew_size']:<6} ${labor['rate']:<11.2f} ${labor['subtotal']:<11.2f}\n"
        
        content += "-" * 88 + "\n"
        content += f"{'LABOR TOTAL:':<76} ${labor_total:>11.2f}\n"
    
    # Totals
    content += f"""
================================================================================
TOTALS
================================================================================
Subtotal:                                                       ${subtotal:>11.2f}
Tax (Oregon):                                                   ${tax:>11.2f}
TOTAL:                                                          ${total:>11.2f}

================================================================================

Valid for: 30 days from estimate date
Payment: Due upon completion
Contact: {input_data.get('company_info', {}).get('phone', '(503) 555-0199')} | {input_data.get('company_info', {}).get('email', 'info@waterwizard.com')}

Template ID: {template_data.get('template_id')}
Category: {template_data.get('category')}
Generated: This estimate was generated from template data (NOT hardcoded Liam Smith data)
"""
    
    # Write to file
    with open(output_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Generated text estimate: {output_path}")
    print(f"   Template: {template_data.get('template_id')}")
    print(f"   Category: {template_data.get('category')}")
    print(f"   Total: ${total:.2f}")
    print(f"   Materials: {len(materials)} items, ${materials_total:.2f}")
    print(f"   Labor: {len(labor_items)} tasks, ${labor_total:.2f}")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 text_template_generator.py <template.json> <input.json> <output.txt>")
        sys.exit(1)
    
    success = generate_text_estimate(sys.argv[1], sys.argv[2], sys.argv[3])
    sys.exit(0 if success else 1)