param(
  [Parameter(Mandatory=$true)]
  [string]$RepoUrl
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  throw "git 명령을 찾을 수 없습니다. Git for Windows를 설치한 뒤 다시 실행해주세요."
}

if (-not (Test-Path -LiteralPath "freshshare_interactive.html")) {
  throw "프로젝트 루트 폴더에서 실행해주세요."
}

if (-not (Test-Path -LiteralPath ".git")) {
  git init
}

git add README.md .gitignore .nojekyll freshshare_interactive.html freshshare_mapping_report.html OCR_BASELINE.md ocr_baseline.py supabase_schema.sql config.example.js data private_data outputs/freshshare_mapping/FreshShare_강의교재_데이터_MCP_매핑.xlsx

$hasChanges = git status --porcelain
if ($hasChanges) {
  git commit -m "feat: add FreshShare prototype dataset mapping"
}

git branch -M main

$remote = git remote
if ($remote -notcontains "origin") {
  git remote add origin $RepoUrl
} else {
  git remote set-url origin $RepoUrl
}

git push -u origin main

Write-Host "GitHub 업로드 완료: $RepoUrl"
