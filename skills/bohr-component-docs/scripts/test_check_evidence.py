"""Synthetic record tests; these do not validate Figma or online collection."""
import json
from pathlib import Path
import tempfile
import unittest

from check_evidence import digest, validate


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.raw = self.root / "synthetic.txt"
        self.raw.write_text("synthetic fixture, not production evidence")
        self.contract = {"scope": "synthetic comparison", "references": [
            {"role": r, "locator": "synthetic"} for r in ("visual", "capability", "online")],
            "checks": [{"id": g, "group": g, "subject": "synthetic source", "applicable": True,
                        "expected": {"component": "whole", "state": "open", "gap": 4},
                        "method": "equal", "evidence_kind": "raw-online" if g == "D" else "raw-design"}
                       for g in ("P", "A", "B", "C", "D", "C1", "C2", "E")]}
        self.report = {"revision": "r1", "checks": [
            {"id": c["id"], "target": "synthetic target", "actual": dict(c["expected"]),
             "checked_revision": "r1", "status": "已通过", "evidence": [
                 {"path": "synthetic.txt", "sha256": digest(self.raw),
                  "kind": c["evidence_kind"], "locator": "synthetic observation"}]}
            for c in self.contract["checks"]]}

    def run_check(self):
        cp, rp = self.root / "contract.json", self.root / "report.json"
        cp.write_text(json.dumps(self.contract))
        self.report["contract_sha256"] = digest(cp)
        rp.write_text(json.dumps(self.report))
        return validate(cp, rp)

    def test_complete_record(self):
        self.assertFalse(self.run_check()["errors"])

    def test_whole_replaced_with_item(self):
        self.report["checks"][3]["actual"]["component"] = "item"
        self.assertTrue(self.run_check()["errors"])

    def test_same_count_wrong_state(self):
        self.report["checks"][1]["actual"]["state"] = "closed"
        self.assertTrue(self.run_check()["errors"])

    def test_spacing_changed(self):
        self.report["checks"][2]["actual"]["gap"] = 24
        self.assertTrue(self.run_check()["errors"])

    def test_missing_check(self):
        self.report["checks"].pop()
        self.assertTrue(self.run_check()["errors"])

    def test_online_replaced_with_design(self):
        self.report["checks"][4]["evidence"][0]["kind"] = "raw-design"
        self.assertTrue(self.run_check()["errors"])

    def test_only_summary(self):
        self.report["checks"][4]["evidence"][0]["kind"] = "summary"
        self.assertTrue(self.run_check()["errors"])

    def test_missing_file(self):
        self.raw.unlink()
        self.assertTrue(self.run_check()["errors"])

    def test_changed_evidence(self):
        self.raw.write_text("changed")
        self.assertTrue(self.run_check()["errors"])

    def test_stale_revision(self):
        self.report["revision"] = "r2"
        self.assertTrue(self.run_check()["errors"])

    def test_not_verified(self):
        self.report["checks"][4]["status"] = "未验证"
        self.assertTrue(self.run_check()["errors"])

    def test_scoped_not_applicable(self):
        self.contract["checks"][4].update(applicable=False, reason="local layout only")
        self.report["checks"][4]["status"] = "不适用"
        self.assertFalse(self.run_check()["errors"])

    def test_unjustified_not_applicable(self):
        self.contract["checks"][4]["applicable"] = False
        self.report["checks"][4]["status"] = "不适用"
        self.assertTrue(self.run_check()["errors"])

    def test_duplicate(self):
        self.report["checks"].append(self.report["checks"][0])
        with self.assertRaises(ValueError):
            self.run_check()

    def test_manual_review_requires_decision(self):
        self.contract["checks"][7]["method"] = "review"
        self.assertTrue(self.run_check()["errors"])
        self.report["checks"][7]["decision"] = "Synthetic review only; no visual acceptance claimed"
        self.assertFalse(self.run_check()["errors"])


if __name__ == "__main__":
    unittest.main()
