#!/usr/bin/env python3
"""
Modern Document Generator for WaterWizard
Uses LibreOffice templates with professional formatting instead of ASCII art
"""

import os
import subprocess
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Dict, List, Any, Optional
import json

from template_processor import TemplateProcessor
from tax_rules import TaxRulesEngine
from fixed_odt_generator import FixedODTGenerator, open_document_for_human_review

class ModernDocumentGenerator:
    """
    Professional document generator using LibreOffice ODT templates
    """
    
    def __init__(self):
        self.processor = TemplateProcessor()
        self.tax_engine = TaxRulesEngine()
        self.template_dir = Path(__file__).parent / "document_templates"
        self.template_dir.mkdir(exist_ok=True)
        
        # Initialize the fixed ODT generator
        self.odt_generator = FixedODTGenerator()
        
        # Create base templates if they don't exist
        self._ensure_base_templates()
        
        # Ensure modern professional template exists
        self._ensure_modern_professional_template()
        
    def _ensure_base_templates(self):
        """Create base ODT templates if they don't exist"""
        contract_template = self.template_dir / "contract_template.odt"
        invoice_template = self.template_dir / "invoice_template.odt"
        
        if not contract_template.exists():
            self._create_contract_template(str(contract_template))
            
        if not invoice_template.exists():
            self._create_invoice_template(str(invoice_template))
    
    def _create_contract_template(self, output_path: str):
        """Create a professional contract template ODT file"""
        
        # Create a minimal ODT structure
        content_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<office:document-content 
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0">

<office:automatic-styles>
    <style:style style:name="CompanyHeader" style:family="paragraph">
        <style:paragraph-properties fo:text-align="center" fo:margin-top="0.2in"/>
        <style:text-properties fo:font-size="18pt" fo:font-weight="bold" fo:color="#1f4e79"/>
    </style:style>
    
    <style:style style:name="SubHeader" style:family="paragraph">
        <style:paragraph-properties fo:text-align="center" fo:margin-bottom="0.3in"/>
        <style:text-properties fo:font-size="14pt" fo:color="#4472c4"/>
    </style:style>
    
    <style:style style:name="SectionHeader" style:family="paragraph">
        <style:paragraph-properties fo:margin-top="0.2in" fo:margin-bottom="0.1in" 
                                   fo:border-bottom="2pt solid #4472c4"/>
        <style:text-properties fo:font-size="12pt" fo:font-weight="bold" fo:color="#1f4e79"/>
    </style:style>
    
    <style:style style:name="ContractTable" style:family="table">
        <style:table-properties style:width="100%" table:align="margins"/>
    </style:style>
    
    <style:style style:name="TableHeader" style:family="table-cell">
        <style:table-cell-properties fo:background-color="#4472c4" fo:border="1pt solid #1f4e79"/>
        <style:text-properties fo:color="#ffffff" fo:font-weight="bold"/>
    </style:style>
    
    <style:style style:name="TableCell" style:family="table-cell">
        <style:table-cell-properties fo:border="0.5pt solid #d0d0d0"/>
    </style:style>
    
    <style:style style:name="TotalRow" style:family="table-cell">
        <style:table-cell-properties fo:background-color="#f2f2f2" fo:border="1pt solid #1f4e79"/>
        <style:text-properties fo:font-weight="bold"/>
    </style:style>
</office:automatic-styles>

<office:body>
<office:text>

<!-- Header Section -->
<text:p text:style-name="CompanyHeader">WATERWIZARD IRRIGATION</text:p>
<text:p text:style-name="SubHeader">Professional Installation Contract</text:p>

<!-- Contract Info -->
<text:p>CONTRACT NUMBER: {{CONTRACT_NUMBER}}</text:p>
<text:p>DATE: {{CONTRACT_DATE}}</text:p>
<text:p></text:p>

<!-- Client and Company Info Table -->
<table:table table:name="InfoTable" table:style-name="ContractTable">
    <table:table-column table:style-name="InfoCol"/>
    <table:table-column table:style-name="InfoCol"/>
    
    <table:table-row>
        <table:table-cell table:style-name="TableCell">
            <text:p><text:span text:style-name="Bold">PREPARED FOR:</text:span></text:p>
            <text:p>{{CLIENT_NAME}}</text:p>
            <text:p>{{CLIENT_ADDRESS}}</text:p>
            <text:p>{{CLIENT_CITY}}, {{CLIENT_STATE}} {{CLIENT_ZIP}}</text:p>
            <text:p>Phone: {{CLIENT_PHONE}}</text:p>
            <text:p>Email: {{CLIENT_EMAIL}}</text:p>
        </table:table-cell>
        
        <table:table-cell table:style-name="TableCell">
            <text:p><text:span text:style-name="Bold">PREPARED BY:</text:span></text:p>
            <text:p>WaterWizard Irrigation &amp; Landscape</text:p>
            <text:p>Professional Irrigation Services</text:p>
            <text:p>Phone: (555) 123-4567</text:p>
            <text:p>Email: info@waterwizard.com</text:p>
        </table:table-cell>
    </table:table-row>
