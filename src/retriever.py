import csv
import os
from typing import List, Dict, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class ProductRetriever:
    def __init__(self, index_dir: str, embedding_model_name: str):
        self.index_path = os.path.join(index_dir, "index.faiss")
        self.mapping_path = os.path.join(index_dir, "mapping.csv")
        if not os.path.exists(self.index_path) or not os.path.exists(self.mapping_path):
            raise FileNotFoundError("Index or mapping not found. Build with build_index.py")
        self.index = faiss.read_index(self.index_path)
        self.model = SentenceTransformer(embedding_model_name)
        self.rows: List[Dict[str, str]] = []
        with open(self.mapping_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.rows.append(row)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[float, Dict[str, str]]]:
        embedding = self.model.encode([query], normalize_embeddings=True, convert_to_numpy=True)
        scores, idxs = self.index.search(embedding.astype(np.float32), top_k)
        results: List[Tuple[float, Dict[str, str]]] = []
        for score, idx in zip(scores[0], idxs[0]):
            if idx < 0 or idx >= len(self.rows):
                continue
            results.append((float(score), self.rows[idx]))
        return results