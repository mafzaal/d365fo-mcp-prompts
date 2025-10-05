# D365FO User Authentication Setup Guide

This guide provides step-by-step instructions for setting up access to Microsoft Dynamics 365 Finance & Operations (D365FO) and configuring Claude Desktop with the D365FO MCP server.

## Prerequisites

- Administrative access to Azure Portal
- Windows PowerShell or Command Prompt access
- Claude Desktop application installed

## Step 1: Grant User Access in Azure Portal

### 1.1 Navigate to Azure Portal
1. Open your web browser and go to [https://portal.azure.com](https://portal.azure.com)
2. Sign in with your Azure administrator credentials

### 1.2 Access Enterprise Applications
1. In the Azure Portal, click on **Microsoft Entra ID** (formerly Azure Active Directory)
2. In the left navigation menu, click **Enterprise applications**
   - **Alternative**: You can directly navigate to [Enterprise Applications](https://portal.azure.com/#view/Microsoft_AAD_IAM/StartboardApplicationsMenuBlade/~/AppAppsPreview)
3. If there's a filter showing "Application type == Enterprise Applications", click the **X** next to it to remove the filter and show all applications
4. Search for "Microsoft Dynamics ERP" in the application list
5. Click on the **Microsoft Dynamics ERP** application

### 1.3 Assign User Access
1. In the Microsoft Dynamics ERP application page, click **Users and groups** in the left navigation
2. Click **+ Add user/group** at the top of the page
3. In the **Add Assignment** panel:
   - Click **Users and groups**
   - Search for and select the user(s) you want to grant access to
   - Click **Select**
4. If roles are available, click **Select a role** and choose the appropriate role
5. Click **Assign** to complete the assignment

### 1.4 Verify Assignment
1. The user should now appear in the **Users and groups** list
2. Note down the user's email address and any assigned roles for reference

## Step 2: Install and Configure Azure CLI

### 2.1 Install Azure CLI (if not already installed)
1. Open PowerShell as Administrator
2. Run the following command to install Azure CLI using winget:
   ```powershell
   winget install --exact --id Microsoft.AzureCLI
   ```
3. Wait for the installation to complete
4. Close and reopen PowerShell to refresh the environment

### 2.2 Verify Installation
1. In PowerShell, run:
   ```powershell
   az --version
   ```
2. You should see version information for Azure CLI

### 2.3 Login to D365FO Environment
1. Run the following command to authenticate with your D365FO environment:
   ```powershell
   az login --scope https://your-fno-env/.default --allow-no-subscriptions
   ```
2. This will open a web browser window for authentication
3. Sign in with the user credentials that were granted access in Step 1
4. After successful authentication, you should see a JSON response with tenant and subscription information

**Alternative: Device Code Login**
If you cannot use browser-based authentication (e.g., on a headless server or restricted environment):
1. Use the device code flow instead:
   ```powershell
   az login --scope https://your-fno-env/.default --allow-no-subscriptions --use-device-code
   ```
2. The command will display a device code and a URL (https://microsoft.com/devicelogin)
3. Open the URL in a browser on any device with internet access
4. Enter the device code when prompted
5. Complete the authentication with your credentials
6. Return to the PowerShell session to see the authentication confirmation

### 2.4 Verify Authentication
1. Run the following to check your current login status:
   ```powershell
   az account show
   ```
2. Ensure the tenant ID matches your organization's tenant

## Step 3: Configure Claude Desktop

### 3.1 Locate Claude Desktop Configuration
1. Open File Explorer
2. Navigate to your user profile directory (usually `C:\Users\<username>`)
3. Look for the Claude Desktop configuration file:
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Alternative path**: `C:\Users\<username>\AppData\Roaming\Claude\claude_desktop_config.json`

### 3.2 Edit Configuration File
1. If the configuration file doesn't exist, create it in the appropriate directory
2. Open the file in your preferred text editor (Notepad, VS Code, etc.)
3. Replace the entire contents with the following configuration:

```json
{
  "mcpServers": {
    "d365fo": {
      "command": "uvx",
      "args": [
        "--from",
        "d365fo-client",
        "d365fo-mcp-server"
      ],
      "env": {
        "D365FO_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### 3.3 Save and Restart Claude Desktop
1. Save the configuration file
2. Close Claude Desktop completely
3. Restart Claude Desktop application
4. The D365FO MCP server should now be available

## Step 4: Verify Setup

### 4.1 Test Azure CLI Connection
1. In PowerShell, test the connection with a simple command:
   ```powershell
   az rest --method GET --url "https://your-fno-env/api/services"
   ```
2. You should receive a response indicating successful connection

### 4.2 Test Claude Desktop Integration
1. Open Claude Desktop
2. Start a new conversation
3. Ask Claude to test the D365FO connection
4. If properly configured, Claude should be able to access D365FO functions through the MCP server

## Troubleshooting

### Common Issues and Solutions

#### Azure CLI Issues
- **Error: 'az' is not recognized**: Restart PowerShell or add Azure CLI to your PATH environment variable
- **Authentication failure**: Ensure the user has proper permissions in Azure Portal
- **Scope errors**: Verify the D365FO environment URL is correct

#### Claude Desktop Issues
- **MCP server not loading**: Check the configuration file syntax and file location
- **uvx command not found**: Install uv package manager: `pip install uv`
- **Permission errors**: Run Claude Desktop as administrator if needed

#### D365FO Access Issues
- **403 Forbidden**: User may not have proper role assignments in D365FO
- **404 Not Found**: Verify the D365FO environment URL is correct and accessible
- **Token expiration**: Re-run the `az login` command to refresh authentication

## Security Notes

- Keep your Azure credentials secure and follow your organization's security policies
- The authentication tokens have limited lifetime and may require periodic renewal
- Monitor access logs in Azure Portal for any unusual activity
- Consider using managed identities or service principals for production environments

## Next Steps

After completing this setup, you should be able to:
- Access D365FO data through Azure CLI commands
- Use Claude Desktop with D365FO integration for data analysis and reporting
- Query D365FO entities and metadata through the MCP server

For additional help with specific D365FO operations, refer to the project documentation or contact your system administrator.