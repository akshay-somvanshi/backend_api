"""
generate_suggestions — Nightly suggestion chip generator.

Triggered by Cloud Scheduler at midnight via:
    POST /generate-suggestions
    Header: X-Cron-Secret: <value of CRON_SECRET env var>

For each user in Firestore:
  1. Reads their profile (company, industry, team, etc.)
  2. Reads messages from their most recent session(s)
  3. Calls Gemini to produce 4 typed suggestion chips
  4. Deletes the user's existing suggestions from the `suggestions` collection
  5. Writes 4 new documents with TTL (expires_at = now + 25h)

Chip types match the app's existing chip vocabulary:
  "Sustainability 101" | "Plan" | "Analyse" | "In the news"

New users with no conversation history get profile-based chips only.
"""

import os
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Header, HTTPException
from google.cloud import firestore as firestore_module
from google import genai
from ...db.client_init import get_firestore

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GOOGLE_PROJECT_ID    = os.getenv("GOOGLE_PROJECT_ID", "dash-beta-e61d0")
GEMINI_LOCATION      = os.getenv("GEMINI_LOCATION", "europe-west1")
GEMINI_MODEL         = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
CRON_SECRET          = os.getenv("CRON_SECRET", "")   # set in Cloud Run env vars

MAX_WORKERS              = 5    # parallel Gemini calls
MAX_SESSIONS_TO_READ     = 3    # how many recent sessions to look back
MAX_MESSAGES_PER_SESSION = 12   # messages pulled from each session
SUGGESTIONS_TTL_HOURS    = 25   # expire just after the next nightly run

CHIP_TYPES = ["Sustainability 101", "Plan", "Analyse", "In the news"]

# ---------------------------------------------------------------------------
# Clients (initialised once at import time)
# ---------------------------------------------------------------------------

db = get_firestore()

gemini_client = genai.Client(
    vertexai=True,
    project=GOOGLE_PROJECT_ID,
    location=GEMINI_LOCATION,
)

router = APIRouter()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Firestore helpers
# ---------------------------------------------------------------------------

def _get_user_profile(user_id: str) -> dict:
    """Return the users/{user_id} document as a dict, or {} on failure."""
    try:
        doc = db.collection("users").document(user_id).get()
        return doc.to_dict() or {}
    except Exception as e:
        logger.warning("Could not read profile for %s: %s", user_id, e)
        return {}


def _get_recent_messages(user_id: str) -> list[dict]:
    """
    Return a flat list of recent {role, content} dicts from the user's
    most recent sessions (newest first, up to MAX_SESSIONS_TO_READ).
    Returns [] if the user has no history yet.
    """
    try:
        sessions_ref = (
            db.collection("messages")
            .document(user_id)
            .collection("sessions")
        )
        # Session IDs are YYYYMMDD — lexicographic sort gives newest last.
        session_docs = sorted(
            sessions_ref.list_documents(),
            key=lambda d: d.id,
            reverse=True,
        )[:MAX_SESSIONS_TO_READ]

        messages = []
        for session_ref in session_docs:
            msgs = (
                session_ref.collection("messages")
                .order_by("timestamp", direction=firestore_module.Query.DESCENDING)
                .limit(MAX_MESSAGES_PER_SESSION)
                .stream()
            )
            for m in msgs:
                data = m.to_dict()
                content = data.get("content", "")
                if isinstance(content, list):
                    content = content[0].get("text", "") if content else ""
                if content and content.strip():
                    messages.append({
                        "role": data.get("role", "user"),
                        "content": content.strip(),
                    })

        # Reverse so the list reads chronologically (oldest → newest)
        return list(reversed(messages))

    except Exception as e:
        logger.warning("Could not read messages for %s: %s", user_id, e)
        return []


# ---------------------------------------------------------------------------
# Gemini prompt + call
# ---------------------------------------------------------------------------

def _build_prompt(profile: dict, messages: list[dict]) -> str:
    name         = profile.get("first_name", "the user")
    company      = profile.get("company_name", "their company")
    industry     = profile.get("company_industry", "unknown industry")
    team         = profile.get("team", "unknown team")
    has_strategy = profile.get("sustainability_strategy", False)
    uk_ops       = profile.get("operate_in_uk", False)

    profile_block = (
        f"User: {name}\n"
        f"Company: {company} ({industry} industry)\n"
        f"Team: {team}\n"
        f"Has sustainability strategy: {'yes' if has_strategy else 'no'}\n"
        f"Operates in the UK: {'yes' if uk_ops else 'no'}"
    )

    if messages:
        convo_lines = [
            f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
            for m in messages[-20:]
        ]
        convo_block = "Recent conversation:\n" + "\n".join(convo_lines)
    else:
        convo_block = "No conversation history yet."

    return f"""You are generating suggestion chips for a sustainability assistant app called Dash.
These chips appear on the home screen and are the first thing the user sees when they open the app.
They must feel personally relevant and immediately useful.

{profile_block}

{convo_block}

Generate exactly 4 suggestion chips. Each chip must have:
- "text": A short, natural prompt (4–7 words max). Do NOT start with "I".
- "type": One of exactly these four values — "Sustainability 101", "Plan", "Analyse", "In the news"

Type guide:
- "Sustainability 101"  → explanatory questions, concept definitions, how-things-work
- "Plan"               → roadmaps, strategies, goal-setting, next steps
- "Analyse"            → calculations, data requests, breakdowns, comparisons
- "In the news"        → current regulations, recent policy, industry news, market trends

Rules:
- Use all 4 types — one chip per type
- If there is conversation history, make the text of each chip continue or build on recent topics
- If there is no history, base the text on the user's industry, team, and UK context
- Each chip text must be actionable and specific — never generic like "Tell me more"

Respond with ONLY a valid JSON array of exactly 4 objects. Example format:
[
  {{"text": "What is Scope 3 reporting?", "type": "Sustainability 101"}},
  {{"text": "Build a net zero roadmap", "type": "Plan"}},
  {{"text": "Show my Scope 2 breakdown", "type": "Analyse"}},
  {{"text": "Latest UK carbon regulations", "type": "In the news"}}
]
"""


