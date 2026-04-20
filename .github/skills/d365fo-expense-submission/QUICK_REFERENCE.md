# D365 F&O Expense Submission - Quick Reference

## Core Entities

| Entity | Collection | Purpose |
|--------|-----------|---------|
| `ExpCopilotAutomationExpense` | `ExpCopilotAutomationExpenses` | Expense lines (individual transactions) |
| `ExpCopilotAutomationReport` | `ExpCopilotAutomationReports` | Expense reports (headers) |
| `ExpCopilotAttachedReceipt` | `ExpCopilotAttachedReceipts` | Receipt attachments |
| `ExpenseCopilotMasterData` | `ExpenseCopilotMasterData` | Master data & receipt upload |
| `ExpCopilotConfiguration` | `ExpCopilotConfigurations` | Copilot configuration |

## Quick Start Workflow

```
1. Upload Receipt (optional)
2. Create Expense Line
3. Attach Receipt to Expense
4. Create/Update Report
5. Submit Report
```

## Essential Code Snippets

### 1. Check Configuration
```python
config = query_entities(
    entity_name="ExpCopilotConfigurations",
    select=["EnableCopilotForExpense", "EnableCreditCardAutoMatch"],
    top=1
)
```

### 2. Upload Receipt
```python
call_action(
    action_name="uploadLargeImageWithWorkerIdByLegalEntityWithCashExpense",
    entity_name="ExpenseCopilotMasterData",
    key_fields=["dataAreaId"],
    key_values=["USSI"],
    parameters={
        "imageBase64": "<base64_string>",
        "FileExtension": "jpg",
        "FileName": "receipt.jpg",
        "ContentType": "image/jpeg",
        "workerId": "000001",
        "cashExpense": False
    }
)
```

### 3. Create Expense Line
```python
create_entity_record(
    entity_name="ExpCopilotAutomationExpenses",
    data={
        "dataAreaId": "USSI",
        "TransactionDate": "2026-04-18T00:00:00Z",
        "ExpenseCategory": "MEALS",
        "Description": "Client dinner",
        "Amount": 125.50,
        "CurrencyCode": "USD",
        "PayMethod": "CREDITCARD",  # REQUIRED
        "ReceiptRequired": "Yes"
    }
)
```

### 4. Attach Receipt
```python
create_entity_record(
    entity_name="ExpCopilotAttachedReceipts",
    data={
        "Name": "Receipt - Client Dinner",
        "RefRecId": 5637144576,  # Expense RecId
        "RefTableId": 7302,      # TrvExpTrans table
        "RefCompanyId": "USSI",
        "DocumentId": document_id,
        "ExpenseLineAttachedTo": exp_trans_number
    }
)
```

### 5. Itemize Expense
```python
call_action(
    action_name="itemizeExpenseQuickly",
    entity_name="ExpCopilotAutomationExpenses",
    key_fields=["dataAreaId", "ExpTransNumber"],
    key_values=["USSI", "EXP-001"],
    parameters={
        "itemizations": json.dumps([
            {"description": "Main", "amount": 100, "category": "MEALS"},
            {"description": "Tax", "amount": 8, "category": "TAX"}
        ])
    }
)
```

### 6. Create Report
```python
create_entity_record(
    entity_name="ExpCopilotAutomationReports",
    data={
        "LegalEntity_DataArea": "USSI",
        "TrvHcmWorker_PersonnelNumber": "000001",
        "Txt1": "April 2026 Expenses",
        "Txt2": "Project-related expenses",
        "InterCompanyLE": "USSI"  # REQUIRED
    }
)
```

### 7. Submit Report
```python
update_entity_record(
    entity_name="ExpCopilotAutomationReports",
    key_fields=["LegalEntity_DataArea", "ExpNumber"],
    key_values=["USSI", "RPT-001"],
    data={
        "WorkflowAction": "Submit",
        "ApprovalStatus": "Submitted"
    }
)
```

## Required Fields

### Expense Line (ExpCopilotAutomationExpense)
- ✅ `PayMethod` - Payment method (MANDATORY)
- ✅ `TransactionDate` - Transaction date
- ✅ `Amount` - Expense amount
- ✅ `CurrencyCode` - Currency code

