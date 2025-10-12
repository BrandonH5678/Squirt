#!/usr/bin/env python3
"""
WaterWizard Invoice - John Shannock
Generate invoice for concrete demolition project at 10402 NW 11th Ave
"""

import sys
import os

# Add src directory to path FIRST
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from uno_invoice_generator import UnoInvoiceGenerator
from file_tracking_system import get_tracked_path
from decimal import Decimal
from datetime import datetime


def main():
    """Generate invoice for John Shannock concrete demolition project"""
    print("🧾 WATERWIZARD INVOICE - JOHN SHANNOCK")
    print("=" * 60)

    generator = UnoInvoiceGenerator()

    try:
        # Client information
        client_info = {
            'name': 'John Shannock',
            'address': '10402 NW 11th Ave',
            'city': 'Vancouver',
            'state': 'WA',
            'zip': '98685',
            'phone': '',
            'email': ''
        }

        project_info = {
            'name': 'Concrete Stairs Demolition & Disposal',
            'address': '10402 NW 11th Ave, Vancouver, WA'
        }

        # Parse line items from voice memo data
        line_items = [
            # Materials - 9/23/2025
            {
                'description': '2x PT 2x4, 1x masonry screws (9/23/2025)',
                'quantity': 1.0,
                'unit_rate': Decimal('49.32'),
                'line_total': Decimal('49.32')
            },
            {
                'description': 'Concrete saw (9/23/2025)',
                'quantity': 1.0,
                'unit_rate': Decimal('130.39'),
                'line_total': Decimal('130.39')
            },
            {
                'description': 'Concrete drill bits (9/23/2025)',
                'quantity': 1.0,
                'unit_rate': Decimal('43.37'),
                'line_total': Decimal('43.37')
            },

            # Labor - Materials pickup - 9/23/2025
            {
                'description': 'Labor: Materials pickup (9/23/2025)',
                'quantity': 2.0,
                'unit_rate': Decimal('75.00'),
                'line_total': Decimal('150.00')
            },

            # Labor - Demolition - 9/23/2025
            {
                'description': 'Labor: Concrete stairs demolition (9/23/2025)',
                'quantity': 6.0,
                'unit_rate': Decimal('75.00'),
                'line_total': Decimal('450.00')
            },

            # Labor - Demolition - 9/24/2025
            {
                'description': 'Labor: Concrete stairs demolition (9/24/2025)',
                'quantity': 4.0,
                'unit_rate': Decimal('75.00'),
                'line_total': Decimal('300.00')
            },

            # Labor - Demolition - 9/25/2025
            {
                'description': 'Labor: Concrete stairs demolition (9/25/2025)',
                'quantity': 4.0,
                'unit_rate': Decimal('75.00'),
                'line_total': Decimal('300.00')
            },

            # Truck fee - 10/8/2025
            {
                'description': 'Truck fee (10/8/2025)',
                'quantity': 1.0,
                'unit_rate': Decimal('50.00'),
                'line_total': Decimal('50.00')
            },

            # Labor - Disposal - 10/8/2025
            {
                'description': 'Labor: Concrete and sand disposal (10/8/2025)',
                'quantity': 4.0,
                'unit_rate': Decimal('75.00'),
                'line_total': Decimal('300.00')
            }
        ]

        # Calculate totals
        subtotal = sum(item['line_total'] for item in line_items)
        # Washington sales tax: 8.4% (Vancouver, WA rate)
        tax_rate = Decimal('0.084')
        tax_amount = (subtotal * tax_rate).quantize(Decimal('0.01'))
        total_before_deposit = subtotal + tax_amount

        # Deposit paid on 9/23/2025
        deposit_amount = Decimal('1000.00')
        total = total_before_deposit - deposit_amount

        print(f"📊 INVOICE SUMMARY:")
        print(f"   Materials: ${sum(item['line_total'] for item in line_items[:3]):.2f}")
        print(f"   Labor Hours: {sum(item['quantity'] for item in line_items[3:] if 'Labor' in item['description'])} @ $75/hr")
        print(f"   Truck Fee: $50.00")
        print(f"   Subtotal: ${subtotal:.2f}")
        print(f"   Tax: ${tax_amount:.2f}")
        print(f"   Total: ${total_before_deposit:.2f}")
        print(f"   Deposit (9/23/2025): -${deposit_amount:.2f}")
        print(f"   BALANCE DUE: ${total:.2f}")
        print()

        # Generate output path
        output_path = get_tracked_path(
            "john_shannock_invoice.odt",
            "John Shannock",
            "invoice"
        )

        print("📋 Generating invoice with LibreOffice UNO...")
        success = generator.generate_invoice(
            client_info,
            project_info,
            line_items,
            subtotal,
            tax_amount,
            total,
            output_path,
            deposit_amount=deposit_amount
        )

        if success:
            print("✅ Invoice generated successfully!")
            print(f"📄 Output: {output_path}")
            print()
            print("💡 Open with: libreoffice", output_path)
        else:
            print("❌ Invoice generation failed")
            return 1

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        generator.close_connection()

    return 0


if __name__ == "__main__":
    sys.exit(main())
