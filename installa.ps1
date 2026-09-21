<#
.SYNOPSIS
    Installa la traduzione italiana di Pokemon Rejuvenation.

.DESCRIPTION
    Copia la cartella patch dentro la cartella del gioco. Non tocca nessun file
    originale: la traduzione vive interamente dentro patch, e per tornare
    all'inglese basta scegliere English nel menu del gioco.

.PARAMETER Gioco
    Cartella di Rejuvenation. Se non la indichi, viene cercata da sola.

.PARAMETER Rimuovi
    Disinstalla la traduzione invece di installarla.

.EXAMPLE
    .\installa.ps1
    .\installa.ps1 -Gioco "D:\Giochi\Rejuvenation"
    .\installa.ps1 -Rimuovi
#>

[CmdletBinding()]
param(
    [string]$Gioco,
    [switch]$Rimuovi
)

$ErrorActionPreference = 'Stop'
$Sorgente = Join-Path $PSScriptRoot 'patch'

function Scrivi-Titolo($testo) {
    Write-Host ''
    Write-Host $testo -ForegroundColor Cyan
    Write-Host ('-' * $testo.Length) -ForegroundColor DarkCyan
}

function Test-CartellaGioco($percorso) {
    if ([string]::IsNullOrWhiteSpace($percorso)) { return $false }
    return Test-Path (Join-Path $percorso 'Data\messages.dat')
}

function Trova-Gioco {
    $candidate = @(
        "$env:USERPROFILE\Desktop\Rejuvenation",
        "$env:USERPROFILE\Downloads\Rejuvenation",
        "$env:USERPROFILE\Documents\Rejuvenation",
        'C:\Rejuvenation',
        'C:\Giochi\Rejuvenation',
        'C:\Games\Rejuvenation',
        'D:\Rejuvenation',
        'D:\Giochi\Rejuvenation',
        'D:\Games\Rejuvenation'
    )
    foreach ($c in $candidate) {
        if (Test-CartellaGioco $c) { return $c }
    }
    return $null
}

Scrivi-Titolo 'Traduzione italiana di Pokemon Rejuvenation'

# --- individua la cartella del gioco ----------------------------------------
if (-not $Gioco) { $Gioco = Trova-Gioco }

while (-not (Test-CartellaGioco $Gioco)) {
    if ($Gioco) {
        Write-Host ''
        Write-Host "In $Gioco non trovo Data\messages.dat." -ForegroundColor Yellow
        Write-Host 'Non sembra la cartella giusta.'
    }
    Write-Host ''
    Write-Host 'Indica la cartella di Rejuvenation: quella che contiene'
    Write-Host 'Data, Graphics e Rejuvenation.exe.'
    Write-Host 'Puoi trascinarci dentro la cartella e premere Invio.'
    Write-Host ''
    $Gioco = (Read-Host 'Cartella').Trim().Trim('"')
    if (-not $Gioco) {
        Write-Host 'Annullato.' -ForegroundColor Yellow
        exit 1
    }
}

$Gioco = (Resolve-Path $Gioco).Path
Write-Host ''
Write-Host "Gioco trovato: $Gioco" -ForegroundColor Green

$Destinazione = Join-Path $Gioco 'patch'

# --- disinstallazione --------------------------------------------------------
if ($Rimuovi) {
    Scrivi-Titolo 'Rimozione'
    $daTogliere = @(
        (Join-Path $Destinazione 'italiano.dat'),
        (Join-Path $Destinazione 'Init\intl.rb'),
        (Join-Path $Destinazione 'Mods\intl.rb')
    )
    $tolti = 0
    foreach ($f in $daTogliere) {
        if (Test-Path $f) { Remove-Item $f -Force; $tolti++; Write-Host "  rimosso $f" }
    }
    # le cartelle si cancellano solo se restano vuote: potrebbero esserci altre mod
    foreach ($d in @((Join-Path $Destinazione 'Init'), (Join-Path $Destinazione 'Mods'))) {
        if ((Test-Path $d) -and -not (Get-ChildItem $d -Force)) { Remove-Item $d -Force }
    }
    Write-Host ''
    if ($tolti -gt 0) {
        Write-Host 'Traduzione rimossa. Il gioco torna in inglese al prossimo avvio.' -ForegroundColor Green
    } else {
        Write-Host 'Non era installata: non ho trovato nulla da rimuovere.' -ForegroundColor Yellow
    }
    Write-Host ''
    exit 0
}

# --- installazione -----------------------------------------------------------
if (-not (Test-Path $Sorgente)) {
    Write-Host ''
    Write-Host "Non trovo la cartella patch accanto a questo script." -ForegroundColor Red
    Write-Host 'Estrai tutto il contenuto dello zip nella stessa cartella e riprova.'
    Write-Host ''
    exit 1
}

Scrivi-Titolo 'Installazione'

# Copia senza cancellare: chi ha altre mod in patch se le tiene.
New-Item -ItemType Directory -Force -Path $Destinazione | Out-Null
Copy-Item (Join-Path $Sorgente '*') -Destination $Destinazione -Recurse -Force

$attesi = @('italiano.dat', 'Init\intl.rb', 'Mods\intl.rb')
$mancanti = @()
foreach ($f in $attesi) {
    $p = Join-Path $Destinazione $f
    if (Test-Path $p) {
        $kb = [math]::Round((Get-Item $p).Length / 1KB)
        Write-Host ("  installato  {0,-16} {1} KB" -f $f, $kb)
    } else {
        $mancanti += $f
    }
}

Write-Host ''
if ($mancanti.Count -gt 0) {
    Write-Host 'Installazione incompleta, mancano:' -ForegroundColor Red
    $mancanti | ForEach-Object { Write-Host "  $_" }
    Write-Host ''
    exit 1
}

Write-Host 'Fatto.' -ForegroundColor Green
Write-Host ''
Write-Host 'Ora avvia Rejuvenation e dal menu principale scegli:' -ForegroundColor White
Write-Host '    Language  ->  Italiano' -ForegroundColor Cyan
Write-Host ''
Write-Host 'La voce Language compare in fondo al menu, sotto Controls.'
Write-Host 'Per tornare all inglese ti basta riselezionare English.'
Write-Host ''
