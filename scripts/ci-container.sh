#!/bin/sh
# Disposable Linux CI only: never touches an installed instance or a Hue bridge.
set -eu
[ "${CI:-}" = "true" ] || { echo 'Run only on a disposable CI runner.'; exit 1; }
[ "$(id -u)" = 0 ] || { echo 'Run with sudo on the disposable CI runner.'; exit 1; }
repo=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
# Resolve every source override against the repository, even from another cwd.
(cd /tmp && docker compose --project-directory "$repo" -f "$repo/compose.yaml" \
    -f "$repo/docker/compose.control.yaml" -f "$repo/docker/compose.color.yaml" \
    -f "$repo/docker/compose.white.yaml" config --quiet)
# Also exercise the conventional docker build entry point, without device access.
base_image=$(sed -n 's/^FROM //p' "$repo/Dockerfile")
docker pull "$base_image"
docker build -t hue2lox-default-ci:check -f "$repo/Dockerfile" "$repo"
docker run --rm --entrypoint python hue2lox-default-ci:check -c 'import app,json; assert json.load(open("/app/config/registry.json")) == {"schema_version":1,"bridges":[]}'
docker image inspect "$base_image" --format 'Base: {{json .RepoDigests}} {{.Os}}/{{.Architecture}}'
test_root=$(mktemp -d /tmp/hue2lox-ci.XXXXXXXX)
project="hue2lox-ci-$$"
compose() { docker compose --project-directory "$test_root/instance" -p "$project" -f "$test_root/instance/compose.yaml" -f "$test_root/image.yaml" "$@"; }
cleanup() { compose down --remove-orphans >/dev/null 2>&1 || true; rm -rf -- "$test_root"; }
trap cleanup EXIT HUP INT TERM
python3 "$repo/scripts/prepare-install.py" --destination "$test_root/instance" --host 127.0.0.1 --port 18443
printf 'services:\n  hue2lox:\n    image: hue2lox-ci:check\n' > "$test_root/image.yaml"
compose config --quiet
compose up -d --build --wait --wait-timeout 120
docker image inspect hue2lox-ci:check --format 'Built image: {{.Id}} {{.Os}}/{{.Architecture}}'
[ "$(compose exec -T hue2lox id -u)" = 10001 ]
compose exec -T hue2lox python -c 'import os; assert not os.access("/app/src", os.W_OK)'
python3 "$repo/scripts/check-ci-http.py" "$test_root/instance"
compose restart
compose up -d --wait --wait-timeout 120
python3 "$repo/scripts/check-ci-http.py" "$test_root/instance"
# Package tooling and all of its bundled dependencies must be absent.
compose exec -T hue2lox python -c 'import importlib.util, importlib.metadata; assert importlib.util.find_spec("pip") is None; assert importlib.util.find_spec("ensurepip") is None; assert list(importlib.metadata.distributions()) == []'
# Offline maintenance and restore on this disposable, bridge-free installation.
compose down
cp -a "$test_root/instance" "$test_root/backup"
python3 "$repo/scripts/renew-certificate.py" --destination "$test_root/instance"
compose up -d --wait --wait-timeout 120
python3 "$repo/scripts/check-ci-http.py" "$test_root/instance"
compose down
python3 "$repo/scripts/renew-certificate.py" --destination "$test_root/instance" --host 127.0.0.2
compose up -d --wait --wait-timeout 120
python3 "$repo/scripts/check-ci-http.py" "$test_root/instance"
compose down
# State and identity must survive both renewals byte-for-byte.
for file in data/registry.json data/admin_auth.json secrets/control_token; do
    cmp "$test_root/backup/$file" "$test_root/instance/$file"
done
rm -rf -- "$test_root/instance"
cp -a "$test_root/backup" "$test_root/instance"
compose up -d --wait --wait-timeout 120
python3 "$repo/scripts/check-ci-http.py" "$test_root/instance"
echo 'PASS: certificate renewal, changed bind IP and complete offline restore; state preserved.'
echo 'PASS: fresh Docker build, health, non-root user, read-only application, HTTPS, login and restart.'

# Prepare a separate HTTP backend without certificate files or TLS variables.
compose down
python3 "$repo/scripts/prepare-install.py" --destination "$test_root/http" --host 127.0.0.1 --port 18444 --scheme http --public-url https://hue.example.org
# Reuse the tested image through the generated HTTP Compose file.
http_compose() { docker compose --project-directory "$test_root/http" -p "$project-http" -f "$test_root/http/compose.yaml" -f "$test_root/image.yaml" "$@"; }
trap 'http_compose down --remove-orphans >/dev/null 2>&1 || true; cleanup' EXIT HUP INT TERM
http_compose config --quiet
http_compose up -d --no-build --wait --wait-timeout 120
python3 "$repo/scripts/check-ci-http.py" "$test_root/http"
http_compose restart
http_compose up -d --no-build --wait --wait-timeout 120
python3 "$repo/scripts/check-ci-http.py" "$test_root/http"
