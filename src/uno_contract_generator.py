#!/usr/bin/env python3
"""
WaterWizard UNO Contract Generator
LibreOffice UNO-based contract generation for Squirt 1.2
Professional formatting with standard WaterWizard contract layout
"""

import uno
from com.sun.star.beans import PropertyValue
from com.sun.star.text.ControlCharacter import PARAGRAPH_BREAK
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import subprocess
import time
import sys
from pathlib import Path


class UnoContractGenerator:
    """LibreOffice UNO-based contract generator for WaterWizard"""

    def __init__(self):
        """Initialize UNO connection"""
        self.context = None
        self.desktop = None
        self.document = None
        self.uno_port = 2002
        self._connect_to_libreoffice()

    def _connect_to_libreoffice(self):
        """Establish connection to LibreOffice UNO bridge"""
        try:
            local_context = uno.getComponentContext()
            resolver = local_context.ServiceManager.createInstanceWithContext(
                "com.sun.star.bridge.UnoUrlResolver", local_context
            )

            try:
                self.context = resolver.resolve(
                    f"uno:socket,host=localhost,port={self.uno_port};urp;StarOffice.ComponentContext"
                )
            except:
                self._start_libreoffice_headless()
                time.sleep(3)
                self.context = resolver.resolve(
                    f"uno:socket,host=localhost,port={self.uno_port};urp;StarOffice.ComponentContext"
                )

            self.desktop = self.context.ServiceManager.createInstanceWithContext(
                "com.sun.star.frame.Desktop", self.context
            )
            print("✅ Connected to LibreOffice UNO")

        except Exception as e:
            print(f"❌ Failed to connect to LibreOffice: {e}")
            raise

    def _start_libreoffice_headless(self):
        """Start LibreOffice headless with UNO"""
        try:
            cmd = [
                'libreoffice', '--headless',
                f'--accept=socket,host=localhost,port={self.uno_port};urp;',
                '--nofirststartwizard', '--nologo'
            ]
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("🚀 Started LibreOffice headless")
        except Exception as e:
            print(f"❌ Failed to start LibreOffice: {e}")
            raise

    def create_new_document(self) -> bool:
        """Create new Writer document"""
        try:
            self.document = self.desktop.loadComponentFromURL(
                "private:factory/swriter", "_blank", 0, ()
            )
            return True
        except Exception as e:
            print(f"❌ Failed to create document: {e}")
            return False

    def generate_contract(self, contract_data: Dict[str, Any], output_path: str) -> bool:
        """Generate professional WaterWizard contract"""

        if not self.create_new_document():
            return False

        try:
            text = self.document.Text
            cursor = text.createTextCursor()

            # Setup document formatting
            self._setup_page_format()

            # Build contract
            self._add_header(cursor, contract_data)
            self._add_scope_of_work(cursor, contract_data)
            self._add_materials_labor(cursor, contract_data)
            self._add_pricing(cursor, contract_data)
            self._add_terms_conditions(cursor, contract_data)
            self._add_signature_block(cursor, contract_data)

            # Save as ODT
            self._save_document(output_path)

            # Generate PDF
            pdf_path = output_path.replace('.odt', '.pdf')
            self._save_as_pdf(pdf_path)

            print(f"✅ Contract generated: {output_path}")
            print(f"✅ PDF: {pdf_path}")

            self.document.close(True)
            self.document = None
            return True

        except Exception as e:
            print(f"❌ Contract generation failed: {e}")
            if self.document:
                self.document.close(False)
            return False

    def _setup_page_format(self):
        """Configure page margins and layout"""
        try:
            page_styles = self.document.StyleFamilies.getByName("PageStyles")
            page_style = page_styles.getByName("Standard")

            # 1" margins
            page_style.LeftMargin = 2540
            page_style.RightMargin = 2540
            page_style.TopMargin = 2540
            page_style.BottomMargin = 2540
        except Exception as e:
            print(f"⚠️  Page format warning: {e}")

    def _add_header(self, cursor, data: Dict):
        """Add WaterWizard header and client info"""
        text = self.document.Text

        # Company name - bold, larger
        cursor.ParaStyleName = "Heading 1"
        text.insertString(cursor, "WaterWizard Landscaping", False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

        # Contact info - normal
        cursor.ParaStyleName = "Standard"
        contact_info = data.get('company_info', {})
        if contact_info:
            text.insertString(cursor, f"{contact_info.get('phone', '')}", False)
            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
            text.insertString(cursor, f"{contact_info.get('email', '')}", False)
            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

        # Contract title
        cursor.ParaStyleName = "Heading 2"
        text.insertString(cursor, "SERVICE CONTRACT", False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

        # Contract details
        cursor.ParaStyleName = "Standard"
        contract_num = data.get('contract_number', 'N/A')
        contract_date = data.get('contract_date', datetime.now().strftime('%Y-%m-%d'))
        text.insertString(cursor, f"Contract #: {contract_num}", False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertString(cursor, f"Date: {contract_date}", False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

        # Client info
        client = data.get('client_info', {})
        text.insertString(cursor, f"Client: {client.get('name', 'N/A')}", False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertString(cursor, f"Property Address: {client.get('property_address', 'N/A')}", False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        if client.get('phone'):
            text.insertString(cursor, f"Phone: {client.get('phone')}", False)
            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

    def _add_scope_of_work(self, cursor, data: Dict):
        """Add scope of work section"""
        text = self.document.Text

        cursor.ParaStyleName = "Heading 3"
        text.insertString(cursor, "SCOPE OF WORK", False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

        cursor.ParaStyleName = "Standard"

        # Project description
        project_desc = data.get('project_description', '')
        if project_desc:
            text.insertString(cursor, project_desc, False)
            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

        # Scope items
        scope_items = data.get('scope_items', [])
        for item in scope_items:
            text.insertString(cursor, f"• {item}", False)
            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

    def _add_materials_labor(self, cursor, data: Dict):
        """Add materials and labor details"""
        text = self.document.Text

        # Materials
        materials = data.get('materials', [])
        if materials:
            cursor.ParaStyleName = "Heading 3"
            text.insertString(cursor, "MATERIALS", False)
            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

            cursor.ParaStyleName = "Standard"
            for mat in materials:
                desc = mat.get('description', '')
                qty = mat.get('qty', 0)
                unit = mat.get('unit', 'each')
                price = mat.get('unit_cost', 0)
                subtotal = mat.get('subtotal', qty * price)

                line = f"{qty} {unit}  {desc}"
                if subtotal > 0:
                    line += f" — ${subtotal:.2f}"

                text.insertString(cursor, line, False)
                text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

        # Labor
        labor_items = data.get('labor', [])
        if labor_items:
            cursor.ParaStyleName = "Heading 3"
            text.insertString(cursor, "LABOR", False)
            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

            cursor.ParaStyleName = "Standard"
            for labor in labor_items:
                task = labor.get('task', labor.get('description', ''))
                hours = labor.get('hours', 0)
                rate = labor.get('rate', 0)
                subtotal = labor.get('subtotal', hours * rate)

                line = f"{task}"
                if hours > 0:
                    line += f" ({hours} hrs @ ${rate:.0f}/hr)"
                if subtotal > 0:
                    line += f" — ${subtotal:.2f}"

                text.insertString(cursor, line, False)
                text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

        # Equipment
        equipment = data.get('equipment', [])
        if equipment:
            cursor.ParaStyleName = "Heading 3"
            text.insertString(cursor, "EQUIPMENT", False)
            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

            cursor.ParaStyleName = "Standard"
            for equip in equipment:
                desc = equip.get('description', '')
                subtotal = equip.get('subtotal', 0)

                line = f"{desc} — ${subtotal:.2f}"
                text.insertString(cursor, line, False)
                text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

    def _add_pricing(self, cursor, data: Dict):
        """Add pricing summary"""
        text = self.document.Text

        cursor.ParaStyleName = "Heading 3"
        text.insertString(cursor, "TOTAL ESTIMATE", False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

        cursor.ParaStyleName = "Standard"

        # Subtotals
        materials_total = data.get('materials_subtotal', 0)
        labor_total = data.get('labor_subtotal', 0)
        equipment_total = data.get('equipment_subtotal', 0)

        if materials_total > 0:
            text.insertString(cursor, f"Materials Subtotal: ${materials_total:.2f}", False)
            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

        if labor_total > 0:
            text.insertString(cursor, f"Labor Subtotal: ${labor_total:.2f}", False)
            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

        if equipment_total > 0:
            text.insertString(cursor, f"Equipment Subtotal: ${equipment_total:.2f}", False)
            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

        # Project subtotal
        subtotal = data.get('subtotal', 0)
        text.insertString(cursor, f"Project Subtotal: ${subtotal:.2f}", False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

        # Tax
        tax_amount = data.get('tax_amount', 0)
        tax_rate = data.get('tax_rate', 0.087)
        if tax_amount > 0:
            text.insertString(cursor, f"Sales Tax ({tax_rate*100:.1f}%): ${tax_amount:.2f}", False)
            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

        # Total - bold
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        total = data.get('total', 0)

        # Make total bold
        cursor.CharWeight = 150  # Bold
        text.insertString(cursor, f"TOTAL: ${total:.2f}", False)
        cursor.CharWeight = 100  # Normal
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

        # Validity
        validity_days = data.get('validity_days', 30)
        text.insertString(cursor, f"Valid for {validity_days} days from contract date", False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

    def _add_terms_conditions(self, cursor, data: Dict):
        """Add payment terms and conditions"""
        text = self.document.Text

        cursor.ParaStyleName = "Heading 3"
        text.insertString(cursor, "PAYMENT TERMS", False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

        cursor.ParaStyleName = "Standard"

        # Payment schedule
        payment_terms = data.get('payment_terms', {})
        deposit_pct = payment_terms.get('deposit_percent', 50)
        text.insertString(cursor, f"• {deposit_pct}% deposit required to schedule work", False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertString(cursor, f"• {100-deposit_pct}% due upon completion", False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertString(cursor, "• Payment accepted: check, cash, credit card", False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

        # Additional terms
        cursor.ParaStyleName = "Heading 3"
        text.insertString(cursor, "TERMS & CONDITIONS", False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

        cursor.ParaStyleName = "Standard"

        terms = data.get('additional_terms', [
            "Work schedule subject to weather conditions",
            "Customer responsible for marking underground utilities",
            "Changes to scope of work require written authorization",
            "Contractor not responsible for damage to unmarked utilities",
            "Customer grants access to property during project duration"
        ])

        for term in terms:
            text.insertString(cursor, f"• {term}", False)
            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

    def _add_signature_block(self, cursor, data: Dict):
        """Add signature section"""
        text = self.document.Text

        cursor.ParaStyleName = "Heading 3"
        text.insertString(cursor, "ACCEPTANCE", False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

        cursor.ParaStyleName = "Standard"
        text.insertString(cursor, "I accept the above terms and authorize WaterWizard Landscaping to proceed with this work.", False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

        # Client signature line
        text.insertString(cursor, "_" * 40, False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertString(cursor, "Client Signature", False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

        # Date line
        text.insertString(cursor, "_" * 40, False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertString(cursor, "Date", False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)

    def _save_document(self, output_path: str):
        """Save document as ODT"""
        try:
            # Ensure absolute path
            abs_path = Path(output_path).absolute()
            file_url = abs_path.as_uri()

            # Save as ODT
            store_props = (
                PropertyValue("FilterName", 0, "writer8", 0),
            )
            self.document.storeAsURL(file_url, store_props)

        except Exception as e:
            print(f"❌ Save error: {e}")
            raise

    def _save_as_pdf(self, pdf_path: str):
        """Export document as PDF"""
        try:
            abs_path = Path(pdf_path).absolute()
            file_url = abs_path.as_uri()

            pdf_props = (
                PropertyValue("FilterName", 0, "writer_pdf_Export", 0),
            )
            self.document.storeToURL(file_url, pdf_props)

        except Exception as e:
            print(f"⚠️  PDF export warning: {e}")


def main():
    """CLI entry point"""
    import json
    import argparse

    parser = argparse.ArgumentParser(description='Generate WaterWizard contracts')
    parser.add_argument('input_file', help='JSON file with contract data')
    parser.add_argument('--output', '-o', help='Output ODT path', default=None)

    args = parser.parse_args()

    # Load contract data
    with open(args.input_file, 'r') as f:
        contract_data = json.load(f)

    # Generate output path
    if not args.output:
        input_path = Path(args.input_file)
        output_path = input_path.parent / f"{input_path.stem}_contract.odt"
    else:
        output_path = Path(args.output)

    # Generate contract
    generator = UnoContractGenerator()
    success = generator.generate_contract(contract_data, str(output_path))

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
