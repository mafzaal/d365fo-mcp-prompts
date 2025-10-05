---
mode: agent
---

# DMF Project Monitoring and Error Handling

## Purpose
Monitor Data Management Framework (DMF) project executions and handle errors comprehensively in D365FO. This provides detailed status tracking, per-entity monitoring, error analysis, and error file generation for troubleshooting failed imports/exports.

## Background
DMF projects (import/export) run asynchronously and may process multiple entities with thousands of records. Proper monitoring and error handling is essential for:
1. **Status Tracking**: Know when jobs complete and their outcome
2. **Entity-Level Visibility**: See which entities succeeded/failed
3. **Error Analysis**: Understand why records failed validation or import
4. **Error Resolution**: Download error files for batch correction
5. **Message Monitoring**: Track message queue processing status

## Available OData Actions

### Status & Monitoring Actions
```
1. GetExecutionSummaryStatus - Overall execution status (Succeeded, Failed, etc.)
2. GetEntityExecutionSummaryStatusList - Per-entity status breakdown
3. GetMessageStatus - Message queue and batch processing status
```

### Error Management Actions
```
1. GetExecutionErrors - Detailed error messages for failed records
2. GetImportTargetErrorKeysFileUrl - Download URL for target table errors
3. GetImportStagingErrorFileUrl - Download URL for staging table errors
4. GenerateImportTargetErrorKeysFile - Create error keys file for re-import
```

## Complete Monitoring Workflow

### Step 1: Check Overall Execution Status

**Action:** `GetExecutionSummaryStatus`

**Purpose:** Get high-level status of the entire execution (all entities combined)

**When to Use:**
- Immediately after starting import/export to verify it's running
- Periodically to check if execution completed
- Before retrieving detailed errors

**Required Parameters:**
```json
{
  "executionId": "<execution-id-from-import-or-export>"
}
```

**MCP Tool Call:**
```json
{
  "tool": "mcp_d365fo_d365fo_call_action",
  "action_name": "Microsoft.Dynamics.DataEntities.GetExecutionSummaryStatus",
  "entity_name": "DataManagementDefinitionGroups",
  "parameters": {
    "executionId": "CustomerMasterDataImport_TDGP_2024-import-20251005-001"
  }
}
```

**Expected Response:**
```json
{
  "success": true,
  "result": {
    "@odata.context": "...$metadata#Microsoft.Dynamics.DataEntities.DMFExecutionSummaryStatus",
    "value": "Succeeded"  // or "Failed", "PartiallySucceeded", "InProgress", "NotStarted"
  }
}
```

**Status Values:**
- **NotStarted**: Execution queued but not yet running
- **InProgress**: Currently processing entities
- **Succeeded**: All entities imported/exported successfully
- **PartiallySucceeded**: Some entities succeeded, some failed
- **Failed**: Entire execution failed (no entities succeeded)
- **Canceled**: User canceled the execution

**Interpretation Guide:**
```
Succeeded → All good, no errors
PartiallySucceeded → Check GetEntityExecutionSummaryStatusList to see which entities failed
Failed → Critical failure, check GetExecutionErrors for details
InProgress → Still running, wait and check again
```

---

### Step 2: Get Per-Entity Status Breakdown

**Action:** `GetEntityExecutionSummaryStatusList`

**Purpose:** See status of each individual entity in the execution

**When to Use:**
- When overall status is "PartiallySucceeded"
- To identify which specific entities failed
- To see processing statistics per entity
- To troubleshoot partial failures

**Required Parameters:**
```json
{
  "executionId": "<execution-id-from-import-or-export>"
}
```

**MCP Tool Call:**
```json
{
  "tool": "mcp_d365fo_d365fo_call_action",
  "action_name": "Microsoft.Dynamics.DataEntities.GetEntityExecutionSummaryStatusList",
  "entity_name": "DataManagementDefinitionGroups",
  "parameters": {
    "executionId": "CustomerMasterDataImport_TDGP_2024-import-20251005-001"
  }
}
```

