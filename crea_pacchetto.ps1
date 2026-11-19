<#
.SYNOPSIS
    Confeziona lo zip da allegare a una Release.

.DESCRIPTION
    Mette insieme la cartella patch, l'installer e la documentazione essenziale.
    Va lanciato dopo costruisci.py, che genera patch/italiano.dat.

    Il pacchetto NON contiene file del gioco: solo la traduzione e gli script.

.EXAMPLE
    .\crea_pacchetto.ps1
    .\crea_pacchetto.ps1 -Versione 1.1
#>

[CmdletBinding()]
param(
    [string]$Versione = '1.0'
)

$ErrorActionPreference = 'Stop'
$Radice = $PSScriptRoot
$Dat = Join-Path $Radice 'patch\italiano.dat'

if (-not (Test-Path $Dat)) {
    Write-Host ''
    Write-Host 'Manca patch\italiano.dat.' -ForegroundColor Red
    Write-Host 'Generalo prima con:' -ForegroundColor White
    Write-Host '    cd strumenti' -ForegroundColor Cyan
    Write-Host '    python costruisci.py' -ForegroundColor Cyan
    Write-Host ''
    exit 1
}

$Nome = "rejuvenation-ita-patch-v$Versione"
$Staging = Join-Path $env:TEMP $Nome
$Zip = Join-Path $Radice "$Nome.zip"

if (Test-Path $Staging) { Remove-Item $Staging -Recurse -Force }
New-Item -ItemType Directory -Path $Staging | Out-Null

Copy-Item (Join-Path $Radice 'patch') -Destination $Staging -Recurse
foreach ($f in @('installa.ps1', 'README.md', 'NOTICE.md', 'LICENSE')) {
    Copy-Item (Join-Path $Radice $f) -Destination $Staging
}
New-Item -ItemType Directory -Path (Join-Path $Staging 'docs') | Out-Null
Copy-Item (Join-Path $Radice 'docs\INSTALLAZIONE.md') -Destination (Join-Path $Staging 'docs')

if (Test-Path $Zip) { Remove-Item $Zip -Force }
Compress-Archive -Path (Join-Path $Staging '*') -DestinationPath $Zip -CompressionLevel Optimal
Remove-Item $Staging -Recurse -Force

# SHA256SUMS.txt accanto allo zip: chi scarica puo' controllare che sia quello originale.
$Somme = Join-Path $Radice 'SHA256SUMS.txt'
'{0}  {1}' -f (Get-FileHash $Zip -Algorithm SHA256).Hash.ToLowerInvariant(), (Split-Path $Zip -Leaf) |
    Set-Content -Path $Somme -Encoding ascii

$mb = [math]::Round((Get-Item $Zip).Length / 1MB, 1)
Write-Host ''
Write-Host "Pacchetto pronto: $Zip  ($mb MB)" -ForegroundColor Green
Get-Content $Somme
Write-Host ''
Write-Host 'Per pubblicarlo:' -ForegroundColor White
Write-Host "    gh release create v$Versione `"$Zip`" `"$Somme`" --title `"v$Versione`" --notes-file NOTE_RELEASE.md" -ForegroundColor Cyan
Write-Host ''
