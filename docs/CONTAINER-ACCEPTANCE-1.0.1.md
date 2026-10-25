# Container acceptance — 1.0.1

**Follow-up 25.10.2026:** [Fresh OS, disabled-flag recovery and actual Portainer GUI completed](acceptance/FINAL-CONTAINER-2026-10-25.md). The historical scope below is retained; hardware remains separate.

Status: **partial acceptance; no new release or production approval**. Recorded 24 October 2026; coordinated VM reboot verified 25 October 2026 (Europe/Berlin).

## Tested identities

- Ubuntu 26.04.1 LTS, amd64, Docker 29.9.2, Docker Compose 5.6.1, isolated Proxmox VM.
- Published image 1.0.1; application commit `f245a4ddd8857706f6ded748fb6945ea5aa88a38`.
- Multi-platform digest: `sha256:7e12e1491937c36cec763850b3db1c60916e727bf9bbdb82a4f5447e5812076b`.
- Quick-start file: `docker/compose.quickstart.yaml` from commit `bd8b4d172cafd8db9e602c992ec3e9704a4ce420` in PR49. No YAML edits for the test.

## Actual quick-start commands

Docker and Compose were already installed. From a new directory on the isolated test VM:

```sh
curl --fail --location --output compose.yaml https://raw.githubusercontent.com/square-com-de/hue2lox/bd8b4d172cafd8db9e602c992ec3e9704a4ce420/docker/compose.quickstart.yaml
printf 'COMPOSE_PROJECT_NAME=accept-hue2lox-quickstart\nHUE2LOX_HTTP_PORT=18444\n' > .env
docker compose up -d --wait
docker compose ps
```

The project name and alternate free port isolate this test from another acceptance stack. Normal default port: 18443. The application volume was new; the OS was reused after the earlier lifecycle tests. This is not a claim that this final quick-start command was run on a newly reset OS.

## Results

| Check | Result | Evidence type |
|---|---|---|
| Public image pull and container health | PASS | Docker pull and Compose wait output |
| Automatic fresh named volume, writable `/data` | PASS | New volume creation and in-container check |
| `admin/admin`, session, no `HUE_PUBLIC_URL` required | PASS, internal HTTP API | Actual HTTP login/session responses 200 |
| Switching, RGB and white control defaults enabled | PASS | Running service environment |
| Earlier separate stack: password change and old-password rejection | PASS | HTTP API; no real bridge |
| Earlier separate stack: restart and recreation retain data | PASS | Identical password/token/registry hashes |
| Earlier separate stack: verified HTTPS including Secure cookie | PASS, API | Explicit certificate trust; no insecure flag |
| Earlier separate stack: real 1.0.0 → 1.0.1 update, cold backup, restore into new volume with 1.0.0, return to 1.0.1 | PASS | Successful retained-password login and identical data hashes |
| Earlier HTTPS stack: host-published port from VM and external Mac | PASS | Health and authenticated API; certificate verified |
| HTTPS browser login with self-signed certificate | NOT VERIFIED | Browser rejects the untrusted test certificate; warning not bypassed |
| Quick-start external HTTP browser login | PASS | Real browser on another LAN computer: admin/admin, dashboard, reload; changed password after restart |
| Quick-start HTTP cold backup and restore into a second volume | PASS | Retained-password API and real browser login; identical password/token/registry hashes; original volume retained |
| Coordinated VM reboot | PASS | Both stacks automatically healthy; changed passwords accepted, old passwords rejected; password/token/registry hashes match the cold pre-reboot backup; real HTTP browser login repeated |
| Real bridges, discovery and Loxone control | NOT TESTED | Production LAN intentionally blocked |
| Portainer GUI deployment of this exact quick-start file | NOT TESTED | Same Compose format, not an independent GUI acceptance claim |

The test firewall limitation is specific to this intentionally isolated VM. It is not an extra configuration step for normal users, nor evidence that unrestricted network access is safe or required.

## Validation limits and next gate

329 source tests passed across the main run and the four test modules retried with the correct `PYTHONPATH`. The initial restricted run could not bind local test sockets; that is a harness limitation, not a passing app test. Syntax, translation keys, documentation links and diff checks passed. No application code changed for this quick start.

The infrastructure owner added a precise exception for the new isolated test endpoint. The HTTP quick-start browser gate passed without bypassing a browser warning. HTTP is intentional: this template sets no TLS variables, and its URL explicitly uses http://. Password change, old-password rejection, retained-password session, foreign-Origin rejection and HTTP cookie behavior passed. HTTPS browser trust remains separate. Independent documentation review and the final clean-OS scope remain explicit gates. Do not infer hardware support or a production approval from these results.

Existing installations keep their current Compose file and volume mapping. Old volumes, TLS files and backups were preserved. No releases, registry tags or production installations changed during this acceptance.
