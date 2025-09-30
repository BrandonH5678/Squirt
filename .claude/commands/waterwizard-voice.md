# WaterWizard Voice Document Generation

Generate professional estimates and invoices from voice memos using AI transcription and content extraction.

## Usage

```
/waterwizard-voice [audio_file] [document_type] [options]
```

## Arguments

- `audio_file`: Path to voice memo audio file (.wav, .mp3, .m4a)
- `document_type`: Type of document to generate (`estimate` or `invoice`)

## Options

- `--mode fast|accurate`: Voice processing mode (default: fast)
  - `fast`: ~30 seconds processing, good for quick estimates
  - `accurate`: ~3 minutes processing, higher accuracy for critical documents
- `--employee [name]`: Name of employee who recorded the memo
- `--review`: Enable interactive review of extracted data before generation
- `--template [path]`: Custom template path (optional)

## Examples

### Quick Estimate from Voice Memo
```
/waterwizard-voice recording.wav estimate --mode fast --employee "John Smith"
```

### High-Accuracy Invoice with Review
```
/waterwizard-voice client_call.m4a invoice --mode accurate --review --employee "Sarah Johnson"
```

### Custom Template
```
/waterwizard-voice estimate_call.wav estimate --template /path/to/custom_template.json
```

## Voice Memo Guidelines

For best results, include in your voice memo:

### Required Information
- **Client name**: "This is for John Smith" or "Client is ABC Company"
- **Service description**: "Fall cleanup" or "Irrigation repair" or "Landscape installation"
- **Property location**: "At 123 Main Street" or "Property on Oak Avenue"

### Optional Information
- **Contact details**: Phone number, email
- **Estimated amount**: "About $500" or "Roughly fifteen hundred dollars"
- **Special requirements**: Access issues, timing constraints
- **Project scope**: Square footage, number of zones, etc.

### Example Voice Memo
> "Hi, this is an estimate for Jane Wilson at 456 Oak Street in Portland. She needs a fall cleanup for her front and back yard, probably about a quarter acre total. Her phone number is 503-555-1234. She mentioned the backyard has a lot of leaves under the deck that are hard to reach. Estimate should be around $400 to $500."

## Processing Flow

1. **Voice Transcription**: Audio converted to text using Whisper AI
2. **Content Extraction**: AI extracts client info, services, amounts, contact details
3. **Data Review**: Optional human review and corrections
4. **Template Processing**: Data merged with appropriate service template
5. **Document Generation**: LibreOffice creates professional PDF and ODT files
6. **Visual Validation**: AI checks document quality and formatting

## Output Files

Generated documents are saved in organized directory structure:

```
Client Files/[ClientName]/
├── [ClientName]_estimate_[date].pdf       # Client-ready PDF
├── [ClientName]_estimate_[date].odt       # Editable document
└── [ClientName]_estimate_[date].csv       # QuickBooks import
```

## Quality Assurance

### Automatic Validation
- Mathematical accuracy verification
- Professional formatting check
- Required field completion
- Template usage confirmation

### Human Review Triggers
- Low transcription confidence (<70%)
- Missing critical information (client name, service description)
- Unusual amounts or pricing
- Audio quality issues

## Business Integration

### Thermal Management
- Voice processing automatically defers during high system temperatures
- Fast mode used when CPU >80°C to prevent overheating

### Business Hours Priority
- Voice processing yields to LibreOffice document generation during business hours (6am-7pm Mon-Fri)
- Accurate mode processing recommended during off-hours

### Error Recovery
- Fallback to manual data entry if voice processing fails
- Backup audio file preservation for re-processing
- Detailed error logging for troubleshooting

## Voice Processing Capabilities

### Supported Audio Formats
- WAV (recommended)
- MP3
- M4A
- OGG

### Language Support
- English (optimized for Pacific Northwest accents)
- Technical landscaping terminology recognition
- Business/client interaction language patterns

### Accuracy Expectations
- **Fast Mode**: ~85% accuracy, 30-60 second processing
- **Accurate Mode**: ~95% accuracy, 2-5 minute processing
- **Names/Addresses**: 70-80% accuracy (review recommended)
- **Numbers/Amounts**: 90%+ accuracy with clear speech

## Troubleshooting

### Common Issues

**Voice not processing**
- Check audio file exists and is readable
- Verify voice engine installation: `python3 -c "import faster_whisper"`
- Check system temperature: `sensors`

**Low accuracy results**
- Use `--mode accurate` for better transcription
- Re-record with clearer speech and less background noise
- Use `--review` mode to manually correct extracted data

**Document generation fails**
- Verify template file exists and is valid JSON
- Check LibreOffice is not in use for other documents
- Review voice processing extraction for missing required fields

**Template not found**
- Default templates located in `/home/johnny5/Squirt/templates/`
- Create custom templates following schema in `templates/schema/estimate_template.schema.json`

### Performance Optimization

**For faster processing:**
- Use WAV files instead of compressed formats
- Record in quiet environment with minimal background noise
- Keep voice memos under 2 minutes when possible
- Use `--mode fast` for routine estimates

**For higher accuracy:**
- Use `--mode accurate` for critical client documents
- Speak clearly with natural pauses between key information
- Record contact information slowly and clearly
- Use `--review` mode for complex or high-value projects

## Related Commands

- `/waterwizard-estimate`: Manual estimate creation
- `/waterwizard-invoice`: Manual invoice creation
- `/waterwizard-validate`: Document validation only
- `/waterwizard-csv-export`: QuickBooks integration

## Technical Requirements

- Python 3.8+ with faster-whisper and openai-whisper packages
- LibreOffice for document generation
- System temperature monitoring for thermal safety
- Minimum 2GB available RAM for voice processing

---

**Note**: Voice processing is a powerful tool but human review is recommended for all client-facing documents to ensure accuracy and professionalism.