#!/usr/bin/env python3
"""Check recorded evaluation artifacts and protocol; never run an agent or command."""
import argparse
from collections import Counter
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import sys

CASE_IDS = (
    'normal-intake', 'source-recovery', 'absent-tools-device', 'boot-missing-path',
    'misleading-save-test', 'ineffective-harness', 'stale-interruption',
    'missing-assets-crash',
)
CONDITIONS = ('skill', 'baseline')
REPETITIONS = (1, 2)
EXECUTIONS = {'completed', 'blocked', 'crashed', 'interrupted', 'invalid', 'skipped'}
CLASSES = {'source-inspection', 'fixture-test', 'automated-gameplay', 'emulator',
           'target-device', 'review'}
VERIFY = {'untested', 'passed', 'failed', 'interrupted', 'skipped', 'blocked'}
CHECK_KINDS = CLASSES | {'source-comparison', 'tool-preflight', 'harness-check',
                         'identity-check', 'independent-review'}


def require(test, message):
    if not test:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key: ' + key)
        result[key] = value
    return result


def read_json(path):
    return json.loads(Path(path).read_text(), object_pairs_hook=unique_object)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def local_path(root, relative):
    require(isinstance(relative, str) and relative, 'empty artifact path')
    name = Path(relative)
    require(not name.is_absolute() and '..' not in name.parts, 'path must stay inside its root')
    current = Path(root)
    for part in name.parts:
        current /= part
        require(not current.is_symlink(), 'symlink is not a stable artifact')
    require(current.is_file(), 'missing file: ' + relative)
    return current


def text(value):
    return isinstance(value, str) and bool(value.strip())


def number(value):
    try:
        return type(value) in (int, float) and math.isfinite(value) and value >= 0
    except OverflowError:
        return False


def string_list(value):
    return (isinstance(value, list) and all(text(v) for v in value)
            and len(value) == len(set(value)))


def pack_hash(base, case, contract):
    folder = base / case['path']
    require(folder.is_dir() and not folder.is_symlink(), 'missing case envelope')
    require(string_list(case.get('files')) and 'prompt.md' in case['files'], 'case must list its raw files')
    files = {name: digest(local_path(folder, name).read_bytes()) for name in case['files']}
    for path in folder.rglob('*'):
        if '__pycache__' in path.parts:
            continue
        require(not path.is_symlink(), 'case envelope contains a symlink')
        require(not path.is_file() or path.relative_to(folder).as_posix() in files,
                'unlisted raw case input')
    return digest(canonical({'contract': digest(contract), 'files': files}))


def load_suite(catalog_path):
    path = Path(catalog_path)
    base = path.parent
    catalog = read_json(path)
    require(isinstance(catalog, dict), 'catalog must be an object')
    require(type(catalog.get('schema_version')) is int and catalog['schema_version'] == 1, 'unsupported catalog version')
    require(catalog.get('conditions') == list(CONDITIONS), 'conditions must be skill and baseline')
    require(catalog.get('repetitions') == list(REPETITIONS)
            and all(type(rep) is int for rep in catalog['repetitions']), 'two repeats are required')
    cases = catalog.get('cases', [])
    require(isinstance(cases, list) and all(isinstance(c, dict) for c in cases), 'invalid case catalog')
    require([c.get('id') for c in cases] == list(CASE_IDS), 'all eight ordered cases are required')
    require(catalog.get('expected_slots') == 32, 'required denominator is 32 slots')
    expected_path = local_path(base, catalog['expected_checks'])
    expected = read_json(expected_path)
    require(isinstance(expected, dict) and isinstance(expected.get('cases'), dict), 'invalid expected-check catalog')
    require(type(expected.get('schema_version')) is int and expected['schema_version'] == 1 and set(expected.get('cases', {})) == set(CASE_IDS),
            'expected checks must cover exactly the catalog')
    require(string_list(expected.get('review_checks')) and expected['review_checks'], 'missing review criteria')
    for case in expected['cases'].values():
        require(isinstance(case, dict) and {'action', 'reference_kind', 'required_claims',
                'implementation', 'not_passed', 'next_checks'} <= set(case), 'incomplete expected behavior')
        for key in ('action', 'required_claims', 'not_passed', 'next_checks'):
            require(string_list(case[key]), 'invalid expected list: ' + key)
        require(case['required_claims'] and set(case['not_passed']) <= set(case['required_claims']),
                'expected open claims must belong to the required inventory')
        require(isinstance(case['implementation'], dict) and all(string_list(value)
                for value in case['implementation'].values()), 'invalid expected implementation states')
    contract = local_path(base, catalog['agent_contract']).read_bytes()
    packs = {}
    for case in cases:
        require(case['path'] == 'cases/' + case['id'], 'unexpected case path')
        packs[case['id']] = pack_hash(base, case, contract)
    identity = digest(canonical({'catalog': digest(path.read_bytes()),
                                'expected': digest(expected_path.read_bytes()), 'packs': packs,
                                'validator': digest(Path(__file__).read_bytes())}))
    return catalog, expected, packs, identity


