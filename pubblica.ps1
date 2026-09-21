<#
.SYNOPSIS
    Pubblica una nuova versione della traduzione, in un comando solo.

.DESCRIPTION
    Ricostruisce la patch dalla tua copia del gioco, esegue i controlli, prepara
    lo zip, carica le modifiche e crea la Release su GitHub.

    La ricostruzione NON puo' girare su GitHub Actions: costruisci.py legge
    Data/messages.dat dal gioco, che non sta nel repository. Per questo il
    passaggio finale si fa da qui.

    Prima di caricare qualsiasi cosa chiede conferma.

.PARAMETER Versione
    Numero di versione, per esempio 1.2

.PARAMETER Note
    File markdown con le note di rilascio. Se manca, ne genera di minime.

.PARAMETER SoloLocale
    Si ferma dopo lo zip, senza toccare GitHub.

.EXAMPLE
    .\pubblica.ps1 -Versione 1.2
    .\pubblica.ps1 -Versione 1.2 -Note note.md
    .\pubblica.ps1 -Versione 1.2 -SoloLocale
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Versione,
    [string]$Note,
    [switch]$SoloLocale
)

$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

function Passo($n, $testo) {
    Write-Host ''
    Write-Host "[$n] $testo" -ForegroundColor Cyan
}

function Fermati($testo) {
    Write-Host ''
    Write-Host $testo -ForegroundColor Red
    exit 1
}

if ($Versione -notmatch '^\d+\.\d+(\.\d+)?$') {
    Fermati "Versione non valida: '$Versione'. Attesa nella forma 1.2 o 1.2.3"
}
$tag = "v$Versione"

if (git tag --list $tag) {
    Fermati "Il tag $tag esiste gia'. Scegli un altro numero di versione."
}

# --- 1. ricostruzione --------------------------------------------------------
Passo 1 'Ricostruisco la patch dalla tua copia del gioco'
python strumenti/costruisci.py
if ($LASTEXITCODE -ne 0) { Fermati 'La ricostruzione e'' fallita.' }

# --- 2. controlli ------------------------------------------------------------
Passo 2 'Controlli sul contenuto e sul formato'
python strumenti/verifica_repo.py
if ($LASTEXITCODE -ne 0) { Fermati 'I controlli sul repository hanno trovato problemi.' }
python strumenti/test_formato.py
if ($LASTEXITCODE -ne 0) { Fermati 'Le prove sul formato sono fallite.' }

# --- 3. pacchetto ------------------------------------------------------------
Passo 3 'Preparo il pacchetto'
& "$PSScriptRoot\crea_pacchetto.ps1" -Versione $Versione
$zip = "rejuvenation-ita-patch-v$Versione.zip"
if (-not (Test-Path $zip)) { Fermati 'Il pacchetto non e'' stato creato.' }

if ($SoloLocale) {
    Write-Host ''
    Write-Host "Pronto in locale: $zip" -ForegroundColor Green
    Write-Host 'Niente e'' stato caricato su GitHub.'
    exit 0
}

# --- 4. conferma prima di uscire allo scoperto -------------------------------
$daCaricare = git status --porcelain -- dati/ patch/Init patch/Mods
Write-Host ''
Write-Host 'Sto per pubblicare:' -ForegroundColor Yellow
Write-Host "  tag      : $tag"
Write-Host "  pacchetto: $zip ($([math]::Round((Get-Item $zip).Length/1MB,1)) MB)"
if ($daCaricare) {
    Write-Host '  modifiche da caricare:'
    $daCaricare | ForEach-Object { Write-Host "     $_" }
} else {
    Write-Host '  nessuna modifica da caricare, solo la Release'
}
Write-Host ''
Write-Host 'Una Release pubblica e'' visibile a tutti e difficile da ritirare.'
$risposta = Read-Host 'Procedo? (scrivi si per confermare)'
if ($risposta -notin @('si', 'sì', 's', 'yes', 'y')) {
    Write-Host 'Annullato. Il pacchetto resta pronto in locale.' -ForegroundColor Yellow
    exit 0
}

# --- 5. carico ---------------------------------------------------------------
if ($daCaricare) {
    Passo 5 'Carico le modifiche'
    git add dati/ patch/Init patch/Mods
    git commit -m "Traduzione aggiornata per la $tag"
    git push origin main
}

# --- 6. release --------------------------------------------------------------
Passo 6 'Creo la Release'
if ($Note -and (Test-Path $Note)) {
    gh release create $tag $zip --title "$tag" --notes-file $Note
} else {
    $auto = "Aggiornamento della traduzione italiana di Pokemon Rejuvenation.`n`n" +
            "Estrai lo zip ed esegui ``installa.ps1`` su Windows, oppure copia la " +
            "cartella ``patch`` nella cartella del gioco su Android, iOS, Linux e macOS.`n`n" +
            "Poi: **Language -> Italiano** dal menu principale.`n`n" +
            "Se avevi gia' una versione precedente, sovrascrivi i tre file: " +
            "i salvataggi non vengono toccati."
    gh release create $tag $zip --title "$tag" --notes $auto
}
if ($LASTEXITCODE -ne 0) { Fermati 'La creazione della Release e'' fallita.' }

Write-Host ''
Write-Host "Pubblicata: $tag" -ForegroundColor Green
gh release view $tag --json url --jq '.url'
Write-Host ''
