$ErrorActionPreference = "Stop"

$payloadPath = Join-Path $PSScriptRoot "gradle-wrapper.jar.base64"
$wrapperPath = Join-Path $PSScriptRoot "gradle-wrapper.jar"
$encoded = (Get-Content -Raw -LiteralPath $payloadPath) -replace '\s', ''
$bytes = [Convert]::FromBase64String($encoded)
[IO.File]::WriteAllBytes($wrapperPath, $bytes)

$expected = "81a82aaea5abcc8ff68b3dfcb58b3c3c429378efd98e7433460610fecd7ae45f"
$sha256 = [System.Security.Cryptography.SHA256]::Create()
try {
    $actual = [BitConverter]::ToString(
        $sha256.ComputeHash([IO.File]::ReadAllBytes($wrapperPath))
    ).Replace("-", "").ToLowerInvariant()
}
finally {
    $sha256.Dispose()
}

if ($actual -ne $expected) {
    throw "Gradle wrapper JAR checksum mismatch."
}
