"""Read-only Chronicle retrieval and campaign-relative history coverage plans.

The caller MUST supply records already filtered for the campaign, branch and
requester's knowledge/access scope. This module never opens a save or discovers
additional records. It neither resolves actions nor writes summaries or state.
An interval plan is not a published archive, a closed year, or generated prose.
"""
from __future__ import annotations

import base64
import copy
import hashlib
import json


AREAS = ("personal", "biographies", "relationships", "institutions", "timeline", "archive")
AREA_ALIASES = {"biography": "biographies", "institutional_history": "institutions",
                "historical_timeline": "timeline", "historical_archive": "archive"}
TIME_FIELDS = ("sequence", "at", "occurrence_at", "occurrence_time", "observed_at",
               "transmitted_at", "received_at", "recorded_at", "as_of", "date",
               "time", "calendar", "precision")
KIND_ALIASES = {"player_declaration": "declaration", "record_player_action": "declaration",
                "ast_record_player_action": "declaration", "record_evidence": "evidence",
                "receive_evidence": "receipt", "evidence_received": "receipt",
                "receive_order": "order", "order_received": "order", "set_scene": "scene"}


def _canonical(value):
    try:
        return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as err:
        raise ValueError("Chronicle input must contain ordinary finite JSON values") from err


def _digest(value):
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _integer(value, name, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer of at least {minimum}")
    return value


def _strings(value):
    if value is None:
        return []
    values = [value] if isinstance(value, str) else value
    if not isinstance(values, (list, tuple)) or any(not isinstance(item, str) or not item.strip() for item in values):
        raise ValueError("Chronicle references and identities must be nonempty strings")
    return list(dict.fromkeys(values))


def budget_policy_view(policy=None):
    """Validate a supplied policy; never select numerical word allowances."""
    if policy is None:
        return {"status": "unconfigured", "numeric_allowances": None,
                "growth_requirement": "Century maximum allowances must strictly increase from 100 through 500 years",
                "symbolic_allowances": {"annual": "A", "five_year": "F", "twenty_five_year": "Q",
                    "centuries": ["B1", "B2", "B3", "B4", "B5"], "constraint": "0 < B1 < B2 < B3 < B4 < B5"},
                "formula_adopted": False}
    if not isinstance(policy, dict) or not isinstance(policy.get("id"), str) or not policy["id"].strip():
        raise ValueError("A configured budget needs an explicit policy ID")
    _integer(policy.get("revision"), "Budget policy revision", 1)
    allowances = {key: _integer(policy.get(key), key + " allowance", 1)
                  for key in ("annual", "five_year", "twenty_five_year")}
    mode = policy.get("mode")
    if mode == "table":
        centuries = policy.get("century_allowances")
        if not isinstance(centuries, list) or len(centuries) != 5:
            raise ValueError("A century budget table needs five explicit allowances")
        centuries = [_integer(value, "Century allowance", 1) for value in centuries]
    elif mode == "linear":
        first = _integer(policy.get("first_century"), "First-century allowance", 1)
        increment = _integer(policy.get("century_increment"), "Century allowance increment", 1)
        centuries = [first + index * increment for index in range(5)]
    else:
        raise ValueError("Select an explicit table or linear budget policy")
    if any(left >= right for left, right in zip(centuries, centuries[1:])):
        raise ValueError("Century word allowances must strictly increase")
    allowances["centuries"] = centuries
    allowances["sealed_epoch"] = centuries[4]
    return {"status": "configured", "id": policy["id"], "revision": policy["revision"],
            "mode": mode, "numeric_allowances": allowances,
            "word_count_policy": copy.deepcopy(policy.get("word_count_policy")),
            "scope": "Supplied maximum prose allowances; not a minimum length or authority to generate/publish history"}


def plan_closed_years(closed_years, *, budget_policy=None):
    """Exact half-open coverage for N explicitly supplied complete relative years.

    Ordinal 0 is campaign-relative Year 1. Civil dates and origin selection are
    deliberately absent. The current incomplete year is outside closed coverage.
    """
    count = _integer(closed_years, "Closed years")
    budget = budget_policy_view(budget_policy)
    numeric = budget["numeric_allowances"]

    def interval(tier, start, end, epoch_index, centuries=None):
        row = {"id": f"plan:{tier}:{start}:{end}", "tier": tier,
               "start_year_ordinal": start, "end_year_ordinal_exclusive": end,
               "start_year": start + 1, "end_year": end, "epoch_index": epoch_index,
               "status": "planned_not_generated", "label": f"Year {start + 1}" if end - start == 1 else f"Years {start + 1}–{end}"}
        if centuries is not None:
            row["century_count"] = centuries
            row["disjoint_century_source_ranges"] = [
                {"start_year_ordinal": start + i * 100, "end_year_ordinal_exclusive": start + (i + 1) * 100}
                for i in range(centuries)]
        if numeric is not None:
            row["word_allowance"] = (numeric["sealed_epoch"] if tier == "sealed_epoch" else
                numeric["centuries"][centuries - 1] if tier == "cumulative_centuries" else numeric[tier])
        return row

    epoch_count, remainder = divmod(count, 500)
    sealed = [interval("sealed_epoch", i * 500, (i + 1) * 500, i, 5) for i in range(epoch_count)]
    active = []
    start = epoch_count * 500
    centuries, residual = divmod(remainder, 100)
    if centuries:
        end = start + centuries * 100
        active.append(interval("cumulative_centuries", start, end, epoch_count, centuries))
        start = end
    for tier, width in (("twenty_five_year", 25), ("five_year", 5), ("annual", 1)):
        groups, residual = divmod(residual, width)
        for _ in range(groups):
            active.append(interval(tier, start, start + width, epoch_count))
            start += width
    entries = sealed + active
    cursor = 0
    for entry in entries:
        if entry["start_year_ordinal"] != cursor:
            raise AssertionError("History plan has a gap or overlap")
        cursor = entry["end_year_ordinal_exclusive"]
    if cursor != count or len(active) > 12:
        raise AssertionError("History plan coverage or compact bound failed")
    return {"schema_version": 1, "status": "interval_plan_only", "closed_years": count,
            "origin": "Relative campaign Year 1; no civil calendar or actual year closure inferred",
            "coverage": {"start_year_ordinal": 0, "end_year_ordinal_exclusive": count,
                         "partition": "disjoint_complete", "validated": True},
            "entries": entries, "sealed_epochs": sealed, "open_epoch_entries": active,
            "sealed_epoch_count": epoch_count, "open_epoch_closed_entry_count": len(active),
            "open_epoch_entry_count_with_current": len(active) + 1,
            "current_year": {"id": f"plan:open_year:{count}", "tier": "open_year",
                "start_year_ordinal": count, "end_year_ordinal_exclusive": count + 1,
                "year": count + 1, "label": f"Year {count + 1} · open", "status": "incomplete_not_closed",
                "included_in_closed_coverage": False},
            "budget_policy": budget, "summary_text_generated": False, "published": False,
            "note": "Sealed epochs stay separate; cumulative entries never extend across an epoch boundary"}


def _normalise_record(record, scope):
    if not isinstance(record, dict) or not isinstance(record.get("id"), str) or not record["id"].strip():
        raise ValueError("Every projected Chronicle record requires a stable nonempty ID")
    # This is consistency validation, not a permission decision: only the
    # caller can establish which records the requester may receive.
    declared_scope = record.get("scope", {})
    if not isinstance(declared_scope, dict):
        raise ValueError("Projected record scope must be an object")
    for key in ("campaign_id", "branch_id", "access_scope_id"):
        declared = record.get(key, declared_scope.get(key))
        if declared is not None and key in scope and declared != scope[key]:
            raise ValueError("Projected Chronicle record belongs to a different campaign, branch or access scope")
    kind = record.get("kind", record.get("type", record.get("op", "record")))
    if not isinstance(kind, str) or not kind.strip():
        raise ValueError("Chronicle record kind must be a nonempty string")
    kind = KIND_ALIASES.get(kind, kind)
    text = None
    text_field = None
    for key in ("text", "declaration", "assertion", "content", "statement", "description"):
        if key in record and record[key] is not None:
            if not isinstance(record[key], str):
                raise ValueError("Projected Chronicle text must be a string")
            text, text_field = record[key], key
            break
    sources = _strings(record.get("source_refs"))
    sources += _strings(record.get("source_ref"))
    sources = list(dict.fromkeys(sources))
    actor_ids = _strings(record.get("actor_ids"))
    for key in ("actor", "subject", "recipient"):
        if isinstance(record.get(key), str) and record[key]:
            actor_ids += [record[key]]
    actor_ids = list(dict.fromkeys(actor_ids))
    institution_ids = _strings(record.get("institution_ids"))
    entities = list(dict.fromkeys(_strings(record.get("entity_ids")) + actor_ids + institution_ids))
    areas = set(_strings(record.get("areas")))
    if not areas <= set(AREAS):
        raise ValueError("Unknown Chronicle area on a projected record")
    areas.add("timeline")
    if record.get("personal") is True or (scope.get("actor_id") and scope["actor_id"] in actor_ids):
        areas.add("personal")
    if actor_ids or kind in {"actor", "character", "biography"}:
        areas.add("biographies")
    if kind in {"relationship", "marriage", "patronage", "alliance", "family_link"}:
        areas.add("relationships")
    if institution_ids or kind in {"institution", "organization", "institutional_history"}:
        areas.add("institutions")
    if kind in {"summary", "archive", "historical_reference", "source_gap", "gap", "annual",
                "five_year", "twenty_five_year", "cumulative_centuries", "sealed_epoch"}:
        areas.add("archive")
    available = record.get("source_available")
    if available is not None and type(available) is not bool:
        raise ValueError("source_available must be an explicit boolean when provided")
    gap = available is False or text is None
    row = {"id": record["id"], "kind": kind, "title": record.get("title") or kind.replace("_", " ").capitalize(),
           "text": text if text is not None else "", "source_refs": sources,
           "actor_ids": actor_ids, "entity_ids": entities, "institution_ids": institution_ids,
           "areas": [area for area in AREAS if area in areas],
           "status": copy.deepcopy(record.get("status")),
           "text_provenance": "provided_projection_text" if text is not None else "source_text_unavailable",
           "text_field": text_field, "reconstructed": False,
           "exact_transcript_claimed": bool(kind in {"dialogue", "transcript"} and record.get("verbatim") is True and not gap),
           "provenance_status": "referenced" if sources else "reference_not_supplied",
           "source_available": False if gap else available,
           "source_gap": gap}
    if not isinstance(row["title"], str):
        raise ValueError("Chronicle record title must be a string")
    if kind == "declaration":
        row["interpretation"] = "Player declaration or attempt; recording it does not establish its outcome"
        if row["status"] is None:
            row["status"] = "declared_not_resolved"
    elif kind in {"order", "received_order"}:
        row["interpretation"] = "Recorded order content; receipt does not establish execution"
    elif kind in {"evidence", "receipt", "report", "rumour", "testimony"}:
        row["interpretation"] = "Attributed evidence or information record; not an additional underlying occurrence"
    elif kind in {"summary", "archive", "annual", "five_year", "twenty_five_year", "cumulative_centuries", "sealed_epoch"}:
        row["interpretation"] = "Supplied historical account; it does not replace authoritative campaign state"
    else:
        row["interpretation"] = "Accessible source record; no additional event or consequence is inferred"
    for key in (*TIME_FIELDS, "revision", "occurrence_id", "supersedes_id", "range", "speaker", "relationship_id", "name"):
        if key in record:
            row[key] = copy.deepcopy(record[key])
    if gap:
        row["gap_note"] = record.get("gap_note") or "Original source text is unavailable or incomplete; no conversation or event has been reconstructed"
    _canonical(row)
    return row


def _sort_key(record):
    # Causal sequence is not elapsed time. Unknown/approximate dates are kept
    # as supplied and never converted into a supposedly exact timeline.
    for field in ("sequence", "at", "received_at", "recorded_at"):
        if type(record.get(field)) is int:
            return (0, record[field], record["id"])
    return (1, 0, record["id"])


def _cursor_encode(fingerprint, offset):
    value = _canonical({"v": 1, "fingerprint": fingerprint, "offset": offset}).encode("utf-8")
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _cursor_offset(cursor, fingerprint, length):
    if cursor is None:
        return 0
    if not isinstance(cursor, str) or len(cursor) > 1000:
        raise ValueError("Invalid Chronicle page cursor")
    try:
        decoded = json.loads(base64.b64decode(cursor + "=" * (-len(cursor) % 4), altchars=b"-_", validate=True))
    except (ValueError, TypeError, UnicodeDecodeError) as err:
        raise ValueError("Invalid Chronicle page cursor") from err
    if not isinstance(decoded, dict) or decoded.get("v") != 1 or decoded.get("fingerprint") != fingerprint:
        raise ValueError("Chronicle records, scope or search changed; restart pagination")
    offset = _integer(decoded.get("offset"), "Chronicle page offset")
    if offset > length:
        raise ValueError("Chronicle page cursor is outside the result set")
    return offset


def build_chronicle(records, query=None, *, scope=None, area="timeline", entity_id=None,
                    limit=30, cursor=None, closed_years=None, budget_policy=None):
    """Retrieve ONLY supplied permission-filtered records without mutating them.

    The record list is the complete trust boundary: there is no world-state,
    archive-file, URL-fetch or title-discovery fallback. A cursor is scoped to
    the exact input projection, search and page size; stale retries fail closed.
    """
    if not isinstance(records, (list, tuple)):
        raise ValueError("Chronicle requires a list of already filtered projection records")
    scope = copy.deepcopy(scope if scope is not None else {})
    if not isinstance(scope, dict):
        raise ValueError("Chronicle scope must be an explicit object")
    _canonical(scope)
    area = AREA_ALIASES.get(area, area)
    if area not in AREAS:
        raise ValueError("Unknown Chronicle area")
    if query is not None and not isinstance(query, str):
        raise ValueError("Chronicle search must be text")
    query = (query or "").strip()
    if len(query) > 1000:
        raise ValueError("Chronicle search is too long")
    if entity_id is not None and (not isinstance(entity_id, str) or not entity_id.strip()):
        raise ValueError("Chronicle entity filter must name a stable identity")
    _integer(limit, "Chronicle page size", 1)
    if limit > 100:
        raise ValueError("Chronicle page size cannot exceed 100")
    unique = {}
    for raw in records:
        row = _normalise_record(raw, scope)
        old = unique.get(row["id"])
        if old is not None and old != row:
            raise ValueError("Conflicting Chronicle payloads share one record ID")
        unique[row["id"]] = row
    all_rows = sorted(unique.values(), key=_sort_key)
    query_folded = query.casefold()
    matching = []
    for row in all_rows:
        if area not in row["areas"] or (entity_id is not None and entity_id not in row["entity_ids"]):
            continue
        searchable = _canonical({key: row.get(key) for key in
            ("id", "title", "text", "name", "source_refs", "actor_ids", "entity_ids", "institution_ids", "status", "speaker")}).casefold()
        if query_folded and query_folded not in searchable:
            continue
        matching.append(row)
    fingerprint = _digest({"records": all_rows, "scope": scope, "query": query.casefold(),
                           "area": area, "entity_id": entity_id, "limit": limit})
    offset = _cursor_offset(cursor, fingerprint, len(matching))
    page = matching[offset:offset + limit]
    next_offset = offset + len(page)
    next_cursor = _cursor_encode(fingerprint, next_offset) if next_offset < len(matching) else None
    datasets = {name: {"count": sum(name in row["areas"] for row in all_rows),
                        "record_ids": [row["id"] for row in all_rows if name in row["areas"]],
                        "status": "accessible_records" if any(name in row["areas"] for row in all_rows) else "no_accessible_records_supplied"}
                for name in AREAS}
    memory = {"status": "unconfigured",
              "reason": "No committed calendar-year origin and closure binding is configured for this Chronicle",
              "automatic_year_closure": False, "automatic_summary_generation": False,
              "supplied_summary_count": sum(row["kind"] in {"summary", "annual", "five_year", "twenty_five_year", "cumulative_centuries", "sealed_epoch"} for row in all_rows),
              "published_summary_count": sum(row["kind"] in {"summary", "annual", "five_year", "twenty_five_year", "cumulative_centuries", "sealed_epoch"} and row["status"] == "published" for row in all_rows),
              "budget_policy": budget_policy_view(budget_policy), "interval_plan": None}
    if closed_years is not None:
        memory["interval_plan"] = plan_closed_years(closed_years, budget_policy=budget_policy)
        memory["plan_note"] = "Explicit ordinal preview only; not evidence that any campaign year has elapsed or closed"
    return {"schema_version": 1, "scope": scope, "area": area, "query": query,
            "entity_id": entity_id, "entries": copy.deepcopy(page),
            "pagination": {"total": len(matching), "limit": limit, "offset": offset, "next_cursor": next_cursor},
            "datasets": datasets, "memory": memory,
            "gaps": [{"record_id": row["id"], "note": row["gap_note"], "source_refs": copy.deepcopy(row["source_refs"])}
                     for row in page if row["source_gap"]],
            "ordering": "Provided causal, receipt or recorded sequence when numerical, otherwise stable record identity; no civil time inferred",
            "record_count_meaning": "Accessible source records, not totals of underlying occurrences or resources",
            "reconstruction": "Available source text only; no missing dialogue, biography or past world state reconstructed",
            "simulation_writes": False}
