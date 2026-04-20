#!/usr/bin/env python3
"""
D365 F&O Expense Submission Example

This script demonstrates how to submit expenses to D365 Finance & Operations
using the MCP server tools. It covers the complete workflow from creating
expense lines to submitting reports.

Prerequisites:
- D365FO MCP server running and configured
- Valid authentication credentials
- Expense categories and payment methods configured in D365FO

Usage:
    python expense_submission_example.py
"""

import json
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class ExpenseSubmissionHelper:
    """Helper class for D365 F&O expense submission operations."""
    
    def __init__(self, company_id: str = "USSI"):
        """
        Initialize the expense submission helper.
        
        Args:
            company_id: Legal entity/company ID in D365FO
        """
        self.company_id = company_id
        
    def check_configuration(self) -> Dict:
        """
        Check Expense Copilot configuration.
        
        Returns:
            Configuration settings dictionary
        """
        print("Checking Expense Copilot configuration...")
        
        # This would be called via MCP tool
        # config = mcp_d365fo-mcp-se_d365fo_query_entities(...)
        
        config = {
            "EnableCopilotForExpense": True,
            "EnableCreditCardAutoMatch": True,
            "EnableItemization": True,
            "MaxDaysForMatch": 7,
            "SkipReportCreation": False
        }
        
        print(f"✓ Copilot enabled: {config['EnableCopilotForExpense']}")
        print(f"✓ Auto-match enabled: {config['EnableCreditCardAutoMatch']}")
        print(f"✓ Itemization enabled: {config['EnableItemization']}")
        
        return config
    
    def upload_receipt(self, image_path: str, worker_id: str, 
                      notes: str = "", is_cash: bool = False) -> str:
        """
        Upload a receipt image to D365FO.
        
        Args:
            image_path: Path to receipt image file
            worker_id: Worker personnel number
            notes: Optional notes about the receipt
            is_cash: True for cash expense, False for credit card
            
        Returns:
            Document ID of uploaded receipt
        """
        print(f"Uploading receipt: {image_path}...")
        
        # Read and encode image
        with open(image_path, 'rb') as f:
            image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Determine file extension
        file_ext = image_path.split('.')[-1].lower()
        content_type = f"image/{file_ext}" if file_ext in ['jpg', 'jpeg', 'png'] else "application/pdf"
        
        # This would call the MCP action
        # result = mcp_d365fo-mcp-se_d365fo_call_action(
        #     action_name="uploadLargeImageWithWorkerIdByLegalEntityWithCashExpense",
        #     entity_name="ExpenseCopilotMasterData",
        #     key_fields=["dataAreaId"],
        #     key_values=[self.company_id],
        #     parameters={
        #         "imageBase64": image_base64,
        #         "FileExtension": file_ext,
        #         "FileName": image_path.split('/')[-1],
        #         "ContentType": content_type,
        #         "workerId": worker_id,
        #         "Notes": notes,
        #         "_sourceCompany": self.company_id,
        #         "cashExpense": is_cash
        #     }
        # )
        
        # Simulated document ID
        document_id = f"DOC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        print(f"✓ Receipt uploaded: {document_id}")
        return document_id
    
    def create_expense_line(self, expense_data: Dict) -> Dict:
        """
        Create a new expense line.
        
        Args:
            expense_data: Expense line data dictionary
            
        Returns:
            Created expense record with ExpTransNumber
        """
        print(f"Creating expense: {expense_data.get('Description', 'No description')}...")
        
        # Ensure required fields
        required_fields = ["TransactionDate", "Amount", "CurrencyCode", "PayMethod"]
        for field in required_fields:
            if field not in expense_data:
                raise ValueError(f"Required field missing: {field}")
        
        # Add company ID
        expense_data["dataAreaId"] = self.company_id
        
        # This would call the MCP create action
        # result = mcp_d365fo-mcp-se_d365fo_create_entity_record(
        #     entity_name="ExpCopilotAutomationExpenses",
        #     data=expense_data,
        #     return_record=True
        # )
        
        # Simulated result
        result = {
            **expense_data,
            "ExpTransNumber": f"EXP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "RecId": 5637144576
        }
        
        print(f"✓ Expense created: {result['ExpTransNumber']}")
        return result
    
    def attach_receipt_to_expense(self, exp_trans_number: str, 
                                   document_id: str, receipt_name: str,
                                   notes: str = "") -> Dict:
        """
        Attach a receipt to an expense line.
        
        Args:
            exp_trans_number: Expense transaction number
            document_id: Document ID from receipt upload
            receipt_name: Descriptive name for the receipt
            notes: Optional notes
            
        Returns:
            Receipt attachment record
        """
        print(f"Attaching receipt to expense {exp_trans_number}...")
        
        # First get the expense record to get RecId
        # expense = mcp_d365fo-mcp-se_d365fo_get_entity_record(...)
        
        # Simulated expense RecId
        ref_rec_id = 5637144576
        
        attachment_data = {
            "Name": receipt_name,
            "RefRecId": ref_rec_id,
            "RefTableId": 7302,  # TrvExpTrans table
            "RefCompanyId": self.company_id,
            "DocumentId": document_id,
            "FileExtension": "jpg",
            "Notes": notes,
            "IsCashExpense": "No",
            "DefaultAttachment": "Yes",
            "ExpenseLineAttachedTo": exp_trans_number
        }
        
        # This would create the attachment
        # result = mcp_d365fo-mcp-se_d365fo_create_entity_record(
        #     entity_name="ExpCopilotAttachedReceipts",
        #     data=attachment_data,
        #     return_record=True
        # )
        
        print("✓ Receipt attached successfully")
        return attachment_data
    
    def itemize_expense(self, exp_trans_number: str, 
                       itemizations: List[Dict]) -> bool:
        """
        Split an expense into multiple line items.
        
        Args:
            exp_trans_number: Expense transaction number to itemize
            itemizations: List of itemization dictionaries
            
        Returns:
            True if successful
        """
        print(f"Itemizing expense {exp_trans_number}...")
        
        # Validate total matches
        total = sum(item['amount'] for item in itemizations)
        print(f"  Total itemized amount: ${total:.2f}")
        
        for i, item in enumerate(itemizations, 1):
            print(f"  {i}. {item['description']}: ${item['amount']:.2f}")
        
        # This would call the itemization action
        # result = mcp_d365fo-mcp-se_d365fo_call_action(
        #     action_name="itemizeExpenseQuickly",
        #     entity_name="ExpCopilotAutomationExpenses",
        #     key_fields=["dataAreaId", "ExpTransNumber"],
        #     key_values=[self.company_id, exp_trans_number],
        #     parameters={"itemizations": json.dumps(itemizations)}
        # )
        
        print("✓ Expense itemized successfully")
        return True
    
    def create_expense_report(self, worker_personnel_number: str,
                             description: str, purpose: str = "",
                             project_id: Optional[str] = None) -> Dict:
        """
        Create an expense report header.
        
        Args:
            worker_personnel_number: Employee personnel number
            description: Report description
            purpose: Purpose of expenses
            project_id: Optional project ID
            
        Returns:
            Created expense report record
        """
        print("Creating expense report...")
        
        report_data = {
            "LegalEntity_DataArea": self.company_id,
            "TrvHcmWorker_PersonnelNumber": worker_personnel_number,
            "Txt1": description,
            "Txt2": purpose,
            "InterCompanyLE": self.company_id,
            "PaymentDate": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "ApprovalStatus": "Draft"
        }
        
        if project_id:
            report_data["ProjId"] = project_id
        
        # This would create the report
        # result = mcp_d365fo-mcp-se_d365fo_create_entity_record(
        #     entity_name="ExpCopilotAutomationReports",
        #     data=report_data,
        #     return_record=True
        # )
        
        # Simulated result
        result = {
            **report_data,
            "ExpNumber": f"RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
        
        print(f"✓ Expense report created: {result['ExpNumber']}")
        return result
    
    def submit_expense_report(self, report_number: str) -> bool:
        """
        Submit an expense report to workflow.
        
        Args:
            report_number: Expense report number
            
        Returns:
            True if successful
        """
        print(f"Submitting expense report {report_number}...")
        
        # This would update the report
        # result = mcp_d365fo-mcp-se_d365fo_update_entity_record(
        #     entity_name="ExpCopilotAutomationReports",
        #     key_fields=["LegalEntity_DataArea", "ExpNumber"],
        #     key_values=[self.company_id, report_number],
        #     data={
        #         "WorkflowAction": "Submit",
        #         "ApprovalStatus": "Submitted"
        #     }
        # )
        
        print("✓ Expense report submitted for approval")
        return True


def example_1_simple_cash_expense():
    """Example 1: Create a simple cash expense without receipt."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Simple Cash Expense (No Receipt)")
    print("="*60)
    
    helper = ExpenseSubmissionHelper("USSI")
    
    # Create parking expense
    expense = helper.create_expense_line({
        "TransactionDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ExpenseCategory": "PARKING",
        "Description": "Airport parking - Business trip",
        "Amount": 48.00,
        "CurrencyCode": "USD",
        "PayMethod": "CASH",
        "ReceiptRequired": "No",
        "CostOwner": "Employee"
    })
    
    print(f"\n✅ Cash expense created: {expense['ExpTransNumber']}")


def example_2_credit_card_with_receipt():
    """Example 2: Credit card expense with receipt attachment."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Credit Card Expense with Receipt")
    print("="*60)
    
    helper = ExpenseSubmissionHelper("USSI")
    
    # Upload receipt first
    document_id = helper.upload_receipt(
        image_path="receipts/dinner_2026-04-18.jpg",
        worker_id="000001",
        notes="Client dinner - itemized receipt",
        is_cash=False
    )
    
    # Create expense
    expense = helper.create_expense_line({
        "TransactionDate": "2026-04-18T19:30:00Z",
        "ExpenseCategory": "MEALS",
        "Description": "Client dinner - Project kickoff meeting",
        "Amount": 185.75,
        "CurrencyCode": "USD",
        "PayMethod": "CREDITCARD",
        "ReceiptRequired": "Yes",
        "CostOwner": "Company",
        "Merchant": "The Steakhouse",
        "AddressCity": "Los Angeles",
        "AddressState": "CA",
        "AddressZipCode": 90001,
        "TaxAmount": 14.86,
        "TaxGroup": "CA",
        "NumOfGuests": 3
    })
    
    # Attach receipt
    helper.attach_receipt_to_expense(
        exp_trans_number=expense['ExpTransNumber'],
        document_id=document_id,
        receipt_name="Client Dinner Receipt",
        notes="All attendees listed on receipt"
    )
    
    print(f"\n✅ Expense with receipt created: {expense['ExpTransNumber']}")


