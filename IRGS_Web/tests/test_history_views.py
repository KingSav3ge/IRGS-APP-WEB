"""Chronicle retrieval and exact epoch coverage; no campaign saves are used."""
import copy
import json
from pathlib import Path
import random
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from history_views import budget_policy_view, build_chronicle, plan_closed_years


SCOPE = {"campaign_id": "campaign-one", "branch_id": "branch-one",
         "access_scope_id": "alice-known", "actor_id": "alice", "mode": "player"}


def projected_records():
    return [
        {"id": "declare-1", "kind": "player_declaration", "actor_ids": ["alice"],
         "text": 'I ask, "May I inspect the weapons?"\nI wait for the answer.',
         "recorded_at": 2, "source_refs": ["player-turn-2"], "status": "declared_not_resolved"},
        {"id": "receipt-1", "kind": "evidence_received", "actor_ids": ["bob"],
         "areas": ["personal"], "text": "A witness says the bridge was damaged.",
         "status": "testimony", "occurrence_at": {"date": "1415-08-10", "precision": "day"},
         "observed_at": 1, "transmitted_at": 3, "received_at": 5,
         "source_refs": ["witness-report", "receipt-5"], "occurrence_id": "bridge-report"},
        {"id": "order-1", "kind": "order_received", "actor_ids": ["alice"],
         "text": "Present the report tomorrow.", "received_at": 6,
         "status": "received", "source_available": True, "source_refs": ["received-letter"]},
        {"id": "relation-1", "kind": "patronage", "actor_ids": ["alice", "bob"],
         "relationship_id": "patronage-one", "text": "Bob offered sponsorship; terms remain unresolved.",
         "source_ref": "conversation-record", "recorded_at": 7},
        {"id": "institution-1", "kind": "institution", "institution_ids": ["guild-one"],
         "text": "A guild office is recorded; its powers require separate evidence.",
         "source_refs": ["charter-reference"], "at": 8},
        {"id": "archive-1", "kind": "summary", "text": "An attributed older account.",
         "range": {"start_year_ordinal": 0, "end_year_ordinal_exclusive": 5},
         "source_refs": ["account-version-1"], "status": "candidate", "verbatim": True},
        {"id": "old-source-gap", "kind": "source_gap", "title": "Earlier scene unavailable",
         "source_available": False, "source_refs": ["missing-scene-source"]},
    ]


