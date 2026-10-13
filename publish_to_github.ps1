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

# 1. Read GITHUB_TOKEN from environment, project .env, or ~/.env
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

Write-Host "Uploading updated 3D examples, images, and animations to https://github.com/$Owner/$RepoName ..." -ForegroundColor Cyan

$FilesToUpload = @(
    "README.md",
    "index.html",
    "assets/argon_sunlit_study.png",
    "assets/argon_3d_live_animation.svg",
    "examples/05_interactive_3d_studio.html",
    "examples/07_multimodal_image_video_to_3d.py",
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
        message = "feat(3d): add live 3D studio, raytraced render, and multimodal image/video-to-3D ($RelPath)"
        content = $Base64Content
        branch  = $Branch
    }
    if ($Sha) {
        $PutBodyHash["sha"] = $Sha
    }

    $PutBody = $PutBodyHash | ConvertTo-Json
    $null = Invoke-RestMethod -Uri $ApiUrl -Method Put -Headers $Headers -Body $PutBody -ContentType "application/json" -TimeoutSec 25
    Write-Host "  [OK] Uploaded $RelPath" -ForegroundColor Green
}

# Enable GitHub Pages on main branch root (/) so index.html is live!
try {
    $PagesBody = @{
        source = @{
            branch = $Branch
            path   = "/"
        }
    } | ConvertTo-Json
    $null = Invoke-RestMethod -Uri "https://api.github.com/repos/$Owner/$RepoName/pages" -Method Post -Headers $Headers -Body $PagesBody -ContentType "application/json" -TimeoutSec 15
    Write-Host "  [OK] Enabled GitHub Pages: https://robinamirbahar.github.io/$RepoName/" -ForegroundColor Green
} catch {
    Write-Host "  [INFO] GitHub Pages already enabled or initializing: https://robinamirbahar.github.io/$RepoName/" -ForegroundColor Yellow
}

# Update repository homepage URL to the live 3D Studio on GitHub Pages
try {
    $RepoPatch = @{
        homepage = "https://robinamirbahar.github.io/$RepoName/"
    } | ConvertTo-Json
    $null = Invoke-RestMethod -Uri "https://api.github.com/repos/$Owner/$RepoName" -Method Patch -Headers $Headers -Body $RepoPatch -ContentType "application/json" -TimeoutSec 15
} catch {}

Write-Host "`nSuccessfully updated: https://github.com/$Owner/$RepoName" -ForegroundColor Cyan
Write-Host "Live 3D WebGL Studio: https://robinamirbahar.github.io/$RepoName/" -ForegroundColor Cyan