</table:table>

<text:p></text:p>
<text:p>PROJECT: {{PROJECT_NAME}}</text:p>
<text:p>LOCATION: {{PROJECT_ADDRESS}}</text:p>

<!-- Project Description -->
<text:p text:style-name="SectionHeader">PROJECT DESCRIPTION</text:p>
<text:p>{{PROJECT_DESCRIPTION}}</text:p>

<!-- Line Items Table -->
<text:p text:style-name="SectionHeader">MATERIALS &amp; EQUIPMENT BREAKDOWN</text:p>

<table:table table:name="LineItemsTable" table:style-name="ContractTable">
    <table:table-column table:style-name="DescCol"/>
    <table:table-column table:style-name="QtyCol"/>
    <table:table-column table:style-name="RateCol"/>
    <table:table-column table:style-name="TotalCol"/>
    
    <table:table-row>
        <table:table-cell table:style-name="TableHeader">
            <text:p>Description</text:p>
        </table:table-cell>
        <table:table-cell table:style-name="TableHeader">
            <text:p>Qty</text:p>
        </table:table-cell>
        <table:table-cell table:style-name="TableHeader">
            <text:p>Rate</text:p>
        </table:table-cell>
        <table:table-cell table:style-name="TableHeader">
            <text:p>Total</text:p>
        </table:table-cell>
    </table:table-row>
    
    {{LINE_ITEMS_ROWS}}
    
    <!-- Totals Section -->
    <table:table-row>
        <table:table-cell table:style-name="TotalRow" table:number-columns-spanned="3">
            <text:p>SUBTOTAL:</text:p>
        </table:table-cell>
        <table:table-cell table:style-name="TotalRow">
            <text:p>${{SUBTOTAL}}</text:p>
        </table:table-cell>
    </table:table-row>
    
    <table:table-row>
        <table:table-cell table:style-name="TotalRow" table:number-columns-spanned="3">
            <text:p>TAX ({{TAX_RATE}}%):</text:p>
        </table:table-cell>
        <table:table-cell table:style-name="TotalRow">
            <text:p>${{TAX_AMOUNT}}</text:p>
        </table:table-cell>
    </table:table-row>
    
    <table:table-row>
        <table:table-cell table:style-name="TotalRow" table:number-columns-spanned="3">
            <text:p><text:span text:style-name="Bold">TOTAL:</text:span></text:p>
        </table:table-cell>
        <table:table-cell table:style-name="TotalRow">
            <text:p><text:span text:style-name="Bold">${{GRAND_TOTAL}}</text:span></text:p>
        </table:table-cell>
    </table:table-row>
</table:table>

<!-- Terms and Conditions -->
<text:p text:style-name="SectionHeader">TERMS AND CONDITIONS</text:p>
<text:list>
    <text:list-item><text:p>Work includes 1-year warranty on installation workmanship</text:p></text:list-item>
    <text:list-item><text:p>Materials warranted per manufacturer specifications</text:p></text:list-item>
    <text:list-item><text:p>Customer responsible for utility locates prior to work</text:p></text:list-item>
    <text:list-item><text:p>Payment due upon completion of work</text:p></text:list-item>
    <text:list-item><text:p>Weather delays may affect completion date</text:p></text:list-item>
    <text:list-item><text:p>Site access required for all work areas</text:p></text:list-item>
</text:list>

<!-- Signature Section -->
<text:p text:style-name="SectionHeader">ACCEPTANCE</text:p>
<text:p></text:p>
<text:p>Customer: ________________________________    Date: _______________</text:p>
<text:p></text:p>
<text:p>WaterWizard Representative: ________________    Date: {{CONTRACT_DATE}}</text:p>

