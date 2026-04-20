# D365 Finance & Operations - Expense Submission Skill

## Overview
This skill provides comprehensive guidance for submitting expenses in Microsoft Dynamics 365 Finance & Operations using the Expense Copilot entities and OData actions. Use this skill when working with expense reports, expense lines, receipts, and automated expense processing workflows.

## When to Use This Skill
- Creating new expense reports and expense lines
- Uploading and attaching receipts to expenses
- Submitting expense reports through workflow
- Implementing automated expense processing with Copilot
- Itemizing expenses (splitting into multiple lines)
- Matching credit card transactions to receipts
- Querying expense data for reporting or integration

## Key Entities

### Core Expense Entities

1. **ExpCopilotAutomationExpense** (`ExpCopilotAutomationExpenses`)
   - Purpose: Manage individual expense lines with AI/Copilot support
   - Category: Transaction
   - Key Fields: `ExpTransNumber`, `dataAreaId`
   - Editable: Yes

2. **ExpCopilotAutomationReport** (`ExpCopilotAutomationReports`)
   - Purpose: Manage expense reports (headers)
   - Category: Transaction
   - Key Fields: `ExpNumber`, `LegalEntity_DataArea`
   - Editable: Yes

3. **ExpCopilotAttachedReceipt** (`ExpCopilotAttachedReceipts`)
   - Purpose: Manage receipts attached to expense lines
   - Category: Master
   - Key Fields: `EntRecId`
   - Editable: Yes

4. **ExpenseCopilotMasterData** (`ExpenseCopilotMasterData`)
   - Purpose: Upload receipts and access master data
   - Category: Transaction
   - Editable: Yes

5. **ExpCopilotConfiguration** (`ExpCopilotConfigurations`)
   - Purpose: Configure Expense Agent/Copilot behavior
   - Category: Configuration
   - Key Fields: `dataAreaId`

## Expense Submission Workflow

### Standard Workflow Steps

```
1. Configure Expense Copilot (one-time setup)
   ↓
2. Upload Receipt (optional)
   ↓
3. Create Expense Line(s)
   ↓
4. Attach Receipt to Expense Line
   ↓
5. Create/Update Expense Report
   ↓
6. Submit Expense Report (Workflow)
   ↓
7. Approval Process
   ↓
8. Posting & Payment
```

## Step-by-Step Implementation

### Step 1: Check Expense Copilot Configuration

Query the current configuration to understand enabled features:

```python
# Query Expense Copilot Configuration
config = mcp_d365fo-mcp-se_d365fo_query_entities(
    entity_name="ExpCopilotConfigurations",
    select=["EnableCopilotForExpense", "EnableCreditCardAutoMatch", 
            "EnableItemization", "ReportGroupBy", "MaxDaysForMatch"],
    top=1
)
```

**Key Configuration Fields to Check:**
- `EnableCopilotForExpense`: Is Expense Agent enabled?
- `EnableCreditCardAutoMatch`: Auto-match receipts to credit card transactions?
- `EnableItemization`: Can expenses be itemized?
- `SkipReportCreation`: Are reports auto-created?
- `MaxDaysForMatch`: Maximum days for receipt matching

### Step 2: Upload Receipt (Optional but Recommended)

Upload a receipt image before creating the expense line:

```python
# Upload receipt using the master data entity action
result = mcp_d365fo-mcp-se_d365fo_call_action(
    action_name="uploadLargeImageWithWorkerIdByLegalEntityWithCashExpense",
    entity_name="ExpenseCopilotMasterData",
    key_fields=["dataAreaId"],
    key_values=["USSI"],  # Your company ID
    parameters={
        "imageBase64": "<base64_encoded_image>",
        "FileExtension": "jpg",
        "FileName": "receipt_2026-04-18.jpg",
        "ContentType": "image/jpeg",
        "workerId": "000001",  # Personnel number
        "Notes": "Dinner with client",
        "_sourceCompany": "USSI",
        "cashExpense": False  # True for cash, False for credit card
    }
)

# The action returns a document ID that can be used to attach to expense
document_id = result['documentId']
```

**Receipt Upload Best Practices:**
- Use JPG/PNG formats for images
- Use PDF for scanned receipts
- Keep file sizes under 5MB for best performance
- Include descriptive notes for easier matching

### Step 3: Create Expense Line

Create the expense transaction:

