Generate a professional WaterWizard invoice from completed work data.

## Usage: /waterwizard-invoice [client_name] [work_description] [materials_used] [labor_hours]

## Arguments:
- client_name: Customer name for invoice
- work_description: Brief description of completed work
- materials_used: List of materials with quantities (can be CSV format or natural language)
- labor_hours: Hours spent on job

## Alternative Usage: /waterwizard-invoice [worksheet_file]
- worksheet_file: Path to CSV/ODS file with standardized fields

## Process:
1. Load WaterWizard context and invoice formatting standards
2. Parse input data (either arguments or worksheet file)
3. Map to invoice line items:
   - Date, description, quantity, unit price, line total for each material
   - Labor entries with hours and rates
4. Generate professional invoice with:
   - "Prepared by" and "Prepared for" blocks
   - Itemized table with all materials and labor
   - Subtotal calculation
   - Sales tax (if applicable)
   - Invoice total
5. Validate mathematical accuracy and required fields
6. Generate QuickBooks-compatible CSV export
7. Confirm all formatting matches business standards

For voice-to-invoice workflow: Accept natural language description and intelligently map to standard elements and pricing.