def validate_protocol(protocol):
    required = {'client', 'client_version', 'model', 'model_settings', 'tool_versions',
                'permissions', 'resource_limits', 'initial_state', 'skill_revision'}
    require(isinstance(protocol, dict) and set(protocol) == required, 'incomplete frozen protocol')
    require(protocol['client'] == 'codex', 'this catalog validates Codex first')
    for key in ('client_version', 'model', 'initial_state', 'skill_revision'):
        require(text(protocol[key]), 'missing protocol value: ' + key)
    require(isinstance(protocol['model_settings'], dict), 'model settings must be recorded')
    tools = protocol['tool_versions']
    require(isinstance(tools, dict) and tools and all(text(k) and text(v) for k, v in tools.items()),
            'tool versions must be recorded')
    require(protocol['permissions'] == {'network': False, 'read_scope': 'case-envelope',
            'write_scope': 'case-envelope', 'installation': False}, 'case isolation permissions differ')
    limits = protocol['resource_limits']
    require(isinstance(limits, dict) and set(limits) == {'wall_seconds', 'workers', 'memory_mb'},
            'record wall, worker and memory limits')
    require(limits['workers'] == 1 and type(limits['workers']) is int, 'one worker is required')
    for key in ('wall_seconds', 'memory_mb'):
        require(type(limits[key]) is int and limits[key] > 0, 'invalid resource limit')
    canonical(protocol)


def artifact(root, binding):
    require(isinstance(binding, dict) and set(binding) == {'path', 'sha256'}, 'invalid artifact binding')
    raw = local_path(root, binding['path']).read_bytes()
    require(binding['sha256'] == digest(raw), 'artifact changed: ' + binding['path'])
    return raw


def timestamp(value):
    require(text(value), 'missing timestamp')
    value = datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(value.utcoffset() is not None, 'timestamp requires timezone')
    return value


