#!/usr/bin/env python3
"""
Template Validation Script for Squirt 1.2
Generates and visually validates all estimate templates
"""

import os
import json
import subprocess
import time
from pathlib import Path

class TemplateValidator:
    def __init__(self):
        self.base_dir = Path('/home/johnny5/Squirt')
        self.templates_dir = self.base_dir / 'templates' / 'estimates'
        self.validation_dir = self.base_dir / 'test_validation_samples'
        self.validation_dir.mkdir(exist_ok=True)
        
        # Sample input data
        self.sample_input = {
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
        
    def find_all_templates(self):
        """Find all JSON templates"""
        templates = []
        for root, dirs, files in os.walk(self.templates_dir):
            for file in files:
                if file.endswith('.json'):
                    templates.append(Path(root) / file)
        return sorted(templates)
    
    def generate_sample(self, template_path):
        """Generate a sample estimate from template"""
        template_name = template_path.stem
        input_file = self.validation_dir / f"{template_name}_input.json"
        output_file = self.validation_dir / f"{template_name}.odt"
        
        # Write sample input
        with open(input_file, 'w') as f:
            json.dump(self.sample_input, f, indent=2)
        
        try:
            # Generate estimate using UNO generator
            cmd = [
                'python3', 
                str(self.base_dir / 'src' / 'uno_estimate_generator.py'),
                str(template_path),
                str(input_file),
                '--output', str(output_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.base_dir, timeout=45)
            
            if result.returncode == 0:
                # Copy from default location if needed
                default_output = Path('/tmp/liam_smith_uno_estimate.odt')
                if default_output.exists() and not output_file.exists():
                    subprocess.run(['cp', str(default_output), str(output_file)])
                return True, "Success"
            else:
                return False, f"Error: {result.stderr}"
                
        except Exception as e:
            return False, f"Exception: {str(e)}"
    
    def validate_all_templates(self):
        """Generate samples for all templates"""
        templates = self.find_all_templates()
        results = []
        
        print(f"🔍 Found {len(templates)} templates to validate")
        print("=" * 60)
        
        for i, template_path in enumerate(templates, 1):
            template_name = template_path.stem
            print(f"[{i:2d}/{len(templates):2d}] Processing: {template_name}")
            
            success, message = self.generate_sample(template_path)
            results.append({
                'template': template_name,
                'path': str(template_path),
                'success': success,
                'message': message
            })
            
            status = "✅" if success else "❌"
            print(f"         {status} {message}")
            
            # Small delay to avoid overwhelming the system
            time.sleep(1)
        
        # Summary
        successful = sum(1 for r in results if r['success'])
        print("=" * 60)
        print(f"📊 VALIDATION SUMMARY: {successful}/{len(results)} templates generated successfully")
        
        if successful < len(results):
            print("\n❌ Failed templates:")
            for r in results:
                if not r['success']:
                    print(f"   - {r['template']}: {r['message']}")
        
        return results

if __name__ == "__main__":
    validator = TemplateValidator()
    results = validator.validate_all_templates()