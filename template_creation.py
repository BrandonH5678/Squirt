#!/usr/bin/env python3
"""
Create a WaterWizard contract template using LibreOffice to generate valid ODT structure.
This will serve as our reference for proper ODT XML generation.
"""

import subprocess
import os
import tempfile

def create_reference_template():
    """Create a reference ODT template with WaterWizard styling using LibreOffice."""
    
    # Create a temporary HTML file with our desired styling and content
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; margin: 1in; }
        .title { font-size: 16pt; font-weight: bold; text-align: center; margin-bottom: 20px; }
        .subtitle { font-size: 14pt; text-align: center; margin-bottom: 30px; }
        .section-header { 
            font-size: 12pt; 
            font-weight: bold; 
            color: #4472c4; 
            margin-top: 20px; 
            margin-bottom: 10px;
        }
        .subsection { 
            font-style: italic; 
            color: #4472c4; 
            margin-top: 15px; 
            margin-bottom: 8px;
        }
        .prepared-table { 
            width: 100%; 
            border-collapse: collapse; 
            margin-bottom: 20px;
        }
        .prepared-table td { 
            padding: 5px; 
            vertical-align: top;
        }
        .bold { font-weight: bold; }
    </style>
</head>
<body>
    <div class="title">{{COMPANY_NAME}} Contract</div>
    <div class="subtitle">Professional Irrigation & Landscape Services</div>
    
    <table class="prepared-table">
        <tr>
            <td class="bold">Prepared for:</td>
            <td>{{CLIENT_NAME}}<br>{{CLIENT_ADDRESS}}</td>
            <td class="bold">Prepared by:</td>
            <td>{{CONTRACTOR_NAME}}<br>{{CONTRACTOR_ADDRESS}}</td>
        </tr>
    </table>
    
    <div class="section-header">PROJECT SUMMARY</div>
    <p><span class="bold">Project:</span> {{PROJECT_DESCRIPTION}}</p>
    <p><span class="bold">Date:</span> {{PROJECT_DATE}}</p>
    <p><span class="bold">Location:</span> {{PROJECT_LOCATION}}</p>
    
    <div class="section-header">PROJECT TOTALS</div>
    
    <div class="subsection">Materials & Equipment</div>
    <p>{{MATERIALS_LIST}}</p>
    
    <div class="subsection">Labor & Installation</div>
    <p>{{LABOR_DETAILS}}</p>
    
    <p><span class="bold">Subtotal:</span> ${{SUBTOTAL}}</p>
    <p><span class="bold">Tax:</span> ${{TAX_AMOUNT}}</p>
    <p><span class="bold">Total:</span> ${{TOTAL_AMOUNT}}</p>
    
    <div class="section-header">TERMS AND CONDITIONS</div>
    <p>{{TERMS_CONDITIONS}}</p>
    
    <div class="section-header">SIGNATURES</div>
    <table class="prepared-table">
        <tr>
            <td>Client Signature: ___________________</td>
            <td>Date: ___________</td>
        </tr>
        <tr>
            <td>Contractor Signature: ___________________</td>
            <td>Date: ___________</td>
        </tr>
    </table>
</body>
</html>
    """
    
    # Write HTML to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(html_content)
        html_file = f.name
    
    # Convert HTML to ODT using LibreOffice
    output_dir = "/home/johnny5/Squirt/template_reference"
    os.makedirs(output_dir, exist_ok=True)
    odt_file = os.path.join(output_dir, "waterwizard_reference_template.odt")
    
    try:
        # Convert HTML to ODT
        result = subprocess.run([
            'libreoffice', '--headless', '--convert-to', 'odt', 
            '--outdir', output_dir, html_file
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Rename the output file to our desired name
            converted_file = os.path.join(output_dir, os.path.basename(html_file).replace('.html', '.odt'))
            if os.path.exists(converted_file):
                os.rename(converted_file, odt_file)
            
            print(f"✅ Successfully created reference ODT template: {odt_file}")
            print(f"LibreOffice output: {result.stdout}")
            return odt_file
        else:
            print(f"❌ LibreOffice conversion failed:")
            print(f"Return code: {result.returncode}")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ LibreOffice conversion timed out")
        return None
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        return None
    finally:
        # Clean up temporary HTML file
        os.unlink(html_file)

if __name__ == "__main__":
    create_reference_template()