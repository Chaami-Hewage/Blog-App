import argparse
import os
import tempfile
import yaml
from typing import Tuple, List, Dict

import gradio as gr
import numpy as np
import soundfile as sf

from .asr import ASRTranscriber
from .retriever import ProductRetriever
from .nlg import NLGGenerator
from .tts import TTSEngine
from .utils import detect_lang_code, ensure_dir


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def numpy_to_wav(np_audio: np.ndarray, sr: int, out_path: str) -> str:
    sf.write(out_path, np_audio, sr)
    return out_path


def create_app(config: dict):
    retriever = ProductRetriever(
        index_dir=config["index_dir"],
        embedding_model_name=config["embeddings_model"],
    )
    asr = ASRTranscriber(
        model_name=config["whisper_model"],
        compute_type=config.get("whisper_compute_type", "float16"),
    )
    nlg = NLGGenerator(
        model_name=config["llm_model"],
        use_4bit=bool(config.get("llm_4bit", True)),
        lora_adapter=config.get("lora_adapter"),
        max_new_tokens=int(config.get("max_new_tokens", 300)),
        temperature=float(config.get("temperature", 0.9)),
        top_p=float(config.get("top_p", 0.9)),
        repetition_penalty=float(config.get("repetition_penalty", 1.05)),
    )
    tts = TTSEngine(
        parler_model=config["tts_en_model"],
        style_prompt=config.get("parler_style_prompt", ""),
        gtts_lang=config.get("gtts_sinhala_lang", "si"),
    )

    outputs_dir = os.path.join(config.get("data_dir", "data"), "responses")
    ensure_dir(outputs_dir)

    def respond(audio: Tuple[int, np.ndarray]) -> Tuple[str, str]:
        if audio is None:
            return "No audio received.", None
        sr, data = audio
        # Save temp wav for ASR
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            wav_path = tmp.name
        sf.write(wav_path, data, sr)
        text, lang_raw = asr.transcribe(wav_path)
        os.unlink(wav_path)
        if not text:
            return "I couldn't hear you. Please try again.", None
        lang = detect_lang_code(text) if lang_raw else "en"
        # Retrieve
        results = retriever.search(text, top_k=int(config.get("top_k", 5)))
        snippets: List[Dict[str, str]] = [r[1] for r in results]
        # Generate
        reply = nlg.generate(text, lang, snippets)
        # TTS
        if lang == "si":
            out_audio = os.path.join(outputs_dir, "response_si.mp3")
            audio_path = tts.tts_sinhala(reply, out_audio)
        else:
            out_audio = os.path.join(outputs_dir, "response_en.wav")
            audio_path = tts.tts_english(reply, out_audio)
        return reply, audio_path

    with gr.Blocks(title="Midnight Divas Voice Assistant") as demo:
        gr.Markdown("**Midnight Divas Bilingual Voice Assistant (Sinhala/English)**")
        with gr.Row():
            audio_in = gr.Audio(sources=["microphone"], type="numpy", label="Speak your question")
        with gr.Row():
            text_out = gr.Textbox(label="Assistant")
        with gr.Row():
            audio_out = gr.Audio(label="Response audio")
        btn = gr.Button("Ask")
        btn.click(fn=respond, inputs=[audio_in], outputs=[text_out, audio_out])
    return demo


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="./src/config.yaml")
    args = parser.parse_args()
    cfg = load_config(args.config)
    demo = create_app(cfg)
    demo.launch(share=bool(cfg.get("share", False)), server_port=int(cfg.get("server_port", 7860)))


if __name__ == "__main__":
    main()