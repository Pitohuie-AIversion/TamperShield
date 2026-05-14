param(
    [string]$HostAddress = "0.0.0.0",
    [int]$Port = 8081,
    [string]$Pipeline = "PP-StructureV3"
)

# Official PaddleX serving demo for PP-StructureV3.
# If your installed PaddleX reports a different pipeline name, pass:
#   .\scripts\start_ppstructure_service.ps1 -Pipeline <official-name-or-yaml-path>

$ErrorActionPreference = "Stop"

Write-Host "Starting official PaddleX PP-StructureV3 service on $HostAddress`:$Port"
Write-Host "Pipeline: $Pipeline"
Write-Host "If startup fails because the pipeline name is unknown, export the official PaddleX pipeline config to YAML and pass the YAML path as -Pipeline."

paddlex --serve --pipeline $Pipeline --host $HostAddress --port $Port
