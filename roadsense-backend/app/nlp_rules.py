from typing import List, Tuple

def analyze_incident(description: str) -> Tuple[List[str], str, str, str]:

    text = description.lower()

    articles = []
    explanation_parts = []
    recommendation = ""
    what_to_say = ""

    if "seatbelt" in text or "kəmər" in text:
        articles.append("Seatbelt rule – Article X.Y")
        explanation_parts.append(
            "Sürücünün və sərnişinlərin təhlükəsizlik kəmərindən istifadə etməsi məcburidir."
        )
        recommendation = "Cərimə düzgündürsə, ödəyin; əks halda, sübut tələb edin."
        what_to_say = (
            "Zəhmət olmasa, mənə konkret maddəni və video/foto sübutu göstərin."
        )

    if "speed" in text or "sürət" in text:
        articles.append("Speeding rule – Article Z.T")
        explanation_parts.append(
            "Yol nişanları ilə müəyyən edilmiş sürət həddinin aşılması inzibati xətadır."
        )
        if not recommendation:
            recommendation = "Sürət həddini aşıbsınızsa, cəriməni qəbul edin; əks halda, radar sübutu tələb edin."
        if not what_to_say:
            what_to_say = (
                "Xahiş edirəm radar ölçümünün nəticəsini və cihazın kalibrlənmə sənədini göstərin."
            )

    if not articles:
        articles.append("No specific article detected")
        explanation_parts.append(
            "Mətnə əsasən konkret qayda tapılmadı. Daha ətraflı məlumat verməyiniz tövsiyə olunur."
        )
        recommendation = "Əmin deyilsinizsə, əlavə məlumat yazın və ya hüquqşünasla məsləhətləşin."
        what_to_say = (
            "Xahiş edirəm, mənə konkret hansı maddəyə əsasən cərimə yazıldığını izah edin."
        )

    explanation = " ".join(explanation_parts)
    return articles, explanation, recommendation, what_to_say
