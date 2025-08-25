import os
from typing import Optional, Tuple

from config import CONFIG


class SpeechToText:
    def __init__(self, engine: Optional[str] = None):
        self.engine = engine or CONFIG.stt_engine
        self._faster_model = None
        self._openai_client = None

    def _get_openai_client(self):
        if self._openai_client is None:
            from openai import OpenAI
            self._openai_client = OpenAI(api_key=CONFIG.openai_api_key)
        return self._openai_client

    def _get_faster_model(self):
        if self._faster_model is None:
            from faster_whisper import WhisperModel
            model_size = CONFIG.faster_whisper_model
            self._faster_model = WhisperModel(model_size, compute_type="auto")
        return self._faster_model

    def _normalize_language(self, language: Optional[str]) -> Optional[str]:
        lang = (language or CONFIG.language_hint or "auto").strip().lower()
        if lang in ("auto", "", None):
            return None
        return lang

    def transcribe(self, audio_path: str, language: Optional[str] = None) -> Tuple[str, float]:
        """
        Returns (text, avg_confidence).
        """
        if self.engine == "openai":
            return self._transcribe_openai(audio_path, language)
        return self._transcribe_faster_whisper(audio_path, language)

    def _transcribe_openai(self, audio_path: str, language: Optional[str]) -> Tuple[str, float]:
        client = self._get_openai_client()
        lang = self._normalize_language(language)
        with open(audio_path, "rb") as f:
            result = client.audio.transcriptions.create(
                model=CONFIG.whisper_model,
                file=f,
                language=lang,
                temperature=0.0,
            )
        # OpenAI returns text; per-segment confidence not provided. Use 1.0.
        return (getattr(result, "text", "") or "").strip(), 1.0

    def _transcribe_faster_whisper(self, audio_path: str, language: Optional[str]) -> Tuple[str, float]:
        model = self._get_faster_model()
        lang = self._normalize_language(language)
        segments, info = model.transcribe(
            audio_path,
            language=lang,
            vad_filter=True,
            beam_size=5,
            best_of=5,
            temperature=0.0,
        )
        texts = []
        confidences = []
        for seg in segments:
            texts.append(seg.text)
            if hasattr(seg, "avg_logprob") and seg.avg_logprob is not None:
                conf = max(0.0, min(1.0, 1.0 + (seg.avg_logprob / 5.0)))
                confidences.append(conf)
        text = " ".join(t.strip() for t in texts).strip()
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.9
        return text, avg_conf