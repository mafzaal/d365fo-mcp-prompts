---
mode: agent
---

# Execute Data Management Export Package and Get Download URL

## Purpose
Execute a Data Management Framework (DMF) export project in D365FO and retrieve the downloadable package URL. This automates the process of running export jobs and obtaining the generated data package.

## Background
After creating a DMF export project with entities, the project needs to be executed to generate the actual data package. The execution process:
1. **Triggers Export**: Initiates the export job asynchronously
2. **Processes Entities**: Exports data from each entity in proper sequence
3. **Generates Package**: Creates a ZIP file containing exported data
4. **Provides URL**: Returns a temporary SAS URL for downloading the package

## Prerequisites
- An existing DMF export project created using `create-export-package.prompt.md`
- Project must have entities added with proper execution sequence
- Legal entity (company) must exist and contain data to export

## Step-by-Step Workflow

### Step 1: Validate Export Project Exists

**Required Information:**
- **definitionGroupId** (string): The Name of the export project (e.g., "USMF_CustomerExport_20241005")
- **legalEntityId** (string): The company code to export from (e.g., "USMF")

**Validation:**
```
1. Verify the project exists by querying DataManagementDefinitionGroups
2. Confirm it has OperationType = "Export"
3. Verify entities are added to the project
4. Ensure legal entity exists and has data
```

**MCP Tool Call:**
```json
{
  "tool": "mcp_d365fo_d365fo_get_entity_record",
  "entity_name": "DataManagementDefinitionGroups",
  "key_fields": ["Name"],
  "key_values": ["<definitionGroupId>"]
}
```

### Step 2: Execute Export to Package

**Action:** Call the `ExportToPackage` OData action to start the export job.

**Required Parameters:**
```json
{
  "definitionGroupId": "<project-name>",
  "packageName": "<definitionGroupId> - <legalEntityId>",
  "executionId": "<unique-execution-id>",
  "reExecute": true,
  "legalEntityId": "<company-code>"
}
```

**Parameter Descriptions:**
- **definitionGroupId**: The Name of the export project (must match existing project)
- **packageName**: Human-readable name for the package (suggested format: "{ProjectName} - {Company}")
- **executionId**: Unique identifier for this execution run (suggested format: "{ProjectName}-{timestamp}")
- **reExecute**: Set to `true` to allow re-running the export, `false` to prevent duplicates
- **legalEntityId**: The company/legal entity code to export data from

