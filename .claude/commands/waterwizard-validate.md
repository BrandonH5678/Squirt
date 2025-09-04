Run comprehensive validation on WaterWizard documents to ensure completeness and accuracy.

## Usage: /waterwizard-validate [document_type] [file_path]

## Arguments:
- document_type: "contract", "invoice", or "receipt"
- file_path: Path to document file to validate

## Validation Checks:

### Universal Requirements:
- [ ] "Prepared by" section present and complete
- [ ] "Prepared for" section present and complete  
- [ ] All currency values formatted correctly ($X.XX)
- [ ] No mathematical errors in calculations
- [ ] Subtotal + tax = total (where applicable)
- [ ] Professional formatting maintained
- [ ] All required fields populated

### Contract-Specific:
- [ ] Project element headings with costs
- [ ] Narrative descriptions for each element
- [ ] Itemized materials and labor tables
- [ ] Terms and clauses section
- [ ] Signature blocks present
- [ ] Element subtotals sum to project total

### Invoice/Receipt-Specific:
- [ ] Date field present
- [ ] Line item table with qty, price, subtotal
- [ ] Materials + labor = subtotal
- [ ] Tax calculation accurate
- [ ] Payment information (receipts only)

## Process:
1. Load document and parse structure
2. Run all applicable validation rules
3. Flag any missing or incorrect elements
4. Provide specific recommendations for fixes
5. Verify CSV export data matches document totals
6. Generate validation report with pass/fail status

## Output:
- Validation summary (PASS/FAIL)
- List of any issues found
- Specific recommendations for corrections
- Confirmation of CSV export accuracy