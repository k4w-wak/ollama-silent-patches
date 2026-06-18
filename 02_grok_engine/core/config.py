"""Grok core config — re-exports from root config.py + adds config_tool."""
import sys
import os
from pathlib import Path

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from config import *

# ═══════════════════════════════════════════════════════════════
# Memory / paths — always available even if root config changes
# ═══════════════════════════════════════════════════════════════
GROK_HOME = Path(os.environ.get("GROK_HOME", os.path.expanduser("~/.grok")))
MEMORY_DIR = GROK_HOME / "memory"
FACTS_FILE = MEMORY_DIR / "facts.json"
MEMORY_SHORT_TERM_SIZE = int(os.environ.get("MEMORY_SHORT_TERM_SIZE", "50"))
MEMORY_AUTO_SAVE = os.environ.get("MEMORY_AUTO_SAVE", "true").lower() in ("true", "1", "yes")

# ═══════════════════════════════════════════════════════════════
# Cloud API timeouts — prevent agent hangs
# ═══════════════════════════════════════════════════════════════
CLOUD_REQUEST_TIMEOUT = int(os.environ.get("CLOUD_REQUEST_TIMEOUT", "120"))  # seconds per API call
CLOUD_MAX_RETRIES = int(os.environ.get("CLOUD_MAX_RETRIES", "3"))             # retries before giving up
CLOUD_RETRY_BASE_WAIT = int(os.environ.get("CLOUD_RETRY_BASE_WAIT", "5"))     # base wait between retries

# ═══════════════════════════════════════════════════════════════
# Ollama / Cloud — always available even if root config import fails
# ═══════════════════════════════════════════════════════════════
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_CLOUD = os.environ.get("OLLAMA_CLOUD", "")
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY", "")

# Also make config_tool available
from core.config_tool import get_setting, set_setting, list_settings
