#!/bin/bash
# Local mDNS discovery only; no internet service, no device changes.
set -u
command -v dns-sd >/dev/null || { echo '@@MISSING_DNSSD@@' >&2; exit 1; }
work=$(mktemp -d) || exit 1
child=''
cleanup() {
  if [ -n "$child" ]; then kill "$child" 2>/dev/null || true; wait "$child" 2>/dev/null || true; fi
  rm -rf "$work"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
capture() {
  local output=$1
  shift
  dns-sd "$@" > "$output" 2>&1 &
  child=$!
  sleep 3
  kill "$child" 2>/dev/null || true
  wait "$child" 2>/dev/null || true
  child=''
}
no_ipv4='@@NO_IPV4@@'
echo '@@SEARCH_MAC@@'
capture "$work/browse" -B _hue._tcp local.
awk '$2 == "Add" { sub(/^.*_hue\._tcp\.[[:space:]]+/, ""); print }' "$work/browse" | sort -u > "$work/names"
if [ ! -s "$work/names" ]; then
  echo '@@NONE@@'
  exit 0
fi
printf '\n%-36s %s\n' 'BRIDGE' 'IPv4'
while IFS= read -r name; do
  capture "$work/lookup" -L "$name" _hue._tcp local.
  host=$(sed -n 's/.*can be reached at \([^: ]*\):.*/\1/p' "$work/lookup" | head -n 1)
  if [ -z "$host" ]; then printf '%-36s %s\n' "$name" '@@NO_HOST@@'; continue; fi
  capture "$work/address" -G v4 "$host"
  ips=$(awk '$2 == "Add" && $6 ~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/ {print $6}' "$work/address" | sort -u | paste -sd ',' -)
  printf '%-36s %s\n' "$name" "${ips:-$no_ipv4}"
done < "$work/names"
