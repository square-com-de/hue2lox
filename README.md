> **1.0.3 in Vorbereitung / preparation only:** Noch nicht veröffentlicht. Download-/Image-Befehle für 1.0.3 erst nach erfolgreicher Veröffentlichung verwenden. / Not published; use 1.0.3 download/image commands only after successful publication. [Aktuell veröffentlicht / currently published: 1.0.2](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.2).

<p align="center"><a href="README.de.md">Deutsch</a> | <a href="README.md">English</a></p>

<p align="center">
  <img src="web/hue2lox-logo.png" width="360" alt="Hue2Lox – our octopus holding the wordmark">
</p>
<h1 align="center">Get a grip on Hue. With Hue2Lox.</h1>
<p align="center">Connect Philips Hue to Loxone – locally, clearly, with eight helping arms.</p>
<p align="center"><a href="docs/MANUAL.md">Manual</a> · <a href="INSTALL.md">Installation</a></p>

**Your Hue lights in Loxone. Easy to connect. Simple to control.**

Bring your Philips Hue lights and scenes into your Loxone setup – without programming, using automatically generated templates for Loxone Config.

Hue2Lox discovers the lights and scenes on your bridges and offers the controls they support: switching, dimming, color and white temperature. Select your devices and copy the ready-made commands or import them into Loxone Config as XML.

Keep everything in view: multiple bridges, your lights and scenes in one interface. Hue2Lox runs locally on your Linux server, supports German and English, and needs no cloud account during normal operation.

## Features

- Pair multiple Hue Bridges and discover lights and Hue scenes.
- Use switching, dimming, RGB and white temperature according to light capabilities.
- Filter by bridge and room; ignore and restore lights or scenes.
- Copy Loxone HTTP commands or export a selection as XML.
- Inspect incoming requests in a temporary, sanitized HTTP monitor.
- Manage locally over HTTP, optionally HTTPS through a reverse proxy; native installations use HTTPS.
- Docker and Podman containers, a native installer and local discovery helpers for macOS, Windows and Linux.
- Scenes as digital on/off circuits, with automatic assignment of uniquely matching groups.

## Preview

![Loxone command fields in Hue2Lox](web/tutorial-commands.png)

*Example with test data and German labels; the current layout is more compact. More illustrations are in the [Loxone guide](docs/TUTORIAL.md).*

## Install and get started

**Preferred: a Docker Compose container in a Linux VM**, for example on Proxmox. Proxmox hosts the VM; Docker Engine and Compose run inside Linux. This does not certify a privileged LXC deployment.

[Runtime/version status](docs/RUNTIME-SUPPORT.md) · [Storage, login, networking and TLS](docs/CONTAINER-SETUP.md)