```python
# Create an expense line
expense_data = {
    "dataAreaId": "USSI",
    # ExpTransNumber is auto-generated, don't provide it
    "TransactionDate": "2026-04-18T00:00:00Z",
    "ExpenseCategory": "MEALS",  # Must exist in system
    "Description": "Client dinner - Project discussion",
    "Amount": 125.50,
    "CurrencyCode": "USD",
    "PayMethod": "CREDITCARD",  # Mandatory field
    "ReceiptRequired": "Yes",
    "CostOwner": "Employee",  # Employee or Company
    "TaxAmount": 10.04,
    "TaxGroup": "CA",
    "Merchant": "The Steakhouse",
    "AddressCity": "Los Angeles",
    "AddressState": "CA",
    "AddressZipCode": 90001,
    "ProjId": "PROJ-2026-001",  # Optional: Link to project
    "ApprovalStatus": "Draft"  # Start as draft
}

expense_line = mcp_d365fo-mcp-se_d365fo_create_entity_record(
    entity_name="ExpCopilotAutomationExpenses",
    data=expense_data,
    return_record=True
)

# Capture the expense transaction number
exp_trans_number = expense_line['ExpTransNumber']
```

**Required Fields:**
- `PayMethod` - Payment method (mandatory)
- `TransactionDate` - Date of expense
- `Amount` - Expense amount
- `CurrencyCode` - Currency code

**Important Optional Fields:**
- `ExpenseCategory` - Category code (e.g., MEALS, TRAVEL, HOTEL)
- `ProjId` - Project ID for project-related expenses
- `ReceiptRequired` - Whether receipt is required
- `TaxAmount`, `TaxGroup` - Tax information
- `Merchant` - Merchant/vendor name
- Location fields: `AddressCity`, `AddressState`, `AddressZipCode`, `AddressCountry`

### Step 4: Attach Receipt to Expense Line

Link the uploaded receipt to the expense line:

```python
# Query to get the reference IDs needed
expense_record = mcp_d365fo-mcp-se_d365fo_get_entity_record(
    entity_name="ExpCopilotAutomationExpenses",
    key_fields=["dataAreaId", "ExpTransNumber"],
    key_values=["USSI", exp_trans_number]
)

# Create receipt attachment
receipt_attachment = {
    "Name": "Receipt - Client Dinner",
    "RefRecId": expense_record['RecId'],  # Record ID of expense line
    "RefTableId": 7302,  # Table ID for TrvExpTrans (expense transactions)
    "RefCompanyId": "USSI",
    "DocumentId": document_id,  # From upload step
    "FileExtension": "jpg",
    "Notes": "Itemized receipt showing all attendees",
    "IsCashExpense": "No",
    "DefaultAttachment": "Yes",
    "ExpenseLineAttachedTo": exp_trans_number
}

receipt = mcp_d365fo-mcp-se_d365fo_create_entity_record(
    entity_name="ExpCopilotAttachedReceipts",
    data=receipt_attachment,
    return_record=True
)
```

### Step 5: Itemize Expense (Optional)

Split an expense into multiple line items using the itemization action:

```python
# Quick itemization - split expense into multiple items
itemization_data = {
    "itemizations": json.dumps([
        {
            "description": "Main course",
            "amount": 85.00,
            "category": "MEALS",
            "quantity": 2
        },
        {
            "description": "Beverages",
            "amount": 30.50,
            "category": "MEALS",
            "quantity": 4
        },
        {
            "description": "Tax",
            "amount": 10.04,
            "category": "TAX",
            "quantity": 1
        }
    ])
}

result = mcp_d365fo-mcp-se_d365fo_call_action(
    action_name="itemizeExpenseQuickly",
    entity_name="ExpCopilotAutomationExpenses",
    key_fields=["dataAreaId", "ExpTransNumber"],
    key_values=["USSI", exp_trans_number],
    parameters=itemization_data
)
```

**Itemization Use Cases:**
- Restaurant bills with multiple items
- Hotel bills showing room, tax, fees separately
- Conference expenses with registration, meals, materials
- Travel with multiple segments

### Step 6: Create or Update Expense Report

Option A: Auto-create report (if Copilot is configured):
```python
# Check if report should be triggered
should_trigger = mcp_d365fo-mcp-se_d365fo_call_action(
    action_name="shouldTriggerReport",
    entity_name="ExpCopilotConfigurations",
    key_fields=["dataAreaId"],
    key_values=["USSI"],
    parameters={
        "_workerId": 22565421394,  # Worker RecId
        "_forceTrigger": True
    }
)
```