</office:text>
</office:body>
</office:document-content>'''

        self._create_odt_file(output_path, content_xml, "contract")
    
    def _ensure_modern_professional_template(self):
        """Create modern professional template if it doesn't exist"""
        modern_template = self.template_dir / "modern_professional_template.odt"
        
        if not modern_template.exists():
            self._create_modern_professional_template(str(modern_template))
    
    def _create_modern_professional_template(self, output_path: str):
        """Create a minimal valid ODT template using LibreOffice standard format"""
        
        # Use the most basic valid ODT content structure
        content_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" office:version="1.2">
 <office:scripts/>
 <office:font-face-decls>
  <style:font-face style:name="Liberation Serif" svg:font-family="'Liberation Serif'" style:font-family-generic="roman" style:font-pitch="variable"/>
 </office:font-face-decls>
 <office:automatic-styles>
  <style:style style:name="P1" style:family="paragraph" style:parent-style-name="Standard">
   <style:text-properties fo:font-size="16pt" fo:font-weight="bold"/>
  </style:style>
  <style:style style:name="P2" style:family="paragraph" style:parent-style-name="Standard">
   <style:text-properties fo:font-size="12pt" fo:font-weight="bold" fo:color="#4472c4"/>
  </style:style>
  <style:style style:name="T1" style:family="text">
   <style:text-properties fo:font-weight="bold"/>
  </style:style>
 </office:automatic-styles>
 <office:body>
  <office:text>
   <text:p text:style-name="P1">CONSTRUCTION CONTRACT</text:p>
   <text:p text:style-name="Standard">{{PROJECT_DESCRIPTION_SHORT}}</text:p>
   <text:p text:style-name="Standard"/>
   <text:p text:style-name="Standard"><text:span text:style-name="T1">Prepared for:</text:span></text:p>
   <text:p text:style-name="Standard">{{CLIENT_NAME}}</text:p>
   <text:p text:style-name="Standard">{{CLIENT_ADDRESS}}</text:p>
   <text:p text:style-name="Standard">{{CLIENT_CITY}}, {{CLIENT_STATE}} {{CLIENT_ZIP}}</text:p>
   <text:p text:style-name="Standard"/>
   <text:p text:style-name="Standard"><text:span text:style-name="T1">Prepared by:</text:span></text:p>
   <text:p text:style-name="Standard">{{CONTRACTOR_NAME}}</text:p>
   <text:p text:style-name="Standard">{{CONTRACTOR_ADDRESS}}</text:p>
   <text:p text:style-name="Standard">{{CONTRACTOR_CITY}}, {{CONTRACTOR_STATE}} {{CONTRACTOR_ZIP}}</text:p>
   <text:p text:style-name="Standard">{{CONTRACTOR_PHONE}}</text:p>
   <text:p text:style-name="Standard">{{CONTRACTOR_EMAIL}}</text:p>
   <text:p text:style-name="Standard"/>
   <text:p text:style-name="P2">PROJECT SUMMARY</text:p>
   <text:p text:style-name="Standard">{{PROJECT_DESCRIPTION}}</text:p>
   <text:p text:style-name="Standard"/>
   <text:p text:style-name="P2">PROJECT TOTALS</text:p>
   <text:p text:style-name="Standard">Materials and Equipment: ${{MATERIALS_TOTAL}}</text:p>
   <text:p text:style-name="Standard">Labor: ${{LABOR_TOTAL}}</text:p>
   <text:p text:style-name="Standard">Subtotal: ${{SUBTOTAL}}</text:p>
   <text:p text:style-name="Standard">{{TAX_DESCRIPTION}}: ${{TAX_AMOUNT}}</text:p>
   <text:p text:style-name="Standard"><text:span text:style-name="T1">Total Project Cost: ${{GRAND_TOTAL}}</text:span></text:p>
   <text:p text:style-name="Standard"/>
   <text:p text:style-name="P2">PAYMENT TERMS</text:p>
   <text:p text:style-name="Standard">{{PAYMENT_TERMS}}</text:p>
   <text:p text:style-name="Standard"/>
   <text:p text:style-name="P2">SCOPE OF WORK</text:p>
   {{SCOPE_SECTIONS}}
   <text:p text:style-name="P2">TERMS AND CONDITIONS</text:p>
   <text:p text:style-name="Standard">1. Scope of Work: Contractor shall perform the work described above.</text:p>
   <text:p text:style-name="Standard">2. Price and Payments: Total cost is ${{GRAND_TOTAL}}.</text:p>
   <text:p text:style-name="Standard">3. Work shall be completed within agreed timeframe.</text:p>
   <text:p text:style-name="Standard"/>
   <text:p text:style-name="P2">SIGNATURES</text:p>
   <text:p text:style-name="Standard">Contractor: _________________________ Date: ________</text:p>
   <text:p text:style-name="Standard">{{CONTRACTOR_NAME}}</text:p>
   <text:p text:style-name="Standard"/>
   <text:p text:style-name="Standard">Owner: _________________________ Date: ________</text:p>
   <text:p text:style-name="Standard">{{CLIENT_NAME}}</text:p>
  </office:text>
 </office:body>
</office:document-content>'''

        self._create_odt_file(output_path, content_xml, "modern_professional")
    
    def _create_invoice_template(self, output_path: str):
        """Create a professional invoice template ODT file"""
        
        content_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<office:document-content 
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0">

