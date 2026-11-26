param(
    [ValidateSet('debug', 'release')] [string] $Variant = 'debug',
    [switch] $NoPayload,
    [switch] $KeepDebs,
    [switch] $Install,
    [string] $TransportId = '',
    [string] $Serial = ''
)

# Local Windows build wrapper. Keeps the machine-specific paths in one place;
# the repository's build_apk.sh remains the source of truth for the build.
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$bash = 'C:\Program Files\Git\bin\bash.exe'
$androidHome = 'C:\Users\Matt\AppData\Local\Android\Sdk'
$jdk = 'C:\PROGRA~1\Android\ANDROI~1\jbr'

$drive = $repo.Substring(0, 1).ToLowerInvariant()
$rest = $repo.Substring(3).Replace('\', '/')
$bashRepo = "/$drive/$rest"

$env:ANDROID_HOME = $androidHome
$env:NX2A_JDK = $jdk
# All worktrees share the main checkout's downloaded toolchain/payload cache.
$gitCommon = & git -C $repo rev-parse --git-common-dir
$mainRepo = (Resolve-Path (Join-Path $gitCommon '..')).Path
$cacheRoot = Join-Path $mainRepo 'packaging\android-apk\.cache'
$env:NX2A_CACHE = $cacheRoot
$env:NX2A_CSHARP_PREBUILT = Join-Path $cacheRoot 'csharp-tools'
$env:NX2A_ADRENOTOOLS_PREBUILT = Join-Path $cacheRoot 'adrenotools-prebuilt'
Remove-Item Env:DOTNET -ErrorAction SilentlyContinue  # source build of dmsh_xlate fails on this fork

$debs = Join-Path $cacheRoot 'debs'
if (-not $NoPayload -and -not $KeepDebs) {
    # Windows tar_filter still trips over stale POSIX symlinks on a second run.
    Remove-Item -Recurse -Force $debs -ErrorAction SilentlyContinue
}

$extra = if ($NoPayload) { '--no-payload' } else { '' }
& $bash -lc "cd '$bashRepo' && bash packaging/android-apk/build_apk.sh $Variant $extra"
if ($LASTEXITCODE -ne 0) { throw "build_apk.sh failed with exit $LASTEXITCODE" }

$apk = Get-ChildItem (Join-Path $repo "android\app\build\outputs\apk\$Variant") -Filter *.apk |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $apk) { throw "no APK in android/app/build/outputs/apk/$Variant" }
Write-Host "APK: $($apk.FullName)"

if ($Install) {
    $adb = Join-Path $androidHome 'platform-tools\adb.exe'
    $adbArgs = @()
    if ($TransportId) { $adbArgs += @('-t', $TransportId) }
    elseif ($Serial) { $adbArgs += @('-s', $Serial) }
    & $adb @adbArgs install -r $apk.FullName
    if ($LASTEXITCODE -ne 0) { throw "adb install failed with exit $LASTEXITCODE" }
}
