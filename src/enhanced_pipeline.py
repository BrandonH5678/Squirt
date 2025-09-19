#!/usr/bin/env python3
"""
WaterWizard Enhanced Pipeline
Sprint 3: Adds validation, enhanced CSV export, and PDF polish to the document pipeline
"""

import sys
sys.path.append('src')

from worksheet_parser import WorksheetParser
from field_mapper import FieldMapper
from template_processor import TemplateProcessor
from document_generator import DocumentGenerator
from modern_document_generator import ModernDocumentGenerator
from csv_exporter import CSVExporter
from validator import DocumentValidator
from accounting_rules import AccountingRulesEngine, DocumentType, DocumentStatus
from file_organizer import SquirtFileOrganizer
from tax_rules import TaxRulesEngine
from format_converter import SquirtFormatConverter, OutputFormat
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Any, Optional
import subprocess

class EnhancedPipeline:
    def __init__(self, output_dir: str = "enhanced_output"):
        """Initialize the enhanced pipeline with validation and export capabilities"""
        self.parser = WorksheetParser()
        self.mapper = FieldMapper()
        self.processor = TemplateProcessor()
        self.generator = DocumentGenerator()
        self.modern_generator = ModernDocumentGenerator()
        self.exporter = CSVExporter()
        self.validator = DocumentValidator()
        self.accounting_engine = AccountingRulesEngine()
        self.file_organizer = SquirtFileOrganizer()
        self.format_converter = SquirtFormatConverter()
        self.tax_engine = TaxRulesEngine()
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for organization
        (self.output_dir / "contracts").mkdir(exist_ok=True)
        (self.output_dir / "invoices").mkdir(exist_ok=True)
        (self.output_dir / "csv_exports").mkdir(exist_ok=True)
        (self.output_dir / "validation_reports").mkdir(exist_ok=True)
        (self.output_dir / "pdfs").mkdir(exist_ok=True)
    
    def process_worksheet_with_validation(self, worksheet_file: str, 
                                        document_type: str = "contract") -> Dict[str, Any]:
        """
        Complete pipeline with validation:
        Worksheet → Templates → Documents → Validation → Exports
        """
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'worksheet_file': worksheet_file,
            'document_type': document_type,
            'projects': [],
            'summary': {},
            'validation_summary': {},
            'export_files': []
        }
        
        try:
            print(f"🚀 ENHANCED WATERWIZARD PIPELINE")
            print(f"📅 Started: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
            print(f"📊 Processing: {worksheet_file}")
            print(f"📄 Document type: {document_type}")
            print("=" * 60)
            
            # Step 1: Parse worksheet
            print("\n1️⃣ PARSING WORKSHEET...")
            projects = self.parser.parse_file(worksheet_file)
            print(f"   Found {len(projects)} projects")
            
            # Step 2: Map fields and validate
            print("\n2️⃣ MAPPING FIELDS...")
            mapping_results = self.mapper.map_batch_projects(projects)
            mapping_report = self.mapper.generate_mapping_report(mapping_results)
            print(f"   Mapped: {mapping_report['successful_mappings']}/{mapping_report['total_projects']}")
            print(f"   Success rate: {mapping_report['success_rate']}")
            
            # Step 3: Process templates with validation
            print("\n3️⃣ GENERATING DOCUMENTS WITH VALIDATION...")
            
            project_results = []
            validation_summary = {'total': 0, 'passed': 0, 'warnings': 0, 'failed': 0}
            
            for i, (template_path, parameters, project, errors) in enumerate(mapping_results, 1):
                client_name = project.get('client_name', f'Client_{i}')
                project_name = project.get('project_name', f'Project_{i}')
                
                project_result = {
                    'project_id': i,
                    'client_name': client_name,
                    'project_name': project_name,
                    'template_type': project.get('template_type'),
                    'mapping_errors': errors,
                    'validation_results': {},
                    'documents_generated': [],
                    'csv_exported': False,
                    'pdf_generated': False,
                    'overall_success': False
                }
                
                if errors:
                    print(f"   ❌ Skipping {client_name}: {len(errors)} mapping errors")
                    project_result['validation_results'] = {'overall_status': 'MAPPING_FAILED'}
                    validation_summary['failed'] += 1
                else:
                    try:
                        # Process template
                        template_result = self.processor.process_template(template_path, parameters)
                        
                        # Prepare client and project info
                        client_info = self._prepare_client_info(project, i)
                        project_info = self._prepare_project_info(project, client_info, i)
                        
                        # Generate document content
                        if document_type == "contract":
                            document_content = self.generator._format_contract(
                                f"WW-{datetime.now().strftime('%Y%m%d')}-{i:03d}",
                                client_info, project_info, template_result['line_items'],
                                Decimal(str(template_result['subtotal'])),
                                Decimal(str(template_result['subtotal'])) * self.generator.tax_rate,
                                Decimal(str(template_result['subtotal'])) * (1 + self.generator.tax_rate),
                                [template_result['narrative']]
                            )
                        else:  # invoice
                            document_content = self.generator._format_invoice(
                                f"INV-{datetime.now().strftime('%Y%m%d')}-{i:03d}",
                                client_info, project_info, template_result['line_items'],
                                Decimal(str(template_result['subtotal'])),
                                Decimal(str(template_result['subtotal'])) * self.generator.tax_rate,
                                Decimal(str(template_result['subtotal'])) * (1 + self.generator.tax_rate)
                            )
                        
                        # Prepare validation data
                        validation_data = {
                            'client_info': client_info,
                            'project_info': project_info,
                            'prepared_by': 'WaterWizard Irrigation & Landscape',
                            'prepared_for': client_name,
                            'project_description': template_result['narrative'],
                            'line_items': template_result['line_items'],
                            'subtotal': template_result['subtotal'],
                            'tax_amount': float(Decimal(str(template_result['subtotal'])) * self.generator.tax_rate),
                            'total': float(Decimal(str(template_result['subtotal'])) * (1 + self.generator.tax_rate)),
                            'tax_rate': float(self.generator.tax_rate),
                            'terms': 'Payment due upon completion',
                            'signature_blocks': 'Customer signature required'
                        }
                        
                        # Run validation
                        validation_results = self.validator.comprehensive_validation(
                            validation_data, document_content
                        )
                        
                        project_result['validation_results'] = validation_results
                        validation_summary['total'] += 1
                        
                        if validation_results['overall_status'] == 'PASS':
                            validation_summary['passed'] += 1
                            print(f"   ✅ {client_name}: Document validated successfully")
                        elif validation_results['overall_status'] == 'PASS_WITH_WARNINGS':
                            validation_summary['warnings'] += 1
                            print(f"   ⚠️  {client_name}: Passed with warnings")
                        else:
                            validation_summary['failed'] += 1
                            print(f"   ❌ {client_name}: Validation failed")
                        
                        # Save documents (even if validation warnings)
                        if validation_results['overall_status'] in ['PASS', 'PASS_WITH_WARNINGS']:
                            # Save text document
                            safe_name = self._safe_filename(client_name)
                            doc_filename = f"{safe_name}_{document_type}_{i:03d}.txt"
                            doc_path = self.output_dir / f"{document_type}s" / doc_filename
                            
                            with open(doc_path, 'w', encoding='utf-8') as f:
                                f.write(document_content)
                            
                            project_result['documents_generated'].append(str(doc_path))
                            
                            # Generate CSV export
                            csv_filename = f"{safe_name}_{document_type}_{i:03d}.csv"
                            csv_path = self.output_dir / "csv_exports" / csv_filename
                            
                            csv_content = self.exporter.export_invoice_to_csv(
                                client_info, project_info, template_result['line_items'],
                                Decimal(str(template_result['subtotal'])),
                                Decimal(str(template_result['subtotal'])) * self.generator.tax_rate,
                                Decimal(str(template_result['subtotal'])) * (1 + self.generator.tax_rate),
                                f"WW-{datetime.now().strftime('%Y%m%d')}-{i:03d}"
                            )
                            
                            with open(csv_path, 'w', newline='') as f:
                                f.write(csv_content)
                            
                            project_result['csv_exported'] = True
                            results['export_files'].append(str(csv_path))
                            
                            # Try to generate PDF
                            try:
                                pdf_path = self._generate_pdf(doc_path)
                                if pdf_path:
                                    project_result['pdf_generated'] = True
                                    project_result['documents_generated'].append(pdf_path)
                            except Exception as e:
                                print(f"   ⚠️  PDF generation failed for {client_name}: {e}")
                            
                            project_result['overall_success'] = True
                        
                        # Save validation report
                        validation_report = self.validator.generate_validation_report(
                            validation_results, f"{client_name} - {project_name}"
                        )
                        
                        report_filename = f"{safe_name}_validation_{i:03d}.txt"
                        report_path = self.output_dir / "validation_reports" / report_filename
                        
                        with open(report_path, 'w') as f:
                            f.write(validation_report)
                        
                    except Exception as e:
                        print(f"   ❌ Processing failed for {client_name}: {str(e)}")
                        project_result['validation_results'] = {'overall_status': 'PROCESSING_FAILED'}
                        validation_summary['failed'] += 1
                
                project_results.append(project_result)
            
            # Step 4: Generate summary
            print(f"\n4️⃣ SUMMARY:")
            print(f"   Total projects: {validation_summary['total']}")
            print(f"   Passed validation: {validation_summary['passed']}")
            print(f"   Passed with warnings: {validation_summary['warnings']}")
            print(f"   Failed validation: {validation_summary['failed']}")
            
            successful_projects = [p for p in project_results if p['overall_success']]
            total_value = sum(
                float(self.processor.process_template(
                    mapping_results[i][0], mapping_results[i][1]
                )['subtotal'])
                for i, p in enumerate(project_results) 
                if p['overall_success']
            )
            
            print(f"   Successfully generated: {len(successful_projects)} documents")
            print(f"   Total project value: ${total_value:.2f}")
            print(f"   Output directory: {self.output_dir}")
            
            results['projects'] = project_results
            results['summary'] = {
                'total_projects': len(project_results),
                'successful_generations': len(successful_projects),
                'total_value': total_value,
                'mapping_report': mapping_report
            }
            results['validation_summary'] = validation_summary
            
        except Exception as e:
            print(f"❌ Pipeline error: {e}")
            results['error'] = str(e)
        
        return results
    
    def generate_client_package(self, client_name: str, documents: Dict[str, str],
                               output_formats: List[OutputFormat] = None) -> Dict[str, Any]:
        """
        Generate complete client delivery package with optimized formats
        
        Args:
            client_name: Name of client for folder organization
            documents: {document_path: document_type} mapping
            output_formats: Specific formats to generate (default: client-preferred)
            
        Returns:
            Results including all generated formats and paths
        """
        
        # Create client-specific output directory
        client_folder = self.file_organizer.client_files_path / self._sanitize_name(client_name)
        client_folder.mkdir(exist_ok=True)
        
        results = {
            'client_name': client_name,
            'client_folder': str(client_folder),
            'documents': {},
            'formats_generated': [],
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"📦 GENERATING CLIENT PACKAGE: {client_name}")
        print("=" * 60)
        
        for doc_path, doc_type_str in documents.items():
            doc_name = Path(doc_path).stem
            
            # Convert string to DocumentType enum
            from format_converter import DocumentType as FmtDocType
            doc_type_map = {
                'contract': FmtDocType.CONTRACT,
                'invoice': FmtDocType.INVOICE, 
                'estimate': FmtDocType.ESTIMATE,
                'receipt': FmtDocType.RECEIPT,
                'worksheet': FmtDocType.WORKSHEET
            }
            
            doc_type = doc_type_map.get(doc_type_str.lower(), FmtDocType.CONTRACT)
            
            # Get recommended formats if none specified
            if output_formats is None:
                client_formats = self.format_converter.get_recommended_formats(doc_type, "client")
            else:
                client_formats = output_formats
            
            print(f"📄 Converting {doc_name} to {len(client_formats)} formats...")
            
            # Convert document to client formats
            conversion_results = self.format_converter.convert_document(
                doc_path, doc_type, client_formats, str(client_folder)
            )
            
            # Track successful conversions
            successful_formats = [fmt for fmt, path in conversion_results.items() if path]
            results['documents'][doc_name] = {
                'original_path': doc_path,
                'document_type': doc_type_str,
                'formats': {fmt.value: path for fmt, path in conversion_results.items() if path},
                'successful_formats': [fmt.value for fmt in successful_formats]
            }
            
            results['formats_generated'].extend([fmt.value for fmt in successful_formats])
            
            print(f"   ✅ {len(successful_formats)} formats: {', '.join(fmt.value for fmt in successful_formats)}")
        
        # Generate updated client index
        index_path = self.file_organizer.generate_client_index()
        results['index_updated'] = index_path
        
        # Summary
        total_files = sum(len(doc['formats']) for doc in results['documents'].values())
        unique_formats = list(set(results['formats_generated']))
        
        print(f"\n✅ CLIENT PACKAGE COMPLETE:")
        print(f"   📁 Folder: {client_folder}")
        print(f"   📄 Files: {total_files} documents in {len(unique_formats)} formats")
        print(f"   🎯 Formats: {', '.join(unique_formats)}")
        
        return results
    
    def _sanitize_name(self, name: str) -> str:
        """Convert names to safe folder names"""
        safe_name = name.replace('/', '-').replace('\\', '-').replace(':', '-')
        safe_name = ''.join(c for c in safe_name if c.isalnum() or c in '-_ ')
        return safe_name.strip()
    
    def _prepare_client_info(self, project: Dict[str, Any], project_id: int) -> Dict[str, str]:
        """Prepare client information dictionary"""
        return {
            'name': project.get('client_name', f'Client_{project_id}'),
            'address': project.get('client_address', '123 Main Street'),
            'city': project.get('client_city', 'Austin'),
            'state': project.get('client_state', 'TX'),
            'zip': project.get('client_zip', '78701'),
            'phone': project.get('client_phone', '(555) 123-4567'),
            'email': project.get('client_email', 'client@example.com')
        }
    
    def _prepare_project_info(self, project: Dict[str, Any], client_info: Dict[str, str], 
                             project_id: int) -> Dict[str, str]:
        """Prepare project information dictionary"""
        return {
            'name': project.get('project_name', f'Project_{project_id}'),
            'address': project.get('project_address', client_info['address']),
            'id': str(project_id).zfill(3)
        }
    
    def _safe_filename(self, name: str) -> str:
        """Convert client name to safe filename"""
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
        return safe_name.replace(' ', '_')
    
    def _generate_pdf(self, text_file_path: Path) -> Optional[str]:
        """Try to generate PDF from text file using LibreOffice"""
        try:
            pdf_filename = text_file_path.stem + '.pdf'
            pdf_path = self.output_dir / "pdfs" / pdf_filename
            
            # Use LibreOffice to convert to PDF
            cmd = [
                'libreoffice', '--headless', '--convert-to', 'pdf',
                '--outdir', str(self.output_dir / "pdfs"),
                str(text_file_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and pdf_path.exists():
                return str(pdf_path)
            else:
                return None
                
        except Exception:
            return None
    
    def process_worksheet_modern(self, worksheet_file: str, 
                               document_type: str = "contract") -> Dict[str, Any]:
        """
        Modern processing pipeline using professional LibreOffice templates
        """
        print(f"🎨 MODERN PROCESSING: {worksheet_file} → {document_type}")
        print("=" * 60)
        
        results = {
            'success': False,
            'projects': [],
            'summary': {},
            'validation_summary': {},
            'output_directory': str(self.output_dir)
        }
        
        try:
            # Step 1: Parse worksheet
            print("1️⃣ Parsing worksheet...")
            projects = self.parser.parse_file(worksheet_file)
            print(f"   Found {len(projects)} projects")
            
            # Step 2: Map fields to template parameters
            print("2️⃣ Mapping fields to templates...")
            mapping_results = self.mapper.map_batch_projects(projects)
            
            # Step 3: Process with modern generation
            print("3️⃣ Generating modern professional documents...")
            
            project_results = []
            validation_summary = {'total': 0, 'passed': 0, 'warnings': 0, 'failed': 0}
            
            for i, (template_path, parameters, project, errors) in enumerate(mapping_results, 1):
                client_name = project.get('client_name', f'Client_{i}')
                project_name = project.get('project_name', f'Project_{i}')
                
                validation_summary['total'] += 1
                
                project_result = {
                    'project_id': i,
                    'client_name': client_name,
                    'project_name': project_name,
                    'overall_success': False,
                    'modern_files': {},
                    'validation_results': {}
                }
                
                if not errors:
                    try:
                        # Prepare client and project info
                        client_info = self._prepare_client_info(project, i)
                        project_info = self._prepare_project_info(project, client_info, i)
                        
                        # Generate using modern templates
                        templates_with_params = [(template_path, parameters)]
                        
                        safe_name = self._safe_filename(client_name)
                        
                        if document_type == "contract":
                            # Generate modern contract
                            odt_filename = f"{safe_name}_contract_{i:03d}.odt"
                            odt_path = str(self.output_dir / "contracts" / odt_filename)
                            
                            self.modern_generator.generate_professional_contract(
                                client_info, project_info, templates_with_params, odt_path
                            )
                            
                            # Skip automatic PDF conversion - use GUI screenshots for validation instead
                            # PDF can be generated manually if needed for client delivery
                            # pdf_path = self.modern_generator.convert_to_pdf(odt_path)
                            
                            # IMPORTANT: Copy to client folder for easy human access
                            client_files = [odt_path]
                            client_folder = self.file_organizer.organize_client_documents(
                                client_name, project_name, client_files, copy_files=True
                            )
                            
                            project_result['modern_files'] = {
                                'odt': odt_path,
                                'pdf': pdf_path,
                                'client_folder': client_folder
                            }
                            
                        elif document_type == "invoice":
                            # Generate modern invoice (future enhancement)
                            print(f"   📋 Modern invoice generation not yet implemented for {client_name}")
                            continue
                        
                        # Process template to get line items for validation
                        template_result = self.processor.process_template(template_path, parameters)
                        
                        # Calculate tax for validation
                        subtotal = float(template_result['subtotal'])
                        tax_rate, _ = self.tax_engine.get_tax_rate(client_info.get('state', 'OR'))
                        tax_amount = subtotal * float(tax_rate)
                        total = subtotal + tax_amount
                        
                        # Validate the processed template
                        validation_issues = []
                        validation_issues.extend(self.validator.validate_mathematical_accuracy(
                            template_result['line_items'], float(subtotal), tax_amount, total, float(tax_rate)
                        ))
                        validation_issues.extend(self.validator.validate_price_reasonableness(
                            template_result['line_items']
                        ))
                        
                        validation_report = {
                            'overall_status': 'PASSED' if not validation_issues else 'WARNING',
                            'issues': validation_issues
                        }
                        
                        project_result['validation_results'] = validation_report
                        
                        if validation_report['overall_status'] == 'PASSED':
                            validation_summary['passed'] += 1
                            project_result['overall_success'] = True
                            print(f"   ✅ Generated modern {document_type}: {client_name}")
                        else:
                            validation_summary['warnings'] += 1
                            project_result['overall_success'] = True  # Still generated
                            print(f"   ⚠️  Generated with warnings: {client_name}")
                        
                        # Save validation report
                        report_filename = f"{safe_name}_validation_{i:03d}.txt"
                        report_path = self.output_dir / "validation_reports" / report_filename
                        
                        with open(report_path, 'w') as f:
                            f.write(f"Modern Document Validation Report\n")
                            f.write(f"Client: {client_name}\n")
                            f.write(f"Status: {validation_report['overall_status']}\n\n")
                            if validation_report.get('issues'):
                                f.write("Issues:\n")
                                for issue in validation_report['issues']:
                                    f.write(f"- {issue}\n")
                        
                    except Exception as e:
                        print(f"   ❌ Modern generation failed for {client_name}: {str(e)}")
                        project_result['validation_results'] = {'overall_status': 'GENERATION_FAILED'}
                        validation_summary['failed'] += 1
                else:
                    print(f"   ❌ Skipping {client_name}: {len(errors)} mapping errors")
                    validation_summary['failed'] += 1
                
                project_results.append(project_result)
            
            # Step 4: Generate summary
            print(f"\n4️⃣ MODERN GENERATION SUMMARY:")
            print(f"   Total projects: {validation_summary['total']}")
            print(f"   Successfully generated: {validation_summary['passed']}")
            print(f"   Generated with warnings: {validation_summary['warnings']}")
            print(f"   Failed generation: {validation_summary['failed']}")
            
            successful_projects = [p for p in project_results if p['overall_success']]
            print(f"   Modern documents created: {len(successful_projects)}")
            print(f"   Output directory: {self.output_dir}")
            
            results['success'] = True
            results['projects'] = project_results
            results['summary'] = {
                'total_projects': len(project_results),
                'successful_generations': len(successful_projects),
                'generation_type': 'modern_professional'
            }
            results['validation_summary'] = validation_summary
            
        except Exception as e:
            print(f"❌ Modern pipeline error: {e}")
            results['error'] = str(e)
        
        return results

def main():
    """Demo the enhanced pipeline"""
    pipeline = EnhancedPipeline()
    
    print("🚀 ENHANCED WATERWIZARD PIPELINE - SPRINT 3")
    print("=" * 60)
    
    # Process the sample worksheet with validation
    results = pipeline.process_worksheet_with_validation('sample_projects.csv', 'contract')
    
    print(f"\n✅ PIPELINE COMPLETE!")
    print(f"📁 All outputs saved to: {pipeline.output_dir}")
    print(f"📊 Check validation_reports/ for detailed validation results")

if __name__ == "__main__":
    main()