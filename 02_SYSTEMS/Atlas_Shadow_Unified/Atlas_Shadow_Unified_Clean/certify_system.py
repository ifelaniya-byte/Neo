#!/usr/bin/env python3
"""Deterministic certification for the SECRET_ZIP primary architecture."""
from pathlib import Path
import json
import py_compile
import tempfile

import atlas_shadow_unified as a
from recursive_optimizer import TelemetryCollector, CandidateEvaluator

ROOT = Path(__file__).resolve().parent


def build_stationary():
    pod = a.KnowledgePod()
    for cid, text in a.AI_CODING_KNOWLEDGE:
        pod.add(cid, text, force=True)
    atlas = a.UnifiedAtlas()
    math_e = a.MathEngine()
    logic = a.LogicEngine()
    code = a.CodeLangDetector()
    pred = a.PredictiveEngine()
    tools = a.build_tools()
    planner = a.Planner()
    gradient = a.TextualGradientEngine(a.LANGUAGE_FORMS)
    router = a.Router(pod, math_e, logic, code, pred, tools, atlas, planner, gradient=gradient)
    agent = a.Agent(router, planner)
    stationary = a.StationaryModel(atlas, pod, gradient=gradient, code=code,
                                    math_e=math_e, logic=logic, planner=planner)
    actor = a.ExperimentalMergedModel(router, agent=agent)
    return atlas, stationary, actor


def main():
    results = {}

    py_files = sorted(ROOT.glob('*.py'))
    for path in py_files:
        py_compile.compile(str(path), doraise=True)
    results['python_compile'] = {'ok': True, 'files': len(py_files)}

    audit = a.SourceEngineer(str(ROOT)).audit()
    results['source_engineer'] = {
        'ok': audit['ok'], 'files': audit['file_count'],
        'critical': audit['critical_count'], 'high': audit['high_count']
    }

    atlas, stationary, actor = build_stationary()
    gate = a.SuperMathCodingGate(stationary.math_e, stationary.logic, stationary.code).run()
    results['super_math_code'] = {'ok': gate['ok'], 'checks': gate['count']}

    initial = stationary.full_verification()
    results['stationary_initial'] = {
        'ok': initial['all_ok'], 'formulas': initial['formulas']
    }

    pipeline = a.SuperReasoningPipeline(stationary, actor).run('machine learning attention transformer')
    results['super_reasoning_pipeline'] = {'ok': pipeline['ok'], 'order': pipeline['pipeline']}

    reflective = a.ReflectiveReasoningLoop(stationary, actor, max_rounds=3).run('attention learning theorem')
    results['reflective_loop'] = {
        'ok': reflective['final_verification_all_ok'],
        'rounds': len(reflective['rounds']),
        'source_ok': reflective['final_source_ok'],
        'math_ok': reflective['final_math_logic_ok'],
        'formulas': reflective['final_formulas'],
    }

    # Verify the intentional corruption/reseal invariant independently.
    atlas.corrupt('Pythagorean theorem', 'latex', r'a^2+b^2=c^3')
    compromised = stationary.full_verification()
    actor_report = stationary.process(focus='verify shadow integrity', force_verify=True)
    actor_actions = actor.act(actor_report)
    recovered = stationary.full_verification()
    results['corruption_recovery'] = {
        'detected': compromised['formulas']['compromised'] == 1,
        'actor_resealed': any(x.get('action') == 'reseal_compromised' and x.get('status') == 'executed' for x in actor_actions),
        'recovered': recovered['all_ok'],
    }

    # Catch the historical telemetry double-execution bug with a counter.
    calls = {'n': 0}
    def counted(payload):
        calls['n'] += 1
    samples = TelemetryCollector().run(counted, ['a', 'b', 'c'])
    results['telemetry_single_invocation'] = {'ok': calls['n'] == 3, 'calls': calls['n'], 'samples': len(samples)}

    ev = CandidateEvaluator('unified_orchestrator', repetitions=2)
    det, detail = ev.deterministic_check(['solve equation', 'atlas summary'])
    bench = ev.benchmark(['solve equation', 'atlas summary'], None)
    results['optimizer_unified_candidate'] = {
        'deterministic': det, 'detail': detail,
        'samples': bench.samples, 'errors': bench.error_rate,
    }

    results['all_ok'] = all([
        results['python_compile']['ok'], results['source_engineer']['ok'],
        results['super_math_code']['ok'], results['stationary_initial']['ok'],
        results['super_reasoning_pipeline']['ok'], results['reflective_loop']['ok'],
        all(results['corruption_recovery'].values()),
        results['telemetry_single_invocation']['ok'],
        results['optimizer_unified_candidate']['deterministic'] and results['optimizer_unified_candidate']['errors'] == 0,
    ])
    print(json.dumps(results, indent=2, default=str))
    return 0 if results['all_ok'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
