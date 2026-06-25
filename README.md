# RedTeam V9 ADK — Autonomous Penetration Testing Agents

Google ADK 2.3.0 multi-agent system for autonomous web
application penetration testing. Connects to the RedTeam V9
MCP server which provides 35 security testing tools.

## Architecture

```
orchestrator_agent
  ├── planner_agent     (Bayesian MCTS branch scoring)
  ├── executor_agent    (attack tool execution)
  └── reflector_agent   (quality gate + phase decisions)
```

All agents connect to V9 MCP via StreamableHTTP.
The MCP server enforces intent-based access control —
agents can only call tools they are authorised for.

## What it does

1. Orchestrator initialises session and fingerprints target
2. Planner scores attack branches using Bayesian MCTS
3. Planner declares intent (authorises specific tools)
4. Executor runs authorised attack tools against target
5. Reflector reviews findings and signals CONTINUE/PIVOT/COMPLETE
6. Loop repeats for each attack phase
7. Orchestrator generates final HTML report with PoC commands

## Installation

### Requirements
- Python 3.13
- pip install -e .

### Setup
```bash
git clone https://github.com/Cheerayu-Chowhan-HCL/redteamv9-adk.git
cd redteamv9-adk
pip install -e .
cp .env.example .env
```

### Configure .env
Open `.env` and fill in:

```
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4o
MCP_URL=http://CHIRAYU_VM_IP:6019/mcp
MCP_KEY=ask-chirayu-for-bearer-token
```

Note: MCP server must be running on Chirayu's VM.
Ask Chirayu to run DEMO_START.ps1 before engagement.

## Run an engagement

```bash
python start_engagement.py --target http://TARGET_URL --session SESSION_ID
```

Examples:
```bash
python start_engagement.py --target http://demo.testfire.net --session v9_adk_001
python start_engagement.py --target http://localhost:8080/altoromutual --session v9_adk_local_001
```

## View live results

Ask Chirayu for access to:
- DAG UI:            `http://CHIRAYU_VM_IP:6081/dag_ui.html`
- Defense Dashboard: `http://CHIRAYU_VM_IP:6081/defense_dashboard.html`

Both update in real time showing agent reasoning,
tool calls, findings, and security layer alerts.

## ADK Web UI (local visual interface)

Find your adk.exe path:
```bash
python -c "import google.adk, pathlib; print(pathlib.Path(google.adk.__file__).parent)"
```

Run web UI:
```bash
C:\path\to\Scripts\adk.exe web .
# Then open http://localhost:8000
```

The web UI shows the 4-agent architecture diagram
and allows interactive engagement sessions.

## Report output

Reports are saved on Chirayu's VM at:
```
C:\Users\chirayu\redteamv9\reports\SESSION_ID_report.html
```

Ask Chirayu to open and share the report after engagement.

## Model recommendations

- Current: `gpt-4o` (128k context — recommended)
- Fallback: `gpt-4o-mini` (128k context — lower cost)
- Not recommended: `gpt-5-mini` (16k context — cuts off mid-engagement)

## Agent descriptions

**orchestrator_agent**: Manages full engagement lifecycle.
  Owns: `create_session`, `fingerprint_target`, `generate_report`

**planner_agent**: Bayesian MCTS branch scoring.
  Owns: `score_branches`, `declare_intent`, `select_skills`
  ONLY agent that calls `declare_intent()`

**executor_agent**: Runs attack tools.
  Owns: `crawl_links`, `test_sqli`, `test_xss`, `test_csrf`,
        `test_auth_bypass`, `run_nuclei_scan`, `add_finding`
  Constrained by IntentCorrelationMiddleware

**reflector_agent**: Quality gate.
  Owns: `get_session_context`, `get_intent_incidents`
  Signals: CONTINUE / PIVOT / COMPLETE

## MCP Server (35 tools)

Full documentation:
https://github.com/Cheerayu-Chowhan-HCL/redteamv9

Tool categories:
- Session management: `create_session`, `get_session_context`
- Recon: `fingerprint_target`, `crawl_links`, `enumerate_endpoints`
- Injection: `test_sqli`, `test_xss`, `test_csrf`, `test_idor`
- Auth: `test_auth_bypass`, `test_session_fixation`
- Config: `check_headers`, `analyse_cookies`, `run_nuclei_scan`
- Knowledge: `retrieve_knowledge`, `distill_knowledge`
- Reporting: `generate_report`, `add_finding`

## For OpenAI SDK version

Same system prompts and tool filters work with
the `openai-agents` package. Reference:
https://github.com/openai/openai-agents-python

Connect to same MCP server, same bearer token.
