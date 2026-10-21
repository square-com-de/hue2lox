#!/bin/sh
# Run as root; updates only the existing Hue2Lox prototype.
set -eu
: "${HUE_PUBLIC_URL:?Set HUE_PUBLIC_URL to this installation HTTPS URL}"
[ "$(id -u)" = 0 ] || { echo 'Run as root'; exit 1; }
src=/opt/loxberry/hue2lox-status-staging
dst=/opt/loxberry/hue2lox-prototype
backup=/opt/loxberry/hue2lox-backups/$(date +%Y%m%d-%H%M%S)
. "$(dirname -- "$0")/copy-runtime.sh"
copy_runtime
install -d -m 700 -o 10001 -g 10001 "$dst/secrets"
if [ ! -f "$dst/secrets/hue_key" ]; then
    install -m 400 -o 10001 -g 10001 "$src/secrets/hue_key" "$dst/secrets/hue_key"
fi
cd "$dst"
docker compose config --quiet
docker compose build
# Validate actual container runtime, TLS and key before replacing running service.
docker compose run --rm --no-deps hue2lox python hue_client.py
docker compose up -d --no-build
# Allow startup, then check both HTTPS endpoints using existing trusted cert.
i=0
until curl --fail --silent --show-error --max-time 8 --cacert health-test.crt "${HUE_PUBLIC_URL}/hue-go/status"; do
    i=$((i + 1)); [ "$i" -lt 5 ] || exit 1
    sleep 2
done
printf '\n'
curl --fail --silent --show-error --max-time 8 --cacert health-test.crt "${HUE_PUBLIC_URL}/health"
printf '\n'
docker compose ps
docker compose logs --tail=20 hue2lox
