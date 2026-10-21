#!/bin/sh
# Prepare new runtime with color commands still disabled. Never sends a PUT.
set -eu
: "${HUE_PUBLIC_URL:?Set HUE_PUBLIC_URL to this installation HTTPS URL}"
[ "$(id -u)" = 0 ] || { echo 'Run as root'; exit 1; }
src=/opt/loxberry/hue2lox-color-staging
dst=/opt/loxberry/hue2lox-prototype
backup=/opt/loxberry/hue2lox-backups/color-$(date +%Y%m%d-%H%M%S)
. "$(dirname -- "$0")/copy-runtime.sh"
copy_runtime
# Preserve existing on/off/dimming activation and token. Do not change override.
cd "$dst"
docker compose config --format json | python3 -c 'import json,sys; d=json.load(sys.stdin); assert str(d["services"]["hue2lox"]["environment"].get("HUE_COLOR_ENABLED")) == "0", "Color must stay disabled"'
docker compose build
docker compose run --rm --no-deps hue2lox python hue_client.py
docker compose up -d --no-build
i=0
until curl --fail --silent --show-error --max-time 8 --cacert health-test.crt "${HUE_PUBLIC_URL}/health"; do
    i=$((i + 1)); [ "$i" -lt 8 ] || exit 1
    sleep 2
done
printf '\n'
curl --fail --silent --show-error --max-time 8 --cacert health-test.crt "${HUE_PUBLIC_URL}/hue-go/status"
printf '\n'
docker compose ps
printf 'Prepared color code installed; color control remains disabled. No Hue PUT sent by this script.\n'