### Expense Report (ExpCopilotAutomationReport)
- ✅ `InterCompanyLE` - Legal entity (MANDATORY)
- ✅ `TrvHcmWorker_PersonnelNumber` - Employee

## Common Expense Categories

| Code | Description |
|------|-------------|
| `MEALS` | Meals & entertainment |
| `HOTEL` | Hotel accommodation |
| `AIRFARE` | Air travel |
| `TAXI` | Taxi/rideshare |
| `PARKING` | Parking fees |
| `MILEAGE` | Mileage reimbursement |
| `PERDIEM` | Per diem allowance |
| `PHONE` | Phone/communications |
| `OFFICE` | Office supplies |

## Payment Methods

| Code | Description |
|------|-------------|
| `CASH` | Cash payment |
| `CREDITCARD` | Corporate credit card |
| `COMPANY` | Company direct payment |
| `PERSONAL` | Personal credit card |

## Approval Status Values

| Status | Description |
|--------|-------------|
| `Draft` | Not submitted |
| `Submitted` | Pending approval |
| `Approved` | Approved |
| `Rejected` | Rejected |
| `Posted` | Posted to ledger |
| `Paid` | Payment completed |

## Querying Examples

### Get All Expenses for Report
```python
query_entities(
    entity_name="ExpCopilotAutomationExpenses",
    filter="ExpNumber eq 'RPT-001'",
    select=["ExpTransNumber", "Amount", "Description"]
)
```

### Get Pending Reports
```python
query_entities(
    entity_name="ExpCopilotAutomationReports",
    filter="ApprovalStatus eq Microsoft.Dynamics.DataEntities.TrvAppStatus'Submitted'",
    order_by=["DocumentCreatedDateTime desc"]
)
```

### Get Expenses by Category
```python
query_entities(
    entity_name="ExpCopilotAutomationExpenses",
    filter="ExpenseCategory eq 'MEALS'",
    top=50
)
```

## Common Scenarios

### Cash Expense (No Receipt)
```python
{
    "ExpenseCategory": "PARKING",
    "Amount": 20.00,
    "PayMethod": "CASH",
    "ReceiptRequired": "No"
}
```

### Credit Card with Auto-Match
```python
{
    "ExpenseCategory": "HOTEL",
    "Amount": 299.00,
    "PayMethod": "CREDITCARD",
    "CreditCardId": "CC-1001",
    "CreditCardTransactionCurrencyAmount": 299.00
}
```

### Project Expense
```python
{
    "ExpenseCategory": "MEALS",
    "Amount": 425.75,
    "PayMethod": "CREDITCARD",
    "ProjId": "PROJ-001",
    "ProjStatusId": "BILLABLE"
}
```

### Per Diem
```python
{
    "ExpenseCategory": "PERDIEM",
    "Amount": 180.00,
    "PayMethod": "COMPANY",
    "PerDiemMealAllowance": 180.00,
    "NumOfDays": 3
}
```

### Mileage
```python
{
    "ExpenseCategory": "MILEAGE",
    "Amount": 104.86,
    "PayMethod": "COMPANY",
    "MileageQty": 156.5,
    "MileageRate": 0.67
}
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| "PayMethod is required" | Add `PayMethod` field (mandatory) |
| "Category not found" | Use valid expense category code |
| "Receipt attachment failed" | Check `RefRecId` and `RefTableId` |
| "Cannot modify approved" | Only draft expenses can be edited |
| "Auto-match not working" | Enable in `ExpCopilotConfiguration` |

## Best Practices

1. ✅ Upload receipts BEFORE creating expenses
2. ✅ Use descriptive filenames for receipts
3. ✅ Validate amounts and dates before submission
4. ✅ Link to projects when applicable
5. ✅ Include merchant and location info
6. ✅ Check policy violations before submission
7. ✅ Use itemization for detailed tracking
8. ✅ Handle errors gracefully with try/catch

## Key Field References

### Table IDs
- `7302` - TrvExpTrans (Expense transactions)

### Receipt File Extensions
- `jpg`, `jpeg`, `png` - Images
- `pdf` - PDF documents

### Cost Owner
- `Employee` - Reimbursable to employee
- `Company` - Non-reimbursable (company paid)

---

**Quick Links:**
- [Full Skill Guide](./SKILL.md)
- [Example Script](./expense_submission_example.py)
- [Skills README](../README.md)
