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
"$work/gitleaks" git --log-opts=--all --redact=100 --no-banner \
  --report-format json --report-path "$work/history.json" .
"$work/gitleaks" dir --redact=100 --no-banner \
  --report-format json --report-path "$work/current.json" .
