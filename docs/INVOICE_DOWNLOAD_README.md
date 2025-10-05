# Invoice PDF Download Script

This PowerShell script downloads customer invoice PDFs from D365 Finance & Operations using Azure CLI and OData actions.

## Prerequisites

1. **Azure CLI installed and configured** (see USER_AUTH.md for setup instructions)
2. **Authenticated with D365FO environment** using `az login`
3. **Appropriate permissions** to access customer invoices in D365FO

## Usage

### Basic Usage
```powershell
.\Download-InvoicePdf.ps1 -LegalEntity "USMF" -InvoiceId "FTI-000001"
```

### Advanced Usage
```powershell
# Specify custom D365FO environment and output path
.\Download-InvoicePdf.ps1 -LegalEntity "DEMF" -InvoiceId "INV-2024-001" -D365FOEnvironment "https://your-d365fo-env.cloudax.dynamics.com" -OutputPath "C:\InvoiceDownloads"

# Skip authentication check (if already authenticated)
.\Download-InvoicePdf.ps1 -LegalEntity "USMF" -InvoiceId "FTI-000001" -SkipAuthentication
```

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `LegalEntity` | Yes | - | The legal entity code (e.g., "USMF", "DEMF") |
| `InvoiceId` | Yes | - | The invoice ID to download |
| `D365FOEnvironment` | No | `https://usnconeboxax1aos.cloud.onebox.dynamics.com` | D365FO environment URL |
| `OutputPath` | No | `.\Reports` | Directory to save the PDF and response JSON |
| `SkipAuthentication` | No | `$false` | Skip Azure CLI authentication check |

## What the Script Does

1. **Authentication Check**: Verifies Azure CLI authentication status
2. **OData Action Call**: Calls the `RunCopilotReport` action using the `SalesInvoiceController`
3. **Response Processing**: Extracts Base64 PDF data from the response
4. **PDF Conversion**: Converts Base64 data to a PDF file
5. **File Management**: Saves both the PDF and raw JSON response

## Output Files

The script creates two files in the output directory:
- `{InvoiceId}.pdf` - The converted invoice PDF
- `{InvoiceId}-response.json` - Raw JSON response from D365FO (for debugging)

## Error Handling

The script includes comprehensive error handling for:
- Azure CLI authentication issues
- D365FO connection problems
- Invalid responses
- File system errors
- Base64 conversion errors

## Examples

### Download Invoice from USMF
```powershell
.\Download-InvoicePdf.ps1 -LegalEntity "USMF" -InvoiceId "FTI-000001"
```

### Download Multiple Invoices (using PowerShell loop)
```powershell
$invoices = @("FTI-000001", "FTI-000002", "FTI-000003")
foreach ($invoice in $invoices) {
    .\Download-InvoicePdf.ps1 -LegalEntity "USMF" -InvoiceId $invoice -SkipAuthentication
}
```

### Custom Environment and Path
```powershell
.\Download-InvoicePdf.ps1 `
    -LegalEntity "PROD" `
    -InvoiceId "INV-2024-12345" `
    -D365FOEnvironment "https://prod-d365fo.company.com" `
    -OutputPath "C:\CompanyInvoices\2024"
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```
   Solution: Run az login --scope https://your-d365fo-env/.default --allow-no-subscriptions
   ```

2. **Invoice Not Found**
   ```
   Check that the InvoiceId exists in the specified LegalEntity
   ```

3. **Permission Denied**
   ```
   Ensure your user has access to the SalesInvoiceController and invoice data
   ```

4. **Base64 Conversion Error**
   ```
   Check the response JSON file to see what data was returned
   ```

### Debug Mode

For debugging, check the response JSON file that's saved alongside the PDF. This contains the full response from D365FO and can help identify issues.

## Related Files

- `Convert-Base64ToPdf.ps1` - Standalone Base64 to PDF converter
- `USER_AUTH.md` - Authentication setup guide
- `.github/prompts/download-customer-invoices.prompt.md` - OData action specification