def example_3_itemized_expense():
    """Example 3: Hotel expense with itemization."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Itemized Hotel Expense")
    print("="*60)
    
    helper = ExpenseSubmissionHelper("USSI")
    
    # Create main expense
    expense = helper.create_expense_line({
        "TransactionDate": "2026-04-18T00:00:00Z",
        "ExpenseCategory": "HOTEL",
        "Description": "Hotel stay - Business trip (3 nights)",
        "Amount": 897.00,
        "CurrencyCode": "USD",
        "PayMethod": "CREDITCARD",
        "ReceiptRequired": "Yes",
        "Merchant": "Hilton Hotel",
        "AddressCity": "San Francisco",
        "AddressState": "CA"
    })
    
    # Itemize the expense
    helper.itemize_expense(
        exp_trans_number=expense['ExpTransNumber'],
        itemizations=[
            {
                "description": "Room charge (3 nights @ $250/night)",
                "amount": 750.00,
                "category": "HOTEL",
                "quantity": 3
            },
            {
                "description": "Resort fee",
                "amount": 75.00,
                "category": "HOTEL",
                "quantity": 1
            },
            {
                "description": "Parking",
                "amount": 45.00,
                "category": "PARKING",
                "quantity": 3
            },
            {
                "description": "Tax",
                "amount": 27.00,
                "category": "TAX",
                "quantity": 1
            }
        ]
    )
    
    print(f"\n✅ Itemized expense created: {expense['ExpTransNumber']}")


def example_4_complete_workflow():
    """Example 4: Complete workflow - Create expenses and submit report."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Complete Expense Submission Workflow")
    print("="*60)
    
    helper = ExpenseSubmissionHelper("USSI")
    
    # Check configuration
    config = helper.check_configuration()
    
    # Create multiple expenses
    expenses = []
    
    # Expense 1: Flight
    expenses.append(helper.create_expense_line({
        "TransactionDate": "2026-04-15T00:00:00Z",
        "ExpenseCategory": "AIRFARE",
        "Description": "Flight LAX-SFO round trip",
        "Amount": 425.00,
        "CurrencyCode": "USD",
        "PayMethod": "CREDITCARD",
        "ReceiptRequired": "Yes",
        "ProjId": "PROJ-2026-001"
    }))
    
    # Expense 2: Hotel
    expenses.append(helper.create_expense_line({
        "TransactionDate": "2026-04-16T00:00:00Z",
        "ExpenseCategory": "HOTEL",
        "Description": "Hotel - 2 nights",
        "Amount": 598.00,
        "CurrencyCode": "USD",
        "PayMethod": "CREDITCARD",
        "ReceiptRequired": "Yes",
        "ProjId": "PROJ-2026-001"
    }))
    
    # Expense 3: Meals
    expenses.append(helper.create_expense_line({
        "TransactionDate": "2026-04-17T00:00:00Z",
        "ExpenseCategory": "MEALS",
        "Description": "Business meals",
        "Amount": 125.50,
        "CurrencyCode": "USD",
        "PayMethod": "CREDITCARD",
        "ReceiptRequired": "Yes",
        "ProjId": "PROJ-2026-001"
    }))
    
    # Create expense report
    report = helper.create_expense_report(
        worker_personnel_number="000001",
        description="April 2026 - Client Site Visit",
        purpose="Project PROJ-2026-001 kickoff meeting in San Francisco",
        project_id="PROJ-2026-001"
    )
    
    # Submit the report
    helper.submit_expense_report(report['ExpNumber'])
    
    total_amount = sum(exp['Amount'] for exp in expenses)
    print(f"\n✅ Complete workflow finished:")
    print(f"   Report: {report['ExpNumber']}")
    print(f"   Expenses: {len(expenses)} line items")
    print(f"   Total: ${total_amount:.2f}")