<office:automatic-styles>
    <style:style style:name="CompanyHeader" style:family="paragraph">
        <style:paragraph-properties fo:text-align="center" fo:margin-top="0.2in"/>
        <style:text-properties fo:font-size="18pt" fo:font-weight="bold" fo:color="#c5504b"/>
    </style:style>
    
    <style:style style:name="InvoiceHeader" style:family="paragraph">
        <style:paragraph-properties fo:text-align="center" fo:margin-bottom="0.3in"/>
        <style:text-properties fo:font-size="16pt" fo:font-weight="bold" fo:color="#c5504b"/>
    </style:style>
    
    <style:style style:name="SectionHeader" style:family="paragraph">
        <style:paragraph-properties fo:margin-top="0.2in" fo:margin-bottom="0.1in"
                                   fo:border-bottom="2pt solid #c5504b"/>
        <style:text-properties fo:font-size="12pt" fo:font-weight="bold" fo:color="#70ad47"/>
    </style:style>
    
    <style:style style:name="InvoiceTable" style:family="table">
        <style:table-properties style:width="100%" table:align="margins"/>
    </style:style>
    
    <style:style style:name="InvoiceTableHeader" style:family="table-cell">
        <style:table-cell-properties fo:background-color="#c5504b" fo:border="1pt solid #70ad47"/>
        <style:text-properties fo:color="#ffffff" fo:font-weight="bold"/>
    </style:style>
    
    <style:style style:name="InvoiceTableCell" style:family="table-cell">
        <style:table-cell-properties fo:border="0.5pt solid #d0d0d0"/>
    </style:style>
    
    <style:style style:name="InvoiceTotalRow" style:family="table-cell">
        <style:table-cell-properties fo:background-color="#f8f8f8" fo:border="1pt solid #70ad47"/>
        <style:text-properties fo:font-weight="bold"/>
    </style:style>
</office:automatic-styles>

<office:body>
<office:text>

<!-- Header Section -->
<text:p text:style-name="CompanyHeader">WATERWIZARD IRRIGATION</text:p>
<text:p text:style-name="InvoiceHeader">INVOICE</text:p>

<!-- Invoice Info -->
<text:p>INVOICE NUMBER: {{INVOICE_NUMBER}}</text:p>
<text:p>DATE: {{INVOICE_DATE}}</text:p>
<text:p>DUE: Upon Receipt</text:p>
<text:p></text:p>

<!-- Client and Company Info Table -->
<table:table table:name="InfoTable" table:style-name="InvoiceTable">
    <table:table-column table:style-name="InfoCol"/>
    <table:table-column table:style-name="InfoCol"/>
    
    <table:table-row>
        <table:table-cell table:style-name="InvoiceTableCell">
            <text:p><text:span text:style-name="Bold">BILL TO:</text:span></text:p>
            <text:p>{{CLIENT_NAME}}</text:p>
            <text:p>{{CLIENT_ADDRESS}}</text:p>
            <text:p>{{CLIENT_CITY}}, {{CLIENT_STATE}} {{CLIENT_ZIP}}</text:p>
        </table:table-cell>
        
        <table:table-cell table:style-name="InvoiceTableCell">
            <text:p><text:span text:style-name="Bold">FROM:</text:span></text:p>
            <text:p>WaterWizard Irrigation &amp; Landscape</text:p>
            <text:p>Professional Irrigation Services</text:p>
            <text:p>Phone: (555) 123-4567</text:p>
            <text:p>Email: info@waterwizard.com</text:p>
        </table:table-cell>
    </table:table-row>
</table:table>

<text:p></text:p>
<text:p>PROJECT: {{PROJECT_NAME}}</text:p>