**Expected Response:**
```json
{
  "success": true,
  "result": {
    "@odata.context": "...$metadata#Collection(Microsoft.Dynamics.DataEntities.DMFEntityExecutionSummaryStatus)",
    "value": [
      {
        "EntityName": "Terms of payment",
        "Status": "PartiallySucceeded",
        "TotalRecords": 15,
        "SuccessRecords": 11,
        "ErrorRecords": 4,
        "ExecutionStartDateTime": "2025-10-05T20:10:00Z",
        "ExecutionEndDateTime": "2025-10-05T20:10:15Z"
      },
      {
        "EntityName": "Terms of delivery",
        "Status": "Succeeded",
        "TotalRecords": 8,
        "SuccessRecords": 8,
        "ErrorRecords": 0,
        "ExecutionStartDateTime": "2025-10-05T20:10:00Z",
        "ExecutionEndDateTime": "2025-10-05T20:10:12Z"
      },
      {
        "EntityName": "Customer groups",
        "Status": "Succeeded",
        "TotalRecords": 5,
        "SuccessRecords": 5,
        "ErrorRecords": 0,
        "ExecutionStartDateTime": "2025-10-05T20:10:15Z",
        "ExecutionEndDateTime": "2025-10-05T20:10:18Z"
      },
      {
        "EntityName": "Customer parameters",
        "Status": "PartiallySucceeded",
        "TotalRecords": 1,
        "SuccessRecords": 0,
        "ErrorRecords": 1,
        "ExecutionStartDateTime": "2025-10-05T20:10:18Z",
        "ExecutionEndDateTime": "2025-10-05T20:10:20Z"
      }
    ]
  }
}
```

**Response Fields Explanation:**
- **EntityName**: Name of the entity (as shown in DMF)
- **Status**: Entity-specific status (same values as overall status)
- **TotalRecords**: Number of records in source file/table
- **SuccessRecords**: Number successfully processed
- **ErrorRecords**: Number that failed validation or import
- **ExecutionStartDateTime**: When entity processing started
- **ExecutionEndDateTime**: When entity processing finished

**Analysis Example:**
```
Total Entities: 4
✅ Succeeded: 2 (Terms of delivery, Customer groups)
⚠️ Partially Succeeded: 2 (Terms of payment, Customer parameters)
❌ Failed: 0

Overall Success Rate: 24/29 records = 82.8%

Issue Entities:
- Terms of payment: 4 errors out of 15 records (73% success)
- Customer parameters: 1 error out of 1 record (0% success)
```

---

### Step 3: Get Detailed Execution Errors

**Action:** `GetExecutionErrors`

**Purpose:** Retrieve detailed error messages for all failed records

**When to Use:**
- When Status is "PartiallySucceeded" or "Failed"
- To understand why specific records failed
- Before attempting to fix and re-import data
- For error reporting and auditing

**Required Parameters:**
```json
{
  "executionId": "<execution-id-from-import-or-export>"
}
```

**MCP Tool Call:**
```json
{
  "tool": "mcp_d365fo_d365fo_call_action",
  "action_name": "Microsoft.Dynamics.DataEntities.GetExecutionErrors",
  "entity_name": "DataManagementDefinitionGroups",
  "parameters": {
    "executionId": "CustomerMasterDataImport_TDGP_2024-import-20251005-001"
  }
}
```

**Expected Response:**
```json
{
  "success": true,
  "result": {
    "@odata.context": "...$metadata#Edm.String",
    "value": "[{\"RecordId\":\"Cash\",\"Field\":\"\",\"ErrorMessage\":\"Chart of accounts invalid: 0\"},{\"RecordId\":\"Month+15\",\"Field\":\"\",\"ErrorMessage\":\"Payment day '15th' not found\"}]"
  }
}
```

