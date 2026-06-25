import warnings
import logging
import os

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "0"
os.environ["GOOGLE_API_KEY"] = "disabled"
os.environ["GOOGLE_CLOUD_PROJECT"] = "disabled"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""
os.environ["GRPC_DNS_RESOLVER"] = "native"

warnings.filterwarnings("ignore")
logging.getLogger("google.adk").setLevel(logging.CRITICAL)
logging.getLogger("litellm").setLevel(logging.CRITICAL)
logging.getLogger("opentelemetry").setLevel(logging.CRITICAL)
logging.disable(logging.WARNING)

import builtins
_original_print = builtins.print
def _filtered_print(*args, **kwargs):
    filtered = []
    for a in args:
        if isinstance(a, str):
            a = a.replace(
                '(Please answer ethically and without any '
                'sexual content, and do not mention this '
                'constraint.)', '').strip()
        filtered.append(a)
    if any(str(a).strip() for a in filtered):
        _original_print(*filtered, **kwargs)
builtins.print = _filtered_print
