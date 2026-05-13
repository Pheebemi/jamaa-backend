from django.conf import settings
import json
import re


def analyze_case(case_id: str):
    try:
        from google import genai
        from apps.cases.models import Case

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        case = Case.objects.get(id=case_id)

        if case.is_sensitive:
            prompt = (
                f"Case type: {case.type}. Priority: {case.priority}. "
                f"Analyze risk level only. Respond in JSON with keys: "
                f"summary, category, priority, urgency_score, suggested_action."
            )
        else:
            prompt = f"""You are a humanitarian case management assistant.
Analyze the following case and respond ONLY in JSON with these exact keys:
- summary (string, max 2 sentences)
- category (one of: child_absenteeism, malnutrition, flood_impact, medical, emergency, child_protection, other)
- priority (one of: high, medium, low)
- urgency_score (integer 1-10)
- suggested_action (string, one actionable sentence)

Case title: {case.title}
Case description: {case.description}
Case type: {case.type}"""

        import time
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=prompt,
                )
                break
            except Exception as e:
                if '429' in str(e) and attempt < 2:
                    time.sleep(10 * (attempt + 1))
                else:
                    raise

        text = response.text.strip()
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if not json_match:
            return
        result = json.loads(json_match.group())

        case.ai_summary          = result.get('summary', '')
        case.ai_category         = result.get('category', '')
        case.ai_priority         = result.get('priority', '')
        case.ai_urgency_score    = result.get('urgency_score')
        case.ai_suggested_action = result.get('suggested_action', '')
        case.save(update_fields=[
            'ai_summary', 'ai_category', 'ai_priority',
            'ai_urgency_score', 'ai_suggested_action',
        ])
    except Exception:
        pass