<!-- Line Items Table -->
<table:table table:name="LineItemsTable" table:style-name="InvoiceTable">
    <table:table-column table:style-name="DescCol"/>
    <table:table-column table:style-name="QtyCol"/>
    <table:table-column table:style-name="RateCol"/>
    <table:table-column table:style-name="AmountCol"/>
    
    <table:table-row>
        <table:table-cell table:style-name="InvoiceTableHeader">
            <text:p>Description</text:p>
        </table:table-cell>
        <table:table-cell table:style-name="InvoiceTableHeader">
            <text:p>Qty</text:p>
        </table:table-cell>
        <table:table-cell table:style-name="InvoiceTableHeader">
            <text:p>Rate</text:p>
        </table:table-cell>
        <table:table-cell table:style-name="InvoiceTableHeader">
            <text:p>Amount</text:p>
        </table:table-cell>
    </table:table-row>
    
    {{LINE_ITEMS_ROWS}}
    
    <!-- Totals Section -->
    <table:table-row>
        <table:table-cell table:style-name="InvoiceTotalRow" table:number-columns-spanned="3">
            <text:p>SUBTOTAL:</text:p>
        </table:table-cell>
        <table:table-cell table:style-name="InvoiceTotalRow">
            <text:p>${{SUBTOTAL}}</text:p>
        </table:table-cell>
    </table:table-row>
    
    <table:table-row>
        <table:table-cell table:style-name="InvoiceTotalRow" table:number-columns-spanned="3">
            <text:p>TAX ({{TAX_RATE}}%):</text:p>
        </table:table-cell>
        <table:table-cell table:style-name="InvoiceTotalRow">
            <text:p>${{TAX_AMOUNT}}</text:p>
        </table:table-cell>
    </table:table-row>
    
    <table:table-row>
        <table:table-cell table:style-name="InvoiceTotalRow" table:number-columns-spanned="3">
            <text:p><text:span text:style-name="Bold">AMOUNT DUE:</text:span></text:p>
        </table:table-cell>
        <table:table-cell table:style-name="InvoiceTotalRow">
            <text:p><text:span text:style-name="Bold">${{GRAND_TOTAL}}</text:span></text:p>
        </table:table-cell>
    </table:table-row>
</table:table>

<text:p></text:p>
<text:p text:style-name="SectionHeader">PAYMENT TERMS: Net 30 days</text:p>
<text:p>THANK YOU FOR YOUR BUSINESS!</text:p>

</office:text>
</office:body>
</office:document-content>'''

        self._create_odt_file(output_path, content_xml, "invoice")
    
    def _create_odt_file(self, output_path: str, content_xml: str, doc_type: str):
        """Create a complete ODT file with proper structure"""
        
        # Create manifest.xml
        manifest_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">
    <manifest:file-entry manifest:full-path="/" manifest:media-type="application/vnd.oasis.opendocument.text"/>
    <manifest:file-entry manifest:full-path="content.xml" manifest:media-type="text/xml"/>
    <manifest:file-entry manifest:full-path="styles.xml" manifest:media-type="text/xml"/>
    <manifest:file-entry manifest:full-path="meta.xml" manifest:media-type="text/xml"/>
</manifest:manifest>'''

        # Create styles.xml
        styles_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<office:document-styles xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0">
<office:styles>
    <style:default-style style:family="paragraph">
        <style:paragraph-properties style:tab-stop-distance="0.5in"/>
        <style:text-properties style:font-name="Calibri" fo:font-size="11pt"/>
    </style:default-style>
    
    <style:style style:name="Bold" style:family="text">
        <style:text-properties fo:font-weight="bold"/>
    </style:style>