# Default chips used when Gemini fails — one per type
_DEFAULT_CHIPS = [
    {"text": "What is a carbon footprint?",       "type": "Sustainability 101"},
    {"text": "Help me build a sustainability plan", "type": "Plan"},
    {"text": "Analyse my energy data",             "type": "Analyse"},
    {"text": "Latest carbon regulation news",      "type": "In the news"},
]


def _call_gemini(prompt: str) -> list[dict]:
    """
    Call Gemini and parse the response as a list of 4 {text, type} dicts.
    Falls back to _DEFAULT_CHIPS on any error.
    """
    try:
        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config={"response_mime_type": "application/json"},
        )
        raw = response.text.strip()

        # Strip markdown code fences if Gemini wraps the JSON
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        chips = json.loads(raw)

        # Validate structure
        if (
            isinstance(chips, list)
            and len(chips) == 4
            and all(
                isinstance(c, dict)
                and isinstance(c.get("text"), str)
                and c.get("type") in CHIP_TYPES
                for c in chips
            )
        ):
            return chips

        logger.warning("Gemini returned unexpected chip format: %s", raw)
        return _DEFAULT_CHIPS

    except Exception as e:
        logger.error("Gemini call failed: %s", e)
        return _DEFAULT_CHIPS


# ---------------------------------------------------------------------------
# Firestore write
# ---------------------------------------------------------------------------

def _write_suggestions(user_id: str, chips: list[dict]) -> None:
    """
    Atomically replaces a user's suggestions in the `suggestions` collection.
    Deletes all existing docs for the user then writes 4 new ones with TTL.
    All operations are batched to minimise round-trips.
    """
    expires_at = datetime.now(timezone.utc) + timedelta(hours=SUGGESTIONS_TTL_HOURS)
    batch = db.batch()

    # Delete existing suggestions for this user
    existing = db.collection("suggestions").where("user_id", "==", user_id).stream()
    for doc in existing:
        batch.delete(doc.reference)

    # Write 4 new suggestion documents
    for chip in chips:
        ref = db.collection("suggestions").document()
        batch.set(ref, {
            "text":       chip["text"],
            "type":       chip["type"],
            "user_id":    user_id,
            "created_at": firestore_module.SERVER_TIMESTAMP,
            "expires_at": expires_at,
        })

    batch.commit()


# ---------------------------------------------------------------------------
# Per-user worker (runs in a thread)
# ---------------------------------------------------------------------------

def _process_user(user_id: str) -> tuple[str, str]:
    """
    Generate and store suggestions for a single user.
    Returns (user_id, "ok" | "error: <msg>").
    """
    try:
        profile  = _get_user_profile(user_id)
        messages = _get_recent_messages(user_id)
        prompt   = _build_prompt(profile, messages)
        chips    = _call_gemini(prompt)
        _write_suggestions(user_id, chips)
        logger.info("Generated suggestions for %s: %s", user_id, chips)
        return user_id, "ok"
    except Exception as e:
        logger.error("Failed to process user %s: %s", user_id, e)
        return user_id, f"error: {e}"


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.post("/generate-suggestions")
def generate_suggestions(x_cron_secret: str = Header(default="")):
    """
    Nightly cron endpoint — iterates all Firestore users and generates
    personalised suggestion chips via Gemini, writing them to the
    `suggestions` collection with a 25-hour TTL.

    Protected by the X-Cron-Secret header (must match CRON_SECRET env var).
    Set this header value in your Cloud Scheduler job configuration.
    """
    if CRON_SECRET and x_cron_secret != CRON_SECRET:
        raise HTTPException(status_code=401, detail="Invalid cron secret.")

    started_at = datetime.now(timezone.utc).isoformat()

    # Collect all user IDs
    try:
        user_ids = [doc.id for doc in db.collection("users").stream()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not list users: {e}")

    if not user_ids:
        return {"started_at": started_at, "total": 0, "results": {}}

    # Fan out — one thread per user, up to MAX_WORKERS concurrent Gemini calls
    results = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(_process_user, uid): uid for uid in user_ids}
        for future in as_completed(futures):
            uid, status = future.result()
            results[uid] = status

    ok_count    = sum(1 for s in results.values() if s == "ok")
    error_count = len(results) - ok_count

    return {
        "started_at":  started_at,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "total":        len(user_ids),
        "ok":           ok_count,
        "errors":       error_count,
        "results":      results,
    }
