# D365 F&O Expense Submission Skill

Complete guide and examples for submitting expenses in Microsoft Dynamics 365 Finance & Operations.

## 📁 Contents

### 📘 [SKILL.md](./SKILL.md) - Comprehensive Guide
Complete skill documentation covering:
- **Overview** - What this skill covers and when to use it
- **Key Entities** - All expense-related entities and their purposes
- **Workflow** - Step-by-step expense submission process
- **Implementation Guide** - Detailed code examples for each step
- **Common Scenarios** - Real-world use cases:
  - Simple cash expenses
  - Credit card expenses with receipts
  - Project expenses with guest attendees
  - Per diem allowances
  - Mileage reimbursement
  - Itemized hotel bills
- **Best Practices** - Recommendations for production use
- **Troubleshooting** - Common issues and solutions
- **Testing Checklist** - What to test before deployment

### ⚡ [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - Cheat Sheet
Quick reference card with:
- Essential code snippets
- Required fields reference
- Common expense categories
- Payment methods and status values
- Query examples
- Scenario templates
- Troubleshooting table

### 💻 [expense_submission_example.py](./expense_submission_example.py) - Working Examples
Python script with 5 complete examples:
1. **Simple Cash Expense** - No receipt required
2. **Credit Card with Receipt** - Upload and attach receipt
3. **Itemized Hotel Expense** - Split into multiple line items
4. **Complete Workflow** - Multiple expenses → report → submission
5. **Per Diem & Mileage** - Specialized expense types

## 🚀 Quick Start

### 1. Read the Quick Reference
Start with [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) for essential code snippets and field references.

### 2. Review Common Scenarios
Check the [SKILL.md Common Scenarios section](./SKILL.md#common-scenarios) for patterns matching your use case.

### 3. Run Examples
Execute the example script to see working implementations:
```bash
python expense_submission_example.py
```

### 4. Implement Your Solution
Use the comprehensive guide in [SKILL.md](./SKILL.md) for detailed implementation guidance.

## 📊 Expense Submission Overview

### Core Workflow
```
Upload Receipt → Create Expense Line → Attach Receipt → 
Create Report → Submit to Workflow → Approval → Payment
```

### Key Entities

| Entity | Purpose |
|--------|---------|
| `ExpCopilotAutomationExpense` | Individual expense lines |
| `ExpCopilotAutomationReport` | Expense report headers |
| `ExpCopilotAttachedReceipt` | Receipt attachments |
| `ExpenseCopilotMasterData` | Master data & uploads |
| `ExpCopilotConfiguration` | Copilot settings |

## 💡 When to Use This Skill

Use this skill when you need to:
- ✅ Create expense reports programmatically
- ✅ Integrate expense submission with external systems
- ✅ Automate receipt processing and matching
- ✅ Build mobile or web apps for expense entry
- ✅ Implement custom expense workflows
- ✅ Process credit card feeds automatically
- ✅ Generate expense reports from email receipts
- ✅ Implement AI-powered expense categorization

## 🎯 Common Use Cases

### 1. Email-to-Expense Integration
Parse email receipts → Extract data with AI → Upload receipt → Create expense → Auto-match

### 2. Mobile Expense App
Capture photo → Upload → OCR processing → Pre-fill form → Submit

### 3. Credit Card Feed Processing
Import transactions → Match to receipts → Create expenses → Auto-report

### 4. Bulk Expense Import
CSV import → Validate data → Create expenses → Generate reports

### 5. Workflow Automation
Policy checking → Auto-approval (small amounts) → Notification → Payment

## 📋 Checklist for Implementation

Before implementing expense submission:

**Configuration**
- [ ] Expense Copilot enabled in D365FO
- [ ] Expense categories configured
- [ ] Payment methods set up
- [ ] Workflow configured
- [ ] Expense policies defined

**Development**
- [ ] Authentication configured (Azure AD)
- [ ] MCP server connected
- [ ] Test environment available
- [ ] Error handling implemented
- [ ] Logging configured

**Testing**
- [ ] Test all expense categories
- [ ] Test all payment methods
- [ ] Test receipt upload/attachment
- [ ] Test itemization
- [ ] Test workflow submission
- [ ] Test policy violations
- [ ] Test error scenarios

**Deployment**
- [ ] Production credentials secured
- [ ] Performance tested
- [ ] Documentation complete
- [ ] User training completed
- [ ] Support procedures in place

## 🔧 Technical Requirements

### Prerequisites
- D365 Finance & Operations environment
- D365FO MCP Server configured
- Azure AD authentication
- Appropriate permissions for expense operations

### Supported Operations
- ✅ Create expense lines
- ✅ Upload receipts
- ✅ Attach receipts to expenses
- ✅ Itemize expenses
- ✅ Create expense reports
- ✅ Submit to workflow
- ✅ Query expense data
- ✅ Update draft expenses

### Limitations
- ❌ Cannot modify approved/posted expenses
- ❌ Cannot delete submitted reports
- ❌ OData filtering has limited support
- ❌ Some fields read-only after submission

## 📚 Additional Resources

### In This Skill
- [Complete Skill Guide](./SKILL.md) - Full documentation
- [Quick Reference](./QUICK_REFERENCE.md) - Cheat sheet
- [Example Script](./expense_submission_example.py) - Working code

### D365FO Documentation
- Expense Management module documentation
- OData API reference
- Workflow configuration guide
- Expense policy setup

### Related Skills
- *Invoice Processing* (coming soon)
- *Purchase Order Creation* (coming soon)
- *Project Management* (coming soon)

## 🤝 Contributing

To improve this skill:
1. Test the examples in your environment
2. Report issues or suggest improvements
3. Share additional scenarios or use cases
4. Contribute code examples

## 📝 Version History

- **v1.0** (April 2026) - Initial release
  - Complete expense submission workflow
  - 5 working examples
  - Quick reference guide
  - Comprehensive documentation

## 💬 Support

For issues or questions:
1. Check [SKILL.md Troubleshooting section](./SKILL.md#troubleshooting)
2. Review [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)
3. Run the example script to validate setup
4. Review D365FO logs for detailed errors

---

**Ready to submit expenses?** Start with [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) or jump into the [complete guide](./SKILL.md)!