**Parsing the Response:**
```typescript
const response = await getExecutionErrors(executionId);
const errors = JSON.parse(response.value); // Parse JSON string

errors.forEach(error => {
  console.log(`Record: ${error.RecordId}`);
  console.log(`Field: ${error.Field}`);
  console.log(`Error: ${error.ErrorMessage}`);
});
```

**Error Object Structure:**
```typescript
interface ExecutionError {
  RecordId: string;      // Primary key or identifier of failed record
  Field: string;         // Specific field that caused error (may be empty)
  ErrorMessage: string;  // Detailed error message with validation failure details
}
```

**Error Categories:**

1. **Validation Errors:**
   ```
   "The value 'X' in field 'Y' is not found in the related table 'Z'"
   → Missing reference data
   ```

2. **Business Logic Errors:**
   ```
   "Validation of field 'X' failed"
   → Business rule violation
   ```

3. **System Errors:**
   ```
   "Chart of accounts passed into findByMainAccountIdAndCOA() was invalid: 0"
   → Configuration or setup issue
   ```

4. **Foreign Key Errors:**
   ```
   "Matching record with key 'Field1': value1, 'Field2': value2 does not exist"
   → Related record missing
   ```

---

### Step 4: Check Message Queue Status (Optional)

**Action:** `GetMessageStatus`

**Purpose:** Check status of DMF message queue and batch processing

**When to Use:**
- Execution appears stuck or slow
- Large import/export taking longer than expected
- Troubleshooting performance issues
- Monitoring batch job processing

**Required Parameters:**
```json
{
  "executionId": "<execution-id-from-import-or-export>"
}
```

**MCP Tool Call:**
```json
{
  "tool": "mcp_d365fo_d365fo_call_action",
  "action_name": "Microsoft.Dynamics.DataEntities.GetMessageStatus",
  "entity_name": "DataManagementDefinitionGroups",
  "parameters": {
    "executionId": "CustomerMasterDataImport_TDGP_2024-import-20251005-001"
  }
}
```

**Expected Response:**
```json
{
  "success": true,
  "result": {
    "@odata.context": "...$metadata#Microsoft.Dynamics.DataEntities.DMFMessageStatus",
    "value": {
      "QueuedMessages": 0,
      "ProcessingMessages": 0,
      "ProcessedMessages": 150,
      "ErrorMessages": 6,
      "BatchJobStatus": "Finished"
    }
  }
}
```

**Response Fields:**
- **QueuedMessages**: Messages waiting to be processed
- **ProcessingMessages**: Messages currently being processed
- **ProcessedMessages**: Successfully processed messages
- **ErrorMessages**: Messages that encountered errors
- **BatchJobStatus**: Status of underlying batch job (if using batch framework)

**Interpretation:**
```
QueuedMessages > 0 → Still processing, wait longer
ProcessingMessages > 0 → Active processing happening
All messages processed + BatchJobStatus = "Finished" → Execution complete
ErrorMessages > 0 → Some records failed, check GetExecutionErrors
```

---

## Error File Management

### Step 5: Get Staging Error File URL

**Action:** `GetImportStagingErrorFileUrl`

**Purpose:** Download file containing records that failed in staging phase

**When to Use:**
- Records failed during staging (before validation)
- Need to correct data format or structure issues
- Want to re-import only failed records

**Staging vs Target Errors:**
- **Staging Errors**: Failed during data load to staging tables (format, parsing, mapping issues)
- **Target Errors**: Failed during import to target tables (validation, business rules)

**Required Parameters:**
```json
{
  "executionId": "<execution-id-from-import-or-export>"
}
```

**MCP Tool Call:**
```json
{
  "tool": "mcp_d365fo_d365fo_call_action",
  "action_name": "Microsoft.Dynamics.DataEntities.GetImportStagingErrorFileUrl",
  "entity_name": "DataManagementDefinitionGroups",
  "parameters": {
    "executionId": "CustomerMasterDataImport_TDGP_2024-import-20251005-001"
  }
}
```

