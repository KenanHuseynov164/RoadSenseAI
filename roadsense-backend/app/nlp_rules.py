import os
import json
from typing import List, Tuple

from openai import OpenAI

from . import scraper_avtostop
from . import live_scraper
from . import law_db

# Create client – API key comes from environment variable OPENAI_API_KEY
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are RoadSenseAI, a legal assistant for Azerbaijani traffic laws.

You will receive:
- user_description: what happened on the road
- matched_laws: list of law entries (article_code, title, fine_info, full_text, source_ref)

You MUST base your answer ONLY on matched_laws.
NEVER invent law articles, fines or punishments that are not inside matched_laws.

Always include the fine (cərimə) clearly when possible.

Your answer MUST be a SINGLE valid JSON object with EXACTLY these fields:

{
  "legal_articles": ["Maddə XXX — Title (Cərimə: X AZN)"],
  "explanation": "short explanation in Azerbaijani",
  "recommendation": "practical advice what the driver should do",
  "what_to_say": "one polite sentence in Azerbaijani the driver can say to the officer"
}

Rules:
- Language: Clear Azerbaijani.
- Be SHORT and SPECIFIC, not a long essay.
- legal_articles: build from matched_laws, include article_code, title and fine_info.
- If no fine_info exists, write: "Cərimə: göstərilməyib".
- If matched_laws is empty or unclear, explain that the law is unclear and give very general safe advice.
- Output MUST be ONLY JSON, no additional text.
"""


def _call_ai(desc: str, matched_laws: List[dict]) -> dict:
    """
    Call OpenAI o3-mini via Responses API and return parsed JSON.
    """

    # Prepare compact law objects for the prompt
    laws_for_prompt = []
    for law in matched_laws:
        laws_for_prompt.append(
            {
                "article_code": law.get("article_code"),
                "title": law.get("title"),
                "fine_info": law.get("fine_info"),
                "summary_az": law.get("summary_az", ""),
                "full_text": law.get("full_text", ""),
                "source_ref": law.get("source_ref", ""),
            }
        )

    payload = {
        "user_description": desc,
        "matched_laws": laws_for_prompt,
    }

    # Responses API – o3-mini
    response = client.responses.create(
        model="o3-mini",   # you can change to "o1-mini" or "o1" if you have access
        input=f"{SYSTEM_PROMPT}\n\nUSER_PAYLOAD:\n{json.dumps(payload, ensure_ascii=False)}",
        max_output_tokens=400,
    )

    # Extract text from response
    try:
        output_text = response.output[0].content[0].text
    except Exception:
        # Completely unexpected shape – give safe fallback
        return {
            "legal_articles": [],
            "explanation": "AI cavabını oxumaqda problem yarandı.",
            "recommendation": "Zabitdən tətbiq etdiyi maddəni və cəriməni izah etməsini xahiş edin.",
            "what_to_say": "Zabit bəy, zəhmət olmasa tətbiq etdiyiniz maddəni və cərimə məbləğini bir daha izah edərdinizmi?",
        }

    # Try to parse JSON
    try:
        data = json.loads(output_text)
    except json.JSONDecodeError:
        # Fallback if model returned something non-JSON
        data = {
            "legal_articles": [],
            "explanation": "AI cavabını JSON formatında ala bilmədik.",
            "recommendation": "Zabitdən maddəni və cəriməni kağız üzərində tam yazmasını xahiş edin.",
            "what_to_say": "Zabit bəy, zəhmət olmasa maddəni tam şəkildə protokolda göstərərdinizmi?",
        }

    # Make sure all fields exist
    data.setdefault("legal_articles", [])
    data.setdefault("explanation", "")
    data.setdefault("recommendation", "")
    data.setdefault("what_to_say", "")

    return data


def analyze_incident(text: str) -> Tuple[List[str], str, str, str]:
    """
    Main function used by FastAPI endpoint.
    Returns: (legal_articles, explanation, recommendation, what_to_say)
    """

    text = (text or "").strip()
    if not text:
        return (
            ["Təsvir boşdur"],
            "Zəhmət olmasa yol hərəkəti ilə bağlı baş verən hadisəni öz sözlərinizlə yazın.",
            "Hadisəni mümkün qədər dəqiq təsvir edin, sonra sistemi yenidən istifadə edin.",
            "Zabit bəy, vəziyyəti düzgün izah etmək üçün mənə bir az vaxt verə bilərsinizmi?",
        )

    # 1️⃣ Try AvtoStop (best structured fines)
    matched = scraper_avtostop.search_avtostop(text)

    # 2️⃣ Try DYP website live
    if not matched:
        matched = live_scraper.search_online(text)

    # 3️⃣ Fallback to local JSON DB
    if not matched:
        matched = law_db.search_laws(text, top_k=5)

    # 4️⃣ Call AI with whatever we matched
    ai_obj = _call_ai(text, matched)

    legal_articles = ai_obj.get("legal_articles", [])
    explanation = ai_obj.get("explanation", "")
    recommendation = ai_obj.get("recommendation", "")
    what_to_say = ai_obj.get("what_to_say", "")

    # Safety fallback: if AI didn’t fill articles but we have matches
    if not legal_articles and matched:
        legal_articles = [
            f"{law.get('article_code')} — {law.get('title')} (Cərimə: {law.get('fine_info', 'N/A')})"
            for law in matched
        ]

    # Final safety defaults
    if not explanation:
        explanation = (
            "Daxil etdiyiniz təsvirə görə uyğun qanun maddəsi barədə aydın izah tapılmadı."
        )
    if not recommendation:
        recommendation = (
            "Zabitdən tətbiq etdiyi maddəni, sübutu və cərimə məbləğini aydın şəkildə izah etməsini xahiş edin."
        )
    if not what_to_say:
        what_to_say = (
            "Zabit bəy, zəhmət olmasa tətbiq etdiyiniz maddəni və cərimə məbləğini bir daha izah edərdinizmi?"
        )

    return legal_articles, explanation, recommendation, what_to_say
