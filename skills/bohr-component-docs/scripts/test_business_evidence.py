"""Business record gate tests: synthetic fixtures, never Figma acceptance."""
import unittest
import test_check_evidence as fixtures


class BusinessEvidenceTests(unittest.TestCase):
    run_check = fixtures.EvidenceTests.run_check
    def setUp(self):
        fixtures.EvidenceTests.setUp(self)
        self.contract['deliverables'] = ['business-cases']
        self.contract['business_scenarios'] = [{
            'id': 'feedback-web', 'platform': 'Web', 'task': 'submit feedback',
            'source_check': 'D', 'composition_check': 'C',
            'elements': [
                {'id': 'description', 'source': 'input', 'check': 'A'},
                {'id': 'consent', 'source': 'checkbox', 'check': 'B'},
                {'id': 'submit', 'source': 'button', 'check': 'C1'}],
            'relations': [{'from': 'consent', 'to': 'submit', 'check': 'C2'}]}]

    def test_complete_business_record(self):
        self.assertFalse(self.run_check()['errors'])

    def test_business_missing_scenarios(self):
        del self.contract['business_scenarios']
        self.assertTrue(self.run_check()['errors'])

    def test_business_empty_scenarios(self):
        self.contract['business_scenarios'] = []
        self.assertTrue(self.run_check()['errors'])

    def test_business_missing_composition(self):
        del self.contract['business_scenarios'][0]['composition_check']
        self.assertTrue(self.run_check()['errors'])

    def test_business_omitted_element_mapping(self):
        self.contract['business_scenarios'][0]['elements'][2]['check'] = 'missing'
        self.assertTrue(self.run_check()['errors'])

    def test_business_element_exempted(self):
        self.contract['checks'][1].update(applicable=False, reason='not enough time')
        self.report['checks'][1]['status'] = '不适用'
        self.assertTrue(self.run_check()['errors'])

    def test_business_relation_unknown_endpoint(self):
        self.contract['business_scenarios'][0]['relations'][0]['to'] = 'unknown'
        self.assertTrue(self.run_check()['errors'])

    def test_business_no_relations(self):
        self.contract['business_scenarios'][0]['relations'] = []
        self.assertTrue(self.run_check()['errors'])

    def test_business_source_design_only(self):
        self.contract['business_scenarios'][0]['source_check'] = 'A'
        self.assertTrue(self.run_check()['errors'])

    def test_business_duplicate_platform_is_not_new_scenario(self):
        self.contract['business_scenarios'].append(dict(self.contract['business_scenarios'][0]))
        self.assertTrue(self.run_check()['errors'])

    def test_business_incomplete_state_stays_failed(self):
        self.report['checks'][3]['status'] = '未验证'
        self.assertTrue(self.run_check()['errors'])

    def test_nonbusiness_local_task_unchanged(self):
        self.contract.pop('business_scenarios')
        self.contract['deliverables'] = ['local-icon-fix']
        self.assertFalse(self.run_check()['errors'])

    def test_business_source_blank(self):
        self.contract['business_scenarios'][0]['elements'][0]['source'] = '   '
        self.assertTrue(self.run_check()['errors'])

    def test_business_source_wrong_type(self):
        self.contract['business_scenarios'][0]['elements'][0]['source'] = {'label': 'input'}
        self.assertTrue(self.run_check()['errors'])

    def test_business_declaration_missing(self):
        del self.contract['deliverables']
        self.assertTrue(self.run_check()['errors'])
