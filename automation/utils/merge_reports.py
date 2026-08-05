#!/usr/bin/env python3
"""
Merge Reports Utility
Combines test results from all parallel suite artifact folders into a single
consolidated JSON file.
Usage:
    python automation/utils/merge_reports.py --input automation/all-artifacts --output automation/reports/merged
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def load_all_results(input_dir: str) -> list:
    """Walk the input directory and collect all JSON test results."""
    results = []
    base = Path(input_dir)
    if not base.exists():
        print(f"Input directory not found: {input_dir}")
        return results

    for json_file in base.rglob('*.json'):
        try:
            with open(json_file, encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                results.extend(data)
            elif isinstance(data, dict):
                if 'tests' in data:
                    results.extend(data['tests'])
                elif 'test_id' in data:
                    results.append(data)
        except (json.JSONDecodeError, IOError) as e:
            print(f"WARN: Could not read {json_file}: {e}")

    return results


def deduplicate(results: list) -> list:
    """Remove duplicate results keeping the last occurrence."""
    seen = {}
    for r in results:
        key = (r.get('test_id', ''), r.get('name', ''), r.get('suite', ''))
        seen[key] = r
    return list(seen.values())


def compute_summary(results: list) -> dict:
    total = len(results)
    passed = sum(1 for r in results if r.get('status', '').lower() in ('passed', 'pass'))
    failed = sum(1 for r in results if r.get('status', '').lower() in ('failed', 'fail', 'error'))
    skipped = sum(1 for r in results if r.get('status', '').lower() in ('skipped', 'skip'))
    rate = round(passed / total * 100, 2) if total > 0 else 0.0

    modules: dict = {}
    for r in results:
        mod = r.get('module', 'Unknown')
        if mod not in modules:
            modules[mod] = {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0}
        modules[mod]['total'] += 1
        s = r.get('status', '').lower()
        if s in ('passed', 'pass'):
            modules[mod]['passed'] += 1
        elif s in ('failed', 'fail', 'error'):
            modules[mod]['failed'] += 1
        else:
            modules[mod]['skipped'] += 1

    return {
        'total': total,
        'passed': passed,
        'failed': failed,
        'skipped': skipped,
        'pass_rate': rate,
        'modules': modules,
        'merged_at': datetime.utcnow().isoformat(),
    }


def merge_reports(input_dir: str, output_dir: str):
    print(f"Merging reports from: {input_dir}")
    raw_results = load_all_results(input_dir)
    print(f"  Raw results found: {len(raw_results)}")

    results = deduplicate(raw_results)
    print(f"  After deduplication: {len(results)}")

    summary = compute_summary(results)
    print(f"  Total: {summary['total']} | Passed: {summary['passed']} | "
          f"Failed: {summary['failed']} | Rate: {summary['pass_rate']}%")

    os.makedirs(output_dir, exist_ok=True)

    # Write merged execution-results.json
    results_path = os.path.join(output_dir, 'execution-results.json')
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"  Merged results: {results_path}")

    # Write summary.json
    summary_path = os.path.join(output_dir, 'merge-summary.json')
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    print(f"  Merge summary: {summary_path}")

    # Also write to parent JSON dir for other tools to pick up
    json_dir = os.path.join(os.path.dirname(output_dir), 'JSON')
    os.makedirs(json_dir, exist_ok=True)
    merged_json = os.path.join(json_dir, 'execution-results.json')
    with open(merged_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)

    return results, summary


def main():
    parser = argparse.ArgumentParser(description='Merge test reports from parallel suites')
    parser.add_argument('--input', required=True, help='Directory containing artifact folders')
    parser.add_argument('--output', required=True, help='Output directory for merged results')
    args = parser.parse_args()

    results, summary = merge_reports(args.input, args.output)
    print(f"\n✅ Merge complete: {summary['total']} tests, {summary['pass_rate']}% pass rate")


if __name__ == '__main__':
    main()
