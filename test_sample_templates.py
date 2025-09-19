#!/usr/bin/env python3
"""
Test a few sample templates to ensure the system works
"""

import os
import json
import subprocess
from pathlib import Path

def test_templates():
    base_dir = Path('/home/johnny5/Squirt')
    validation_dir = base_dir / 'test_validation_samples'
    validation_dir.mkdir(exist_ok=True)
    
    # Sample input data
    sample_input = {
        "client_name": "Test Client",
        "property_address": "123 Test Street, Portland, OR 97205", 
        "estimate_date": "2025-01-04",
        "project_description": "Template validation test",
        "contact_info": {
            "phone": "(503) 555-0123",
            "email": "test@example.com"
        },
        "company_info": {
            "name": "WaterWizard Irrigation & Landscape",
            "license": "CCB #12345", 
            "phone": "(503) 555-0199",
            "email": "info@waterwizard.com"
        }
    }
    
    # Test these templates first
    test_templates = [
        'templates/estimates/lighting/path_lighting_economy.json',
        'templates/estimates/irrigation_zone/sprinkler_zone_turf.json',
        'templates/estimates/mulching/mulch_bed_refresh.json',
        'templates/estimates/maintenance/fall_cleanup_comprehensive.json',
        'templates/estimates/planting/native_plant_installation.json'
    ]
    
    results = []
    
    for template_path in test_templates:
        template_name = Path(template_path).stem
        print(f"Testing: {template_name}")
        
        input_file = validation_dir / f"{template_name}_input.json"
        
        # Write sample input
        with open(input_file, 'w') as f:
            json.dump(sample_input, f, indent=2)
        
        try:
            cmd = [
                'python3', 
                str(base_dir / 'src' / 'uno_estimate_generator.py'),
                str(base_dir / template_path),
                str(input_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=base_dir, timeout=30)
            
            if result.returncode == 0:
                # Copy from default location
                default_output = Path('/tmp/liam_smith_uno_estimate.odt')
                target_output = validation_dir / f"{template_name}.odt"
                if default_output.exists():
                    subprocess.run(['cp', str(default_output), str(target_output)])
                    print(f"✅ Success: {template_name}")
                    results.append((template_name, True, "Generated successfully"))
                else:
                    print(f"⚠️  Generated but no output found: {template_name}")
                    results.append((template_name, False, "No output file"))
            else:
                print(f"❌ Failed: {template_name} - {result.stderr[:100]}")
                results.append((template_name, False, result.stderr[:100]))
                
        except Exception as e:
            print(f"❌ Exception: {template_name} - {str(e)}")
            results.append((template_name, False, str(e)))
    
    # Summary
    successful = sum(1 for _, success, _ in results if success)
    print(f"\n📊 Test Results: {successful}/{len(results)} templates generated successfully")
    
    return results

if __name__ == "__main__":
    test_templates()