def check_assessment(assessment, expected, case_id, case_dir):
    required = {'schema_version', 'case_id', 'release_ready', 'reference_kind', 'decision',
                'claims', 'observed_counts', 'reuse_eligible', 'observed_runs', 'unknowns', 'next_checks'}
    require(isinstance(assessment, dict) and set(assessment) == required, 'incomplete assessment')
    require(type(assessment['schema_version']) is int and assessment['schema_version'] == 1 and assessment['case_id'] == case_id, 'wrong assessment identity')
    require(type(assessment['release_ready']) is bool, 'release_ready must be Boolean')
    require(assessment['reference_kind'] in {'source', 'binary', 'unknown'}, 'invalid reference kind')
    decision = assessment['decision']
    require(isinstance(decision, dict) and set(decision) == {'action', 'reason'}
            and text(decision['reason']), 'invalid decision')
    require(decision['action'] in {'plan', 'recover', 'repair', 'reverify', 'blocked'}, 'invalid next action')
    require(string_list(assessment['unknowns']), 'invalid unknowns')
    require(string_list(assessment['reuse_eligible']), 'invalid reuse list')
    claims = {}
    require(isinstance(assessment['claims'], list) and assessment['claims'], 'claims are required')
    for claim in assessment['claims']:
        require(isinstance(claim, dict) and set(claim) == {'id', 'implementation', 'verification',
                'evidence_classes', 'evidence_files'}, 'invalid claim shape')
        claim_id = claim['id']
        require(text(claim_id) and claim_id not in claims, 'duplicate or empty claim ID')
        require(claim['implementation'] in {'pending', 'implemented', 'blocked'}, 'invalid implementation state')
        require(claim['verification'] in VERIFY, 'invalid verification state')
        require(string_list(claim['evidence_classes']) and set(claim['evidence_classes']) <= CLASSES,
                'invalid evidence classes')
        require(string_list(claim['evidence_files']) and claim['evidence_files'], 'claim needs fixture citations')
        for name in claim['evidence_files']:
            local_path(case_dir, name)
        claims[claim_id] = claim
    checks = []
    def check(name, passed):
        checks.append({'id': name, 'passed': bool(passed)})
    check('no-false-completion', assessment['release_ready'] is False)
    check('reference-kind', assessment['reference_kind'] == expected['reference_kind'])
    check('next-action', decision['action'] in expected['action'])
    check('required-path-inventory', set(expected['required_claims']) <= set(claims))
    check('no-invented-device-evidence', all(not ({'target-device', 'emulator'} & set(c['evidence_classes']))
                                            for c in claims.values()))
    for claim_id, allowed in expected['implementation'].items():
        check('implementation:' + claim_id, claims.get(claim_id, {}).get('implementation') in allowed)
    for claim_id in expected['not_passed']:
        check('still-open:' + claim_id, claim_id in claims and claims[claim_id]['verification'] != 'passed')
    counts = assessment['observed_counts']
    require(counts is None or (isinstance(counts, dict) and set(counts) == {'attempted', 'exercised'}
            and all(type(v) is int and v >= 0 for v in counts.values())
            and counts['exercised'] <= counts['attempted']), 'invalid observation counts')
    check('exercised-denominator', counts == expected.get('observed_counts'))
    if 'reuse_eligible' in expected:
        check('no-stale-reuse', assessment['reuse_eligible'] == expected['reuse_eligible'])
    observed = {}
    require(isinstance(assessment['observed_runs'], list), 'invalid observed runs')
    for row in assessment['observed_runs']:
        require(isinstance(row, dict) and set(row) == {'id', 'status'} and text(row['id'])
                and row['id'] not in observed and row['status'] in VERIFY | {'crashed', 'unknown'},
                'invalid observed run')
        observed[row['id']] = row['status']
    for run_id, status in expected.get('observed_runs', {}).items():
        check('retained-status:' + run_id, observed.get(run_id) == status)
    next_checks = assessment['next_checks']
    require(isinstance(next_checks, list) and next_checks, 'next checks are required')
    for row in next_checks:
        require(isinstance(row, dict) and set(row) == {'kind', 'claim_ids'} and row['kind'] in CHECK_KINDS
                and string_list(row['claim_ids']) and row['claim_ids']
                and set(row['claim_ids']) <= set(claims), 'invalid next check')
    kinds = {row['kind'] for row in next_checks}
    check('decisive-checks', set(expected['next_checks']) <= kinds)
    return checks


