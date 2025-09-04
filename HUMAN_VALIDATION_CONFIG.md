# Human-in-the-Loop Validation Configuration

## Overview
Squirt now automatically implements human-in-the-loop validation for all document generation to ensure visual quality control.

## How It Works
1. **Automatic Document Opening**: After generating any document with visual styling, Squirt automatically opens it for human review
2. **Validation Checklist**: Clear instructions are provided for what to review
3. **Multiple Format Support**: Both ODT source files and PDF outputs are opened for review
4. **Quality Control**: Ensures visual styling meets professional standards before delivery

## Configuration Options

### Enable/Disable Auto-Opening
```python
# Enable automatic human validation (default)
generator.generate_modern_professional_contract(
    client_info, contractor_info, project_info, line_items, output_path,
    auto_open_for_review=True  # Default
)

# Disable for automated/batch processing
generator.generate_modern_professional_contract(
    client_info, contractor_info, project_info, line_items, output_path,
    auto_open_for_review=False
)
```

### Manual Validation Call
```python
# For existing documents
generator.open_document_for_human_review(document_path, "contract")
```

## Validation Checklist

When documents open, review for:
- ✓ **Visual styling**: Colors, fonts, formatting
- ✓ **Professional appearance**: Overall document presentation
- ✓ **Content layout**: Organization and structure
- ✓ **Typography hierarchy**: Title, header, body text sizing
- ✓ **Visual inconsistencies**: Any formatting errors

### Modern Professional Style Elements
- ✓ **Blue section headers** (`#4472c4`): PROJECT SUMMARY, PROJECT TOTALS, etc.
- ✓ **Blue italic subsections**: Materials & Equipment
- ✓ **Professional typography**: 16pt title, 14pt subtitle, 12pt headers
- ✓ **Strategic bold formatting**: For emphasis and structure
- ✓ **Clean table layouts**: Prepared for/by sections
- ✓ **Professional color scheme**: Throughout the document

## Integration with Development Workflow

### When Human Validation Triggers
- ✅ **Template modifications**: Any changes to visual styling
- ✅ **New document generation**: All modern professional contracts
- ✅ **Style testing**: During development and testing
- ✅ **Quality assurance**: Before client delivery

### Files Automatically Generated for Review
1. `*.odt` - Source document with full styling
2. `*.pdf` - Final delivery format (when LibreOffice available)

## Benefits
- **Quality Assurance**: Ensures documents meet visual standards
- **Immediate Feedback**: Catch styling issues before client delivery
- **Professional Standards**: Maintain consistent document appearance
- **Development Safety**: Validate changes during template modifications

## Future Enhancements
- Screenshot-based automated comparison
- Batch validation summaries
- Integration with CI/CD pipelines
- Custom validation checklists per document type