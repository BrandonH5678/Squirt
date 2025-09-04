#!/usr/bin/env python3
"""
Populate the working LibreOffice-generated template with actual contract data
to test if the structure remains valid when populated.
"""

import zipfile
import os
from pathlib import Path

def populate_working_template():
    """
    Take the working reference template and populate it with real data
    """
    
    reference_path = "/home/johnny5/Squirt/template_reference/waterwizard_reference_template.odt"
    output_path = "/home/johnny5/Squirt/template_reference/populated_test_contract.odt"
    
    # Extract the working template
    extract_dir = "/home/johnny5/Squirt/template_reference/working_extract"
    os.makedirs(extract_dir, exist_ok=True)
    
    with zipfile.ZipFile(reference_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    # Read the content.xml
    content_path = os.path.join(extract_dir, "content.xml")
    with open(content_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace placeholders with actual data
    replacements = {
        '{{COMPANY_NAME}}': 'WaterWizard',
        '{{CLIENT_NAME}}': 'John Smith Test Client',
        '{{CLIENT_ADDRESS}}': '123 Test Street\nTestville, OR 97000',
        '{{CONTRACTOR_NAME}}': 'WaterWizard Irrigation & Landscape Services',
        '{{CONTRACTOR_ADDRESS}}': '456 Business Ave\nPortland, OR 97201',
        '{{PROJECT_DESCRIPTION}}': 'Complete sprinkler system installation with 2 zones',
        '{{PROJECT_DATE}}': 'September 3, 2025',
        '{{PROJECT_LOCATION}}': '123 Test Street, Testville, OR',
        '{{MATERIALS_LIST}}': '• 2x Rain Bird electronic valves @ $175.00 each = $350.00\n• 8x Sprinkler heads @ $45.00 each = $360.00\n• 150ft trenching in turf @ $6.50/ft = $975.00',
        '{{LABOR_DETAILS}}': '• System design and planning: 2 hours\n• Installation and testing: 6 hours\n• Total labor: 8 hours @ $85.00/hour = $680.00',
        '{{SUBTOTAL}}': '2,365.00',
        '{{TAX_AMOUNT}}': '0.00',
        '{{TOTAL_AMOUNT}}': '2,365.00',
        '{{TERMS_CONDITIONS}}': 'Work to be completed within 5 business days of contract signing. Payment due within 30 days of project completion. All materials are warranted for 1 year.'
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
    
    print(f"✅ Created populated template: {output_path}")
    
    # Clean up
    import shutil
    shutil.rmtree(extract_dir)
    
    return output_path

if __name__ == "__main__":
    result = populate_working_template()
    print(f"📄 Please test opening: {result}")
    print("🔍 Verify:")
    print("  1. Opens without XML error dialogs")
    print("  2. Blue headers are preserved") 
    print("  3. All data appears correctly formatted")
    print("  4. Professional appearance maintained")