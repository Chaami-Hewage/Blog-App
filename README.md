## Midnight Divas Voice Chatbot

A voice-first chatbot with a Midnight Divas vibe. It supports highly-accurate speech-to-text (Sinhala supported via OpenAI Whisper and Faster-Whisper), emotional responses, text-to-speech, and a Gradio UI. Includes an optional MCP hook inspired by the MCP-powered voice agents cookbook.

### Features
- Sinhala-capable STT via OpenAI Whisper or Faster-Whisper
- Emotional agent aligned to Midnight Divas vibe
- TTS via OpenAI TTS
- Gradio UI for record → transcribe → respond → play
- Optional MCP hook to discover MCP tools
- Colab notebook for quick testing

### Setup
1. Python 3.10+
2. Install system deps:
   - ffmpeg (required for audio)
3. Create .env or export env vars:
```
OPENAI_API_KEY=your_api_key_here
STT_ENGINE=faster_whisper   # or openai
FASTER_WHISPER_MODEL=large-v3-turbo  # or large-v3
WHISPER_MODEL=whisper-1
TTS_MODEL=gpt-4o-mini-tts
TTS_VOICE=alloy
LANGUAGE_HINT=auto  # si, en, or auto
```

4. Install Python deps:
```bash
pip install -r requirements.txt
```

### Run
```bash
python main.py
```
It will launch a Gradio UI where you can record audio, get Sinhala/English transcription, receive a Midnight Divas styled response, and hear TTS playback.

### Notes on Sinhala
- Faster-Whisper `large-v3(-turbo)` provides strong multilingual accuracy including Sinhala. Use `LANGUAGE_HINT=si` for Sinhala recordings to increase accuracy, or keep `auto`.
- OpenAI Whisper (`whisper-1`) also supports Sinhala; you can compare both engines.

### MCP Hook (Optional)
- If you have an MCP server, set (example):
```
MCP_SERVER_CMD=node
MCP_SERVER_ARGS=your_mcp_server_script.js
```
- The app will expose a button in UI to list available tools from the MCP server.

### Colab
Open `colab_midnight_divas.ipynb` and run cells for a ready-to-test environment.