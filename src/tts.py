import os
from typing import Optional

import torch
from gtts import gTTS
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer


class TTSEngine:
    def __init__(self, parler_model: str, style_prompt: str, gtts_lang: str = "si", device: Optional[str] = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.parler = ParlerTTSForConditionalGeneration.from_pretrained(parler_model).to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(parler_model)
        self.style_prompt = style_prompt
        self.gtts_lang = gtts_lang

    def tts_english(self, text: str, out_path: str) -> str:
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        style_inputs = self.tokenizer(self.style_prompt, return_tensors="pt").to(self.device)
        with torch.no_grad():
            audio_tensor = self.parler.generate(input_ids=inputs.input_ids, prompt_input_ids=style_inputs.input_ids)[0]
        audio = audio_tensor.cpu().numpy()
        from scipy.io.wavfile import write as wavwrite
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        wavwrite(out_path, 24000, audio)
        return out_path

    def tts_sinhala(self, text: str, out_path: str) -> str:
        tts = gTTS(text=text, lang=self.gtts_lang)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        tts.save(out_path)
        return out_path