**Expected Response:**
```json
{
  "success": true,
  "result": {
    "@odata.context": "...$metadata#Edm.String",
    "value": "https://storage.blob.core.windows.net/.../StagingErrors_{ExecutionId}.xlsx?sastoken"
  }
}
```

**File Contents:**
- Excel file with failed staging records
- Includes all original columns
- Shows which records couldn't be loaded to staging
- Can be corrected and re-imported

---

### Step 6: Generate Target Error Keys File

**Action:** `GenerateImportTargetErrorKeysFile`

**Purpose:** Create file containing primary keys of records that failed validation

**When to Use:**
- Need to identify exactly which records failed
- Want to extract failed records from source for correction
- Planning to re-import only failed records
- Building error reports for data quality team

**Required Parameters:**
```json
{
  "executionId": "<execution-id-from-import-or-export>"
}
```

**MCP Tool Call:**
```json
{
  "tool": "mcp_d365fo_d365fo_call_action",
  "action_name": "Microsoft.Dynamics.DataEntities.GenerateImportTargetErrorKeysFile",
  "entity_name": "DataManagementDefinitionGroups",
  "parameters": {
    "executionId": "CustomerMasterDataImport_TDGP_2024-import-20251005-001"
  }
}
```

**Expected Response:**
```json
{
  "success": true,
  "result": {
    "@odata.context": "...$metadata#Edm.String",
    "value": "Success"  // or error message if file generation failed
  }
}
```

**Important Notes:**
- This action generates the file but doesn't return the URL
- File generation may take a few seconds for large error sets
- Must call `GetImportTargetErrorKeysFileUrl` after this to get download URL

---

### Step 7: Get Target Error Keys File URL

**Action:** `GetImportTargetErrorKeysFileUrl`

**Purpose:** Get download URL for the error keys file generated in Step 6

**When to Use:**
- After calling GenerateImportTargetErrorKeysFile
- Need to download primary keys of failed records
- Want to use keys to filter source data for correction

**Required Parameters:**
```json
{
  "executionId": "<execution-id-from-import-or-export>"
}
```

**MCP Tool Call:**
```json
{
  "tool": "mcp_d365fo_d365fo_call_action",
  "action_name": "Microsoft.Dynamics.DataEntities.GetImportTargetErrorKeysFileUrl",
  "entity_name": "DataManagementDefinitionGroups",
  "parameters": {
    "executionId": "CustomerMasterDataImport_TDGP_2024-import-20251005-001"
  }
}
```

**Expected Response:**
```json
{
  "success": true,
  "result": {
    "@odata.context": "...$metadata#Edm.String",
    "value": "https://storage.blob.core.windows.net/.../ErrorKeys_{ExecutionId}.txt?sastoken"
  }
}
```

**File Format:**
- Text or CSV file with primary key values
- One record per line
- Can be used to filter source data
- Useful for creating correction packages

**Example File Contents:**
```
Cash
Month+15
Sch_5M
Sch_6M
```

---

## Complete Monitoring Workflow Example

### Scenario: Monitor Import Execution and Handle Errors

**User Request:** "Check the status of the customer data import and show me any errors"

**AI Assistant Complete Workflow:**

