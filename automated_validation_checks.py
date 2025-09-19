#!/usr/bin/env python3
"""
Automated Validation Checks for Generated Templates
Validates that generated estimates meet the validation expectations in templates
"""

import os
import json
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import re

class AutomatedValidator:
    def __init__(self):
        self.base_dir = Path('/home/johnny5/Squirt')
        self.templates_dir = self.base_dir / 'templates' / 'estimates'
        self.samples_dir = self.base_dir / 'test_validation_samples'
        self.validation_results = []
    
    def extract_odt_content(self, odt_path):
        """Extract text content from ODT file"""
        try:
            with zipfile.ZipFile(odt_path, 'r') as z:
                content_xml = z.read('content.xml')
                root = ET.fromstring(content_xml)
                
                # Extract all text elements
                text_content = []
                for elem in root.iter():
                    if elem.text:
                        text_content.append(elem.text.strip())
                
                return ' '.join(text_content)
        except Exception as e:
            return f"Error reading ODT: {str(e)}"
    
    def validate_currency_format(self, content):
        """Check for proper currency formatting"""
        currency_pattern = r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
        currency_matches = re.findall(currency_pattern, content)
        return len(currency_matches) > 0
    
    def validate_required_sections(self, content, required_sections):
        """Check if required sections are present"""
        missing_sections = []
        content_lower = content.lower()
        
        for section in required_sections:
            # Convert section names to searchable text
            search_terms = {
                'Materials & Equipment': ['materials', 'equipment'],
                'Labor & Installation': ['labor', 'installation'],
                'Subtotal': ['subtotal'],
                'Tax': ['tax'],
                'Total': ['total']
            }
            
            if section in search_terms:
                found = any(term in content_lower for term in search_terms[section])
                if not found:
                    missing_sections.append(section)
            else:
                if section.lower() not in content_lower:
                    missing_sections.append(section)
        
        return missing_sections
    
    def validate_company_info(self, content):
        """Check if company information is present"""
        checks = {
            'company_name': 'waterwizard' in content.lower(),
            'license_number': 'ccb' in content.lower(),
            'phone_number': re.search(r'\(\d{3}\)\s*\d{3}-\d{4}', content) is not None,
            'email': '@' in content
        }
        return checks
    
    def validate_template_and_output(self, template_path, output_path):
        """Validate a single template and its output"""
        template_name = template_path.stem
        
        # Load template
        try:
            with open(template_path, 'r') as f:
                template = json.load(f)
        except Exception as e:
            return {
                'template': template_name,
                'status': 'error',
                'message': f"Failed to load template: {str(e)}",
                'checks': {}
            }
        
        # Extract content from ODT
        if not output_path.exists():
            return {
                'template': template_name,
                'status': 'error', 
                'message': "Output file not found",
                'checks': {}
            }
        
        content = self.extract_odt_content(output_path)
        
        if content.startswith('Error'):
            return {
                'template': template_name,
                'status': 'error',
                'message': content,
                'checks': {}
            }
        
        # Run validation checks
        checks = {}
        
        # Basic format checks
        checks['currency_format'] = self.validate_currency_format(content)
        checks['company_info'] = self.validate_company_info(content)
        
        # Template-specific validation expectations
        if 'validation_expectations' in template:
            expectations = template['validation_expectations']
            
            # Required sections check
            if 'required_sections' in expectations:
                missing_sections = self.validate_required_sections(
                    content, expectations['required_sections']
                )
                checks['required_sections'] = {
                    'missing': missing_sections,
                    'passed': len(missing_sections) == 0
                }
            
            # Content length check (basic quality indicator)
            checks['content_length'] = {
                'length': len(content),
                'adequate': len(content) > 1000  # Minimum content expectation
            }
            
            # Template title/description presence
            if 'title_format' in template:
                title_words = template.get('description', '').split()[:3]
                checks['template_content'] = any(word.lower() in content.lower() for word in title_words if len(word) > 3)
        
        # Determine overall status
        critical_failures = []
        if not checks.get('currency_format', False):
            critical_failures.append("No currency formatting found")
        if not checks.get('company_info', {}).get('company_name', False):
            critical_failures.append("Company name missing")
        if not checks.get('content_length', {}).get('adequate', False):
            critical_failures.append("Content too short")
            
        status = 'passed' if len(critical_failures) == 0 else 'warning'
        
        return {
            'template': template_name,
            'status': status,
            'message': '; '.join(critical_failures) if critical_failures else "All checks passed",
            'checks': checks,
            'content_preview': content[:200] + "..." if len(content) > 200 else content
        }
    
    def run_all_validations(self):
        """Run validation on all templates"""
        print("🔍 Running automated validation checks on all generated templates")
        print("=" * 70)
        
        templates = list(self.templates_dir.glob('**/*.json'))
        
        for i, template_path in enumerate(templates, 1):
            template_name = template_path.stem
            output_path = self.samples_dir / f"{template_name}.odt"
            
            print(f"[{i:2d}/{len(templates):2d}] Validating: {template_name}")
            
            result = self.validate_template_and_output(template_path, output_path)
            self.validation_results.append(result)
            
            status_icon = {"passed": "✅", "warning": "⚠️", "error": "❌"}.get(result['status'], "?")
            print(f"         {status_icon} {result['message']}")
        
        # Summary
        passed = sum(1 for r in self.validation_results if r['status'] == 'passed')
        warnings = sum(1 for r in self.validation_results if r['status'] == 'warning')  
        errors = sum(1 for r in self.validation_results if r['status'] == 'error')
        
        print("=" * 70)
        print(f"📊 VALIDATION SUMMARY:")
        print(f"   ✅ Passed: {passed}")
        print(f"   ⚠️  Warnings: {warnings}")
        print(f"   ❌ Errors: {errors}")
        print(f"   📄 Total: {len(self.validation_results)}")
        
        # Detailed issues
        if warnings > 0 or errors > 0:
            print(f"\n⚠️  Issues Found:")
            for result in self.validation_results:
                if result['status'] in ['warning', 'error']:
                    print(f"   - {result['template']}: {result['message']}")
        
        return self.validation_results
    
    def save_validation_report(self, filename='validation_report.json'):
        """Save detailed validation report"""
        report_path = self.base_dir / filename
        with open(report_path, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        print(f"📄 Detailed report saved: {report_path}")

if __name__ == "__main__":
    validator = AutomatedValidator()
    results = validator.run_all_validations()
    validator.save_validation_report()