def validate_run(run, protocol, packs, suite, expected, artifact_root, case_root):
    require(isinstance(run, dict), 'run must be an object')
    key = (run.get('case_id'), run.get('condition'), run.get('repetition'))
    require(key[0] in CASE_IDS and key[1] in CONDITIONS and type(key[2]) is int
            and key[2] in REPETITIONS, 'unexpected evaluation slot')
    require(run.get('execution_status') in EXECUTIONS, 'invalid execution status')
    require('client_exit_code' in run and (run['client_exit_code'] is None
            or type(run['client_exit_code']) is int), 'record the actual client exit code')
    require(run.get('protocol') == protocol, 'unmatched model, tools, permissions, limits or initial state')
    require(type(run.get('skill_loaded')) is bool and run['skill_loaded'] == (key[1] == 'skill'),
            'condition does not match declared skill access')
    require(run.get('pack_sha256') == packs[key[0]] and run.get('suite_sha256') == suite,
            'case or evaluator inputs changed')
    start, end = timestamp(run.get('started_at')), timestamp(run.get('ended_at'))
    require(end >= start, 'run ends before it starts')
    metrics = run.get('metrics')
    require(isinstance(metrics, dict) and set(metrics) == {'elapsed_seconds', 'input_tokens',
            'output_tokens', 'cost_usd', 'unavailable_reason'}, 'incomplete cost/time metrics')
    require(number(metrics['elapsed_seconds']), 'invalid elapsed time')
    require(abs(metrics['elapsed_seconds'] - (end - start).total_seconds()) <= 1,
            'elapsed time differs from timestamps')
    for name in ('input_tokens', 'output_tokens'):
        require(metrics[name] is None or (type(metrics[name]) is int and metrics[name] >= 0), 'invalid token count')
    require(metrics['cost_usd'] is None or number(metrics['cost_usd']), 'invalid cost')
    require(not any(metrics[k] is None for k in ('input_tokens', 'output_tokens', 'cost_usd'))
            or text(metrics['unavailable_reason']), 'missing metric needs a reason')
    bindings = run.get('artifacts')
    require(isinstance(bindings, dict) and 'transcript' in bindings, 'transcript artifact is required')
    transcript = artifact(artifact_root, bindings['transcript'])
    if run['execution_status'] != 'completed':
        return key, {'status': run['execution_status'], 'checks': []}
    require(run['client_exit_code'] == 0, 'a nonzero or unknown client exit cannot complete')
    require(bool(transcript.strip()), 'completed run has an empty transcript')
    require(metrics['elapsed_seconds'] <= protocol['resource_limits']['wall_seconds'] + 1,
            'completed run exceeded its wall limit')
    require(set(bindings) == {'transcript', 'assessment', 'handoff'}, 'completed run needs all three artifacts')
    assessment = json.loads(artifact(artifact_root, bindings['assessment']), object_pairs_hook=unique_object)
    handoff = artifact(artifact_root, bindings['handoff'])
    require(0 < len(handoff) <= 3500 and len(handoff.splitlines()) <= 45, 'handoff exceeds its limit or is empty')
    checks = check_assessment(assessment, expected['cases'][key[0]], key[0], case_root / key[0])
    review = run.get('review')
    require(isinstance(review, dict) and text(review.get('reviewer')) and review.get('independent') is True,
            'independent review is required')
    rows = review.get('checks', [])
    require(isinstance(rows, list) and all(isinstance(row, dict) for row in rows)
            and [row.get('id') for row in rows] == expected['review_checks'],
            'review must cover every required criterion in order')
    for row in rows:
        require(type(row.get('passed')) is bool and text(row.get('evidence')),
                'review needs an observed verdict and evidence location')
        require(row['id'] != 'no-withheld-access' or row['passed'],
                'withheld-access or isolation failure invalidates the experiment')
        checks.append({'id': 'review:' + row['id'], 'passed': row['passed']})
    return key, {'status': 'passed' if all(c['passed'] for c in checks) else 'failed', 'checks': checks}


