#!/usr/bin/env python3
"""
WaterWizard Document Generator
Generates professional contracts, invoices, and receipts from templates
"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
import json
from pathlib import Path
from template_processor import TemplateProcessor
from tax_rules import TaxRulesEngine
from format_converter import SquirtFormatConverter, DocumentType as FmtDocType, OutputFormat
from modern_html_document_generator import ModernHtmlDocumentGenerator

class DocumentGenerator:
    def __init__(self):
        self.processor = TemplateProcessor()
        self.tax_engine = TaxRulesEngine()
        self.format_converter = SquirtFormatConverter()
        self.default_tax_rate = Decimal("0.0875")  # 8.75% fallback rate
        
        # Use modern HTML>ODT generator for better reliability
        self.modern_generator = ModernHtmlDocumentGenerator()
        
    def generate_contract(self, client_info: dict, project_info: dict, templates_with_params: list) -> str:
        """Generate a professional contract document"""
        doc_number = f"WW-{datetime.now().strftime('%Y%m%d')}-001"
        
        # Process all templates
        all_line_items = []
        total_subtotal = Decimal("0")
        narratives = []
        
        for template_path, params in templates_with_params:
            result = self.processor.process_template(template_path, params)
            all_line_items.extend(result['line_items'])
            total_subtotal += Decimal(str(result['subtotal']))
            narratives.append(result['narrative'])
        
        # Calculate tax and total
        tax_amount = (total_subtotal * self.tax_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        grand_total = (total_subtotal + tax_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Generate contract document
        contract = self._format_contract(
            doc_number, client_info, project_info, all_line_items,
            total_subtotal, tax_amount, grand_total, narratives
        )
        
        return contract
    
    def generate_invoice(self, client_info: dict, project_info: dict, templates_with_params: list) -> str:
        """Generate a professional invoice document"""
        doc_number = f"INV-{datetime.now().strftime('%Y%m%d')}-001"
        
        # Process all templates  
        all_line_items = []
        total_subtotal = Decimal("0")
        
        for template_path, params in templates_with_params:
            result = self.processor.process_template(template_path, params)
            all_line_items.extend(result['line_items'])
            total_subtotal += Decimal(str(result['subtotal']))
        
        # Calculate tax and total
        tax_amount = (total_subtotal * self.tax_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        grand_total = (total_subtotal + tax_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Generate invoice document
        invoice = self._format_invoice(
            doc_number, client_info, project_info, all_line_items,
            total_subtotal, tax_amount, grand_total
        )
        
        return invoice
    
    def generate_contract_odt(self, client_info: dict, project_info: dict, 
                             templates_with_params: list, output_path: str) -> bool:
        """Generate a professional contract in ODT format using modern pipeline"""
        print(f"📄 Generating modern contract ODT...")
        
        try:
            success = self.modern_generator.generate_contract(
                client_info, project_info, templates_with_params, output_path
            )
            
            if success:
                print(f"✅ Modern contract ODT generated: {output_path}")
                return True
            else:
                print(f"❌ Modern contract ODT generation failed")
                return False
                
        except Exception as e:
            print(f"❌ Contract ODT generation error: {e}")
            return False
    
    def generate_invoice_odt(self, client_info: dict, project_info: dict,
                           templates_with_params: list, output_path: str) -> bool:
        """Generate a professional invoice in ODT format using modern pipeline"""
        print(f"📄 Generating modern invoice ODT...")
        
        try:
            success = self.modern_generator.generate_invoice(
                client_info, project_info, templates_with_params, output_path
            )
            
            if success:
                print(f"✅ Modern invoice ODT generated: {output_path}")
                return True
            else:
                print(f"❌ Modern invoice ODT generation failed")
                return False
                
        except Exception as e:
            print(f"❌ Invoice ODT generation error: {e}")
            return False
    
    def _format_contract(self, doc_number, client_info, project_info, line_items, 
                        subtotal, tax_amount, total, narratives):
        """Format a professional contract document"""
        
        date_str = datetime.now().strftime("%B %d, %Y")
        
        # Group line items by category for better presentation
        materials = [item for item in line_items if item['category'] == 'materials']
        equipment = [item for item in line_items if item['category'] == 'equipment'] 
        labor = [item for item in line_items if item['category'] == 'labor']
        
        contract = f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                           WATERWIZARD IRRIGATION                              ║
║                        Professional Installation Contract                      ║
╚═══════════════════════════════════════════════════════════════════════════════╝

CONTRACT NUMBER: {doc_number}
DATE: {date_str}

PREPARED FOR:                          PREPARED BY:
{client_info['name']}                           WaterWizard Irrigation & Landscape
{client_info['address']}                        Professional Irrigation Services
{client_info.get('city', '')}, {client_info.get('state', '')} {client_info.get('zip', '')}
Phone: {client_info.get('phone', 'N/A')}       Phone: (555) 123-4567
Email: {client_info.get('email', 'N/A')}       Email: info@waterwizard.com

PROJECT: {project_info['name']}
LOCATION: {project_info.get('address', client_info['address'])}

═════════════════════════════════════════════════════════════════════════════════

PROJECT DESCRIPTION:

{chr(10).join(narratives)}

═════════════════════════════════════════════════════════════════════════════════

MATERIALS & EQUIPMENT BREAKDOWN:

┌─────────────────────────────────────────────┬──────┬─────────┬─────────────┐
│ Description                                 │ Qty  │ Rate    │ Total       │
├─────────────────────────────────────────────┼──────┼─────────┼─────────────┤"""

        # Add materials
        if materials:
            contract += f"\n│ MATERIALS                                   │      │         │             │"
            for item in materials:
                desc = item['description'][:43]
                qty_str = f"{item['quantity']:.1f}"
                rate_str = f"${item['unit_rate']:.2f}"
                total_str = f"${item['line_total']:.2f}"
                contract += f"\n│ {desc:<43} │ {qty_str:>4} │ {rate_str:>7} │ {total_str:>11} │"
        
        # Add equipment
        if equipment:
            contract += f"\n│ EQUIPMENT                                   │      │         │             │"
            for item in equipment:
                desc = item['description'][:43]
                qty_str = f"{item['quantity']:.1f}"
                rate_str = f"${item['unit_rate']:.2f}"
                total_str = f"${item['line_total']:.2f}"
                contract += f"\n│ {desc:<43} │ {qty_str:>4} │ {rate_str:>7} │ {total_str:>11} │"
        
        # Add labor
        if labor:
            contract += f"\n│ LABOR                                       │      │         │             │"
            for item in labor:
                desc = item['description'][:43]
                qty_str = f"{item['quantity']:.1f}"
                rate_str = f"${item['unit_rate']:.2f}"
                total_str = f"${item['line_total']:.2f}"
                contract += f"\n│ {desc:<43} │ {qty_str:>4} │ {rate_str:>7} │ {total_str:>11} │"
        
        contract += f"""
├─────────────────────────────────────────────┴──────┴─────────┼─────────────┤
│                                              SUBTOTAL: │ ${subtotal:>11.2f} │
│                                    TAX ({self.tax_rate*100:.2f}%): │ ${tax_amount:>11.2f} │
│                                               TOTAL: │ ${total:>11.2f} │
└────────────────────────────────────────────────────────┴─────────────┘

TERMS AND CONDITIONS:

• Work includes 1-year warranty on installation workmanship
• Materials warranted per manufacturer specifications  
• Customer responsible for utility locates prior to work
• Payment due upon completion of work
• Weather delays may affect completion date
• Site access required for all work areas

ACCEPTANCE:

Customer: ________________________________    Date: _______________

WaterWizard Representative: ________________    Date: {date_str}

═════════════════════════════════════════════════════════════════════════════════
"""
        return contract
    
    def _format_invoice(self, doc_number, client_info, project_info, line_items,
                       subtotal, tax_amount, total):
        """Format a professional invoice document"""
        
        date_str = datetime.now().strftime("%B %d, %Y")
        
        invoice = f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                           WATERWIZARD IRRIGATION                              ║