**MCP Tool Call:**
```json
{
  "action_name": "Microsoft.Dynamics.DataEntities.ExportToPackage",
  "entity_name": "DataManagementDefinitionGroups",
  "parameters": {
    "definitionGroupId": "USMF_CustomerExport_20241005",
    "packageName": "USMF_CustomerExport_20241005 - USMF",
    "executionId": "USMF_CustomerExport_20241005-export-20241005",
    "reExecute": true,
    "legalEntityId": "USMF"
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
- The actual export runs asynchronously in the background
- The executionId is required to retrieve the package URL later

### Step 3: Get Exported Package URL

**Action:** Call the `GetExportedPackageUrl` OData action to retrieve the download URL.

**Required Parameters:**
```json
{
  "executionId": "<executionId-from-step-2>"
}
```

**Parameter Descriptions:**
- **executionId**: The execution ID returned from the ExportToPackage action in Step 2

**MCP Tool Call:**
```json
{
  "action_name": "Microsoft.Dynamics.DataEntities.GetExportedPackageUrl",
  "entity_name": "DataManagementDefinitionGroups",
  "parameters": {
    "executionId": "USMF_CustomerExport_20241005-export-20241005"
  }
}
```

**Expected Response:**
```json
{
  "success": true,
  "result": {
    "value": "https://storage.blob.core.windows.net/path/to/package.zip?sastoken"
  }
}
```

**Important Notes:**
- If the export is still running, this may return an empty or error response
- The URL is a temporary SAS (Shared Access Signature) URL with limited validity (typically 60-90 minutes)
- The URL can be used to download the ZIP package containing exported data files

### Step 4: Handle Export Status and Timing

**Export Timing Considerations:**
```
1. Small datasets (< 1000 records per entity): Usually complete in seconds
2. Medium datasets (1000-10000 records): May take 1-3 minutes
3. Large datasets (> 10000 records): Can take 5-30 minutes or more
4. Multiple entities: Add time for each entity in sequence
```

**Polling Strategy (if needed):**
```
1. Call GetExportedPackageUrl immediately after ExportToPackage
2. If URL is not ready, wait 5-10 seconds and retry
3. Implement maximum retry count (e.g., 20 retries = ~2-3 minutes)
4. Inform user if export is taking longer than expected
```

**Error Handling:**
```
1. Empty URL response: Export still running or failed
2. Error in GetExportedPackageUrl: Export may have failed
3. Query DMFExecutionEntity to check execution status if needed
```

## Complete Example Workflow

**User Request:** "Execute the customer export project for USMF and get the download URL"

**AI Assistant Steps:**

### 1. **Identify Export Project:**
```
Project Name: USMF_CustomerExport_20241005
Legal Entity: USMF
```

### 2. **Validate Project Exists:**
```json
{
  "tool": "mcp_d365fo_d365fo_get_entity_record",
  "entity_name": "DataManagementDefinitionGroups",
  "key_fields": ["Name"],
  "key_values": ["USMF_CustomerExport_20241005"]
}
```

### 3. **Execute Export:**
```json
{
  "tool": "mcp_d365fo_d365fo_call_action",
  "action_name": "Microsoft.Dynamics.DataEntities.ExportToPackage",
  "entity_name": "DataManagementDefinitionGroups",
  "parameters": {
    "definitionGroupId": "USMF_CustomerExport_20241005",
    "packageName": "USMF_CustomerExport_20241005 - USMF",
    "executionId": "USMF_CustomerExport_20241005-export-20241005-143022",
    "reExecute": true,
    "legalEntityId": "USMF"
  }
}
```

**Response:**
```
Execution ID: USMF_CustomerExport_20241005-export-20241005-143022
Status: Export job started successfully
```

### 4. **Get Package URL:**
```json
{
  "tool": "mcp_d365fo_d365fo_call_action",
  "action_name": "Microsoft.Dynamics.DataEntities.GetExportedPackageUrl",
  "entity_name": "DataManagementDefinitionGroups",
  "parameters": {
    "executionId": "USMF_CustomerExport_20241005-export-20241005-143022"
  }
}
```

**Response:**
```
Package URL: https://storage.blob.core.windows.net/.../DMFPackage.zip?sv=...&se=...
Package Name: USMF_CustomerExport_20241005 - USMF_ABC123_DMFPackage.zip
Expires: In 90 minutes
```

### 5. **Confirm Success:**
```
✅ Export completed successfully
📦 Package contains: 4 entities
📥 Download URL provided
⏰ URL valid for: 90 minutes
```

## Configuration Options

### Execution ID Format Options
```
1. With timestamp: "{ProjectName}-export-{YYYYMMDD}-{HHMMSS}"
2. With UUID: "{ProjectName}-{uuid}"
3. Simple: "{ProjectName}-export-{YYYYMMDD}"
4. Custom: Any unique string (max length varies by D365FO version)
```

### Package Name Format Options
```
1. Standard: "{ProjectName} - {LegalEntity}"
2. With date: "{ProjectName} - {LegalEntity} - {Date}"
3. Descriptive: "{EntityTypes} Export - {LegalEntity}"
4. Custom: Any descriptive name (max length ~100 characters)
```

### ReExecute Options
- **true**: Allow re-running the export even if a previous execution exists
- **false**: Prevent duplicate executions (will fail if execution ID already used)

**Best Practice:** Use `true` for development/testing, `false` for production to prevent accidental re-runs

## Advanced Scenarios

### Scenario 1: Export with Custom Execution ID
```
Generate unique execution ID using timestamp or UUID:
- Timestamp: "ProjectName-export-20241005-143022"
- UUID: "ProjectName-550e8400-e29b-41d4-a716-446655440000"
```

### Scenario 2: Export Multiple Legal Entities
```
1. Execute export for each legal entity separately
2. Use different executionId for each
3. Retrieve package URL for each execution
4. Combine or process packages as needed
```

### Scenario 3: Check Export Status Before Getting URL
```
1. Query DMFExecutionEntity with executionId
2. Check ExecutionStatus field (Running, Succeeded, Failed, etc.)
3. Only call GetExportedPackageUrl if status is "Succeeded"
```

### Scenario 4: Automated Export Scheduling
```
1. Store project name and legal entity in configuration
2. Generate unique executionId for each scheduled run
3. Execute export and store URL in tracking system
4. Download and process package automatically
```

## Error Messages and Troubleshooting

**Common Errors:**

### 1. **"Export project not found":**
```
Cause: definitionGroupId doesn't match any existing project
Solution: Verify project name and ensure it was created successfully
```

### 2. **"Legal entity does not exist":**
```
Cause: legalEntityId is invalid or company doesn't exist
Solution: Verify company code and ensure it's set up in D365FO
```

### 3. **"Package URL is empty":**
```
Cause: Export is still running or failed
Solution: Wait a few seconds and retry GetExportedPackageUrl
Alternative: Check execution status in DMFExecutionEntity
```

### 4. **"Execution ID already exists":**
```
Cause: executionId was already used and reExecute is false
Solution: Generate a new unique executionId or set reExecute to true
```

### 5. **"No data exported":**
```
Cause: Entities have no data in the specified legal entity
Solution: Verify legal entity has data for the entities in the project
```

### 6. **"URL has expired":**
```
Cause: SAS URL validity period has elapsed
Solution: Re-execute the export to get a new URL
```

## Important Notes

### 1. **Execution ID Requirements:**
- Must be unique for each export execution
- Recommended to include timestamp or UUID
- Used to track and retrieve export results
- Cannot be reused unless reExecute is true

### 2. **Package URL Characteristics:**
- Temporary SAS URL with time-limited access
- Typically valid for 60-90 minutes
- Points to ZIP file in Azure Blob Storage
- One-time use recommended (download immediately)

### 3. **Export Process:**
- Runs asynchronously in the background
- Respects entity execution sequence and dependencies
- Generates one file per entity in EXCEL or configured format
- Creates manifest and metadata files in package

### 4. **Performance Considerations:**
- Small datasets export almost instantly
- Large datasets may take several minutes
- Multiple entities add cumulative time
- Network and server load affect timing

### 5. **Package Contents:**
- ZIP file containing exported data files
- Manifest.xml with metadata
- Package.xml with structure information
- One data file per entity (EXCEL, CSV, XML, etc.)

### 6. **Security Considerations:**
- SAS URLs contain access tokens - treat as sensitive
- URLs expire automatically for security
- Downloads are logged in D365FO audit trail
- Packages contain actual business data

## Use Cases

### 1. **Data Backup:**
```
Regular export of master data and configurations
Store packages in secure backup location
Version control for configuration changes
```

### 2. **Environment Migration:**
```
Export from source environment
Download package
Import to target environment
Verify data consistency
```

### 3. **Data Analysis:**
```
Export transactional data
Download and open in Excel
Perform offline analysis
Generate reports and insights
```

### 4. **Integration Testing:**
```
Export sample data from production
Import to test environment
Use for integration testing
Validate data processing logic
```

### 5. **Compliance and Auditing:**
```
Export data for regulatory compliance
Archive packages as evidence
Provide to auditors as needed
Maintain historical snapshots
```

## Code Examples

### TypeScript/JavaScript Implementation:
```typescript
import { v4 as uuidv4 } from 'uuid';