Option B: Manually create expense report:
```python
# Create expense report header
report_data = {
    "LegalEntity_DataArea": "USSI",
    # ExpNumber is auto-generated
    "TrvHcmWorker_PersonnelNumber": "000001",
    "Txt1": "April 2026 Business Expenses",
    "Txt2": "Project-related meals and travel",
    "Destination": "Los Angeles, CA",
    "InterCompanyLE": "USSI",  # Mandatory
    "PaymentDate": "2026-04-30T00:00:00Z",
    "ProjId": "PROJ-2026-001",  # Optional
    "ApprovalStatus": "Draft"
}

expense_report = mcp_d365fo-mcp-se_d365fo_create_entity_record(
    entity_name="ExpCopilotAutomationReports",
    data=report_data,
    return_record=True
)

report_number = expense_report['ExpNumber']
```

### Step 7: Link Expense Lines to Report

Update expense lines to associate them with the report:

```python
# Update expense line with report number
update_data = {
    "ExpNumber": report_number
}

mcp_d365fo-mcp-se_d365fo_update_entity_record(
    entity_name="ExpCopilotAutomationExpenses",
    key_fields=["dataAreaId", "ExpTransNumber"],
    key_values=["USSI", exp_trans_number],
    data=update_data
)
```

### Step 8: Submit Expense Report to Workflow

```python
# Submit report by updating approval status
submit_data = {
    "WorkflowAction": "Submit",
    "ApprovalStatus": "Submitted"
}

mcp_d365fo-mcp-se_d365fo_update_entity_record(
    entity_name="ExpCopilotAutomationReports",
    key_fields=["LegalEntity_DataArea", "ExpNumber"],
    key_values=["USSI", report_number],
    data=submit_data
)
```

## Common Scenarios

### Scenario 1: Simple Cash Expense (No Receipt)

```python
# Create a simple cash expense without receipt
cash_expense = {
    "dataAreaId": "USSI",
    "TransactionDate": "2026-04-18T00:00:00Z",
    "ExpenseCategory": "PARKING",
    "Description": "Airport parking - 2 days",
    "Amount": 48.00,
    "CurrencyCode": "USD",
    "PayMethod": "CASH",
    "ReceiptRequired": "No",  # No receipt for small amounts
    "CostOwner": "Employee"
}

result = mcp_d365fo-mcp-se_d365fo_create_entity_record(
    entity_name="ExpCopilotAutomationExpenses",
    data=cash_expense,
    return_record=True
)
```

### Scenario 2: Credit Card Expense with Auto-Match

```python
# Create expense that will auto-match to credit card transaction
cc_expense = {
    "dataAreaId": "USSI",
    "TransactionDate": "2026-04-15T00:00:00Z",
    "ExpenseCategory": "HOTEL",
    "Description": "Hotel stay - Business trip",
    "Amount": 299.00,
    "CurrencyCode": "USD",
    "PayMethod": "CREDITCARD",
    "CreditCardId": "CC-1001",  # Reference to credit card
    "CreditCardTransactionCurrencyAmount": 299.00,
    "CreditCardTransactionCurrency": "USD",
    "ReceiptRequired": "Yes",
    "Merchant": "Hilton Hotel",
    "AddressCity": "San Francisco",
    "AddressState": "CA"
}

# System will auto-match if enabled in configuration
result = mcp_d365fo-mcp-se_d365fo_create_entity_record(
    entity_name="ExpCopilotAutomationExpenses",
    data=cc_expense,
    return_record=True
)
```

### Scenario 3: Project Expense with Guest Attendees

```python
# Create expense for client entertainment
entertainment_expense = {
    "dataAreaId": "USSI",
    "TransactionDate": "2026-04-18T00:00:00Z",
    "ExpenseCategory": "MEALS",
    "Description": "Client dinner - Project kickoff",
    "Amount": 425.75,
    "CurrencyCode": "USD",
    "PayMethod": "CREDITCARD",
    "ProjId": "PROJ-2026-001",
    "ProjStatusId": "BILLABLE",  # Mark as billable to client
    "CostOwner": "Company",
    "NumOfGuests": 4,
    "ReceiptRequired": "Yes",
    "Merchant": "The Capital Grille",
    "TaxAmount": 34.06,
    "TaxGroup": "CA"
}

result = mcp_d365fo-mcp-se_d365fo_create_entity_record(
    entity_name="ExpCopilotAutomationExpenses",
    data=entertainment_expense,
    return_record=True
)
```

### Scenario 4: Per Diem Expense

