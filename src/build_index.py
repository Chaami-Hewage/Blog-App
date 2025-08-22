import argparse
import csv
import os
from typing import List, Dict

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


def load_products(csv_path: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def build_corpus(rows: List[Dict[str, str]]) -> List[str]:
    corpus = []
    for r in rows:
        text = f"Title: {r.get('title','')}. Category: {r.get('category','')}. Price: {r.get('price','')}. Details: {r.get('description','')} URL: {r.get('url','')}"
        corpus.append(text)
    return corpus


def save_mapping(rows: List[Dict[str, str]], map_path: str) -> None:
    with open(map_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["idx", "title", "category", "price", "url", "description"])
        writer.writeheader()
        for idx, r in enumerate(rows):
            writer.writerow({
                "idx": idx,
                "title": r.get("title", ""),
                "category": r.get("category", ""),
                "price": r.get("price", ""),
                "url": r.get("url", ""),
                "description": r.get("description", ""),
            })


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--index_dir", required=True)
    parser.add_argument("--model", default="sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
    args = parser.parse_args()

    os.makedirs(args.index_dir, exist_ok=True)

    rows = load_products(args.csv)
    corpus = build_corpus(rows)

    model = SentenceTransformer(args.model)
    embeddings = model.encode(corpus, batch_size=64, show_progress_bar=True, convert_to_numpy=True, normalize_embeddings=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings.astype(np.float32))

    faiss.write_index(index, os.path.join(args.index_dir, "index.faiss"))
    save_mapping(rows, os.path.join(args.index_dir, "mapping.csv"))

    print(f"Indexed {len(rows)} products to {args.index_dir}")


if __name__ == "__main__":
    main()