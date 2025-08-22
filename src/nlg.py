from typing import List, Dict, Optional

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    GenerationConfig,
    BitsAndBytesConfig,
)
from peft import PeftModel

from .style import build_system_prompt, format_context_snippets


class NLGGenerator:
    def __init__(
        self,
        model_name: str,
        use_4bit: bool = True,
        lora_adapter: Optional[str] = None,
        max_new_tokens: int = 300,
        temperature: float = 0.9,
        top_p: float = 0.9,
        repetition_penalty: float = 1.05,
    ) -> None:
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        quant = None
        if use_4bit:
            quant = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
            )
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.float16,
            quantization_config=quant,
            trust_remote_code=True,
        )
        if lora_adapter:
            self.model = PeftModel.from_pretrained(self.model, lora_adapter)
        self.generation_config = GenerationConfig(
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=temperature,
            top_p=top_p,
            repetition_penalty=repetition_penalty,
        )

    def _build_messages(
        self,
        user_query: str,
        language: str,
        retrieved: List[Dict[str, str]],
    ) -> List[Dict[str, str]]:
        system = build_system_prompt(language)
        context = format_context_snippets(retrieved, language)
        if language.lower().startswith("si"):
            instruction = (
                "පහත නිෂ්පාදන තොරතුරු මත පදනම්ව කෙටි, ආකර්ෂණීය පිලිතුරක් දෙන්න. "
                "පරිශීලක භාෂාවට (සිංහල) ගැළපෙන්න. ගැළපෙන නිෂ්පාදන නාම, වැදගත් විස්තර, මිල, හා Link සම්බන්ධ කරන්න. "
                "ආත්මවිශ්වාසිය හා ආදරණීය ලහිරි ඇතත්, ගෞරවයෙන් හා ලස්සනින්. අවසානයේ සාර්ථක call-to-action එකක් ඇතුළත් කරන්න."
            )
        else:
            instruction = (
                "Craft a short, captivating reply based on the product info. "
                "Respond in the user's language (English), include relevant product names, key details, price, and a link. "
                "Keep it tasteful, confident, and enticing with a clear, gentle call-to-action."
            )
        user = (
            f"User query: {user_query}\n\n"
            f"Product context (use only what's relevant, you may reference 1-3 items):\n{context}"
        )
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": instruction + "\n\n" + user},
        ]

    def generate(self, user_query: str, language: str, retrieved: List[Dict[str, str]]) -> str:
        messages = self._build_messages(user_query, language, retrieved)
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer([prompt], return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            outputs = self.model.generate(**inputs, generation_config=self.generation_config)
        text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Strip the prompt
        if text.startswith(prompt):
            text = text[len(prompt):]
        return text.strip()