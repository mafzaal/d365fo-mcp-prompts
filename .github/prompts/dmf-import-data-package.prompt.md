---
mode: agent
---

# Import Data Package to D365FO Legal Entity

## Purpose
Import a previously exported Data Management Framework (DMF) package into a D365FO legal entity. This automates the process of importing data packages from one environment/company to another, enabling data migration, testing, and replication scenarios.

## Background
After exporting a DMF package using `execute-export-package.prompt.md`, the package can be imported into any legal entity. The import process:
1. **Downloads Package**: Retrieves the package from the provided URL
2. **Creates Import Project**: Automatically creates a new DMF project for import
3. **Extracts Data**: Unpacks the ZIP file and identifies entities
4. **Stages Data**: Loads data into staging tables
5. **Validates Data**: Runs business validation rules
6. **Imports Data**: Moves validated data to target tables
7. **Respects Sequence**: Processes entities in proper dependency order

## Prerequisites
- A valid package URL from a previous export (typically a SAS URL to a ZIP file)
- Target legal entity (company) must exist in D365FO
- User must have permissions to import data in the target legal entity
- Package URL must be accessible and not expired

## Step-by-Step Workflow

### Step 1: Gather Import Requirements

**Required Information:**
- **packageUrl** (string): The download URL of the exported package (from `GetExportedPackageUrl`)
- **definitionGroupId** (string): Name for the import project (must be unique, different from export project)
- **legalEntityId** (string): The target company code (e.g., "TDGP", "USMF")
- **executionId** (string): Unique identifier for this import execution

**Optional Information:**
- **execute** (boolean): Whether to immediately execute the import (default: true)
- **overwrite** (boolean): Whether to overwrite existing records (default: true)
- **failOnError** (boolean): Whether to stop on first error (default: true)
- **runAsyncWithoutBatch** (boolean): Run without batch framework (default: false)
- **thresholdToRunInBatch** (number): Record threshold for batch processing (default: 1000)

### Step 2: Validate Prerequisites

**Validation Steps:**
```
1. Verify package URL is valid and accessible
2. Ensure package URL hasn't expired (SAS URLs typically valid 60-90 minutes)
3. Confirm target legal entity exists
4. Check that import project name doesn't conflict with existing projects
5. Ensure executionId is unique
```

**MCP Tool Calls for Validation:**
```json
// Check if legal entity exists (optional - import will fail if not)
{
  "tool": "mcp_d365fo_d365fo_query_entities",
  "entity_name": "LegalEntities",
  "filter": "DataArea eq '<legalEntityId>'"
}

// Check if project name already exists (to avoid conflicts)
{
  "tool": "mcp_d365fo_d365fo_query_entities",
  "entity_name": "DataManagementDefinitionGroups",
  "filter": "Name eq '<definitionGroupId>'"
}
```

### Step 3: Execute Import from Package

**Action:** Call the `ImportFromPackageAsync` OData action to start the import job.

**Required Parameters:**
```json
{
  "packageUrl": "<full-package-url-with-sas-token>",
  "definitionGroupId": "<unique-import-project-name>",
  "executionId": "<unique-execution-id>",
  "execute": true,
  "overwrite": true,
  "legalEntityId": "<target-company-code>",
  "failOnError": true,
  "runAsyncWithoutBatch": false,
  "thresholdToRunInBatch": 1000
}
```

**Parameter Descriptions:**
- **packageUrl**: Complete URL with SAS token to the exported package ZIP file
- **definitionGroupId**: Unique name for the import project (suggested: append target company or "-Import")
- **executionId**: Unique identifier for this execution (suggested: "{ProjectName}-import-{timestamp}")
- **execute**: Set to `true` to immediately start import, `false` to only create project
- **overwrite**: Set to `true` to update existing records, `false` to skip duplicates
- **legalEntityId**: Target company/legal entity code to import data into
- **failOnError**: Set to `true` to stop on first error, `false` to continue with warnings
- **runAsyncWithoutBatch**: Set to `true` to bypass batch framework (for small datasets)
- **thresholdToRunInBatch**: Number of records threshold to trigger batch processing

