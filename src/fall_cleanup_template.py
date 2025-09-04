#!/usr/bin/env python3
"""
Fall Clean-up Contract Template Generator
Based on manually refined Liam Smith estimate structure
Template for WaterWizard's Fall Clean-up service contracts
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


class FallCleanupTemplate:
    """Template generator for Fall Clean-up contracts based on refined structure"""
    
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
    
    def generate_fall_cleanup_contract(self, client_info: Dict[str, Any], 
                                     cleanup_scope: Dict[str, Any],
                                     additional_scopes: List[Dict[str, Any]] = None,
                                     output_path: str = None,
                                     valid_days: int = 30) -> bool:
        """
        Generate Fall Clean-up contract using the refined template structure
        
        Args:
            client_info: Client details (name, address, phone, email)
            cleanup_scope: Main fall cleanup scope with tasks and pricing
            additional_scopes: List of additional scopes (tree removal, pruning, etc)
            output_path: Where to save the contract
            valid_days: Contract validity period
            
        Returns:
            bool: Success status
        """
        
        if not self.document:
            self.document = self.desktop.loadComponentFromURL(
                "private:factory/swriter", "_blank", 0, ()
            )
        
        try:
            # Get document text and cursor
            text = self.document.Text
            cursor = text.createTextCursor()
            
            # Set up document formatting
            self._setup_document_styles()
            
            # Generate contract content
            self._add_contract_header(cursor, client_info)
            self._add_contract_details_table(cursor, client_info, valid_days)
            self._add_scope_sections(cursor, cleanup_scope, additional_scopes or [])
            self._add_project_totals(cursor, cleanup_scope, additional_scopes or [])
            self._add_contract_footer(cursor, valid_days)
            
            # Save document
            if output_path:
                self._save_document_as_odt(output_path)
                print(f"✅ Fall Clean-up contract generated: {output_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate Fall Clean-up contract: {e}")
            if self.document:
                try:
                    self.document.close(False)
                except:
                    pass
                self.document = None
            return False
    
    def _setup_document_styles(self):
        """Configure document-wide styles matching manual edits"""
        try:
            # Get style families
            style_families = self.document.StyleFamilies
            para_styles = style_families.getByName("ParagraphStyles")
            
            # Configure page style for margins
            page_styles = style_families.getByName("PageStyles")
            page_style = page_styles.getByName("Standard")
            
            # Set margins (in millimeters * 100)
            page_style.LeftMargin = 2000   # 20mm
            page_style.RightMargin = 2000  # 20mm
            page_style.TopMargin = 2000    # 20mm
            page_style.BottomMargin = 2000 # 20mm
            
        except Exception as e:
            print(f"⚠️ Warning: Could not setup document styles: {e}")
    
    def _add_contract_header(self, cursor, client_info: Dict[str, Any]):
        """Add contract header with proper styling"""
        text = self.document.Text
        
        # Contract title
        text.insertString(cursor, "MAINTENANCE CONTRACT", False)
        cursor.goLeft(len("MAINTENANCE CONTRACT"), True)
        cursor.CharFontName = "Liberation Sans"
        cursor.CharHeight = 18
        cursor.CharWeight = 150  # Bold
        cursor.ParaAdjust = 1    # Center alignment
        cursor.CharColor = 0x000000  # Black
        cursor.gotoEnd(False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        
        # Contract subtitle - dynamic project name
        project_title = f"Fall Clean-up – {client_info.get('name', 'Client')} Property"
        text.insertString(cursor, project_title, False)
        cursor.goLeft(len(project_title), True)
        cursor.CharFontName = "Liberation Sans"
        cursor.CharHeight = 16
        cursor.CharWeight = 150  # Bold
        cursor.ParaAdjust = 1    # Center alignment
        cursor.CharColor = 0x000000  # Black
        cursor.gotoEnd(False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
    
    def _add_contract_details_table(self, cursor, client_info: Dict[str, Any], valid_days: int):
        """Add contract details table with proper formatting"""
        try:
            text = self.document.Text
            
            # Create table for contract header information
            table = self.document.createInstance("com.sun.star.text.TextTable")
            table.initialize(7, 2)  # 7 rows, 2 columns
            
            text.insertTextContent(cursor, table, False)
            
            # Configure table appearance  
            table.setPropertyValue("Width", 16000)
            table.setPropertyValue("RelativeWidth", 100)
            
            # Set column widths - narrow left, wide right
            try:
                columns = table.getColumns()
                columns.getByIndex(0).setPropertyValue("RelativeWidth", 25)  # Left column narrow
                columns.getByIndex(1).setPropertyValue("RelativeWidth", 75)  # Right column wide
            except:
                pass
            
            # Fill table with data
            estimate_number = f"EST-{datetime.now().strftime('%Y%m%d')}-001"
            date_str = datetime.now().strftime("%B %d, %Y")
            valid_until = (datetime.now() + timedelta(days=valid_days)).strftime("%B %d, %Y")
            
            table.getCellByName("A1").setString("Estimate Number:")
            table.getCellByName("B1").setString(estimate_number)
            
            table.getCellByName("A2").setString("Date:")
            table.getCellByName("B2").setString(date_str)
            
            table.getCellByName("A3").setString("Valid Until:")
            table.getCellByName("B3").setString(valid_until)
            
            table.getCellByName("A4").setString("")
            table.getCellByName("B4").setString("")
            
            table.getCellByName("A5").setString("ESTIMATE FOR:")
            client_info_text = f"{client_info.get('name', 'N/A')}\\n{client_info.get('address', 'N/A')}\\n{client_info.get('city', '')}, {client_info.get('state', '')} {client_info.get('zip', '')}"
            table.getCellByName("B5").setString(client_info_text)
            
            table.getCellByName("A6").setString("PROJECT:")
            table.getCellByName("B6").setString(f"Fall Clean-up – {client_info.get('name', 'Client')} Property")
            
            table.getCellByName("A7").setString("LOCATION:")
            table.getCellByName("B7").setString(client_info.get('address', 'N/A'))
            
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
            print(f"⚠️ Warning: Could not create contract details table: {e}")
    
    def _add_scope_sections(self, cursor, cleanup_scope: Dict[str, Any], additional_scopes: List[Dict[str, Any]]):
        """Add all scope sections with proper formatting"""
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
        
        # Add main cleanup scope
        self._add_single_scope_section(cursor, cleanup_scope)
        
        # Add additional scopes
        for scope in additional_scopes:
            self._add_single_scope_section(cursor, scope)
    
    def _add_single_scope_section(self, cursor, scope: Dict[str, Any]):
        """Add a single scope section with title and description"""
        text = self.document.Text
        
        # Scope area title
        scope_title = scope.get('title', 'Work Area')
        text.insertString(cursor, scope_title, False)
        cursor.goLeft(len(scope_title), True)
        cursor.CharWeight = 150  # Bold
        cursor.CharColor = 0x4A90E2  # Blue
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
        
        # Add breakdown table for this scope
        self._add_scope_breakdown_table(cursor, scope)
        
        # Add spacing
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
    
    def _add_scope_breakdown_table(self, cursor, scope: Dict[str, Any]):
        """Add breakdown table for a scope area"""
        try:
            text = self.document.Text
            
            # Determine items to include
            materials = scope.get('materials', [])
            labor = scope.get('labor', [])
            equipment = scope.get('equipment', [])
            
            total_items = len(materials) + len(labor) + len(equipment)
            if total_items == 0:
                return
            
            # Create table with header
            table = self.document.createInstance("com.sun.star.text.TextTable")
            table.initialize(total_items + 1, 4)  # +1 for header
            text.insertTextContent(cursor, table, False)
            
            # Configure table
            table.setPropertyValue("Width", 16000)
            table.setPropertyValue("RelativeWidth", 100)
            
            # Header row
            table.getCellByName("A1").setString("Description")
            table.getCellByName("B1").setString("Quantity")
            table.getCellByName("C1").setString("Price")
            table.getCellByName("D1").setString("Subtotal")
            
            # Style header
            for col in ['A', 'B', 'C', 'D']:
                cell = table.getCellByName(f"{col}1")
                cell_cursor = cell.createTextCursor()
                cell_cursor.CharWeight = 150  # Bold
            
            current_row = 2
            
            # Add materials
            for material in materials:
                table.getCellByName(f"A{current_row}").setString(material.get('description', ''))
                table.getCellByName(f"B{current_row}").setString(str(material.get('qty', '')))
                table.getCellByName(f"C{current_row}").setString(f"${material.get('price', 0):.2f}")
                table.getCellByName(f"D{current_row}").setString(f"${material.get('subtotal', 0):.2f}")
                current_row += 1
            
            # Add labor
            for labor_item in labor:
                table.getCellByName(f"A{current_row}").setString(labor_item.get('task', ''))
                table.getCellByName(f"D{current_row}").setString(f"${labor_item.get('subtotal', 0):.2f}")
                current_row += 1
            
            # Add equipment
            for equip_item in equipment:
                table.getCellByName(f"A{current_row}").setString(equip_item.get('description', ''))
                table.getCellByName(f"B{current_row}").setString(str(equip_item.get('qty', '')))
                table.getCellByName(f"C{current_row}").setString(f"${equip_item.get('price', 0):.2f}")
                table.getCellByName(f"D{current_row}").setString(f"${equip_item.get('subtotal', 0):.2f}")
                current_row += 1
            
            cursor.gotoEnd(False)
            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
            
        except Exception as e:
            print(f"⚠️ Warning: Could not create scope breakdown table: {e}")
    
    def _add_project_totals(self, cursor, cleanup_scope: Dict[str, Any], additional_scopes: List[Dict[str, Any]]):
        """Add project totals section"""
        text = self.document.Text
        
        # Calculate totals
        subtotal = Decimal(str(cleanup_scope.get('total', 0)))
        for scope in additional_scopes:
            subtotal += Decimal(str(scope.get('total', 0)))
        
        tax_amount = Decimal('0.00')  # Oregon no sales tax
        total = subtotal + tax_amount
        
        # Project totals header
        text.insertString(cursor, "PROJECT TOTALS", False)
        cursor.goLeft(len("PROJECT TOTALS"), True)
        cursor.CharFontName = "Liberation Sans"
        cursor.CharHeight = 14
        cursor.CharWeight = 150  # Bold
        cursor.CharColor = 0x4A90E2  # Blue
        cursor.gotoEnd(False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        
        # Create totals table
        try:
            table = self.document.createInstance("com.sun.star.text.TextTable")
            table.initialize(3, 2)  # 3 rows for totals
            text.insertTextContent(cursor, table, False)
            
            # Configure table
            table.setPropertyValue("Width", 16000)
            table.setPropertyValue("RelativeWidth", 100)
            
            # Subtotal
            table.getCellByName("A1").setString("Subtotal")
            table.getCellByName("B1").setString(f"${subtotal:.2f}")
            
            # Tax
            table.getCellByName("A2").setString("Sales Tax (Oregon - No Sales Tax)")
            table.getCellByName("B2").setString("$0.00")
            
            # Total
            table.getCellByName("A3").setString("TOTAL ESTIMATED COST")
            table.getCellByName("B3").setString(f"${total:.2f}")
            
            # Style totals
            for row in range(1, 4):
                # Left column bold
                cell = table.getCellByName(f"A{row}")
                cell_cursor = cell.createTextCursor()
                cell_cursor.CharWeight = 150  # Bold
                
                # Right column alignment
                cell = table.getCellByName(f"B{row}")
                cell_cursor = cell.createTextCursor()
                cell_cursor.ParaAdjust = 2  # Right align
                
                if row == 3:  # Total row
                    cell_cursor.CharWeight = 150  # Bold
                    cell_cursor.CharColor = 0x4A90E2  # Blue
            
            cursor.gotoEnd(False)
            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
            
        except Exception as e:
            print(f"⚠️ Warning: Could not create totals table: {e}")
    
    def _add_contract_footer(self, cursor, valid_days: int):
        """Add contract footer with terms and contact info"""
        text = self.document.Text
        
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        
        # Important notice
        text.insertString(cursor, "IMPORTANT NOTICE", False)
        cursor.goLeft(len("IMPORTANT NOTICE"), True)
        cursor.CharFontName = "Liberation Sans"
        cursor.CharHeight = 12
        cursor.CharWeight = 150  # Bold
        cursor.CharColor = 0x4A90E2  # Blue
        cursor.gotoEnd(False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        
        notice_text = f"This estimate is valid for {valid_days} days from the date above. Prices are subject to change based on site conditions, material availability, and scope modifications discovered during work."
        text.insertString(cursor, notice_text, False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        
        # Estimate terms
        text.insertString(cursor, "ESTIMATE TERMS", False)
        cursor.goLeft(len("ESTIMATE TERMS"), True)
        cursor.CharFontName = "Liberation Sans"
        cursor.CharHeight = 12
        cursor.CharWeight = 150  # Bold
        cursor.CharColor = 0x4A90E2  # Blue
        cursor.gotoEnd(False)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        
        terms = [
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
    """Test the Fall Clean-up template with sample data"""
    print("🍂 FALL CLEAN-UP TEMPLATE GENERATOR")
    print("=" * 50)
    
    generator = FallCleanupTemplate()
    
    try:
        # Sample client data
        client_info = {
            'name': 'Sample Client',
            'address': '123 Main St',
            'city': 'Portland',
            'state': 'OR',
            'zip': '97205',
            'phone': '503-555-0123',
            'email': 'client@email.com'
        }
        
        # Main fall cleanup scope
        cleanup_scope = {
            "title": "Fall Clean-up — $315.00",
            "description": "Baseline fall landscape cleanup and maintenance service including deadheading, pruning, plant removal, and debris collection. Includes specific plant removal as part of comprehensive seasonal cleanup.",
            "materials": [
                {"qty": 1, "price": 40.00, "description": "Disposal Fee", "subtotal": 40.00}
            ],
            "labor": [
                {"task": "Dead head, prune various plants", "subtotal": 75.00},
                {"task": "Plant removal (specify type)", "subtotal": 150.00},
                {"task": "General debris collection & cleanup", "subtotal": 50.00}
            ],
            "total": 315.00
        }
        
        # Additional scopes (customizable per project)
        additional_scopes = [
            {
                "title": "Specialized Tree Removal — $300.00", 
                "description": "Complete tree removal including root ball excavation, cutting, and site restoration. This is additional scope beyond routine fall cleanup.",
                "materials": [],
                "labor": [
                    {"task": "Dig and cut root ball", "subtotal": 225.00},
                    {"task": "Setup, backfill & cleanup", "subtotal": 75.00}
                ],
                "total": 300.00
            }
        ]
        
        output_path = "/tmp/fall_cleanup_template_sample.odt"
        
        success = generator.generate_fall_cleanup_contract(
            client_info, cleanup_scope, additional_scopes, output_path
        )
        
        if success:
            print("✅ Fall Clean-up template generated successfully!")
            print(f"📄 Output: {output_path}")
            
        else:
            print("❌ Template generation failed")
            
    finally:
        generator.close_connection()


if __name__ == "__main__":
    main()