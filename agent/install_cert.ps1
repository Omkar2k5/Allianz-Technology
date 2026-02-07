$certPath = Join-Path $PSScriptRoot "ca_cert.pem"

if (-not (Test-Path $certPath)) {
    # Check if we are in src or parent
    $certPath = Join-Path $PSScriptRoot "target\release\ca_cert.pem"
}

if (Test-Path $certPath) {
    Write-Host "📜 Found certificate at: $certPath"
    
    # Remove old certificates to prevent conflicts
    Write-Host "🧹 Cleaning up old certificates..."
    Get-ChildItem Cert:\CurrentUser\Root | Where-Object { $_.Subject -like "*Eco-Compute*" } | ForEach-Object {
        Write-Host "   - Removing old cert: $($_.Thumbprint)"
        Remove-Item "Cert:\CurrentUser\Root\$($_.Thumbprint)" -Force -ErrorAction SilentlyContinue
    }

    Write-Host "🔐 Installing CA Certificate to Trusted Root Store..."
    try {
        Import-Certificate -FilePath $certPath -CertStoreLocation Cert:\CurrentUser\Root
        Write-Host "✅ Certificate installed successfully!"
        Write-Host "⚠️  You may get a Windows security popup asking to confirm the installation. Please click 'Yes'."
        Write-Host "🔄 Please restart your browser (Chrome/Edge) completely for changes to take effect."
    } catch {
        Write-Error "❌ Failed to install certificate: $_"
    }
} else {
    Write-Host "❌ ca_cert.pem not found. Please run the agent first to generate it."
}
