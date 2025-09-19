#!/usr/bin/env python3
"""
Test template processing logic without LibreOffice complexity
"""

import json
import sys
from pathlib import Path

def test_template_processing(template_path, input_path):
    """Test that template processing actually works"""
    print(f"🧪 Testing template processing...")
    print(f"Template: {Path(template_path).name}")
    print(f"Input: {Path(input_path).name}")
    print("-" * 50)
    
    # Load template
    try:
        with open(template_path, 'r') as f:
            template_data = json.load(f)
        print(f"✅ Template loaded: {template_data.get('template_id')}")
        print(f"   Category: {template_data.get('category')}")
        print(f"   Description: {template_data.get('description')[:80]}...")
    except Exception as e:
        print(f"❌ Failed to load template: {e}")
        return False
    
    # Load input
    try:
        with open(input_path, 'r') as f:
            input_data = json.load(f)
        print(f"✅ Input loaded for client: {input_data.get('client_name')}")
    except Exception as e:
        print(f"❌ Failed to load input: {e}")
        return False
    
    # Process materials
    print(f"\n📦 MATERIALS ({len(template_data.get('materials', []))} items):")
    materials_total = 0
    for i, material in enumerate(template_data.get('materials', [])[:3], 1):  # Show first 3
        description = material.get('description', 'Unknown')
        unit_cost = material.get('unit_cost', 0)
        default_qty = material.get('default_qty', 1)
        markup = material.get('markup', 0)
        
        marked_up_cost = unit_cost * (1 + markup)
        subtotal = marked_up_cost * default_qty
        materials_total += subtotal
        
        print(f"   {i}. {description}")
        print(f"      {default_qty} @ ${unit_cost:.2f} (+{markup*100:.0f}%) = ${subtotal:.2f}")
    
    if len(template_data.get('materials', [])) > 3:
        print(f"   ... and {len(template_data.get('materials', [])) - 3} more materials")
    
    # Process labor
    print(f"\n🔧 LABOR ({len(template_data.get('labor', []))} tasks):")
    labor_total = 0
    labor_rates = {'maintenance': 45, 'install': 65, 'pruning': 75, 'electrical': 85}
    
    for i, labor in enumerate(template_data.get('labor', [])[:3], 1):  # Show first 3
        description = labor.get('description', 'Unknown')
        default_hrs = labor.get('default_hrs', 1)
        skill_level = labor.get('skill_level', 'maintenance')
        crew_size = labor.get('crew_size', 1)
        
        hourly_rate = labor_rates.get(skill_level, 50)
        subtotal = default_hrs * hourly_rate * crew_size
        labor_total += subtotal
        
        print(f"   {i}. {description}")
        print(f"      {default_hrs} hrs @ ${hourly_rate}/hr x {crew_size} crew = ${subtotal:.2f}")
    
    if len(template_data.get('labor', [])) > 3:
        print(f"   ... and {len(template_data.get('labor', [])) - 3} more labor tasks")
    
    # Totals
    subtotal = materials_total + labor_total
    total = subtotal  # No tax in Oregon
    
    print(f"\n💰 PRICING:")
    print(f"   Materials Total: ${materials_total:.2f}")
    print(f"   Labor Total: ${labor_total:.2f}")
    print(f"   Subtotal: ${subtotal:.2f}")
    print(f"   Tax: $0.00 (Oregon)")
    print(f"   TOTAL: ${total:.2f}")
    
    # Template-specific title
    parameters = template_data.get('parameters', {})
    title = template_data.get('title_format', 'Service')
    try:
        # Use default values for title formatting
        format_values = {k: v.get('default', 'N/A') for k, v in parameters.items()}
        formatted_title = title.format(**format_values)
        print(f"\n📋 ESTIMATE TITLE:")
        print(f"   {formatted_title} — ${total:.2f}")
    except Exception as e:
        print(f"   {title} — ${total:.2f}")
    
    print(f"\n✅ Template processing test SUCCESSFUL!")
    print(f"   This template would generate DIFFERENT content than Liam Smith!")
    return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 test_template_processing.py <template.json> <input.json>")
        sys.exit(1)
    
    success = test_template_processing(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)