export async function exportToPackage(
  definitionGroupId: string,
  legalEntityId: string
): Promise<any> {
  const uri = "/data/DataManagementDefinitionGroups/Microsoft.Dynamics.DataEntities.ExportToPackage";
  
  const contract = {
    definitionGroupId: definitionGroupId,
    packageName: `${definitionGroupId} - ${legalEntityId}`,
    executionId: `${definitionGroupId}-${uuidv4()}`,
    reExecute: true,
    legalEntityId: legalEntityId,
  };
  
  return await postData(uri, contract);
}

export async function getExportedPackageUrl(
  executionId: string
): Promise<string> {
  const uri = "/data/DataManagementDefinitionGroups/Microsoft.Dynamics.DataEntities.GetExportedPackageUrl";
  
  const contract = {
    executionId: executionId
  };
  
  const response = await postData(uri, contract);
  return response.value;
}

// Usage:
const result = await exportToPackage("USMF_CustomerExport_20241005", "USMF");
const executionId = result.value;

// Wait for export to complete (polling)
let url = "";
let retries = 0;
while (!url && retries < 20) {
  await sleep(5000); // Wait 5 seconds
  url = await getExportedPackageUrl(executionId);
  retries++;
}

if (url) {
  console.log(`Download package: ${url}`);
} else {
  console.log("Export is taking longer than expected");
}
```

### Python Implementation:
```python
import uuid
import time
import requests

def export_to_package(definition_group_id: str, legal_entity_id: str, base_url: str, token: str) -> str:
    """Execute DMF export and return execution ID"""
    uri = f"{base_url}/data/DataManagementDefinitionGroups/Microsoft.Dynamics.DataEntities.ExportToPackage"
    
    contract = {
        "definitionGroupId": definition_group_id,
        "packageName": f"{definition_group_id} - {legal_entity_id}",
        "executionId": f"{definition_group_id}-{uuid.uuid4()}",
        "reExecute": True,
        "legalEntityId": legal_entity_id
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(uri, json=contract, headers=headers)
    response.raise_for_status()
    
    return response.json()["value"]

def get_exported_package_url(execution_id: str, base_url: str, token: str) -> str:
    """Get download URL for exported package"""
    uri = f"{base_url}/data/DataManagementDefinitionGroups/Microsoft.Dynamics.DataEntities.GetExportedPackageUrl"
    
    contract = {
        "executionId": execution_id
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(uri, json=contract, headers=headers)
    response.raise_for_status()
    
    return response.json()["value"]

# Usage:
execution_id = export_to_package("USMF_CustomerExport_20241005", "USMF", base_url, token)
print(f"Export started with execution ID: {execution_id}")

# Poll for completion
url = ""
retries = 0
while not url and retries < 20:
    time.sleep(5)
    try:
        url = get_exported_package_url(execution_id, base_url, token)
    except:
        pass
    retries += 1

if url:
    print(f"Package ready: {url}")
else:
    print("Export still processing...")
```

## Additional Resources

- See `create-export-package.prompt.md` for creating export projects
- D365FO Data Management Framework documentation
- OData Actions documentation for ExportToPackage and GetExportedPackageUrl
- DMF entity reference for execution status tracking
