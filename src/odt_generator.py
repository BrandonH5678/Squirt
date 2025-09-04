#!/usr/bin/env python3
"""
WaterWizard ODT Generator
Generates LibreOffice Writer (ODT) documents from template parameters
"""

import json
import subprocess
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Any, Tuple
from template_processor import TemplateProcessor

class ODTGenerator:
    def __init__(self):
        """Initialize ODT generator"""
        self.processor = TemplateProcessor()
        self.tax_rate = Decimal("0.0875")  # 8.75%
        
    def generate_contract_odt(self, client_info: Dict[str, Any], project_info: Dict[str, Any], 
                             template_results: List[Dict[str, Any]], output_path: str) -> str:
        """Generate ODT contract document from template results"""
        
        # Generate the text content first
        content = self._generate_contract_content(client_info, project_info, template_results)
        
        # Write to a temporary text file
        temp_txt_path = output_path.replace('.odt', '_temp.txt')
        with open(temp_txt_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Try to convert to ODT using LibreOffice if available
        try:
            odt_path = self._convert_to_odt(temp_txt_path, output_path)
            return odt_path
        except Exception as e:
            print(f"Warning: Could not create ODT file: {e}")
            print("Saving as formatted text file instead...")
            # Rename temp file to final text output
            final_txt_path = output_path.replace('.odt', '.txt')
            Path(temp_txt_path).rename(final_txt_path)
            return final_txt_path
    
    def _generate_contract_content(self, client_info: Dict[str, Any], project_info: Dict[str, Any], 
                                  template_results: List[Dict[str, Any]]) -> str:
        """Generate formatted contract content"""
        
        doc_number = f"WW-{datetime.now().strftime('%Y%m%d')}-{project_info.get('id', '001')}"
        date_str = datetime.now().strftime("%B %d, %Y")
        
        # Calculate totals
        all_line_items = []
        total_subtotal = Decimal("0")
        narratives = []
        
        for result in template_results:
            all_line_items.extend(result['line_items'])
            total_subtotal += Decimal(str(result['subtotal']))
            narratives.append(result['narrative'])
        
        tax_amount = (total_subtotal * self.tax_rate).quantize(Decimal('0.01'))
        grand_total = (total_subtotal + tax_amount).quantize(Decimal('0.01'))
        
        # Group line items by category
        materials = [item for item in all_line_items if item['category'] == 'materials']
        equipment = [item for item in all_line_items if item['category'] == 'equipment']
        labor = [item for item in all_line_items if item['category'] == 'labor']
        
        # Build content
        content = f"""WATERWIZARD IRRIGATION
Professional Installation Contract

CONTRACT NUMBER: {doc_number}
DATE: {date_str}

PREPARED FOR:                          PREPARED BY:
{client_info.get('name', 'N/A')}        WaterWizard Irrigation & Landscape
{client_info.get('address', 'N/A')}     Professional Irrigation Services
{client_info.get('city', '')}, {client_info.get('state', '')} {client_info.get('zip', '')}
Phone: {client_info.get('phone', 'N/A')} Phone: (555) 123-4567
Email: {client_info.get('email', 'N/A')} Email: info@waterwizard.com

PROJECT: {project_info.get('name', 'Irrigation Project')}
LOCATION: {project_info.get('address', client_info.get('address', 'N/A'))}

===================================================================

PROJECT DESCRIPTION:

{chr(10).join(narratives)}

===================================================================

MATERIALS & EQUIPMENT BREAKDOWN:

Description                                   Qty      Rate       Total
-------------------------------------------------------------------"""

        # Add materials
        if materials:
            content += "\nMATERIALS"
            for item in materials:
                desc = item['description'][:40]
                qty_str = f"{item['quantity']:.1f}"
                rate_str = f"${item['unit_rate']:.2f}"
                total_str = f"${item['line_total']:.2f}"
                content += f"\n{desc:<40} {qty_str:>6} {rate_str:>10} {total_str:>10}"
        
        # Add equipment
        if equipment:
            content += "\nEQUIPMENT"
            for item in equipment:
                desc = item['description'][:40]
                qty_str = f"{item['quantity']:.1f}"
                rate_str = f"${item['unit_rate']:.2f}"
                total_str = f"${item['line_total']:.2f}"
                content += f"\n{desc:<40} {qty_str:>6} {rate_str:>10} {total_str:>10}"
        
        # Add labor
        if labor:
            content += "\nLABOR"
            for item in labor:
                desc = item['description'][:40]
                qty_str = f"{item['quantity']:.1f}"
                rate_str = f"${item['unit_rate']:.2f}"
                total_str = f"${item['line_total']:.2f}"
                content += f"\n{desc:<40} {qty_str:>6} {rate_str:>10} {total_str:>10}"
        
        content += f"""
-------------------------------------------------------------------
                                           SUBTOTAL: ${float(total_subtotal):>10.2f}
                                    TAX ({self.tax_rate*100:.2f}%): ${float(tax_amount):>10.2f}
                                              TOTAL: ${float(grand_total):>10.2f}

TERMS AND CONDITIONS:

• Work includes 1-year warranty on installation workmanship
• Materials warranted per manufacturer specifications
• Customer responsible for utility locates prior to work  
• Payment due upon completion of work
• Weather delays may affect completion date
• Site access required for all work areas

ACCEPTANCE:

Customer: ________________________________    Date: _______________

WaterWizard Representative: ________________    Date: {date_str}

==================================================================="""
        
        return content
    
    def _convert_to_odt(self, txt_path: str, odt_path: str) -> str:
        """Convert text file to ODT using LibreOffice"""
        try:
            # Check if LibreOffice is available
            result = subprocess.run(['libreoffice', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                raise Exception("LibreOffice not found or not working")
            
            # Convert using LibreOffice headless mode
            output_dir = Path(odt_path).parent
            cmd = [
                'libreoffice', '--headless', '--convert-to', 'odt',
                '--outdir', str(output_dir), txt_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # LibreOffice creates file with same name but .odt extension
                expected_odt = txt_path.replace('.txt', '.odt')
                if Path(expected_odt).exists():
                    if expected_odt != odt_path:
                        Path(expected_odt).rename(odt_path)
                    return odt_path
                else:
                    raise Exception("ODT file was not created")
            else:
                raise Exception(f"LibreOffice conversion failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise Exception("LibreOffice conversion timed out")
        except FileNotFoundError:
            raise Exception("LibreOffice command not found")
    
    def generate_worksheet_to_documents(self, worksheet_file: str, output_dir: str = "output") -> List[Dict[str, Any]]:
        """
        Complete pipeline: Worksheet → Templates → ODT Documents
        This is the main function that combines all Sprint 2 components
        """
        from worksheet_parser import WorksheetParser
        from field_mapper import FieldMapper
        
        parser = WorksheetParser()
        mapper = FieldMapper()
        
        # Create output directory
        Path(output_dir).mkdir(exist_ok=True)
        
        results = []
        
        try:
            # Step 1: Parse worksheet
            print("📊 Parsing worksheet...")
            projects = parser.parse_file(worksheet_file)
            print(f"   Found {len(projects)} projects")
            
            # Step 2: Map fields to template parameters  
            print("🗺️  Mapping fields...")
            mapping_results = mapper.map_batch_projects(projects)
            
            # Step 3: Process templates and generate documents
            print("📄 Generating documents...")
            
            for i, (template_path, parameters, project, errors) in enumerate(mapping_results, 1):
                client_name = project.get('client_name', f'Client_{i}')
                project_name = project.get('project_name', f'Project_{i}')
                
                result = {
                    'project_id': i,
                    'client_name': client_name,
                    'project_name': project_name,
                    'template_type': project.get('template_type'),
                    'success': False,
                    'errors': errors.copy(),
                    'output_files': []
                }
                
                if errors:
                    print(f"   ❌ Skipping {client_name}: {len(errors)} errors")
                    result['errors'] = errors
                else:
                    try:
                        # Process template
                        template_result = self.processor.process_template(template_path, parameters)
                        
                        # Prepare client and project info
                        client_info = {
                            'name': client_name,
                            'address': project.get('client_address', '123 Main Street'),
                            'city': project.get('client_city', 'Austin'),
                            'state': project.get('client_state', 'TX'),
                            'zip': project.get('client_zip', '78701'),
                            'phone': project.get('client_phone', '(555) 123-4567'),
                            'email': project.get('client_email', 'client@example.com')
                        }
                        
                        project_info = {
                            'name': project_name,
                            'address': client_info['address'],
                            'id': str(i).zfill(3)
                        }
                        
                        # Generate ODT document
                        safe_client_name = "".join(c for c in client_name if c.isalnum() or c in (' ', '-', '_')).strip()
                        safe_client_name = safe_client_name.replace(' ', '_')
                        
                        output_filename = f"{safe_client_name}_{project.get('template_type')}_{i:03d}.odt"
                        output_path = f"{output_dir}/{output_filename}"
                        
                        generated_file = self.generate_contract_odt(
                            client_info, project_info, [template_result], output_path
                        )
                        
                        result['success'] = True
                        result['output_files'].append(generated_file)
                        result['subtotal'] = template_result['subtotal']
                        
                        print(f"   ✅ Generated: {Path(generated_file).name}")
                        
                    except Exception as e:
                        result['errors'].append(f"Document generation error: {str(e)}")
                        print(f"   ❌ Failed {client_name}: {str(e)}")
                
                results.append(result)
            
            # Generate summary
            successful = sum(1 for r in results if r['success'])
            total_value = sum(float(r.get('subtotal', 0)) for r in results if r['success'])
            
            print(f"\n📈 GENERATION SUMMARY:")
            print(f"   Total projects: {len(results)}")
            print(f"   Successfully generated: {successful}")
            print(f"   Failed: {len(results) - successful}")
            print(f"   Total project value: ${total_value:.2f}")
            print(f"   Output directory: {output_dir}")
            
        except Exception as e:
            print(f"❌ Pipeline error: {e}")
            return []
        
        return results

def main():
    """Demo the complete Sprint 2 pipeline"""
    generator = ODTGenerator()
    
    print("📄 WATERWIZARD ODT GENERATOR")
    print("=" * 50)
    print("🚀 Testing complete worksheet-to-document pipeline...")
    
    # Use the sample CSV from earlier tests
    results = generator.generate_worksheet_to_documents('sample_projects.csv', 'sprint2_output')
    
    if results:
        print(f"\n📁 Output files generated in 'sprint2_output/' directory")
        print("✅ Sprint 2 pipeline complete!")

if __name__ == "__main__":
    main()