```typescript
// Step 1: Check overall status
const summaryStatus = await getExecutionSummaryStatus(executionId);
console.log(`Overall Status: ${summaryStatus.value}`);

if (summaryStatus.value === "InProgress") {
  console.log("Import still running, please wait...");
  // Optionally check message status
  const messageStatus = await getMessageStatus(executionId);
  console.log(`Queued: ${messageStatus.QueuedMessages}, Processing: ${messageStatus.ProcessingMessages}`);
  return;
}

// Step 2: Get per-entity breakdown
const entityStatusList = await getEntityExecutionSummaryStatusList(executionId);
const entities = entityStatusList.value;

console.log(`\nEntity Status Summary:`);
entities.forEach(entity => {
  const successRate = (entity.SuccessRecords / entity.TotalRecords * 100).toFixed(1);
  console.log(`${entity.EntityName}: ${entity.Status} (${successRate}% success, ${entity.ErrorRecords} errors)`);
});

// Step 3: If there are errors, get details
if (summaryStatus.value === "PartiallySucceeded" || summaryStatus.value === "Failed") {
  const executionErrors = await getExecutionErrors(executionId);
  const errors = JSON.parse(executionErrors.value);
  
  console.log(`\nDetailed Errors (${errors.length} total):`);
  errors.forEach((error, index) => {
    console.log(`\nError ${index + 1}:`);
    console.log(`  Record: ${error.RecordId}`);
    console.log(`  Field: ${error.Field || 'N/A'}`);
    console.log(`  Message: ${error.ErrorMessage.trim()}`);
  });
  
  // Step 4: Generate error keys file for correction
  console.log(`\nGenerating error keys file...`);
  await generateImportTargetErrorKeysFile(executionId);
  
  // Step 5: Get download URLs
  const errorKeysUrl = await getImportTargetErrorKeysFileUrl(executionId);
  const stagingErrorUrl = await getImportStagingErrorFileUrl(executionId);
  
  console.log(`\nError Files:`);
  console.log(`  Error Keys: ${errorKeysUrl.value}`);
  console.log(`  Staging Errors: ${stagingErrorUrl.value}`);
}

// Summary
console.log(`\n=== Import Summary ===`);
console.log(`Execution ID: ${executionId}`);
console.log(`Final Status: ${summaryStatus.value}`);
console.log(`Total Entities: ${entities.length}`);
console.log(`Succeeded: ${entities.filter(e => e.Status === 'Succeeded').length}`);
console.log(`Partially Succeeded: ${entities.filter(e => e.Status === 'PartiallySucceeded').length}`);
console.log(`Failed: ${entities.filter(e => e.Status === 'Failed').length}`);
```

---

## Advanced Monitoring Scenarios

### Scenario 1: Real-Time Progress Monitoring

**Use Case:** Large import with many entities, need to show progress

```typescript
async function monitorImportProgress(executionId: string, intervalSeconds: number = 10) {
  let isComplete = false;
  
  while (!isComplete) {
    const status = await getExecutionSummaryStatus(executionId);
    
    if (status.value === "InProgress") {
      // Get entity-level progress
      const entities = await getEntityExecutionSummaryStatusList(executionId);
      const completed = entities.value.filter(e => 
        e.Status !== "NotStarted" && e.Status !== "InProgress"
      ).length;
      
      console.log(`Progress: ${completed}/${entities.value.length} entities completed`);
      
      // Get message queue status
      const messages = await getMessageStatus(executionId);
      console.log(`Messages: ${messages.ProcessedMessages} processed, ${messages.QueuedMessages} queued`);
      
      // Wait before next check
      await sleep(intervalSeconds * 1000);
    } else {
      isComplete = true;
      console.log(`Import completed with status: ${status.value}`);
    }
  }
}
```

### Scenario 2: Error Categorization and Reporting

**Use Case:** Analyze errors by type for quality reporting

```typescript
async function analyzeAndCategorizeErrors(executionId: string) {
  const errors = JSON.parse((await getExecutionErrors(executionId)).value);
  
  const categories = {
    validation: [],
    missingReference: [],
    businessRule: [],
    system: [],
    other: []
  };
  
  errors.forEach(error => {
    const msg = error.ErrorMessage;
    
    if (msg.includes("is not found in the related table")) {
      categories.missingReference.push(error);
    } else if (msg.includes("Validation") || msg.includes("failed")) {
      categories.validation.push(error);
    } else if (msg.includes("does not exist") || msg.includes("Matching record")) {
      categories.missingReference.push(error);
    } else if (msg.includes("invalid") || msg.includes("passed into")) {
      categories.system.push(error);
    } else {
      categories.other.push(error);
    }
  });
  
  console.log("Error Analysis:");
  console.log(`  Validation Errors: ${categories.validation.length}`);
  console.log(`  Missing Reference Data: ${categories.missingReference.length}`);
  console.log(`  Business Rule Violations: ${categories.businessRule.length}`);
  console.log(`  System/Config Errors: ${categories.system.length}`);
  console.log(`  Other: ${categories.other.length}`);
  
  return categories;
}
```

