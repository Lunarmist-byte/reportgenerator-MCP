import json
import os
from openai import OpenAI
import google.generativeai as genai

def test_api_key(provider, key):
    try:
        if not key.strip():
            return False, "API key is empty."
            
        if provider == "openai":
            client = OpenAI(api_key=key.strip())
            client.models.list()
            return True, "Success! Connected to OpenAI."
            
        elif provider == "openrouter":
            import requests
            response = requests.get(
                "https://openrouter.ai/api/v1/auth/key",
                headers={"Authorization": f"Bearer {key.strip()}"}
            )
            if response.status_code == 200:
                return True, "Success! Connected to OpenRouter."
            else:
                return False, f"Invalid API key (Status: {response.status_code})"
                
        elif provider == "gemini":
            genai.configure(api_key=key.strip())
            models = list(genai.list_models())
            return True, "Success! Connected to Google Gemini."
            
    except Exception as e:
        return False, f"Error: {str(e)}"
    return False, "Unknown provider."

def generate_report(settings, notes, report_type, csv_data=None):
    provider = settings.get("default_model", "openai")
    
    prompt = f"""You are a professional report generator. 
User Notes:
{notes}

Report Type: {report_type}

"""
    if csv_data:
        prompt += f"\nAdditional Data (CSV):\n{csv_data}\n"
        
    if report_type == "Financial":
        table_schema = ',\n    "table": {\n        "headers": ["Column 1", "Column 2"],\n        "rows": [["Row 1 Col 1", "Row 1 Col 2"], ["Row 2 Col 1", "Row 2 Col 2"]]\n    }'
        table_instruction = 'You MUST include a "table" key with the formatted data.'
    else:
        table_schema = ''
        table_instruction = 'Do NOT include a "table" key. Only generate text paragraphs.'

    prompt += f"""
Generate a comprehensive, formal report.
You must return the response EXCLUSIVELY as a valid JSON object with the following schema:
{{
    "title": "A suitable title for the report",
    "date": "Today's date",
    "paragraphs": ["Paragraph 1 text", "Paragraph 2 text", ...]{table_schema}
}}
{table_instruction}
Do NOT output Markdown. Output strictly JSON.
"""

    if provider == "openai":
        client = OpenAI(api_key=settings.get("openai_api_key"))
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
        
    elif provider == "openrouter":
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.get("openrouter_api_key")
        )
        response = client.chat.completions.create(
            model=settings.get("openrouter_model", "anthropic/claude-3-haiku"),
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content
        if content.startswith("```json"):
            content = content.split("```json")[1].split("```")[0].strip()
        return json.loads(content)
        
    elif provider == "gemini":
        genai.configure(api_key=settings.get("gemini_api_key"))
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(prompt)
        content = response.text
        if content.startswith("```json"):
            content = content.split("```json")[1].split("```")[0].strip()
        elif content.startswith("```"):
            content = content.split("```")[1].split("```")[0].strip()
        return json.loads(content)
    
    return None
