"""Private, local-only email inbox source (fork addition, last30days-mail).

This adapter is the engine-side half of the mail integration. It performs NO
network and NO MCP calls of its own - the engine is a standalone subprocess and
cannot reach MCP. Instead, the hosting agent (Claude) prefetches inbox mail via
the Gmail MCP, applies the sender-allowlist / label filter, and writes a small
JSON file. This module loads that file, keeps only messages inside the run's
date window, relevance-scores each against the topic, and returns normalized
``SourceItem`` objects for the shared relevance/fusion/rerank pipeline.

Like ``corpus``, mail is treated as a PRIVATE first-party source: the pipeline
scores it with the deterministic reranker only, so inbox text never enters a
hosted reasoning prompt. Unlike ``corpus``, mail is NOT siloed into its own
render section - it stays merged in the ranked evidence clusters and is flagged
as inbox-derived at synthesis time.

Prefetch JSON schema (written by the agent, read here):

    {
      "generated_at": "YYYY-MM-DD",     # optional, informational
      "topic": "dropshipping",          # optional, informational
      "items": [
        {
          "id": "gmail-thread-or-message-id",   # required, stable id
          "subject": "...",                      # -> title
          "from": "Sender Name <addr@domain>",   # display author
          "from_email": "addr@domain",           # -> container (the sender)
          "date": "YYYY-MM-DD",                  # received date (window filter)
          "body": "plain-text body ...",         # -> body (scored + snippeted)
          "labels": ["Newsletters"],             # matched Gmail label(s)
          "matched_by": "label" | "sender",      # why it qualified (optional)
          "permalink": "https://mail.google.com/..."  # optional; else mail://
        }
      ]
    }
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import entity_extract, log, relevance, schema

SOURCE = "mail"
MAX_ITEMS = 500
MAX_BODY_CHARS = 200_000
# Same floor corpus uses: below this the message is not really about the topic.
MIN_MATCH_SCORE = 0.15


@dataclass
class MailScanResult:
    """One bounded load of prefetched inbox mail, plus non-fatal notes."""

    items: list[schema.SourceItem]
    notes: list[str] = field(default_factory=list)
    messages_scanned: int = 0
    matched: int = 0


def resolve_items_path(
    cli_value: str | None,
    configured: str | None,
) -> Path | None:
    """Pick the mail-items JSON path from the CLI flag or config, if any."""
    raw = (cli_value or configured or "").strip()
    if not raw:
        return None
    return Path(raw).expanduser().resolve()


def _match_score(topic: str, text: str) -> float:
    """Relevance of a message to the topic - identical shape to corpus scoring."""
    lexical = relevance.token_overlap_relevance(topic, text)
    topic_entities = entity_extract.extract_text_entities(topic)
    text_entities = entity_extract.extract_text_entities(text)
    entity_score = entity_extract.entity_overlap(topic_entities, text_entities)
    return round(max(lexical, entity_score * 0.9), 4)


def _coerce_items(payload: Any, notes: list[str]) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        raw = payload.get("items")
    elif isinstance(payload, list):
        raw = payload
    else:
        raw = None
    if not isinstance(raw, list):
        notes.append("Mail items file had no 'items' list; nothing loaded")
        return []
    return [entry for entry in raw if isinstance(entry, dict)]


def search(
    topic: str,
    items_path: Path | str,
    *,
    from_date: str,
    to_date: str,
    all_time: bool = False,
    limit: int = 12,
) -> MailScanResult:
    """Load prefetched inbox mail and return topic-scored SourceItems.

    Makes no network/MCP call: the agent has already fetched and filtered the
    mail (by allowlisted sender OR chosen label) into ``items_path``.
    """
    notes: list[str] = []
    path = Path(items_path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        notes.append("Mail items file not found; inbox source produced nothing")
        return MailScanResult(items=[], notes=notes)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        notes.append(f"Mail items file unreadable ({exc.__class__.__name__}); skipped")
        return MailScanResult(items=[], notes=notes)

    entries = _coerce_items(payload, notes)
    candidates: list[tuple[float, str, schema.SourceItem]] = []
    messages_scanned = 0

    for entry in entries[:MAX_ITEMS]:
        messages_scanned += 1
        published_at = str(entry.get("date") or "").strip()[:10]
        if not all_time and published_at:
            if not (from_date <= published_at <= to_date):
                continue

        subject = str(entry.get("subject") or "").strip() or "(no subject)"
        body = str(entry.get("body") or "")[:MAX_BODY_CHARS]
        from_display = str(entry.get("from") or entry.get("from_email") or "").strip()
        from_email = str(entry.get("from_email") or from_display).strip()
        labels = entry.get("labels")
        labels = [str(x) for x in labels] if isinstance(labels, list) else []
        matched_by = str(entry.get("matched_by") or "").strip()

        score = _match_score(topic, f"{subject}\n{body}")
        if score < MIN_MATCH_SCORE:
            continue

        stable = str(entry.get("id") or f"{from_email}|{subject}|{published_at}")
        digest = hashlib.sha256(stable.encode("utf-8")).hexdigest()
        permalink = str(entry.get("permalink") or "").strip()
        url = permalink or f"mail://{digest}"

        why_bits = ["From your inbox"]
        if from_display:
            why_bits.append(from_display)
        if labels:
            why_bits.append("label: " + ", ".join(labels))
        elif matched_by == "sender":
            why_bits.append("allowlisted sender")

        item = schema.SourceItem(
            item_id=f"M{digest[:12]}",
            source=SOURCE,
            title=subject,
            body=body,
            url=url,
            author=from_display or None,
            container=from_email or None,
            published_at=published_at or None,
            date_confidence="high" if published_at else "low",
            relevance_hint=score,
            why_relevant=" - ".join(why_bits),
            # Let extract_best_snippet derive the matching window (corpus does
            # the same); a raw header/intro snippet reads as unrelated boilerplate.
            snippet="",
            metadata={
                "from": from_display,
                "from_email": from_email,
                "labels": labels,
                "matched_by": matched_by,
                "has_permalink": bool(permalink),
                "local_only": True,
                "first_party": True,
            },
        )
        candidates.append((score, published_at, item))

    # Highest score first; within a score, newer date first.
    candidates.sort(key=lambda row: (-row[0], _neg_date_key(row[1]), row[2].title.casefold()))
    items = [item for _score, _date, item in candidates[: max(0, limit)]]

    log.source_log(
        "Mail",
        f"loaded {messages_scanned} message(s), {len(candidates)} on-topic, {len(items)} kept",
        tty_only=False,
    )
    return MailScanResult(
        items=items,
        notes=notes,
        messages_scanned=messages_scanned,
        matched=len(candidates),
    )


def _neg_date_key(date_str: str) -> str:
    """Sort key that puts newer ISO dates first while keeping strings comparable."""
    # Invert each digit so a lexicographic ascending sort yields newest-first.
    if not date_str:
        return "~"  # empties last
    return "".join(chr(ord("9") - (ord(c) - ord("0"))) if c.isdigit() else c for c in date_str)
