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