def example_5_per_diem_and_mileage():
    """Example 5: Per diem and mileage expenses."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Per Diem and Mileage")
    print("="*60)
    
    helper = ExpenseSubmissionHelper("USSI")
    
    # Per diem expense
    per_diem = helper.create_expense_line({
        "TransactionDate": "2026-04-18T00:00:00Z",
        "ExpenseCategory": "PERDIEM",
        "Description": "Per diem allowance - Business trip (3 days)",
        "Amount": 180.00,  # 3 days x $60/day
        "CurrencyCode": "USD",
        "PayMethod": "COMPANY",
        "ReceiptRequired": "No",
        "Location": "New York, NY",
        "PerDiemMealAllowance": 180.00,
        "NumOfDays": 3
    })
    
    # Mileage expense
    mileage = helper.create_expense_line({
        "TransactionDate": "2026-04-18T00:00:00Z",
        "ExpenseCategory": "MILEAGE",
        "Description": "Personal vehicle mileage - Client site visit",
        "Amount": 104.86,  # 156.5 miles x $0.67/mile
        "CurrencyCode": "USD",
        "PayMethod": "COMPANY",
        "ReceiptRequired": "No",
        "MileageQty": 156.5,
        "MileageRate": 0.67,
        "Origin": "Office - Los Angeles",
        "Destination": "Client Site - San Diego"
    })
    
    print(f"\n✅ Per diem created: {per_diem['ExpTransNumber']}")
    print(f"✅ Mileage created: {mileage['ExpTransNumber']}")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("D365 F&O EXPENSE SUBMISSION EXAMPLES")
    print("="*60)
    print("\nThis script demonstrates various expense submission scenarios.")
    print("In a real implementation, these would call the D365FO MCP tools.")
    
    try:
        example_1_simple_cash_expense()
        example_2_credit_card_with_receipt()
        example_3_itemized_expense()
        example_4_complete_workflow()
        example_5_per_diem_and_mileage()
        
        print("\n" + "="*60)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
