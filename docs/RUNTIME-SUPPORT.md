# Runtime and version status

[Deutsch](RUNTIME-SUPPORT.de.md) · [Installation](../INSTALL.md) · [Lessons learned](LESSONS-LEARNED.md)

As of 24 October 2026: published **1.0.1**, commit `f245a4ddd8857706f6ded748fb6945ea5aa88a38`. Image startup, working login, lifecycle acceptance and observed lamp effects are different evidence scopes.

| Path | Observed scope | Limit |
|---|---|---|
| Linux Docker Engine + Compose plugin (`docker compose`) | [Release CI](https://github.com/square-com-de/hue2lox/actions/runs/40100051393): fresh startup, HTTPS/login, installer/ZIP, image update and exact rollback; AMD64/ARM64 builds, boot and anonymous pulls | Not every Docker/Compose version. The new partial Proxmox acceptance below records Docker29.9.2/Compose5.6.1; historical reports for other versions do not establish that binding. Compose must support the update guide's `--wait`/`--wait-timeout`. |
| Portainer CE **2.45.3 LTS**, Linux Docker Standalone | Actual GUI: web editor/deploy, automatic volume, browser login, restart/recreate retaining credentials/state. [Evidence](acceptance/FINAL-CONTAINER-2026-10-25.md) | Ubuntu26.04.1 amd64/Docker29.9.2; not Swarm, rootless or every version. |
| Podman Desktop **1.30.5, macOS ARM64** | Public 1.0.1 ARM64 image: actual GUI pull, **Run Image → Create and start**, fresh data, browser `admin/admin`, reload and GUI restart/relogin; an additional named-volume CLI check passed on macOS 27.0.1, client/VM engine **6.1.4**. [Acceptance](acceptance/DESKTOP-1.0.1.md) | Local desktop flow only. No certification of `podman compose`, the Docker installer under Podman, Windows/Linux Podman or LAN multicast. A CLI version alone does not establish this GUI flow. |
| Native systemd, **amd64**, experimental | CI: isolated Debian **12/13**, Ubuntu **24.04/26.04** lifecycles. Earlier real VMs: Ubuntu **26.04**, DietPi **13** at the [recorded commit](DEPLOYMENT-ACCEPTANCE.md) | Historical acceptance does not apply retroactively to each new archive. Native ARM/physical Raspberry Pi acceptance is missing. Python **3.11+** per the [native guide](INSTALL-NATIVE.en.md), not blanket OS-derivative support. |
| LoxBerry | Existing Linux/Docker deployment on a specific LoxBerry VM was operated separately | **No dedicated LoxBerry plugin or plugin ZIP.** A native foundation is not plugin acceptance. |
| Unraid/Synology, Docker Desktop on Mac/Windows, other derivatives | Container/Compose examples are integration guidance | Linux CI and a Mac Podman test do not certify all platforms. Separate acceptance is needed. |

Installer distribution detection is not hardware acceptance. The [installation matrix](../INSTALL.md) lists recognized OS versions; this table limits the evidenced paths. An amd64 image is not an ARM image; a 64-bit CPU with a 32-bit OS is insufficient.

## Choose the correct entry point

- Linux: [versioned source ZIP and guided installer](../INSTALL.md), or the [fixed Compose file](DOCKER.md#docker-compose). Do not run the Docker installer through a Podman alias.
- Accepted Mac desktop flow: [four GUI steps](DOCKER.md#podman-desktop-on-macos). Direct localhost/private-IP access in 1.0.1 needs no additional browser URL. Custom DNS/reverse proxies need a matching `HUE_PUBLIC_URL`.
- Native: [separate archive](INSTALL-NATIVE.en.md) matching the source ZIP's version/commit; container settings are not systemd settings.

## Updating is not restarting

A new image version requires a **recreated container**, as do changed environment variables. Pull only downloads; restart reuses the old container image/environment. First back up data, secrets, certificates, Compose/env and the exact old image. Use [Docker update/rollback](UPDATE-DOCKER.md) or [native maintenance](INSTALL-NATIVE.en.md); handle custom Portainer/Compose stacks separately. Never delete the only data copy using `down -v` or pruning.

Fresh data uses `admin/admin`. Retained data keeps its existing password, bridge keys and intentionally disabled controls. For RC5 state, [targeted recovery](RECOVERY-CONTROL.md) explains why ordinary updates do not silently change `0` to `1`. Token and lamp capability checks still apply.

Pin `1.0.1` instead of `latest`, or use its published digest. The [digest record](https://github.com/square-com-de/hue2lox/releases/download/v1.0.1/container-digests.json) binds platform and commit. Historical releases remain unchanged.

## New partial Proxmox acceptance

Ubuntu **26.04.1 amd64**, Docker **29.9.2**, Compose **5.6.1**: image/API login, persistence, update and restore/rollback passed. The exact quick-start file now also passed on a new OS with empty Docker; disabled-flag recovery and actual Portainer GUI passed. Real hardware remains separate. [Final evidence](acceptance/FINAL-CONTAINER-2026-10-25.md). [Evidence and limits](acceptance/PROXMOX-1.0.1.md). Runtime versions are now recorded for this new partial acceptance.

## Before the next stable approval

The additional clean-OS, disabled-flag recovery and Portainer checks passed. Separate hardware acceptance, final version-bound release decision for a new candidate remain open. The new records passed a separate read-only review. Runtime versions, executed commands and retained-password checks are recorded in the new Deployer report. Record hardware scope explicitly; mocks establish no new lamp/Miniserver acceptance. The maintainer opens the [technical stable gate](GHCR-RELEASE.md#stable-acceptance-gate) only using that evidence. Published 1.0.0/1.0.1 are not rewritten.

**Additional acceptance:** The [partial Proxmox report](CONTAINER-ACCEPTANCE-1.0.1.md) now records runtime versions, the unchanged quick-start file, browser and lifecycle evidence. The [final acceptance](acceptance/FINAL-CONTAINER-2026-10-25.md) closes clean-OS, flags and Portainer for the stated1.0.1 identity; other platform and hardware limits remain explicit. Owner of this final acceptance: Engineer; coordination through the PM.