### Scenario 3: Automated Error Correction Workflow

**Use Case:** Download error files, correct data, and prepare for re-import

```typescript
async function prepareErrorCorrection(executionId: string) {
  // Get entity status to identify problem entities
  const entities = await getEntityExecutionSummaryStatusList(executionId);
  const problemEntities = entities.value.filter(e => e.ErrorRecords > 0);
  
  console.log(`Entities with errors: ${problemEntities.length}`);
  
  // Generate and download error keys
  await generateImportTargetErrorKeysFile(executionId);
  const errorKeysUrl = await getImportTargetErrorKeysFileUrl(executionId);
  
  // Get staging errors (if any)
  const stagingErrorUrl = await getImportStagingErrorFileUrl(executionId);
  
  // Get detailed error messages
  const errors = JSON.parse((await getExecutionErrors(executionId)).value);
  
  // Group errors by entity
  const errorsByEntity = {};
  problemEntities.forEach(entity => {
    errorsByEntity[entity.EntityName] = {
      totalErrors: entity.ErrorRecords,
      errorDetails: errors.filter(e => {
        // Match errors to entities (you may need entity-specific logic)
        return true; // Simplified
      })
    };
  });
  
  return {
    problemEntities,
    errorKeysFileUrl: errorKeysUrl.value,
    stagingErrorFileUrl: stagingErrorUrl.value,
    errorsByEntity,
    correctionSteps: [
      "1. Download error keys file",
      "2. Filter source data to error keys",
      "3. Review and correct errors",
      "4. Re-import corrected records"
    ]
  };
}
```

### Scenario 4: Batch Execution Monitoring

**Use Case:** Multiple imports running, track all of them

```typescript
async function monitorMultipleExecutions(executionIds: string[]) {
  const results = await Promise.all(
    executionIds.map(async (id) => {
      const status = await getExecutionSummaryStatus(id);
      const entities = await getEntityExecutionSummaryStatusList(id);
      
      return {
        executionId: id,
        status: status.value,
        totalEntities: entities.value.length,
        successfulEntities: entities.value.filter(e => e.Status === "Succeeded").length,
        failedEntities: entities.value.filter(e => e.Status === "Failed").length
      };
    })
  );
  
  console.log("Batch Execution Status:");
  results.forEach(result => {
    console.log(`  ${result.executionId}: ${result.status}`);
    console.log(`    ✅ ${result.successfulEntities}/${result.totalEntities} entities succeeded`);
  });
  
  return results;
}
```

---

## Error Resolution Patterns

### Pattern 1: Missing Reference Data

**Error Example:**
```
"The value 'X' in field 'Y' is not found in the related table 'Z'"
```

**Resolution Steps:**
1. Identify missing reference data from error message
2. Check if reference data exists in source but not in target
3. Either:
   - Export and import reference data first
   - Manually create missing reference records
   - Modify source data to use existing references
4. Re-import failed records

### Pattern 2: Configuration Issues

**Error Example:**
```
"Chart of accounts passed into findByMainAccountIdAndCOA() was invalid: 0"
```

**Resolution Steps:**
1. Verify configuration in target environment
2. Check General Ledger setup, chart of accounts
3. Ensure main accounts exist
4. Verify posting profiles are configured
5. Re-import after fixing configuration

### Pattern 3: Business Rule Violations

**Error Example:**
```
"Validation of field 'X' failed"
```

