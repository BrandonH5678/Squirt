Generate QuickBooks-compatible CSV export from WaterWizard invoices and contracts.

## Usage: /waterwizard-csv-export [document_path] [export_type]

## Arguments:
- document_path: Path to invoice, contract, or receipt file
- export_type: "quickbooks", "generic", or "custom"

## Export Formats:

### QuickBooks Format:
```csv
Date,Item,Description,Qty,Unit Price,Line Total,Tax Rate,Tax Amount,Invoice Total,Customer,Invoice Number
```

### Generic Accounting Format:
```csv
Date,Account,Description,Debit,Credit,Reference,Customer
```

## Process:
1. Parse source document (contract, invoice, or receipt)
2. Extract all line items with quantities and pricing
3. Separate materials and labor into appropriate rows
4. Calculate tax amounts and totals
5. Format according to selected export type
6. Validate CSV data matches source document totals
7. Generate export file with proper naming convention

## Data Mapping:
- **Materials**: Item name, quantity, unit price, line total
- **Labor**: Task description, hours, hourly rate, labor total  
- **Tax**: Calculated tax amount on taxable items
- **Totals**: Subtotal, tax total, invoice total
- **Metadata**: Date, customer info, invoice/contract number

## Validation:
- Ensure CSV totals match document totals exactly
- Verify all line items are captured
- Check decimal precision (2 places for currency)
- Confirm date formatting consistency
- Validate customer information completeness

## Output:
- CSV file saved with naming: `WaterWizard_{CustomerName}_{InvoiceNumber}_{Date}.csv`
- Validation report confirming data accuracy
- Summary of exported line items and totals

This enables seamless import into QuickBooks or other accounting software while maintaining data integrity.