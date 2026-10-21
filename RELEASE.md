# Hue2Lox — Release Candidate 4

[RC4 release and downloads](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.4) · [English installation](INSTALL.md) · [Deutsche Installation](INSTALL.de.md)

RC4 (`v1.0.0-rc.4`) offers a fixed installer ZIP and the first prebuilt GHCR image
for AMD64/ARM64. RC1, RC2 and RC3 remain unchanged. Existing installations are not
updated automatically. `main` remains the separate development version.

RC4 bietet ein festes Installer-ZIP und erstmals ein fertiges GHCR-Image für
AMD64/ARM64. RC1, RC2, RC3 und laufende Installationen bleiben unverändert.

Publisher: **square | com** · [Impressum](https://square-com.de/impressum/)
License: Apache 2.0 for original project material; see LICENSE, NOTICE and THIRD-PARTY-NOTICES.md.

## Changes since RC3 / Änderungen seit RC3

- Installer: choose direct HTTPS with a generated certificate or HTTP, for example behind Traefik. / HTTPS mit eigenem Zertifikat oder HTTP, etwa hinter Traefik, im Installer wählen.
- Prebuilt image: `ghcr.io/square-com-de/hue2lox:1.0.0-rc.4`, persistent data volume and lamp control enabled by default. / Fertiges Image mit persistentem Datenspeicher und standardmäßig freigegebener Lampensteuerung.
- Python 3.15 container base, pinned by digest; unused pip/ensurepip tooling removed. / Per Digest festgeschriebene Python-3.15-Basis, ungenutzte pip-/ensurepip-Werkzeuge entfernt.
- AMD64/ARM64 scans, inventories, SPDX SBOMs, corresponding sources and license materials accompany the release. / Scans, Inventare, SPDX-SBOMs sowie Quellen- und Lizenzbeilagen für beide Architekturen.
- English/German installation choices, direct-download links and checksums aligned. / Deutsche und englische Installationswege, Direktdownloads und Prüfsummen abgeglichen.

## Downloads and verification

Follow [DOWNLOADS.md](docs/DOWNLOADS.md) for the fixed ZIP, checksum and archive
root. The installer builds locally; Docker/Compose users can pull the fixed
image version instead. `latest` is reserved for stable releases.

The release includes `hue2lox-base-sources.tar.gz`, `container-evidence.tar.gz`,
`container-release.json` and `SHA256SUMS.txt`. Published image digests are recorded
in `container-digests.json` with a separate checksum. Keep these materials with
the corresponding images; see [container sources](docs/CONTAINER-SOURCES.md).

## Validation and limits / Prüfung und Grenzen

Automated source tests, isolated HTTP/HTTPS installation and restart, certificate
renewal, backup/restore, both platform startup checks and fixable HIGH/CRITICAL
vulnerability scans gate publication. The release notes record the exact commit,
ZIP checksum and completed run. Green automated checks are not a substitute for
real-device acceptance: a fresh RC4 Debian installation and end-to-end Loxone
control still need user testing before stable.

Automatische Tests prüfen unter anderem HTTP/HTTPS, Neustart, Zertifikatserneuerung,
Backup/Wiederherstellung und beide Image-Architekturen. Der frische Debian-Test
mit RC4 und die durchgängige Loxone-Abnahme stehen vor Stable noch aus.

## Operating notes

- Initial login: `admin` / `admin`. Change the password after installation.
- For a trusted local network; use a TLS reverse proxy or built-in HTTPS where appropriate.
- The installer refuses to overwrite an existing destination and is not a general updater.
- Back up credentials, tokens and device state before any manual update.
- Native Debian/Python installation without Docker remains in preparation (PR #18).
- Report ordinary problems through Issues; security issues privately via [SECURITY.md](SECURITY.md).

## Future prebuilt image release gate

Preparation status and per-platform evidence: [Container compliance](docs/IMAGE-COMPLIANCE.md).
The preparation workflow builds and inventories candidates without pushing to any registry.
The separate [GHCR release workflow](docs/GHCR-RELEASE.md) runs for a
published release: tests, both platform scans and source-material checks gate
publication. Merging it alone does not publish images or change RC3.

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

These checks apply to every future image release. A local
user who later redistributes their built image must assess that distribution's
obligations separately; the local-build workflow is not a blanket exemption.