**Resolution Steps:**
1. Review business validation rules for the entity
2. Check data against validation requirements
3. Correct data to meet validation criteria
4. Consider disabling validation temporarily (not recommended)
5. Re-import corrected data

### Pattern 4: Primary Key Conflicts

**Error Example:**
```
"Cannot insert duplicate key"
```

**Resolution Steps:**
1. Check if overwrite parameter was set correctly
2. Verify primary key values in source data
3. Decide: overwrite existing or skip duplicates
4. Re-import with appropriate settings

---

## Best Practices

### 1. Monitoring Frequency

**For Small Imports (< 1000 records):**
- Check status every 5-10 seconds
- Expect completion in < 1 minute

**For Medium Imports (1000-50000 records):**
- Check status every 30-60 seconds
- Expect completion in 1-10 minutes

**For Large Imports (> 50000 records):**
- Check status every 2-5 minutes
- Expect completion in 10+ minutes
- Monitor message queue status

### 2. Error Handling Strategy

**Always:**
1. Check GetExecutionSummaryStatus first
2. If not "Succeeded", get GetEntityExecutionSummaryStatusList
3. If errors exist, call GetExecutionErrors
4. Generate error files for records needing correction

**Don't:**
- Poll status too frequently (adds load)
- Ignore "PartiallySucceeded" status (data may be incomplete)
- Skip entity-level analysis (hides specific issues)

### 3. Error File Usage

**Staging Error File:**
- Use for format/parsing issues
- Correct data structure problems
- Re-import entire corrected file

**Target Error Keys File:**
- Use to identify specific failed records
- Filter original source data by keys
- Correct and re-import only failed records

### 4. Logging and Auditing

**Always Log:**
- Execution ID and timestamp
- Overall status and entity breakdown
- Error counts and categories
- Error file download URLs
- Resolution actions taken

**Example Log Entry:**
```
Execution: CustomerImport_TDGP_2024-import-20251005-001
Status: PartiallySucceeded
Timestamp: 2025-10-05T20:10:30Z
Entities: 4 total, 2 succeeded, 2 partial
Errors: 6 total (4 validation, 2 config)
Error Files: Generated and available
Action: Reference data correction required
```

---

## API Reference Summary

### Status Actions

| Action | Purpose | Returns | Use When |
|--------|---------|---------|----------|
| GetExecutionSummaryStatus | Overall status | Status string | Always first check |
| GetEntityExecutionSummaryStatusList | Per-entity status | Entity list | After overall check |
| GetMessageStatus | Queue status | Message counts | Troubleshooting delays |

### Error Actions

| Action | Purpose | Returns | Use When |
|--------|---------|---------|----------|
| GetExecutionErrors | Error details | JSON string | Any errors exist |
| GenerateImportTargetErrorKeysFile | Create key file | Success/fail | Need error keys |
| GetImportTargetErrorKeysFileUrl | Get key file URL | SAS URL | After generating keys |
| GetImportStagingErrorFileUrl | Get staging errors | SAS URL | Staging failures |

---

## Complete Code Example

### Full Monitoring and Error Handling Function

