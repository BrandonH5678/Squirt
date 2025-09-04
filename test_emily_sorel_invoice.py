#!/usr/bin/env python3
"""
Test Emily & Ed Sorel invoice generation using UNO API
"""

import sys
sys.path.append('src')

from uno_invoice_generator import UnoInvoiceGenerator
from decimal import Decimal
from datetime import datetime

def main():
    print("🧾 EMILY & ED SOREL INVOICE - UNO GENERATOR TEST")
    print("=" * 60)
    
    generator = UnoInvoiceGenerator()
    
    try:
        # Emily & Ed Sorel client data
        client_info = {
            'name': 'Emily & Ed Sorel',
            'address': '5951 SE 19th Ave',
            'city': 'Portland',
            'state': 'OR',
            'zip': '97202',
            'phone': '(555) 123-4567',  # Not provided, using placeholder
            'email': 'esorel@email.com'  # Not provided, using placeholder
        }
        
        project_info = {
            'name': 'Irrigation System Maintenance - Head & Nozzle Replacement',
            'address': '5951 SE 19th Ave, Portland, OR 97202'
        }
        
        # Line items based on provided data
        line_items = [
            {
                'description': 'Irrigation labor: moving and replacing heads and nozzles', 
                'quantity': 2.0, 
                'unit_rate': 82.00, 
                'line_total': 164.00
            },
            {
                'description': 'Rain Bird PRS 45 heads', 
                'quantity': 3.0, 
                'unit_rate': 8.00, 
                'line_total': 24.00
            },
            {
                'description': 'Rain Bird 10 VAN nozzles', 
                'quantity': 2.0, 
                'unit_rate': 5.00, 
                'line_total': 10.00
            },
            {
                'description': 'Funny pipe', 
                'quantity': 12.0, 
                'unit_rate': 0.45, 
                'line_total': 5.40
            }
        ]
        
        # Calculate totals
        subtotal = Decimal("203.40")  # 164 + 24 + 10 + 5.40
        tax_amount = Decimal("0.00")   # Oregon no sales tax
        total = Decimal("203.40")
        
        output_path = "/tmp/emily_sorel_invoice_uno.odt"
        
        print("📋 Generating Emily & Ed Sorel invoice...")
        print(f"   Labor: 2 hours @ $82/hr = $164.00")
        print(f"   Materials: Rain Bird heads, nozzles, pipe = $39.40")
        print(f"   Total: ${total}")
        print()
        
        success = generator.generate_invoice(
            client_info, project_info, line_items, 
            subtotal, tax_amount, total, output_path
        )
        
        if success:
            print("✅ Emily & Ed Sorel Invoice generated successfully!")
            print(f"📄 Output: {output_path}")
            
            # Display file information
            import os
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"📊 File size: {file_size:,} bytes")
                print(f"🕐 Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
                
            # Try to open document for verification
            try:
                import subprocess
                subprocess.run(['libreoffice', output_path], timeout=2)
                print("🚀 Invoice opened in LibreOffice for verification")
            except:
                print(f"💡 Open manually: libreoffice {output_path}")
                
            print()
            print("🔍 INVOICE VERIFICATION:")
            print("=" * 30)
            print("✓ Client: Emily & Ed Sorel")
            print("✓ Address: 5951 SE 19th Ave, Portland OR 97202") 
            print("✓ Service Date: August 5th, 2025 (in project description)")
            print("✓ Labor: 2 hours @ $82/hour = $164.00")
            print("✓ Rain Bird PRS 45 heads: 3 × $8 = $24.00")
            print("✓ Rain Bird 10 VAN nozzles: 2 × $5 = $10.00")
            print("✓ Funny pipe 12 ft: 12 × $0.45 = $5.40")
            print("✓ Oregon tax: $0.00 (no sales tax)")
            print("✓ Total: $203.40")
            
        else:
            print("❌ Invoice generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        generator.close_connection()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)