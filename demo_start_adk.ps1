# RedTeam V9 ADK Demo Start
# Usage: .\demo_start_adk.ps1 [target_url] [session_id]
# Example: .\demo_start_adk.ps1 http://localhost:8080/altoromutual v9_adk_001

Write-Host "=== RedTeam V9 ADK Demo ===" -ForegroundColor Cyan

# Step 1 - Verify V9 MCP is reachable
Write-Host "Checking V9 MCP server..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod "http://10.30.21.5:6019/health" `
        -Headers @{ Authorization = "Bearer Ql1_9GtWuoXZrfcQtgX-wFXGEq_oNf04jeDNwXC-db4" } `
        -TimeoutSec 5
    Write-Host "  MCP: $($health.service) - $($health.tools) tools - OK" -ForegroundColor Green
} catch {
    Write-Host "  MCP server not reachable at 10.30.21.5:6019" -ForegroundColor Red
    Write-Host "  Ask Chirayu to start DEMO_START.ps1 on his machine" -ForegroundColor Red
    exit 1
}

# Step 2 - Verify Azure OpenAI (gpt-5-mini)
Write-Host "Checking Azure OpenAI (gpt-5-mini)..." -ForegroundColor Yellow
$azureTest = python -c @"
import sys
sys.path.insert(0, 'C:/users/chirayu/sandeep_adk')
from orchestrator_agent.env import openai_api_key, openai_api_base, api_version
from openai import AzureOpenAI
client = AzureOpenAI(
    api_key=openai_api_key,
    azure_endpoint=openai_api_base,
    api_version=api_version
)
try:
    r = client.chat.completions.create(
        model='gpt-5-mini',
        messages=[{'role':'user','content':'say hi'}],
        max_completion_tokens=5
    )
    print('Azure gpt-5-mini OK')
except Exception as e:
    print(f'Azure FAILED: {e}')
"@ 2>&1
Write-Host "  $azureTest"
if ($azureTest -like "*FAILED*") {
    Write-Host "  Azure connection failed - check .env" -ForegroundColor Red
    exit 1
}

# Step 3 - Run engagement
$target  = if ($args[0]) { $args[0] } else { "http://localhost:8080/altoromutual" }
$session = if ($args[1]) { $args[1] } else { "v9_adk_$(Get-Date -Format 'yyyyMMdd_HHmmss')" }

Write-Host ""
Write-Host "Starting ADK engagement..." -ForegroundColor Green
Write-Host "  Target:  $target"  -ForegroundColor Cyan
Write-Host "  Session: $session" -ForegroundColor Cyan
Write-Host ""

Set-Location C:\Users\chirayu\sandeep_adk
python start_engagement.py --target $target --session $session
