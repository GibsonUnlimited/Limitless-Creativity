"""Persistent local catalog and research; no LLM dependency."""
from contextlib import contextmanager
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
import hashlib
import json
import os
import re
import sqlite3
import uuid

def data_dir():
    return Path(os.getenv("PUBLISHING_DATA_DIR", "data")).expanduser().resolve()

@contextmanager
def database():
    root = data_dir()
    root.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(root / "publishing.db", timeout=15)
    conn.row_factory = sqlite3.Row
    try:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS catalog (
            id TEXT PRIMARY KEY, kind TEXT NOT NULL CHECK(kind IN ('book','character','series')),
            title TEXT NOT NULL, summary TEXT NOT NULL, metadata_json TEXT NOT NULL DEFAULT '{}'
        );
        CREATE TABLE IF NOT EXISTS ideas (
            id TEXT PRIMARY KEY, fingerprint TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL, concept TEXT NOT NULL, target_age TEXT NOT NULL,
            product_type TEXT NOT NULL, score REAL NOT NULL CHECK(score BETWEEN 1 AND 10),
            status TEXT NOT NULL DEFAULT 'proposed', created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS research_reports (
            id TEXT PRIMARY KEY, title TEXT NOT NULL, content TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """)
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def search_catalog(query="", kind="all", limit=20):
    if kind not in {"all", "book", "character", "series"}:
        raise ValueError("kind must be all, book, character, or series")
    if not 1 <= limit <= 100:
        raise ValueError("limit must be 1..100")
    with database() as conn:
        rows = conn.execute(
            "SELECT * FROM catalog WHERE (?='all' OR kind=?) AND "
            "(instr(lower(title),lower(?))>0 OR instr(lower(summary),lower(?))>0) "
            "ORDER BY title LIMIT ?", (kind, kind, query, query, limit)).fetchall()
    return [dict(r) for r in rows]

def list_ideas(limit=20):
    if not 1 <= limit <= 100:
        raise ValueError("limit must be 1..100")
    with database() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM ideas ORDER BY score DESC, created_at DESC LIMIT ?", (limit,))]

def save_idea(title, concept, target_age, product_type, score):
    if not all(s.strip() for s in (title, concept, target_age, product_type)):
        raise ValueError("Idea fields cannot be blank")
    if not 1 <= score <= 10:
        raise ValueError("score must be 1..10")
    fingerprint = hashlib.sha256((title.strip().casefold() + "|" + concept.strip().casefold()).encode()).hexdigest()
    with database() as conn:
        conn.execute("INSERT OR IGNORE INTO ideas VALUES (?,?,?,?,?,?,?, 'proposed',?)",
                     (uuid.uuid4().hex, fingerprint, title.strip(), concept.strip(), target_age,
                      product_type, score, datetime.now(timezone.utc).isoformat()))
        return dict(conn.execute("SELECT * FROM ideas WHERE fingerprint=?", (fingerprint,)).fetchone())

def save_report(title, content):
    if not title.strip() or not content.strip():
        raise ValueError("Report title and content cannot be blank")
    report_id = uuid.uuid4().hex
    with database() as conn:
        conn.execute("INSERT INTO research_reports VALUES (?,?,?,?)",
                     (report_id, title, content, datetime.now(timezone.utc).isoformat()))
    return {"report_id": report_id, "storage": str(data_dir() / "publishing.db")}

def originality_check(text, limit=5):
    if not text.strip():
        raise ValueError("Text cannot be blank")
    if not 1 <= limit <= 20:
        raise ValueError("limit must be 1..20")
    words = set(re.findall(r"\w+", text.casefold()))
    matches = []
    with database() as conn:
        rows = conn.execute("SELECT id,title,summary FROM catalog").fetchall()
        ideas = conn.execute("SELECT id,title,concept AS summary FROM ideas").fetchall()
    for source, records in (("catalog", rows), ("ideas", ideas)):
        for row in records:
            candidate = row["title"] + " " + row["summary"]
            other = set(re.findall(r"\w+", candidate.casefold()))
            similarity = max(len(words & other) / max(1, len(words | other)),
                             SequenceMatcher(None, text.casefold(), candidate.casefold()).ratio())
            matches.append({"source": source, "id": row["id"], "title": row["title"],
                            "similarity": round(similarity, 3)})
    return {"scope": "Local titles, summaries and idea concepts only; no manuscript or web scan. "
                     "This heuristic is not plagiarism detection, rights clearance or proof of originality.",
            "records_checked": len(rows) + len(ideas),
            "matches": sorted(matches, key=lambda x: x["similarity"], reverse=True)[:limit]}

def import_catalog(path):
    records = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("Catalog JSON must be a list")
    with database() as conn:
        for row in records:
            if row.get("kind") not in {"book", "character", "series"}:
                raise ValueError("Invalid catalog kind")
            if not all(isinstance(row.get(k), str) and row[k].strip() for k in ("id", "title", "summary")):
                raise ValueError("Each record needs id, title, summary strings")
            conn.execute("INSERT INTO catalog VALUES (?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET "
                         "kind=excluded.kind,title=excluded.title,summary=excluded.summary,metadata_json=excluded.metadata_json",
                         (row["id"], row["kind"], row["title"], row["summary"], json.dumps(row.get("metadata", {}))))
    return len(records)
