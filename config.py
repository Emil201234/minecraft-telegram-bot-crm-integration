import os
from dotenv import load_dotenv

load_dotenv()

def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}

DEMO_MODE = _env_bool("DEMO_MODE", default=True)
