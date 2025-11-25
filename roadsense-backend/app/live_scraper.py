import requests
from bs4 import BeautifulSoup
import re

URL = "https://www.dyp.gov.az/?/az/content/224"

def fetch_all_laws():
    try:
        resp = requests.get(URL, timeout=10)
        resp.raise_for_status()
    except:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    content = soup.find("div", class_="content")
    if not content:
        return []

    laws = []

    for idx, item in enumerate(content.find_all(["li", "p"]), start=1):
        text = item.get_text(strip=True)
        if not text or "Maddə" not in text:
            continue

        # Article
        parts = text.replace("—", "-").split("-")
        article = parts[0].strip()

        # Fine detection
        fine = "N/A"
        m = re.search(r"\d+(\s*-\s*\d+)?\s*AZN", text, re.IGNORECASE)
        if m:
            fine = m.group(0)

        title = " ".join(parts[1:]).strip()

        laws.append({
            "id": idx,
            "article_code": article,
            "title": title,
            "fine_info": fine,
            "full_text": text,
            "source_ref": URL
        })

    return laws


def search_online(query: str, top_k=3):
    laws = fetch_all_laws()
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
