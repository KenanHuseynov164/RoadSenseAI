import os
import json
from typing import List, Tuple

from openai import OpenAI

from . import scraper_avtostop
from . import live_scraper
from . import law_db

# Uses OPENAI_API_KEY from environment
client = OpenAI()

SYSTEM_PROMPT = """
You are RoadSenseAI, a legal assistant for Azerbaijani traffic laws.

Goal:
- Given the driver's description and a small list of matched laws,
  you must choose the MOST RELEVANT article and explain it VERY SHORTLY.

Output FORMAT (MUST be valid JSON, no extra text):

{
  "legal_articles": [
    "Maddə XXX — qısa ad (Cərimə: X AZN, Y bal)"
  ],
  "explanation": "max 2 qısa cümlə ilə, nəyə görə bu maddə tətbiq olunur.",
  "recommendation": "1 qısa cümlə: sürücü nə etməlidir.",
  "what_to_say": "1 nəzakətli cümlə zabitə demək üçün."
}

STRICT RULES:
- Cavab Azərbaycan dilində olmalıdır.
- "legal_articles" MASSIVİ maksimum 2 element olsun.
- Heç vaxt tam qanun mətnini kopyalama, yalnız qısa cümlə yaz.
- Mümkün olduqda cəriməni AZN və balla göstər (əgər fine_info verilibsə).
- Əgər dəqiq maddə tapılmırsa, bunu de, amma yenə də qısa izah + tövsiyə ver.
"""
import re

def detect_speed_case(text: str):
    """
    Try to detect a speeding case from free text.
    Example: '60liq yolda 90la getdim' -> limit=60, speed=90, delta=30 -> Maddə 328.2
    Returns a single 'law' dict or None.
    """
    numbers = re.findall(r"\d+", text)

    # We need at least 2 numbers: limit and actual speed
    if len(numbers) < 2:
        return None

    limit = int(numbers[0])
    speed = int(numbers[1])

    if speed <= limit:
        return None

    delta = speed - limit

    if 10 <= delta <= 20:
        return {
            "article_code": "Maddə 328.1",
            "title": "Sürət həddinin 10–20 km/saat aşılması",
            "fine_info": "10 AZN",
            "summary_az": "Sürət həddini 10–20 km/saat aralığında aşdıqda tətbiq olunur.",
            "full_text": "Sürət həddinin 10–20 km/saat aşılması — 10 AZN cərimə.",
            "source_ref": "AUTO_NUMERIC"
        }
    elif 20 < delta <= 40:
        return {
            "article_code": "Maddə 328.2",
            "title": "Sürət həddinin 20–40 km/saat aşılması",
            "fine_info": "50 AZN",
            "summary_az": "Sürət həddini 20–40 km/saat aralığında aşdıqda tətbiq olunur.",
            "full_text": "Sürət həddinin 20–40 km/saat aşılması — 50 AZN cərimə.",
            "source_ref": "AUTO_NUMERIC"
        }
    elif delta > 40:
        return {
            "article_code": "Maddə 328.3",
            "title": "Sürət həddinin 40 km/saatdan çox aşılması",
            "fine_info": "150–250 AZN",
            "summary_az": "Sürət həddini 40 km/saatdan çox aşdıqda tətbiq olunur.",
            "full_text": "Sürət həddinin 40+ km/saat aşılması — 150–250 AZN cərimə.",
            "source_ref": "AUTO_NUMERIC"
        }

    return None

def _call_ai(desc: str, matched: List[dict]) -> dict:
    # Hazırlanmış qanun məlumatını kiçik formaya salaq
    laws_for_prompt = []
    for law in matched:
        laws_for_prompt.append(
            {
                "article_code": law.get("article_code"),
                "title": law.get("title"),
                "fine_info": law.get("fine_info"),
                "summary_az": law.get("summary_az", ""),
                # tam mətni yox, yalnız ilk 300 simvol (modelə kontekst kimi)
                "full_text_short": (law.get("full_text", "")[:300]),
                "source_ref": law.get("source_ref"),
            }
        )

    payload = {
        "user_description": desc,
        "matched_laws": laws_for_prompt,
    }

    # JSON mode → model MÜTLƏQ JSON qaytarır
    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        temperature=0.2,
        max_tokens=220,
    )

    content = resp.choices[0].message.content

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # Yenə də problem olsa – qısa fallback istifadə edirik
        data = {
            "legal_articles": [],
            "explanation": "Sistem AI cavabını emal edə bilmədi.",
            "recommendation": "Zabitdən tətbiq etdiyi maddəni və cəriməni aydın şəkildə izah etməsini xahiş edin.",
            "what_to_say": "Zabit bəy, zəhmət olmasa tətbiq etdiyiniz maddəni və cərimə məbləğini bir daha izah edərdinizmi?",
        }

    # Bütün açarların mövcud olduğuna əmin olaq
    if "legal_articles" not in data or not isinstance(data["legal_articles"], list):
        data["legal_articles"] = []

    for key in ["explanation", "recommendation", "what_to_say"]:
        if key not in data or not isinstance(data[key], str):
            data[key] = ""

    return data


def analyze_incident(text: str) -> Tuple[List[str], str, str, str]:
    text = (text or "").strip()
    if not text:
        return (
            ["Təsvir boşdur"],
            "Zəhmət olmasa vəziyyəti aydın şəkildə təsvir edin.",
            "Öncə hadisəni tam yazın, sonra sistemi yenidən istifadə edin.",
            "Zabit bəy, bir az vaxt verin, vəziyyəti izah edim."
        )

    # 0️⃣ First: try numeric speed logic
    matched_laws = []
    numeric_law = detect_speed_case(text)
    if numeric_law:
        matched_laws.append(numeric_law)
    else:
        # 1️⃣ Try Avtostop
        matched_laws = scraper_avtostop.search_avtostop(text)

        # 2️⃣ Try DYP
        if not matched_laws:
            matched_laws = live_scraper.search_online(text)

        # 3️⃣ Fallback to local JSON
        if not matched_laws:
            matched_laws = law_db.search_laws(text, top_k=5)

    ai = _call_ai(text, matched_laws)

    legal_articles = ai.get("legal_articles", [])
    explanation = ai.get("explanation", "")
    recommendation = ai.get("recommendation", "")
    what_to_say = ai.get("what_to_say", "")

    if not legal_articles and matched_laws:
        legal_articles = [
            f"{law['article_code']} — {law['title']} (Cərimə: {law.get('fine_info','N/A')})"
            for law in matched_laws
        ]

    return legal_articles, explanation, recommendation, what_to_say

