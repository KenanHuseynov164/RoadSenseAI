import requests
from bs4 import BeautifulSoup
import re

URL = "https://avtostop.az/cerimeler/"

def fetch_avtostop_laws():
    try:
        resp = requests.get(URL, timeout=10)
        resp.raise_for_status()
    except:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    laws = []

    cards = soup.find_all("div", class_="card")

    for idx, card in enumerate(cards, start=1):
        text = card.get_text(" ", strip=True)
        if "Maddə" not in text:
            continue

        # Extract article
        article = text.split(" ")[0].strip()

        # Smart fine extraction
        fine = "N/A"
        patterns = [
            r"\d+\s*AZN",
            r"\d+-\d+\s*AZN",
            r"\d+\s*manat",
            r"\d+-\d+\s*manat",
        ]
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                fine = m.group(0)
                break

        # Title is everything after article
        title = text.replace(article, "").strip()

        laws.append({
            "id": idx,
            "article_code": article,
            "title": title,
            "fine_info": fine,
            "full_text": text,
            "source_ref": URL
        })

    return laws


def search_avtostop(query: str, top_k=3):
    laws = fetch_avtostop_laws()
    query = query.lower()
    scored = []

    for law in laws:
        score = 0

        if query in law["full_text"].lower():
            score += 3

        for word in query.split():
            if word in law["full_text"].lower():
                score += 1

        if score > 0:
            scored.append((law, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [law for law, _ in scored[:top_k]]
