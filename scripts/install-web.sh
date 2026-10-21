#!/bin/sh
# Installs admin UI, preserving overrides, registry and control/bridge secrets.
set -eu
: "${HUE_PUBLIC_URL:?Set HUE_PUBLIC_URL to this installation HTTPS URL}"
[ "$(id -u)" = 0 ] || { echo 'Run as root'; exit 1; }
reset_admin=0
case "${1:-}" in
    '') ;;
    --reset-admin) reset_admin=1 ;;
    *) echo 'Usage: install-web.sh [--reset-admin]'; exit 1 ;;
esac
src=/opt/loxberry/hue2lox-web-staging
dst=/opt/loxberry/hue2lox-prototype
backup=/opt/loxberry/hue2lox-backups/web-$(date +%Y%m%d-%H%M%S)
. "$(dirname -- "$0")/copy-runtime.sh"
copy_runtime
# Persistent state; preserve existing runtime registry and newly paired keys.
install -d -m 700 -o 10001 -g 10001 "$dst/data"
if [ ! -f "$dst/data/registry.json" ]; then
    install -m 600 -o 10001 -g 10001 "$dst/config/registry.json" "$dst/data/registry.json"
fi
# Migrate a previous administrator once; never reset a changed password on update.
if [ "$reset_admin" = 1 ]; then
    python3 "$src/src/admin_auth.py" "$dst/data/admin_auth.json" --username admin --default
elif [ ! -f "$dst/data/admin_auth.json" ]; then
    if [ -f "$dst/secrets/admin_auth.json" ]; then
        install -m 600 -o 10001 -g 10001 "$dst/secrets/admin_auth.json" "$dst/data/admin_auth.json"
    else
        python3 "$src/src/admin_auth.py" "$dst/data/admin_auth.json" --username admin --default
    fi
fi
chown 10001:10001 "$dst/data/admin_auth.json"
chmod 600 "$dst/data/admin_auth.json"
# The rollback copy contains metadata/path references only, never bridge-key contents.
cp -p "$dst/data/registry.json" "$backup/runtime-registry.json"
install -d -m 755 "$dst/web"
# Remove only the retired icon assets before building the updated image.
rm -f "$dst/web/hue-icons.js" "$dst/web/hue-icons-license.txt"
install -d -m 755 "$dst/web/lamp-icons"
for f in "$src"/web/lamp-icons/*.svg; do install -m 644 "$f" "$dst/web/lamp-icons/"; done
for f in licenses.html tutorial-en.html i18n.js tutorial.html tutorial.css tutorial-config.png tutorial-commands.png tutorial-monitor.png index.html app.css app.js admin.js bridges.js scenes.js discovery.js monitor.js octopus.png hue2lox-logo.png lamp-icons.js; do install -m 644 "$src/web/$f" "$dst/web/$f"; done
install -d -m 755 "$dst/web/locales"
for f in de.js en.js de.json en.json; do install -m 644 "$src/web/locales/$f" "$dst/web/locales/$f"; done
cd "$dst"
install -d -m 755 "$dst/catalog"
install -m 644 "$src/catalog/"* "$dst/catalog/"
docker compose config --quiet
docker compose build
if ! docker compose run --rm --no-deps hue2lox python hue_client.py; then
    printf 'Hinweis: Hue-Status derzeit nicht erreichbar; Web-Verwaltung wird trotzdem aktualisiert.\n'
fi
docker compose up -d --no-build --force-recreate
i=0
until curl --fail --silent --show-error --max-time 8 --cacert health-test.crt "${HUE_PUBLIC_URL}/health"; do
    i=$((i + 1)); [ "$i" -lt 8 ] || exit 1
    sleep 2
done
printf '\n'
code=$(curl --silent --show-error --output /dev/null --write-out '%{http_code}' --max-time 12 --cacert health-test.crt "${HUE_PUBLIC_URL}/api/admin/lights")
[ "$code" = 401 ] || { printf 'Expected protected admin endpoint (401), got %s\n' "$code"; exit 1; }
printf 'Admin API requires login (401).\n'
printf '\n'
docker compose ps
printf 'Admin UI (Benutzer: admin): %s/\n' "$HUE_PUBLIC_URL"