**MCP Tool Call:**
```json
{
  "tool": "mcp_d365fo_d365fo_call_action",
  "action_name": "Microsoft.Dynamics.DataEntities.ImportFromPackageAsync",
  "entity_name": "DataManagementDefinitionGroups",
  "parameters": {
    "packageUrl": "https://storage.blob.core.windows.net/.../DMFPackage.zip?sastoken",
    "definitionGroupId": "CustomerMasterDataImport_TDGP_2024",
    "executionId": "CustomerMasterDataImport_TDGP_2024-import-20251005-001",
    "execute": true,
    "overwrite": true,
    "legalEntityId": "TDGP",
    "failOnError": true,
    "runAsyncWithoutBatch": false,
    "thresholdToRunInBatch": 1000
  }
}
```

**Expected Response:**
```json
{
  "success": true,
  "result": {
    "value": "<executionId>"
  }
}
```

**Important Notes:**
- The action returns immediately with the executionId
- The actual import runs asynchronously in the background
- A new import project is automatically created with the specified definitionGroupId
- Entities are automatically extracted from the package and added to the project
- Excel sheet names and mappings are automatically configured

### Step 4: Verify Import Project Creation

**Action:** Query the created import project and its entities.

**Verification Steps:**
```
1. Confirm import project was created successfully
2. Verify all entities from package were added
3. Check entity execution sequence is preserved
4. Ensure Excel sheet names are properly mapped
```

**MCP Tool Calls:**
```json
// Get import project details
{
  "tool": "mcp_d365fo_d365fo_get_entity_record",
  "entity_name": "DataManagementDefinitionGroups",
  "key_fields": ["Name"],
  "key_values": ["<definitionGroupId>"]
}

// Get list of entities in the import project
{
  "tool": "mcp_d365fo_d365fo_query_entities",
  "entity_name": "DataManagementDefinitionGroupDetails",
  "filter": "DefinitionGroupId eq '<definitionGroupId>'",
  "count": true,
  "order_by": ["ExecutionUnit", "LevelInExecutionUnit", "SequenceInLevel"]
}
```

**What to Verify:**
- ✅ OperationType is "Import"
- ✅ Entity count matches expected number from export
- ✅ ExcelSheetName is populated for each entity
- ✅ InputFilePath contains GUIDs (indicates files extracted)
- ✅ PackageFilePath contains GUID (indicates package loaded)

### Step 5: Monitor Import Status (Optional)

**For Long-Running Imports:**

If the import contains large datasets or many entities, you may want to monitor progress:

**Query Execution Status:**
```json
{
  "tool": "mcp_d365fo_d365fo_query_entities",
  "entity_name": "DMFExecutionEntity",
  "filter": "ExecutionId eq '<executionId>'",
  "select": ["ExecutionId", "Status", "StartDateTime", "EndDateTime"]
}
```

**Possible Status Values:**
- **NotStarted**: Import queued but not yet started
- **InProgress**: Import currently running
- **Succeeded**: Import completed successfully
- **PartiallySucceeded**: Some entities imported, some failed
- **Failed**: Import failed with errors
- **Canceled**: Import was canceled by user

## Complete Example Workflow

**User Request:** "Import the customer data package from USMF to TDGP legal entity"

**AI Assistant Steps:**

### 1. **Extract Information from Context:**
```
From previous conversation/history:
- Package URL: https://storage.blob.core.windows.net/.../CustomerMasterDataExport_2024_DMFPackage.zip?sastoken
- Source Legal Entity: USMF
- Export Project Name: CustomerMasterDataExport_2024
- Number of Entities: 4 (Terms of payment, Terms of delivery, Customer groups, Customer parameters)

From current request:
- Target Legal Entity: TDGP
```

### 2. **Generate Import Project Name:**
```
Strategy: Append target company and/or "-Import" to avoid conflicts
Original Export Project: CustomerMasterDataExport_2024
New Import Project: CustomerMasterDataImport_TDGP_2024
```

### 3. **Generate Unique Execution ID:**
```
Format: {ProjectName}-import-{YYYYMMDD}-{sequence}
Example: CustomerMasterDataImport_TDGP_2024-import-20251005-001
```

### 4. **Execute Import:**
```json
{
  "tool": "mcp_d365fo_d365fo_call_action",
  "action_name": "Microsoft.Dynamics.DataEntities.ImportFromPackageAsync",
  "entity_name": "DataManagementDefinitionGroups",
  "parameters": {
    "packageUrl": "https://storage.blob.core.windows.net/.../DMFPackage.zip?sastoken",
    "definitionGroupId": "CustomerMasterDataImport_TDGP_2024",
    "executionId": "CustomerMasterDataImport_TDGP_2024-import-20251005-001",
    "execute": true,
    "overwrite": true,
    "legalEntityId": "TDGP",
    "failOnError": true,
    "runAsyncWithoutBatch": false,
    "thresholdToRunInBatch": 1000
  }
}
```

