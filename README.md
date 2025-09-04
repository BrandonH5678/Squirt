# SQUIRT - WaterWizard Document Automation System

**S**treamlined **Q**uality **U**niform **I**rrigation **R**ecords & **T**emplates

An AI-powered document automation system for irrigation and landscape construction businesses.

## Overview

Squirt transforms manual contract and invoice creation into a streamlined, professional workflow. It eliminates calculation errors, ensures tax compliance, and produces presentation-ready documents in seconds.

## Core Features

- **Smart Document Generation**: Converts project worksheets into professional contracts and invoices
- **Multi-Format Output**: PDF for clients, ODT for editing, CSV for QuickBooks integration
- **Tax Compliance**: State-specific tax rules (Oregon no-tax, Washington district lookup ready)
- **Validation Engine**: Prevents math errors and formatting inconsistencies
- **Professional Branding**: Consistent WaterWizard formatting across all documents

## System Architecture

```
Input Layer → Processing Core → Business Logic → Output Layer
     ↓              ↓               ↓            ↓
Client Data → Parser/Generator → Tax/Validation → Documents/CSV
```

### Key Components:
- **Template Engine**: JSON-based service definitions
- **Data Parser**: Handles real-world spreadsheet input
- **Document Generator**: Professional formatting with branding
- **Tax Engine**: State-specific compliance rules
- **Validator**: Multi-layer accuracy checking
- **File Organizer**: Client/company file structure

## Installation

### Prerequisites
- Python 3.8+
- LibreOffice (for PDF generation)
- Git (for version control)

### Setup
```bash
git clone https://github.com/[your-username]/squirt.git
cd squirt
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

## Usage

### Quick Start
```python
# Generate a contract
python generate_contract.py --client "John Doe" --project "Fall Cleanup" --amount 777.50

# Create invoice
python generate_invoice.py --client "John Doe" --services "Landscape Maintenance"
```

### With Claude Code
```
/waterwizard-contract [client] [project_type] [amount]
/waterwizard-invoice [client] [description]
```

## File Structure

```
squirt/
├── src/                    # Core Python modules
├── .claude/               # Claude Code commands
├── Client Files/          # Individual client documents
├── Company Files/         # Internal business documents
├── tests/                 # Test suite
├── templates/             # Document templates
└── examples/              # Sample projects
```

## State Tax Compliance

- **Oregon**: Automatic no sales tax compliance
- **Washington**: Framework ready for district-based lookup
- **Extensible**: Easy to add new states and tax rules

## Business Impact

- **Time Savings**: 2+ hours → 5 minutes per document
- **Error Prevention**: Mathematical validation prevents costly mistakes
- **Professional Image**: Consistent branded documents
- **Scalability**: Template-driven approach supports unlimited service types

## Development History

Built in iterative sprints focusing on:
1. Core document generation pipeline
2. Professional formatting and validation
3. Multi-format output and file organization
4. Business integration and tax compliance

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is proprietary to WaterWizard Irrigation & Landscape Services.

## Support

For support and questions, contact: info@waterwizard.com

---

**Note**: This system contains business-specific templates and pricing. Client data is excluded from version control for privacy protection.