║                              INVOICE                                          ║
╚═══════════════════════════════════════════════════════════════════════════════╝

INVOICE NUMBER: {doc_number}
DATE: {date_str}
DUE: Upon Receipt

BILL TO:                               FROM:
{client_info['name']}                           WaterWizard Irrigation & Landscape
{client_info['address']}                        Professional Irrigation Services  
{client_info.get('city', '')}, {client_info.get('state', '')} {client_info.get('zip', '')}
                                       Phone: (555) 123-4567
                                       Email: info@waterwizard.com

PROJECT: {project_info['name']}

═════════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────┬──────┬─────────┬─────────────┐
│ Description                                 │ Qty  │ Rate    │ Amount      │
├─────────────────────────────────────────────┼──────┼─────────┼─────────────┤"""

        for item in line_items:
            desc = item['description'][:43]
            qty_str = f"{item['quantity']:.1f} {item['unit']}"
            rate_str = f"${item['unit_rate']:.2f}"
            total_str = f"${item['line_total']:.2f}"
            invoice += f"\n│ {desc:<43} │ {qty_str:>4} │ {rate_str:>7} │ {total_str:>11} │"

        invoice += f"""
├─────────────────────────────────────────────┴──────┴─────────┼─────────────┤
│                                              SUBTOTAL: │ ${subtotal:>11.2f} │
│                                    TAX ({self.tax_rate*100:.2f}%): │ ${tax_amount:>11.2f} │
│                                        AMOUNT DUE: │ ${total:>11.2f} │
└────────────────────────────────────────────────────────┴─────────────┘

