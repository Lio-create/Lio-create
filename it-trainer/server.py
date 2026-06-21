import anthropic
import uvicorn
import json
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from database import save_ticket, update_score, get_all_tickets, get_ticket, get_stats, init_db
from vm_agent import prepare_vm, vm_status as get_vm_status_raw

API_KEY = ""  # <-- hier deinen Key eintragen


init_db()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
client = anthropic.Anthropic(api_key=API_KEY)

class MessageRequest(BaseModel):
    system: str
    user: str

class VMRequest(BaseModel):
    script: str
    restore_snapshot: bool = False
    snapshot_name: str = "Sauber"

class SaveTicketRequest(BaseModel):
    ticket: dict

class ScoreRequest(BaseModel):
    ticket_id: str
    score: int
    grade: str

def clean_json(text):
    text = text.strip()
    text = re.sub(r'^```json\s*', '', text)
    text = re.sub(r'^```\s*', '', text)
    text = re.sub(r'```\s*$', '', text)
    return text.strip()

@app.post("/api/ticket")
async def generate_ticket(req: MessageRequest):
    try:
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=req.system,
            messages=[{"role": "user", "content": req.user}]
        )
        text = clean_json(msg.content[0].text)
        data = json.loads(text)
        return {"ok": True, "data": data}
    except json.JSONDecodeError as e:
        return JSONResponse({"ok": False, "error": f"JSON-Fehler: {str(e)}"}, status_code=200)
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

@app.post("/api/script")
async def generate_script(req: MessageRequest):
    try:
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=req.system,
            messages=[{"role": "user", "content": req.user}]
        )
        text = msg.content[0].text.strip()
        text = re.sub(r'^```powershell\s*', '', text)
        text = re.sub(r'^```\s*', '', text)
        text = re.sub(r'```\s*$', '', text)
        return {"ok": True, "script": text.strip()}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

@app.post("/api/evaluate")
async def evaluate(req: MessageRequest):
    try:
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            system=req.system,
            messages=[{"role": "user", "content": req.user}]
        )
        text = clean_json(msg.content[0].text)
        data = json.loads(text)
        return {"ok": True, "data": data}
    except json.JSONDecodeError as e:
        return JSONResponse({"ok": False, "error": f"JSON-Fehler: {str(e)}"}, status_code=200)
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

@app.post("/api/tickets/save")
async def save_ticket_endpoint(req: SaveTicketRequest):
    try:
        save_ticket(req.ticket)
        return {"ok": True}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

@app.get("/api/tickets")
async def list_tickets():
    try:
        tickets = get_all_tickets()
        return {"ok": True, "tickets": tickets}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

@app.get("/api/tickets/{ticket_id}")
async def get_single_ticket(ticket_id: str):
    try:
        ticket = get_ticket(ticket_id)
        if not ticket:
            return JSONResponse({"ok": False, "error": "Nicht gefunden"}, status_code=404)
        return {"ok": True, "ticket": ticket}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

@app.post("/api/tickets/score")
async def save_score(req: ScoreRequest):
    try:
        update_score(req.ticket_id, req.score, req.grade)
        return {"ok": True}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

@app.get("/api/stats")
async def statistics():
    try:
        stats = get_stats()
        return {"ok": True, "stats": stats}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


class ChatRequest(BaseModel):
    system: str
    history: list
    message: str

@app.post("/api/chat")
async def chat(req: ChatRequest):
    try:
        messages = []
        for msg in req.history[:-1]:  # letzte Nachricht kommt separat
            if msg.get("role") in ["user", "assistant"]:
                messages.append({"role": msg["role"], "content": msg["content"]})
        # Aktuelle Nachricht
        messages.append({"role": "user", "content": req.message})

        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=400,
            system=req.system,
            messages=messages
        )
        return {"ok": True, "text": msg.content[0].text}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

@app.post("/api/vm/prepare")
async def vm_prepare(req: VMRequest):
    result = prepare_vm(req.script, req.restore_snapshot, req.snapshot_name)
    return result

@app.get("/api/vm/status")
async def vm_status():
    try:
        status = get_vm_status_raw()
        return {"ok": True, "status": status}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.get("/")
async def root():
    return FileResponse("index.html")

if __name__ == "__main__":
    print("\n✓ IT Trainer läuft auf http://localhost:8000\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
