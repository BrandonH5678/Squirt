#!/usr/bin/env python3
"""
WaterWizard CSV Exporter
Generates QuickBooks-compatible CSV files from invoice data
"""

import csv
from datetime import datetime
from decimal import Decimal
from io import StringIO

class CSVExporter:
    def __init__(self):
        """Initialize CSV exporter with QuickBooks format"""
        self.quickbooks_headers = [
            'Date', 'Transaction Type', 'Customer', 'Invoice #', 
            'Item', 'Description', 'Qty', 'Unit Price', 'Amount',
            'Tax Code', 'Tax Amount', 'Total'
        ]
    
    def export_invoice_to_csv(self, client_info: dict, project_info: dict, 
                             line_items: list, subtotal: Decimal, 
                             tax_amount: Decimal, total: Decimal, 
                             invoice_number: str) -> str:
        """Export invoice data to QuickBooks CSV format"""
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(self.quickbooks_headers)
        
        date_str = datetime.now().strftime('%m/%d/%Y')
        customer = client_info['name']
        
        # Write each line item
        for item in line_items:
            row = [
                date_str,                    # Date
                'Invoice',                   # Transaction Type  
                customer,                    # Customer
                invoice_number,              # Invoice #
                item['element_id'],          # Item
                item['description'],         # Description
                f"{item['quantity']:.2f}",   # Qty
                f"{item['unit_rate']:.2f}",  # Unit Price
                f"{item['line_total']:.2f}", # Amount
                'TX',                        # Tax Code (Texas)
                '',                          # Tax Amount (per line - leave empty)
                ''                           # Total (per line - leave empty)
            ]
            writer.writerow(row)
        
        # Write tax line
        writer.writerow([
            date_str,
            'Invoice',
            customer,
            invoice_number,
            'TAX',
            'Sales Tax',
            '1.00',
            f"{tax_amount:.2f}",
            f"{tax_amount:.2f}",
            'TX',
            f"{tax_amount:.2f}",
            ''
        ])
        
        # Write total line (summary)
        writer.writerow([
            date_str,
            'Invoice',
            customer, 
            invoice_number,
            'TOTAL',
            f"Invoice Total - {project_info['name']}",
            '',
            '',
            f"{total:.2f}",
            '',
            f"{tax_amount:.2f}",
            f"{total:.2f}"
        ])
        
        return output.getvalue()
    
    def save_csv(self, csv_content: str, filename: str):
        """Save CSV content to file"""
        with open(filename, 'w', newline='') as f:
            f.write(csv_content)
        print(f"✅ CSV exported to: {filename}")

def main():
    """Demo CSV export functionality"""
    from document_generator import DocumentGenerator
    
    generator = DocumentGenerator()
    exporter = CSVExporter()
    
    # Sample data
    client = {
        "name": "John & Mary Smith",
        "address": "123 Oak Street",
        "city": "Austin", 
        "state": "TX",
        "zip": "78701"
    }
    
    project = {
        "name": "Backyard Sprinkler System Installation"
    }
    
    templates = [
        ("src/templates/sprinkler_zone.json", {
            "zone_number": 1,
            "head_count": 6,
            "trench_feet": 120,
            "soil_type": "turf"  # Use turf for simpler example
        })
    ]
    
    # Generate invoice data
    all_line_items = []
    total_subtotal = Decimal("0")
    
    for template_path, params in templates:
        result = generator.processor.process_template(template_path, params)
        all_line_items.extend(result['line_items'])
        total_subtotal += Decimal(str(result['subtotal']))
    
    tax_rate = Decimal("0.0875")
    tax_amount = (total_subtotal * tax_rate).quantize(Decimal('0.01'))
    grand_total = (total_subtotal + tax_amount).quantize(Decimal('0.01'))
    
    invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-001"
    
    # Generate CSV
    csv_content = exporter.export_invoice_to_csv(
        client, project, all_line_items, total_subtotal,
        tax_amount, grand_total, invoice_number
    )
    
    print("📊 QUICKBOOKS CSV EXPORT")
    print("=" * 50)
    print(csv_content)
    
    # Save to file
    filename = f"invoice_{datetime.now().strftime('%Y%m%d')}.csv"
    exporter.save_csv(csv_content, filename)

if __name__ == "__main__":
    main()