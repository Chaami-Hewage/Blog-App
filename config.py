import os
from dataclasses import dataclass


@dataclass
class AppConfig:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    stt_engine: str = os.getenv("STT_ENGINE", "faster_whisper")  # or "openai"
    faster_whisper_model: str = os.getenv("FASTER_WHISPER_MODEL", "large-v3-turbo")
    whisper_model: str = os.getenv("WHISPER_MODEL", "whisper-1")
    language_hint: str = os.getenv("LANGUAGE_HINT", "auto")  # "si", "en", or "auto"

    tts_model: str = os.getenv("TTS_MODEL", "gpt-4o-mini-tts")
    tts_voice: str = os.getenv("TTS_VOICE", "alloy")

    # Optional MCP
    mcp_server_cmd: str = os.getenv("MCP_SERVER_CMD", "")
    mcp_server_args: str = os.getenv("MCP_SERVER_ARGS", "")


CONFIG = AppConfig()