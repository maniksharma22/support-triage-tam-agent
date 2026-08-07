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
    
    for root, dirs, files in os.walk(kb_path):
        for file in files:
            if file.endswith((".md", ".txt")):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if any(word in content.lower() for word in query.lower().split() if len(word) > 3):
                            return f"Reference from {file}: {content[:300]}..."
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
    
    kb_snippet = search_knowledge_base(ticket_text)
    
    prompt = f"""
    Analyze the following support ticket and return a JSON object with:
    - urgency_tier (P1, P2, P3, or P4)
    - category (e.g., Billing, Software Issue, Onboarding, Troubleshooting)
    - suggested_response (a helpful response incorporating this KB snippet: {kb_snippet})
    - routing_team (e.g., Engineering Escalations, Billing Support, Product Support, General Support)

    Ticket: {ticket_text}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={
                'response_mime_type': 'application/json'
            }
        )
        return json.loads(response.text)
    except Exception:
        return {
            "urgency_tier": "P4",
            "category": "General",
            "suggested_response": f"We have received your request. {kb_snippet}",
            "routing_team": "General Support"
        }

def process_query(user_query: str) -> str:
    if not user_query:
        return "Please provide a query."
    
    kb_result = search_knowledge_base(user_query)
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=f"Answer the user query based on this reference info: {kb_result}\n\nQuery: {user_query}",
    )
    return response.text