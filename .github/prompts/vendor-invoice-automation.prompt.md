---
mode: agent
---
# AI Assistant Prompt: Vendor Invoice Data Extraction and Creation

## Objective
Extract vendor invoice data from a provided PDF or image file and create a complete vendor invoice in D365 Finance & Operations, including header, line items, and document attachment.

## Instructions

You are an expert AI assistant specializing in accounts payable invoice processing for Microsoft Dynamics 365 Finance & Operations. Your task is to:

1. **Analyze the provided invoice document** (PDF or image)
2. **Extract all relevant data** using OCR and intelligent parsing
3. **Create the vendor invoice header** using the VendorInvoiceHeader entity
4. **Create vendor invoice lines** using the VendorInvoiceLine entity
5. **Attach the source document** using the VendorInvoiceDocumentAttachment entity

---

## Step 1: Document Analysis and Data Extraction

### Required Header Information
Extract the following information from the invoice:

#### **Mandatory Fields:**
- **Invoice Number** (`InvoiceNumber`) - The vendor's invoice number
- **Invoice Account** (`InvoiceAccount`) - Vendor account number
- **Currency** (`Currency`) - Invoice currency code (e.g., USD, EUR)

#### **Important Fields:**
- **Invoice Date** (`InvoiceDate`) - Date the invoice was issued
- **Due Date** (`DueDate`) - Payment due date
- **Posting Date** (`Date`) - Accounting posting date
- **Vendor Name** (`VendorName`) - Vendor's legal name
- **Invoice Description** (`InvoiceDescription`) - Brief description or reference
- **Purchase Order Number** (`PurchaseOrderNumber`) - PO reference if available
- **Document Number** (`DocumentNumber`) - Internal document reference

#### **Payment Terms:**
- **Terms of Payment** (`TermsOfPayment`) - Payment terms code (e.g., Net30, COD)
- **Method of Payment** (`MethodOfPayment`) - Payment method code
- **Cash Discount Code** (`CashDiscountCode`) - Cash discount terms
- **Cash Discount Date** (`CashDiscountDate`) - Discount expiration date
- **Cash Discount** (`CashDiscount`) - Discount amount

#### **Financial Information:**
- **Exchange Rate** (`ExchangeRate`) - Currency exchange rate if applicable
- **Total Discount** (`TotalDiscount`) - Total line discount amount
- **Imported Amount** (`ImportedAmount`) - Total invoice amount from document
- **Imported Sales Tax** (`ImportedSalesTax`) - Total tax amount from document

#### **Tax Information:**
- **Sales Tax Group** (`SalesTaxGroup`) - Tax group applicable to header
- **Tax Exempt Number** (`TaxExemptNumber`) - Tax exemption reference if applicable
- **Prices Include Sales Tax** (`IsPricesIncludeSalesTax`) - Yes/No

#### **Delivery Information:**
- **Site** (`Site`) - Delivery site
- **Warehouse** (`Warehouse`) - Delivery warehouse
- **Delivery Name** (`DeliveryName`) - Delivery recipient name
- **Delivery State** (`DeliveryState`) - Delivery state/province

#### **Additional Fields:**
- **Comment** (`Comment`) - Any notes or comments
- **Bank Account** (`BankAccount`) - Vendor bank account reference
- **Payment Group Code** (`PaymentGroupCode`) - Payment grouping code
- **Posting Profile** (`PostingProfile`) - GL posting profile

---

## Step 2: Line Item Extraction

For **each line item** on the invoice, extract:

#### **Mandatory Line Fields:**
- **Header Reference** (`HeaderReference`) - Links to header (use same value as header)
- **Line Number** (`InvoiceLineNumber`) - Sequential line number (1, 2, 3, etc.)

#### **Item Identification:**
- **Item Number** (`ItemNumber`) - Product/item number
- **Item Name** (`ItemName`) - Item description
- **Line Description** (`LineDescription`) - Additional line description
- **Line Type** (`LineType`) - Item, Service, or Charge

#### **Procurement Category (for non-item lines):**
- **Procurement Category Name** (`ProcurementCategoryName`) - Category if not an item
- **Procurement Category Hierarchy** (`ProcurementCategoryHierarchyName`) - Category hierarchy

#### **Quantities and Units:**
- **Quantity** (`InventNow` or `ReceiveNow`) - Invoice quantity
- **Unit** (`Unit`) - Unit of measure (EA, PCS, KG, etc.)

#### **Pricing:**
- **Unit Price** (`UnitPrice`) - Price per unit
- **Price Unit** (`PriceUnit`) - Pricing unit quantity
- **Amount** (`Amount`) - Line total amount (quantity × unit price)
- **Net Amount** (`NetAmount`) - Net amount after discounts

#### **Discounts:**
- **Discount** (`Discount`) - Line discount amount
- **Discount Percent** (`DiscountPercent`) - Line discount percentage
- **Multiline Discount** (`MultilineDiscount`) - Multiline discount amount

