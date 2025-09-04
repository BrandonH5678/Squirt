#!/usr/bin/env python3
"""
WaterWizard Document Validator
Comprehensive validation system for document quality, accuracy, and completeness
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Any, Tuple, Optional
import re
from datetime import datetime

class DocumentValidator:
    def __init__(self):
        """Initialize document validator with validation rules"""
        self.required_sections = [
            'prepared_by', 'prepared_for', 'project_description',
            'line_items', 'subtotal', 'tax_amount', 'total',
            'terms', 'signature_blocks'
        ]
        
        self.price_ranges = {
            # Element type -> (min_price, max_price, description)
            'valve_1inch': (30.0, 80.0, "1-inch irrigation valve"),
            'sprinkler_head_prs45': (5.0, 15.0, "PRS-45 spray head"),
            'pvc_pipe_1inch': (1.0, 5.0, "1-inch PVC pipe per foot"),
            'trenching': (1.0, 15.0, "trenching per foot"),
            'valve_install': (50.0, 150.0, "valve installation"),
            'head_install': (15.0, 50.0, "sprinkler head installation")
        }
        
        self.tax_rate_range = (0.06, 0.12)  # 6% to 12% sales tax range
        
    def validate_document_structure(self, document_data: Dict[str, Any]) -> List[str]:
        """Validate that required document sections are present"""
        errors = []
        
        # Check for required sections
        missing_sections = []
        for section in self.required_sections:
            if section not in document_data or not document_data[section]:
                missing_sections.append(section)
        
        if missing_sections:
            errors.append(f"Missing required sections: {', '.join(missing_sections)}")
        
        # Check client information completeness
        client_info = document_data.get('client_info', {})
        required_client_fields = ['name', 'address']
        missing_client_fields = [field for field in required_client_fields 
                                if not client_info.get(field)]
        
        if missing_client_fields:
            errors.append(f"Missing client information: {', '.join(missing_client_fields)}")
        
        # Check project information
        project_info = document_data.get('project_info', {})
        if not project_info.get('name'):
            errors.append("Missing project name")
        
        return errors
    
    def validate_mathematical_accuracy(self, line_items: List[Dict[str, Any]], 
                                     subtotal: float, tax_amount: float, 
                                     total: float, tax_rate: float = 0.0875) -> List[str]:
        """Validate mathematical calculations for accuracy"""
        errors = []
        tolerance = Decimal('0.01')  # 1 cent tolerance
        
        # Convert to Decimal for precise calculations
        subtotal_decimal = Decimal(str(subtotal))
        tax_amount_decimal = Decimal(str(tax_amount))
        total_decimal = Decimal(str(total))
        tax_rate_decimal = Decimal(str(tax_rate))
        
        # 1. Validate line item calculations
        line_item_errors = 0
        for i, item in enumerate(line_items):
            qty = Decimal(str(item.get('quantity', 0)))
            rate = Decimal(str(item.get('unit_rate', 0)))
            line_total = Decimal(str(item.get('line_total', 0)))
            
            expected_total = (qty * rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            if abs(line_total - expected_total) > tolerance:
                errors.append(
                    f"Line item {i+1} calculation error: "
                    f"{qty} × ${rate} should equal ${expected_total}, got ${line_total}"
                )
                line_item_errors += 1
        
        if line_item_errors > 0:
            errors.append(f"Found {line_item_errors} line item calculation errors")
        
        # 2. Validate subtotal = sum of line items
        calculated_subtotal = sum(Decimal(str(item.get('line_total', 0))) for item in line_items)
        calculated_subtotal = calculated_subtotal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        if abs(subtotal_decimal - calculated_subtotal) > tolerance:
            errors.append(
                f"Subtotal error: sum of line items = ${calculated_subtotal}, "
                f"but subtotal shows ${subtotal_decimal}"
            )
        
        # 3. Validate tax calculation
        expected_tax = (calculated_subtotal * tax_rate_decimal).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        if abs(tax_amount_decimal - expected_tax) > tolerance:
            errors.append(
                f"Tax calculation error: ${calculated_subtotal} × {tax_rate_decimal} = ${expected_tax}, "
                f"but tax shows ${tax_amount_decimal}"
            )
        
        # 4. Validate total = subtotal + tax
        expected_total = calculated_subtotal + expected_tax
        
        if abs(total_decimal - expected_total) > tolerance:
            errors.append(
                f"Total error: ${calculated_subtotal} + ${expected_tax} = ${expected_total}, "
                f"but total shows ${total_decimal}"
            )
        
        return errors
    
    def validate_price_reasonableness(self, line_items: List[Dict[str, Any]]) -> List[str]:
        """Check for price outliers and unusual quantities"""
        warnings = []
        
        for i, item in enumerate(line_items):
            element_id = item.get('element_id', '')
            unit_rate = float(item.get('unit_rate', 0))
            quantity = float(item.get('quantity', 0))
            line_total = float(item.get('line_total', 0))
            description = item.get('description', 'Unknown item')
            
            # Check unit price ranges
            if element_id in self.price_ranges:
                min_price, max_price, desc = self.price_ranges[element_id]
                
                if unit_rate < min_price:
                    warnings.append(
                        f"Line {i+1} ({description}): Unit price ${unit_rate:.2f} seems low "
                        f"for {desc} (typical range: ${min_price:.2f}-${max_price:.2f})"
                    )
                elif unit_rate > max_price:
                    warnings.append(
                        f"Line {i+1} ({description}): Unit price ${unit_rate:.2f} seems high "
                        f"for {desc} (typical range: ${min_price:.2f}-${max_price:.2f})"
                    )
            
            # Check for unusual quantities
            if element_id == 'sprinkler_head_prs45' and quantity > 50:
                warnings.append(f"Line {i+1}: Large quantity of spray heads ({quantity}) - verify count")
            elif element_id == 'trenching' and quantity > 500:
                warnings.append(f"Line {i+1}: Extensive trenching ({quantity} ft) - verify footage")
            elif element_id == 'valve_1inch' and quantity > 20:
                warnings.append(f"Line {i+1}: Many valves ({quantity}) - verify count")
            
            # Check for very large line totals
            if line_total > 5000:
                warnings.append(f"Line {i+1}: High line total (${line_total:.2f}) - verify calculation")
        
        return warnings
    
    def validate_format_consistency(self, document_content: str) -> List[str]:
        """Validate document formatting and consistency"""
        errors = []
        
        # Check for proper currency formatting
        currency_pattern = r'\$\d{1,3}(?:,\d{3})*\.\d{2}'
        improper_currency = re.findall(r'\$\d+(?:\.\d{1})?[^\d\.]', document_content)
        
        if improper_currency:
            errors.append(f"Inconsistent currency formatting found: {improper_currency[:3]}")
        
        # Check for required text sections
        required_text = [
            'WATERWIZARD', 'CONTRACT', 'INVOICE', 'PREPARED FOR', 'PREPARED BY',
            'SUBTOTAL', 'TAX', 'TOTAL'
        ]
        
        missing_text = []
        for text in required_text:
            if text not in document_content.upper():
                missing_text.append(text)
        
        if missing_text:
            errors.append(f"Missing required text elements: {', '.join(missing_text)}")
        
        # Check for signature blocks
        if 'Customer:' not in document_content or 'Date:' not in document_content:
            errors.append("Missing signature blocks")
        
        return errors
    
    def validate_tax_rate(self, tax_amount: float, subtotal: float) -> List[str]:
        """Validate tax rate is within reasonable range"""
        warnings = []
        
        if subtotal > 0:
            calculated_rate = tax_amount / subtotal
            min_rate, max_rate = self.tax_rate_range
            
            if calculated_rate < min_rate:
                warnings.append(
                    f"Tax rate ({calculated_rate:.1%}) seems low "
                    f"(typical range: {min_rate:.1%}-{max_rate:.1%})"
                )
            elif calculated_rate > max_rate:
                warnings.append(
                    f"Tax rate ({calculated_rate:.1%}) seems high "
                    f"(typical range: {min_rate:.1%}-{max_rate:.1%})"
                )
        
        return warnings
    
    def comprehensive_validation(self, document_data: Dict[str, Any], 
                               document_content: str = "") -> Dict[str, List[str]]:
        """Run all validation checks and return results"""
        results = {
            'critical_errors': [],
            'math_errors': [],
            'format_errors': [],
            'price_warnings': [],
            'tax_warnings': [],
            'overall_status': 'UNKNOWN'
        }
        
        # 1. Document structure validation
        structure_errors = self.validate_document_structure(document_data)
        results['critical_errors'].extend(structure_errors)
        
        # 2. Mathematical validation
        line_items = document_data.get('line_items', [])
        subtotal = float(document_data.get('subtotal', 0))
        tax_amount = float(document_data.get('tax_amount', 0))
        total = float(document_data.get('total', 0))
        tax_rate = float(document_data.get('tax_rate', 0.0875))
        
        if line_items:
            math_errors = self.validate_mathematical_accuracy(
                line_items, subtotal, tax_amount, total, tax_rate
            )
            results['math_errors'].extend(math_errors)
            
            # Price reasonableness check
            price_warnings = self.validate_price_reasonableness(line_items)
            results['price_warnings'].extend(price_warnings)
        
        # 3. Format validation
        if document_content:
            format_errors = self.validate_format_consistency(document_content)
            results['format_errors'].extend(format_errors)
        
        # 4. Tax rate validation
        tax_warnings = self.validate_tax_rate(tax_amount, subtotal)
        results['tax_warnings'].extend(tax_warnings)
        
        # 5. Overall status determination
        total_errors = (len(results['critical_errors']) + 
                       len(results['math_errors']) + 
                       len(results['format_errors']))
        
        if total_errors == 0:
            results['overall_status'] = 'PASS'
        elif total_errors <= 2 and not results['critical_errors']:
            results['overall_status'] = 'PASS_WITH_WARNINGS'
        else:
            results['overall_status'] = 'FAIL'
        
        return results
    
    def generate_validation_report(self, validation_results: Dict[str, List[str]], 
                                 project_name: str = "Unknown Project") -> str:
        """Generate a formatted validation report"""
        report = f"""
