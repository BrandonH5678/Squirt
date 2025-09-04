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
        
        # Contract title - Kim Sherertz format
        text.insertString(cursor, "MAINTENANCE CONTRACT", False)
        cursor.goLeft(len("MAINTENANCE CONTRACT"), True)
        cursor.CharFontName = "Liberation Sans"
        cursor.CharHeight = 18
        cursor.CharWeight = 150  # Bold
        cursor.ParaAdjust = 1    # Center alignment
        cursor.CharColor = 0x000000  # Black like Kim Sherertz
        cursor.gotoEnd(False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        
        # Contract subtitle
        text.insertString(cursor, project_info.get('name', 'Project'), False)
        cursor.goLeft(len(project_info.get('name', 'Project')), True)
        cursor.CharFontName = "Liberation Sans"
        cursor.CharHeight = 16
        cursor.CharWeight = 150  # Bold
        cursor.ParaAdjust = 1    # Center alignment
        cursor.CharColor = 0x000000  # Black
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
            
            # Set column widths - very narrow left, very wide right
            try:
                columns = table.getColumns()
                columns.getByIndex(0).setPropertyValue("RelativeWidth", 25)  # Left column very narrow
                columns.getByIndex(1).setPropertyValue("RelativeWidth", 75)  # Right column very wide
            except:
                pass  # Skip column sizing if not supported
            
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
            
            # Style the table cells - left column bold, right column normal
            for row in range(1, 8):
                # Left column (labels) - bold
                cell = table.getCellByName(f"A{row}")
                cell_cursor = cell.createTextCursor()
                cell_cursor.CharWeight = 150  # Bold
                cell_cursor.CharColor = 0x000000  # Black
                
                # Right column (data) - normal weight
                cell = table.getCellByName(f"B{row}")
                cell_cursor = cell.createTextCursor()  
                cell_cursor.CharWeight = 100  # Normal
                cell_cursor.CharColor = 0x000000  # Black
            
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
        
        # Services section header - Left aligned with line break
        text.insertString(cursor, "SCOPE OF WORK BY CATEGORY", False)
        cursor.goLeft(len("SCOPE OF WORK BY CATEGORY"), True)
        cursor.CharFontName = "Liberation Sans"
        cursor.CharHeight = 14
        cursor.CharWeight = 150  # Bold
        cursor.CharColor = 0x4A90E2  # Kim Sherertz blue
        cursor.ParaAdjust = 0  # Left alignment
        cursor.gotoEnd(False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)  # Extra line break
        
        # Add each scope area
        for scope in scope_areas:
            self._add_scope_area_section(cursor, scope)
        
        # Add project totals at the end
        self._add_project_totals(cursor, subtotal, tax_amount, total)
    
    def _add_scope_area_section(self, cursor, scope: Dict[str, Any]):
        """Add a scope area section with title, description, and breakdown using tables"""
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
        
        # Scope description - smaller black text
        description = scope.get('description', '')
        if description:
            text.insertString(cursor, description, False)
            cursor.goLeft(len(description), True)
            cursor.CharFontName = "Liberation Sans"
            cursor.CharHeight = 11  # Smaller than title
            cursor.CharWeight = 100  # Normal weight
            cursor.CharColor = 0x000000  # Black
            cursor.gotoEnd(False)
            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        
        # Create table for this scope area's breakdown
        self._add_scope_breakdown_table(cursor, scope)
        
        # Add spacing between scope areas
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
    
    def _add_scope_breakdown_table(self, cursor, scope: Dict[str, Any]):
        """Add a professional table for scope area breakdown"""
        try:
            text = self.document.Text
            
            # Determine table rows needed
            materials = scope.get('materials', [])
            labor = scope.get('labor', [])
            equipment = scope.get('equipment', [])
            
            row_count = 0
            if materials: row_count += len(materials) + 2  # header + items + space
            if labor: row_count += len(labor) + 2
            if equipment: row_count += len(equipment) + 2
            
            if row_count == 0:
                return  # No breakdown items
            
            # Create table
            table = self.document.createInstance("com.sun.star.text.TextTable")
            table.initialize(row_count, 4)  # 4 columns: Description, Qty, Rate, Amount
            text.insertTextContent(cursor, table, False)
            
            # Configure table
            table.setPropertyValue("Width", 16000)
            table.setPropertyValue("RelativeWidth", 100)
            
            current_row = 1
            
            # Add materials section
            if materials:
                table.getCellByName(f"A{current_row}").setString("MATERIALS & EQUIPMENT")
                cell = table.getCellByName(f"A{current_row}")
                cell_cursor = cell.createTextCursor()
                cell_cursor.CharWeight = 150
                current_row += 1
                
                for material in materials:
                    qty = f"{material.get('qty', 0)}"
                    price = f"${material.get('price', 0):.2f}"
                    subtotal = f"${material.get('subtotal', 0):.2f}"
                    desc = material.get('description', '')
                    
                    table.getCellByName(f"A{current_row}").setString(desc)
                    table.getCellByName(f"B{current_row}").setString(qty)
                    table.getCellByName(f"C{current_row}").setString(price)
                    table.getCellByName(f"D{current_row}").setString(subtotal)
                    current_row += 1
                
                current_row += 1  # Space
            
            # Add labor section
            if labor:
                table.getCellByName(f"A{current_row}").setString("LABOR")
                cell = table.getCellByName(f"A{current_row}")
                cell_cursor = cell.createTextCursor()
                cell_cursor.CharWeight = 150
                current_row += 1
                
                for labor_item in labor:
                    task = labor_item.get('task', '')
                    labor_subtotal = f"${labor_item.get('subtotal', 0):.2f}"
                    
                    table.getCellByName(f"A{current_row}").setString(task)
                    table.getCellByName(f"D{current_row}").setString(labor_subtotal)
                    current_row += 1
                
                current_row += 1  # Space
                
            # Add equipment section
            if equipment:
                table.getCellByName(f"A{current_row}").setString("EQUIPMENT & FEES")
                cell = table.getCellByName(f"A{current_row}")
                cell_cursor = cell.createTextCursor()
                cell_cursor.CharWeight = 150
                current_row += 1
                
                for equip_item in equipment:
                    qty = f"{equip_item.get('qty', 0)}"
                    price = f"${equip_item.get('price', 0):.2f}"
                    subtotal = f"${equip_item.get('subtotal', 0):.2f}"
                    desc = equip_item.get('description', '')
                    
                    table.getCellByName(f"A{current_row}").setString(desc)
                    table.getCellByName(f"B{current_row}").setString(qty)
                    table.getCellByName(f"C{current_row}").setString(price)
                    table.getCellByName(f"D{current_row}").setString(subtotal)
                    current_row += 1
            
            # Move cursor after table
            cursor.gotoEnd(False)
            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
            
        except Exception as e:
            print(f"⚠️ Warning: Could not create scope breakdown table: {e}")
            # Fallback to simple text
            self._add_simple_scope_breakdown(cursor, scope)

    def _add_simple_scope_breakdown(self, cursor, scope: Dict[str, Any]):
        """Fallback simple text breakdown"""
        text = self.document.Text
        
        materials = scope.get('materials', [])
        labor = scope.get('labor', [])
        equipment = scope.get('equipment', [])
        
        if materials:
            text.insertString(cursor, "Materials & Equipment:", False)
            text.insertControlCharacter(cursor, LINE_BREAK, False)
            for material in materials:
                line = f"  {material.get('qty', 0)} x ${material.get('price', 0):.2f} = ${material.get('subtotal', 0):.2f} {material.get('description', '')}"
                text.insertString(cursor, line, False)
                text.insertControlCharacter(cursor, LINE_BREAK, False)
        
        if labor:
            text.insertString(cursor, "Labor:", False)
            text.insertControlCharacter(cursor, LINE_BREAK, False)
            for labor_item in labor:
                line = f"  {labor_item.get('task', '')} - ${labor_item.get('subtotal', 0):.2f}"
                text.insertString(cursor, line, False)
                text.insertControlCharacter(cursor, LINE_BREAK, False)
        
        if equipment:
            text.insertString(cursor, "Equipment & Fees:", False)
            text.insertControlCharacter(cursor, LINE_BREAK, False)
            for equip_item in equipment:
                line = f"  {equip_item.get('qty', 0)} x ${equip_item.get('price', 0):.2f} = ${equip_item.get('subtotal', 0):.2f} {equip_item.get('description', '')}"
                text.insertString(cursor, line, False)
                text.insertControlCharacter(cursor, LINE_BREAK, False)

    def _add_project_totals_table(self, cursor, subtotal: Decimal, tax_amount: Decimal, total: Decimal):
        """Add project totals in a professional table format"""
        try:
            text = self.document.Text
            
            # Create simple totals table
            table = self.document.createInstance("com.sun.star.text.TextTable")
            table.initialize(4, 2)  # 4 rows for totals
            text.insertTextContent(cursor, table, False)
            
            # Configure table
            table.setPropertyValue("Width", 16000)
            table.setPropertyValue("RelativeWidth", 100)
            
            # Set column widths for totals table
            try:
                columns = table.getColumns()
                columns.getByIndex(0).setPropertyValue("RelativeWidth", 60)  # Left column 
                columns.getByIndex(1).setPropertyValue("RelativeWidth", 40)  # Right column
            except:
                pass
            
            # Subtotal
            table.getCellByName("A1").setString("Subtotal")
            table.getCellByName("B1").setString(f"${subtotal:.2f}")
            
            # Tax
            if tax_amount > 0:
                table.getCellByName("A2").setString("Est. Tax")
                table.getCellByName("B2").setString(f"${tax_amount:.2f}")
            else:
                table.getCellByName("A2").setString("Sales Tax (Oregon - No Sales Tax)")
                table.getCellByName("B2").setString("$0.00")
            
            # Contingency (5% buffer typically included in total)
            contingency = total - subtotal - tax_amount
            table.getCellByName("A3").setString("Contingency & Buffer")
            table.getCellByName("B3").setString(f"${contingency:.2f}")
            
            # Total
            table.getCellByName("A4").setString("TOTAL ESTIMATED COST")
            table.getCellByName("B4").setString(f"${total:.2f}")
            
            # Style the total row
            for col in ['A', 'B']:
                cell = table.getCellByName(f"{col}4")
                cell_cursor = cell.createTextCursor()
                cell_cursor.CharWeight = 150  # Bold
                cell_cursor.CharColor = 0x0066CC  # Blue
            
            # Right-align amounts
            for row in range(1, 5):
                cell = table.getCellByName(f"B{row}")
                cell_cursor = cell.createTextCursor()
                cell_cursor.ParaAdjust = 2  # Right align
                
                # Style labels
                cell = table.getCellByName(f"A{row}")
                cell_cursor = cell.createTextCursor()
                cell_cursor.CharWeight = 150  # Bold
            
            cursor.gotoEnd(False)
            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
            
        except Exception as e:
            print(f"⚠️ Warning: Could not create totals table: {e}")
            # Fallback to simple text
            text.insertString(cursor, f"Subtotal: ${subtotal:.2f}", False)
            text.insertControlCharacter(cursor, LINE_BREAK, False)
            text.insertString(cursor, f"Tax: ${tax_amount:.2f}", False)  
            text.insertControlCharacter(cursor, LINE_BREAK, False)
            text.insertString(cursor, f"TOTAL: ${total:.2f}", False)

    def _add_project_totals(self, cursor, subtotal: Decimal, tax_amount: Decimal, total: Decimal):
        """Add project totals section with proper table formatting"""
        text = self.document.Text
        
        # Project totals header
        text.insertString(cursor, "PROJECT TOTALS", False)
        cursor.goLeft(len("PROJECT TOTALS"), True)
        cursor.ParaStyleName = "SectionHeader"
        cursor.gotoEnd(False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        
        self._add_project_totals_table(cursor, subtotal, tax_amount, total)
        
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
        
        # Contact information - updated from manual edits
        text.insertString(cursor, "Ready to proceed? Contact us at waterwizardpdx@gmail.com or (707) 845-4714", False)
        cursor.goLeft(len("Ready to proceed? Contact us at waterwizardpdx@gmail.com or (707) 845-4714"), True)
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
            'name': 'Fall Clean-up – Liam Smith Property',
            'address': '6112 SE 77th Ave, Portland, OR'
        }
        
        # Scope areas (Fall Clean-up contract with 3 distinct scope areas)
        scope_areas = [
            {
                "title": "Fall Clean-up — $315.00",
                "description": "Baseline fall landscape cleanup and maintenance service including deadheading, pruning, plant removal, and debris collection. Includes specific hollyhock removal as part of comprehensive seasonal cleanup.",
                "materials": [
                    {"qty": 1, "price": 40.00, "description": "Disposal Fee", "subtotal": 40.00}
                ],
                "labor": [
                    {"task": "Dead head, prune various plants", "subtotal": 75.00},
                    {"task": "Dig/remove 80%-90% hollyhocks", "subtotal": 150.00},
                    {"task": "General debris collection & cleanup", "subtotal": 50.00}
                ],
                "total": 315.00
            },
            {
                "title": "Tree of Heaven Removal — $300.00", 
                "description": "Complete Tree of Heaven removal including root ball excavation, cutting, and site restoration. This is additional scope beyond routine fall cleanup.",
                "materials": [],
                "labor": [
                    {"task": "Dig and cut root ball", "subtotal": 225.00},
                    {"task": "Setup, backfill & cleanup", "subtotal": 75.00}
                ],
                "total": 300.00
            },
            {
                "title": "Laurel Hedge Pruning — $162.50",
                "description": "Specialized pruning of Laurel hedge away from house structure and clearing sideyard travel areas. Additional scope beyond routine cleanup.",
                "materials": [],
                "equipment": [
                    {"qty": 1, "price": 100.00, "description": "Truck fee", "subtotal": 100.00}
                ],
                "labor": [
                    {"task": "Prune Laurel hedge", "subtotal": 37.50},
                    {"task": "Debris disposal", "subtotal": 25.00}
                ],
                "total": 162.50
            }
        ]
        
        subtotal = Decimal("777.50")
        tax_amount = Decimal("0.00")  # Oregon no sales tax
        total = Decimal("777.50")
        
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