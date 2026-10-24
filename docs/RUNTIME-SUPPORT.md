# Runtime and version status

[Deutsch](RUNTIME-SUPPORT.de.md) · [Installation](../INSTALL.md) · [Lessons learned](LESSONS-LEARNED.md)

As of 24 October 2026: published **1.0.1**, commit `f245a4ddd8857706f6ded748fb6945ea5aa88a38`. Image startup, working login, lifecycle acceptance and observed lamp effects are different evidence scopes.

| Path | Observed scope | Limit |
|---|---|---|
| Linux Docker Engine + Compose plugin (`docker compose`) | [Release CI](https://github.com/square-com-de/hue2lox/actions/runs/40100051393): fresh startup, HTTPS/login, installer/ZIP, image update and exact rollback; AMD64/ARM64 builds, boot and anonymous pulls | Not every Docker/Compose version. Historical VM reports did not record exact Engine/Compose versions publicly; the Deployer must add them before the next approval. Compose must support the update guide's `--wait`/`--wait-timeout`. |
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

## Before the next stable approval

Open: independent acceptance of these consolidated guides; exact Docker/Compose versions and actually executed copy/paste commands; recovery retaining passwords and deliberately disabled flags. Record hardware scope explicitly; mocks establish no new lamp/Miniserver acceptance. The maintainer opens the [technical stable gate](GHCR-RELEASE.md#stable-acceptance-gate) only using that evidence. Published 1.0.0/1.0.1 are not rewritten.

**Current additional acceptance:** test Docker Compose as the preferred end-user path in a fresh Proxmox Linux VM. Record Docker/Compose versions, immutable image identity, actual installation/start commands, initial login, browser URL, volume, TLS, network limits, recreate, backup/restore and rollback. This new acceptance is pending; do not invent tested commands or port/IP values. Owner: Deployer, handoff through the PM.
