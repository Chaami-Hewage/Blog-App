import argparse
import csv
import os
from typing import List, Dict

import torch
from datasets import Dataset
from peft import LoraConfig
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TrainingArguments,
)
from trl import SFTTrainer

from .style import build_system_prompt


def load_products(csv_path: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def build_training_samples(rows: List[Dict[str, str]], language: str = "en") -> List[Dict[str, str]]:
    samples: List[Dict[str, str]] = []
    system = build_system_prompt(language)
    for r in rows:
        title = r.get("title", "").strip()
        price = r.get("price", "").strip()
        url = r.get("url", "").strip()
        desc = r.get("description", "").strip()
        if language == "si":
            user = f"මේ නිෂ්පාදනය ගැන කියන්න: {title}"
            assistant = (
                f"{title} ගැන කෙටි, ආකර්ෂණීය විස්තරයක්: {desc}. මිල {price}. "
                f"වැඩි විස්තර: {url}. ඔබට ගැළපෙන චර්ම/රූපයේ හැඟීම් ඉස්මතු කරමින් ලස්සන CTA එකක් දාන්න."
            )
        else:
            user = f"Tell me about this product: {title}"
            assistant = (
                f"A short, enticing description for {title}: {desc}. Price: {price}. "
                f"Learn more: {url}. Keep it confident, elegant, and persuasive with a gentle CTA."
            )
        samples.append({
            "system": system,
            "user": user,
            "assistant": assistant,
        })
    return samples


def to_chat_text(tokenizer, system: str, user: str, assistant: str) -> str:
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant},
    ]
    return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--base_model", default="Qwen/Qwen2.5-3B-Instruct")
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--language", default="en")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--batch", type=int, default=1)
    parser.add_argument("--grad_accum", type=int, default=8)
    args = parser.parse_args()

    rows = load_products(args.csv)
    samples = build_training_samples(rows, args.language)

    tokenizer = AutoTokenizer.from_pretrained(args.base_model, use_fast=True)
    texts = [to_chat_text(tokenizer, s["system"], s["user"], s["assistant"]) for s in samples]
    ds = Dataset.from_dict({"text": texts})

    quant = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        device_map="auto",
        torch_dtype=torch.float16,
        quantization_config=quant,
        trust_remote_code=True,
    )

    lora = LoraConfig(
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    )

    training_args = TrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.batch,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        num_train_epochs=args.epochs,
        logging_steps=10,
        save_steps=200,
        save_total_limit=2,
        bf16=torch.cuda.is_available(),
        fp16=not torch.cuda.is_available(),
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        peft_config=lora,
        train_dataset=ds,
        dataset_text_field="text",
        max_seq_length=2048,
        args=training_args,
    )

    trainer.train()
    trainer.model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)


if __name__ == "__main__":
    main()