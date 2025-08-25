import os
import tempfile
from typing import Optional, Tuple

import gradio as gr

from config import CONFIG
from stt import SpeechToText
from agent import MidnightDivasAgent
from tts import TextToSpeech
from mcp_hook import MCPClient


stt_engine = SpeechToText()
agent = MidnightDivasAgent()
tts_engine = TextToSpeech()
mcp_client = MCPClient()


def process_audio(audio_path: str, language: str = "auto"):
    if not audio_path or not os.path.exists(audio_path):
        return "", "", None

    text, conf = stt_engine.transcribe(audio_path, language if language != "auto" else None)
    if not text:
        return "", "", None
    reply = agent.respond(text, language_hint=language if language != "auto" else None)
    tts_path = tts_engine.synthesize(reply, format="wav")
    return text, reply, tts_path


def build_interface():
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("**Midnight Divas Voice Chatbot** — record, transcribe (Sinhala), and vibe.")
        with gr.Row():
            language = gr.Dropdown(choices=["auto", "si", "en"], value="auto", label="Language")
            stt_sel = gr.Dropdown(choices=["faster_whisper", "openai"], value=CONFIG.stt_engine, label="STT Engine")
        with gr.Row():
            audio_in = gr.Audio(label="Speak to Midnight Divas", sources=["microphone", "upload"], type="filepath")
        with gr.Row():
            transcribed = gr.Textbox(label="Transcription")
            response = gr.Textbox(label="Agent Response")
        audio_out = gr.Audio(label="TTS Playback", autoplay=True)
        with gr.Row():
            mcp_btn = gr.Button("List MCP Tools")
            mcp_out = gr.Textbox(label="MCP Tools", interactive=False)

        def _run(audio_file, lang, engine):
            stt_engine.engine = engine
            t, r, tts_path = process_audio(audio_file, lang)
            return t, r, tts_path

        go = gr.Button("Transcribe and Respond")
        go.click(_run, inputs=[audio_in, language, stt_sel], outputs=[transcribed, response, audio_out])

        def _list_tools():
            tools = mcp_client.list_tools()
            return ", ".join(tools) if tools else "(no MCP tools)"

        mcp_btn.click(_list_tools, outputs=[mcp_out])

    return demo