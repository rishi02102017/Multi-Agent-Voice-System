from fastapi import FastAPI, Request
import requests

app = FastAPI()

# Airtable Config
AIRTABLE_API_KEY = "patvgVW87r3FUDb2O.93b9d1fa9b59a2768f6cbee984e1e700d8e406ef29ac603341f9436fa01c3b1f"
BASE_ID = "appWWsoUnzdxBcWA1"
TABLE_NAME = "Call_Records"  # Can use "Leads" in place of "Call_Records"
AIRTABLE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"

HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}


#  GET route for browser ping
@app.get("/")
def welcome():
    return {"message": "Webhook server is live!"}


#  POST webhook endpoint
@app.post("/webhook")
async def receive_webhook(request: Request):
    data = await request.json()
    print("Webhook received:", data)

    # Extract safely from nested JSON (based on actual Vapi format)
    call_id = data.get("call", {}).get("id", "vapi-call-xxxx")
    phone_number = data.get("phone", "+91XXXXXXXXXX")
    start_time = data.get("createdAt", "2025-04-07T00:00:00Z")
    end_time = data.get("updatedAt", "2025-04-07T00:01:00Z")

    # Extract last assistant message as transcript
    messages = data.get("message", {}).get("artifact", {}).get("messages", [])
    transcript = messages[-1].get("message", "Hi! This is Maya from Interia..."
                                  ) if messages else "No transcript available"

    # Airtable record format
    airtable_payload = {
        "records": [{
            "fields": {
                "callproviderID": call_id,
                "phonenumberID": "vapi-agent-001",
                "customernumber": phone_number,
                "type": "outbound",
                "started": start_time,
                "ended": end_time,
                "milliseconds": 70000,  # placeholder
                "cost": 1.3,  # placeholder
                "end reason": "Client confirmed design discussion",
                "transcript": transcript
            }
        }]
    }

    response = requests.post(AIRTABLE_URL,
                             json=airtable_payload,
                             headers=HEADERS)
    print("Airtable response:", response.status_code, response.text)

    return {"status": "success"}