class EpochCoverageTests(unittest.TestCase):
    def shape(self, n):
        return [(e["tier"], e["start_year_ordinal"], e["end_year_ordinal_exclusive"])
                for e in plan_closed_years(n)["entries"]]

    def assert_partition(self, n):
        plan = plan_closed_years(n)
        cursor = 0
        for entry in plan["entries"]:
            start, end = entry["start_year_ordinal"], entry["end_year_ordinal_exclusive"]
            self.assertEqual(start, cursor)
            self.assertGreater(end, start)
            self.assertEqual(entry["start_year"], start + 1)
            self.assertEqual(entry["end_year"], end)
            width = end - start
            tier = entry["tier"]
            if tier in {"annual", "five_year", "twenty_five_year"}:
                expected = {"annual": 1, "five_year": 5, "twenty_five_year": 25}[tier]
                self.assertEqual(width, expected)
                self.assertEqual(start % expected, 0)
            elif tier == "sealed_epoch":
                self.assertEqual(width, 500)
                self.assertEqual(start % 500, 0)
                self.assertEqual(entry["century_count"], 5)
            else:
                self.assertEqual(tier, "cumulative_centuries")
                self.assertIn(width, (100, 200, 300, 400))
                self.assertEqual(start % 500, 0)
            self.assertEqual(start // 500, (end - 1) // 500)
            cursor = end
        self.assertEqual(cursor, n)
        self.assertEqual(len({e['id'] for e in plan['entries']}), len(plan['entries']))
        self.assertEqual(plan["sealed_epoch_count"], n // 500)
        self.assertLessEqual(len(plan["open_epoch_entries"]), 12)
        self.assertEqual(plan["current_year"]["start_year_ordinal"], n)
        self.assertEqual(plan["current_year"]["end_year_ordinal_exclusive"], n + 1)
        self.assertFalse(plan["current_year"]["included_in_closed_coverage"])
        self.assertFalse(plan["summary_text_generated"])
        self.assertFalse(plan["published"])
        return plan

    def test_required_boundaries_and_incomplete_groups(self):
        expected = {
            0: [],
            4: [("annual", i, i + 1) for i in range(4)],
            5: [("five_year", 0, 5)],
            24: [("five_year", i, i + 5) for i in range(0, 20, 5)] + [("annual", i, i + 1) for i in range(20, 24)],
            25: [("twenty_five_year", 0, 25)],
            99: [("twenty_five_year", i, i + 25) for i in range(0, 75, 25)]
                + [("five_year", i, i + 5) for i in range(75, 95, 5)]
                + [("annual", i, i + 1) for i in range(95, 99)],
            100: [("cumulative_centuries", 0, 100)],
            200: [("cumulative_centuries", 0, 200)],
            400: [("cumulative_centuries", 0, 400)],
            499: [("cumulative_centuries", 0, 400)]
                + [("twenty_five_year", i, i + 25) for i in range(400, 475, 25)]
                + [("five_year", i, i + 5) for i in range(475, 495, 5)]
                + [("annual", i, i + 1) for i in range(495, 499)],
            500: [("sealed_epoch", 0, 500)],
            1000: [("sealed_epoch", 0, 500), ("sealed_epoch", 500, 1000)],
        }
        for n, shape in expected.items():
            with self.subTest(n=n):
                self.assertEqual(self.shape(n), shape)
                self.assert_partition(n)

    def test_intermediate_century_examples_and_separate_epochs(self):
        self.assertEqual(self.shape(175), [("cumulative_centuries", 0, 100),
            ("twenty_five_year", 100, 125), ("twenty_five_year", 125, 150), ("twenty_five_year", 150, 175)])
        self.assertEqual(self.shape(300), [("cumulative_centuries", 0, 300)])
        self.assertEqual(self.shape(600), [("sealed_epoch", 0, 500), ("cumulative_centuries", 500, 600)])
        self.assertEqual(self.shape(1100), [("sealed_epoch", 0, 500), ("sealed_epoch", 500, 1000),
                                           ("cumulative_centuries", 1000, 1100)])

    def test_property_exact_coverage_alignment_and_twelve_entry_bound(self):
        rng = random.Random(1415)
        for n in list(range(501)) + [rng.randrange(0, 100000) for _ in range(400)]:
            with self.subTest(n=n):
                self.assert_partition(n)
        self.assertEqual(max(len(plan_closed_years(n)["open_epoch_entries"]) for n in range(500)), 12)
        self.assertEqual(plan_closed_years(499)["open_epoch_entry_count_with_current"], 13)

    def test_source_centuries_are_disjoint_not_overlapping_cumulative_inputs(self):
        for n in (100, 200, 300, 400, 500, 1000, 1400):
            for entry in plan_closed_years(n)["entries"]:
                if "century_count" not in entry:
                    continue
                ranges = entry["disjoint_century_source_ranges"]
                self.assertEqual(len(ranges), entry["century_count"])
                self.assertEqual(ranges[0]["start_year_ordinal"], entry["start_year_ordinal"])
                self.assertEqual(ranges[-1]["end_year_ordinal_exclusive"], entry["end_year_ordinal_exclusive"])
                for i, item in enumerate(ranges):
                    self.assertEqual(item["end_year_ordinal_exclusive"] - item["start_year_ordinal"], 100)
                    if i:
                        self.assertEqual(ranges[i - 1]["end_year_ordinal_exclusive"], item["start_year_ordinal"])

    def test_repeated_plans_are_identical_and_bad_ordinals_are_rejected(self):
        self.assertEqual(plan_closed_years(999), plan_closed_years(999))
        for bad in (-1, True, False, 1.0, "5", None):
            with self.subTest(value=bad), self.assertRaises(ValueError):
                plan_closed_years(bad)


class BudgetPolicyTests(unittest.TestCase):
    def policy(self):
        return {"id": "test-fixture-not-production", "revision": 1, "mode": "table",
                "annual": 10, "five_year": 20, "twenty_five_year": 30,
                "century_allowances": [40, 50, 60, 70, 80]}

    def test_unconfigured_policy_has_symbols_and_no_adopted_numbers(self):
        policy = budget_policy_view()
        self.assertEqual(policy["status"], "unconfigured")
        self.assertIsNone(policy["numeric_allowances"])
        self.assertFalse(policy["formula_adopted"])
        self.assertTrue(all("word_allowance" not in item for item in plan_closed_years(499)["entries"]))

    def test_explicit_table_grows_and_resets_inside_next_epoch(self):
        policy = self.policy()
        before = copy.deepcopy(policy)
        for n, expected in ((100, 40), (200, 50), (300, 60), (400, 70), (500, 80), (600, 40)):
            plan = plan_closed_years(n, budget_policy=policy)
            self.assertEqual(plan["entries"][-1]["word_allowance"], expected)
        self.assertEqual(policy, before)
        self.assertEqual(plan_closed_years(525, budget_policy=policy)["entries"][-1]["word_allowance"], 30)

    def test_linear_growth_requires_explicit_selection_and_positive_increment(self):
        policy = {**self.policy(), "mode": "linear", "first_century": 41, "century_increment": 7}
        self.assertEqual(budget_policy_view(policy)["numeric_allowances"]["centuries"], [41, 48, 55, 62, 69])
        policy["century_increment"] = 0
        with self.assertRaises(ValueError):
            budget_policy_view(policy)

    def test_invalid_or_nongrowing_configurations_fail(self):
        changes = [{"id": ""}, {"revision": 0}, {"mode": None}, {"annual": True},
                   {"five_year": 0}, {"twenty_five_year": -2}, {"century_allowances": [1, 2, 3, 4]},
                   {"century_allowances": [1, 2, 2, 4, 5]}, {"century_allowances": [5, 4, 3, 2, 1]},
                   {"century_allowances": [1, 2, 3, 4, 5.5]}]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(ValueError):
                budget_policy_view({**self.policy(), **change})


class ChronicleRetrievalTests(unittest.TestCase):
    def test_exact_declaration_is_preserved_as_attempt_not_an_outcome(self):
        raw = projected_records()[0]
        result = build_chronicle([raw], scope=SCOPE)
        entry = result["entries"][0]
        self.assertEqual(entry["text"], raw["text"])
        self.assertEqual(entry["kind"], "declaration")
        self.assertEqual(entry["status"], "declared_not_resolved")
        self.assertIn("does not establish its outcome", entry["interpretation"])
        self.assertFalse(entry["reconstructed"])
        self.assertFalse(result["simulation_writes"])

    def test_occurrence_observation_transmission_receipt_remain_distinct(self):
        record = projected_records()[1]
        entry = build_chronicle([record], scope=SCOPE)["entries"][0]
        for field in ("occurrence_at", "observed_at", "transmitted_at", "received_at"):
            self.assertEqual(entry[field], record[field])
        self.assertEqual(entry["status"], "testimony")
        self.assertEqual(entry["kind"], "receipt")
        self.assertNotIn("recorded_at", entry)
        self.assertNotIn("date", entry)

    def test_order_receipt_never_manufactures_execution(self):
        entry = build_chronicle([projected_records()[2]], scope=SCOPE)["entries"][0]
        self.assertEqual(entry["kind"], "order")
        self.assertEqual(entry["status"], "received")
        self.assertIn("does not establish execution", entry["interpretation"])

    def test_available_datasets_require_supported_records_not_text_inference(self):
        records = projected_records()
        result = build_chronicle(records, scope=SCOPE)
        self.assertIn("relation-1", result["datasets"]["relationships"]["record_ids"])
        self.assertNotIn("declare-1", result["datasets"]["relationships"]["record_ids"])
        self.assertEqual(result["datasets"]["institutions"]["record_ids"], ["institution-1"])
        self.assertIn("receipt-1", result["datasets"]["personal"]["record_ids"])
        self.assertIn("receipt-1", result["datasets"]["biographies"]["record_ids"])
        relations = build_chronicle(records, scope=SCOPE, area="relationships")
        self.assertEqual([r["id"] for r in relations["entries"]], ["relation-1"])
        self.assertEqual(build_chronicle(records, scope=SCOPE, area="biography")["area"], "biographies")
        empty = build_chronicle([], scope=SCOPE)
        self.assertTrue(all(d["status"] == "no_accessible_records_supplied" for d in empty["datasets"].values()))

    def test_missing_source_is_a_gap_and_never_an_exact_reconstructed_conversation(self):
        missing = {"id": "lost-dialogue", "kind": "dialogue", "source_available": False,
                   "text": "A surviving paraphrase, not the conversation.", "verbatim": True,
                   "source_refs": ["unavailable-original"]}
        result = build_chronicle([missing], scope=SCOPE)
        entry = result["entries"][0]
        self.assertEqual(entry["text"], missing["text"])
        self.assertTrue(entry["source_gap"])
        self.assertFalse(entry["source_available"])
        self.assertFalse(entry["exact_transcript_claimed"])
        self.assertFalse(entry["reconstructed"])
        self.assertEqual(result["gaps"][0]["record_id"], "lost-dialogue")
        self.assertEqual(build_chronicle([projected_records()[-1]])["entries"][0]["text"], "")

    def test_candidate_summary_is_not_a_published_epoch_or_new_year_closure(self):
        result = build_chronicle([projected_records()[5]], scope=SCOPE)
        self.assertEqual(result["memory"]["status"], "unconfigured")
        self.assertEqual(result["memory"]["supplied_summary_count"], 1)
        self.assertEqual(result["memory"]["published_summary_count"], 0)
        self.assertIsNone(result["memory"]["interval_plan"])
        self.assertFalse(result["memory"]["automatic_year_closure"])
        self.assertFalse(result["memory"]["automatic_summary_generation"])
        self.assertFalse(result["entries"][0]["exact_transcript_claimed"])

    def test_only_explicit_closed_years_produce_a_preview_not_published_history(self):
        result = build_chronicle([], closed_years=1000)
        self.assertEqual(result["memory"]["status"], "unconfigured")
        self.assertEqual(result["memory"]["interval_plan"]["sealed_epoch_count"], 2)
        self.assertFalse(result["memory"]["interval_plan"]["published"])
        self.assertIn("not evidence", result["memory"]["plan_note"])

    def test_same_occurrence_reports_are_not_counted_as_resources_or_duplicate_events(self):
        records = [{"id": "report-a", "kind": "report", "occurrence_id": "one-casualty-claim",
                    "text": "One witness claims an injury.", "source_ref": "witness-a"},
                   {"id": "report-b", "kind": "report", "occurrence_id": "one-casualty-claim",
                    "text": "Another witness disputes the injury.", "source_ref": "witness-b"}]
        result = build_chronicle(records)
        self.assertEqual(len(result["entries"]), 2)
        self.assertTrue(all(row["occurrence_id"] == "one-casualty-claim" for row in result["entries"]))
        self.assertNotIn("casualty_total", result)
        self.assertNotIn("resources", result)
        self.assertIn("not totals", result["record_count_meaning"])

    def test_inspection_and_nested_return_values_never_mutate_input_or_open_files(self):
        records, scope = projected_records(), copy.deepcopy(SCOPE)
        before_records, before_scope = copy.deepcopy(records), copy.deepcopy(scope)
        with patch("builtins.open", side_effect=AssertionError("Chronicle must not open files")):
            result = build_chronicle(records, scope=scope, closed_years=500)
        self.assertEqual(records, before_records)
        self.assertEqual(scope, before_scope)
        result["entries"][0]["source_refs"].append("changed-return-value")
        result["scope"]["actor_id"] = "elsewhere"
        self.assertEqual(records, before_records)
        self.assertEqual(scope, before_scope)

    def test_exact_duplicates_are_deduplicated_and_conflicting_identity_is_rejected(self):
        record = projected_records()[0]
        self.assertEqual(build_chronicle([record, copy.deepcopy(record)])["pagination"]["total"], 1)
        with self.assertRaises(ValueError):
            build_chronicle([record, {**record, "text": "Different alleged declaration"}])

    def test_search_only_returns_supplied_records_and_preserves_identity_filters(self):
        records = projected_records()
        self.assertEqual(build_chronicle(records, "UNPASSED SECRET")["entries"], [])
        result = build_chronicle(records, "BRIDGE", scope=SCOPE, entity_id="bob")
        self.assertEqual([r["id"] for r in result["entries"]], ["receipt-1"])
        self.assertEqual(build_chronicle(records, "bridge", entity_id="unknown-person")["entries"], [])
        self.assertEqual(build_chronicle(records, "player-turn-2")["entries"][0]["id"], "declare-1")

    def test_paginated_order_is_stable_under_input_reordering(self):
        records = [{"id": f"record-{i}", "kind": "record", "text": f"Event {i}", "recorded_at": i}
                   for i in range(9)]
        cursor, found = None, []
        while True:
            page = build_chronicle(list(reversed(records)), scope=SCOPE, limit=2, cursor=cursor)
            found.extend(row["id"] for row in page["entries"])
            cursor = page["pagination"]["next_cursor"]
            if cursor is None:
                break
        self.assertEqual(found, [r["id"] for r in records])
        self.assertEqual(len(found), len(set(found)))
        first = build_chronicle(records, scope=SCOPE, limit=2)
        second = build_chronicle(list(reversed(records)), scope=SCOPE, limit=2)
        self.assertEqual(first["pagination"]["next_cursor"], second["pagination"]["next_cursor"])

    def test_cursor_cannot_cross_scope_search_area_page_size_or_changed_records(self):
        records = projected_records()
        cursor = build_chronicle(records, scope=SCOPE, limit=1)["pagination"]["next_cursor"]
        variants = [{"scope": {**SCOPE, "branch_id": "another-branch"}},
                    {"scope": {**SCOPE, "mode": "creator"}}, {"query": "bridge"},
                    {"area": "personal"}, {"limit": 2}]
        for change in variants:
            args = {"scope": SCOPE, "limit": 1, "cursor": cursor, **change}
            with self.subTest(change=change), self.assertRaises(ValueError):
                build_chronicle(records, **args)
        changed = copy.deepcopy(records)
        changed[0]["text"] += " A later revision."
        with self.assertRaises(ValueError):
            build_chronicle(changed, scope=SCOPE, limit=1, cursor=cursor)
        for invalid in ("!", "not-json", "", "e30", 100, "x" * 1001):
            with self.subTest(cursor=invalid), self.assertRaises(ValueError):
                build_chronicle(records, cursor=invalid)

    def test_explicit_cross_campaign_branch_or_access_scope_in_record_is_rejected(self):
        record = projected_records()[0]
        for key in ("campaign_id", "branch_id", "access_scope_id"):
            for value in ({key: "other"}, {"scope": {key: "other"}}):
                with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                    build_chronicle([{**record, **value}], scope=SCOPE)

    def test_bad_inputs_do_not_guess_or_fall_back_to_an_authoritative_world(self):
        for records in ({"actors": {"secret": {}}}, ["record"], [{"text": "no stable ID"}],
                        [{"id": "x", "text": 3}], [{"id": "x", "source_available": "yes"}]):
            with self.subTest(records=records), self.assertRaises(ValueError):
                build_chronicle(records)
        for kwargs in ({"limit": 0}, {"limit": 101}, {"limit": True}, {"query": 2},
                       {"area": "unknown"}, {"scope": "world"}, {"entity_id": ""}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                build_chronicle([], **kwargs)


if __name__ == "__main__":
    unittest.main()