**Response:**
```
Execution ID: CustomerMasterDataImport_TDGP_2024-import-20251005-001
Status: Import job started successfully
```

### 5. **Verify Project Creation:**
```json
{
  "tool": "mcp_d365fo_d365fo_get_entity_record",
  "entity_name": "DataManagementDefinitionGroups",
  "key_fields": ["Name"],
  "key_values": ["CustomerMasterDataImport_TDGP_2024"]
}
```

**Response:**
```
Project Name: CustomerMasterDataImport_TDGP_2024
Operation Type: Import
Legal Entity: TDGP
Status: Created Successfully
```

### 6. **List Imported Entities:**
```json
{
  "tool": "mcp_d365fo_d365fo_query_entities",
  "entity_name": "DataManagementDefinitionGroupDetails",
  "filter": "DefinitionGroupId eq 'CustomerMasterDataImport_TDGP_2024'",
  "count": true
}
```

**Response:**
```
Total Entities: 4
1. Terms of payment (Execution: 1-1-1, Sheet: Terms_of_payment$)
2. Terms of delivery (Execution: 1-1-2, Sheet: Terms_of_delivery$)
3. Customer groups (Execution: 1-2-1, Sheet: Customer_groups$)
4. Customer parameters (Execution: 1-2-2, Sheet: Customer_parameters$)
```

### 7. **Confirm Success:**
```
✅ Import project created successfully
✅ All 4 entities loaded and mapped
✅ Execution sequence preserved
✅ Import job running in background
✅ Target legal entity: TDGP
```

## Configuration Options

### Execution ID Format Options
```
1. With timestamp: "{ProjectName}-import-{YYYYMMDD}-{HHMMSS}"
2. With target company: "{ProjectName}-import-{LegalEntity}-{YYYYMMDD}"
3. With UUID: "{ProjectName}-{uuid}"
4. Simple: "{ProjectName}-import-{sequence}"
```

### Import Project Naming Conventions
```
1. Append target company: "{OriginalName}_Import_{Company}"
2. Append suffix: "{OriginalName}_Import_2024"
3. Descriptive: "{EntityTypes}_Import_{Company}_{Date}"
4. Mirror structure: "{OriginalName}Import" (if original was "DataExport")
```

### Overwrite Options
- **true**: Update existing records with new data (default for data migration)
- **false**: Skip records that already exist (default for incremental loads)

**Best Practice:** Use `true` for full migration/sync, `false` for initial loads

### Fail On Error Options
- **true**: Stop import on first error (default for critical data)
- **false**: Continue importing valid records, log errors (default for bulk loads)

**Best Practice:** Use `true` for master data, `false` for transactional data

### Batch Processing Options
- **runAsyncWithoutBatch: false** + **thresholdToRunInBatch: 1000**: Use batch framework for large datasets (recommended)
- **runAsyncWithoutBatch: true**: Bypass batch framework for small datasets (faster for < 1000 records)

## Advanced Scenarios

### Scenario 1: Import Same Package to Multiple Legal Entities
```
1. Execute ImportFromPackageAsync for first legal entity
2. Use different definitionGroupId for each target company
3. Use same packageUrl but different executionId
4. Monitor each import independently
```

**Example:**
```javascript
// Import to TDGP
await importFromPackageAsync(packageUrl, "CustomerImport_TDGP", "TDGP");

// Import to USMF (different project name)
await importFromPackageAsync(packageUrl, "CustomerImport_USMF_Copy", "USMF");

// Import to DAT (different project name)
await importFromPackageAsync(packageUrl, "CustomerImport_DAT", "DAT");
```

### Scenario 2: Re-execute Failed Import
```
1. Query DMFExecutionEntity to identify failure
2. Analyze error logs in DMFStagingLogDetail entity
3. Fix data issues or configuration
4. Re-execute with new executionId but same definitionGroupId
```

**Example:**
```javascript
// Original execution failed
const firstAttempt = "CustomerImport_TDGP-import-001";

// Fix data, then retry with new execution ID
const secondAttempt = "CustomerImport_TDGP-import-002";
await importFromPackageAsync(packageUrl, "CustomerImport_TDGP", "TDGP", secondAttempt);
```