```python
# Create per diem expense with daily allowances
per_diem_expense = {
    "dataAreaId": "USSI",
    "TransactionDate": "2026-04-18T00:00:00Z",
    "ExpenseCategory": "PERDIEM",
    "Description": "Per diem - Business trip (3 days)",
    "CurrencyCode": "USD",
    "PayMethod": "COMPANY",
    "Location": "New York, NY",
    "PerDiemMealAllowance": 180.00,  # 3 days x $60/day
    "PerDiemHotelAllowance": 0.00,   # Hotel paid separately
    "NumOfDays": 3,
    "ReceiptRequired": "No",
    "Amount": 180.00
}

result = mcp_d365fo-mcp-se_d365fo_create_entity_record(
    entity_name="ExpCopilotAutomationExpenses",
    data=per_diem_expense,
    return_record=True
)
```

### Scenario 5: Mileage Reimbursement

```python
# Create mileage expense
mileage_expense = {
    "dataAreaId": "USSI",
    "TransactionDate": "2026-04-18T00:00:00Z",
    "ExpenseCategory": "MILEAGE",
    "Description": "Client site visit - Round trip",
    "CurrencyCode": "USD",
    "PayMethod": "COMPANY",
    "MileageQty": 156.5,  # Miles driven
    "MileageRate": 0.67,  # IRS standard mileage rate
    "Amount": 104.86,     # 156.5 * 0.67
    "VehicleType": "Personal",
    "Origin": "Office - Los Angeles",
    "Destination": "Client Site - San Diego",
    "ReceiptRequired": "No"
}

result = mcp_d365fo-mcp-se_d365fo_create_entity_record(
    entity_name="ExpCopilotAutomationExpenses",
    data=mileage_expense,
    return_record=True
)
```

## Querying Expense Data

### Query All Expenses for a Report

```python
expenses = mcp_d365fo-mcp-se_d365fo_query_entities(
    entity_name="ExpCopilotAutomationExpenses",
    filter="ExpNumber eq 'EXP-2026-001'",
    select=["ExpTransNumber", "TransactionDate", "ExpenseCategory", 
            "Description", "Amount", "ApprovalStatus"],
    order_by=["TransactionDate desc"]
)
```

### Query Pending Expense Reports

```python
pending_reports = mcp_d365fo-mcp-se_d365fo_query_entities(
    entity_name="ExpCopilotAutomationReports",
    filter="ApprovalStatus eq Microsoft.Dynamics.DataEntities.TrvAppStatus'Submitted'",
    select=["ExpNumber", "TrvHcmWorker_PersonnelNumber", "AmountTotal", 
            "Txt1", "DocumentCreatedDateTime"],
    order_by=["DocumentCreatedDateTime desc"],
    top=50
)
```

### Query Expenses by Date Range

```python
# Note: OData filtering is limited, so retrieve and filter
all_expenses = mcp_d365fo-mcp-se_d365fo_query_entities(
    entity_name="ExpCopilotAutomationExpenses",
    select=["ExpTransNumber", "TransactionDate", "Amount", "ExpenseCategory"],
    top=1000
)

# Filter in code for date range
from datetime import datetime
start_date = datetime(2026, 4, 1)
end_date = datetime(2026, 4, 30)

april_expenses = [
    exp for exp in all_expenses['data']
    if start_date <= datetime.fromisoformat(exp['TransactionDate'].replace('Z', '')) <= end_date
]
```

## Best Practices

### 1. Data Validation
- **Always validate**: Expense category, payment method, and company before creating
- **Check required fields**: Use entity schema to identify mandatory fields
- **Validate amounts**: Ensure amounts are positive and within policy limits
- **Date validation**: Transaction date should not be in the future

### 2. Receipt Management
- **Upload before creating expense**: Makes auto-matching more reliable
- **Use descriptive names**: Include date and merchant in filename
- **Standard formats**: Prefer JPG/PDF formats
- **Size limits**: Keep under 5MB for performance

### 3. Error Handling
```python
try:
    expense = mcp_d365fo-mcp-se_d365fo_create_entity_record(
        entity_name="ExpCopilotAutomationExpenses",
        data=expense_data,
        return_record=True
    )
except Exception as e:
    if "ExpenseCategory" in str(e):
        print("Invalid expense category - check setup")
    elif "PayMethod" in str(e):
        print("Payment method is required")
    elif "Policy" in str(e):
        print("Policy violation detected")
    else:
        print(f"Error creating expense: {e}")
```

### 4. Workflow Integration
- **Check status before updating**: Don't modify approved expenses
- **Use proper actions**: Use workflow actions (Submit, Approve, Reject)
- **Handle rejections**: Capture rejection comments and allow resubmission

