#!/usr/bin/env python3
"""
Batch Template Generator for All 17 Templates
Generates professional ODT estimates from all template files using working HTML-to-ODT process
"""

import os
import sys
import subprocess
from pathlib import Path

sys.path.append('/home/johnny5/Squirt/src')
from html_to_odt_generator import HtmlToOdtGenerator

def find_all_templates():
    """Find all template JSON files"""
    templates_dir = Path('/home/johnny5/Squirt/templates/estimates')
    templates = []
    
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.json'):
                templates.append(Path(root) / file)
    
    return sorted(templates)

def generate_batch_estimates():
    """Generate ODT estimates for all templates"""
    templates = find_all_templates()
    input_file = '/home/johnny5/Squirt/test_validation_samples/sample_input_basic.json'
    output_dir = Path('/home/johnny5/Squirt/test_validation_samples')
    
    print(f"🎯 BATCH TEMPLATE GENERATOR")
    print(f"Found {len(templates)} templates")
    print(f"Input: {input_file}")
    print(f"Output: {output_dir}")
    print("=" * 60)
    
    generator = HtmlToOdtGenerator()
    results = []
    
    for i, template_path in enumerate(templates, 1):
        template_name = template_path.stem
        html_file = output_dir / f"BATCH_{template_name}.html"
        odt_file = output_dir / f"BATCH_{template_name}.odt"
        
        print(f"\n[{i:2d}/{len(templates)}] Processing: {template_name}")
        
        try:
            # Load template and generate HTML
            if not generator.load_files(str(template_path), input_file):
                results.append((template_name, "❌ FAILED - Load error"))
                continue
            
            materials, labor, equipment = generator.calculate_costs()
            html_content, total = generator.create_professional_html(materials, labor, equipment)
            
            # Save HTML
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Convert to ODT using LibreOffice
            cmd = [
                'libreoffice', '--headless', '--convert-to', 'odt',
                '--outdir', str(output_dir),
                str(html_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and odt_file.exists():
                results.append((template_name, f"✅ SUCCESS - ${total:.2f}"))
                print(f"    ✅ Generated: ${total:.2f}")
            else:
                results.append((template_name, "❌ FAILED - Conversion error"))
                print(f"    ❌ LibreOffice conversion failed")
                
        except Exception as e:
            results.append((template_name, f"❌ FAILED - {str(e)[:30]}"))
            print(f"    ❌ Error: {e}")
    
    # Summary report
    print("\n" + "=" * 60)
    print("📊 BATCH GENERATION SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for _, status in results if status.startswith("✅"))
    failed = len(results) - successful
    
    print(f"Total templates: {len(results)}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print()
    
    for template_name, status in results:
        print(f"{template_name:35} | {status}")
    
    if successful > 0:
        print(f"\n🎯 SUCCESS: Generated {successful} professional ODT estimates!")
        print(f"Output files: test_validation_samples/BATCH_*.odt")
    else:
        print(f"\n❌ CRITICAL: No templates generated successfully!")
    
    return successful == len(results)

if __name__ == "__main__":
    success = generate_batch_estimates()
    sys.exit(0 if success else 1)