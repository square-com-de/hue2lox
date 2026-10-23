# RC5 → RC6: update and explicit control opt-in

[Deutsch](RECOVERY-CONTROL.de.md)

**RC6 is unpublished.** This guide is for isolated acceptance using the supplied local RC6 archives; do not pull unavailable RC6 registry images. Production and hardware remain untouched.

The RC5 Docker installer stored `HUE_WRITES_ENABLED`, `HUE_COLOR_ENABLED` and `HUE_WHITE_ENABLED` as `0`. The direct RC5 image without these overrides defaults to `1`. RC6 sets all three to `1` for **fresh installations only**. Updates preserve existing values, including intentionally disabled `0` values. Correction therefore requires an explicit operator decision. `1` only permits switching/dimming/RGB/TW/Lumitech features supported by each light; bearer-token and capability checks remain enforced. No pairing, credential or saved light-mode reset is needed.

## 1. Back up and stage a standard Docker installation

For an unmodified RC5 installer deployment with `compose.yaml`, `.env`, `data/`, `certs/`, `secrets/` in its installation directory. Custom Compose/Portainer stacks, extra overrides or external volumes require separate review; this guide does not qualify them. Pause external restart automation. Never use `down -v`, pruning or global restarts.

First verify the new source ZIP against the **separately supplied** SHA256 and extract it outside the installation. Set `INSTANCE` to the existing installation and `SOURCE` to that new source directory. Run every following section in the same root shell; after interruption, restore variables from recorded paths. Record `BACKUP` securely. `set -e` exits the root shell on errors; do not blindly continue.

```sh
su -
```

Enter the following only after the password prompt and the new root shell appear:

```sh
set -eu
umask 077
INSTANCE=/opt/hue2lox
SOURCE=/home/lance/hue2lox-v1.0.0-rc.6
CANDIDATE="${INSTANCE}.rc6"
PREVIOUS="${INSTANCE}.before-rc6"
export HUE2LOX_INSTALL_LANG=en
test -d "$INSTANCE"
test -d "$SOURCE"
test ! -e "$CANDIDATE"
test ! -e "$PREVIOUS"
test -z "${COMPOSE_FILE:-}"
for name in compose.override.yaml compose.override.yml docker-compose.override.yaml docker-compose.override.yml; do
  test ! -e "$INSTANCE/$name"
done
python3 "$SOURCE/scripts/recover-control-flags.py" --settings "$INSTANCE/.env" --check
cd "$INSTANCE"
OLD_CONTAINER=$(docker compose ps -q hue2lox)
test -n "$OLD_CONTAINER"
OLD_IMAGE=$(docker inspect --format '{{.Image}}' "$OLD_CONTAINER")
BACKUP=$(mktemp -d /root/hue2lox-rc5-before-rc6-XXXXXXXX)
chmod 700 "$BACKUP"
printf '%s\n' "$OLD_IMAGE" > "$BACKUP/image-id.txt"
docker image save --output "$BACKUP/image.tar" "$OLD_IMAGE"
printf 'Protected backup: %s\n' "$BACKUP"
docker compose down
cp -a "$INSTANCE" "$BACKUP/instance"
(cd "$INSTANCE" && find data secrets -type f -exec sha256sum {} + && if test -d certs; then find certs -type f -exec sha256sum {} +; fi) > "$BACKUP/private-before.sha256"
python3 "$SOURCE/scripts/prepare-docker-update.py" \
  --destination "$INSTANCE" --candidate "$CANDIDATE" --source build
```

Downtime starts at `down`. The full cold backup contains code, settings, password hash, tokens, certificates and registry, plus the exact old image. Keep it private; never publish backups or file-hash lists. Staging creates a sibling of the old installation. If the build fails, use section 4 to start the old installation from its backup.

## 2. Decide explicitly and recreate the container

`yes` enables the three flags only in the new candidate. `no` preserves every value; old `0` values continue to disable the corresponding controls. An answer is required. The helper prints only the three flags and a private backup path, never secrets. It refuses ambiguous/customized files instead of overwriting them.

```sh
printf 'Explicitly enable supported control? [yes/no]: '
read -r ENABLE_CONTROL
case "$ENABLE_CONTROL" in
  yes) python3 "$SOURCE/scripts/recover-control-flags.py" \
         --settings "$CANDIDATE/.env" --enable-supported-control ;;
  no) python3 "$SOURCE/scripts/recover-control-flags.py" \
        --settings "$CANDIDATE/.env" --check ;;
  *) echo 'Stopped: yes or no required.'; exit 1 ;;
esac
(cd "$CANDIDATE" && docker compose config --quiet && docker compose build)
cd /root
mv "$INSTANCE" "$PREVIOUS"
mv "$CANDIDATE" "$INSTANCE"
cd "$INSTANCE"
docker compose up -d --no-build --pull never --wait --wait-timeout 120
sha256sum --check "$BACKUP/private-before.sha256"
NEW_CONTAINER=$(docker compose ps -q hue2lox)
NEW_IMAGE=$(docker inspect --format '{{.Image}}' "$NEW_CONTAINER")
test "$NEW_IMAGE" != "$OLD_IMAGE"
python3 "$SOURCE/scripts/recover-control-flags.py" --settings "$INSTANCE/.env" --check
```

