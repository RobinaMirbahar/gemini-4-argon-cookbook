<#
.SYNOPSIS
    Publishes the Gemini 4 Argon Cookbook directly to https://github.com/RobinaMirbahar/gemini-4-argon-cookbook
    using the GitHub REST API (no local Git installation required).
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

# 2. Fallback: Check if a GitHub token (ghp_... or github_pat_...) is currently on the Windows Clipboard
if (-not $Token) {
    try {
        $Clip = (Get-Clipboard -ErrorAction SilentlyContinue | Out-String).Trim()
        if ($Clip -match "^(ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+)$") {
            $Token = $Clip
        }
    } catch {}
}

if (-not $Token) {
    Write-Host "[ERROR] GITHUB_TOKEN is empty." -ForegroundColor Red
    Write-Host "Please either:"
    Write-Host "  1. Open .env in the editor, paste your ghp_... token after GITHUB_TOKEN=, and save (Ctrl+S), OR"
    Write-Host "  2. Copy your ghp_... token to your clipboard (Ctrl+C) and re-run this script."
    exit 1
}

$Headers = @{
    "Authorization"        = "Bearer $Token"
    "Accept"               = "application/vnd.github+json"
    "User-Agent"           = "gemini-4-argon-cookbook-publisher"
    "X-GitHub-Api-Version" = "2022-11-28"
}

Write-Host "Creating or verifying repository https://github.com/$Owner/$RepoName ..." -ForegroundColor Cyan
try {
    $null = Invoke-RestMethod -Uri "https://api.github.com/repos/$Owner/$RepoName" -Method Get -Headers $Headers -TimeoutSec 20
    Write-Host "Repository $Owner/$RepoName already exists. Updating files..." -ForegroundColor Yellow
} catch {
    $CreateBody = @{
        name        = $RepoName
        description = "Gemini 4 Argon Cookbook & Starter Kit - 1M Unified Token Long-Decode Continuation, Deep Reasoning Thought Signatures, Autonomous Cyber/Code Auditor, and Pure-Python 3D Raytracer"
        homepage    = "https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-argon/"
        private     = $false
        auto_init   = $true
    } | ConvertTo-Json
    $null = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method Post -Headers $Headers -Body $CreateBody -ContentType "application/json" -TimeoutSec 20
    Write-Host "Created public repository: https://github.com/$Owner/$RepoName" -ForegroundColor Green
    Start-Sleep -Seconds 2
}

# Set repository topics
$TopicsBody = @{
    names = @("gemini", "gemini-4-argon", "google-deepmind", "interactions-api", "ai-agents", "google-antigravity", "raytracer")
} | ConvertTo-Json
try {
    $null = Invoke-RestMethod -Uri "https://api.github.com/repos/$Owner/$RepoName/topics" -Method Put -Headers $Headers -Body $TopicsBody -ContentType "application/json" -TimeoutSec 15
} catch {}

# Upload all project files via GitHub Contents API
$FilesToUpload = @(
    "README.md",
    "LICENSE",
    ".gitignore",
    ".env.example",
    "requirements.txt",
    "package.json",
    "SOCIAL_POSTS.md",
    "publish_to_github.ps1",
    "examples/01_long_decode_continuation.py",
    "examples/01_long_decode_continuation.ts",
    "examples/02_deep_reasoning_thoughts.py",
    "examples/03_security_code_auditor.py",
    "examples/04_vanilla_3d_raytracer.py",
    "examples/05_interactive_3d_studio.html",
    "examples/06_enterprise_research_workflow.py"
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
        message = "feat: add $RelPath for Gemini 4 Argon Cookbook"
        content = $Base64Content
        branch  = $Branch
    }
    if ($Sha) {
        $PutBodyHash["sha"] = $Sha
    }

    $PutBody = $PutBodyHash | ConvertTo-Json
    $null = Invoke-RestMethod -Uri $ApiUrl -Method Put -Headers $Headers -Body $PutBody -ContentType "application/json" -TimeoutSec 20
    Write-Host "  [OK] Uploaded $RelPath" -ForegroundColor Green
}

Write-Host "`nSuccessfully published to: https://github.com/$Owner/$RepoName" -ForegroundColor Cyan
