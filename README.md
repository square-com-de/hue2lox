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
- Manage locally over HTTPS without a cloud account for normal operation.

## Preview

![Loxone command fields in Hue2Lox](web/tutorial-commands.png)

*Example with test data and German labels; the current layout is more compact. More illustrations are in the [Loxone guide](docs/TUTORIAL.md).*

## Install and get started

Choose the installation method that suits you:

| Installation method | Who is it for? | Status and guide |
| --- | --- | --- |
| **Installer with Docker** | A guided setup for beginners. The assistant prepares Docker and builds Hue2Lox on your server. | **Available in RC5** · [Installation guide](INSTALL.md) |
| **Docker / Compose with a prebuilt image** | For existing container setups, including those behind a reverse proxy such as Traefik. | **Available in RC5** · [Container guide](docs/DOCKER.md) |
| **Python installer, without Docker** | For experimental direct service installation on explicitly supported Linux test targets. | **Experimental / PR #18** · [Shared installer and native guide](docs/INSTALL-NATIVE.en.md). Not included in RC5. |

Choose the guided installer or use the versioned Docker Hub or GHCR image directly. The development installer offers Docker or native operation; the native path is experimental and is not part of RC5. For Docker, the development installer offers a pinned release image or a local build. Choose the local build to test the new app features, including discovery help; published RC5 images remain unchanged.

### Get started with the Docker installer (RC5)

You need a Linux server, VM or Raspberry Pi with a supported 64-bit OS, a Hue Bridge and a Loxone Miniserver for control. Use your Mac or Windows PC to follow the setup guide.

1. **Start the installer:** the [English installation guide](INSTALL.md) takes you through connecting to the server, downloading RC5 directly with its checksum and starting the installer.
2. **Set up Hue2Lox:** the installer checks your system and can install missing packages and Docker. Existing working Docker installations are reused.
3. **Pair your bridge:** open the displayed web address (verify the certificate when using direct HTTPS) and sign in with `admin` / `admin`. You can change the password in the interface.
4. **Connect to Loxone:** choose lights or scenes and follow the [illustrated guide](docs/TUTORIAL.md) to copy commands or import XML into Loxone Config.

**[Open the installation guide](INSTALL.md) · [Download RC5 ZIP](https://github.com/square-com-de/hue2lox/releases/download/v1.0.0-rc.5/hue2lox-v1.0.0-rc.5.zip) · [Verify the download](docs/DOWNLOADS.md)**

Prefer guidance from an AI assistant? Use the [ChatGPT or Claude installation prompt](docs/AI-INSTALL.md). It guides you to the same interactive installer.

## Feedback & contact

Have you tried Hue2Lox? I'd love to hear your feedback – including what works well!

- **By email, no GitHub account needed:** [hue2lox@square-com.de](mailto:hue2lox@square-com.de)
- **Feedback or questions on GitHub:** [Open feedback / question](https://github.com/square-com-de/hue2lox/issues/new?template=feedback_question.md) (GitHub account required).
- **Bugs or improvement ideas:** [Choose an issue template](https://github.com/square-com-de/hue2lox/issues/new/choose).

For problems, include your Hue2Lox version, a short description and, if useful, a screenshot or error message. Please omit passwords and tokens. Report security issues privately – see [security reporting](SECURITY.md).

## Release status and technical notes

**Release Candidate 5.** German and English are available. An earlier fresh Debian 13 installation, bridge pairing, light display and restart have passed a user-run test. A fresh Debian test of the RC5 package and end-to-end testing with a Loxone Miniserver are still pending. Original project code is licensed under Apache 2.0.

RC5 offers **source code with the installer** and a **prebuilt Docker Hub/GHCR image for AMD64/ARM64**: `ghcr.io/square-com-de/hue2lox:1.0.0-rc.5`. The installer continues to build locally. Source and license materials accompany the [release](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.5). There is no `latest` tag before a stable release.

RC5 is an immutable version. Verify its [commit and checksum](docs/DOWNLOADS.md). `main` is the separate development version.

Create and edit scenes in the Hue app; recall them through Loxone. Synchronizing actual Hue light state back into the Loxone Lighting Controller is not part of this project.

**Existing installations:** a general release updater is not yet available. Preserve credentials and device state; do not overwrite an existing installation with fresh setup.

See [release notes](RELEASE.md) and [documented test results](docs/TEST-RESULTS.md) for details.

## Documentation

| Topic | Start here |
| --- | --- |
| Usage, troubleshooting and backup | [Manual](docs/MANUAL.md) |
| Native installer and VM evidence | [Native guide](docs/INSTALL-NATIVE.en.md) · [VM acceptance](docs/NATIVE-VM-ACCEPTANCE.md) |
| Fresh test installation | [Installation](INSTALL.md) |
| Prebuilt Docker image (AMD64/ARM64) | [Container guide](docs/DOCKER.md) |
| Loxone HTTP outputs and XML | [Illustrated guide](docs/TUTORIAL.md) |
| Architecture and container | [Technical reference (German)](docs/CONTAINER.md) |
| Quality checks and contributing | [Development](CONTRIBUTING.md) |
| Joint hardware tests | [Acceptance plan](docs/ACCEPTANCE.md) |
| Sources, icons and licensing | [Third-party notices](THIRD-PARTY-NOTICES.md) |
| Release status and limits | [Release notes](RELEASE.md) |

## Quality and security

[GitHub checks](https://github.com/square-com-de/hue2lox/actions/workflows/quality.yml) cover source, translations, local HTTPS startup and an isolated container. Passing checks do not prove compatibility with every light or Miniserver.

Do not submit tokens, private keys, private backups or token-bearing XML in issues or pull requests. See [security reporting](SECURITY.md).

## License status

Hue2Lox uses the [Apache License 2.0](LICENSE), which permits commercial use and redistribution under its terms. Original code, documentation and project artwork are included to the extent applicable rights exist. Third-party materials retain their own terms: [notices](THIRD-PARTY-NOTICES.md) · [NOTICE](NOTICE).

Independent project; not officially affiliated with Philips Hue or Loxone.

<p align="center"><strong>by <a href="https://square-com.de/">square | com</a></strong> · <a href="https://square-com.de/impressum/">Impressum / Legal notice</a></p>
