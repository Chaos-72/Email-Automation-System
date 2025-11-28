# test_parse_intent.py
import os
import json
from typing import Dict, Any
import dateparser
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# -------------------------------
# Helper function to fix datetime
# -------------------------------
def fix_datetime(datetime_str: str) -> str:
    dt = dateparser.parse(datetime_str, settings={'PREFER_DATES_FROM': 'future'})
    if dt is None:
        return datetime_str
    return dt.isoformat()

# -------------------------------
# Setup LLM
# -------------------------------
llm = ChatGoogleGenerativeAI(temperature=0.2, model='gemini-2.5-flash')

# -------------------------------
# Prompt template
# -------------------------------
intent_prompt = PromptTemplate.from_template(
    "You are a structured assistant. Parse the user instruction into JSON.\n"
    "User Input: {prompt}\n\n"
    "Return JSON only with keys:\n"
    "- intent: one of create_event | send_email | bulk_send\n"
    "- details: object with relevant fields depending on intent\n\n"
    "Example output:\n"
    '{{"intent":"create_event","details":{{"title":"...","datetime":"tomorrow at 11:00 AM","attendees":["a@b.com"],"cancel_conflicts":true}}}}'
)

intent_chain = LLMChain(llm=llm, prompt=intent_prompt)

# -------------------------------
# Function to parse intent
# -------------------------------
def parse_intent(prompt_text: str) -> Dict[str, Any]:
    raw = intent_chain.run({"prompt": prompt_text})
    
    try:
        parsed = json.loads(raw)
    except Exception:
        import re
        m = re.search(r"(\{.*\})", raw, re.S)
        if m:
            parsed = json.loads(m.group(1))
        else:
            raise ValueError(f"LLM did not return JSON. Raw: {raw}")
    
    # Fix datetime if intent is create_event
    if parsed.get("intent") == "create_event" and "details" in parsed:
        details = parsed["details"]
        if "datetime" in details:
            details["datetime"] = fix_datetime(details["datetime"])
    
    return parsed

# -------------------------------
# Independent test
# -------------------------------
if __name__ == "__main__":
    test_prompts = [
        "Create event for Diwali Holiday meeting tomorrow at 1pm.",
        "Send email to John about project updates.",
        "Schedule team lunch next Friday at 12:30 PM."
    ]
    
    for prompt in test_prompts:
        result = parse_intent(prompt)
        print(f"\nPrompt: {prompt}")
        print("Parsed JSON:")
        print(json.dumps(result, indent=4))
