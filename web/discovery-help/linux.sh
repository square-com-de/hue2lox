#!/bin/bash
# Local mDNS only. No internet service and no device changes.
set -u
command -v avahi-browse >/dev/null || { echo '@@MISSING_AVAHI@@' >&2; exit 1; }
work=$(mktemp -d) || exit 1
child=''
cleanup() {
  if [ -n "$child" ]; then kill "$child" 2>/dev/null || true; wait "$child" 2>/dev/null || true; fi
  rm -rf "$work"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
echo '@@SEARCH@@'
avahi-browse -rpt _hue._tcp > "$work/results" 2> "$work/errors" &
child=$!
sleep 5
kill "$child" 2>/dev/null || true
wait "$child" 2>/dev/null || true
child=''
# Avahi uses decimal escapes (e.g. \\032), not shell/octal escapes.
awk -F ';' '$1 == "=" && $3 == "IPv4" && $8 ~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/ {
  name=$4; decoded=""
  while (length(name)) {
    if (substr(name,1,1)=="\\" && substr(name,2,3) ~ /^[0-9][0-9][0-9]$/) {
      code=substr(name,2,3)+0
      decoded=decoded ((code>=32 && code!=127) ? sprintf("%c",code) : "?")
      name=substr(name,5)
    } else { decoded=decoded substr(name,1,1); name=substr(name,2) }
  }
  printf "%-36s %s\n", decoded, $8
}' "$work/results" | sort -u > "$work/bridges"
printf '\n%-36s %s\n' 'BRIDGE' 'IPv4'
if [ -s "$work/bridges" ]; then cat "$work/bridges"; else
  echo '@@NONE@@'
  if [ -s "$work/errors" ]; then cat "$work/errors" >&2; echo '@@AVAHI_SERVICE@@' >&2; fi
fi
