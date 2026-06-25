import os
import sys
import asyncio
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from orchestrator_agent.env import mcp_url, mcp_key
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

mcp_tools = MCPToolset(
    connection_params=StreamableHTTPServerParams(
        url=mcp_url,
        headers={"Authorization": f"Bearer {mcp_key}"},
    )
)

async def main():
    session = await mcp_tools._mcp_session_manager.create_session()
    tools = await session.list_tools()
    for t in tools.tools:
        print(t.name, t.inputSchema)
        print("--------------------")

asyncio.run(main())
