#!/usr/bin/env python3
"""
WaterWizard Sprint 3 Demonstration
Showcase validation, enhanced exports, and PDF polish features
"""

import sys
sys.path.append('src')

from enhanced_pipeline import EnhancedPipeline
from batch_csv_exporter import BatchCSVExporter
from pathlib import Path
import json

def create_comprehensive_test_worksheet():
    """Create a comprehensive test worksheet with various scenarios"""
    
    test_data = """client_name,template_type,zone_number,head_count,trench_feet,soil_type,project_name,client_address,client_city,client_state,client_zip,client_phone,client_email
"Premium Estates LLC",sprinkler_zone,1,12,250,rocky,"Executive Home Front Yard","456 Highland Drive","Austin","TX","78704","(512) 555-9876","info@premiumestates.com"
"Rodriguez Family Trust",sprinkler_zone,2,8,180,clay,"Backyard Entertainment Area","2847 Maple Ridge Drive","Cedar Park","TX","78613","(512) 555-7834","mrodriguez@email.com" 
"Sunset Gardens HOA",sprinkler_zone,3,15,320,roots,"Community Entrance Landscaping","1200 Sunset Blvd","Round Rock","TX","78681","(512) 555-4422","manager@sunsetgardens.com"
"Thompson Residence",head_replacement,,,8,,,"Repair Storm Damage","789 Oak Valley Lane","Austin","TX","78745","(512) 555-3311","thompson.family@email.com"
"Thompson Residence",valve_install,,,,,,"Add Zone 4 Control","789 Oak Valley Lane","Austin","TX","78745","(512) 555-3311","thompson.family@email.com"
"Green Valley Park",trenching,,,450,turf,"Main Water Line Extension","100 Park Avenue","Austin","TX","78701","(512) 555-2200","parks@austin.gov"
"Luxury Townhomes",sprinkler_zone,1,6,120,clay,"Unit 1A Courtyard","1500 River Place","Austin","TX","78730","(512) 555-8899","maintenance@luxurytownhomes.com"
"Luxury Townhomes",sprinkler_zone,2,6,120,clay,"Unit 1B Courtyard","1500 River Place","Austin","TX","78730","(512) 555-8899","maintenance@luxurytownhomes.com"
"""
    
    with open('comprehensive_test.csv', 'w') as f:
        f.write(test_data)
    
    print("📊 Created comprehensive test worksheet with 8 projects")
    return 'comprehensive_test.csv'

