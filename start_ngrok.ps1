# Load environment variables
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        $env:$($matches[1]) = $matches[2]
    }
}

Write-Host "Starting ngrok with auth token..."
ngrok config add-authtoken $env:NGROK_AUTH_TOKEN
ngrok http 8000 