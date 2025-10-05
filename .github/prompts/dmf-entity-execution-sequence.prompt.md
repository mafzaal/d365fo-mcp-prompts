---
mode: agent
---

# Get Entity Execution Sequence for D365FO Data Entities

## Purpose
Retrieve the execution sequence order for D365FO data entities used in Data Management Framework (DMF) operations. This determines the order in which entities should be imported/exported based on their dependencies.

## Background
The `GetEntitySequence` action in D365FO analyzes entity dependencies and returns execution metadata including:
- **Execution Unit**: Group of entities that can be processed together
- **Level in Execution Unit**: Dependency level (entities at lower levels must be processed first)
- **Sequence in Level**: Order within the same level

## How to Use D365FO MCP Tools

### Step 1: Identify the OData Action
The entity sequence is retrieved using the OData action:
- **Action Name**: `Microsoft.Dynamics.DataEntities.GetEntitySequence`
- **Entity Binding**: `DataManagementDefinitionGroups`
- **Binding Type**: Collection-bound action
- **Method**: POST

### Step 2: Prepare Entity List
**CRITICAL**: Use the entity **labels** (human-readable names), not the entity names or public collection names.

First, get the entity schema to find the label:
```
Use mcp_d365fo_d365fo_get_entity_schema or mcp_d365fo_d365fo_search_entities
Look for the "label_text" field in the response
```

Format the entity labels as a comma-separated string:
- Single entity: `"Customers V3"` (not "CustomersV3" or "CustCustomerV3Entity")
- Multiple entities: `"Customers V3,Sales order headers V2,Released products V2"`

**Example Mappings:**
| Entity Name | Public Collection | **Entity Label (Use This)** |
|-------------|-------------------|----------------------------|
| CustCustomerV3Entity | CustomersV3 | **Customers V3** |
| SalesOrderHeaderV2Entity | SalesOrderHeadersV2 | **Sales order headers V2** |
| CustCustomerGroupEntity | CustomerGroups | **Customer groups** |
| PaymentTermEntity | PaymentTerms | **Terms of payment** |
| DeliveryTermsEntity | DeliveryTerms | **Terms of delivery** |

### Step 3: Call the Action
Use the `mcp_d365fo_d365fo_call_action` tool with these parameters:

```
action_name: "Microsoft.Dynamics.DataEntities.GetEntitySequence"
entity_name: "DataManagementDefinitionGroups"
parameters: {
  "listOfDataEntities": "<comma-separated-entity-labels>"
}
profile: "default" (or your specific profile)
```

**Example:**
```json
{
  "action_name": "Microsoft.Dynamics.DataEntities.GetEntitySequence",
  "entity_name": "DataManagementDefinitionGroups",
  "parameters": {
    "listOfDataEntities": "Terms of payment,Terms of delivery,Customer groups,Customers V3,Customer parameters"
  }
}
```

### Step 4: Parse the Response
The action returns a comma-separated string with format:
```
EntityLabel-ExecutionUnit-LevelInExecutionUnit-SequenceInLevel,EntityLabel-ExecutionUnit-LevelInExecutionUnit-SequenceInLevel,...
```

Example raw response:
```
"Terms of payment-1-1-1,Terms of delivery-1-1-1,Customer groups-1-2-1,Customers V3-1-3-1,Customer parameters-1-4-1,"
```

**Note:** The response uses entity labels, not entity names.

### Step 5: Process the Results
Parse each comma-separated entry by splitting on `-` to extract:
1. **entityLabel** (string): Human-readable label of the data entity
2. **executionUnit** (number): Processing group number (lower numbers first)
3. **levelInExecutionUnit** (number): Dependency level within the unit (lower levels first)
4. **sequenceInLevel** (number): Order within the same level (lower numbers first)

Filter out any malformed entries (not exactly 4 parts) or empty strings.

**Sorting Priority:**
1. First by `executionUnit` (ascending)
2. Then by `levelInExecutionUnit` (ascending)
3. Finally by `sequenceInLevel` (ascending)

## Complete Example Workflow

**User Request:** "Get the execution sequence for customer-related entities"

**Steps:**
1. Search for entities: Use `mcp_d365fo_d365fo_search_entities` with pattern "customer"
2. Get entity schemas to find labels:
   - CustomerParametersEntity → "Customer parameters"
   - CustCustomerGroupEntity → "Customer groups"
   - PaymentTermEntity → "Terms of payment"
   - CustCustomerV3Entity → "Customers V3"
3. Format entity list: `"Customer parameters,Customer groups,Terms of payment,Customers V3"`
4. Call action using MCP tool
5. Parse response string
6. Sort by execution unit, level, and sequence
7. Present sorted results showing the correct import/export order

**Example Response:**
```
"Terms of payment-1-1-1,Terms of delivery-1-1-1,Customer groups-1-2-1,Customers V3-1-3-1,Customer parameters-1-4-1,"
```

**Expected Output Format:**
```
Execution Order:
1. Terms of payment (Unit: 1, Level: 1, Sequence: 1)
1. Terms of delivery (Unit: 1, Level: 1, Sequence: 1)
2. Customer groups (Unit: 1, Level: 2, Sequence: 1)
3. Customers V3 (Unit: 1, Level: 3, Sequence: 1)
4. Customer parameters (Unit: 1, Level: 4, Sequence: 1)
```

## Important Notes
- **CRITICAL**: Always use entity **labels** (e.g., "Customers V3"), not entity names (e.g., "CustCustomerV3Entity") or collection names (e.g., "CustomersV3")
- Use `mcp_d365fo_d365fo_get_entity_schema` to retrieve the correct label_text for each entity
- Entities with lower execution unit numbers should be processed first
- Within the same unit, process lower levels before higher levels
- Within the same level, follow the sequence number order
- This sequence ensures referential integrity during import/export operations
- Always validate that entity names exist before calling this action
- The response may include a trailing comma - handle this when parsing

## Error Handling
- Verify all entity names are valid D365FO public entity names
- Check that the action is available (may require specific D365FO version/configuration)
- Handle malformed responses by filtering entries that don't match the expected format
- If an entity is not found, the action may omit it from results or return an error

## Use Cases
1. **Data Import Planning**: Determine the correct order to import entities to avoid foreign key violations
2. **Data Export Sequencing**: Export entities in dependency order for clean re-imports
3. **DMF Project Configuration**: Configure data projects with proper entity sequencing
4. **Migration Scripts**: Plan multi-entity migrations with correct execution order