WATERWIZARD VALIDATION REPORT
========================================
Project: {project_name}
Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
Status: {validation_results['overall_status']}

"""
        
        # Critical errors
        if validation_results['critical_errors']:
            report += "🚨 CRITICAL ERRORS:\n"
            for error in validation_results['critical_errors']:
                report += f"   • {error}\n"
            report += "\n"
        
        # Math errors
        if validation_results['math_errors']:
            report += "🧮 MATHEMATICAL ERRORS:\n"
            for error in validation_results['math_errors']:
                report += f"   • {error}\n"
            report += "\n"
        
        # Format errors
        if validation_results['format_errors']:
            report += "📄 FORMAT ERRORS:\n"
            for error in validation_results['format_errors']:
                report += f"   • {error}\n"
            report += "\n"
        
        # Price warnings
        if validation_results['price_warnings']:
            report += "💰 PRICE WARNINGS:\n"
            for warning in validation_results['price_warnings']:
                report += f"   • {warning}\n"
            report += "\n"
        
        # Tax warnings
        if validation_results['tax_warnings']:
            report += "🏛️ TAX WARNINGS:\n"
            for warning in validation_results['tax_warnings']:
                report += f"   • {warning}\n"
            report += "\n"
        
        # Summary
        total_issues = sum(len(issues) for issues in validation_results.values() 
                          if isinstance(issues, list))
        
        if validation_results['overall_status'] == 'PASS':
            report += "✅ VALIDATION PASSED - Document ready for client presentation\n"
        elif validation_results['overall_status'] == 'PASS_WITH_WARNINGS':
            report += f"⚠️ PASSED WITH {total_issues} WARNINGS - Review recommended\n"
        else:
            report += f"❌ VALIDATION FAILED - {total_issues} issues require attention\n"
        
        report += "========================================\n"
        
        return report

def main():
    """Demo the validation system"""
    validator = DocumentValidator()
    
    print("🔍 WATERWIZARD DOCUMENT VALIDATOR")
    print("=" * 50)
    
    # Test with sample document data
    sample_document = {
        'client_info': {'name': 'Smith Family', 'address': '123 Oak St'},
        'project_info': {'name': 'Sprinkler Installation'},
        'prepared_by': 'WaterWizard Irrigation',
        'prepared_for': 'Smith Family',
        'project_description': 'Install new sprinkler zone',
        'line_items': [
            {'element_id': 'valve_1inch', 'quantity': 1, 'unit_rate': 45.00, 'line_total': 45.00, 'description': 'Control valve'},
            {'element_id': 'sprinkler_head_prs45', 'quantity': 6, 'unit_rate': 8.50, 'line_total': 51.00, 'description': 'Spray heads'},
            {'element_id': 'trenching', 'quantity': 100, 'unit_rate': 3.00, 'line_total': 300.00, 'description': 'Hand trenching'}
        ],
        'subtotal': 396.00,
        'tax_amount': 34.65,
        'total': 430.65,
        'tax_rate': 0.0875,
        'terms': 'Payment due upon completion',
        'signature_blocks': 'Customer signature required'
    }
    
    sample_content = """
    WATERWIZARD IRRIGATION
    PROFESSIONAL INSTALLATION CONTRACT
    PREPARED FOR: Smith Family
    PREPARED BY: WaterWizard Irrigation
    SUBTOTAL: $396.00
    TAX (8.75%): $34.65
    TOTAL: $430.65
    Customer: _________________ Date: _______
    """
    
    # Run validation
    results = validator.comprehensive_validation(sample_document, sample_content)
    
    # Generate report
    report = validator.generate_validation_report(results, "Smith Family Sprinkler Installation")
    print(report)

if __name__ == "__main__":
    main()