| Installation path | Status | Guide |
| --- | --- | --- |
| **Docker Compose in a Linux VM** | Preferred container path: fixed **1.0.3**, persistent volume and matching browser URL. | [Container guide](docs/DOCKER.md#docker-compose) · [Setup](docs/CONTAINER-SETUP.md) |
| Podman Desktop on macOS ARM64 | Separately tested local path, not blanket LAN/Proxmox acceptance. | [Accepted flow and limits](docs/DOCKER.md#podman-desktop-on-macos) |
| Native without Docker | Guided native installer; experimental on explicitly tested amd64/systemd targets. | [Native guide](docs/INSTALL-NATIVE.en.md) |

### Simple start

Prerequisites: Linux with Docker Engine, the Compose plugin and curl; Docker permissions (for example `su -`) and free port **18443**. Run from the desired parent directory. The new `hue2lox` folder must not exist; maintain existing installations using the update procedure.

```sh
mkdir hue2lox &&
cd hue2lox &&
curl --fail --location --output compose.yaml https://raw.githubusercontent.com/square-com-de/hue2lox/v1.0.3/docker/compose.quickstart.yaml &&
docker compose up -d --wait &&
docker compose ps
```

Open **http://SERVER-IP:18443** using the Linux server’s private IP. Fresh data: **admin / admin**, then change the password. Storage is created automatically; retain the folder/project and volume during updates. HTTP is for a trusted LAN. For HTTPS with Traefik, see [configuration locations and the complete example](docs/CONTAINER-SETUP.md#http-or-https).

1. **Prepare the container:** Start the [Compose quick-start file](docker/compose.quickstart.yaml) using the [short guide](docs/CONTAINER-SETUP.md). Docker/Compose must be installed and port 18443 free. Browser login and persistence were independently checked; see [exact test scope and limits](docs/CONTAINER-ACCEPTANCE-1.0.1.md).
2. **Sign in:** use the actual HTTP/HTTPS URL; port 8443 alone does not mean HTTPS. Fresh data: `admin/admin`; retained data: the existing password. Verify the certificate when using HTTPS.
3. **Configure the bridge:** it must be reachable from the container. Failed multicast discovery differs from failed direct connectivity; manual IP entry cannot bypass a network block.
4. **Connect Loxone:** use the [illustrated commands/XML guide](docs/TUTORIAL.md). Import new digital commands for scene OFF; existing recall outputs are not rewritten.

**Already installed?** Use [backup, update and rollback](docs/UPDATE-DOCKER.md), not the fresh installer. Pull and restart do not replace an existing container. Handle custom Portainer/Compose stacks separately; preserve passwords and intentionally disabled controls. [1.0.3 downloads/checksums](docs/DOWNLOADS.md) · [Release notes](docs/RELEASE-NOTES-1.0.3.md). There is no dedicated LoxBerry plugin yet.

## Feedback & contact

Have you tried Hue2Lox? I'd love to hear your feedback – including what works well!

- **By email, no GitHub account needed:** [hue2lox@square-com.de](mailto:hue2lox@square-com.de)
- **Feedback or questions on GitHub:** [Open feedback / question](https://github.com/square-com-de/hue2lox/issues/new?template=feedback_question.md) (GitHub account required).
- **Bugs or improvement ideas:** [Choose an issue template](https://github.com/square-com-de/hue2lox/issues/new/choose).

For problems, include your Hue2Lox version, a short description and, if useful, a screenshot or error message. Please omit passwords and tokens. Report security issues privately – see [security reporting](SECURITY.md).

## Release status and technical notes

**Hue2Lox 1.0.3 — in Vorbereitung / unreleased.** Includes the native installation path, local discovery help, scene on/off and an installed-version display. Prior hardware acceptance belongs to 1.0.0/1.0.1; it is not a new 1.0.3 hardware test. See [release notes and actual acceptance scope](docs/RELEASE-NOTES-1.0.3.md). Use the versioned download commands below only after 1.0.3 publication completes.

Use the versioned ZIP or `1.0.3` images from Docker Hub/GHCR (AMD64/ARM64). `latest` follows the latest successfully verified stable release; pin `1.0.3` for reproducible deployments. Native operation remains experimental and amd64-only. Earlier RC packages stay unchanged.

Create and edit scenes in the Hue app. [Scene on/off](docs/features/SCENE-SWITCH.md) activates a scene and switches off its assigned group. Existing recall commands keep working; import the new digital commands to use OFF. Actual light-state feedback into the Loxone Lighting Controller is not included.

**Existing installations:** use the [backup/update/rollback procedure](docs/UPDATE-DOCKER.md) for standard Docker deployments or [native maintenance](docs/INSTALL-NATIVE.en.md). Inspect custom Compose/prototype installations separately. Fresh setup is not a general updater.

Changes and remaining approval: [changelog](CHANGELOG.md) · [release overview](RELEASE.md) · [1.0.3 preparation](docs/PREPARATION-1.0.3.md). Historical reports are listed separately in the [documentation index](docs/INDEX.md).

## Documentation

[All guides, technical references and historical reports](docs/INDEX.md).

| Topic | Start here |
| --- | --- |
| Usage, troubleshooting and backup | [Manual](docs/MANUAL.md) |
| Native installer and VM evidence | [Native guide](docs/INSTALL-NATIVE.en.md) · [Current VM acceptance](docs/DEPLOYMENT-ACCEPTANCE.md) |
| Fresh test installation | [Installation](INSTALL.md) |
| Prebuilt Docker image (AMD64/ARM64) | [Container guide](docs/DOCKER.md) |
| Loxone HTTP outputs and XML | [Illustrated guide](docs/TUTORIAL.md) |
| Architecture and container | [Technical reference (German)](docs/CONTAINER.md) |
| Quality checks and contributing | [Development](CONTRIBUTING.md) |
| Joint hardware tests | [Acceptance plan](docs/ACCEPTANCE.md) |
| Sources, icons and licensing | [Third-party notices](THIRD-PARTY-NOTICES.md) |
| Release status and limits | [Release notes](RELEASE.md) |

**After an update:** Recreate rather than only restart; retained data keeps its password and intentionally disabled controls. For RC5 state, read the [targeted recovery guide](docs/RECOVERY-CONTROL.md) first. [Lessons learned and open release gates](docs/LESSONS-LEARNED.md).

## Quality and security

[GitHub checks](https://github.com/square-com-de/hue2lox/actions/workflows/quality.yml) cover source, translations, local HTTPS startup and an isolated container. Passing checks do not prove compatibility with every light or Miniserver.

Do not submit tokens, private keys, private backups or token-bearing XML in issues or pull requests. See [security reporting](SECURITY.md).

## License status

Hue2Lox uses the [Apache License 2.0](LICENSE), which permits commercial use and redistribution under its terms. Original code, documentation and project artwork are included to the extent applicable rights exist. Third-party materials retain their own terms: [notices](THIRD-PARTY-NOTICES.md) · [NOTICE](NOTICE).

Independent project; not officially affiliated with Philips Hue or Loxone.

<p align="center"><strong>by <a href="https://square-com.de/">square | com</a></strong> · <a href="https://square-com.de/impressum/">Impressum / Legal notice</a></p>
