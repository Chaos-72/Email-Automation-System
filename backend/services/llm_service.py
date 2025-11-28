# backend/services/llm_service.py
import json
from typing import Any, Dict
import os, re
import dateparser
from datetime import datetime


# from langchain.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from tavily import TavilyClient
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# ChatOpenAI reads OPENAI_API_KEY from env automatically if set


# Helpers for festival date extraction and lookup
def _extract_date_from_text(text: str):
    """Try to pull a single date string (YYYY-MM-DD or human readable) from arbitrary text.
    Returns an ISO date string (YYYY-MM-DD) or None.
    """
    if not text:
        return None
    # Try to find YYYY-MM-DD first
    m = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", text)
    if m:
        return m.group(1)
    # Try common human-readable dates like 'October 21, 2025' or '21 October 2025'
    m = re.search(r'([A-Za-z]+ \d{1,2},? \d{4})', text)
    if not m:
        m = re.search(r'(\d{1,2} [A-Za-z]+ \d{4})', text)
    if m:
        parsed = dateparser.parse(m.group(1), settings={'TIMEZONE': 'Asia/Kolkata'})
        if parsed:
            return parsed.date().isoformat()
    # Try dateparser.search to find dates embedded in longer text
    try:
        found = dateparser.search.search_dates(text, settings={'TIMEZONE': 'Asia/Kolkata'})
        if found and len(found) > 0:
            return found[0][1].date().isoformat()
    except Exception:
        pass
    return None


def _lookup_festival_date(festival_name: str):
    """Query Tavily for festival dates, preferring the nearest future occurrence.
    Tries current year first, then next year. Returns an ISO date string YYYY-MM-DD or None.
    """
    if not festival_name:
        return None
    festival_name = festival_name.strip()
    today = datetime.now().date()
    current_year = today.year

    # small local fallback mapping (only for common festivals)
    local_fallbacks = {
        "diwali": f"{current_year}-10-21",
        "holi":   f"{current_year}-03-25",
    }

    tc = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    # try current year then next year
    for yr in (current_year, current_year + 1):
        queries = [
            f"Date of {festival_name} in {yr} in India",
            f"{festival_name} {yr} date in India",
            f"{festival_name} {yr} date"
        ]
        for q in queries:
            try:
                res = tc.search(q)
            except Exception:
                res = None
            if not res:
                continue
            results = res.get("results") or []
            for r in results:
                text = r.get("content") or r.get("title") or (r.get("raw_content") or "")
                dt_str = _extract_date_from_text(text)
                if not dt_str:
                    continue
                # parse to date and ensure it's in the requested year and in the future
                parsed = dateparser.parse(dt_str, settings={'TIMEZONE': 'Asia/Kolkata'})
                if not parsed:
                    continue
                parsed_date = parsed.date()
                if parsed_date.year != yr:
                    # still accept if parsed_date is in the future and >= today
                    if parsed_date >= today:
                        return parsed_date.isoformat()
                    continue
                if parsed_date >= today:
                    return parsed_date.isoformat()

    # fallback: if local_fallbacks for current year is in the past, try next year
    key = festival_name.lower()
    fb = local_fallbacks.get(key)
    if fb:
        parsed = dateparser.parse(fb, settings={'TIMEZONE': 'Asia/Kolkata'})
        if parsed and parsed.date() >= today:
            return parsed.date().isoformat()
        # try next year fallback
        parsed_next = dateparser.parse(fb.replace(str(current_year), str(current_year + 1)), settings={'TIMEZONE': 'Asia/Kolkata'})
        if parsed_next:
            return parsed_next.date().isoformat()

    return None


# Helper function to fix datetime strings

def fix_datetime(datetime_str: str) -> str:
    dt = dateparser.parse(
        datetime_str, 
        settings={
            'PREFER_DATES_FROM': 'future',
            "RELATIVE_BASE": datetime.now(),
            "RETURN_AS_TIMEZONE_AWARE": True,
            "TIMEZONE": "Asia/Kolkata"
        }
    )

    # If failed to parse, try detecting festival names dynamically

    if dt is None:
        pattern = re.compile(r"\b(after|on|before)?\s*(diwali|holi|makar\s*sankranti|eid|raksha\s*bandhan|pongal|christmas)\b", re.I)
        match = pattern.search(datetime_str)
        if match:
            festival = match.group(2)
            # Use lookup helper which prefers future occurrences (current year, then next year)
            festival_date = _lookup_festival_date(festival)
            if festival_date:
                # parse ISO date (YYYY-MM-DD) into timezone-aware datetime
                dt = dateparser.parse(festival_date, settings={
                    'TIMEZONE': 'Asia/Kolkata',
                    'RETURN_AS_TIMEZONE_AWARE': True
                })
                
    return dt.isoformat() if dt else None


# Low temperature for deterministic outputs in demo
llm = ChatGoogleGenerativeAI(temperature=0.2, model='gemini-2.5-flash')

# Intent parser: returns JSON with keys intent, details
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

# Email generator chain
email_template = PromptTemplate.from_template(
    "You are a professional email writer. Compose a concise, clear email. Sign off as Ravi Bhagat.\n"
    "Instruction: {instruction}\n"
    "Recipient: {recipient}\n\n"
    "Return JSON only:\n"
    '{{\"subject\":\"...\",\"body_html\":\"...\",\"body_text\":\"...\"}}'
)
email_chain = LLMChain(llm=llm, prompt=email_template)

def generate_email(instruction: str, recipient: Dict[str, Any] = None) -> Dict[str, str]:
    recipient_json = json.dumps(recipient) if recipient else "{}"
    raw = email_chain.run({"instruction": instruction, "recipient": recipient_json})
    try:
        parsed = json.loads(raw)
    except Exception:
        import re
        m = re.search(r"(\{.*\})", raw, re.S)
        if m:
            parsed = json.loads(m.group(1))
        else:
            raise ValueError(f"Failed to parse email JSON from LLM output. Raw: {raw}")
        

    # --- NEW: Fix datetime for create_event ---
    if parsed.get("intent") == "create_event" and "details" in parsed:
        details = parsed["details"]
        if "datetime" in details and details["datetime"]:
            fixed_dt = fix_datetime(details["datetime"])
            details["datetime"] = fixed_dt  # replace with ISO datetime
    return parsed
