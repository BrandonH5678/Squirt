#!/usr/bin/env python3
"""
Squirt Format Converter
Handles conversion between various document formats with formatting preservation
Optimized for client-common formats: PDF, DOC/DOCX, XLS/XLSX, CSV
"""

import subprocess
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from enum import Enum
import tempfile

class DocumentType(Enum):
    CONTRACT = "contract"
    INVOICE = "invoice"
    RECEIPT = "receipt"
    ESTIMATE = "estimate"
    WORKSHEET = "worksheet"

class OutputFormat(Enum):
    PDF = "pdf"
    ODT = "odt"
    DOC = "doc"
    DOCX = "docx"
    TXT = "txt"
    XLS = "xls"
    XLSX = "xlsx"
    CSV = "csv"

class SquirtFormatConverter:
    def __init__(self):
        """Initialize format converter with client-optimized settings"""
        
        # Format preferences for different document types
        self.format_rules = {
            DocumentType.CONTRACT: {
                'client_preferred': [OutputFormat.PDF, OutputFormat.DOCX],
                'internal_preferred': [OutputFormat.ODT, OutputFormat.TXT],
                'formatting_critical': True,
                'requires_signature': True
            },
            DocumentType.INVOICE: {
                'client_preferred': [OutputFormat.PDF, OutputFormat.XLSX],
                'internal_preferred': [OutputFormat.ODT, OutputFormat.CSV],
                'formatting_critical': True,
                'requires_signature': False
            },
            DocumentType.ESTIMATE: {
                'client_preferred': [OutputFormat.PDF, OutputFormat.DOCX],
                'internal_preferred': [OutputFormat.ODT, OutputFormat.TXT],
                'formatting_critical': True,
                'requires_signature': False
            },
            DocumentType.RECEIPT: {
                'client_preferred': [OutputFormat.PDF],
                'internal_preferred': [OutputFormat.ODT, OutputFormat.CSV],
                'formatting_critical': False,
                'requires_signature': False
            },
            DocumentType.WORKSHEET: {
                'client_preferred': [OutputFormat.XLSX, OutputFormat.CSV],
                'internal_preferred': [OutputFormat.CSV, OutputFormat.TXT],
                'formatting_critical': False,
                'requires_signature': False
            }
        }
        
        # LibreOffice conversion parameters for optimal formatting
        self.libreoffice_params = {
            OutputFormat.PDF: {
                'filter': 'writer_pdf_Export',
                'options': '--convert-to pdf',
                'preserve_formatting': True
            },
            OutputFormat.DOCX: {
                'filter': 'MS Word 2007 XML',
                'options': '--convert-to docx',
                'preserve_formatting': True
            },
            OutputFormat.DOC: {
                'filter': 'MS Word 97',
                'options': '--convert-to doc',
                'preserve_formatting': True
            },
            OutputFormat.XLSX: {
                'filter': 'Calc MS Excel 2007 XML',
                'options': '--convert-to xlsx',
                'preserve_formatting': True
            },
            OutputFormat.XLS: {
                'filter': 'MS Excel 97',
                'options': '--convert-to xls',
                'preserve_formatting': True
            },
            OutputFormat.CSV: {
                'filter': 'Text - txt - csv (StarCalc)',
                'options': '--convert-to csv',
                'preserve_formatting': False
            }
        }
    
    def convert_document(self, source_path: str, doc_type: DocumentType, 
                        target_formats: List[OutputFormat] = None,
                        output_dir: str = None) -> Dict[OutputFormat, str]:
        """
        Convert document to multiple formats with optimized settings
        
        Args:
            source_path: Path to source document
            doc_type: Type of document for format optimization
            target_formats: Specific formats to generate (default: client_preferred)
            output_dir: Output directory (default: same as source)
            
        Returns:
            Dictionary mapping formats to output file paths
        """
        
        source_file = Path(source_path)
        if not source_file.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        if output_dir is None:
            output_dir = source_file.parent
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True)
        
        # Use client-preferred formats if none specified
        if target_formats is None:
            target_formats = self.format_rules[doc_type]['client_preferred']
        
        results = {}
        
        for format_type in target_formats:
            try:
                output_path = self._convert_single_format(
                    source_path, format_type, output_dir, doc_type
                )
                results[format_type] = output_path
            except Exception as e:
                print(f"⚠️  Failed to convert to {format_type.value}: {e}")
                results[format_type] = None
        
        return results
    
    def _convert_single_format(self, source_path: str, target_format: OutputFormat,
                              output_dir: Path, doc_type: DocumentType) -> str:
        """Convert single file to specific format with optimization"""
        
        source_file = Path(source_path)
        base_name = source_file.stem
        
        # Handle special cases for format preservation
        if target_format in [OutputFormat.PDF] and self._has_ascii_diagrams(source_path):
            return self._convert_with_monospace_preservation(
                source_path, target_format, output_dir, base_name
            )
        
        # Standard LibreOffice conversion
        output_file = output_dir / f"{base_name}.{target_format.value}"
        
        conversion_params = self.libreoffice_params.get(target_format)
        if not conversion_params:
            raise ValueError(f"Unsupported format: {target_format}")
        
        cmd = [
            'libreoffice', '--headless', '--invisible',
            conversion_params['options'], str(source_path),
            '--outdir', str(output_dir)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                raise RuntimeError(f"LibreOffice conversion failed: {result.stderr}")
            
            if not output_file.exists():
                raise FileNotFoundError(f"Expected output file not created: {output_file}")
            
            return str(output_file)
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("LibreOffice conversion timed out")
    
    def _has_ascii_diagrams(self, file_path: str) -> bool:
        """Check if file contains ASCII box drawing characters"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for common ASCII diagram patterns
            diagram_chars = ['┌', '┐', '└', '┘', '│', '─', '├', '┤', '┬', '┴', '┼',
                           '+', '|', '-', '╔', '╗', '╚', '╝', '║', '═']
            
            return any(char in content for char in diagram_chars)
            
        except:
            return False
    
    def _convert_with_monospace_preservation(self, source_path: str, 
                                           target_format: OutputFormat,
                                           output_dir: Path, base_name: str) -> str:
        """Convert files with ASCII diagrams using monospace font preservation"""
        
        if Path(source_path).suffix.lower() == '.md':
            # Convert markdown with ASCII diagrams to formatted text first
            formatted_txt = self._markdown_to_formatted_text(source_path)
            temp_file = output_dir / f"{base_name}_temp.txt"
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(formatted_txt)
            
            # Convert formatted text to target format
            output_file = self._convert_single_format(
                str(temp_file), target_format, output_dir, DocumentType.CONTRACT
            )
            
            # Clean up temp file
            temp_file.unlink()
            
            return output_file
        
        else:
            # Direct conversion for already formatted text files
            return self._convert_single_format(source_path, target_format, output_dir, DocumentType.CONTRACT)
    
    def _markdown_to_formatted_text(self, md_path: str) -> str:
        """Convert markdown with ASCII diagrams to properly formatted text"""
        
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Convert markdown code blocks to preserve formatting
        lines = content.split('\n')
        formatted_lines = []
        in_code_block = False
        
        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            
            # Convert markdown headers to text formatting
            if line.startswith('# '):
                formatted_lines.append('')
                formatted_lines.append('=' * 80)
                formatted_lines.append(line[2:].upper().center(80))
                formatted_lines.append('=' * 80)
                formatted_lines.append('')
            elif line.startswith('## '):
                formatted_lines.append('')
                formatted_lines.append(line[3:].upper())
                formatted_lines.append('-' * len(line[3:]))
            elif line.startswith('### '):
                formatted_lines.append('')
                formatted_lines.append(line[4:])
            else:
                # Preserve ASCII diagrams and regular text
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def get_recommended_formats(self, doc_type: DocumentType, 
                               recipient_type: str = "client") -> List[OutputFormat]:
        """Get recommended formats for specific document type and recipient"""
        
        if recipient_type == "client":
            return self.format_rules[doc_type]['client_preferred']
        else:
            return self.format_rules[doc_type]['internal_preferred']
    
    def batch_convert_client_package(self, documents: Dict[str, DocumentType],
                                   output_dir: str) -> Dict[str, Dict[OutputFormat, str]]:
        """
        Convert multiple documents for client delivery package
        
        Args:
            documents: {file_path: document_type} mapping
            output_dir: Output directory for converted files
            
        Returns:
            {file_name: {format: output_path}} mapping
        """
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        results = {}
        
        for doc_path, doc_type in documents.items():
            file_name = Path(doc_path).stem
            
            # Get client-preferred formats
            client_formats = self.get_recommended_formats(doc_type, "client")
            
            # Convert to all client formats
            conversion_results = self.convert_document(
                doc_path, doc_type, client_formats, str(output_path)
            )
            
            results[file_name] = conversion_results
            
            print(f"✅ Converted {file_name} to {len([r for r in conversion_results.values() if r])} formats")
        
        return results

def main():
    """Demo the format converter"""
    
    print("📄 SQUIRT FORMAT CONVERTER")
    print("=" * 50)
    
    converter = SquirtFormatConverter()
    
    # Show format recommendations
    print("📋 FORMAT RECOMMENDATIONS:")
    for doc_type in DocumentType:
        client_formats = converter.get_recommended_formats(doc_type, "client")
        internal_formats = converter.get_recommended_formats(doc_type, "internal")
        
        print(f"\n{doc_type.value.upper()}:")
        print(f"  Client:   {', '.join(f.value for f in client_formats)}")
        print(f"  Internal: {', '.join(f.value for f in internal_formats)}")
    
    print(f"\n🎯 KEY FEATURES:")
    print("• Automatic format detection for ASCII diagrams")
    print("• Client-optimized format preferences")
    print("• Monospace font preservation for technical docs")
    print("• Batch conversion for delivery packages")
    print("• LibreOffice integration with error handling")
    
    print(f"\n💼 COMMON CLIENT FORMATS:")
    print("• PDF: Universal compatibility, professional presentation")
    print("• DOCX: Microsoft Word editing capability")
    print("• XLSX: Spreadsheet data with formatting")
    print("• CSV: Simple data exchange format")

if __name__ == "__main__":
    main()