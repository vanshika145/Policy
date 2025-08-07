@echo off
echo Starting ngrok with auth token...
ngrok config add-authtoken %NGROK_AUTH_TOKEN%
ngrok http 8000 