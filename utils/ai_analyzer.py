import openai, json
PROMPT_TEMPLATE = """You are an assistant that analyzes a list of telegram messages (text only).
Input: JSON list of messages with fields: id, date, sender, text.
Tasks:
1) Return TOP-3 themes with percentage distribution and 2 example messages each.
2) Return TOP-3 sentiments (positive/neutral/negative/other) with percentages and 2 example messages each.
3) Provide 1-2 actionable insights (concise).
Output JSON with keys: text (human-readable short report), themes, sentiments, insights.
Be concise.
"""

class Analyzer:
    def __init__(self, openai_key):
        openai.api_key = openai_key

    def analyze_messages(self, messages, top_n=3):
        sample = messages[:1000]
        payload = PROMPT_TEMPLATE + "\n\n" + json.dumps(sample[:500], ensure_ascii=False)
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role":"system","content":"You are a helpful analyst."},
                      {"role":"user","content":payload}],
            max_tokens=800,
            temperature=0.2
        )
        text = resp['choices'][0]['message']['content']
        out = {"text": text}
        try:
            import re
            m = re.search(r"\{.+\}", text, flags=re.S)
            if m:
                j = json.loads(m.group(0))
                out.update(j)
        except Exception:
            pass
        return out

