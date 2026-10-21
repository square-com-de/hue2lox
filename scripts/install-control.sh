#!/bin/sh
# Deploy prepared code with lamp control DISABLED. Never sends a Hue PUT.
set -eu
: "${HUE_PUBLIC_URL:?Set HUE_PUBLIC_URL to this installation HTTPS URL}"
[ "$(id -u)" = 0 ] || { echo 'Run as root'; exit 1; }
src=/opt/loxberry/hue2lox-control-staging
dst=/opt/loxberry/hue2lox-prototype
backup=/opt/loxberry/hue2lox-backups/control-$(date +%Y%m%d-%H%M%S)
. "$(dirname -- "$0")/copy-runtime.sh"
copy_runtime
cd "$dst"
docker compose config --quiet
docker compose build
# This CLI entry point only reads status; write_state is not called.
docker compose run --rm --no-deps hue2lox python hue_client.py
docker compose up -d --no-build
i=0
until curl --fail --silent --show-error --max-time 8 --cacert health-test.crt "${HUE_PUBLIC_URL}/health"; do
    i=$((i + 1)); [ "$i" -lt 5 ] || exit 1
    sleep 2
done
printf '\n'
curl --fail --silent --show-error --max-time 8 --cacert health-test.crt "${HUE_PUBLIC_URL}/hue-go/status"
printf '\n'
docker compose ps
docker compose logs --tail=20 hue2lox
printf 'Prepared code installed. Lamp writes remain disabled.\n'