### 5. Performance Optimization
- **Batch operations**: Create multiple expenses in sequence
- **Use select**: Only retrieve fields you need
- **Pagination**: Use `top` and `skip` for large datasets
- **Caching**: Cache configuration and master data lookups

## Policy Violations

Handle policy violations gracefully:

```python
# Check for policy violations after creating expense
expense = mcp_d365fo-mcp-se_d365fo_get_entity_record(
    entity_name="ExpCopilotAutomationExpenses",
    key_fields=["dataAreaId", "ExpTransNumber"],
    key_values=["USSI", exp_trans_number],
    select=["PolicyViolation", "PolicyMessage", "ReceiptRequired", "ReceiptAttached"]
)

if expense.get('PolicyViolation'):
    print(f"Policy violation: {expense['PolicyMessage']}")
    # Request justification or attach missing receipt
    
if expense.get('ReceiptRequired') == 'Yes' and not expense.get('ReceiptAttached'):
    print("Warning: Receipt required but not attached")
```

## Integration Patterns

### Pattern 1: Email Receipt Processing
```
Email with receipt → Parse email → Extract attachment → 
Upload to D365FO → OCR/AI processing → Create expense → 
Auto-match to credit card → Notify user
```

### Pattern 2: Mobile App Integration
```
Capture photo → Upload receipt → Fill expense form → 
Create expense with attachment → Submit report → 
Push notification on approval
```

### Pattern 3: Credit Card Feed Integration
```
Import CC transactions → Create draft expenses → 
AI match to receipts → User review/approve → 
Auto-create reports → Submit workflow
```

## Testing Checklist

Before deploying expense submission code:

- [ ] Test with all expense categories used in organization
- [ ] Test with different payment methods (Cash, Credit Card, Company)
- [ ] Test receipt upload and attachment
- [ ] Test itemization with multiple line items
- [ ] Test project-related expenses
- [ ] Test per diem calculations
- [ ] Test mileage calculations
- [ ] Test policy violation handling
- [ ] Test workflow submission and approval
- [ ] Test error scenarios (invalid category, missing required fields)
- [ ] Test with multiple legal entities/companies
- [ ] Test multi-currency scenarios
- [ ] Test expense report creation and linking

## Troubleshooting

### Common Issues

**Issue**: "PayMethod is required"
- **Solution**: Always include `PayMethod` field - it's mandatory

**Issue**: "Expense category not found"
- **Solution**: Query available categories first or use valid category codes

**Issue**: "Receipt attachment failed"
- **Solution**: Verify `RefRecId` and `RefTableId` are correct; ensure expense exists

**Issue**: "Cannot modify approved expense"
- **Solution**: Check `ApprovalStatus` before updates; only draft expenses can be modified

**Issue**: "Auto-match not working"
- **Solution**: Check `ExpCopilotConfiguration` - ensure `EnableCreditCardAutoMatch` is enabled

**Issue**: "Itemization failed"
- **Solution**: Ensure total of itemized amounts equals original expense amount

## Reference: Key Field Values

### Expense Categories (Examples)
- `MEALS` - Meals and entertainment
- `HOTEL` - Hotel accommodation
- `AIRFARE` - Air travel
- `TAXI` - Taxi/rideshare
- `PARKING` - Parking fees
- `MILEAGE` - Mileage reimbursement
- `PERDIEM` - Per diem allowance
- `PHONE` - Phone/communications
- `OFFICE` - Office supplies
- `OTHER` - Other expenses

### Payment Methods (Examples)
- `CASH` - Cash payment
- `CREDITCARD` - Corporate credit card
- `COMPANY` - Company direct payment
- `PERSONAL` - Personal credit card (employee paid)

### Approval Status Values
- `Draft` - Not submitted
- `Submitted` - Submitted for approval
- `Approved` - Approved
- `Rejected` - Rejected
- `Posted` - Posted to ledger
- `Paid` - Payment completed

### Cost Owner Values
- `Employee` - Employee expense (reimbursable)
- `Company` - Company expense (non-reimbursable)

## Additional Resources

- D365FO Expense Management documentation
- OData API reference for expense entities
- Workflow configuration guide
- Expense policy setup guide
- Mobile expense app integration guide

## Notes

- All date/time fields use ISO 8601 format with UTC timezone
- Amounts should be positive decimal values
- Currency codes must be valid ISO 4217 codes (USD, EUR, GBP, etc.)
- The Expense Copilot features require proper licensing and configuration
- Some fields may be read-only depending on expense status
- Custom fields may be available depending on organization's configuration

---

**Last Updated**: April 2026  
**Version**: 1.0  
**Tested with**: D365 F&O Version 10.0.40+
