param(
    [string]$HostAddress = "0.0.0.0",
    [int]$Port = 8080,
    [string]$Pipeline = "OCR"
)

# Official PaddleX serving demo for the PaddleOCR OCR pipeline.
# Install serving support first:
#   paddlex --install serving

$ErrorActionPreference = "Stop"

Write-Host "Starting official PaddleX OCR service on $HostAddress`:$Port"
Write-Host "Pipeline: $Pipeline"

paddlex --serve --pipeline $Pipeline --host $HostAddress --port $Port
