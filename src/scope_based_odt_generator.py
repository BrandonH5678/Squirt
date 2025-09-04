#!/usr/bin/env python3
"""
Scope-based ODT generator specifically designed for Squirt scope-based contracts.
Unlike FixedODTGenerator, this supports proper scope organization without hardcoded category headers.
"""

import zipfile
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class ScopeBasedODTGenerator:
    """Generate ODT files with scope-based organization and modern professional styling"""
    
    def __init__(self):
        pass
    
    def _escape_xml_entities(self, text: str) -> str:
        """Properly escape XML entities to prevent corruption"""
        if not isinstance(text, str):
            text = str(text)
        
        # Replace XML special characters with entities
        text = text.replace('&', '&amp;')  # Must be first
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&apos;')
        
        return text
    
    def create_scope_based_contract(self, contract_data: Dict[str, Any], output_path: str) -> bool:
        """
        Create a scope-based contract ODT file with modern professional styling.
        
        Args:
            contract_data: Dictionary containing contract information including scope_content
            output_path: Path where to save the ODT file
            
        Returns:
            True if successful, False otherwise
        """
        
        try:
            # Get the proper XML content using scope-based structure
            content_xml = self._get_scope_based_content_xml(contract_data)
            styles_xml = self._get_modern_styles_xml()
            manifest_xml = self._get_manifest_xml()
            meta_xml = self._get_meta_xml()
            mimetype = "application/vnd.oasis.opendocument.text"
            
            # Create the ODT file
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as odt_file:
                # IMPORTANT: mimetype must be first and uncompressed
                odt_file.writestr('mimetype', mimetype, compress_type=zipfile.ZIP_STORED)
                odt_file.writestr('META-INF/manifest.xml', manifest_xml)
                odt_file.writestr('content.xml', content_xml)
                odt_file.writestr('styles.xml', styles_xml)
                odt_file.writestr('meta.xml', meta_xml)
            
            print(f"✅ Successfully created scope-based ODT file: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating scope-based ODT file: {e}")
            return False
    
    def _get_scope_based_content_xml(self, data: Dict[str, Any]) -> str:
        """Generate content.xml using scope-based organization structure"""
        
        # Escape all data values to prevent XML corruption
        escaped_data = {}
        for key, value in data.items():
            if key == 'scope_content':
                # Special handling for scope content - convert line breaks to ODT format
                scope_content = str(value)
                scope_content = scope_content.replace('\\n', '<text:line-break/>')
                scope_content = self._escape_xml_entities(scope_content)
                escaped_data[key] = scope_content
            else:
                escaped_data[key] = self._escape_xml_entities(str(value))
        
        # Use LibreOffice-compatible namespace declarations with scope-based content structure
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<office:document-content xmlns:css3t="http://www.w3.org/TR/css3-text/" xmlns:grddl="http://www.w3.org/2003/g/data-view#" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xforms="http://www.w3.org/2002/xforms" xmlns:dom="http://www.w3.org/2001/xml-events" xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0" xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0" xmlns:math="http://www.w3.org/1998/Math/MathML" xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:ooo="http://openoffice.org/2004/office" xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" xmlns:ooow="http://openoffice.org/2004/writer" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:drawooo="http://openoffice.org/2010/draw" xmlns:oooc="http://openoffice.org/2004/calc" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:calcext="urn:org:documentfoundation:names:experimental:calc:xmlns:calcext:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2" xmlns:tableooo="http://openoffice.org/2009/table" xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0" xmlns:rpt="http://openoffice.org/2005/report" xmlns:formx="urn:openoffice:names:experimental:ooxml-odf-interop:xmlns:form:1.0" xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0" xmlns:officeooo="http://openoffice.org/2009/office" xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" xmlns:loext="urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0" xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0" xmlns:field="urn:openoffice:names:experimental:ooo-ms-interop:xmlns:field:1.0" office:version="1.3">
<office:scripts/>
<office:font-face-decls>
<style:font-face style:name="Arial" svg:font-family="Arial, sans-serif"/>
<style:font-face style:name="Liberation Sans" svg:font-family="&apos;Liberation Sans&apos;" style:font-family-generic="swiss" style:font-pitch="variable"/>
<style:font-face style:name="Liberation Serif" svg:font-family="&apos;Liberation Serif&apos;" style:font-family-generic="roman" style:font-pitch="variable"/>
</office:font-face-decls>
<office:automatic-styles>
<style:style style:name="Table1" style:family="table">
<style:table-properties style:width="7.3188in" table:align="left"/>
</style:style>
<style:style style:name="Table1.A" style:family="table-column">
<style:table-column-properties style:column-width="1.8in"/>
</style:style>
<style:style style:name="Table1.B" style:family="table-column">
<style:table-column-properties style:column-width="2.7in"/>
</style:style>
<style:style style:name="Table1.C" style:family="table-column">
<style:table-column-properties style:column-width="1.4in"/>
</style:style>
<style:style style:name="Table1.D" style:family="table-column">
<style:table-column-properties style:column-width="1.4in"/>
</style:style>
<style:style style:name="Table1.A1" style:family="table-cell">
<style:table-cell-properties style:vertical-align="middle" fo:padding="0.0194in" fo:border="none"/>
</style:style>
<style:style style:name="P1" style:family="paragraph" style:parent-style-name="Table_20_Contents">
<style:paragraph-properties fo:margin-left="0in" fo:margin-right="0in" fo:text-indent="0in" style:auto-text-indent="false"/>
</style:style>
<style:style style:name="P2" style:family="paragraph" style:parent-style-name="Table_20_Contents">
<style:paragraph-properties fo:margin-left="0in" fo:margin-right="0in" fo:text-indent="0in" style:auto-text-indent="false"/>
<style:text-properties fo:font-weight="bold"/>
</style:style>
<style:style style:name="P3" style:family="paragraph" style:parent-style-name="Text_20_body">
<style:paragraph-properties fo:margin-left="0in" fo:margin-right="0in" fo:text-indent="0in" style:auto-text-indent="false"/>
</style:style>
<style:style style:name="P5" style:family="paragraph" style:parent-style-name="Text_20_body" style:master-page-name="HTML">
<style:paragraph-properties fo:margin-left="0in" fo:margin-right="0in" fo:margin-top="0in" fo:margin-bottom="0.2083in" style:contextual-spacing="false" fo:text-align="center" style:justify-single-word="false" fo:text-indent="0in" style:auto-text-indent="false" style:page-number="auto"/>
<style:text-properties fo:font-size="16pt" fo:font-weight="bold"/>
</style:style>
<style:style style:name="P6" style:family="paragraph" style:parent-style-name="Text_20_body">
<style:paragraph-properties fo:margin-left="0in" fo:margin-right="0in" fo:margin-top="0in" fo:margin-bottom="0.3126in" style:contextual-spacing="false" fo:text-align="center" style:justify-single-word="false" fo:text-indent="0in" style:auto-text-indent="false"/>
<style:text-properties fo:font-size="14pt"/>
</style:style>
<style:style style:name="P7" style:family="paragraph" style:parent-style-name="Text_20_body">
<style:paragraph-properties fo:margin-left="0in" fo:margin-right="0in" fo:margin-top="0.2083in" fo:margin-bottom="0.1043in" style:contextual-spacing="false" fo:text-indent="0in" style:auto-text-indent="false"/>
<style:text-properties fo:color="#4472c4" loext:opacity="100%" fo:font-size="12pt" fo:font-weight="bold"/>
</style:style>
<style:style style:name="P8" style:family="paragraph" style:parent-style-name="Text_20_body">
<style:paragraph-properties fo:margin-left="0in" fo:margin-right="0in" fo:margin-top="0.1563in" fo:margin-bottom="0.0835in" style:contextual-spacing="false" fo:text-indent="0in" style:auto-text-indent="false"/>
<style:text-properties fo:color="#4472c4" loext:opacity="100%" fo:font-style="italic"/>
</style:style>
<style:style style:name="T1" style:family="text">
<style:text-properties fo:font-weight="bold"/>
</style:style>
</office:automatic-styles>
<office:body>
<office:text>
<text:sequence-decls>
<text:sequence-decl text:display-outline-level="0" text:name="Illustration"/>
<text:sequence-decl text:display-outline-level="0" text:name="Table"/>
<text:sequence-decl text:display-outline-level="0" text:name="Text"/>
<text:sequence-decl text:display-outline-level="0" text:name="Drawing"/>
<text:sequence-decl text:display-outline-level="0" text:name="Figure"/>
</text:sequence-decls>
<text:p text:style-name="P5">CONSTRUCTION CONTRACT</text:p>
<text:p text:style-name="P6">{escaped_data.get('project_title', 'Landscape Maintenance Services')}</text:p>
<table:table table:name="Table1" table:style-name="Table1">
<table:table-column table:style-name="Table1.A"/>
<table:table-column table:style-name="Table1.B"/>
<table:table-column table:style-name="Table1.C"/>
<table:table-column table:style-name="Table1.D"/>
<table:table-row>
<table:table-cell table:style-name="Table1.A1" office:value-type="string">
<text:p text:style-name="P2">Prepared for:</text:p>
</table:table-cell>
<table:table-cell table:style-name="Table1.A1" office:value-type="string">
<text:p text:style-name="P1">{escaped_data.get('client_name', 'Client Name')}<text:line-break/>{escaped_data.get('client_address', 'Client Address')}</text:p>
</table:table-cell>
<table:table-cell table:style-name="Table1.A1" office:value-type="string">
<text:p text:style-name="P2">Prepared by:</text:p>
</table:table-cell>
<table:table-cell table:style-name="Table1.A1" office:value-type="string">
<text:p text:style-name="P1">{escaped_data.get('contractor_name', 'WaterWizard Irrigation &amp; Landscape')}<text:line-break/>{escaped_data.get('contractor_address', 'Professional Landscape Services')}</text:p>
</table:table-cell>
</table:table-row>
</table:table>
<text:p text:style-name="P7">PROJECT SUMMARY</text:p>
<text:p text:style-name="P3">{escaped_data.get('project_summary', 'Complete landscape maintenance and cleanup services.')}</text:p>
<text:p text:style-name="P7">PROJECT TOTALS</text:p>
<text:p text:style-name="P3"><text:span text:style-name="T1">Materials &amp; Disposal</text:span>                              ${escaped_data.get('materials_total', '0.00')}</text:p>
<text:p text:style-name="P3"><text:span text:style-name="T1">Equipment &amp; Fees</text:span>                                  ${escaped_data.get('equipment_total', '0.00')}</text:p>
<text:p text:style-name="P3"><text:span text:style-name="T1">Labor</text:span>                                             ${escaped_data.get('labor_total', '0.00')}</text:p>
<text:p text:style-name="P3"><text:span text:style-name="T1">Subtotal</text:span>                                          ${escaped_data.get('subtotal', '0.00')}</text:p>
<text:p text:style-name="P3"><text:span text:style-name="T1">Sales Tax (Oregon - No state sales tax)</text:span>          ${escaped_data.get('tax_amount', '0.00')}</text:p>
<text:p text:style-name="P3"><text:span text:style-name="T1">Total Project Cost</text:span>                                ${escaped_data.get('total_amount', '0.00')}</text:p>
<text:p text:style-name="P7">PAYMENT TERMS</text:p>
<text:p text:style-name="P3">{escaped_data.get('payment_terms', 'Payment due upon completion of work.')}</text:p>
<text:p text:style-name="P7">SCOPE OF WORK BY AREA</text:p>
<text:p text:style-name="Text_20_body">{escaped_data.get('scope_content', 'Scope of work will appear here')}</text:p>
<text:p text:style-name="P7">TERMS &amp; CONDITIONS</text:p>
<text:p text:style-name="Text_20_body">{escaped_data.get('terms_conditions', 'Standard terms and conditions apply.')}</text:p>
<text:p text:style-name="P7">ACCEPTANCE:</text:p>
<text:p text:style-name="Text_20_body"/>
<text:p text:style-name="P3"><text:span text:style-name="T1">Customer:</text:span> ________________________________    <text:span text:style-name="T1">Date:</text:span> _______________</text:p>
<text:p text:style-name="P3">{escaped_data.get('client_name', 'Client Name')}</text:p>
<text:p text:style-name="Text_20_body"/>
<text:p text:style-name="P3"><text:span text:style-name="T1">WaterWizard Representative:</text:span> ________________    <text:span text:style-name="T1">Date:</text:span> {escaped_data.get('contract_date', datetime.now().strftime('%B %d, %Y'))}</text:p>
<text:p text:style-name="Text_20_body"/>
</office:text>
</office:body>
</office:document-content>'''
    
    def _get_modern_styles_xml(self) -> str:
        """Return LibreOffice-compatible styles.xml with modern professional styling"""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<office:document-styles xmlns:css3t="http://www.w3.org/TR/css3-text/" xmlns:grddl="http://www.w3.org/2003/g/data-view#" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:dom="http://www.w3.org/2001/xml-events" xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0" xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0" xmlns:math="http://www.w3.org/1998/Math/MathML" xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:ooo="http://openoffice.org/2004/office" xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" xmlns:ooow="http://openoffice.org/2004/writer" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:drawooo="http://openoffice.org/2010/draw" xmlns:oooc="http://openoffice.org/2004/calc" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:calcext="urn:org:documentfoundation:names:experimental:calc:xmlns:calcext:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2" xmlns:tableooo="http://openoffice.org/2009/table" xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0" xmlns:rpt="http://openoffice.org/2005/report" xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0" xmlns:officeooo="http://openoffice.org/2009/office" xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" xmlns:loext="urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0" xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0" xmlns:field="urn:openoffice:names:experimental:ooo-ms-interop:xmlns:field:1.0" office:version="1.3">
<office:font-face-decls>
<style:font-face style:name="Arial" svg:font-family="Arial, sans-serif"/>
<style:font-face style:name="Liberation Sans" svg:font-family="&apos;Liberation Sans&apos;" style:font-family-generic="swiss" style:font-pitch="variable"/>
<style:font-face style:name="Liberation Serif" svg:font-family="&apos;Liberation Serif&apos;" style:font-family-generic="roman" style:font-pitch="variable"/>
</office:font-face-decls>
<office:styles>
<style:default-style style:family="paragraph">
<style:paragraph-properties style:text-autospace="ideograph-alpha" style:punctuation-wrap="hanging" style:line-break="strict" style:writing-mode="page"/>
<style:text-properties style:use-window-font-color="true" loext:opacity="0%" style:font-name="Liberation Serif" fo:font-size="12pt" fo:language="en" fo:country="US" style:font-name-asian="Liberation Serif" style:font-size-asian="12pt" style:language-asian="zh" style:country-asian="CN" style:font-name-complex="Liberation Serif" style:font-size-complex="12pt" style:language-complex="hi" style:country-complex="IN"/>
</style:default-style>
<style:style style:name="Standard" style:family="paragraph" style:class="text">
<style:paragraph-properties fo:margin-left="1in" fo:margin-right="1in" fo:margin-top="1in" fo:margin-bottom="1in" style:contextual-spacing="false"/>
<style:text-properties style:font-name="Arial" fo:font-family="Arial, sans-serif"/>
</style:style>
<style:style style:name="Table_20_Contents" style:display-name="Table Contents" style:family="paragraph" style:parent-style-name="Text_20_body" style:class="extra"/>
<style:style style:name="Text_20_body" style:display-name="Text body" style:family="paragraph" style:parent-style-name="Standard" style:class="text">
<style:paragraph-properties fo:margin-top="0in" fo:margin-bottom="0.1965in" style:contextual-spacing="false"/>
</style:style>
</office:styles>
<office:automatic-styles>
<style:page-layout style:name="Mpm1">
<style:page-layout-properties fo:page-width="8.5in" fo:page-height="11in" style:num-format="1" style:print-orientation="portrait" fo:margin-top="0.7874in" fo:margin-bottom="0.7874in" fo:margin-left="0.7874in" fo:margin-right="0.7874in" style:writing-mode="lr-tb" style:footnote-max-height="0in" loext:margin-gutter="0in">
<style:footnote-sep style:line-style="solid" style:adjustment="left" style:rel-width="25%" style:color="#000000"/>
</style:page-layout-properties>
<style:header-style/>
<style:footer-style/>
</style:page-layout>
</office:automatic-styles>
<office:master-styles>
<style:master-page style:name="Standard" style:page-layout-name="Mpm1"/>
<style:master-page style:name="HTML" style:page-layout-name="Mpm1"/>
</office:master-styles>
</office:document-styles>'''
    
    def _get_manifest_xml(self) -> str:
        """Return proper manifest.xml"""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">
 <manifest:file-entry manifest:full-path="/" manifest:media-type="application/vnd.oasis.opendocument.text"/>
 <manifest:file-entry manifest:full-path="content.xml" manifest:media-type="text/xml"/>
 <manifest:file-entry manifest:full-path="styles.xml" manifest:media-type="text/xml"/>
 <manifest:file-entry manifest:full-path="meta.xml" manifest:media-type="text/xml"/>
</manifest:manifest>'''
    
    def _get_meta_xml(self) -> str:
        """Return basic meta.xml"""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<office:document-meta xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" xmlns:dc="http://purl.org/dc/elements/1.1/" office:version="1.3">
<office:meta>
<meta:generator>WaterWizard Squirt System - Scope Based Generator</meta:generator>
<dc:title>WaterWizard Scope-Based Contract</dc:title>
<dc:creator>WaterWizard Irrigation</dc:creator>
<meta:creation-date>{datetime.now().isoformat()}</meta:creation-date>
</office:meta>
</office:document-meta>'''