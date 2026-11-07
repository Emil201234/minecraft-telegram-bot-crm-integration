from rcon.source import rcon
import os
from dotenv import load_dotenv

load_dotenv()
HOST = os.getenv("RCON_HOST", "127.0.0.1")
PORT = int(os.getenv("RCON_PORT", "25575"))
PASSWORD = os.getenv("RCON_PASSWORD", "demo_password")

async def run_command(command: str) -> str:
    try:
        return await rcon(command, host=HOST, port=PORT, passwd=PASSWORD)
    except (ConnectionRefusedError, OSError, TimeoutError):
        return None