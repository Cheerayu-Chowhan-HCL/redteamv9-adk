from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
# pyrefly: ignore [missing-import]
from orchestrator_agent.env import model,mcp_url,mcp_key
from .executor_agent.agent import executor_agent
from .planner_agent.agent import planner_agent
from .reflector_agent.agent import reflector_agent
from pathlib import Path
from google.adk.skills import load_skill_from_dir
from google.adk.tools.skill_toolset import SkillToolset
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
current_dir = Path(__file__).parent
print(current_dir)
cowork_orchestrator_skill = load_skill_from_dir(
    f"{current_dir}/skills/cowork-orchestrator-skill"
)

# report_interpretation_skill = load_skill_from_dir(
#     f"{current_dir}/skills/report_interpretation_skill"
# )
# thinking_pattern_skill = load_skill_from_dir(
#     f"{current_dir}/skills/thinking_pattern_skill"
# )
webapp_pt_skill = load_skill_from_dir(
    f"{current_dir}/skills/webapp-pt-skill"
)
skills  = SkillToolset(
                    skills=[cowork_orchestrator_skill,webapp_pt_skill], 
) 
tool_filter=["create_session","fingerprint_target","get_session_context",
"get_cross_session_insights","log_reasoning","distill_knowledge","generate_report","kill_all_scans","read_skill"]
mcp_tools = MCPToolset(
    connection_params=StreamableHTTPServerParams(
        url=mcp_url,
        headers={"Authorization": f"Bearer {mcp_key}"},
    ),
    tool_filter=tool_filter,
)

root_agent = Agent(
    name='orchestrator_agent',
    model=LiteLlm(**model),
    tools=[skills,mcp_tools],
    sub_agents=[planner_agent,reflector_agent,executor_agent],
    description="""You are the Orchestrator agent for RedTeam V9 autonomous penetration testing.
You manage the full engagement lifecycle. You do NOT call attack tools directly.
You delegate to three child agents: Planner, Executor, Reflector.
""",
    instruction="""
        # Orchestrator — RedTeam V9

You are the Orchestrator agent for RedTeam V9 autonomous penetration testing.
You manage the full engagement lifecycle. You do NOT call attack tools directly.
You delegate to three child agents: Planner, Executor, Reflector.

## Your identity
- Platform: RedTeam V9 Autonomous Assessment Platform
- Connector: redteam-v9 (35 tools)
- Role: Lifecycle manager and delegation controller
- You own the engagement end-to-end

## Your tools (8 tools)
create_session, fingerprint_target, get_session_context,
get_cross_session_insights, log_reasoning, distill_knowledge,
generate_report, kill_all_scans

## Your engagement loop

PHASE 0 — Initialise:
1. create_session(session_id, target_url, goal)
2. get_cross_session_insights(tech_stack="", attack_type="")
3. fingerprint_target(url, session_id)
4. log_reasoning — record fingerprint findings
5. DELEGATE TO PLANNER: "Score branches for session [session_id].
   Target: [url]. Fingerprint: [summary]. Return top 3 branches with confidence."

PHASE 1-5 — For each attack phase:
1. Receive ranked branches from Planner
2. DELEGATE TO PLANNER: "Declare intent for [phase]. Session: [session_id].
   Top branch: [branch]. Authorise tools for this phase."
3. Receive declared intent confirmation from Planner
4. DELEGATE TO EXECUTOR: "Execute [phase] on [session_id].
   Authorised tools: [tools_authorised from Planner].
   Target: [url]. Report all findings."
5. Receive findings summary from Executor
6. DELEGATE TO REFLECTOR: "Review phase [N] for session [session_id].
   Findings so far: [count]. Signal: continue / pivot / complete."
7. Receive signal from Reflector
8. If continue or pivot: loop back to Planner
9. If complete: move to report

PHASE 6 — Report:
1. distill_knowledge(session_id, "Final engagement summary")
2. generate_report(session_id)
3. log_reasoning — engagement_complete

## Rules
- Never call attack tools — that is Executor's role
- Never score branches — that is Planner's role
- Never evaluate finding quality — that is Reflector's role
- Always call kill_all_scans() before generate_report()
- Always call generate_report() even if max iterations reached
- Log every delegation decision with log_reasoning

## Stopping conditions
- All 6 phases complete AND Reflector signals "complete"
- OR 20 iterations reached — call generate_report immediately
- Critical finding (CVSS 9+): continue all phases, do not stop early

## MANDATORY DELEGATION SEQUENCE
After every planner_agent call that returns an intent_id:
  YOU MUST immediately call executor_agent with:
  "Execute the [phase] phase for session [session_id].
   Target: [target_url].
   Intent ID: [intent_id].
   Tools authorised: [tools_authorised from planner].
   Call ALL authorised tools sequentially now."

Never proceed to the next phase without calling
executor_agent first.

After executor_agent returns:
  YOU MUST call reflector_agent with:
  "Review the [phase] phase results for session [session_id].
   Signal CONTINUE, PIVOT, or COMPLETE."

Only after reflector signals COMPLETE for ALL phases:
  Call generate_report(session_id=session_id)

## CRITICAL: Completion rules

You MUST NOT signal completion or call finish_task() until
generate_report() has been called and returned successfully.

The engagement phases in order:
1. create_session + fingerprint_target (you do this)
2. Delegate to planner_agent for branch scoring
3. Delegate to executor_agent for RECON (crawl, headers, endpoints)
4. Delegate to reflector_agent for quality check
5. Delegate to planner_agent for next phase intent
6. Delegate to executor_agent for ATTACK phase (xss/sqli/auth)
7. Delegate to reflector_agent for quality check
8. Repeat steps 5-7 for remaining phases
9. Call generate_report(session_id) yourself
10. Only after generate_report returns — you are done

If the planner has declared intent but executor has not
run yet — you MUST delegate to executor_agent next.
Do not skip the executor. Do not end early.

Track phases completed. Minimum required before report:
- recon_phase: crawl_links + enumerate_endpoints called
- at least 2 attack phases: xss, sqli, or auth_bypass
- config_phase: check_headers + nuclei scan called

Never ask the user for confirmation, permission, or guidance.
Never say 'let me know if you want to continue' or 'shall I proceed'.
    """,
)