#### **Tax:**
- **Sales Tax Group** (`SalesTaxGroup`) - Line-level tax group
- **Item Sales Tax** (`ItemSalesTax`) - Item tax group

#### **Product Dimensions (if applicable):**
- **Color** (`ProductColorId`) - Product color
- **Size** (`ProductSizeId`) - Product size
- **Style** (`ProductStyleId`) - Product style
- **Configuration** (`ProductConfigurationId`) - Product configuration

#### **Inventory Dimensions:**
- **Warehouse** (`InventoryWarehouseId`) - Storage warehouse
- **Site** (`InventorySiteId`) - Storage site
- **Batch Number** (`ItemBatchNumber`) - Batch/lot number
- **Inventory Status** (`OrderedInventoryStatusId`) - Inventory status

#### **Purchase Order Reference:**
- **Purchase Order** (`PurchaseOrder`) - PO number
- **Purchase Line Number** (`PurchLineNumber`) - PO line number

#### **Accounting:**
- **Main Account** (`MainAccountDisplayValue`) - GL account
- **Financial Dimensions** (`DimensionDisplayValue`) - Default dimensions

---

## Step 3: Data Validation

Before creating the invoice, validate:

1. **Vendor Exists**: Verify `InvoiceAccount` exists in the system
2. **Currency is Valid**: Confirm currency code is active
3. **Required Fields**: All mandatory fields are populated
4. **Line Totals**: Sum of line amounts matches header total (within tolerance)
5. **Tax Calculations**: Tax amounts are reasonable
6. **PO References**: If PO is referenced, verify it exists
7. **Items Exist**: Verify all item numbers exist in inventory
8. **Units Valid**: Unit of measure codes are valid
9. **Dates Logical**: Invoice date ≤ Posting date ≤ Due date

---

## Step 4: Create Vendor Invoice Header

Use the `d365fo_create_entity_record` tool:

```json
{
  "entity_name": "VendorInvoiceHeaders",
  "data": {
    "dataAreaId": "USMF",
    "InvoiceNumber": "<extracted_invoice_number>",
    "InvoiceAccount": "<extracted_vendor_account>",
    "Currency": "<extracted_currency>",
    "InvoiceDate": "<extracted_invoice_date>",
    "Date": "<posting_date>",
    "DueDate": "<due_date>",
    "VendorName": "<vendor_name>",
    "InvoiceDescription": "<description>",
    "PurchaseOrderNumber": "<po_number>",
    "TermsOfPayment": "<payment_terms>",
    "MethodOfPayment": "<payment_method>",
    "ImportedAmount": <total_amount>,
    "ImportedSalesTax": <tax_amount>,
    "SalesTaxGroup": "<tax_group>",
    "IsPricesIncludeSalesTax": "No",
    "Comment": "Created via AI invoice extraction"
  },
  "return_record": true
}
```

**Save the returned `HeaderReference`** - you'll need this for lines and attachments.

---

## Step 5: Create Vendor Invoice Lines

For each extracted line item, use the `d365fo_create_entity_record` tool:

```json
{
  "entity_name": "VendorInvoiceLines",
  "data": {
    "dataAreaId": "USMF",
    "HeaderReference": "<header_reference_from_step_4>",
    "InvoiceLineNumber": 1.0,
    "LineType": "Item",
    "ItemNumber": "<item_number>",
    "LineDescription": "<line_description>",
    "InventNow": <quantity>,
    "Unit": "<unit>",
    "UnitPrice": <unit_price>,
    "Amount": <line_total>,
    "NetAmount": <net_amount>,
    "DiscountPercent": <discount_percent>,
    "SalesTaxGroup": "<tax_group>",
    "ItemSalesTax": "<item_tax_group>",
    "InventoryWarehouseId": "<warehouse>",
    "InventorySiteId": "<site>",
    "PurchaseOrder": "<po_number>",
    "PurchLineNumber": <po_line_number>
  },
  "return_record": true
}
```

Repeat for each line, incrementing `InvoiceLineNumber`.

---

## Step 6: Attach Source Document

Attach the original PDF/image to the invoice header:

1. **Read the PDF/image file** and convert to base64
2. **Extract file information**: filename, file type
3. **Create attachment** using `d365fo_create_entity_record`:

```json
{
  "entity_name": "VendorInvoiceDocumentAttachments",
  "data": {
    "dataAreaId": "USMF",
    "HeaderReference": "<header_reference_from_step_4>",
    "TypeId": "File",
    "FileName": "<original_filename.pdf>",
    "Name": "Source Invoice Document",
    "FileContents": "<base64_encoded_file_content>",
    "FileType": "pdf",
    "Restriction": "None",
    "Notes": "Original vendor invoice automatically attached",
    "DefaultAttachment": "Yes"
  },
  "return_record": true
}
```

---

