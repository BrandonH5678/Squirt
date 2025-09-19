#!/usr/bin/env python3

import sys
import os
sys.path.append('/home/johnny5/Squirt/src')

from html_to_odt_generator import HtmlToOdtGenerator

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 debug_html_only.py template.json input.json output.html")
        return
    
    template_path, input_path, output_path = sys.argv[1:4]
    
    gen = HtmlToOdtGenerator()
    if not gen.load_files(template_path, input_path):
        return
    
    materials, labor_items, equipment_items = gen.calculate_costs()
    html_content, total = gen.create_professional_html(materials, labor_items, equipment_items)
    
    print(f"💰 Calculated total: ${total:.2f}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML saved: {output_path}")
    
    # Quick verification
    if 'Test Client' in html_content and 'ProTrade PTH1' in html_content:
        print("✅ HTML contains template-specific content!")
    else:
        print("❌ HTML still has issues")

if __name__ == "__main__":
    main()