from typing import Tuple

from faster_whisper import WhisperModel
from langdetect import detect


class ASRTranscriber:
    def __init__(self, model_name: str, compute_type: str = "float16"):
        self.model = WhisperModel(model_name, compute_type=compute_type)

    def transcribe(self, audio_path: str) -> Tuple[str, str]:
        segments, info = self.model.transcribe(audio_path, beam_size=5, vad_filter=True)
        text = " ".join([s.text.strip() for s in segments]).strip()
        try:
            lang = detect(text) if text else "en"
        except Exception:
            lang = info.language or "en"
        return text, lang