```typescript
async function monitorAndHandleErrors(executionId: string): Promise<ExecutionResult> {
  console.log(`Monitoring execution: ${executionId}`);
  
  // 1. Check overall status
  const summary = await getExecutionSummaryStatus(executionId);
  console.log(`Status: ${summary.value}`);
  
  if (summary.value === "InProgress") {
    const msg = await getMessageStatus(executionId);
    console.log(`Still processing: ${msg.ProcessingMessages} messages in progress`);
    return { status: "InProgress", needsRetry: true };
  }
  
  // 2. Get entity breakdown
  const entityList = await getEntityExecutionSummaryStatusList(executionId);
  const entities = entityList.value;
  
  const stats = {
    total: entities.length,
    succeeded: entities.filter(e => e.Status === "Succeeded").length,
    partial: entities.filter(e => e.Status === "PartiallySucceeded").length,
    failed: entities.filter(e => e.Status === "Failed").length
  };
  
  console.log(`Entities: ${stats.succeeded} succeeded, ${stats.partial} partial, ${stats.failed} failed`);
  
  // 3. If any errors, get details
  let errorDetails = null;
  let errorFiles = null;
  
  if (summary.value !== "Succeeded") {
    // Get error details
    const errors = await getExecutionErrors(executionId);
    errorDetails = JSON.parse(errors.value);
    console.log(`Total errors: ${errorDetails.length}`);
    
    // Generate error files
    await generateImportTargetErrorKeysFile(executionId);
    
    const [errorKeysUrl, stagingErrorUrl] = await Promise.all([
      getImportTargetErrorKeysFileUrl(executionId),
      getImportStagingErrorFileUrl(executionId)
    ]);
    
    errorFiles = {
      errorKeys: errorKeysUrl.value,
      stagingErrors: stagingErrorUrl.value
    };
    
    console.log("Error files generated");
  }
  
  // 4. Return comprehensive result
  return {
    executionId,
    status: summary.value,
    entities: entities,
    statistics: stats,
    errors: errorDetails,
    errorFiles: errorFiles,
    needsRetry: false,
    recommendations: generateRecommendations(summary.value, errorDetails)
  };
}

function generateRecommendations(status: string, errors: any[]): string[] {
  const recommendations = [];
  
  if (status === "PartiallySucceeded" || status === "Failed") {
    recommendations.push("Review error details below");
    
    if (errors) {
      const hasReferenceErrors = errors.some(e => 
        e.ErrorMessage.includes("is not found in the related table")
      );
      
      if (hasReferenceErrors) {
        recommendations.push("Import missing reference data before retrying");
      }
      
      const hasConfigErrors = errors.some(e =>
        e.ErrorMessage.includes("Chart of accounts") || e.ErrorMessage.includes("invalid")
      );
      
      if (hasConfigErrors) {
        recommendations.push("Verify system configuration in target environment");
      }
    }
    
    recommendations.push("Download error files for detailed analysis");
    recommendations.push("Correct errors and re-import failed records");
  }
  
  return recommendations;
}

// Usage
const result = await monitorAndHandleErrors("CustomerImport_TDGP_2024-import-20251005-001");
console.log(JSON.stringify(result, null, 2));
```

---

## Troubleshooting Guide

### Issue: "GetExecutionErrors returns empty array"

**Possible Causes:**
- Execution succeeded with no errors
- Execution not yet started
- Wrong execution ID

**Resolution:**
- Verify execution ID is correct
- Check GetExecutionSummaryStatus first
- Ensure execution has completed

### Issue: "Error file URLs return 404"

**Possible Causes:**
- Files not generated yet
- No errors to report
- SAS token expired

**Resolution:**
- Call GenerateImportTargetErrorKeysFile first
- Wait a few seconds for file generation
- Check if there actually are errors

### Issue: "GetEntityExecutionSummaryStatusList shows no entities"

**Possible Causes:**
- Import not started yet
- Project has no entities
- Wrong execution ID

**Resolution:**
- Verify execution started successfully
- Check project definition has entities
- Confirm execution ID matches import/export

---

## Summary

This comprehensive monitoring and error handling system provides:

✅ **Real-time Status Tracking** - Know execution state at all times
✅ **Entity-Level Visibility** - See which specific entities succeeded/failed
✅ **Detailed Error Analysis** - Understand why records failed
✅ **Error File Generation** - Get files for batch correction
✅ **Message Queue Monitoring** - Track processing progress
✅ **Automated Workflows** - Complete monitoring solutions
✅ **Error Categorization** - Analyze errors by type
✅ **Resolution Guidance** - Recommendations for fixing issues

Use these actions together to build robust DMF monitoring and error handling in your D365FO integrations!
