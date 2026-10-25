#!/bin/sh
# Read-only scan on a disposable Linux CI runner, never prints matched secrets.
set -eu
[ "${CI:-}" = true ] || { echo 'Run only on an isolated CI runner.'; exit 1; }
repo=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
work=$(mktemp -d)
trap 'rm -rf -- "$work"' EXIT HUP INT TERM
umask 077
curl --fail --location --silent --show-error \
  https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz \
  --output "$work/tool.tar.gz"
printf '%s  %s\n' 551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb "$work/tool.tar.gz" | sha256sum --check -
tar -xzf "$work/tool.tar.gz" -C "$work" gitleaks
cd "$repo"
git fetch origin '+refs/heads/*:refs/remotes/origin/*' --tags
scan_status=0
"$work/gitleaks" git --log-opts=--all --redact=100 --no-banner \
  --report-format json --report-path "$work/history.json" . || scan_status=$?
"$work/gitleaks" dir --redact=100 --no-banner \
  --report-format json --report-path "$work/current.json" . || scan_status=$?
# Print locations only. Never print Match, Secret, context or the raw report.
# Both scans still run and any failure remains a failure; private reports are
# removed by the existing trap and are never uploaded as artifacts.
python3 - "$work/history.json" "$work/current.json" <<'PY'
import json
import pathlib
import sys

fields = ('Commit', 'File', 'RuleID', 'StartLine', 'Fingerprint')
for name in sys.argv[1:]:
    report = pathlib.Path(name)
    findings = json.loads(report.read_text())
    if not isinstance(findings, list):
        raise SystemExit('Invalid private scanner report; scan not accepted')
    for finding in findings:
        metadata = {field: finding.get(field) for field in fields}
        metadata['scan'] = report.stem
        print('gitleaks-metadata ' + json.dumps(metadata, ensure_ascii=True))
PY
exit "$scan_status"
