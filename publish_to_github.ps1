<#
.SYNOPSIS
    Publishes the Gemini 4 Argon Cookbook directly to https://github.com/RobinaMirbahar/gemini-4-argon-cookbook
    and enables GitHub Pages for the Live 3D Studio.
#>

param(
    [string]$RepoName = "gemini-4-argon-cookbook",
    [string]$Owner = "RobinaMirbahar",
    [string]$Branch = "main"
)

$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$Token = $env:GITHUB_TOKEN
foreach ($EnvFile in @("$PSScriptRoot\.env", "$HOME\.env")) {
    if (-not $Token -and (Test-Path $EnvFile)) {
        @(Get-Content $EnvFile) | ForEach-Object {
            if ($_ -match "^\s*GITHUB_TOKEN\s*=\s*(.+)\s*$") {
                $Candidate = $Matches[1].Trim('"', "'", " ")
                if ($Candidate.Length -gt 5) {
                    $Token = $Candidate
                }
            }
        }
    }
}

if (-not $Token) {
    Write-Host "[ERROR] GITHUB_TOKEN is empty." -ForegroundColor Red
    exit 1
}

$Headers = @{
    "Authorization"        = "Bearer $Token"
    "Accept"               = "application/vnd.github+json"
    "User-Agent"           = "gemini-4-argon-cookbook-publisher"
    "X-GitHub-Api-Version" = "2022-11-28"
}

Write-Host "Uploading built-from-scratch 3D examples and renders to https://github.com/$Owner/$RepoName ..." -ForegroundColor Cyan

Remove-Item -Path (Join-Path $PSScriptRoot "assets\ai_leaders_fellowship.png") -Force -ErrorAction SilentlyContinue
try {
    $OldUrl = "https://api.github.com/repos/$Owner/$RepoName/contents/assets/ai_leaders_fellowship.png"
    $OldFile = Invoke-RestMethod -Uri ("$OldUrl" + "?ref=$Branch") -Method Get -Headers $Headers -TimeoutSec 15
    $DelBody = @{
        message = "chore: remove personal photo from repository"
        sha     = $OldFile.sha
        branch  = $Branch
    } | ConvertTo-Json
    $null = Invoke-RestMethod -Uri $OldUrl -Method Delete -Headers $Headers -Body $DelBody -ContentType "application/json" -TimeoutSec 15
    Write-Host "  [OK] Removed assets/ai_leaders_fellowship.png from GitHub" -ForegroundColor Yellow
} catch {}

$FilesToUpload = @(
    "README.md",
    "index.html",
    "assets/robina_gemini_4_argon_infographic.jpg",
    "assets/argon_3d_pagoda_temple.png",
    "assets/argon_3d_shatter_physics.png",
    "assets/argon_3d_robotics_ik.png",
    "examples/08_procedural_3d_pagoda_temple.py",
    "examples/09_3d_physics_shatter_arena.html",
    "examples/10_3d_robotics_ik_simulator.html",
    "publish_to_github.ps1"
)

foreach ($RelPath in $FilesToUpload) {
    $FullPath = Join-Path $PSScriptRoot ($RelPath -replace "/", "\")
    if (-not (Test-Path $FullPath)) { continue }

    $Bytes = [System.IO.File]::ReadAllBytes($FullPath)
    $Base64Content = [Convert]::ToBase64String($Bytes)
    $ApiUrl = "https://api.github.com/repos/$Owner/$RepoName/contents/$RelPath"

    $Sha = $null
    try {
        $Existing = Invoke-RestMethod -Uri ("$ApiUrl" + "?ref=$Branch") -Method Get -Headers $Headers -TimeoutSec 15
        $Sha = $Existing.sha
    } catch {}

    $PutBodyHash = @{
        message = "feat(3d): add built-from-scratch 3D examples, renders, and WebGL arenas ($RelPath)"
        content = $Base64Content
        branch  = $Branch
    }
    if ($Sha) {
        $PutBodyHash["sha"] = $Sha
    }

    $PutBody = $PutBodyHash | ConvertTo-Json
    $null = Invoke-RestMethod -Uri $ApiUrl -Method Put -Headers $Headers -Body $PutBody -ContentType "application/json" -TimeoutSec 30
    Write-Host "  [OK] Uploaded $RelPath" -ForegroundColor Green
}

Write-Host "`nSuccessfully updated: https://github.com/$Owner/$RepoName" -ForegroundColor Cyan
Write-Host "Live 3D WebGL Studio: https://robinamirbahar.github.io/$RepoName/" -ForegroundColor Cyan
