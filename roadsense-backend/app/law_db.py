import json
import os
from typing import List, Dict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "laws.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    LAWS = json.load(f)

def search_laws(query: str, top_k: int = 5) -> List[Dict]:
    q = query.lower()
    scored = []

    for law in LAWS:
        score = 0

        if q in law["full_text"].lower():
            score += 3

        for word in q.split():
            if word in law["full_text"].lower():
                score += 1

        if score > 0:
            scored.append((law, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [law for law, _ in scored[:top_k]]
