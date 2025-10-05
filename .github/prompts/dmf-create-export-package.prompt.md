---
mode: agent
---

# Create Data Management Export Project in D365FO

## Purpose
Create a Data Management Framework (DMF) export project in D365FO with proper entity sequencing and configuration. This automates the process of setting up export projects that can be executed to generate data packages.

## Background
A DMF export project consists of:
1. **Data Project Definition**: Container that defines project settings and operation type
2. **Data Project Entities**: Individual entities added to the project with execution order metadata
3. **Entity Sequencing**: Proper ordering based on dependencies to ensure clean exports

The process involves:
- Creating the project definition using `DataManagementDefinitionGroups` entity
- Getting execution sequence for the entities using `GetEntitySequence` action
- Adding each entity to the project using `DataManagementDefinitionGroupDetails` entity

## Step-by-Step Workflow

### Step 1: Validate Input Parameters

**Required Parameters:**
- **projectName** (string): Unique identifier for the project (e.g., "CustomerExport_2024")
- **projectDescription** (string): Human-readable description (e.g., "Export customer master data")
- **dataEntities** (array of strings): List of entity public collection names or labels

**Validation:**
```
1. Verify projectName is not empty and follows naming conventions
2. Verify all entity names exist in D365FO
3. Optionally check if project name already exists to avoid duplicates
```

### Step 2: Get Entity Execution Sequence

**CRITICAL**: Before creating the project, get the proper execution sequence for the entities.

**Action:** Use `GetEntitySequence` action as described in the `entity-execution-sequence.prompt.md`:

```
1. Convert entity public collection names to entity labels if needed
   - Use mcp_d365fo_d365fo_get_entity_schema to get label_text
   
2. Call GetEntitySequence action:
   - action_name: "Microsoft.Dynamics.DataEntities.GetEntitySequence"
   - entity_name: "DataManagementDefinitionGroups"
   - parameters: { "listOfDataEntities": "<comma-separated-entity-labels>" }

3. Parse the response to get execution metadata for each entity:
   - executionUnit (number)
   - levelInExecutionUnit (number)
   - sequenceInLevel (number)
```

**Example MCP Tool Call:**
```json
{
  "action_name": "Microsoft.Dynamics.DataEntities.GetEntitySequence",
  "entity_name": "DataManagementDefinitionGroups",
  "parameters": {
    "listOfDataEntities": "Customer groups,Customers V3,Terms of payment"
  }
}
```

### Step 3: Create Data Project Definition

**Entity:** `DataManagementDefinitionGroups`  
**Operation:** CREATE (POST)

**Required Fields:**
```json
{
  "Name": "<projectName>",
  "ProjectCategory": "Project",
  "OperationType": "Export",
  "GenerateDataPackage": "Yes",
  "Description": "<projectDescription>",
  "TruncateEntityData": "Yes"
}
```

**Field Descriptions:**
- **Name**: Unique project identifier (acts as primary key)
- **ProjectCategory**: Always "Project" for DMF projects
- **OperationType**: "Export" for export projects, "Import" for import projects
- **GenerateDataPackage**: "Yes" to create downloadable package, "No" otherwise
- **Description**: Project description for documentation
- **TruncateEntityData**: "Yes" to clear previous data, "No" to append

**MCP Tool Call:**
```
Use mcp_d365fo_d365fo_create_entity_record:
- entity_name: "DataManagementDefinitionGroups"
- data: <payload from above>
- return_record: true (to verify creation)
```

**Example:**
```json
{
  "entity_name": "DataManagementDefinitionGroups",
  "data": {
    "Name": "CustomerExport_2024",
    "ProjectCategory": "Project",
    "OperationType": "Export",
    "GenerateDataPackage": "Yes",
    "Description": "Export customer master data",
    "TruncateEntityData": "Yes"
  },
  "return_record": true
}
```

### Step 4: Add Entities to Project

**Entity:** `DataManagementDefinitionGroupDetails`  
**Operation:** CREATE (POST) - one record per entity

**For Each Entity in Sequence:**
```json
{
  "DefinitionGroupId": "<projectName>",
  "EntityName": "<entityName>",
  "ExecutionUnit": <executionUnit from sequence>,
  "LevelInExecutionUnit": <levelInExecutionUnit from sequence>,
  "SequenceInLevel": <sequenceInLevel from sequence>,
  "SourceFormat": "EXCEL",
  "DefaultRefreshType": "FullPush",
  "AutoGenerateMapping": "Yes"
}
```

**Field Descriptions:**
- **DefinitionGroupId**: Must match the project Name created in Step 3
- **EntityName**: The entity label (as used in GetEntitySequence)
- **ExecutionUnit**: From sequence response (determines processing group)
- **LevelInExecutionUnit**: From sequence response (determines dependency level)
- **SequenceInLevel**: From sequence response (determines order within level)
- **SourceFormat**: File format for export (EXCEL, CSV, XML, etc.)
- **DefaultRefreshType**: "FullPush" for complete export, "Incremental" for changes only
- **AutoGenerateMapping**: "Yes" to auto-map fields, "No" for manual mapping

**MCP Tool Call (Loop through sequenced entities):**
```
For each sequenced entity:
  Use mcp_d365fo_d365fo_create_entity_record:
  - entity_name: "DataManagementDefinitionGroupDetails"
  - data: <payload from above>
  - return_record: false (optional, for performance)
```

