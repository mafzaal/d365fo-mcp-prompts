param(
    [Parameter(Mandatory=$false)]
    [string]$JsonFilePath = ".\Reports\a.json",
    
    [Parameter(Mandatory=$false)]
    [string]$OutputPath = ".\Reports"
)

function Get-SafeFileName {
    param([string]$fileName)
    $invalidChars = [IO.Path]::GetInvalidFileNameChars() -join ''
    $pattern = "[$([regex]::Escape($invalidChars))]"
    return $fileName -replace $pattern, '_'
}

try {
    if (!(Test-Path -Path $JsonFilePath)) {
        Write-Error "JSON file not found: $JsonFilePath"
        return
    }
    
    Write-Host "Reading JSON file: $JsonFilePath" -ForegroundColor Yellow
    $jsonContent = Get-Content -Path $JsonFilePath -Raw | ConvertFrom-Json
    
    if (-not $jsonContent.result.value) {
        Write-Error "No 'value' field found in the JSON result"
        return
    }
    $Base64String = $jsonContent.result.value
    
    $InvoiceId = "default"
    if ($jsonContent.parameters._controllerArgsJson) {
        try {
            $controllerArgs = $jsonContent.parameters._controllerArgsJson | ConvertFrom-Json
            if ($controllerArgs.DataTableFieldValue) {
                $InvoiceId = $controllerArgs.DataTableFieldValue
            }
        }
        catch {
            Write-Warning "Could not parse controller args, using default filename"
        }
    }
    
    Write-Host "Found Base64 data for Invoice: $InvoiceId" -ForegroundColor Green
    
    if (!(Test-Path -Path $OutputPath)) {
        New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
        Write-Host "Created output directory: $OutputPath" -ForegroundColor Green
    }
    
    $safeInvoiceId = Get-SafeFileName -fileName $InvoiceId
    $fileName = "$safeInvoiceId.pdf"
    $fullPath = Join-Path -Path $OutputPath -ChildPath $fileName
    
    Write-Host "Converting base64 string to PDF..." -ForegroundColor Yellow
    $pdfBytes = [System.Convert]::FromBase64String($Base64String)
    [System.IO.File]::WriteAllBytes($fullPath, $pdfBytes)
    
    if (Test-Path -Path $fullPath) {
        $fileInfo = Get-Item -Path $fullPath
        Write-Host "PDF file created successfully!" -ForegroundColor Green
        Write-Host "Location: $fullPath" -ForegroundColor Cyan
        Write-Host "Size: $([math]::Round($fileInfo.Length / 1KB, 2)) KB" -ForegroundColor Cyan
        Write-Host "Created: $($fileInfo.CreationTime)" -ForegroundColor Cyan
    } else {
        Write-Error "Failed to create PDF file at: $fullPath"
    }
}
catch {
    Write-Error "Error: $($_.Exception.Message)"
}