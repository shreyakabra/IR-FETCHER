import os
from dotenv import load_dotenv
load_dotenv()

DOWNLOAD_ROOT = os.getenv("DOWNLOAD_ROOT", "./data/downloads")
METADATA_ROOT = os.getenv("METADATA_ROOT", "./data/metadata")
DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "openai")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
