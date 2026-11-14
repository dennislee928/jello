#!/usr/bin/env python3
"""Run independent security checks; missing tools and errors fail closed."""
import argparse
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', help='Optional container reference, preferably pinned by digest')
    args = parser.parse_args()
    out = ROOT / 'reports/security'
    out.mkdir(parents=True, exist_ok=True)
    # Never inherit a GitHub token into scanners or regression tests.
    env = {k: v for k, v in os.environ.items() if k not in ('GH_TOKEN', 'GITHUB_TOKEN')}
    trivy = ['docker', 'run', '--rm', '-v', f'{ROOT}:/src:ro', '-w', '/src',
             'aquasec/trivy:0.76.2@sha256:8f6bb947dbc528902e11f2f5be52f7b519f6a39d5d148f41166f2040499768fb']
    common = ['--skip-dirs', '.git', '--skip-dirs', 'reports/security', '--skip-dirs', '.venv']
    jobs = [
        ('sast', [sys.executable, '-m', 'bandit', '-r', 'scripts', '-f', 'json', '-ll']),
        ('sca-secrets-config', trivy + ['fs', '--scanners', 'vuln,secret,misconfig',
          '--severity', 'HIGH,CRITICAL', '--exit-code', '1', '--format', 'json'] + common + ['.']),
        ('sbom', trivy + ['fs', '--format', 'cyclonedx'] + common + ['.']),
        ('runtime-regression', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v']),
    ]
    if args.image:
        if args.image.startswith('-'):
            parser.error('image must not start with a dash')
        jobs.append(('image', trivy + ['image', '--scanners', 'vuln,secret', '--severity',
                    'HIGH,CRITICAL', '--exit-code', '1', '--format', 'json', args.image]))
    results = []
    for name, command in jobs:
        with (out / f'{name}.json' if name != 'runtime-regression' else out / f'{name}.log').open('w') as stdout, (out / f'{name}.stderr.log').open('w') as stderr:
            try:
                proc = subprocess.run(command, cwd=ROOT, env=env, stdout=stdout,
                                      stderr=stderr, timeout=900, check=False)
                code = proc.returncode
            except (OSError, subprocess.TimeoutExpired) as exc:
                stderr.write(str(exc))
                code = 2
        results.append({'check': name, 'status': 'PASS' if code == 0 else 'FAIL_OR_ERROR', 'exit_code': code})
    results.extend({'check': name, 'status': 'NOT_APPLICABLE', 'reason': reason} for name, reason in [
        ('dast/iast', 'No running application or instrumentation target in this repository.'),
        *([] if args.image else [('image', 'No image supplied; use --image registry/name@sha256:...')]),
    ])
    report = {'verified_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'results': results}
    (out / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')
    summary = '# CI-SEC\n\n' + '\n'.join(f"- {r['check']}: {r['status']}" for r in results) + '\n'
    (out / 'summary.md').write_text(summary)
    print(summary)
    return int(any(r['status'] == 'FAIL_OR_ERROR' for r in results))


if __name__ == '__main__':
    raise SystemExit(main())
