[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$LegalEntity,
    
    [Parameter(Mandatory=$true)]
    [string]$InvoiceId,
    
    [Parameter(Mandatory=$false)]
    [string]$D365FOEnvironment = "https://usnconeboxax1aos.cloud.onebox.dynamics.com",
    
    [Parameter(Mandatory=$false)]
    [string]$OutputPath = ".\Reports",
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipAuthentication
)

function Write-LogMessage {
    param(
        [string]$Message,
        [ValidateSet("Info", "Warning", "Error", "Success")]
        [string]$Level = "Info"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $colors = @{
        "Info" = "White"
        "Warning" = "Yellow"
        "Error" = "Red"
        "Success" = "Green"
    }
    
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $colors[$Level]
}

function Test-AzureAuthentication {
    try {
        Write-LogMessage "Checking Azure CLI authentication status..." -Level "Info"
        $account = az account show 2>$null | ConvertFrom-Json
        if ($account) {
            Write-LogMessage "Authenticated as: $($account.user.name)" -Level "Success"
            return $true
        }
    }
    catch {
        Write-LogMessage "Not authenticated with Azure CLI" -Level "Warning"
    }
    return $false
}

function Invoke-AzureAuthentication {
    param([string]$Environment)
    
    Write-LogMessage "Authenticating with D365FO environment..." -Level "Info"
    try {
        $scope = "$Environment/.default"
        Write-LogMessage "Using scope: $scope" -Level "Info"
        
        # Attempt login with the specific scope
        $result = az login --scope $scope --allow-no-subscriptions 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-LogMessage "Authentication successful" -Level "Success"
            return $true
        } else {
            Write-LogMessage "Authentication failed. Error: $result" -Level "Error"
            return $false
        }
    }
    catch {
        Write-LogMessage "Authentication error: $($_.Exception.Message)" -Level "Error"
        return $false
    }
}

function Get-SafeFileName {
    param([string]$fileName)
    $invalidChars = [IO.Path]::GetInvalidFileNameChars() -join ''
    $pattern = "[$([regex]::Escape($invalidChars))]"
    return $fileName -replace $pattern, '_'
}

function Invoke-D365FOAction {
    param(
        [string]$Environment,
        [string]$LegalEntity,
        [string]$InvoiceId
    )
    
    Write-LogMessage "Preparing OData action call for Invoice: $InvoiceId in Legal Entity: $LegalEntity" -Level "Info"
    
    # Build the controller args JSON
    $controllerArgs = @{
        DataTableName = "CustInvoiceJour"
        DataTableFieldName = "InvoiceId"
        DataTableFieldValue = $InvoiceId
    } | ConvertTo-Json -Compress
    
    # Build the action parameters
    $actionPayload = @{
        "_contractName" = "SrsCopilotArgsContract"
        "_controllerArgsJson" = $controllerArgs
        "_controllerName" = "SalesInvoiceController"
        "_legalEntityName" = $LegalEntity
        "_reportParameterJson" = "{}"
    } | ConvertTo-Json -Compress
    
    Write-LogMessage "Controller Args: $controllerArgs" -Level "Info"
    
    # Construct the OData action URL
    $actionUrl = "$Environment/data/SrsFinanceCopilots/Microsoft.Dynamics.DataEntities.RunCopilotReport"
    
    Write-LogMessage "Calling OData action: $actionUrl" -Level "Info"
    
    try {
        # Make the REST call using az rest
        $response = az rest --method POST `
                           --url $actionUrl `
                           --resource $Environment `
                           --body $actionPayload `
                           --headers "Content-Type=application/json" 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-LogMessage "OData action call successful" -Level "Success"
            return $response | ConvertFrom-Json
        } else {
            Write-LogMessage "OData action call failed. Error: $response" -Level "Error"
            return $null
        }
    }
    catch {
        Write-LogMessage "Error calling OData action: $($_.Exception.Message)" -Level "Error"
        return $null
    }
}

