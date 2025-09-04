#!/usr/bin/env python3
"""
Generate a comprehensive sample invoice to demonstrate WaterWizard templates
"""

import sys
sys.path.append('src')
from document_generator import DocumentGenerator
from csv_exporter import CSVExporter
from datetime import datetime
from decimal import Decimal

def generate_comprehensive_sample():
    """Generate a realistic mixed-service invoice"""
    
    generator = DocumentGenerator()
    exporter = CSVExporter()
    
    # Realistic client
    client = {
        "name": "Rodriguez Family Trust",
        "address": "2847 Maple Ridge Drive",
        "city": "Cedar Park", 
        "state": "TX",
        "zip": "78613",
        "phone": "(512) 555-7834",
        "email": "mrodriguez@email.com"
    }
    
    project = {
        "name": "Front Yard Irrigation Repair & New Zone Installation",
        "address": "2847 Maple Ridge Drive, Cedar Park, TX"
    }
    
    # Mixed service scenario: repair work + new installation
    templates = [
        # Repair: Replace 5 broken heads with swing joints and minor pipe repair
        ("src/templates/head_replacement.json", {
            "head_count": 5,
            "head_type": "spray",
            "swing_joint_needed": True,
            "pipe_repair": True
        }),
        
        # New installation: Zone 3 in rocky soil (challenging conditions)
        ("src/templates/sprinkler_zone.json", {
            "zone_number": 3,
            "head_count": 7,
            "trench_feet": 185,
            "soil_type": "rocky"  # More expensive soil type
        }),
        
        # Additional trenching for connecting to main line
        ("src/templates/trenching.json", {
            "trench_feet": 35,
            "soil_type": "roots",  # Tree root obstacles
            "depth": "standard"
        }),
        
        # Valve manifold installation (3 valves in one box - cost savings)
        ("src/templates/valve_install.json", {
            "valve_count": 3,
            "valve_size": "1inch",
            "manifold": True,  # Should save money vs separate boxes
            "wiring_feet": 75
        })
    ]
    
    print("🏠 COMPREHENSIVE WATERWIZARD INVOICE DEMONSTRATION")
    print("="*60)
    print(f"📅 Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    print(f"🎯 Scenario: Mixed repair/installation project with challenging conditions")
    print("\n🔍 MATHEMATICAL VERIFICATION:")
    
    # Process each template and show breakdown
    all_line_items = []
    total_subtotal = 0
    template_totals = []
    
    print("\n" + "="*60)
    
    for i, (template_path, params) in enumerate(templates, 1):
        result = generator.processor.process_template(template_path, params)
        template_name = result['template_name']
        template_subtotal = result['subtotal']
        
        print(f"\n{i}️⃣ {template_name.upper()}")
        print("-" * 40)
        print(f"Parameters: {params}")
        print(f"Subtotal: ${template_subtotal:.2f}")
        
        # Show key calculations
        if "soil_type" in params:
            soil = params["soil_type"]
            if soil != "turf":
                print(f"🌱 Soil modifier applied: {soil} soil")
        
        if "manifold" in params and params["manifold"]:
            print("📦 Manifold savings: 3 valves using 1 box instead of 3")
            
        if "swing_joint_needed" in params and params["swing_joint_needed"]:
            print("🔧 Premium repair: Includes swing joints & pipe repair")
        
        all_line_items.extend(result['line_items'])
        total_subtotal += template_subtotal
        template_totals.append((template_name, template_subtotal))
    
    # Calculate final totals
    tax_rate = generator.tax_rate
    total_subtotal = Decimal(str(total_subtotal))
    tax_amount = (total_subtotal * tax_rate).quantize(Decimal('0.01'))
    grand_total = total_subtotal + tax_amount
    
    print("\n" + "="*60)
    print("💰 COST BREAKDOWN BY SERVICE:")
    for name, amount in template_totals:
        percentage = (float(amount) / float(total_subtotal)) * 100
        print(f"  {name:<35} ${amount:>8.2f} ({percentage:>5.1f}%)")
    
    print(f"\n{'SUBTOTAL:':<35} ${float(total_subtotal):>8.2f}")
    print(f"{'TAX (8.75%):':<35} ${float(tax_amount):>8.2f}")
    print(f"{'GRAND TOTAL:':<35} ${float(grand_total):>8.2f}")
    
    print("\n🧮 MATHEMATICAL ACCURACY CHECK:")
    manual_total = sum(item['line_total'] for item in all_line_items)
    print(f"  Sum of line items: ${manual_total:.2f}")
    print(f"  Template subtotal: ${float(total_subtotal):.2f}")
    print(f"  ✅ Match: {'YES' if abs(manual_total - float(total_subtotal)) < 0.01 else 'NO'}")
    
    # Generate the full invoice
    invoice = generator.generate_invoice(client, project, templates)
    
    print("\n" + "="*60)
    print("📄 PROFESSIONAL INVOICE OUTPUT:")
    print("="*60)
    print(invoice)
    
    # Generate CSV for QuickBooks
    invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-DEMO"
    csv_content = exporter.export_invoice_to_csv(
        client, project, all_line_items, 
        total_subtotal, tax_amount, grand_total, invoice_number
    )
    
    print("\n" + "="*60)
    print("📊 QUICKBOOKS CSV EXPORT (First 5 lines):")
    print("="*60)
    lines = csv_content.strip().split('\n')
    for line in lines[:6]:  # Header + 5 data lines
        print(line)
    print(f"... ({len(lines)-1} total data rows)")
    
    # Save files
    date_suffix = datetime.now().strftime('%Y%m%d_%H%M')
    invoice_file = f"sample_invoice_{date_suffix}.txt"
    csv_file = f"sample_invoice_{date_suffix}.csv"
    
    with open(invoice_file, 'w') as f:
        f.write(invoice)
    
    with open(csv_file, 'w') as f:
        f.write(csv_content)
    
    print(f"\n📁 FILES SAVED:")
    print(f"  Invoice: {invoice_file}")
    print(f"  CSV:     {csv_file}")
    
    return {
        'subtotal': float(total_subtotal),
        'tax': float(tax_amount), 
        'total': float(grand_total),
        'line_items': len(all_line_items),
        'templates_used': len(templates)
    }

if __name__ == "__main__":
    result = generate_comprehensive_sample()
    
    print(f"\n✅ DEMONSTRATION COMPLETE")
    print(f"   Templates: {result['templates_used']} different services")
    print(f"   Line items: {result['line_items']} detailed charges")
    print(f"   Total value: ${result['total']:.2f}")
    print(f"   Ready for: Client presentation & QuickBooks import")