"""Synthetic validator tests. These do not call agents or supply live evaluations."""
import contextlib
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('evaluation_results', ROOT / 'check_results.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class ResultChecks(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.suite = self.root / 'evaluations'
        shutil.copytree(ROOT, self.suite, ignore=shutil.ignore_patterns('tests', '__pycache__'))
        self.catalog = self.suite / 'catalog.json'
        _, self.expected, self.packs, self.identity = checker.load_suite(self.catalog)
        self.protocol = {
            'client': 'codex', 'client_version': 'synthetic-test-version',
            'model': 'synthetic-test-model', 'model_settings': {'reasoning_effort': 'test'},
            'tool_versions': {'python': 'synthetic'},
            'permissions': {'network': False, 'read_scope': 'case-envelope',
                            'write_scope': 'case-envelope', 'installation': False},
            'resource_limits': {'wall_seconds': 30, 'workers': 1, 'memory_mb': 256},
            'initial_state': 'synthetic unit test, no actual agent', 'skill_revision': 'synthetic-revision',
        }
        self.results = {'schema_version': 1, 'protocol': deepcopy(self.protocol), 'runs': []}
        self.results_path = self.root / 'results.json'

    def binding(self, path, content):
        path = self.root / path
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = content.encode() if isinstance(content, str) else content
        path.write_bytes(raw)
        return {'path': path.relative_to(self.root).as_posix(), 'sha256': hashlib.sha256(raw).hexdigest()}

    def assessment(self, case_id):
        expected = self.expected['cases'][case_id]
        return {
            'schema_version': 1, 'case_id': case_id, 'release_ready': False,
            'reference_kind': expected['reference_kind'],
            'decision': {'action': expected['action'][0], 'reason': 'Synthetic validator test.'},
            'claims': [{'id': claim_id, 'implementation': expected['implementation'].get(claim_id, ['pending'])[0],
                        'verification': 'untested', 'evidence_classes': ['source-inspection'],
                        'evidence_files': ['reference.md']} for claim_id in expected['required_claims']],
            'observed_counts': expected.get('observed_counts'),
            'reuse_eligible': [],
            'observed_runs': [{'id': key, 'status': status} for key, status in expected.get('observed_runs', {}).items()],
            'unknowns': ['Synthetic validator test; no live evidence.'],
            'next_checks': [{'kind': kind, 'claim_ids': expected['required_claims']}
                            for kind in expected['next_checks']],
        }

    def make_run(self, case_id='normal-intake', condition='skill', repetition=1):
        folder = f'runs/{case_id}-{condition}-{repetition}'
        assessment = self.assessment(case_id)
        offset = checker.CASE_IDS.index(case_id) * 8 + ({'baseline': 0, 'skill': 2} if repetition == 1
                 else {'skill': 4, 'baseline': 6})[condition]
        start = datetime(2026, 11, 7, 10, tzinfo=timezone.utc) + timedelta(seconds=offset)
        run = {
            'case_id': case_id, 'condition': condition, 'repetition': repetition,
            'execution_status': 'completed', 'client_exit_code': 0, 'protocol': deepcopy(self.protocol),
            'skill_loaded': condition == 'skill', 'pack_sha256': self.packs[case_id],
            'suite_sha256': self.identity, 'started_at': start.isoformat(),
            'ended_at': (start + timedelta(seconds=1)).isoformat(),
            'metrics': {'elapsed_seconds': 1, 'input_tokens': None, 'output_tokens': None,
                        'cost_usd': None, 'unavailable_reason': 'Synthetic unit test; no model call.'},
            'artifacts': {
                'transcript': self.binding(folder + '/transcript.txt', 'Synthetic validator input, not an agent transcript.\n'),
                'assessment': self.binding(folder + '/assessment.json', json.dumps(assessment)),
                'handoff': self.binding(folder + '/handoff.md', 'Synthetic unit-test handoff.\n'),
            },
            'review': {'reviewer': 'synthetic-unit-test', 'independent': True,
                       'checks': [{'id': check, 'passed': True, 'evidence': 'Synthetic input for a validator test.'}
                                  for check in self.expected['review_checks']]},
        }
        self.results['runs'].append(run)
        return run

    def change_assessment(self, run, change):
        path = run['artifacts']['assessment']['path']
        value = json.loads((self.root / path).read_text())
        change(value)
        run['artifacts']['assessment'] = self.binding(path, json.dumps(value))

    def evaluate(self):
        self.results_path.write_text(json.dumps(self.results))
        return checker.evaluate(self.catalog, self.results_path)

    def outcome(self, summary, run):
        return summary['by_case'][run['case_id']][run['condition']][str(run['repetition'])]['status']

    def all_runs(self):
        for case in checker.CASE_IDS:
            for condition in checker.CONDITIONS:
                for repetition in checker.REPETITIONS:
                    self.make_run(case, condition, repetition)

    def test_unrun_denominator_is_32(self):
        self.results['protocol'] = None
        summary = self.evaluate()
        self.assertEqual((summary['status'], summary['skill_acceptance'], summary['missing_slots']),
                         ('pending', 'pending', 32))

    def test_required_completion_rejects_empty_suite(self):
        self.evaluate()
        with contextlib.redirect_stdout(io.StringIO()):
            code = checker.main([str(self.results_path), '--catalog', str(self.catalog), '--require-complete'])
        self.assertEqual(code, 1)

    def test_complete_synthetic_matrix(self):
        self.all_runs()
        summary = self.evaluate()
        self.assertEqual(summary['completed_slots'], 32)
        self.assertEqual((summary['status'], summary['skill_acceptance']), ('completed', 'passed'))

    def test_baseline_behavior_failure_is_comparison_not_missing_data(self):
        self.all_runs()
        run = next(r for r in self.results['runs'] if r['condition'] == 'baseline')
        self.change_assessment(run, lambda a: a.update(release_ready=True))
        summary = self.evaluate()
        self.assertEqual(self.outcome(summary, run), 'failed')
        self.assertEqual((summary['status'], summary['skill_acceptance']), ('completed', 'passed'))

    def test_skill_false_completion_fails(self):
        run = self.make_run()
        self.change_assessment(run, lambda a: a.update(release_ready=True))
        summary = self.evaluate()
        self.assertEqual(self.outcome(summary, run), 'failed')
        self.assertEqual(summary['skill_acceptance'], 'failed')

    def test_every_seeded_open_claim_cannot_pass(self):
        for case_id in checker.CASE_IDS:
            with self.subTest(case_id=case_id):
                run = self.make_run(case_id)
                claim_id = self.expected['cases'][case_id]['not_passed'][0]
                self.change_assessment(run, lambda a: next(c for c in a['claims'] if c['id'] == claim_id)
                                       .update(verification='passed'))
                self.assertEqual(self.outcome(self.evaluate(), run), 'failed')

    def test_requested_input_does_not_count_as_exercised(self):
        run = self.make_run('ineffective-harness')
        self.change_assessment(run, lambda a: a.update(observed_counts={'attempted': 4, 'exercised': 4}))
        self.assertEqual(self.outcome(self.evaluate(), run), 'failed')

    def test_stale_result_cannot_be_reused(self):
        run = self.make_run('stale-interruption')
        self.change_assessment(run, lambda a: a.update(reuse_eligible=['jump-old']))
        self.assertEqual(self.outcome(self.evaluate(), run), 'failed')

    def test_underlying_crash_cannot_be_wrapped_into_pass(self):
        run = self.make_run('missing-assets-crash')
        self.change_assessment(run, lambda a: a['observed_runs'][1].update(status='passed'))
        self.assertEqual(self.outcome(self.evaluate(), run), 'failed')

    def test_marking_everything_pending_is_not_a_valid_intake(self):
        run = self.make_run()
        self.change_assessment(run, lambda a: a['claims'][0].update(implementation='pending'))
        self.assertEqual(self.outcome(self.evaluate(), run), 'failed')

    def test_invented_device_evidence_fails(self):
        run = self.make_run()
        self.change_assessment(run, lambda a: a['claims'][0].update(evidence_classes=['target-device']))
        self.assertEqual(self.outcome(self.evaluate(), run), 'failed')

    def test_changed_protocol_is_invalid(self):
        for field, value in [('model', 'other'), ('initial_state', 'inherited history'),
                             ('tool_versions', {'python': 'different'})]:
            with self.subTest(field=field):
                self.results['runs'] = []
                run = self.make_run()
                run['protocol'][field] = value
                self.assertEqual(self.evaluate()['status'], 'invalid')

    def test_changed_case_is_invalid(self):
        self.make_run()
        (self.suite / 'cases/normal-intake/game.py').write_text('different input\n')
        self.assertEqual(self.evaluate()['status'], 'invalid')

    def test_changed_expected_checks_are_not_retroactive_passes(self):
        self.make_run()
        path = self.suite / 'evaluator/expected.json'
        value = json.loads(path.read_text())
        value['notes'] = 'Changed after a result.'
        path.write_text(json.dumps(value))
        self.assertEqual(self.evaluate()['status'], 'invalid')

    def test_changed_artifact_is_invalid(self):
        run = self.make_run()
        (self.root / run['artifacts']['transcript']['path']).write_text('changed')
        self.assertEqual(self.evaluate()['status'], 'invalid')

    def test_duplicate_slot_cannot_shrink_denominator(self):
        run = self.make_run()
        self.results['runs'].append(deepcopy(run))
        summary = self.evaluate()
        self.assertEqual(summary['status'], 'invalid')
        self.assertEqual(summary['missing_slots'], 31)

    def test_noncompleted_evaluation_never_passes(self):
        for status in checker.EXECUTIONS - {'completed'}:
            with self.subTest(status=status):
                self.results['runs'] = []
                run = self.make_run()
                run['execution_status'] = status
                summary = self.evaluate()
                self.assertEqual(self.outcome(summary, run), status)
                self.assertEqual(summary['skill_acceptance'], 'pending')
                self.assertEqual(summary['completed_slots'], 0)

    def test_missing_cost_is_not_zero(self):
        run = self.make_run()
        run['metrics']['unavailable_reason'] = ''
        self.assertEqual(self.evaluate()['status'], 'invalid')

    def test_nonfinite_cost_is_invalid(self):
        run = self.make_run()
        run['metrics']['cost_usd'] = float('nan')
        self.assertEqual(self.evaluate()['status'], 'invalid')

    def test_over_budget_completed_run_is_invalid(self):
        run = self.make_run()
        run['ended_at'] = '2026-11-07T10:01:00+00:00'
        run['metrics']['elapsed_seconds'] = 60
        self.assertEqual(self.evaluate()['status'], 'invalid')

    def test_artifact_cannot_escape_result_root(self):
        run = self.make_run()
        run['artifacts']['transcript']['path'] = '../outside.txt'
        self.assertEqual(self.evaluate()['status'], 'invalid')

    def test_symlink_artifact_is_invalid(self):
        run = self.make_run()
        original = self.root / run['artifacts']['transcript']['path']
        target = self.root / 'elsewhere.txt'
        target.write_bytes(original.read_bytes())
        original.unlink()
        original.symlink_to(target)
        self.assertEqual(self.evaluate()['status'], 'invalid')

    def test_handoff_limit_is_checked(self):
        run = self.make_run()
        path = run['artifacts']['handoff']['path']
        run['artifacts']['handoff'] = self.binding(path, 'line\n' * 46)
        self.assertEqual(self.evaluate()['status'], 'invalid')

    def test_review_failure_is_behavior_failure(self):
        run = self.make_run()
        run['review']['checks'][0]['passed'] = False
        self.assertEqual(self.outcome(self.evaluate(), run), 'failed')

    def test_malformed_review_is_invalid(self):
        run = self.make_run()
        run['review']['checks'] = [None]
        self.assertEqual(self.evaluate()['status'], 'invalid')

    def test_nonzero_client_exit_cannot_complete(self):
        run = self.make_run()
        run['client_exit_code'] = 1
        self.assertEqual(self.evaluate()['status'], 'invalid')

    def test_reversed_condition_order_is_invalid(self):
        baseline = self.make_run(condition='baseline')
        skill = self.make_run(condition='skill')
        baseline['started_at'], skill['started_at'] = skill['started_at'], baseline['started_at']
        baseline['ended_at'], skill['ended_at'] = skill['ended_at'], baseline['ended_at']
        self.assertEqual(self.evaluate()['status'], 'invalid')

    def test_overlapping_case_runs_violate_one_worker(self):
        first = self.make_run()
        second = self.make_run('source-recovery')
        second['started_at'], second['ended_at'] = first['started_at'], first['ended_at']
        self.assertEqual(self.evaluate()['status'], 'invalid')

    def test_baseline_isolation_failure_invalidates_skill_acceptance(self):
        self.all_runs()
        run = next(r for r in self.results['runs'] if r['condition'] == 'baseline')
        row = next(row for row in run['review']['checks'] if row['id'] == 'no-withheld-access')
        row['passed'] = False
        summary = self.evaluate()
        self.assertEqual(summary['status'], 'invalid')
        self.assertNotEqual(summary['skill_acceptance'], 'passed')

    def test_huge_metrics_are_invalid_without_overflow(self):
        for field in ('cost_usd', 'elapsed_seconds'):
            with self.subTest(field=field):
                self.results['runs'] = []
                run = self.make_run()
                run['metrics'][field] = 10 ** 400
                self.assertEqual(self.evaluate()['status'], 'invalid')

    def test_missing_required_case_is_not_smaller_success(self):
        value = json.loads(self.catalog.read_text())
        value['cases'].pop()
        self.catalog.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, 'eight'):
            checker.load_suite(self.catalog)

    def test_unlisted_fixture_input_is_rejected(self):
        (self.suite / 'cases/normal-intake/extra-answer.txt').write_text('unexpected input')
        with self.assertRaisesRegex(ValueError, 'unlisted'):
            checker.load_suite(self.catalog)

    def test_interpreter_cache_is_not_part_of_declared_envelope(self):
        folder = self.suite / 'cases/normal-intake/__pycache__'
        folder.mkdir()
        (folder / 'game.pyc').write_bytes(b'not an agent input')
        self.assertEqual(checker.load_suite(self.catalog)[3], self.identity)

    def test_boolean_schema_version_is_invalid(self):
        self.results['schema_version'] = True
        with self.assertRaisesRegex(ValueError, 'invalid result'):
            self.evaluate()

    def test_nonobject_catalog_exits_cleanly(self):
        self.catalog.write_text('[null]')
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(checker.main(['--catalog', str(self.catalog)]), 2)

    def test_nonobject_case_exits_cleanly(self):
        value = json.loads(self.catalog.read_text())
        value['cases'][0] = None
        self.catalog.write_text(json.dumps(value))
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(checker.main(['--catalog', str(self.catalog)]), 2)

    def test_nonobject_expected_checks_exit_cleanly(self):
        (self.suite / 'evaluator/expected.json').write_text('[]')
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(checker.main(['--catalog', str(self.catalog)]), 2)

    def test_duplicate_json_keys_are_rejected(self):
        self.results_path.write_text('{"schema_version":1,"schema_version":1,"protocol":null,"runs":[]}')
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            checker.evaluate(self.catalog, self.results_path)


if __name__ == '__main__':
    unittest.main()
