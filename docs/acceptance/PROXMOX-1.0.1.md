# Proxmox Linux VM acceptance — partial

24 October 2026. Independent Deployer report, not a production deployment or blanket hardware approval.

- Ubuntu 26.04.1 LTS, amd64; Docker Engine 29.9.2; Compose 5.6.1.
- Public 1.0.1 image, application commit `f245a4ddd8857706f6ded748fb6945ea5aa88a38`.
- Image index `sha256:7e12e1491937c36cec763850b3db1c60916e727bf9bbdb82a4f5447e5812076b`.
- Separate Compose projects and data volumes; temporary credentials, empty bridge registry, no hardware pairing or lamp commands.

## Passed

Public image pull and health, fresh `admin/admin` API login, password change, rejection of the old password, restart/recreation retaining data, internally verified HTTPS and secure session cookie, foreign-origin rejection, enabled control defaults, update from 1.0.0 to 1.0.1, cold backup and restoration into a separate volume, rollback with matching 1.0.0 data, and restart of restored data with 1.0.1. Password/token/registry hashes were preserved through these lifecycle checks.

After a narrowly scoped correction to the test infrastructure, the published HTTPS port was reachable from the client with certificate verification; retained-password API login passed. The test firewall exception is not an end-user installation step.

## Still open

- Real browser login: the HTTPS browser rejected the self-signed test certificate. Verified API login is not browser acceptance.
- Exact simplified Compose file acceptance: the independent Deployer started a separate fresh container from `docker/compose.quickstart.yaml` at PR49 commit `bd8b4d172cafd8db9e602c992ec3e9704a4ce420`; internal health, login, writable volume and control defaults passed. Its published-port/browser check is still pending. Do not substitute the earlier custom lifecycle Compose file for this check.
- Portainer UI flow; VM reboot; real bridge discovery/pairing and Loxone control. The isolated VM cannot reach production LAN devices.
- Recovery of deliberately disabled control flags is not established by the enabled-default tests above.

## Actually executed core commands

```sh
docker compose config --quiet
docker compose up -d --wait
docker compose ps
```

Lifecycle testing also used `docker compose up -d --force-recreate --wait`, a stopped-volume backup and restoration into a separate volume. These commands alone are not a complete backup/restore procedure. The Deployer retains the detailed scripts, hashes and per-step results; no passwords or private keys belong in this report.

This partial record does not open the stable acceptance gate. The exact final file, browser flow and independent documentation review must be accepted separately.
