# Updating Docker and rolling back

[Deutsch](UPDATE-DOCKER.de.md)

For **standard deployments created by the shared installer**, with either local builds or pinned release images. Native deployments use [native maintenance](INSTALL-NATIVE.en.md). Standalone Compose/Portainer stacks using `/data` need their own stack and complete volume backup; the staging tool below does not manage them. RC1 and RC5 remain unchanged. This tool is merged into main from PR #18; [deployment acceptance](DEPLOYMENT-ACCEPTANCE.md) passed, and RC6 uses a fixed version; pulling the same pinned tag is not a version upgrade. Published RC5 images do not acquire PR features. Review release compatibility before changing versions; arbitrary data-schema migrations are not guaranteed.

## Select a reviewed target and stop the existing deployment

Log in with `su -`, then enter the remaining commands in that new root shell. Replace paths. SOURCE is a **separate, reviewed new checkout/archive**, not the installed directory. Record its commit or release version/checksum. Test with empty bridge/Miniserver configuration.

```sh
su -
```

Then:

```sh
set -eu
umask 077
INSTANCE=/opt/hue2lox-test
SOURCE=/home/lance/hue2lox-new
CANDIDATE="${INSTANCE}.update-candidate"
export HUE2LOX_INSTALL_LANG=en
cd "$INSTANCE"
test ! -e "$CANDIDATE"
OLD_CONTAINER=$(docker compose ps -q hue2lox)
test -n "$OLD_CONTAINER"
OLD_IMAGE=$(docker inspect --format '{{.Image}}' "$OLD_CONTAINER")
docker compose down
BACKUP=$(mktemp -d /root/hue2lox-docker-update-XXXXXXXX)
chmod 700 "$BACKUP"
printf '%s\n' "$OLD_IMAGE" > "$BACKUP/image-id.txt"
docker image save --output "$BACKUP/image.tar" "$OLD_IMAGE"
cp -a "$INSTANCE" "$BACKUP/instance"
printf 'Protected backup: %s\n' "$BACKUP"
```

Stop on any error. Pause external restart automation for this deployment. Never use `down -v`, global restarts or pruning. The private backup includes all code, settings, passwords, tokens, certificates and the exact old image. Do not publish it. Downtime starts at `down`.

Custom Compose modifications are refused; manually review/migrate custom mounts, proxy labels and other changes separately. The tool preserves instance identity, endpoint, public URL, feature flags and other `.env` settings. Do not combine this with a network/certificate migration.

## Stage the new deployment: choose exactly one source

**Local build**, including tests of new PR code:

```sh
python3 "$SOURCE/scripts/prepare-docker-update.py" \
  --destination "$INSTANCE" --candidate "$CANDIDATE" --source build
cd "$CANDIDATE"
docker compose config --quiet
docker compose build
```

**Pinned release image**, instead of the preceding block:

```sh
python3 "$SOURCE/scripts/prepare-docker-update.py" \
  --destination "$INSTANCE" --candidate "$CANDIDATE" \
  --source image --registry ghcr
cd "$CANDIDATE"
docker compose config --quiet
docker compose pull hue2lox
```

Use `--registry dockerhub` for Docker Hub. The target version is taken from the reviewed `SOURCE/install/release-image.json`; inspect it first. The candidate `.env` records the exact `HUE2LOX_IMAGE`. No floating `latest` or silent fallback is used. With no newer published version there is no new release image to test: use a local build. CI exercises both registry paths with locally built test images without publishing or changing releases.

Staging does not start containers or modify the original installation. It copies the cold private state with `cp -a`, preserving ownership/modes and existing certificates. Fresh candidate credentials are replaced by the retained private categories.

## Switch back to the original path and verify

```sh
cd /root
PREVIOUS="${INSTANCE}.before-update-$(date +%Y%m%d-%H%M%S)"
test ! -e "$PREVIOUS"
mv "$INSTANCE" "$PREVIOUS"
mv "$CANDIDATE" "$INSTANCE"
cd "$INSTANCE"
docker compose up -d --no-build --pull never --wait --wait-timeout 120
python3 "$SOURCE/scripts/start-install.py" --destination "$INSTANCE"
docker compose ps
```

The startup helper checks the actual HTTP/HTTPS endpoint; HTTPS uses retained certificate trust. For local builds this extra helper call can run a cached build again; use the direct check below instead for fully offline verification. Failure requires investigation/rollback, not a success claim.

For HTTPS, replace the address with the actual existing endpoint:

```sh
curl --noproxy '*' --fail --cacert "$INSTANCE/health-test.crt" \
  https://192.0.2.50:18443/health
```

For HTTP use `http://…/health` without `--cacert`; also check the public HTTPS endpoint/login when using a proxy. Sign in with the previously changed password and confirm the initial password remains rejected. Verify new application code/image identity and retained settings/data, then container and real VM restart. Hardware acceptance is separate.

## Full rollback: old image AND old private data

Set BACKUP to the previously printed backup directory. Later data/password changes are reverted. This also works after preparation/build failure while the original directory is still present.

```sh
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
```

The override forces the exact saved image without rebuilding/downloading, including for local-build installations. Keep both `-f` files for subsequent `up` while operating this restored deployment; ordinary `start-install.py` can build or select the normal image reference again. Repeat direct health verification and login with the **password at backup time**. Retain backups and previous/failed directories until acceptance is complete.

## Acceptance criteria

Demonstrate different target code/image, retained registry/token/password/certificate/public URL/feature flags/owners/modes after update, and exact old image plus old data after rollback. A deliberately broken isolated candidate must fail startup and be recoverable. A version label change alone is not a code migration. These are deployment tests, not a general schema-migration or hardware qualification.

For an actual RC5→RC6 transition and explicit control opt-in, follow the [specific recovery guide](RECOVERY-CONTROL.md).