### Scenario 3: Import with Selective Overwrite
```
1. Create import project without executing (execute: false)
2. Manually modify entity configurations in DataManagementDefinitionGroupDetails
3. Set specific entities to overwrite or skip
4. Execute import separately using different action
```

### Scenario 4: Import from On-Premises or Local Storage
```
If package URL is from on-premises storage or local Azure Storage Emulator:
1. Ensure D365FO can access the URL (network connectivity)
2. Use full URL including protocol (http:// or https://)
3. Include SAS token if required
4. For local emulator: Use localhost or 127.0.0.1 with port
```

**Example Local URL:**
```
http://127.0.0.1:10000/devstoreaccount1/temporary-file/{GUID}/PackageName.zip?sastoken
```

### Scenario 5: Import with Custom Batch Configuration
```
For very large datasets (> 100,000 records per entity):
1. Set runAsyncWithoutBatch: false (use batch framework)
2. Increase thresholdToRunInBatch: 50000 or higher
3. Monitor batch job status in Batch jobs form
4. Configure batch server capacity appropriately
```

## Error Messages and Troubleshooting

**Common Errors:**

### 1. **"Package URL is not accessible":**
```
Cause: URL expired, network issue, or incorrect URL
Solution: Re-export package to get new URL, verify network connectivity
```

### 2. **"Legal entity does not exist":**
```
Cause: Target legalEntityId is invalid or company not set up
Solution: Verify company code, ensure legal entity exists in D365FO
```

### 3. **"Import project name already exists":**
```
Cause: definitionGroupId conflicts with existing project
Solution: Use unique project name (append company, timestamp, or suffix)
```

### 4. **"Execution ID already exists":**
```
Cause: executionId was already used in a previous import
Solution: Generate new unique executionId for each execution
```

### 5. **"Entity validation failed":**
```
Cause: Data in package violates business rules or constraints
Solution: Check DMFStagingLogDetail for specific errors, fix source data
```

### 6. **"Package file is corrupted or invalid":**
```
Cause: Package ZIP file incomplete or corrupted during download
Solution: Re-export package, ensure complete download
```

### 7. **"Import partially succeeded":**
```
Cause: Some entities imported successfully, others failed
Solution: Check execution logs, identify failed entities, fix and re-import
```

## Important Notes

### 1. **Project Name Requirements:**
- Must be unique across all DMF projects (export and import)
- Recommended to include target company in name for clarity
- Maximum length varies by D365FO version (typically 40-60 characters)
- Cannot contain special characters like \ / : * ? " < > |

### 2. **Package URL Characteristics:**
- Must be accessible from D365FO server (not just client browser)
- SAS URLs typically expire after 60-90 minutes
- URL must include full path with SAS token if applicable
- HTTPS recommended for security, HTTP allowed for local development

