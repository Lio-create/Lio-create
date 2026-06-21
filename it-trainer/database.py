import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "tickets.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            difficulty TEXT,
            category TEXT,
            subject TEXT,
            priority TEXT,
            reporter TEXT,
            department TEXT,
            device TEXT,
            description TEXT,
            note TEXT,
            tools TEXT,
            lernziel TEXT,
            errors TEXT,
            questions TEXT,
            powershell TEXT,
            score INTEGER DEFAULT NULL,
            grade TEXT DEFAULT NULL,
            solved INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()
    print("[DB] Datenbank initialisiert")

def save_ticket(ticket: dict):
    conn = get_db()
    conn.execute("""
        INSERT OR REPLACE INTO tickets
        (id, created_at, difficulty, category, subject, priority, reporter,
         department, device, description, note, tools, lernziel, errors,
         questions, powershell, score, grade, solved)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        ticket.get("id"),
        ticket.get("created_at", datetime.now().isoformat()),
        ticket.get("difficulty"),
        ticket.get("category"),
        ticket.get("subject"),
        ticket.get("priority"),
        ticket.get("reporter"),
        ticket.get("department"),
        ticket.get("device"),
        ticket.get("description"),
        ticket.get("note"),
        json.dumps(ticket.get("tools", []), ensure_ascii=False),
        ticket.get("lernziel"),
        json.dumps(ticket.get("errors", []), ensure_ascii=False),
        json.dumps(ticket.get("questions", []), ensure_ascii=False),
        ticket.get("powershell"),
        ticket.get("score"),
        ticket.get("grade"),
        1 if ticket.get("solved") else 0
    ))
    conn.commit()
    conn.close()

def update_score(ticket_id: str, score: int, grade: str):
    conn = get_db()
    conn.execute("""
        UPDATE tickets SET score=?, grade=?, solved=1 WHERE id=?
    """, (score, grade, ticket_id))
    conn.commit()
    conn.close()

def get_all_tickets():
    conn = get_db()
    rows = conn.execute("""
        SELECT * FROM tickets ORDER BY created_at DESC
    """).fetchall()
    conn.close()
    result = []
    for row in rows:
        t = dict(row)
        t["tools"] = json.loads(t["tools"] or "[]")
        t["errors"] = json.loads(t["errors"] or "[]")
        t["questions"] = json.loads(t["questions"] or "[]")
        result.append(t)
    return result

def get_ticket(ticket_id: str):
    conn = get_db()
    row = conn.execute("SELECT * FROM tickets WHERE id=?", (ticket_id,)).fetchone()
    conn.close()
    if not row:
        return None
    t = dict(row)
    t["tools"] = json.loads(t["tools"] or "[]")
    t["errors"] = json.loads(t["errors"] or "[]")
    t["questions"] = json.loads(t["questions"] or "[]")
    return t

def get_stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
    solved = conn.execute("SELECT COUNT(*) FROM tickets WHERE solved=1").fetchone()[0]
    avg_score = conn.execute("SELECT AVG(score) FROM tickets WHERE score IS NOT NULL").fetchone()[0]
    by_difficulty = conn.execute("""
        SELECT difficulty, COUNT(*) as count, AVG(score) as avg_score
        FROM tickets GROUP BY difficulty
    """).fetchall()
    conn.close()
    return {
        "total": total,
        "solved": solved,
        "avg_score": round(avg_score or 0, 1),
        "by_difficulty": [dict(r) for r in by_difficulty]
    }

init_db()
