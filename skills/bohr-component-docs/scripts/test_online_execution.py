"""Synthetic execution records; no live endpoint acceptance."""
import unittest
import test_check_evidence as fixtures


class OnlineExecutionTests(unittest.TestCase):
    run_check = fixtures.EvidenceTests.run_check

    def setUp(self):
        fixtures.EvidenceTests.setUp(self)

    def test_complete_two_platform_records(self):
        self.assertFalse(self.run_check()['errors'])

    def test_missing_platform_is_rejected(self):
        self.contract['checks'].pop()
        self.report['checks'].pop()
        self.assertTrue(self.run_check()['errors'])

    def test_no_execution_cannot_pass(self):
        del self.report['checks'][4]['execution']
        self.assertTrue(self.run_check()['errors'])

    def test_unattempted_cannot_pass(self):
        self.report['checks'][4]['execution']['state'] = 'not-attempted'
        self.assertTrue(self.run_check()['errors'])

    def test_blocked_cannot_pass(self):
        self.report['checks'][4]['execution'].update(state='blocked', recovery='restore access')
        self.assertTrue(self.run_check()['errors'])

    def test_missing_action_cannot_pass(self):
        del self.report['checks'][4]['execution']['action']
        self.assertTrue(self.run_check()['errors'])

    def test_missing_before_after_cannot_pass(self):
        del self.report['checks'][4]['execution']['before']
        self.assertTrue(self.run_check()['errors'])

    def test_local_scope_can_exempt_both_platforms(self):
        for i in (4, 8):
            self.contract['checks'][i].update(applicable=False, reason='local translation only')
            self.report['checks'][i]['status'] = '不适用'
            self.report['checks'][i].pop('execution')
        self.assertFalse(self.run_check()['errors'])

    def test_design_evidence_cannot_be_endpoint_evidence(self):
        self.contract['checks'][4]['evidence_kind'] = 'raw-design'
        self.report['checks'][4]['evidence'][0]['kind'] = 'raw-design'
        self.assertTrue(self.run_check()['errors'])
