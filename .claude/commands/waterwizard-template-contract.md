# WaterWizard Template-Based Contract Generator

Generate professional WaterWizard contracts from source files (ODS, PDF, JSON) using category templates with standard formatting.

## Usage: /waterwizard-template-contract [input_file] [template_category]

## Arguments:
- **input_file**: Path to source file containing project data
  - Supported formats: `.ods`, `.pdf`, `.json`, voice transcription files
  - Example: `/home/johnny5/Downloads/Whitely drainage.ods`
  - Example: `client_project_estimate.json`

- **template_category**: Contract template category to use
  - `drainage` - French drain, surface drainage, downspout extensions
  - `irrigation` - Sprinkler zones, drip systems, valve replacements
  - `hardscape` - Retaining walls, patios, edging
  - `maintenance` - Fall cleanup, pruning, fertilization
  - `lighting` - Path lighting, landscape lighting
  - `planting` - Tree/shrub installation, native plants
  - `excavation` - Trenching, area excavation

## Process:
1. **Load and Parse Input File**:
   - ODS/Excel: Extract line items, pricing, client info
   - PDF: OCR and parse structured estimate data
   - JSON: Direct import of contract data structure
   - Voice transcription: Extract project details from processed memo

2. **Select Template**:
   - Load category template from `/templates/contracts/{template_category}/`
   - Apply template scope, materials, labor, and terms
   - Merge with input file data

3. **Generate Contract** (UNO LibreOffice):
   - Professional WaterWizard header with company info
   - Contract number and date
   - Client information section
   - **Scope of Work**: Bulleted list of deliverables
   - **Materials**: Itemized with quantities, unit costs, subtotals
   - **Labor**: Task descriptions with hours, rates, subtotals
   - **Equipment**: Truck fees and specialized equipment
   - **Pricing Summary**: Materials/Labor/Equipment subtotals, tax, **bold total**
   - **Payment Terms**: Deposit %, balance due timing
   - **Terms & Conditions**: Standard legal clauses
   - **Signature Block**: Client acceptance section

4. **Output**:
   - Generate ODT: `/home/johnny5/Downloads/{client}_{category}_Contract.odt`
   - Generate PDF: `/home/johnny5/Downloads/{client}_{category}_Contract.pdf`
   - Save contract data JSON for future reference

5. **Validation**:
   - Verify all calculations (materials + labor + equipment = subtotal)
   - Confirm tax calculation accuracy
   - Check template completeness (all sections present)
   - Flag missing required fields

## Examples:

```bash
# Generate French drain contract from ODS estimate
/waterwizard-template-contract "/home/johnny5/Downloads/Whitely drainage.ods" drainage

# Generate irrigation contract from JSON data
/waterwizard-template-contract "smith_sprinkler_project.json" irrigation

# Generate hardscape contract from voice memo transcription
/waterwizard-template-contract "jones_retaining_wall_memo.json" hardscape
```

## Template Structure:

Templates are stored in `/home/johnny5/Squirt/templates/contracts/` and include:
- Standard scope of work language
- Common material lists with pricing
- Labor task definitions with rate/hour formulas
- Equipment requirements
- Category-specific terms and conditions
- Calculation formulas for pricing

## Output Format:

**ODT Document** (LibreOffice):
- Professional multi-page contract
- Consistent WaterWizard branding
- Print-ready formatting
- Editable for custom adjustments

**PDF Export**:
- Client-ready professional presentation
- Email-friendly format
- Digital signature compatible

**JSON Data File**:
- Complete contract data structure
- Reusable for modifications
- Audit trail for pricing history

## Technical Implementation:

Uses `src/uno_contract_generator.py` with LibreOffice UNO bridge:
- Headless document generation
- Professional typography and layout
- Automatic table formatting
- PDF export with embedded fonts
- Zero mathematical errors (Decimal precision)

## Integration Points:

- **Voice Processing**: Can accept voice memo transcriptions as input
- **Estimate Templates**: Links to existing estimate template system
- **File Tracking**: Automatically tracks generated contracts
- **QuickBooks Export**: Future integration for accounting sync

---

**Maintains WaterWizard professional standards with zero mathematical errors and <5 minute generation time.**