**Example Loop:**
```javascript
// Assuming sequencedDataEntities = [
//   { entityLabel: "Customer groups", executionUnit: 1, levelInExecutionUnit: 1, sequenceInLevel: 1 },
//   { entityLabel: "Customers V3", executionUnit: 1, levelInExecutionUnit: 2, sequenceInLevel: 1 }
// ]

For each entity:
{
  "entity_name": "DataManagementDefinitionGroupDetails",
  "data": {
    "DefinitionGroupId": "CustomerExport_2024",
    "EntityName": "Customer groups",
    "ExecutionUnit": 1,
    "LevelInExecutionUnit": 1,
    "SequenceInLevel": 1,
    "SourceFormat": "EXCEL",
    "DefaultRefreshType": "FullPush",
    "AutoGenerateMapping": "Yes"
  }
}
```

### Step 5: Verify Project Creation

**Verification Steps:**
```
1. Query the project to verify it was created:
   - Use mcp_d365fo_d365fo_get_entity_record
   - entity_name: "DataManagementDefinitionGroups"
   - key_fields: ["Name"]
   - key_values: [<projectName>]

2. Query project entities to verify all were added:
   - Use mcp_d365fo_d365fo_query_entities
   - entity_name: "DataManagementDefinitionGroupDetails"
   - filter: "DefinitionGroupId eq '<projectName>'"
   - Verify count matches input entity count
```

## Complete Example Workflow

**User Request:** "Create an export project for customer data including customers, customer groups, and payment terms"

**AI Assistant Steps:**

1. **Understand Requirements:**
   - Project name: Generate or ask user (e.g., "CustomerDataExport_2024")
   - Description: "Export customer master data"
   - Entities: ["CustomersV3", "CustomerGroups", "PaymentTerms"]

2. **Get Entity Labels:**
   ```
   Search/get schema for each entity to find label_text:
   - CustomersV3 → "Customers V3"
   - CustomerGroups → "Customer groups"
   - PaymentTerms → "Terms of payment"
   ```

3. **Get Execution Sequence:**
   ```
   Call GetEntitySequence with: "Customer groups,Terms of payment,Customers V3"
   Parse response to get execution metadata
   ```

4. **Create Project:**
   ```
   Create DataManagementDefinitionGroups record with project settings
   ```

5. **Add Entities:**
   ```
   For each entity in execution order:
     Create DataManagementDefinitionGroupDetails record
   ```

6. **Confirm Success:**
   ```
   Query and display created project and entities
   ```

## Configuration Options

### Operation Types
- **Export**: Extract data from D365FO
- **Import**: Load data into D365FO
- **CopyIntoLegalEntity**: Copy data between legal entities

### Source/Target Formats
- **EXCEL**: Excel workbook format
- **CSV**: Comma-separated values
- **XML**: XML format
- **PACKAGE**: Data package format
- **ODBC**: Database connection

### Refresh Types
- **FullPush**: Export/import all records
- **Incremental**: Only changed records (requires change tracking)
- **Upsert**: Insert new or update existing

### Generate Data Package Options
- **Yes**: Create downloadable package file
- **No**: Execute without package generation

## Important Notes

1. **Entity Names vs Labels:**
   - GetEntitySequence requires entity **labels** (e.g., "Customers V3")
   - Entity records can use labels or public collection names depending on field
   - Always verify the correct format by checking entity schema

2. **Execution Sequence:**
   - CRITICAL for maintaining referential integrity
   - Lower execution units run first
   - Lower levels within units run first
   - Lower sequences within levels run first

3. **Project Name Uniqueness:**
   - Project Name (DefinitionGroupId) must be unique
   - Check for existing projects before creation
   - Use timestamps or unique identifiers in names

4. **Error Handling:**
   - Validate all entity names exist before starting
   - Check for successful project creation before adding entities
   - Handle partial failures (project created but entities not added)
   - Verify all entities were added successfully

5. **Performance Considerations:**
   - Adding many entities may take time (sequential operations)
   - Consider batch operations if available
   - Provide progress updates for large projects

## Use Cases

1. **Master Data Export:**
   - Export reference data (customers, vendors, items)
   - Include dependent entities (groups, terms, categories)
   - Use for backup or migration

2. **Configuration Export:**
   - Export system configuration entities
   - Include parameters and settings
   - Use for environment setup

3. **Transaction Export:**
   - Export transactional data (orders, invoices)
   - Include headers and lines
   - Use for archival or reporting

4. **Cross-Environment Migration:**
   - Export from source environment
   - Import to target environment
   - Maintain data consistency

## Error Messages and Troubleshooting

**Common Errors:**

1. **"Entity not found":**
   - Verify entity name/label is correct
   - Check entity is available in D365FO version
   - Use search tools to find correct entity name

2. **"Project already exists":**
   - Project Name must be unique
   - Use different name or delete existing project

3. **"Invalid execution sequence":**
   - Ensure GetEntitySequence returned valid data
   - Verify all required fields are numeric
   - Check for parsing errors in response

4. **"Entity add failed":**
   - Verify project was created successfully
   - Check DefinitionGroupId matches project Name
   - Verify entity name format is correct

## Additional Resources

- See `entity-execution-sequence.prompt.md` for detailed GetEntitySequence usage
- D365FO Data Management Framework documentation
- Entity metadata can be explored using search tools