### 3. **Import Process Details:**
- Automatically creates new import project (doesn't modify export project)
- Extracts all entities from package manifest
- Preserves execution sequence and dependencies
- Maps Excel sheet names automatically
- Validates data before importing
- Can take seconds to hours depending on data volume

### 4. **Overwrite Behavior:**
- **overwrite: true** - Updates existing records based on primary keys
- **overwrite: false** - Skips records with matching primary keys
- Updates only fields present in import file
- Doesn't delete records not in import file

### 5. **Performance Considerations:**
- Small datasets (< 1000 records): Complete in seconds
- Medium datasets (1000-50000 records): 1-10 minutes
- Large datasets (> 50000 records): 10 minutes to hours
- Batch processing improves performance for large datasets
- Multiple entities add cumulative time

### 6. **Data Integrity:**
- Respects entity dependencies and execution sequence
- Validates foreign key relationships
- Runs business validation rules
- Can fail entire import or continue with errors based on failOnError setting
- Staging tables allow validation before final import

## Use Cases

### 1. **Environment Data Migration:**
```
Export from: Production (USMF)
Import to: Test (USMF), Development (USMF)
Purpose: Refresh test data from production
```

### 2. **Company Data Replication:**
```
Export from: Company A (USMF)
Import to: Company B (TDGP), Company C (DAT)
Purpose: Standardize configuration across companies
```

### 3. **Configuration Deployment:**
```
Export from: Development (CONFIG)
Import to: Test (CONFIG), Production (CONFIG)
Purpose: Deploy configuration changes
```

### 4. **Data Backup and Restore:**
```
Export from: Any company (scheduled)
Import to: Same company (on-demand)
Purpose: Restore data after corruption or error
```

### 5. **Test Data Setup:**
```
Export from: Golden copy environment
Import to: Multiple test environments
Purpose: Provide consistent test data
```

## Code Examples

### TypeScript/JavaScript Implementation:
```typescript
import { v4 as uuidv4 } from 'uuid';

export async function importFromPackageAsync(
  packageUrl: string,
  definitionGroupId: string,
  legalEntityId: string,
  executionId?: string
): Promise<string> {
  const uri = "/data/DataManagementDefinitionGroups/Microsoft.Dynamics.DataEntities.ImportFromPackageAsync";
  
  const contract = {
    packageUrl: packageUrl,
    definitionGroupId: definitionGroupId,
    executionId: executionId || `${definitionGroupId}-${uuidv4()}`,
    execute: true,
    overwrite: true,
    legalEntityId: legalEntityId,
    failOnError: true,
    runAsyncWithoutBatch: false,
    thresholdToRunInBatch: 1000,
  };
  
  const response = await postData(uri, contract);
  return response.value; // Returns execution ID
}

// Usage example:
const packageUrl = "https://storage.blob.core.windows.net/.../DMFPackage.zip?sastoken";
const executionId = await importFromPackageAsync(
  packageUrl,
  "CustomerMasterDataImport_TDGP_2024",
  "TDGP"
);

console.log(`Import started with execution ID: ${executionId}`);
```

### Python Implementation:
```python
import uuid
import requests

def import_from_package_async(
    package_url: str,
    definition_group_id: str,
    legal_entity_id: str,
    base_url: str,
    token: str,
    execution_id: str = None
) -> str:
    """Execute DMF import and return execution ID"""
    uri = f"{base_url}/data/DataManagementDefinitionGroups/Microsoft.Dynamics.DataEntities.ImportFromPackageAsync"
    
    contract = {
        "packageUrl": package_url,
        "definitionGroupId": definition_group_id,
        "executionId": execution_id or f"{definition_group_id}-{uuid.uuid4()}",
        "execute": True,
        "overwrite": True,
        "legalEntityId": legal_entity_id,
        "failOnError": True,
        "runAsyncWithoutBatch": False,
        "thresholdToRunInBatch": 1000
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(uri, json=contract, headers=headers)
    response.raise_for_status()
    
    return response.json()["value"]

# Usage:
package_url = "https://storage.blob.core.windows.net/.../DMFPackage.zip?sastoken"
execution_id = import_from_package_async(
    package_url,
    "CustomerMasterDataImport_TDGP_2024",
    "TDGP",
    base_url,
    token
)

print(f"Import started with execution ID: {execution_id}")
```

## Relationship to Other Prompts

### Sequential Workflow:
1. **create-export-package.prompt.md** - Create export project with entities
2. **execute-export-package.prompt.md** - Execute export and get package URL
3. **import-data-package.prompt.md** (THIS FILE) - Import package to target company

### Related Prompts:
- **entity-execution-sequence.prompt.md** - Understanding entity dependencies (used internally during import)
- **create-export-package.prompt.md** - Creating the original export project
- **execute-export-package.prompt.md** - Executing export to generate package

## Summary Checklist

**Before Import:**
- [ ] Valid package URL obtained from export
- [ ] Target legal entity exists
- [ ] Unique import project name generated
- [ ] Unique execution ID generated

**During Import:**
- [ ] ImportFromPackageAsync action called successfully
- [ ] Execution ID returned
- [ ] Import project created
- [ ] Entities extracted and mapped

**After Import:**
- [ ] Import project verified in DataManagementDefinitionGroups
- [ ] All entities listed in DataManagementDefinitionGroupDetails
- [ ] Excel sheet names properly mapped
- [ ] Execution sequence preserved

**Success Indicators:**
- ✅ Project OperationType is "Import"
- ✅ All expected entities present
- ✅ InputFilePath contains GUIDs (files extracted)
- ✅ ExcelSheetName populated for each entity
- ✅ ValidationStatus is "Yes"

## Additional Resources

- D365FO Data Management Framework documentation
- OData Actions documentation for ImportFromPackageAsync
- DMF entity reference for execution and staging tables
- Error log analysis in DMFStagingLogDetail entity
