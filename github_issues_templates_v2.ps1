# Helper functions for consistent GitHub issue templates in dhii-mail

function New-DhiiCodeIssue {
  param(
    [Parameter(Mandatory=$true)][string]$Title,
    [Parameter(Mandatory=$true)][string[]]$Labels,
    [Parameter(Mandatory=$true)][string]$Problem,
    [Parameter(Mandatory=$true)][string]$Impact,
    [Parameter(Mandatory=$true)][string]$ProposedFix,
    [Parameter(Mandatory=$false)][string[]]$AffectedFiles = @(),
    [Parameter(Mandatory=$false)][string[]]$Tasks = @(),
    [Parameter(Mandatory=$false)][string[]]$VerificationHints = @()
  )

  $bodyLines = @()
  $bodyLines += "### Summary"
  $bodyLines += $Problem
  $bodyLines += ""

  $bodyLines += "### Impact"
  $bodyLines += $Impact
  $bodyLines += ""

  if ($AffectedFiles.Count -gt 0) {
    $bodyLines += "### Affected files"
    foreach ($f in $AffectedFiles) {
      $bodyLines += "- `$f`"
    }
    $bodyLines += ""
  }

  $bodyLines += "### Proposed direction"
  $bodyLines += $ProposedFix
  $bodyLines += ""

  if ($Tasks.Count -gt 0) {
    $bodyLines += "### Tasks"
    foreach ($t in $Tasks) {
      $bodyLines += "- [ ] $t"
    }
    $bodyLines += ""
  }

  if ($VerificationHints.Count -gt 0) {
    $bodyLines += "### Verification (for automation)"
    foreach ($v in $VerificationHints) {
      $bodyLines += "- [ ] $v"
    }
    $bodyLines += ""
  }

  $body = ($bodyLines -join "`n")

  $labelArgs = @()
  foreach ($l in $Labels) {
    $labelArgs += @('--label', $l)
  }

  $tmp = [System.IO.Path]::GetTempFileName()
  Set-Content -Path $tmp -Value $body -Encoding UTF8

  Write-Host "Creating issue: $Title" -ForegroundColor Cyan
  gh issue create --title $Title @labelArgs --body-file $tmp

  Remove-Item $tmp -ErrorAction SilentlyContinue
}

Export-ModuleMember -Function New-DhiiCodeIssue
