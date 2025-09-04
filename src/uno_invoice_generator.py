#!/usr/bin/env python3
"""
WaterWizard UNO Invoice Generator
LibreOffice UNO-based invoice generation for Squirt 1.2
Modern professional formatting with reliable ODT output
"""

import uno
from com.sun.star.beans import PropertyValue
from com.sun.star.text.ControlCharacter import PARAGRAPH_BREAK, LINE_BREAK
from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Any, Optional
import subprocess
import time
import os
import tempfile


class UnoInvoiceGenerator:
    """LibreOffice UNO-based invoice generator for WaterWizard"""
    
    def __init__(self):
        """Initialize UNO connection and document components"""
        self.context = None
        self.desktop = None
        self.document = None
        self.uno_port = 2002
        self._connect_to_libreoffice()
    
    def _connect_to_libreoffice(self):
        """Establish connection to LibreOffice UNO bridge"""
        try:
            # Try to connect to existing LibreOffice instance
            local_context = uno.getComponentContext()
            resolver = local_context.ServiceManager.createInstanceWithContext(
                "com.sun.star.bridge.UnoUrlResolver", local_context
            )
            
            # Try to connect to headless LibreOffice instance
            try:
                self.context = resolver.resolve(
                    f"uno:socket,host=localhost,port={self.uno_port};urp;StarOffice.ComponentContext"
                )
            except:
                # Start headless LibreOffice instance
                self._start_libreoffice_headless()
                time.sleep(3)  # Give LO time to start
                self.context = resolver.resolve(
                    f"uno:socket,host=localhost,port={self.uno_port};urp;StarOffice.ComponentContext"
                )
            
            # Get desktop service
            self.desktop = self.context.ServiceManager.createInstanceWithContext(
                "com.sun.star.frame.Desktop", self.context
            )
            
            print("✅ Connected to LibreOffice UNO")
            
        except Exception as e:
            print(f"❌ Failed to connect to LibreOffice UNO: {e}")
            raise
    
    def _start_libreoffice_headless(self):
        """Start LibreOffice in headless mode with UNO listening"""
        try:
            cmd = [
                'libreoffice',
                '--headless',
                f'--accept=socket,host=localhost,port={self.uno_port};urp;StarOffice.ServiceManager',
                '--nofirststartwizard',
                '--nologo'
            ]
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("🚀 Started LibreOffice headless instance")
        except Exception as e:
            print(f"❌ Failed to start LibreOffice: {e}")
            raise
    
    def create_new_document(self) -> bool:
        """Create a new Writer document"""
        try:
            # Create new Writer document
            self.document = self.desktop.loadComponentFromURL(
                "private:factory/swriter", "_blank", 0, ()
            )
            return True
        except Exception as e:
            print(f"❌ Failed to create new document: {e}")
            return False
    
    def generate_invoice(self, client_info: Dict[str, Any], project_info: Dict[str, Any], 
                        line_items: List[Dict[str, Any]], subtotal: Decimal, 
                        tax_amount: Decimal, total: Decimal, output_path: str) -> bool:
        """Generate professional invoice using UNO API"""
        
        if not self.create_new_document():
            return False
        
        try:
            # Get document text and cursor
            text = self.document.Text
            cursor = text.createTextCursor()
            
            # Set up document formatting
            self._setup_document_styles()
            
            # Generate invoice content in modern professional style
            self._add_invoice_header(cursor, client_info, project_info)
            self._add_invoice_body(cursor, line_items, subtotal, tax_amount, total)
            self._add_invoice_footer(cursor)
            
            # Save document as ODT
            self._save_document_as_odt(output_path)
            
            # Close document
            self.document.close(True)
            self.document = None
            
            print(f"✅ Invoice generated: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate invoice: {e}")
            if self.document:
                try:
                    self.document.close(False)
                except:
                    pass
                self.document = None
            return False
    
    def _setup_document_styles(self):
        """Configure document-wide styles and formatting"""
        try:
            # Get style families
            style_families = self.document.StyleFamilies
            para_styles = style_families.getByName("ParagraphStyles")
            
            # Configure page style for margins and layout
            page_styles = style_families.getByName("PageStyles")
            page_style = page_styles.getByName("Standard")
            
            # Set margins (in millimeters * 100)
            page_style.LeftMargin = 2000   # 20mm
            page_style.RightMargin = 2000  # 20mm
            page_style.TopMargin = 2000    # 20mm
            page_style.BottomMargin = 2000 # 20mm
            
            # Create custom paragraph styles
            self._create_header_styles(para_styles)
            
        except Exception as e:
            print(f"⚠️ Warning: Could not setup document styles: {e}")
    
    def _create_header_styles(self, para_styles):
        """Create WaterWizard header styles"""
        try:
            # Main header style
            if not para_styles.hasByName("WaterWizardHeader"):
                header_style = self.document.createInstance("com.sun.star.style.ParagraphStyle")
                header_style.CharFontName = "Liberation Sans"
                header_style.CharHeight = 20
                header_style.CharWeight = 150  # Bold
                header_style.ParaAdjust = 1    # Center alignment
                header_style.CharColor = 0x0066CC  # Blue color
                header_style.ParaTopMargin = 0
                header_style.ParaBottomMargin = 200
                para_styles.insertByName("WaterWizardHeader", header_style)
            
            # Subheader style
            if not para_styles.hasByName("WaterWizardSubHeader"):
                subheader_style = self.document.createInstance("com.sun.star.style.ParagraphStyle")
                subheader_style.CharFontName = "Liberation Sans"
                subheader_style.CharHeight = 14
                subheader_style.CharWeight = 150  # Bold
                subheader_style.ParaAdjust = 1    # Center alignment
                subheader_style.CharColor = 0x666666  # Gray color
                subheader_style.ParaTopMargin = 0
                subheader_style.ParaBottomMargin = 400
                para_styles.insertByName("WaterWizardSubHeader", subheader_style)
            
            # Section header style
            if not para_styles.hasByName("SectionHeader"):
                section_style = self.document.createInstance("com.sun.star.style.ParagraphStyle")
                section_style.CharFontName = "Liberation Sans"
                section_style.CharHeight = 12
                section_style.CharWeight = 150  # Bold
                section_style.CharColor = 0x0066CC  # Blue color
                section_style.ParaTopMargin = 400
                section_style.ParaBottomMargin = 200
                para_styles.insertByName("SectionHeader", section_style)
            
        except Exception as e:
            print(f"⚠️ Warning: Could not create header styles: {e}")
    
    def _add_invoice_header(self, cursor, client_info: Dict[str, Any], project_info: Dict[str, Any]):
        """Add modern professional invoice header"""
        text = self.document.Text
        
        # Company header
        text.insertString(cursor, "WATERWIZARD IRRIGATION", False)
        cursor.gotoEnd(False)
        text.insertControlCharacter(cursor, LINE_BREAK, False)
        text.insertString(cursor, "Professional Landscape Services", False)
        
        # Apply header style to company name
        cursor.gotoStart(False)
        cursor.goRight(len("WATERWIZARD IRRIGATION"), True)  # Select company name
        cursor.ParaStyleName = "WaterWizardHeader"
        
        # Apply subheader style to tagline
        cursor.gotoEnd(False)
        cursor.goLeft(len("Professional Landscape Services"), True)
        cursor.ParaStyleName = "WaterWizardSubHeader"
        
        cursor.gotoEnd(False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        
        # Invoice title
        text.insertString(cursor, "INVOICE", False)
        cursor.goLeft(len("INVOICE"), True)
        cursor.CharHeight = 18
        cursor.CharWeight = 150  # Bold
        cursor.CharColor = 0x0066CC
        cursor.ParaAdjust = 1  # Center
        cursor.gotoEnd(False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        
        # Invoice details
        doc_number = f"INV-{datetime.now().strftime('%Y%m%d')}-001"
        date_str = datetime.now().strftime("%B %d, %Y")
        
        # Create table for invoice details and client info
        self._add_invoice_details_table(cursor, doc_number, date_str, client_info, project_info)
    
    def _add_invoice_details_table(self, cursor, doc_number: str, date_str: str, 
                                  client_info: Dict[str, Any], project_info: Dict[str, Any]):
        """Add invoice details and client information in professional table format"""
        try:
            text = self.document.Text
            
            # Create table for invoice header information
            table = self.document.createInstance("com.sun.star.text.TextTable")
            table.initialize(6, 2)  # 6 rows, 2 columns
            
            text.insertTextContent(cursor, table, False)
            
            # Configure table appearance
            table.setPropertyValue("Width", 16000)  # Full width
            table.setPropertyValue("RelativeWidth", 100)
            
            # Remove borders for cleaner look (skip if not available)
            try:
                table.setPropertyValue("TableBorder", None)
            except:
                pass  # Skip border formatting if not available
            
            # Fill table with data
            # Row 1: Invoice details
            table.getCellByName("A1").setString("Invoice Number:")
            table.getCellByName("B1").setString(doc_number)
            
            table.getCellByName("A2").setString("Date:")
            table.getCellByName("B2").setString(date_str)
            
            table.getCellByName("A3").setString("Due:")
            table.getCellByName("B3").setString("Upon Receipt")
            
            # Row 4: Blank separator
            table.getCellByName("A4").setString("")
            table.getCellByName("B4").setString("")
            
            # Rows 5-6: Bill To information
            table.getCellByName("A5").setString("BILL TO:")
            bill_to_info = f"{client_info.get('name', 'N/A')}\n{client_info.get('address', 'N/A')}\n{client_info.get('city', '')}, {client_info.get('state', '')} {client_info.get('zip', '')}"
            table.getCellByName("B5").setString(bill_to_info)
            
            table.getCellByName("A6").setString("PROJECT:")
            table.getCellByName("B6").setString(project_info.get('name', 'N/A'))
            
            # Style the table cells
            for row in range(1, 7):
                for col in ['A', 'B']:
                    cell = table.getCellByName(f"{col}{row}")
                    cell_cursor = cell.createTextCursor()
                    if col == 'A':  # Labels
                        cell_cursor.CharWeight = 150  # Bold
                        cell_cursor.CharColor = 0x0066CC
            
            # Move cursor after table
            cursor.gotoEnd(False)
            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
            
        except Exception as e:
            print(f"⚠️ Warning: Could not create invoice details table: {e}")
            # Fallback to simple text
            text = self.document.Text
            text.insertString(cursor, f"Invoice Number: {doc_number}", False)
            text.insertControlCharacter(cursor, LINE_BREAK, False)
            text.insertString(cursor, f"Date: {date_str}", False)
            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
    
    def _add_invoice_body(self, cursor, line_items: List[Dict[str, Any]], 
                         subtotal: Decimal, tax_amount: Decimal, total: Decimal):
        """Add invoice body with line items in professional table"""
        text = self.document.Text
        
        # Services section header
        text.insertString(cursor, "SERVICES PROVIDED", False)
        cursor.goLeft(len("SERVICES PROVIDED"), True)
        cursor.ParaStyleName = "SectionHeader"
        cursor.gotoEnd(False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        
        # Create line items table
        self._add_line_items_table(cursor, line_items, subtotal, tax_amount, total)
    
    def _add_line_items_table(self, cursor, line_items: List[Dict[str, Any]], 
                             subtotal: Decimal, tax_amount: Decimal, total: Decimal):
        """Create professional line items table"""
        try:
            text = self.document.Text
            
            # Calculate table rows needed
            row_count = len(line_items) + 5  # Items + header + 3 total rows + blank
            table = self.document.createInstance("com.sun.star.text.TextTable")
            table.initialize(row_count, 4)  # Description, Qty, Rate, Amount
            
            text.insertTextContent(cursor, table, False)
            
            # Configure table appearance
            table.setPropertyValue("Width", 16000)
            table.setPropertyValue("RelativeWidth", 100)
            
            # Set column widths
            columns = table.getColumns()
            columns.getByIndex(0).setPropertyValue("RelativeWidth", 50)  # Description
            columns.getByIndex(1).setPropertyValue("RelativeWidth", 15)  # Qty
            columns.getByIndex(2).setPropertyValue("RelativeWidth", 15)  # Rate  
            columns.getByIndex(3).setPropertyValue("RelativeWidth", 20)  # Amount
            
            # Header row with professional styling
            table.getCellByName("A1").setString("Description")
            table.getCellByName("B1").setString("Qty")
            table.getCellByName("C1").setString("Rate")
            table.getCellByName("D1").setString("Amount")
            
            # Style header row
            for col in ['A', 'B', 'C', 'D']:
                cell = table.getCellByName(f"{col}1")
                cell_cursor = cell.createTextCursor()
                cell_cursor.CharWeight = 150  # Bold
                cell_cursor.CharColor = 0x0066CC
                cell_cursor.ParaAdjust = 1  # Center alignment
                
                # Add border to header (skip if not available)
                try:
                    # Simple border formatting
                    cell.setPropertyValue("BottomBorder", 1)
                except:
                    pass  # Skip border if not supported
            
            # Add line items
            for i, item in enumerate(line_items, start=2):
                desc = str(item.get('description', ''))
                qty = f"{item.get('quantity', 0):.1f}"
                rate = f"${item.get('unit_rate', 0):.2f}"
                amount = f"${item.get('line_total', 0):.2f}"
                
                table.getCellByName(f"A{i}").setString(desc)
                table.getCellByName(f"B{i}").setString(qty)
                table.getCellByName(f"C{i}").setString(rate)
                table.getCellByName(f"D{i}").setString(amount)
                
                # Right-align numeric columns
                for col in ['B', 'C', 'D']:
                    cell = table.getCellByName(f"{col}{i}")
                    cell_cursor = cell.createTextCursor()
                    cell_cursor.ParaAdjust = 2  # Right alignment
            
            # Totals section
            total_start_row = len(line_items) + 2
            
            # Blank row
            table.getCellByName(f"A{total_start_row}").setString("")
            
            # Subtotal
            table.getCellByName(f"C{total_start_row + 1}").setString("SUBTOTAL:")
            table.getCellByName(f"D{total_start_row + 1}").setString(f"${subtotal:.2f}")
            
            # Tax
            if tax_amount > 0:
                table.getCellByName(f"C{total_start_row + 2}").setString("TAX:")
                table.getCellByName(f"D{total_start_row + 2}").setString(f"${tax_amount:.2f}")
                total_row = total_start_row + 3
            else:
                table.getCellByName(f"C{total_start_row + 2}").setString("TAX (Oregon - No Sales Tax):")
                table.getCellByName(f"D{total_start_row + 2}").setString("$0.00")
                total_row = total_start_row + 3
            
            # Total
            table.getCellByName(f"C{total_row}").setString("TOTAL:")
            table.getCellByName(f"D{total_row}").setString(f"${total:.2f}")
            
            # Style totals section
            for row in range(total_start_row + 1, total_row + 1):
                for col in ['C', 'D']:
                    cell = table.getCellByName(f"{col}{row}")
                    cell_cursor = cell.createTextCursor()
                    cell_cursor.CharWeight = 150  # Bold
                    cell_cursor.ParaAdjust = 2  # Right alignment
                    
                    if row == total_row:  # Final total row
                        cell_cursor.CharColor = 0x0066CC
                        try:
                            cell.setPropertyValue("TopBorder", 1)
                        except:
                            pass  # Skip border if not supported
            
            # Move cursor after table
            cursor.gotoEnd(False)
            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
            
        except Exception as e:
            print(f"⚠️ Warning: Could not create line items table: {e}")
            # Fallback to simple text format
            self._add_simple_line_items(cursor, line_items, subtotal, tax_amount, total)
    
    def _add_simple_line_items(self, cursor, line_items: List[Dict[str, Any]], 
                              subtotal: Decimal, tax_amount: Decimal, total: Decimal):
        """Fallback simple text format for line items"""
        text = self.document.Text
        
        text.insertString(cursor, "Description                           Qty    Rate      Amount", False)
        text.insertControlCharacter(cursor, LINE_BREAK, False)
        text.insertString(cursor, "-" * 60, False)
        text.insertControlCharacter(cursor, LINE_BREAK, False)
        
        for item in line_items:
            desc = str(item.get('description', ''))[:30]
            qty = f"{item.get('quantity', 0):.1f}"
            rate = f"${item.get('unit_rate', 0):.2f}"
            amount = f"${item.get('line_total', 0):.2f}"
            
            line = f"{desc:<30} {qty:>5} {rate:>8} {amount:>10}"
            text.insertString(cursor, line, False)
            text.insertControlCharacter(cursor, LINE_BREAK, False)
        
        text.insertControlCharacter(cursor, LINE_BREAK, False)
        text.insertString(cursor, f"SUBTOTAL: ${subtotal:.2f}", False)
        text.insertControlCharacter(cursor, LINE_BREAK, False)
        text.insertString(cursor, f"TAX: ${tax_amount:.2f}", False)
        text.insertControlCharacter(cursor, LINE_BREAK, False)
        text.insertString(cursor, f"TOTAL: ${total:.2f}", False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
    
    def _add_invoice_footer(self, cursor):
        """Add professional invoice footer"""
        text = self.document.Text
        
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        
        # Payment terms section
        text.insertString(cursor, "PAYMENT TERMS", False)
        cursor.goLeft(len("PAYMENT TERMS"), True)
        cursor.ParaStyleName = "SectionHeader"
        cursor.gotoEnd(False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        
        text.insertString(cursor, "Payment due upon completion of work.", False)
        text.insertControlCharacter(cursor, LINE_BREAK, False)
        text.insertString(cursor, "Thank you for choosing WaterWizard for your landscape needs!", False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        
        # Contact information
        text.insertString(cursor, "Questions? Contact us at info@waterwizard.com or (555) 123-4567", False)
        cursor.goLeft(len("Questions? Contact us at info@waterwizard.com or (555) 123-4567"), True)
        cursor.CharHeight = 10
        cursor.CharColor = 0x666666
        cursor.ParaAdjust = 1  # Center
    
    def _save_document_as_odt(self, output_path: str):
        """Save document as ODT file"""
        try:
            # Prepare save properties
            save_props = (
                PropertyValue("FilterName", 0, "writer8", 0),
                PropertyValue("Overwrite", 0, True, 0)
            )
            
            # Convert path to URL format
            if not output_path.startswith("file://"):
                output_path = f"file://{os.path.abspath(output_path)}"
            
            # Save document
            self.document.storeAsURL(output_path, save_props)
            
        except Exception as e:
            print(f"❌ Failed to save document: {e}")
            raise
    
    def close_connection(self):
        """Close UNO connection and cleanup"""
        try:
            if self.document:
                self.document.close(False)
                self.document = None
            
            if self.desktop:
                self.desktop = None
            
            if self.context:
                self.context = None
                
        except Exception as e:
            print(f"⚠️ Error closing UNO connection: {e}")


def main():
    """Test the UNO invoice generator with Liam Smith data"""
    print("🧾 WATERWIZARD UNO INVOICE GENERATOR - SQUIRT 1.2")
    print("=" * 60)
    
    generator = UnoInvoiceGenerator()
    
    try:
        # Liam Smith test data
        client_info = {
            'name': 'Liam Smith',
            'address': '6112 SE 77th Ave',
            'city': 'Portland',
            'state': 'OR',
            'zip': '97206',
            'phone': '785-979-5599',
            'email': 'lsmith@email.com'
        }
        
        project_info = {
            'name': 'Fall Clean-up 2025',
            'address': '6112 SE 77th Ave, Portland, OR'
        }
        
        # Line items from Liam Smith project
        line_items = [
            {'description': 'Truck fee', 'quantity': 1.0, 'unit_rate': 100.00, 'line_total': 100.00},
            {'description': 'Disposal fee', 'quantity': 1.0, 'unit_rate': 40.00, 'line_total': 40.00},
            {'description': 'Labor: Dead head, prune', 'quantity': 1.0, 'unit_rate': 75.00, 'line_total': 75.00},
            {'description': 'Labor: Dig/remove 80%-90% hollyhocks', 'quantity': 2.0, 'unit_rate': 75.00, 'line_total': 150.00},
            {'description': 'Labor: Dig and cut root ball', 'quantity': 3.0, 'unit_rate': 75.00, 'line_total': 225.00},
            {'description': 'Labor: Setup, backfill & cleanup', 'quantity': 1.0, 'unit_rate': 75.00, 'line_total': 75.00}
        ]
        
        subtotal = Decimal("665.00")
        tax_amount = Decimal("0.00")  # Oregon no sales tax
        total = Decimal("665.00")
        
        output_path = "/tmp/liam_smith_uno_invoice.odt"
        
        print("📋 Generating invoice with UNO API...")
        success = generator.generate_invoice(
            client_info, project_info, line_items, 
            subtotal, tax_amount, total, output_path
        )
        
        if success:
            print("✅ UNO Invoice generated successfully!")
            print(f"📄 Output: {output_path}")
            
            # Try to open with LibreOffice to verify
            try:
                subprocess.run(['libreoffice', output_path], timeout=2)
                print("🚀 Document opened in LibreOffice")
            except:
                print("💡 Open manually with: libreoffice", output_path)
        else:
            print("❌ Invoice generation failed")
            
    finally:
        generator.close_connection()


if __name__ == "__main__":
    main()