PAYMENT TERMS: Net 30 days
THANK YOU FOR YOUR BUSINESS!

═════════════════════════════════════════════════════════════════════════════════
"""
        return invoice
    
    def generate_contract_multiformat(self, client_info: dict, project_info: dict, 
                                    templates_with_params: list, 
                                    output_dir: str = ".", 
                                    formats: list = None) -> dict:
        """Generate contract in multiple client-preferred formats"""
        
        # Generate base contract
        contract_content = self.generate_contract(client_info, project_info, templates_with_params)
        
        # Save as text file first
        doc_number = f"WW-{datetime.now().strftime('%Y%m%d')}-001"
        base_filename = f"{client_info['name'].replace(' ', '_').lower()}_{doc_number.lower()}_contract"
        txt_path = f"{output_dir}/{base_filename}.txt"
        
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(contract_content)
        
        # Convert to client formats
        if formats is None:
            formats = self.format_converter.get_recommended_formats(FmtDocType.CONTRACT, "client")
        
        conversion_results = self.format_converter.convert_document(
            txt_path, FmtDocType.CONTRACT, formats, output_dir
        )
        
        results = {
            'content': contract_content,
            'base_file': txt_path,
            'formats': {fmt.value: path for fmt, path in conversion_results.items() if path},
            'client_ready': [fmt.value for fmt, path in conversion_results.items() if path and fmt in [OutputFormat.PDF, OutputFormat.DOCX]]
        }
        
        return results
    
    def generate_invoice_multiformat(self, client_info: dict, project_info: dict, 
                                   templates_with_params: list, 
                                   output_dir: str = ".", 
                                   formats: list = None) -> dict:
        """Generate invoice in multiple client-preferred formats"""
        
        # Generate base invoice
        invoice_content = self.generate_invoice(client_info, project_info, templates_with_params)
        
        # Save as text file first
        doc_number = f"INV-{datetime.now().strftime('%Y%m%d')}-001"
        base_filename = f"{client_info['name'].replace(' ', '_').lower()}_{doc_number.lower()}_invoice"
        txt_path = f"{output_dir}/{base_filename}.txt"
        
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(invoice_content)
        
        # Convert to client formats
        if formats is None:
            formats = self.format_converter.get_recommended_formats(FmtDocType.INVOICE, "client")
        
        conversion_results = self.format_converter.convert_document(
            txt_path, FmtDocType.INVOICE, formats, output_dir
        )
        
        results = {
            'content': invoice_content,
            'base_file': txt_path,
            'formats': {fmt.value: path for fmt, path in conversion_results.items() if path},
            'client_ready': [fmt.value for fmt, path in conversion_results.items() if path and fmt in [OutputFormat.PDF, OutputFormat.XLSX]]
        }
        
        return results

def main():
    """Demo the document generator"""
    generator = DocumentGenerator()
    
    # Sample client and project info
    client = {
        "name": "John & Mary Smith",
        "address": "123 Oak Street", 
        "city": "Austin",
        "state": "TX",
        "zip": "78701",
        "phone": "(512) 555-0123",
        "email": "jsmith@email.com"
    }
    
    project = {
        "name": "Backyard Sprinkler System Installation",
        "address": "123 Oak Street, Austin, TX"
    }
    
    # Templates and parameters for a 2-zone system
    templates = [
        ("src/templates/sprinkler_zone.json", {
            "zone_number": 1,
            "head_count": 6,
            "trench_feet": 120,
            "soil_type": "clay"
        }),
        ("src/templates/sprinkler_zone.json", {
            "zone_number": 2, 
            "head_count": 8,
            "trench_feet": 150,
            "soil_type": "clay"
        })
    ]
    
    print("🏠 GENERATING WATERWIZARD DOCUMENTS")
    print("=" * 50)
    
    # Generate contract
    contract = generator.generate_contract(client, project, templates)
    print("\n📄 CONTRACT GENERATED")
    print(contract)
    
    # Generate invoice  
    invoice = generator.generate_invoice(client, project, templates)
    print("\n📄 INVOICE GENERATED") 
    print(invoice)

if __name__ == "__main__":
    main()