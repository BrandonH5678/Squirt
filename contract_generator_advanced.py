#!/usr/bin/env python3
"""
Create a perfectly aligned WaterWizard contract using the proper table structure
"""

import zipfile
import os
from pathlib import Path

def create_perfect_contract():
    """
    Create a perfectly formatted contract with properly aligned prepared for/by blocks
    """
    
    reference_path = "/home/johnny5/Squirt/template_reference/waterwizard_reference_template.odt"
    output_path = "/home/johnny5/Squirt/template_reference/perfect_waterwizard_contract.odt"
    
    # Extract the working template
    extract_dir = "/home/johnny5/Squirt/template_reference/perfect_extract"
    os.makedirs(extract_dir, exist_ok=True)
    
    with zipfile.ZipFile(reference_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    # Read the content.xml
    content_path = os.path.join(extract_dir, "content.xml")
    with open(content_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace placeholders with perfectly formatted data
    replacements = {
        '{{COMPANY_NAME}}': 'WaterWizard',
        '{{CLIENT_NAME}}': 'John Smith',
        '{{CLIENT_ADDRESS}}': '123 Maple Street<text:line-break/>Testville, OR 97000',
        '{{CONTRACTOR_NAME}}': 'WaterWizard Irrigation &amp; Landscape Services',
        '{{CONTRACTOR_ADDRESS}}': '456 Business Avenue<text:line-break/>Portland, OR 97201<text:line-break/>Phone: (503) 555-0123',
        '{{PROJECT_DESCRIPTION}}': 'Complete sprinkler system installation with 2 zones, trenching, and professional landscaping',
        '{{PROJECT_DATE}}': 'September 3, 2025',
        '{{PROJECT_LOCATION}}': '123 Maple Street, Testville, OR 97000',
        '{{MATERIALS_LIST}}': '• 2x Rain Bird 1" Electronic Valve @ $175.00 each = $350.00<text:line-break/>• 8x Hunter MP Rotator Sprinkler Heads @ $45.00 each = $360.00<text:line-break/>• 150ft Trenching in Regular Turf @ $6.50/ft = $975.00<text:line-break/>• PVC Pipe and Fittings = $285.00',
        '{{LABOR_DETAILS}}': '• System Design and Layout: 2 hours @ $85.00/hour = $170.00<text:line-break/>• Installation and Trenching: 6 hours @ $85.00/hour = $510.00<text:line-break/>• Testing and Final Adjustments: 1 hour @ $85.00/hour = $85.00',
        '{{SUBTOTAL}}': '2,735.00',
        '{{TAX_AMOUNT}}': '0.00',
        '{{TOTAL_AMOUNT}}': '2,735.00',
        '{{TERMS_CONDITIONS}}': 'Work to be completed within 5 business days of contract signing. Payment due within 30 days of project completion. All materials carry manufacturer warranties. Installation guaranteed for 1 year. Client responsible for obtaining necessary permits.'
    }
    
    # Apply replacements
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)
    
    # Write the updated content
    with open(content_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Recreate the ODT file
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as new_zip:
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, extract_dir)
                new_zip.write(file_path, arc_path)
    
    print(f"✅ Created perfect contract: {output_path}")
    
    # Clean up
    import shutil
    shutil.rmtree(extract_dir)
    
    return output_path

if __name__ == "__main__":
    result = create_perfect_contract()
    print(f"📄 Perfect contract ready for validation: {result}")
    print("🔍 This version should have:")
    print("  - Properly aligned prepared for/by table")
    print("  - Professional detailed content")
    print("  - All formatting requirements met")