#!/usr/bin/env python3
"""
WaterWizard UNO Estimate Generator
LibreOffice UNO-based estimate generation for Squirt 1.2
Professional estimates with modern formatting and reliable ODT output
"""

import uno
from com.sun.star.beans import PropertyValue
from com.sun.star.text.ControlCharacter import PARAGRAPH_BREAK, LINE_BREAK
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import subprocess
import time
import os
from human_validation_helper import HumanValidationHelper


class UnoEstimateGenerator:
    """LibreOffice UNO-based estimate generator for WaterWizard"""
    
    def __init__(self):
        """Initialize UNO connection and document components"""
        self.context = None
        self.desktop = None
        self.document = None
        self.uno_port = 2002
        self.validator = HumanValidationHelper()
        self._connect_to_libreoffice()
    
    def _connect_to_libreoffice(self):
        """Establish connection to LibreOffice UNO bridge"""
        try:
            # Try to connect to existing LibreOffice instance
            local_context = uno.getComponentContext()
            resolver = local_context.ServiceManager.createInstanceWithContext(
                "com.sun.star.bridge.UnoUrlResolver", local_context
            )
            
            # Connect to headless LibreOffice instance
            try:
                self.context = resolver.resolve(
                    f"uno:socket,host=localhost,port={self.uno_port};urp;StarOffice.ComponentContext"
                )
            except:
                # Start headless LibreOffice if not running
                self._start_libreoffice_headless()
                time.sleep(3)
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
            self.document = self.desktop.loadComponentFromURL(
                "private:factory/swriter", "_blank", 0, ()
            )
            return True
        except Exception as e:
            print(f"❌ Failed to create new document: {e}")
            return False
    
    def generate_estimate(self, client_info: Dict[str, Any], project_info: Dict[str, Any], 
                         scope_areas: List[Dict[str, Any]], subtotal: Decimal, 
                         tax_amount: Decimal, total: Decimal, output_path: str,
                         valid_days: int = 30, open_for_validation: bool = True) -> bool:
        """Generate professional estimate using UNO API"""
        
        if not self.create_new_document():
            return False
        
        try:
            # Get document text and cursor
            text = self.document.Text
            cursor = text.createTextCursor()
            
            # Set up document formatting
            self._setup_document_styles()
            
            # Generate estimate content in modern professional style
            self._add_estimate_header(cursor, client_info, project_info, valid_days)
            self._add_estimate_body(cursor, scope_areas, subtotal, tax_amount, total)
            self._add_estimate_footer(cursor, valid_days)
            
            # Save document as ODT
            self._save_document_as_odt(output_path)
            
            # Close document
            self.document.close(True)
            self.document = None
            
            print(f"✅ Estimate generated: {output_path}")
            
            # Open for human validation if requested
            if open_for_validation:
                self.validator.open_for_validation(output_path, "estimate")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate estimate: {e}")
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
        """Create WaterWizard header styles for estimates"""
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
            
            # Estimate title style (larger than invoice)
            if not para_styles.hasByName("EstimateTitle"):
                estimate_style = self.document.createInstance("com.sun.star.style.ParagraphStyle")
                estimate_style.CharFontName = "Liberation Sans"
                estimate_style.CharHeight = 16
                estimate_style.CharWeight = 150  # Bold
                estimate_style.ParaAdjust = 1    # Center alignment
                estimate_style.CharColor = 0x0066CC  # Blue color
                estimate_style.ParaTopMargin = 200
                estimate_style.ParaBottomMargin = 400
                para_styles.insertByName("EstimateTitle", estimate_style)
            
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
    
    def _add_estimate_header(self, cursor, client_info: Dict[str, Any], 
                           project_info: Dict[str, Any], valid_days: int):
        """Add modern professional estimate header"""
        text = self.document.Text
        
        # Company header
        text.insertString(cursor, "WATERWIZARD IRRIGATION", False)
        cursor.gotoEnd(False)
        text.insertControlCharacter(cursor, LINE_BREAK, False)
        text.insertString(cursor, "Professional Landscape Services", False)
        
        # Apply header style to company name
        cursor.gotoStart(False)
        cursor.goRight(len("WATERWIZARD IRRIGATION"), True)
        cursor.ParaStyleName = "WaterWizardHeader"
        
        cursor.gotoEnd(False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        
        # Estimate title
        text.insertString(cursor, "PROJECT ESTIMATE", False)
        cursor.goLeft(len("PROJECT ESTIMATE"), True)
        cursor.ParaStyleName = "EstimateTitle"
        cursor.gotoEnd(False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        
        # Estimate details
        estimate_number = f"EST-{datetime.now().strftime('%Y%m%d')}-001"
        date_str = datetime.now().strftime("%B %d, %Y")
        valid_until = (datetime.now() + timedelta(days=valid_days)).strftime("%B %d, %Y")
        
        # Create table for estimate details and client info
        self._add_estimate_details_table(cursor, estimate_number, date_str, 
                                       valid_until, client_info, project_info)
    
    def _add_estimate_details_table(self, cursor, estimate_number: str, date_str: str,
                                  valid_until: str, client_info: Dict[str, Any], 
                                  project_info: Dict[str, Any]):
        """Add estimate details and client information in professional table format"""
        try:
            text = self.document.Text
            
            # Create table for estimate header information
            table = self.document.createInstance("com.sun.star.text.TextTable")
            table.initialize(7, 2)  # 7 rows, 2 columns
            
            text.insertTextContent(cursor, table, False)
            
            # Configure table appearance
            table.setPropertyValue("Width", 16000)
            table.setPropertyValue("RelativeWidth", 100)
            
            # Fill table with data
            # Row 1-3: Estimate details
            table.getCellByName("A1").setString("Estimate Number:")
            table.getCellByName("B1").setString(estimate_number)
            
            table.getCellByName("A2").setString("Date:")
            table.getCellByName("B2").setString(date_str)
            
            table.getCellByName("A3").setString("Valid Until:")
            table.getCellByName("B3").setString(valid_until)
            
            # Row 4: Blank separator
            table.getCellByName("A4").setString("")
            table.getCellByName("B4").setString("")
            
            # Rows 5-7: Client and project information
            table.getCellByName("A5").setString("ESTIMATE FOR:")
            client_info_text = f"{client_info.get('name', 'N/A')}\n{client_info.get('address', 'N/A')}\n{client_info.get('city', '')}, {client_info.get('state', '')} {client_info.get('zip', '')}"
            table.getCellByName("B5").setString(client_info_text)
            
            table.getCellByName("A6").setString("PROJECT:")
            table.getCellByName("B6").setString(project_info.get('name', 'N/A'))
            
            table.getCellByName("A7").setString("LOCATION:")
            table.getCellByName("B7").setString(project_info.get('address', client_info.get('address', 'N/A')))
            
            # Style the table cells
            for row in range(1, 8):
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
            print(f"⚠️ Warning: Could not create estimate details table: {e}")
            # Fallback to simple text
            self._add_simple_estimate_header(cursor, estimate_number, date_str, 
                                           valid_until, client_info, project_info)
    
    def _add_simple_estimate_header(self, cursor, estimate_number: str, date_str: str,
                                  valid_until: str, client_info: Dict[str, Any], 
                                  project_info: Dict[str, Any]):
        """Fallback simple text header"""
        text = self.document.Text
        text.insertString(cursor, f"Estimate Number: {estimate_number}", False)
        text.insertControlCharacter(cursor, LINE_BREAK, False)
        text.insertString(cursor, f"Date: {date_str}", False)
        text.insertControlCharacter(cursor, LINE_BREAK, False)
        text.insertString(cursor, f"Valid Until: {valid_until}", False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        
        text.insertString(cursor, f"ESTIMATE FOR: {client_info.get('name', 'N/A')}", False)
        text.insertControlCharacter(cursor, LINE_BREAK, False)
        text.insertString(cursor, f"PROJECT: {project_info.get('name', 'N/A')}", False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
    
    def _add_estimate_body(self, cursor, scope_areas: List[Dict[str, Any]], 
                          subtotal: Decimal, tax_amount: Decimal, total: Decimal):
        """Add estimate body with scope areas in professional format"""
        text = self.document.Text
        
        # Services section header
        text.insertString(cursor, "SCOPE OF WORK BY AREA", False)
        cursor.goLeft(len("SCOPE OF WORK BY AREA"), True)
        cursor.ParaStyleName = "SectionHeader"
        cursor.gotoEnd(False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        
        # Add each scope area
        for scope in scope_areas:
            self._add_scope_area_section(cursor, scope)
        
        # Add project totals at the end
        self._add_project_totals(cursor, subtotal, tax_amount, total)
    
    def _add_scope_area_section(self, cursor, scope: Dict[str, Any]):
        """Add a scope area section with title, description, and breakdown"""
        text = self.document.Text
        
        # Scope area title with cost
        scope_title = scope.get('title', 'Work Area')
        text.insertString(cursor, scope_title, False)
        cursor.goLeft(len(scope_title), True)
        cursor.CharWeight = 150  # Bold
        cursor.CharColor = 0x0066CC  # Blue
        cursor.CharHeight = 14
        cursor.gotoEnd(False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        
        # Scope description
        description = scope.get('description', '')
        if description:
            text.insertString(cursor, description, False)
            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        
        # Materials breakdown (if any)
        materials = scope.get('materials', [])
        if materials:
            text.insertString(cursor, "Materials & Equipment", False)
            text.insertControlCharacter(cursor, LINE_BREAK, False)
            
            # Simple materials table format
            text.insertString(cursor, "Qty     Unit Price    Subtotal    Description", False)
            text.insertControlCharacter(cursor, LINE_BREAK, False)
            
            for material in materials:
                qty = material.get('qty', 0)
                price = material.get('price', 0)
                subtotal = material.get('subtotal', 0)
                desc = material.get('description', '')
                
                line = f"{qty:<7} ${price:<10.2f}   ${subtotal:<9.2f}   {desc}"
                text.insertString(cursor, line, False)
                text.insertControlCharacter(cursor, LINE_BREAK, False)
            
            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        
        # Labor breakdown
        labor = scope.get('labor', [])
        if labor:
            text.insertString(cursor, "Labor", False)
            text.insertControlCharacter(cursor, LINE_BREAK, False)
            
            text.insertString(cursor, "Task                                              Subtotal", False)
            text.insertControlCharacter(cursor, LINE_BREAK, False)
            
            for labor_item in labor:
                task = labor_item.get('task', '')
                labor_subtotal = labor_item.get('subtotal', 0)
                
                line = f"{task:<50} ${labor_subtotal:.2f}"
                text.insertString(cursor, line, False)
                text.insertControlCharacter(cursor, LINE_BREAK, False)
        
        # Equipment breakdown (if any)
        equipment = scope.get('equipment', [])
        if equipment:
            text.insertControlCharacter(cursor, LINE_BREAK, False)
            text.insertString(cursor, "Equipment & Fees", False)
            text.insertControlCharacter(cursor, LINE_BREAK, False)
            
            text.insertString(cursor, "Qty     Unit Price    Subtotal    Description", False)
            text.insertControlCharacter(cursor, LINE_BREAK, False)
            
            for equip_item in equipment:
                qty = equip_item.get('qty', 0)
                price = equip_item.get('price', 0)
                subtotal = equip_item.get('subtotal', 0)
                desc = equip_item.get('description', '')
                
                line = f"{qty:<7} ${price:<10.2f}   ${subtotal:<9.2f}   {desc}"
                text.insertString(cursor, line, False)
                text.insertControlCharacter(cursor, LINE_BREAK, False)
        
        # Add spacing between scope areas
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
    
    def _add_project_totals(self, cursor, subtotal: Decimal, tax_amount: Decimal, total: Decimal):
        """Add project totals section"""
        text = self.document.Text
        
        # Project totals header
        text.insertString(cursor, "PROJECT TOTALS", False)
        cursor.goLeft(len("PROJECT TOTALS"), True)
        cursor.ParaStyleName = "SectionHeader"
        cursor.gotoEnd(False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        
        # Totals breakdown
        text.insertString(cursor, f"Materials & Disposal                              ${subtotal * Decimal('0.1'):.2f}", False)
        text.insertControlCharacter(cursor, LINE_BREAK, False)
        text.insertString(cursor, f"Equipment & Fees                                  ${subtotal * Decimal('0.15'):.2f}", False)
        text.insertControlCharacter(cursor, LINE_BREAK, False)
        text.insertString(cursor, f"Labor                                             ${subtotal * Decimal('0.75'):.2f}", False)
        text.insertControlCharacter(cursor, LINE_BREAK, False)
        
        # Main totals
        text.insertString(cursor, f"Subtotal                                          ${subtotal:.2f}", False)
        text.insertControlCharacter(cursor, LINE_BREAK, False)
        
        if tax_amount > 0:
            text.insertString(cursor, f"Est. Tax                                          ${tax_amount:.2f}", False)
        else:
            text.insertString(cursor, f"Sales Tax (Oregon - No state sales tax)          ${tax_amount:.2f}", False)
        
        text.insertControlCharacter(cursor, LINE_BREAK, False)
        
        # Total with emphasis
        text.insertString(cursor, f"Total Estimated Cost                              ${total:.2f}", False)
        cursor.goLeft(len(f"Total Estimated Cost                              ${total:.2f}"), True)
        cursor.CharWeight = 150  # Bold
        cursor.CharColor = 0x0066CC  # Blue
        cursor.gotoEnd(False)
        
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
    
    def _add_line_items_table(self, cursor, line_items: List[Dict[str, Any]], 
                             subtotal: Decimal, tax_amount: Decimal, total: Decimal):
        """Create professional line items table for estimate"""
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
            
            # Set column widths (with error handling like invoice generator)
            try:
                columns = table.getColumns()
                columns.getByIndex(0).setPropertyValue("RelativeWidth", 50)  # Description
                columns.getByIndex(1).setPropertyValue("RelativeWidth", 15)  # Qty
                columns.getByIndex(2).setPropertyValue("RelativeWidth", 15)  # Rate  
                columns.getByIndex(3).setPropertyValue("RelativeWidth", 20)  # Amount
            except:
                pass  # Skip column sizing if not supported
            
            # Header row
            table.getCellByName("A1").setString("Description")
            table.getCellByName("B1").setString("Qty")
            table.getCellByName("C1").setString("Est. Rate")
            table.getCellByName("D1").setString("Est. Amount")
            
            # Style header row
            for col in ['A', 'B', 'C', 'D']:
                cell = table.getCellByName(f"{col}1")
                cell_cursor = cell.createTextCursor()
                cell_cursor.CharWeight = 150  # Bold
                cell_cursor.CharColor = 0x0066CC
                cell_cursor.ParaAdjust = 1  # Center alignment
            
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
                table.getCellByName(f"C{total_start_row + 2}").setString("EST. TAX:")
                table.getCellByName(f"D{total_start_row + 2}").setString(f"${tax_amount:.2f}")
                total_row = total_start_row + 3
            else:
                table.getCellByName(f"C{total_start_row + 2}").setString("TAX (Oregon - No Sales Tax):")
                table.getCellByName(f"D{total_start_row + 2}").setString("$0.00")
                total_row = total_start_row + 3
            
            # Total
            table.getCellByName(f"C{total_row}").setString("ESTIMATED TOTAL:")
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
        
        text.insertString(cursor, "Description                           Qty    Est. Rate  Est. Amount", False)
        text.insertControlCharacter(cursor, LINE_BREAK, False)
        text.insertString(cursor, "-" * 65, False)
        text.insertControlCharacter(cursor, LINE_BREAK, False)
        
        for item in line_items:
            desc = str(item.get('description', ''))[:30]
            qty = f"{item.get('quantity', 0):.1f}"
            rate = f"${item.get('unit_rate', 0):.2f}"
            amount = f"${item.get('line_total', 0):.2f}"
            
            line = f"{desc:<30} {qty:>5} {rate:>10} {amount:>12}"
            text.insertString(cursor, line, False)
            text.insertControlCharacter(cursor, LINE_BREAK, False)
        
        text.insertControlCharacter(cursor, LINE_BREAK, False)
        text.insertString(cursor, f"SUBTOTAL: ${subtotal:.2f}", False)
        text.insertControlCharacter(cursor, LINE_BREAK, False)
        text.insertString(cursor, f"EST. TAX: ${tax_amount:.2f}", False)
        text.insertControlCharacter(cursor, LINE_BREAK, False)
        text.insertString(cursor, f"ESTIMATED TOTAL: ${total:.2f}", False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
    
    def _add_estimate_footer(self, cursor, valid_days: int):
        """Add professional estimate footer with terms"""
        text = self.document.Text
        
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        
        # Important notice section
        text.insertString(cursor, "IMPORTANT NOTICE", False)
        cursor.goLeft(len("IMPORTANT NOTICE"), True)
        cursor.ParaStyleName = "SectionHeader"
        cursor.gotoEnd(False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        
        notice_text = f"This estimate is valid for {valid_days} days from the date above. Prices are subject to change based on site conditions, material availability, and scope modifications discovered during work."
        text.insertString(cursor, notice_text, False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        
        # Estimate terms section  
        text.insertString(cursor, "ESTIMATE TERMS", False)
        cursor.goLeft(len("ESTIMATE TERMS"), True)
        cursor.ParaStyleName = "SectionHeader"
        cursor.gotoEnd(False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        
        terms = [
            "• This is an estimate only - actual costs may vary based on site conditions",
            "• Final pricing will be confirmed before work begins",
            "• Customer responsible for utility locates prior to work",
            "• Additional charges may apply for unforeseen complications",
            "• Weather delays may affect project timeline",
            "• Site access required for all work areas",
            "• Estimate includes 1-year warranty on installation workmanship"
        ]
        
        for term in terms:
            text.insertString(cursor, term, False)
            text.insertControlCharacter(cursor, LINE_BREAK, False)
        
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        
        # Contact information
        text.insertString(cursor, "Ready to proceed? Contact us at info@waterwizard.com or (555) 123-4567", False)
        cursor.goLeft(len("Ready to proceed? Contact us at info@waterwizard.com or (555) 123-4567"), True)
        cursor.CharHeight = 10
        cursor.CharColor = 0x666666
        cursor.ParaAdjust = 1  # Center
        cursor.gotoEnd(False)
        
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertString(cursor, "WaterWizard Irrigation & Landscape - Professional Services Since 2020", False)
        cursor.goLeft(len("WaterWizard Irrigation & Landscape - Professional Services Since 2020"), True)
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
                
        except Exception as e:
            print(f"⚠️ Error closing UNO connection: {e}")


def main():
    """Test the UNO estimate generator with Liam Smith data"""
    print("📊 WATERWIZARD UNO ESTIMATE GENERATOR - SQUIRT 1.2")
    print("=" * 60)
    
    generator = UnoEstimateGenerator()
    
    try:
        # Liam Smith test data (estimate version)
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
            'name': 'Fall Clean-up 2025 Maintenance Services',
            'address': '6112 SE 77th Ave, Portland, OR'
        }
        
        # Scope areas (organized by work area like Kim Sherertz format)
        scope_areas = [
            {
                "title": "Hollyhock Removal — Estimated $225.00",
                "description": "Deadhead all hollyhocks and remove 80%-90% of existing plants. Includes complete removal of root systems and site preparation.",
                "materials": [
                    {"qty": 1, "price": 40.00, "description": "Disposal Fee", "subtotal": 40.00}
                ],
                "labor": [
                    {"task": "Dead head, prune", "subtotal": 75.00},
                    {"task": "Dig/remove 80%-90% hollyhocks", "subtotal": 150.00}
                ],
                "total": 265.00
            },
            {
                "title": "Tree of Heaven Removal — Estimated $300.00", 
                "description": "Complete Tree of Heaven removal including root ball excavation, cutting, and site restoration to prevent regrowth.",
                "materials": [],
                "labor": [
                    {"task": "Dig and cut root ball", "subtotal": 225.00},
                    {"task": "Setup, backfill & cleanup", "subtotal": 75.00}
                ],
                "total": 300.00
            },
            {
                "title": "Site Cleanup & Disposal — Estimated $100.00",
                "description": "Complete debris collection, proper disposal of all organic matter, and final site cleanup and restoration.",
                "materials": [],
                "equipment": [
                    {"qty": 1, "price": 100.00, "description": "Truck fee", "subtotal": 100.00}
                ],
                "labor": [],
                "total": 100.00
            }
        ]
        
        subtotal = Decimal("665.00")
        tax_amount = Decimal("0.00")  # Oregon no sales tax
        total = Decimal("665.00")
        
        output_path = "/tmp/liam_smith_uno_estimate.odt"
        
        print("📋 Generating estimate with UNO API...")
        print(f"   Valid for: 30 days")
        print(f"   Estimated total: ${total}")
        print()
        
        success = generator.generate_estimate(
            client_info, project_info, scope_areas, 
            subtotal, tax_amount, total, output_path,
            valid_days=30, open_for_validation=True
        )
        
        if success:
            print("✅ UNO Estimate generated successfully!")
            print(f"📄 Output: {output_path}")
            
        else:
            print("❌ Estimate generation failed")
            
    finally:
        generator.close_connection()


if __name__ == "__main__":
    main()