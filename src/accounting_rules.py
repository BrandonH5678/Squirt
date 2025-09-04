#!/usr/bin/env python3
"""
Squirt Accounting Rules Engine
Defines when and how to generate CSV accounting files for QuickBooks integration
"""

from enum import Enum
from typing import Dict, Any, Optional
import csv
from datetime import datetime
from decimal import Decimal

class DocumentType(Enum):
    ESTIMATE = "estimate"
    QUOTE = "quote" 
    CONTRACT = "contract"
    INVOICE = "invoice"
    RECEIPT = "receipt"

class DocumentStatus(Enum):
    DRAFT = "draft"
    SENT = "sent"
    SIGNED = "signed"
    PAID = "paid"
    CANCELLED = "cancelled"

class AccountingRulesEngine:
    def __init__(self):
        """Initialize accounting rules for CSV generation"""
        
        # Define which document types/statuses require CSV accounting files
        self.csv_required_rules = {
            # Estimates and quotes: NO CSV until signed
            (DocumentType.ESTIMATE, DocumentStatus.DRAFT): False,
            (DocumentType.ESTIMATE, DocumentStatus.SENT): False,
            (DocumentType.ESTIMATE, DocumentStatus.SIGNED): True,  # Convert to contract when signed
            
            (DocumentType.QUOTE, DocumentStatus.DRAFT): False,
            (DocumentType.QUOTE, DocumentStatus.SENT): False,
            (DocumentType.QUOTE, DocumentStatus.SIGNED): True,  # Convert to contract when signed
            
            # Contracts: Always generate CSV once signed
            (DocumentType.CONTRACT, DocumentStatus.DRAFT): False,
            (DocumentType.CONTRACT, DocumentStatus.SENT): False,
            (DocumentType.CONTRACT, DocumentStatus.SIGNED): True,  # ALWAYS generate CSV
            
            # Invoices: Always generate CSV 
            (DocumentType.INVOICE, DocumentStatus.DRAFT): False,
            (DocumentType.INVOICE, DocumentStatus.SENT): True,   # Generate when sent
            (DocumentType.INVOICE, DocumentStatus.SIGNED): True,  # Generate when agreed
            
            # Receipts: Always generate CSV
            (DocumentType.RECEIPT, DocumentStatus.DRAFT): True,
            (DocumentType.RECEIPT, DocumentStatus.SENT): True,
            (DocumentType.RECEIPT, DocumentStatus.SIGNED): True,
        }
        
        # QuickBooks CSV headers
        self.quickbooks_headers = [
            'Date', 'Transaction Type', 'Customer', 'Invoice #', 
            'Product/Service', 'Description', 'Qty', 'Rate', 'Amount',
            'Billable', 'Tax Code', 'Tax Amount', 'Customer Message', 'Memo'
        ]
    
    def should_generate_csv(self, doc_type: DocumentType, doc_status: DocumentStatus) -> bool:
        """Determine if CSV accounting file should be generated"""
        return self.csv_required_rules.get((doc_type, doc_status), False)
    
    def get_transaction_type(self, doc_type: DocumentType, doc_status: DocumentStatus) -> str:
        """Get appropriate QuickBooks transaction type"""
        
        if doc_type in [DocumentType.ESTIMATE, DocumentType.QUOTE]:
            if doc_status == DocumentStatus.SIGNED:
                return "Invoice"  # Signed estimate becomes an invoice
            else:
                return "Estimate"
        elif doc_type == DocumentType.CONTRACT:
            if doc_status == DocumentStatus.SIGNED:
                return "Invoice"  # Signed contract becomes an invoice
            else:
                return "Estimate"
        elif doc_type == DocumentType.INVOICE:
            return "Invoice"
        elif doc_type == DocumentType.RECEIPT:
            return "Payment"
        else:
            return "Invoice"  # Default
    
    def generate_accounting_csv(self, project_data: Dict[str, Any], 
                               doc_type: DocumentType, doc_status: DocumentStatus,
                               output_path: str) -> Optional[str]:
        """Generate QuickBooks CSV if required by accounting rules"""
        
        # Check if CSV should be generated
        if not self.should_generate_csv(doc_type, doc_status):
            return None
        
        # Extract project information
        client_name = project_data.get('client_name', 'Unknown Client')
        line_items = project_data.get('line_items', [])
        subtotal = Decimal(str(project_data.get('subtotal', 0)))
        tax_amount = Decimal(str(project_data.get('tax_amount', 0)))
        total = subtotal + tax_amount
        
        # Generate document number
        doc_number = project_data.get('doc_number', f"WW-{datetime.now().strftime('%Y%m%d')}-001")
        
        # Get transaction type based on document type and status
        transaction_type = self.get_transaction_type(doc_type, doc_status)
        
        # Generate CSV content
        csv_lines = []
        csv_lines.append(','.join(self.quickbooks_headers))
        
        batch_date = datetime.now().strftime('%m/%d/%Y')
        
        # Add line items
        for item in line_items:
            row = [
                batch_date,                           # Date
                transaction_type,                     # Transaction Type
                client_name,                         # Customer
                doc_number,                          # Invoice #
                item.get('element_id', 'SERVICE'),   # Product/Service
                item.get('description', 'Service'),  # Description
                f"{item.get('quantity', 1):.2f}",    # Qty
                f"{item.get('unit_rate', 0):.2f}",   # Rate
                f"{item.get('line_total', 0):.2f}",  # Amount
                'Y',                                 # Billable
                'TAX',                              # Tax Code
                '',                                 # Tax Amount (per line)
                'Thank you for your business!',     # Customer Message
                f"Project: {project_data.get('project_name', 'N/A')}" # Memo
            ]
            csv_lines.append(','.join(f'"{field}"' if ',' in str(field) else str(field) 
                                    for field in row))
        
        # Add tax line if applicable
        if tax_amount > 0:
            tax_row = [
                batch_date,                         # Date
                transaction_type,                   # Transaction Type
                client_name,                       # Customer
                doc_number,                        # Invoice #
                'TAX',                             # Product/Service
                'Sales Tax',                       # Description
                '1.00',                            # Qty
                f"{tax_amount:.2f}",               # Rate
                f"{tax_amount:.2f}",               # Amount
                'N',                               # Billable
                'TAX',                             # Tax Code
                f"{tax_amount:.2f}",               # Tax Amount
                '',                                # Customer Message
                'Sales tax'                        # Memo
            ]
            csv_lines.append(','.join(f'"{field}"' if ',' in str(field) else str(field) 
                                    for field in tax_row))
        
        # Save CSV file
        with open(output_path, 'w', newline='') as f:
            f.write('\n'.join(csv_lines))
        
        return output_path
    
    def get_accounting_status_message(self, doc_type: DocumentType, doc_status: DocumentStatus) -> str:
        """Get status message about CSV generation"""
        
        if self.should_generate_csv(doc_type, doc_status):
            return f"✅ CSV accounting file required for {doc_type.value} with status {doc_status.value}"
        else:
            return f"⏸️ No CSV accounting file needed for {doc_type.value} with status {doc_status.value}"

def main():
    """Demo the accounting rules engine"""
    
    engine = AccountingRulesEngine()
    
    print("📊 SQUIRT ACCOUNTING RULES ENGINE")
    print("=" * 50)
    
    # Test various document type and status combinations
    test_scenarios = [
        (DocumentType.ESTIMATE, DocumentStatus.DRAFT),
        (DocumentType.ESTIMATE, DocumentStatus.SENT), 
        (DocumentType.ESTIMATE, DocumentStatus.SIGNED),
        (DocumentType.CONTRACT, DocumentStatus.DRAFT),
        (DocumentType.CONTRACT, DocumentStatus.SIGNED),
        (DocumentType.INVOICE, DocumentStatus.SENT),
        (DocumentType.INVOICE, DocumentStatus.SIGNED),
    ]
    
    print("CSV Generation Rules:")
    for doc_type, doc_status in test_scenarios:
        message = engine.get_accounting_status_message(doc_type, doc_status)
        print(f"  {message}")
    
    print(f"\n🎯 KEY RULES:")
    print("• Estimates/Quotes: No CSV until signed")
    print("• Signed Contracts: Always generate CSV")  
    print("• Invoices: Always generate CSV")
    print("• Receipts: Always generate CSV")

if __name__ == "__main__":
    main()