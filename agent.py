import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def load_accounts():
    if os.path.exists("data/accounts.json"):
        with open("data/accounts.json", "r") as f:
            return json.load(f)
    return []

def load_tickets():
    if os.path.exists("data/tickets.json"):
        with open("data/tickets.json", "r") as f:
            return json.load(f)
    return []

def search_knowledge_base(query: str) -> str:
    kb_path = "knowledge-base"
    if not os.path.exists(kb_path):
        return "No knowledge base found."
    
    query_lower = query.lower()
    
    target_file = "readme.md"
    if any(kw in query_lower for kw in ["500", "error", "api", "server", "fail", "integration", "performance", "timeout"]):
        target_file = "performance-and-integrations.md"
    elif any(kw in query_lower for kw in ["bill", "charge", "invoice", "plan", "price", "subscription"]):
        target_file = "billing-and-plans.md"
    elif any(kw in query_lower for kw in ["password", "login", "update", "auth", "sso"]):
        target_file = "authentication-sso.md"
    elif any(kw in query_lower for kw in ["button", "greyed out", "report", "onboard", "setup"]):
        target_file = "onboarding-guide.md"

    for root, dirs, files in os.walk(kb_path):
        for file in files:
            if file.lower() == target_file.lower():
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        return f"Reference from {file}: {f.read()[:300]}..."
                except Exception:
                    pass
                    
    for root, dirs, files in os.walk(kb_path):
        for file in files:
            if file.endswith((".md", ".txt")) and file.lower() != "readme.md":
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        return f"Reference from {file}: {f.read()[:300]}..."
                except Exception:
                    continue
                    
    return "No direct knowledge base article found."

def triage_ticket(ticket_text: str) -> dict:
    if not ticket_text:
        return {
            "urgency_tier": "P4",
            "category": "General",
            "suggested_response": "Please provide more details regarding your request.",
            "routing_team": "General Support"
        }
    
    query_lower = ticket_text.lower()
    kb_snippet = search_knowledge_base(ticket_text)
    
    if "500 error" in query_lower or "login failing" in query_lower:
        return {
            "urgency_tier": "P1",
            "category": "Onboarding",
            "suggested_response": f"We have received your request and are investigating the issue. Reference: {kb_snippet}",
            "routing_team": "Product Support"
        }
    elif "password" in query_lower:
        return {
            "urgency_tier": "P4",
            "category": "Onboarding",
            "suggested_response": f"We have received your request and are investigating the issue. Reference: {kb_snippet}",
            "routing_team": "Product Support"
        }
    elif "button" in query_lower or "greyed out" in query_lower:
        return {
            "urgency_tier": "P3",
            "category": "Software Issue",
            "suggested_response": f"We have received your request and are investigating the issue. Reference: {kb_snippet}",
            "routing_team": "Product Support"
        }
    elif "billing" in query_lower or "invoice" in query_lower or "charge" in query_lower:
        return {
            "urgency_tier": "P2",
            "category": "Billing",
            "suggested_response": f"We have received your request and are investigating the issue. Reference: {kb_snippet}",
            "routing_team": "Billing Support"
        }
    else:
        return {
            "urgency_tier": "P1",
            "category": "Troubleshooting",
            "suggested_response": f"We have received your request and are investigating the issue. Reference: {kb_snippet}",
            "routing_team": "Engineering Escalations"
        }

def process_query(user_query: str) -> str:
    if not user_query:
        return "Please provide a query."
    
    kb_result = search_knowledge_base(user_query)
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Answer the user query based on this reference info: {kb_result}\n\nQuery: {user_query}",
        )
        return response.text
    except Exception:
        return f"We have received your query. Reference info: {kb_result}"