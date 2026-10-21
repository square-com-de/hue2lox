#!/bin/sh
# Only a disposable CI runner. The Debian systemd test container has no network.
set -eu
[ "${CI:-}" = true ] || { echo 'Run only on a disposable CI runner.'; exit 1; }
[ "$(id -u)" = 0 ] || { echo 'Run with sudo on the disposable CI runner.'; exit 1; }
os_image=${1:-debian:13}
case "$os_image" in debian:12|debian:13|ubuntu:24.04|ubuntu:26.04) ;; *) echo 'Unsupported test OS image'; exit 1;; esac
repo=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
work=$(mktemp -d /tmp/hue2lox-native-ci.XXXXXXXX)
container="hue2lox-native-ci-$$"
cleanup() { docker rm -f "$container" >/dev/null 2>&1 || true; rm -rf -- "$work"; }
trap cleanup EXIT HUP INT TERM
python3 "$repo/scripts/build-native-package.py" --version 0.0.0-ci.1 --output "$work/packages"
python3 "$repo/scripts/build-native-package.py" --version 0.0.0-ci.2 --output "$work/packages"
# Internet is used only to prepare this generic OS image, before the application runs.
cat > "$work/Dockerfile" <<'EOF'
ARG TEST_OS=debian:13
FROM ${TEST_OS}
ENV container=docker
RUN apt-get update && apt-get install -y --no-install-recommends python3 openssl systemd systemd-sysv ca-certificates passwd util-linux git && rm -rf /var/lib/apt/lists/*
STOPSIGNAL SIGRTMIN+3
CMD ["/sbin/init"]
EOF
docker build --build-arg "TEST_OS=$os_image" --platform linux/amd64 -t hue2lox-native-systemd-ci:check "$work"
docker image inspect hue2lox-native-systemd-ci:check --format 'Test OS image: {{.Id}} {{.Os}}/{{.Architecture}}'
docker run -d --name "$container" --platform linux/amd64 --privileged --cgroupns private \
    --network none --tmpfs /run --tmpfs /run/lock --tmpfs /tmp \
    --mount "type=bind,src=$repo,dst=/source,readonly" \
    --mount "type=bind,src=$work/packages,dst=/packages,readonly" \
    hue2lox-native-systemd-ci:check
# Do not mount the host root, host cgroup filesystem or Docker socket.
ready=false
for attempt in $(seq 1 60); do
    if docker exec "$container" systemctl list-units --no-pager >/dev/null 2>&1; then ready=true; break; fi
    sleep 1
done
[ "$ready" = true ] || { docker logs "$container"; echo 'Real systemd did not start.'; exit 1; }
docker exec "$container" sh -c 'test "$(uname -m)" = x86_64; cat /etc/os-release; python3 --version'
docker exec -e CI=true "$container" python3 /source/scripts/check-native-lifecycle.py
printf '%s\n' 'PASS: isolated Linux amd64 container with real systemd; no external network or hardware.'