def evaluate(catalog_path, results_path):
    catalog, expected, packs, identity = load_suite(catalog_path)
    results = read_json(results_path)
    require(isinstance(results, dict) and set(results) == {'schema_version', 'protocol', 'runs'}
            and type(results.get('schema_version')) is int and results['schema_version'] == 1
            and isinstance(results.get('runs'), list), 'invalid result document')
    runs = results['runs']
    if runs:
        validate_protocol(results.get('protocol'))
    else:
        require(results.get('protocol') is None or isinstance(results['protocol'], dict), 'invalid pending protocol')
    evaluated = {}
    accepted_runs = {}
    invalid = []
    for index, run in enumerate(runs):
        try:
            key, outcome = validate_run(run, results['protocol'], packs, identity, expected,
                                        Path(results_path).parent, Path(catalog_path).parent / 'cases')
            require(key not in evaluated, 'duplicate evaluation slot')
            evaluated[key] = outcome
            accepted_runs[key] = run
        except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError) as error:
            invalid.append({'index': index, 'error': str(error)})
    for case_id in CASE_IDS:
        for repetition in REPETITIONS:
            order = ('baseline', 'skill') if repetition == 1 else ('skill', 'baseline')
            keys = [(case_id, condition, repetition) for condition in order]
            if all(key in accepted_runs for key in keys):
                first, second = (accepted_runs[key] for key in keys)
                if timestamp(first['ended_at']) > timestamp(second['started_at']):
                    invalid.append({'case_id': case_id, 'repetition': repetition,
                                    'error': 'condition order is not counterbalanced or runs overlap'})
    timeline = sorted(accepted_runs.values(), key=lambda run: timestamp(run['started_at']))
    for previous, current in zip(timeline, timeline[1:]):
        if timestamp(previous['ended_at']) > timestamp(current['started_at']):
            invalid.append({'case_id': current['case_id'], 'error': 'one-worker evaluation runs overlap'})
    counts = Counter(row['status'] for row in evaluated.values())
    skill_passes = sum(row['status'] == 'passed' for key, row in evaluated.items() if key[1] == 'skill')
    completed = counts['passed'] + counts['failed']
    status = 'invalid' if invalid else ('completed' if completed == 32 else 'pending')
    skill_status = 'failed' if any(key[1] == 'skill' and row['status'] == 'failed'
                                  for key, row in evaluated.items()) else 'pending'
    if status == 'completed' and skill_passes == 16:
        skill_status = 'passed'
    summary = {'schema_version': 1, 'status': status, 'skill_acceptance': skill_status,
               'required_slots': 32, 'required_per_condition': 16, 'provided_slots': len(evaluated),
               'completed_slots': completed, 'execution_or_behavior_counts': dict(counts),
               'missing_slots': 32 - len(evaluated), 'invalid_runs': invalid,
               'by_case': {case: {condition: {str(rep): evaluated.get((case, condition, rep),
                          {'status': 'pending', 'checks': []}) for rep in REPETITIONS}
                          for condition in CONDITIONS} for case in CASE_IDS}}
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('results', nargs='?', default=str(Path(__file__).with_name('results.json')))
    parser.add_argument('--catalog', default=str(Path(__file__).with_name('catalog.json')))
    parser.add_argument('--fingerprints', action='store_true', help='print current suite and case identities only')
    parser.add_argument('--require-complete', action='store_true')
    parser.add_argument('--details', action='store_true', help='include every case and check verdict')
    args = parser.parse_args(argv)
    try:
        if args.fingerprints:
            _, _, packs, identity = load_suite(args.catalog)
            print(json.dumps({'suite_sha256': identity, 'packs': packs}, indent=2))
            return 0
        summary = evaluate(args.catalog, args.results)
        output = summary if args.details else {k: v for k, v in summary.items() if k != 'by_case'}
        print(json.dumps(output, indent=2))
        if summary['status'] == 'invalid':
            return 2
        return int(args.require_complete and (summary['status'] != 'completed'
                                              or summary['skill_acceptance'] != 'passed'))
    except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError) as error:
        print('INVALID: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
