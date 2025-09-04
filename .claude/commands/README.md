# WaterWizard Claude Code Commands

This directory contains custom slash commands for Claude Code to automate WaterWizard irrigation business document generation, validation, and workflow management.

## Command Overview

### Core Commands
- `/waterwizard-context` - Loads business context and document standards
- `/waterwizard-contract [project] [client] [zones] [feet] [soil]` - Generates professional contracts
- `/waterwizard-invoice [client] [description] [materials] [hours]` - Creates itemized invoices  
- `/waterwizard-validate [type] [file]` - Comprehensive document validation
- `/waterwizard-elements [action] [element]` - Manages template library
- `/waterwizard-pricing [category] [item]` - Displays and updates pricing
- `/waterwizard-csv-export [document] [format]` - QuickBooks CSV generation

## Quick Start Workflow

### 1. Load Context
```
/waterwizard-context
```
Initializes Claude with business knowledge, document standards, and formatting requirements.

### 2. Generate Contract
```
/waterwizard-contract "Sprinkler Expansion" "John Smith" 2 150 turf
```
Creates complete contract for 2-zone sprinkler system with 150 feet of trenching in regular turf.

### 3. Validate Document
```
/waterwizard-validate contract /path/to/contract.pdf
```
Runs comprehensive validation checks and provides correction recommendations.

### 4. Export for Accounting
```
/waterwizard-csv-export /path/to/invoice.pdf quickbooks
```
Generates QuickBooks-compatible CSV for seamless accounting integration.

## Template System

### Element Library (`templates/elements.json`)
Atomic pricing templates for:
- Valve installations ($175 typical)
- Sprinkler heads ($45 typical) 
- Trenching by soil type ($6.50-11.70/ft)
- Pipe assembly ($4.85/ft)

### Document Formats
- `contract_format.md` - Professional contract layout
- `invoice_format.md` - Clean invoice structure
- `validation_rules.json` - Comprehensive validation criteria

## Phase 1 Capabilities

✅ **Implemented:**
- Template-based document generation
- Mathematical validation and accuracy
- Professional formatting consistency
- CSV export for QuickBooks
- Element-based pricing system

🚧 **Phase 2 Goals:**
- Voice transcription integration (Whisper)
- Hot-folder workflow automation
- Enhanced validation scripts

🔮 **Phase 3 Vision:**
- RAG-powered template selection
- Vector database for historical data
- Visual diagram generation

## Usage Examples

### Simple Invoice Generation
```
/waterwizard-invoice "Jane Doe" "Sprinkler repair" "2 heads, 20ft pipe" 2.5
```

### Check Pricing
```
/waterwizard-pricing materials valve_electronic
```

### Add New Element
```
/waterwizard-elements add drip_line_installation
```

## File Structure
```
.commands/
├── README.md
├── waterwizard-* (command files)
└── templates/
    ├── elements.json
    ├── contract_format.md
    ├── invoice_format.md
    └── validation_rules.json
```

## Integration Notes

- Designed for 4GB RAM constraints (Phase 1)
- Compatible with LibreOffice and Pandoc
- Outputs ready for QuickBooks import
- Maintains Kim Sherertz contract formatting standards
- Mathematical precision with decimal calculations

---

**Ready for Turn 2 Implementation!** 🚀

This command structure provides Claude Code with everything needed for WaterWizard document orchestration while maintaining the agentic coding principles from the research.