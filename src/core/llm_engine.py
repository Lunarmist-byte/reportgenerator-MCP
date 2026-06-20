import json
import os
from openai import OpenAI
import google.generativeai as genai

def generate_report(settings, notes, report_type, csv_data=None):
    provider = settings.get("default_model", "openai")
    
    prompt = f"""You are a professional report generator. 
User Notes:
{notes}

Report Type: {report_type}

"""
    if csv_data:
        prompt += f"\nAdditional Data (CSV):\n{csv_data}\n"
        
    prompt += """
Generate a comprehensive, formal report.
You must return the response EXCLUSIVELY as a valid JSON object with the following schema:
{
    "title": "A suitable title for the report",
    "date": "Today's date",
    "paragraphs": ["Paragraph 1 text", "Paragraph 2 text", ...],
    "table": {
        "headers": ["Column 1", "Column 2"],
        "rows": [["Row 1 Col 1", "Row 1 Col 2"], ["Row 2 Col 1", "Row 2 Col 2"]]
    }
}
If no table is needed, set "table" to null. If it's a financial report or CSV is provided, definitely create a table.
Do NOT output Markdown. Output strictly JSON.
"""

    if provider == "openai":
        client = OpenAI(api_key=settings.get("openai_api_key"))
        response = client.chat.completions.create(
            model="gpt-4o", # or standard gpt-3.5-turbo if needed, let's stick to gpt-4o for best results
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
            model="anthropic/claude-3-haiku", # reasonable fast model on OR
            messages=[{"role": "user", "content": prompt}]
        )
        # Claude might not support response_format type json natively on OR without specific models,
        # but we can parse the string.
        content = response.choices[0].message.content
        # Strip code blocks
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
