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
- Shared Docker/native installer and local discovery helpers for macOS, Windows and Linux.
- Scenes as digital on/off circuits, with automatic assignment of uniquely matching groups.

## Preview

![Loxone command fields in Hue2Lox](web/tutorial-commands.png)

*Example with test data and German labels; the current layout is more compact. More illustrations are in the [Loxone guide](docs/TUTORIAL.md).*

## Install and get started

The shared **1.0.0 installer** offers Docker or native operation. The installation guides use the versioned 1.0.0 source ZIP and fixed images; verify checksums and successful release publication.

| Installation method | Who is it for? | Guide |
| --- | --- | --- |
| **Installer with Docker** | Guided setup; fixed release image after publication or local build. | [Installation guide](INSTALL.md). Choose **local build** for source tests. |
| **Docker / Compose** | Existing container environments, including reverse proxies. | [Container guide](docs/DOCKER.md). Use the fixed 1.0.0 image. |
| **Native without Docker** | Experimental systemd operation on explicitly tested amd64 Linux targets. | [Native guide](docs/INSTALL-NATIVE.en.md). Source ZIP and native archive required. |

1. **Start the installer:** the [guide](INSTALL.md) covers prerequisites, package verification and deployment selection. Use your Mac or Windows PC to operate the Linux server.
2. **Set up Hue2Lox:** the installer checks prerequisites and reuses working Docker installations. Fresh installations enable the control features each light supports.
3. **Sign in:** open the displayed web address and verify its certificate for direct HTTPS. Initial login `admin/admin`; change the password afterwards. Add your Hue Bridge and read its lights and scenes.
4. **Connect Loxone:** the [illustrated guide](docs/TUTORIAL.md) explains commands and XML for Loxone Config.

**[Installation guide](INSTALL.md) · [1.0.0 packages and checksums](docs/DOWNLOADS.md) · [1.0.0 release notes](docs/RELEASE-NOTES-1.0.0.md)**

**Already installed?** Follow the [backup, update and rollback guide](docs/UPDATE-DOCKER.md). Updating never overrides intentionally disabled controls. AI guidance is available through the [installation prompt](docs/AI-INSTALL.md).

## Feedback & contact

Have you tried Hue2Lox? I'd love to hear your feedback – including what works well!

- **By email, no GitHub account needed:** [hue2lox@square-com.de](mailto:hue2lox@square-com.de)
- **Feedback or questions on GitHub:** [Open feedback / question](https://github.com/square-com-de/hue2lox/issues/new?template=feedback_question.md) (GitHub account required).
- **Bugs or improvement ideas:** [Choose an issue template](https://github.com/square-com-de/hue2lox/issues/new/choose).

For problems, include your Hue2Lox version, a short description and, if useful, a screenshot or error message. Please omit passwords and tokens. Report security issues privately – see [security reporting](SECURITY.md).

## Release status and technical notes

**Stable 1.0.0.** Includes the shared installer, local discovery help and scene on/off control. User acceptance covers TV-strip Lumitech color, warm/cold white, dimming, off, scene changes and final OFF. Docker/native lifecycle tests on Ubuntu and DietPi cover restart, update/rollback and retained data. See [release notes and limits](docs/RELEASE-NOTES-1.0.0.md).

Use the versioned ZIP or `1.0.0` images from Docker Hub/GHCR (AMD64/ARM64). `latest` follows the latest successfully verified stable release; pin `1.0.0` for reproducible deployments. Native operation remains experimental and amd64-only. Earlier RC packages stay unchanged.

Create and edit scenes in the Hue app. [Scene on/off](docs/features/SCENE-SWITCH.md) activates a scene and switches off its assigned group. Existing recall commands keep working; import the new digital commands to use OFF. Actual light-state feedback into the Loxone Lighting Controller is not included.

**Existing installations:** use the [backup/update/rollback procedure](docs/UPDATE-DOCKER.md) for standard Docker deployments or [native maintenance](docs/INSTALL-NATIVE.en.md). Inspect custom Compose/prototype installations separately. Fresh setup is not a general updater.

See the [changelog](CHANGELOG.md), [historical RC6 preparation](docs/RC6-PREPARATION.md) and [release overview](RELEASE.md).

## Documentation

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

## Quality and security

[GitHub checks](https://github.com/square-com-de/hue2lox/actions/workflows/quality.yml) cover source, translations, local HTTPS startup and an isolated container. Passing checks do not prove compatibility with every light or Miniserver.

Do not submit tokens, private keys, private backups or token-bearing XML in issues or pull requests. See [security reporting](SECURITY.md).

## License status

Hue2Lox uses the [Apache License 2.0](LICENSE), which permits commercial use and redistribution under its terms. Original code, documentation and project artwork are included to the extent applicable rights exist. Third-party materials retain their own terms: [notices](THIRD-PARTY-NOTICES.md) · [NOTICE](NOTICE).

Independent project; not officially affiliated with Philips Hue or Loxone.

<p align="center"><strong>by <a href="https://square-com.de/">square | com</a></strong> · <a href="https://square-com.de/impressum/">Impressum / Legal notice</a></p>
