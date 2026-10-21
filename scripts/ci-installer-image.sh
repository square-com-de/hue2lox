#!/bin/sh
# Disposable CI: exercise the installer against an already built release-layout image.
set -eu
[ "${CI:-}" = true ] && [ "$(id -u)" = 0 ] || { echo 'Disposable root CI only'; exit 1; }
repo=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
work=$(mktemp -d /tmp/hue2lox-image-install.XXXXXXXX)
cleanup() {
  for instance in "$work"/dockerhub "$work"/ghcr; do
    if [ -f "$instance/compose.yaml" ]; then
      docker compose --project-directory "$instance" -f "$instance/compose.yaml" down >/dev/null 2>&1 || true
    fi
  done
  rm -rf -- "$work"
}
trap cleanup EXIT HUP INT TERM
# The preceding ci-container.sh builds the exact root Dockerfile used by releases.
# Tag that local image for both installer choices. Do not pull/publish a not-yet-released version.
version=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "$repo/install/release-image.json")
expected=$(docker image inspect hue2lox-default-ci:check --format '{{.Id}}')
for registry in dockerhub ghcr; do
  case "$registry" in
    dockerhub) image="docker.io/dubctrl/hue2lox:$version"; scheme=https; port=18543;;
    ghcr) image="ghcr.io/square-com-de/hue2lox:$version"; scheme=http; port=18544;;
  esac
  docker tag hue2lox-default-ci:check "$image"
  instance="$work/$registry"
  python3 "$repo/scripts/prepare-install.py" --destination "$instance" --host 127.0.0.1 \
    --port "$port" --registry "$registry" --scheme "$scheme"
  if grep -q '    build:' "$instance/compose.yaml"; then echo 'Unexpected build configuration'; exit 1; fi
  python3 "$repo/scripts/start-install.py" --destination "$instance"
  name=$(sed -n 's/^HUE2LOX_CONTAINER_NAME=//p' "$instance/.env")
  [ "$(docker inspect "$name" --format '{{.Image}}')" = "$expected" ]
  python3 "$repo/scripts/check-ci-http.py" "$instance"
  for file in data/admin_auth.json data/registry.json secrets/control_token; do
    (cd "$instance" && sha256sum "$file") >> "$work/$registry.before"
  done
  # Repeated starts reuse the saved image and preserve credentials, token and registry.
  HUE2LOX_INSTALL_COMPACT=1 python3 "$repo/scripts/start-install.py" --destination "$instance"
  (cd "$instance" && sha256sum --check "$work/$registry.before")
  python3 "$repo/scripts/check-ci-http.py" "$instance"
done
echo 'PASS: installer image mode for both registries; HTTPS/HTTP, login, no local build, repeated start and state preservation.'
