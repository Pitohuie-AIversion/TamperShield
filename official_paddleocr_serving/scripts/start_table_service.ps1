param(
    [string]$HostAddress = "0.0.0.0",
    [int]$Port = 8082,
    [string]$Pipeline = ""
)

# Official PaddleX serving demo for Table Recognition v2.
# The PaddleOCR CLI name is table_recognition_v2, but the PaddleX serving
# pipeline name can vary by installed PaddleX/PaddleOCR version. Do not guess:
# pass -Pipeline with the official pipeline name or an exported YAML config.

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Pipeline)) {
    Write-Error "Pipeline is required. Confirm the official PaddleX pipeline name or export a pipeline YAML, then run: .\scripts\start_table_service.ps1 -Pipeline <official-name-or-yaml-path>"
}

Write-Host "Starting official PaddleX Table Recognition v2 service on $HostAddress`:$Port"
Write-Host "Pipeline: $Pipeline"

paddlex --serve --pipeline $Pipeline --host $HostAddress --port $Port