</office:styles>
</office:document-styles>'''

        # Create meta.xml
        meta_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<office:document-meta xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
    xmlns:dc="http://purl.org/dc/elements/1.1/">
<office:meta>
    <meta:generator>WaterWizard Squirt System</meta:generator>
    <dc:title>WaterWizard {doc_type.title()} Template</dc:title>
    <dc:creator>WaterWizard Irrigation</dc:creator>
    <meta:creation-date>{datetime.now().isoformat()}</meta:creation-date>
</office:meta>
</office:document-meta>'''

        # Create the ODT file
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as odt_file:
            odt_file.writestr('mimetype', 'application/vnd.oasis.opendocument.text')
            odt_file.writestr('META-INF/manifest.xml', manifest_xml)
            odt_file.writestr('content.xml', content_xml)
            odt_file.writestr('styles.xml', styles_xml)
            odt_file.writestr('meta.xml', meta_xml)

    def generate_professional_contract(self, client_info: dict, project_info: dict, 
                                     templates_with_params: list, output_path: str) -> str:
        """Generate a professional contract using ODT template"""
        
        # Process templates to get line items
        all_line_items = []
        total_subtotal = Decimal("0")
        narratives = []
        
        for template_path, params in templates_with_params:
            result = self.processor.process_template(template_path, params)
            all_line_items.extend(result['line_items'])
            total_subtotal += Decimal(str(result['subtotal']))
            narratives.append(result['narrative'])
        
        # Calculate taxes
        state = client_info.get('state', 'OR')
        tax_rate, tax_description = self.tax_engine.get_tax_rate(state)
        tax_amount = (total_subtotal * tax_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        grand_total = (total_subtotal + tax_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Load contract template
        template_path = self.template_dir / "contract_template.odt"
        
        # Create temporary working file
        with tempfile.NamedTemporaryFile(suffix='.odt', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Copy template to temp file
        with zipfile.ZipFile(str(template_path), 'r') as template_zip:
            template_zip.extractall(Path(temp_path).parent / "template_extract")
        
        # Read and modify content.xml
        extract_dir = Path(temp_path).parent / "template_extract"
        content_path = extract_dir / "content.xml"
        
        with open(content_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace placeholders
        doc_number = f"WW-{datetime.now().strftime('%Y%m%d')}-{project_info.get('id', '001')}"
        date_str = datetime.now().strftime("%B %d, %Y")
        
        replacements = {
            '{{CONTRACT_NUMBER}}': doc_number,
            '{{CONTRACT_DATE}}': date_str,
            '{{CLIENT_NAME}}': client_info.get('name', ''),
            '{{CLIENT_ADDRESS}}': client_info.get('address', ''),
            '{{CLIENT_CITY}}': client_info.get('city', ''),
            '{{CLIENT_STATE}}': client_info.get('state', ''),
            '{{CLIENT_ZIP}}': client_info.get('zip', ''),
            '{{CLIENT_PHONE}}': client_info.get('phone', ''),
            '{{CLIENT_EMAIL}}': client_info.get('email', ''),
            '{{PROJECT_NAME}}': project_info.get('name', ''),
            '{{PROJECT_ADDRESS}}': project_info.get('address', ''),
            '{{PROJECT_DESCRIPTION}}': ' '.join(narratives),
            '{{SUBTOTAL}}': f"{float(total_subtotal):.2f}",
            '{{TAX_RATE}}': f"{float(tax_rate * 100):.2f}",
            '{{TAX_AMOUNT}}': f"{float(tax_amount):.2f}",
            '{{GRAND_TOTAL}}': f"{float(grand_total):.2f}"
        }
        
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)
        
        # Generate line items table rows
        line_items_xml = self._generate_line_items_xml(all_line_items)
        content = content.replace('{{LINE_ITEMS_ROWS}}', line_items_xml)
        
        # Write modified content
        with open(content_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Recreate ODT file
        with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as new_odt:
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    file_path = Path(root) / file
                    arc_path = file_path.relative_to(extract_dir)
                    new_odt.write(file_path, arc_path)
        
        # Move to final location
        Path(temp_path).rename(output_path)
        
        # Clean up
        import shutil
        shutil.rmtree(extract_dir)
        
        return output_path

    def generate_modern_professional_contract(self, client_info: dict, contractor_info: dict, 
                                            project_info: dict, line_items: list, output_path: str, 
                                            auto_open_for_review: bool = True) -> str:
        """Generate a contract using the modern professional template with visual styling"""
        
        # Calculate totals by category
        materials_total = sum(Decimal(str(item.get('line_total', 0))) 
                            for item in line_items if item.get('category') == 'materials')
        labor_total = sum(Decimal(str(item.get('line_total', 0))) 
                        for item in line_items if item.get('category') == 'labor')
        equipment_total = sum(Decimal(str(item.get('line_total', 0))) 
                            for item in line_items if item.get('category') == 'equipment')
        
        # Combine materials and equipment for display
        materials_equipment_total = materials_total + equipment_total
        subtotal = materials_equipment_total + labor_total
        
        # Calculate taxes
        state = client_info.get('state', 'OR')
        tax_rate, tax_description = self.tax_engine.get_tax_rate(state)
        tax_amount = (subtotal * tax_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        grand_total = (subtotal + tax_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Format line items for display
        materials_list = self._format_line_items_list(line_items, ['materials', 'equipment'])
        labor_details = self._format_line_items_list(line_items, ['labor'])
        
        # Prepare contract data for the fixed ODT generator
        contract_data = {
            'company_name': contractor_info.get('name', 'WaterWizard'),
            'client_name': client_info.get('name', ''),
            'client_address': f"{client_info.get('address', '')}\\n{client_info.get('city', '')}, {client_info.get('state', '')} {client_info.get('zip', '')}",
            'contractor_name': contractor_info.get('name', ''),
            'contractor_address': f"{contractor_info.get('address', '')}\\n{contractor_info.get('city', '')}, {contractor_info.get('state', '')} {contractor_info.get('zip', '')}",
            'project_description': project_info.get('description', ''),
            'project_date': datetime.now().strftime('%B %d, %Y'),
            'project_location': client_info.get('address', ''),
            'materials_list': materials_list,
            'labor_details': labor_details,
            'subtotal': f"{float(subtotal):.2f}",
            'tax_amount': f"{float(tax_amount):.2f}",
            'total_amount': f"{float(grand_total):.2f}",
            'terms_conditions': project_info.get('payment_terms', 'Work to be completed within agreed timeframe. Payment due upon completion.')
        }
        
        # Use the fixed ODT generator
        success = self.odt_generator.create_waterwizard_contract(contract_data, output_path)
        
        if not success:
            raise Exception("Failed to generate contract ODT file")
        
        # Automatic human-in-the-loop validation for visual styling
        if auto_open_for_review:
            open_document_for_human_review(output_path, "modern professional contract")
        
        return output_path
    
    def _format_line_items_list(self, line_items: list, categories: list) -> str:
        """Format line items for display in the contract"""
        filtered_items = [item for item in line_items if item.get('category') in categories]
        
        if not filtered_items:
            return "No items in this category"
        
        lines = []
        for item in filtered_items:
            desc = item.get('description', 'Item')
            qty = item.get('quantity', 1)
            rate = item.get('unit_rate', 0)
            total = item.get('line_total', 0)
            
            if categories == ['labor']:
                lines.append(f"• {desc}: {qty} hours @ ${rate:.2f}/hour = ${total:.2f}")
            else:
                lines.append(f"• {desc}: {qty} units @ ${rate:.2f} = ${total:.2f}")
        
        return "\\n".join(lines)
    
    def _generate_scope_sections_modern(self, line_items: List[Dict[str, Any]], 
                                      materials_total: Decimal, labor_total: Decimal) -> str:
        """Generate scope of work sections - minimal format for valid ODT"""
        
        sections = []
        
        # Group items by category
        materials_items = [item for item in line_items if item.get('category') in ['materials', 'equipment']]
        labor_items = [item for item in line_items if item.get('category') == 'labor']
        
        if materials_items:
            sections.append(f'''<text:p text:style-name="Standard"><text:span text:style-name="T1">Materials and Equipment (${float(materials_total):.2f})</text:span></text:p>
''')
            for item in materials_items:
                qty = item.get('quantity', 0)
                rate = item.get('unit_rate', 0)
                total = item.get('line_total', 0)
                desc = item.get('description', '')
                sections.append(f'''<text:p text:style-name="Standard">{desc}: {qty} x ${rate:.2f} = ${total:.2f}</text:p>
''')
            sections.append('<text:p text:style-name="Standard"/>\n')
        
        if labor_items:
            sections.append(f'''<text:p text:style-name="Standard"><text:span text:style-name="T1">Labor Services (${float(labor_total):.2f})</text:span></text:p>
''')
            for item in labor_items:
                desc = item.get('description', '')
                total = item.get('line_total', 0)
                qty = item.get('quantity', 0)
                sections.append(f'''<text:p text:style-name="Standard">{desc}: {qty} hours = ${total:.2f}</text:p>
''')
        
        return ''.join(sections)
    
    def _generate_line_items_xml(self, line_items: List[Dict[str, Any]]) -> str:
        """Generate XML for line items table rows"""
        
        xml_rows = []
        
        # Group by category
        categories = {}
        for item in line_items:
            cat = item['category'].upper()
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(item)
        
        # Generate rows for each category
        for category, items in categories.items():
            # Category header
            xml_rows.append(f'''
    <table:table-row>
        <table:table-cell table:style-name="TableCell" table:number-columns-spanned="4">
            <text:p><text:span text:style-name="Bold">{category}</text:span></text:p>
        </table:table-cell>
    </table:table-row>''')
            
            # Items in category
            for item in items:
                xml_rows.append(f'''
    <table:table-row>
        <table:table-cell table:style-name="TableCell">
            <text:p>{item['description']}</text:p>
        </table:table-cell>
        <table:table-cell table:style-name="TableCell">
            <text:p>{item['quantity']:.1f}</text:p>
        </table:table-cell>
        <table:table-cell table:style-name="TableCell">
            <text:p>${item['unit_rate']:.2f}</text:p>
        </table:table-cell>
        <table:table-cell table:style-name="TableCell">
            <text:p>${item['line_total']:.2f}</text:p>
        </table:table-cell>
    </table:table-row>''')
        
        return ''.join(xml_rows)

    def convert_to_pdf(self, odt_path: str, pdf_path: str = None) -> str:
        """Convert ODT to PDF using LibreOffice"""
        
        if pdf_path is None:
            pdf_path = odt_path.replace('.odt', '.pdf')
        
        output_dir = Path(pdf_path).parent
        
        cmd = [
            'libreoffice', '--headless', '--convert-to', 'pdf',
            '--outdir', str(output_dir), odt_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return pdf_path
            else:
                raise RuntimeError(f"PDF conversion failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            raise RuntimeError("PDF conversion timed out")
    
    def open_document_for_human_review(self, document_path: str, document_type: str = "generated") -> bool:
        """
        Open document for human-in-the-loop validation
        This ensures quality control by allowing human review of visual styling
        """
        
        print(f"\n🔍 HUMAN-IN-THE-LOOP VALIDATION")
        print("=" * 50)
        print(f"Opening {document_type} document for human review...")
        print(f"Document: {document_path}")
        print("\nPlease review the document for:")
        print("✓ Visual styling (colors, fonts, formatting)")
        print("✓ Professional appearance") 
        print("✓ Content layout and organization")
        print("✓ Typography hierarchy")
        print("✓ Any visual inconsistencies")
        
        if not Path(document_path).exists():
            print(f"❌ Document not found: {document_path}")
            return False
        
        # Try multiple methods to open the document
        open_methods = []
        
        if Path(document_path).suffix.lower() == '.pdf':
            open_methods = [
                ['evince', document_path],
                ['okular', document_path], 
                ['xdg-open', document_path]
            ]
        else:
            # For ODT files
            open_methods = [
                ['libreoffice', '--writer', document_path],
                ['lowriter', document_path],
                ['xdg-open', document_path]
            ]
        
        for method in open_methods:
            try:
                # Use Popen with detach to prevent hanging
                process = subprocess.Popen(
                    method,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
                
                print(f"✅ Document opened for human review using: {method[0]}")
                return True
                
            except FileNotFoundError:
                continue
            except Exception as e:
                print(f"⚠️  Method {method[0]} failed: {e}")
                continue
        
        print(f"❌ Could not automatically open document with any method")
        print(f"📁 Please manually open: {Path(document_path).absolute()}")
        print(f"💡 Install LibreOffice for better ODT support: sudo apt install libreoffice")
        
        # Provide text preview for ODT files as last resort
        if Path(document_path).suffix.lower() == '.odt':
            self._show_odt_text_preview(document_path)
        
        return False
    
    def _show_odt_text_preview(self, odt_path: str):
        """Show text preview of ODT content for validation when GUI opening fails"""
        try:
            print(f"\n📄 TEXT PREVIEW (for validation when GUI unavailable):")
            print("=" * 60)
            
            with zipfile.ZipFile(odt_path, 'r') as odt_file:
                if 'content.xml' in odt_file.namelist():
                    content_xml = odt_file.read('content.xml').decode('utf-8')
                    
                    # Extract text content using basic regex
                    import re
                    
                    # Remove XML tags but keep text content
                    text_content = re.sub(r'<[^>]+>', '\n', content_xml)
                    text_content = re.sub(r'\n+', '\n', text_content)  # Clean multiple newlines
                    
                    # Show first part of content for validation
                    lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                    preview_lines = lines[:20]  # First 20 non-empty lines
                    
                    for line in preview_lines:
                        if line and not line.startswith('<?xml'):
                            print(f"  {line}")
                    
                    print(f"\n... (showing first 20 lines)")
                    print(f"📝 Full document available at: {Path(odt_path).absolute()}")
                    
        except Exception as e:
            print(f"⚠️  Could not show text preview: {e}")

def main():
    """Demo the modern document generator"""
    
    print("🎨 MODERN WATERWIZARD DOCUMENT GENERATOR")
    print("=" * 60)
    
    generator = ModernDocumentGenerator()
    
    # Sample data
    client = {
        "name": "Premium Estates LLC",
        "address": "456 Highland Drive",
        "city": "Austin",
        "state": "TX", 
        "zip": "78704",
        "phone": "(512) 555-9876",
        "email": "info@premiumestates.com"
    }
    
    project = {
        "name": "Executive Home Front Yard",
        "address": "456 Highland Drive",
        "id": "001"
    }
    
    templates = [
        ("src/templates/sprinkler_zone.json", {
            "zone_number": 1,
            "head_count": 12,
            "trench_feet": 250,
            "soil_type": "rocky"
        })
    ]
    
    # Generate modern contract
    output_dir = Path("modern_test_output")
    output_dir.mkdir(exist_ok=True)
    
    odt_path = str(output_dir / "modern_contract_test.odt")
    
    print("📄 Generating professional contract...")
    generator.generate_professional_contract(client, project, templates, odt_path)
    
    print("📊 Converting to PDF...")
    pdf_path = generator.convert_to_pdf(odt_path)
    
    print(f"✅ Generated files:")
    print(f"   ODT: {odt_path}")
    print(f"   PDF: {pdf_path}")

if __name__ == "__main__":
    main()