function Convert-Base64ToPdf {
    param(
        [string]$Base64Data,
        [string]$InvoiceId,
        [string]$OutputPath
    )
    
    Write-LogMessage "Converting Base64 data to PDF for Invoice: $InvoiceId" -Level "Info"
    
    try {
        # Create output directory if it doesn't exist
        if (!(Test-Path -Path $OutputPath)) {
            New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
            Write-LogMessage "Created output directory: $OutputPath" -Level "Success"
        }
        
        # Generate safe filename
        $safeInvoiceId = Get-SafeFileName -fileName $InvoiceId
        $fileName = "$safeInvoiceId.pdf"
        $fullPath = Join-Path -Path $OutputPath -ChildPath $fileName
        
        # Convert Base64 to bytes and save as PDF
        $pdfBytes = [System.Convert]::FromBase64String($Base64Data)
        [System.IO.File]::WriteAllBytes($fullPath, $pdfBytes)
        
        if (Test-Path -Path $fullPath) {
            $fileInfo = Get-Item -Path $fullPath
            Write-LogMessage "PDF file created successfully!" -Level "Success"
            Write-LogMessage "Location: $fullPath" -Level "Info"
            Write-LogMessage "Size: $([math]::Round($fileInfo.Length / 1KB, 2)) KB" -Level "Info"
            Write-LogMessage "Created: $($fileInfo.CreationTime)" -Level "Info"
            return $fullPath
        } else {
            Write-LogMessage "Failed to create PDF file at: $fullPath" -Level "Error"
            return $null
        }
    }
    catch {
        Write-LogMessage "Error converting Base64 to PDF: $($_.Exception.Message)" -Level "Error"
        return $null
    }
}

function Save-ResponseToJson {
    param(
        [object]$Response,
        [string]$InvoiceId,
        [string]$OutputPath
    )
    
    try {
        $safeInvoiceId = Get-SafeFileName -fileName $InvoiceId
        $jsonFileName = "$safeInvoiceId-response.json"
        $jsonPath = Join-Path -Path $OutputPath -ChildPath $jsonFileName
        
        $Response | ConvertTo-Json -Depth 10 | Out-File -FilePath $jsonPath -Encoding UTF8
        Write-LogMessage "Response saved to: $jsonPath" -Level "Info"
        return $jsonPath
    }
    catch {
        Write-LogMessage "Error saving response to JSON: $($_.Exception.Message)" -Level "Warning"
        return $null
    }
}

# Main execution
Write-LogMessage "=== D365FO Invoice PDF Download Script ===" -Level "Info"
Write-LogMessage "Legal Entity: $LegalEntity" -Level "Info"
Write-LogMessage "Invoice ID: $InvoiceId" -Level "Info"
Write-LogMessage "D365FO Environment: $D365FOEnvironment" -Level "Info"
Write-LogMessage "Output Path: $OutputPath" -Level "Info"

try {
    # Check authentication unless skipped
    if (-not $SkipAuthentication) {
        if (-not (Test-AzureAuthentication)) {
            Write-LogMessage "Azure CLI authentication required" -Level "Warning"
            if (-not (Invoke-AzureAuthentication -Environment $D365FOEnvironment)) {
                Write-LogMessage "Authentication failed. Cannot proceed." -Level "Error"
                exit 1
            }
        }
    } else {
        Write-LogMessage "Skipping authentication check as requested" -Level "Warning"
    }
    
    # Call the D365FO OData action
    Write-LogMessage "Calling D365FO OData action..." -Level "Info"
    $response = Invoke-D365FOAction -Environment $D365FOEnvironment -LegalEntity $LegalEntity -InvoiceId $InvoiceId
    
    if (-not $response) {
        Write-LogMessage "Failed to get response from D365FO. Exiting." -Level "Error"
        exit 1
    }
    
    # Save the full response to JSON for debugging
    Save-ResponseToJson -Response $response -InvoiceId $InvoiceId -OutputPath $OutputPath
    
    # Check if the response contains the expected Base64 data
    if ($response.value) {
        Write-LogMessage "Found Base64 data in response" -Level "Success"
        
        # Convert Base64 to PDF
        $pdfPath = Convert-Base64ToPdf -Base64Data $response.value -InvoiceId $InvoiceId -OutputPath $OutputPath
        
        if ($pdfPath) {
            Write-LogMessage "Invoice PDF download completed successfully!" -Level "Success"
            Write-LogMessage "PDF saved to: $pdfPath" -Level "Success"
            
            # Ask if user wants to open the PDF
            $openPdf = Read-Host "Would you like to open the PDF file? (y/N)"
            if ($openPdf -eq 'y' -or $openPdf -eq 'Y') {
                Start-Process $pdfPath
            }
        } else {
            Write-LogMessage "Failed to create PDF file" -Level "Error"
            exit 1
        }
    } else {
        Write-LogMessage "No Base64 data found in response. Check the response JSON file for details." -Level "Error"
        Write-LogMessage "Response structure:" -Level "Info"
        $response | ConvertTo-Json -Depth 3 | Write-Host
        exit 1
    }
}
catch {
    Write-LogMessage "Unexpected error: $($_.Exception.Message)" -Level "Error"
    Write-LogMessage "Stack trace: $($_.ScriptStackTrace)" -Level "Error"
    exit 1
}

Write-LogMessage "Script execution completed." -Level "Success"