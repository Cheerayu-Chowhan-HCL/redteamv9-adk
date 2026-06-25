import suppress_warnings  # must be first before any adk import
import os
import asyncio
import argparse
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))

from orchestrator_agent.env import mcp_url, mcp_key, model
from orchestrator_agent.agent import root_agent as orchestrator_agent

async def run_engagement(target_url: str, session_id: str):
    print(f"RedTeam V9 ADK Engagement")
    print(f"Target:  {target_url}")
    print(f"Session: {session_id}")
    print(f"Model:   {model['model']}")
    print(f"MCP:     {mcp_url}")
    print()

    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types

    session_service = InMemorySessionService()
    APP_NAME = "redteam_v9_adk"
    USER_ID = "operator"

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
    )

    runner = Runner(
        agent=orchestrator_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    start_message = f"""Authorised penetration test.

Target: {target_url}
Session: {session_id}
Goal: Full black-box web application security assessment.

You are the Orchestrator. Begin immediately:
1. create_session({session_id!r}, {target_url!r}, 'Full black-box web application security assessment')
2. fingerprint_target({target_url!r}, {session_id!r})
3. Delegate to Planner: score branches and declare recon intent
4. Delegate to Executor: execute recon phase
5. Delegate to Reflector: review quality
6. Continue all phases until generate_report fires.

Do not pause. Do not ask for approval. Complete all phases.

IMPORTANT: This is a fully automated engagement. Do not ask for user input at any point.
Do not say 'let me know' or 'shall I' or 'if you want'. Execute all 6 phases sequentially
and call generate_report() when complete. Begin now."""

    content = types.Content(
        role="user",
        parts=[types.Part(text=start_message)]
    )

    print("=== ADK Engagement Starting ===")
    print()

    async def run_with_timeout(runner, user_id, session_id, content, timeout_secs=900):
        try:
            async with asyncio.timeout(timeout_secs):
                async for event in runner.run_async(
                    user_id=user_id,
                    session_id=session_id,
                    new_message=content,
                ):
                    # Track tool calls for completion detection
                    if hasattr(event, 'get_function_calls'):
                        try:
                            calls = event.get_function_calls()
                            if calls:
                                for call in calls:
                                    tool_name = call.name
                                    print(f'\n[TOOL] {tool_name}', flush=True)
                                    if tool_name == 'generate_report':
                                        print('\n\n=== REPORT GENERATED ===',
                                              flush=True)
                        except Exception:
                            pass

                    # Print text content
                    if hasattr(event, 'content') and event.content:
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                print(part.text, end='', flush=True)
            return True
        except TimeoutError:
            print(f'\n[TIMEOUT] Engagement exceeded {timeout_secs}s — partial results may be available.')
            import traceback
            traceback.print_exc()
            return False
        except Exception as exc:
            print(f'\n[ERROR] Engagement error: {exc}')
            import traceback
            traceback.print_exc()
            return False

    await run_with_timeout(runner, USER_ID, session_id, content, timeout_secs=900)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', default='http://localhost:8080/altoromutual')
    parser.add_argument('--session', default='v9_adk_001')
    args = parser.parse_args()
    try:
        asyncio.run(run_engagement(args.target, args.session))
    except Exception as e:
        import traceback
        print(f'\nFATAL ERROR: {e}')
        traceback.print_exc()
