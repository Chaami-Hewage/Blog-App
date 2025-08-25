from typing import Optional

from config import CONFIG


MIDNIGHT_DIVAS_SYSTEM = (
    "You are Midnight Divas: sultry, confident, playful, and empowering. "
    "Your tone should be warm, a touch mysterious, with subtle charm. "
    "Be emotionally intelligent. Mirror the user's mood gently and keep it uplifting. "
    "When speaking Sinhala, keep it natural and contemporary. "
    "Do not be explicit. Keep responses short and intimate, like a late-night radio host."
)


class MidnightDivasAgent:
    def __init__(self, model: str = "gpt-4o-mini" ):
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=CONFIG.openai_api_key)
        return self._client

    def respond(self, user_text: str, language_hint: Optional[str] = None) -> str:
        client = self._get_client()
        # Encourage bilingual Sinhala/English continuation depending on input
        style_hint = "Sinhala" if (language_hint or "").lower() == "si" or any(
            ch in user_text for ch in ["අ", "ආ", "ඇ", "ශ", "ණ", "ළ", "ෘ"]
        ) else "English"
        messages = [
            {"role": "system", "content": MIDNIGHT_DIVAS_SYSTEM},
            {"role": "user", "content": f"Language: {style_hint}.\nMessage: {user_text}"},
        ]
        completion = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.8,
            max_tokens=300,
        )
        return completion.choices[0].message.content.strip()