**`docker compose restart` is insufficient:** changed environment settings require container recreation. No re-pairing or new token. Before publication, RC6 is built from the new local source; the [pinned-image update path](UPDATE-DOCKER.md) is separately available after publication.

## 3. Verify the actual application and retained state

The example assumes the existing HTTPS endpoint was already `127.0.0.1:18443`. Replace it with the **actual previous endpoint**; for HTTP omit `--cacert`. Do not combine this update with a network/certificate migration. The second check compares a real RC6 file absent from RC5; a version-label change alone is not a code update.

```sh
curl --noproxy '*' --fail --cacert "$INSTANCE/health-test.crt" \
  https://127.0.0.1:18443/health
curl --noproxy '*' --fail --cacert "$INSTANCE/health-test.crt" \
  https://127.0.0.1:18443/assets/sidebar-icons.svg --output /root/rc6-sidebar-icons.svg
cmp "$SOURCE/web/sidebar-icons.svg" /root/rc6-sidebar-icons.svg
```

Sign in through the browser with the previously changed password; the initial `admin` password must still be rejected. Inspect discovery help and new icons. Compare registry, tokens, certificates, owners and modes with the cold backup without printing their contents. Private-file hashes must match; `.env` may differ only in selected deployment source and explicitly enabled flags. Repeat HTTPS/login after container and VM restart. Test without paired hardware; control/token/capability checks use isolated fixtures only. Real Hue/Loxone acceptance remains open.

## 4. Exact rollback: old image AND old state

`BACKUP` must point to the path printed earlier. Password/data changes since the backup are reverted. This also applies after preparation/build failures while `INSTANCE` is unchanged. Retain the failed RC6 directory.

```sh
# BACKUP=/root/hue2lox-rc5-before-rc6-EXACT_PRINTED_SUFFIX
cd "$INSTANCE"
docker compose down
cd /root
FAILED="${INSTANCE}.before-rollback-$(date +%Y%m%d-%H%M%S)"
test ! -e "$FAILED"
mv "$INSTANCE" "$FAILED"
cp -a "$BACKUP/instance" "$INSTANCE"
docker image load --input "$BACKUP/image.tar"
OLD_IMAGE=$(cat "$BACKUP/image-id.txt")
docker image inspect "$OLD_IMAGE" >/dev/null
printf 'services:\n  hue2lox:\n    image: "%s"\n' "$OLD_IMAGE" > "$BACKUP/rollback-image.yaml"
cd "$INSTANCE"
docker compose -f compose.yaml -f "$BACKUP/rollback-image.yaml" \
  up -d --no-build --pull never --wait --wait-timeout 120
RESTORED_CONTAINER=$(docker compose ps -q hue2lox)
test "$(docker inspect --format '{{.Image}}' "$RESTORED_CONTAINER")" = "$OLD_IMAGE"
sha256sum --check "$BACKUP/private-before.sha256"
cmp "$BACKUP/instance/.env" "$INSTANCE/.env"
```

Repeat direct health verification and login with the **password at backup time**. Keep both `-f` files for subsequent `up` commands; the normal startup helper may otherwise build/select another image. Retain the backup and previous/failed directories until full acceptance.

## 5. Native development installation: separate path

RC5 had **no native release package**. This path only covers previously recorded experimental native deployments, not a “native RC5 migration”. Verify source ZIP and RC6 native archive against their separately supplied SHA256 values. In a root shell:

```sh
python3 "$SOURCE/scripts/recover-control-flags.py" --settings /etc/hue2lox/settings.env --check
sh "$SOURCE/deployment/native/update.sh" \
  --package /home/lance/hue2lox-1.0.0-rc.6-native.tar.gz \
  --sha256 "$VERIFIED_NATIVE_SHA256"
```

First set `VERIFIED_NATIVE_SHA256` to the independently supplied hash. Record the protected backup path under `/var/backups/hue2lox/` **printed by the updater**. The updater preserves existing flags. Only if explicitly opting into control, run this block (otherwise skip it):

```sh
systemctl stop hue2lox
python3 "$SOURCE/scripts/recover-control-flags.py" \
  --settings /etc/hue2lox/settings.env --enable-supported-control
systemctl restart hue2lox
python3 "$SOURCE/scripts/native-assistant.py" health
```

Stop on failure. Roll back using the exact recorded backup path, then verify health and the previous login:

```sh
sh "$SOURCE/deployment/native/rollback.sh" --backup /var/backups/hue2lox/EXACT_PRINTED_BACKUP
python3 "$SOURCE/scripts/native-assistant.py" health
```

Native rollback restores code **and** the private state including old flags. No arbitrary schema migration or native ARM qualification is implied.