def run_comprehensive_demonstration():
    """Run complete Sprint 3 demonstration"""
    
    print("🚀 WATERWIZARD SPRINT 3 DEMONSTRATION")
    print("=" * 60)
    print("🎯 Showcasing: Validation + Enhanced Exports + PDF Polish")
    print("=" * 60)
    
    # Create test data
    worksheet_file = create_comprehensive_test_worksheet()
    
    # Initialize enhanced pipeline
    pipeline = EnhancedPipeline("sprint3_demo_output")
    
    # Process with contracts
    print("\n📄 PROCESSING CONTRACTS WITH VALIDATION...")
    contract_results = pipeline.process_worksheet_with_validation(worksheet_file, 'contract')
    
    # Process with invoices
    print(f"\n📄 PROCESSING INVOICES WITH VALIDATION...")
    invoice_results = pipeline.process_worksheet_with_validation(worksheet_file, 'invoice')
    
    # Batch CSV export
    print(f"\n📊 CREATING BATCH CSV EXPORT...")
    batch_exporter = BatchCSVExporter()
    
    # Combine successful projects from both runs
    all_successful_projects = []
    all_successful_projects.extend([p for p in contract_results['projects'] if p['overall_success']])
    all_successful_projects.extend([p for p in invoice_results['projects'] if p['overall_success']])
    
    batch_csv_file = str(pipeline.output_dir / "waterwizard_complete_batch.csv")
    batch_result = batch_exporter.export_batch_projects(all_successful_projects, batch_csv_file)
    
    # Create QuickBooks guide
    guide_file = str(pipeline.output_dir / "quickbooks_import_guide.txt")
    batch_exporter.create_quickbooks_mapping_guide(guide_file)
    
    print(f"   {batch_result}")
    print(f"   📖 Import guide: {Path(guide_file).name}")
    
    # Generate comprehensive summary
    print(f"\n📈 SPRINT 3 COMPREHENSIVE RESULTS:")
    print("=" * 60)
    
    # Contract summary
    contract_summary = contract_results['summary']
    contract_validation = contract_results['validation_summary']
    
    print(f"📄 CONTRACTS:")
    print(f"   Projects processed: {contract_summary['total_projects']}")
    print(f"   Successfully generated: {contract_summary['successful_generations']}")
    print(f"   Validation passed: {contract_validation.get('passed', 0)}")
    print(f"   Validation warnings: {contract_validation.get('warnings', 0)}")
    print(f"   Validation failed: {contract_validation.get('failed', 0)}")
    print(f"   Total contract value: ${contract_summary['total_value']:.2f}")
    
    # Invoice summary
    invoice_summary = invoice_results['summary']
    invoice_validation = invoice_results['validation_summary']
    
    print(f"\n📋 INVOICES:")
    print(f"   Projects processed: {invoice_summary['total_projects']}")
    print(f"   Successfully generated: {invoice_summary['successful_generations']}")
    print(f"   Validation passed: {invoice_validation.get('passed', 0)}")
    print(f"   Validation warnings: {invoice_validation.get('warnings', 0)}")
    print(f"   Validation failed: {invoice_validation.get('failed', 0)}")
    print(f"   Total invoice value: ${invoice_summary['total_value']:.2f}")
    
    # File summary
    output_dir = pipeline.output_dir
    contract_files = list((output_dir / "contracts").glob("*.txt"))
    invoice_files = list((output_dir / "invoices").glob("*.txt"))
    pdf_files = list((output_dir / "pdfs").glob("*.pdf"))
    csv_files = list((output_dir / "csv_exports").glob("*.csv"))
    validation_files = list((output_dir / "validation_reports").glob("*.txt"))
    
    print(f"\n📁 FILES GENERATED:")
    print(f"   Contracts: {len(contract_files)} documents")
    print(f"   Invoices: {len(invoice_files)} documents") 
    print(f"   PDFs: {len(pdf_files)} files")
    print(f"   Individual CSVs: {len(csv_files)} exports")
    print(f"   Validation reports: {len(validation_files)} reports")
    print(f"   Batch CSV: 1 combined export")
    print(f"   QuickBooks guide: 1 import guide")
    
    # Validation insights
    print(f"\n🔍 VALIDATION INSIGHTS:")
    
    # Check common validation issues
    common_issues = {}
    for result in contract_results['projects'] + invoice_results['projects']:
        validation = result.get('validation_results', {})
        for error_type in ['critical_errors', 'math_errors', 'format_errors']:
            errors = validation.get(error_type, [])
            for error in errors:
                common_issues[error] = common_issues.get(error, 0) + 1
    
    if common_issues:
        print("   Most common validation issues:")
        for issue, count in sorted(common_issues.items(), key=lambda x: x[1], reverse=True)[:3]:
            print(f"   • {issue} ({count} occurrences)")
    else:
        print("   ✅ No common validation issues found")
    
    # Success rates by template type
    print(f"\n📊 SUCCESS RATES BY TEMPLATE TYPE:")
    template_stats = {}
    
    for result in contract_results['projects'] + invoice_results['projects']:
        template_type = result['template_type']
        if template_type not in template_stats:
            template_stats[template_type] = {'total': 0, 'success': 0}
        
        template_stats[template_type]['total'] += 1
        if result['overall_success']:
            template_stats[template_type]['success'] += 1
    
    for template_type, stats in template_stats.items():
        success_rate = (stats['success'] / stats['total']) * 100 if stats['total'] > 0 else 0
        print(f"   {template_type}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
    
    print(f"\n✅ SPRINT 3 DEMONSTRATION COMPLETE!")
    print(f"📁 All outputs in: {output_dir}")
    print(f"🎯 Features demonstrated:")
    print(f"   ✅ Comprehensive document validation")
    print(f"   ✅ Mathematical accuracy verification")
    print(f"   ✅ Format consistency checking")
    print(f"   ✅ Price reasonableness warnings") 
    print(f"   ✅ Enhanced CSV exports for QuickBooks")
    print(f"   ✅ PDF generation with LibreOffice")
    print(f"   ✅ Batch processing capabilities")
    print(f"   ✅ Detailed validation reporting")
    
    return {
        'contract_results': contract_results,
        'invoice_results': invoice_results,
        'output_directory': str(output_dir),
        'batch_csv_file': batch_csv_file,
        'files_generated': {
            'contracts': len(contract_files),
            'invoices': len(invoice_files),
            'pdfs': len(pdf_files),
            'csvs': len(csv_files),
            'validation_reports': len(validation_files)
        }
    }

def main():
    """Run the Sprint 3 demonstration"""
    results = run_comprehensive_demonstration()
    
    # Save results summary
    summary_file = Path(results['output_directory']) / "sprint3_summary.json"
    
    # Prepare JSON-serializable results
    json_results = {
        'demonstration_date': results['contract_results']['timestamp'],
        'files_generated': results['files_generated'],
        'output_directory': results['output_directory'],
        'batch_csv_file': results['batch_csv_file']
    }
    
    with open(summary_file, 'w') as f:
        json.dump(json_results, f, indent=2)
    
    print(f"\n📄 Summary saved to: {summary_file}")

if __name__ == "__main__":
    main()