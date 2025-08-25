import tempfile
from typing import Optional

from config import CONFIG


class TextToSpeech:
    def __init__(self, model: Optional[str] = None, voice: Optional[str] = None):
        self.model = model or CONFIG.tts_model
        self.voice = voice or CONFIG.tts_voice
        self._openai_client = None

    def _get_openai_client(self):
        if self._openai_client is None:
            from openai import OpenAI
            self._openai_client = OpenAI(api_key=CONFIG.openai_api_key)
        return self._openai_client

    def synthesize(self, text: str, format: str = "wav") -> str:
        """
        Returns a filesystem path to the synthesized audio file.
        """
        client = self._get_openai_client()
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{format}") as tmp:
            tmp_path = tmp.name
        try:
            with client.audio.speech.with_streaming_response.create(
                model=self.model,
                voice=self.voice,
                input=text,
                format=format,
            ) as response:
                response.stream_to_file(tmp_path)
        except AttributeError:
            # Fallback for SDKs without with_streaming_response
            resp = client.audio.speech.create(
                model=self.model,
                voice=self.voice,
                input=text,
                format=format,
            )
            audio_bytes = None
            if hasattr(resp, "read"):
                audio_bytes = resp.read()
            elif hasattr(resp, "content"):
                audio_bytes = resp.content
            else:
                audio_bytes = bytes(resp)
            with open(tmp_path, "wb") as f:
                f.write(audio_bytes)
        return tmp_path