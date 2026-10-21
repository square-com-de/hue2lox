# Hue2Lox — Release Candidate 3

[RC3 release notes and ZIP](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.3) · [English installation](docs/INSTALL.en.md) · [Deutsche Installation](INSTALL.md)

RC3 (`v1.0.0-rc.3`) packages the updated application, repository layout and direct-download documentation into one fixed source archive. RC1 (`v1.0.0-rc.1`) and RC2 (`v1.0.0-rc.2`) remain unchanged. The `main` branch can contain newer development work; use the named RC3 asset for normal installation and testing.

RC3 enthält Anwendung, aktuelle Ordnerstruktur und die vereinfachte Direktdownload-Anleitung in einem festen Paket. RC1 und RC2 bleiben unverändert. Der erneute Test auf einer frischen Debian-VM folgt genau dieser öffentlichen RC3-Anleitung; er ist noch nicht abgeschlossen.

Publisher: **square | com** · [Impressum](https://square-com.de/impressum/)
License: Apache 2.0 for original project material; see LICENSE, NOTICE and THIRD-PARTY-NOTICES.md.

The authoritative [download mapping](docs/DOWNLOADS.md) records the published candidate, commit, archive root and checksum. Stable is preparation only; no stable asset or checksum is implied.

## Changes since RC2 / Änderungen seit RC2

- Clear bilingual welcome heading and separated language selection at installer startup. / Deutliche zweisprachige Überschrift und abgesetzte Sprachauswahl beim Installerstart.
- Shorter root-login instructions in German and English. / Kürzere Root-Anmeldung in der deutschen und englischen Anleitung.
- All normal download links point to the fixed RC3 package and checksum. / Alle regulären Downloadlinks führen zum festen RC3-Paket mit Prüfsumme.

## Delivery

This repository starts with a clean source snapshot, without private development history.
Download the named RC3 ZIP and follow its [INSTALL.md](INSTALL.md); the guide verifies SHA256SUMS.txt before extraction. Cloning main is a separate development path.
Docker images are built locally from these sources. No prebuilt Hue2Lox images or VM appliances are distributed.

## Validation and limits

On 20 October 2026, a user-run fresh Debian 13 VM installation passed installation, login, bridge discovery/pairing, inventory display and a full VM reboot with the configuration retained. See [docs/TEST-RESULTS.md](docs/TEST-RESULTS.md).
Automated source, HTTPS and container checks are defined in GitHub Actions; consult the run for the specific commit.
Isolated CI covers backup/restore, certificate renewal and an IP change. A fresh Debian test of this exact RC3 package and real Loxone/client-trust acceptance remain open. Existing historical live-control tests do not imply every device or distribution is covered.

## Operating notes

- Intended for a trusted local network; do not expose the interface directly to the Internet.
- Initial login: `admin` / `admin`. Change the password after installation.
- New installations generate individual control tokens and TLS keys.
- The installer refuses to overwrite an existing destination. It is not a general upgrade tool. Back up existing configuration and secrets before any manual update; preserve `.env` and the installation name.
- See [SECURITY.md](SECURITY.md) for reporting vulnerabilities, and GitHub Issues for ordinary bugs (without private data).

## Future prebuilt image release gate

Preparation status and per-platform evidence: [Container compliance](docs/IMAGE-COMPLIANCE.md).
The image workflow currently builds and inventories candidates without pushing to any registry.

Before changing the delivery model, complete and review the following for the
exact image to be distributed:

- Record the release/source commit, build recipes and patches, base index and
  platform digests, resulting image digests and every offered CPU architecture.
- Inventory the final image, including OS packages, Python, pip, vendored
  libraries and transitive dependencies; produce a versioned SBOM per platform.
- Collect applicable complete license texts, copyrights and notices per
  component, with a mapping to the inventory. A generic Python/Alpine notice
  or a list of SPDX identifiers alone is not the complete license package.
- Determine and fulfill source-delivery obligations under each applicable
  GPL/LGPL or other license: retain matching sources, build scripts and patches,
  and provide a compliant delivery method or offer where permitted. Do not
  assume a link to an upstream homepage or SBOM satisfies these obligations.
- Retain copies and an availability/retention plan for any required source
  delivery or offers; document where recipients obtain the materials.
- Package notices and accompanying materials with the release, and verify the
  recipient-facing download path. Resolve the Hue certificate redistribution
  question for images as well as source archives.
- Run image security checks and acceptance tests on the exact release digests.
  Record license review and release approval separately from test results.

Until these checks are complete, continue source-only distribution. A local
user who later redistributes their built image must assess that distribution's
obligations separately; the local-build workflow is not a blanket exemption.
