# Squirt Vision Validation System

A comprehensive screenshot-based document validation system using Claude Vision API for automated quality assessment of generated LibreOffice documents.

## Overview

This system captures screenshots of generated documents and uses AI vision analysis to validate document quality, formatting, and professional appearance - catching issues that traditional code testing cannot detect.

## Features

- **Automated Screenshot Capture**: Converts ODT → PDF → Screenshot for analysis
- **Claude Vision Integration**: Structured prompts for document quality assessment
- **Professional Validation Criteria**: Tests layout, formatting, content completeness
- **Validation History**: Timestamped JSON reports for tracking quality over time
- **Fallback Methods**: Multiple screenshot capture strategies for reliability

## Quick Start

```python
from src.vision_validator import VisionValidator

# Initialize validator
validator = VisionValidator()

# Test a document
odt_path = "/path/to/document.odt"

# Capture screenshot
screenshot = validator.capture_document_screenshot(odt_path)

# Analyze with vision
if screenshot['success']:
    analysis = validator.analyze_document_with_vision(screenshot['screenshot_base64'])
    
    if analysis['ready_for_claude_vision']:
        # Ready for Claude Vision API integration
        print("Vision analysis prepared!")
        print(f"Prompt: {analysis['prompt']}")
        # analysis['image_data'] contains base64 screenshot
```

## Validation Criteria

The system evaluates documents against 8 professional criteria:

1. **Professional Appearance** - Overall document presentation
2. **Header Formatting** - Title and company name styling
3. **Table Structure** - Alignment and organization
4. **Content Completeness** - All required fields present
5. **Typography** - Font consistency and readability  
6. **Layout Balance** - Proper spacing and margins
7. **Data Accuracy** - Correct information display
8. **Print Readiness** - Suitable for professional printing

## Architecture

```
VisionValidator
├── capture_document_screenshot()    # ODT → PDF → PNG
├── analyze_document_with_vision()   # Prepare Claude Vision analysis
├── save_validation_history()       # Store results
└── _create_vision_validation_prompt() # Generate analysis prompts
```

## Installation Requirements

```bash
# System dependencies
sudo apt-get install libreoffice poppler-utils

# Python packages (if needed)
pip install Pillow
```

## Usage Examples

### Basic Document Validation

```python
validator = VisionValidator()

# Generate and validate document
result = validator.capture_document_screenshot("contract.odt")
if result['success']:
    print(f"Screenshot saved: {result['screenshot_path']}")
    
    # Prepare for vision analysis
    analysis = validator.analyze_document_with_vision(result)
    print(f"Analysis type: {analysis['analysis_type']}")
```

### Integration with Document Generation

```python
def generate_and_validate_contract(client_data):
    # Generate ODT document
    odt_path = create_contract(client_data)
    
    # Validate with vision system
    validator = VisionValidator()
    screenshot = validator.capture_document_screenshot(odt_path)
    
    if screenshot['success']:
        analysis = validator.analyze_document_with_vision(screenshot)
        
        if analysis['ready_for_claude_vision']:
            # Send to Claude Vision API for automated validation
            # This would integrate with actual Claude API
            vision_results = send_to_claude_vision(analysis)
            
            # Save validation history
            validator.save_validation_history(vision_results, odt_path)
            
            return vision_results
    
    return None
```

## File Structure

```
src/
└── vision_validator.py          # Main validation system
validation_screenshots/          # Captured document images  
validation_history/             # JSON validation reports
template_reference/             # ODT templates and samples
```

## Validation Report Format

```json
{
  "timestamp": "2025-01-03T10:30:45",
  "document_path": "/path/to/document.odt",
  "overall_score": 8,
  "criteria": [
    {
      "category": "Professional Appearance",
      "description": "Document looks professional and polished",
      "status": "PASS"
    }
  ],
  "screenshot_path": "/path/to/screenshot.png"
}
```

## Integration Notes

- **Claude Vision API**: System prepares structured prompts and base64 images
- **LibreOffice Compatibility**: Handles ODT format conversion automatically  
- **Error Handling**: Graceful fallbacks for screenshot capture failures
- **Performance**: Efficient PDF conversion with headless LibreOffice

## Development Status

✅ **Completed**:
- Screenshot capture system
- Vision analysis preparation
- Validation criteria framework
- History tracking

🔄 **In Progress**:
- Extended document type support (invoices, reports)
- Enhanced error recovery
- Performance optimization

## Contributing

This system was developed as part of the Squirt document automation project. It can be adapted for any LibreOffice-based document generation system requiring visual quality validation.

## License

Developed for integration with document automation systems. Adapt as needed for your specific use case.

---

*Part of the Squirt document automation ecosystem - ensuring generated documents meet professional standards through automated visual validation.*