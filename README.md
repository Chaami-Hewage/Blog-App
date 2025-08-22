## Midnight Divas Bilingual Voice Assistant (Sinhala/English)

End-to-end voice-to-voice assistant that answers product questions about Midnight Divas using:
- ASR: Whisper (faster-whisper)
- RAG: FAISS + Sentence-Transformers (multilingual)
- NLG: Qwen2.5-3B-Instruct with brand tone and emotions
- TTS: Parler-TTS (English expressive), gTTS (Sinhala)
- Optional: QLoRA fine-tuning for brand style
- UI: Gradio voice chat

### Quickstart (Colab)
1. Open the provided Colab notebook in `notebooks/colab_midnight_divas_voice_assistant.ipynb`.
2. Run cells to install dependencies, build the product index (upload CSV or scrape), and launch the Gradio app.

### Local (GPU recommended)
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.app --config ./src/config.yaml
```

### Data
- Preferred: Upload a `data/products.csv` with columns: `title,description,price,url,category`.
- Or scrape collections with `src/scrape_products.py` (respect robots and ToS).

### Index
```
python src/build_index.py --csv data/products.csv --index_dir data/index
```

### Optional LoRA Fine-tuning
```
python src/train_lora.py --csv data/products.csv --output_dir models/qwen2.5-3b-md-lora
```

Then reference the adapter in `src/config.yaml`.

### Notes
- English TTS uses Parler-TTS for emotional, humanized delivery.
- Sinhala TTS uses gTTS; expressive controls are limited. The NLG prompt encodes mood and style.
- All models are local; no API keys are required.