## Step 7: Summary and Verification

After creation, provide a summary:

### **Invoice Created Successfully**

**Header Details:**
- Invoice Number: [number]
- Vendor: [name] ([account])
- Total Amount: [currency] [amount]
- Invoice Date: [date]
- Due Date: [date]
- Header Reference: [reference]

**Line Items:** [count] lines created
- Line 1: [item] - [description] - [qty] [unit] @ [price] = [amount]
- Line 2: [item] - [description] - [qty] [unit] @ [price] = [amount]
- ...

**Document Attachment:** ✓ Source invoice attached

**Next Steps:**
1. Review invoice details in D365 F&O
2. Validate accounting distributions
3. Submit for approval workflow (if configured)
4. Post invoice when approved

---

## Error Handling

If any step fails:

1. **Document the error** with specific details
2. **Identify missing or invalid data**
3. **Suggest corrections** based on D365 F&O requirements
4. **Provide partial results** if some steps succeeded
5. **Recommend manual intervention** if needed

### Common Errors:
- **Vendor not found**: Verify vendor account exists and is active
- **Item not found**: Check item number format and existence
- **Currency invalid**: Ensure currency is active in the system
- **Duplicate invoice**: Check if invoice number already exists for vendor
- **Tax group invalid**: Verify tax group is configured
- **PO not found**: Verify purchase order exists and is open
- **Quantity exceeds PO**: Check remaining quantities on PO line

---

## Data Extraction Best Practices

### OCR Tips:
1. **Enhance image quality** if text is unclear
2. **Identify invoice structure**: header, line items table, totals
3. **Parse tables carefully**: align columns correctly
4. **Handle multi-page invoices**: combine all pages
5. **Validate extracted numbers**: check calculations

### Field Mapping Intelligence:
- Look for common labels: "Invoice #", "Invoice No", "Bill To", "Ship To"
- Parse dates in various formats: MM/DD/YYYY, DD-MMM-YYYY, YYYY/MM/DD
- Extract currency symbols: $, €, £, ¥
- Identify PO references: "PO#", "Purchase Order", "Order No"
- Calculate totals: subtotal + tax = total

### Line Item Parsing:
- Identify table structure: headers (Item, Description, Qty, Price, Total)
- Skip header rows and total rows
- Handle wrapped descriptions across multiple lines
- Parse quantities and prices correctly (watch for decimal separators)
- Calculate line totals and verify against parsed amounts

---

## Example Workflow

```
USER: Here's a vendor invoice PDF [attachment]

ASSISTANT:
1. Analyzing invoice document...
   ✓ Extracted invoice #INV-2024-1234
   ✓ Vendor: Contoso Ltd (V-001)
   ✓ Date: 2024-10-15
   ✓ Total: $1,250.00

2. Parsing line items...
   ✓ Found 3 line items
   - Item A1000: Widget (10 EA @ $50.00)
   - Item B2000: Gadget (5 EA @ $90.00)
   - Service: Installation (1 HR @ $200.00)

3. Creating vendor invoice header...
   ✓ Created header with reference: VEN-2024-001234

4. Creating invoice lines...
   ✓ Line 1 created
   ✓ Line 2 created
   ✓ Line 3 created

5. Attaching source document...
   ✓ PDF attached to invoice

✅ Invoice successfully created in D365 F&O!
```

---

## Profile Configuration

Use the default D365FO profile or specify:
- Profile: "default" (or specific profile name)
- Ensure profile has proper authentication
- Verify permissions for vendor invoice creation

---

## Notes

- Always **validate data** before creating records
- Use **try-catch** patterns for error handling
- Provide **clear feedback** on success or failure
- **Log important details** for audit trail
- Consider **duplicate detection** before creating
- Handle **multi-currency** invoices appropriately
- Respect **workflow** configurations if enabled
- Follow **company-specific** validation rules

---

## Advanced Scenarios

### Matching to Purchase Orders:
If PO number is found, retrieve PO lines and match invoice lines to PO lines for three-way matching.

### Charges and Fees:
Create charge lines using `LineType: "Charge"` with appropriate charge codes.

### Tax Overrides:
If manual tax amounts are provided, set `OverrideSalesTax: "Yes"` and specify amounts.

### Multi-Currency:
Ensure exchange rates are current and apply correctly to amounts.

### Project Invoices:
If invoice is project-related, populate project dimensions and references.

### Approval Workflow:
After creation, the invoice may enter approval workflow automatically based on company configuration.

---

## Testing Checklist

Before considering the task complete:

- [ ] Header created with valid HeaderReference
- [ ] All mandatory fields populated
- [ ] Line count matches extracted items
- [ ] Line totals sum correctly
- [ ] Tax calculations are reasonable
- [ ] Document attached successfully
- [ ] Can view invoice in D365 F&O UI
- [ ] No validation errors present
- [ ] Invoice ready for posting or approval

---

## End of Prompt
