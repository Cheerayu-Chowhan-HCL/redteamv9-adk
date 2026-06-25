import os
import pathlib
import litellm
from dotenv import load_dotenv

_env_path = pathlib.Path(__file__).parent.parent / '.env'
load_dotenv(_env_path)

openai_api_key = os.environ.get("OPENAI_API_KEY", "")
openai_model   = os.environ.get("OPENAI_MODEL", "o3")
mcp_url        = os.environ.get("MCP_URL", "http://10.30.21.5:6019/mcp")
mcp_key        = os.environ.get("MCP_KEY", "")

model = {
    "api_key":               openai_api_key,
    "model":                 openai_model,
    "max_completion_tokens": 4000,
    "timeout":               300,
    "drop_params":           True,
}

litellm.drop_params   = True
litellm.modify_params = True
