param(
  [string]$WheelDir = "$(Split-Path -Parent $PSScriptRoot)\wheels"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$req1 = Join-Path $repoRoot "requirement.txt"
$req2 = Join-Path $repoRoot "requirements.txt"

Write-Host "Wheel output: $WheelDir"
New-Item -ItemType Directory -Force -Path $WheelDir | Out-Null

if (!(Test-Path $req1)) { throw "Missing $req1" }

Write-Host "Preparing pip toolchain..."
python -m pip install --upgrade pip wheel

Write-Host "Downloading wheels (requires Internet)..."

if (Test-Path $req2) {
  python -m pip wheel --wheel-dir $WheelDir -r $req1 -r $req2
} else {
  python -m pip wheel --wheel-dir $WheelDir -r $req1
}

Write-Host "Done. Wheels are in: $WheelDir"

