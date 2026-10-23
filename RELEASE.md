# RC6 candidate — prepared, unpublished / vorbereitet, unveröffentlicht

This branch is the RC6 release candidate source with version pin `1.0.0-rc.6`. It must remain unmerged until separately approved; no tag/release/image is created here. / Dieser Branch enthält den RC6-Kandidaten mit festem Versionspin. Bis zur separaten Freigabe ungemergt lassen; hier wird kein Tag/Release/Image angelegt.

[RC6 release-note draft / Release-Notes-Entwurf](docs/RELEASE-NOTES-RC6.md) · [Technical checks / Technische Prüfungen](docs/RC6-TECHNICAL-REVIEW.md) · [Hardware plan / Hardwareplan](docs/ACCEPTANCE.md)

# Release status / Release-Stand — 23.10.2026

**Published / Veröffentlicht: RC5. RC6: unpublished preparation / unveröffentlichte Vorbereitung.** PR #18 is merged into main; [current deployment acceptance / aktuelle Deployment-Abnahme](docs/DEPLOYMENT-ACCEPTANCE.md) passed. See [changelog](CHANGELOG.md) and [RC6 draft and release gates / RC6-Entwurf und Freigabepunkte](docs/RC6-PREPARATION.md). No RC6 tag, release or image is advertised as available. / Kein RC6-Tag, Release oder Image wird als verfügbar dargestellt.

The RC5 description below is historical and describes RC5 only, including its then-open tests. RC1/RC5 tags, releases and assets remain unchanged. / Der folgende RC5-Text ist historisch und gilt einschließlich damaliger offener Tests nur für RC5. RC1/RC5-Tags, Releases und Assets bleiben unverändert.

---

# Hue2Lox — Release Candidate 5

[RC5 release and downloads](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.5) · [English installation](INSTALL.md) · [Deutsche Installation](INSTALL.de.md)

RC5 (`v1.0.0-rc.5`) adds Docker Hub publication alongside GHCR. The application
and installer behavior are unchanged from RC4. RC1–RC4 and running installations
remain unchanged; `main` is the separate development version.

RC5 ergänzt Docker Hub neben GHCR. Anwendung und Installer verhalten sich wie in
RC4. RC1–RC4 und laufende Installationen bleiben unverändert.

Publisher: **square | com** · [Impressum](https://square-com.de/impressum/)
License: Apache 2.0 for original project material; see LICENSE, NOTICE and THIRD-PARTY-NOTICES.md.

## Changes since RC4 / Änderungen seit RC4

- Identical tested AMD64/ARM64 images published to Docker Hub and GHCR. / Identische geprüfte Images für AMD64/ARM64 in beiden Registries.
- Anonymous pulls from both registries must match the tested image IDs. Published digests and source/license materials accompany the release. / Öffentliche Downloads beider Registries werden mit den geprüften Images abgeglichen; Digests und Quellen-/Lizenzbeilagen liegen beim Release.
- Versioned ZIP, checksum, Compose and German/English installation links aligned to RC5. / ZIP, Prüfsumme, Compose und deutsche/englische Installationslinks auf RC5 abgestimmt.
- Podman Desktop instructions explain the required browser URL and manual bridge pairing fallback. / Podman-Desktop-Anleitung erklärt Browseradresse und manuelle Bridge-Kopplung.

## Downloads and verification / Downloads und Prüfung

[Download and checksum](docs/DOWNLOADS.md) · [Container guide](docs/DOCKER.md)

```sh
docker pull docker.io/dubctrl/hue2lox:1.0.0-rc.5
# Or / oder:
podman pull ghcr.io/square-com-de/hue2lox:1.0.0-rc.5
```

The installer builds locally from the ZIP. Both registries offer the same prebuilt
images. RC5 never creates or updates `latest`; that tag is reserved for stable.
Der Installer baut lokal aus dem ZIP. Beide Registries bieten dieselben fertigen
Images an. RC5 setzt keinen `latest`-Tag; dieser bleibt Stable vorbehalten.

Release assets include `hue2lox-base-sources.tar.gz`, `container-evidence.tar.gz`,
`container-release.json`, `SHA256SUMS.txt` and `container-digests.json` with its
own checksum. Keep these materials with the images; see [container sources](docs/CONTAINER-SOURCES.md).

## Validation and limits / Prüfung und Grenzen

Source tests, installation/restart tests, both platform scans and source-material
checks gate publication. The release notes record the exact commit, ZIP checksum
and completed workflow. Fresh RC5 Debian and end-to-end Loxone acceptance remain
pending before stable. This is a release candidate.

Automatische Tests, Installation/Neustart, beide Plattformscans und Quellenabgleich
sichern die Veröffentlichung ab. Commit, ZIP-Prüfsumme und Workflow stehen in den
Release Notes. Die frische RC5-Debian-Abnahme und der durchgängige Loxone-Test
stehen vor Stable noch aus.

## Operating notes / Betriebshinweise

- Initial login: `admin` / `admin`; change the password after installation. / Erstpasswort nach der Installation ändern.
- Set `HUE_PUBLIC_URL` to the exact browser URL. An origin mismatch can still show an incorrect-password message; RC5 does not change this behavior. / `HUE_PUBLIC_URL` muss zur Browseradresse passen. Abweichungen können weiterhin als falsches Passwort angezeigt werden.
- Mac Podman multicast discovery may find no bridges; enter the bridge IP manually. / Unter Mac Podman gegebenenfalls die Bridge-IP manuell eingeben.
- Use a trusted local network; choose built-in HTTPS or a TLS reverse proxy as needed. / Im vertrauenswürdigen lokalen Netzwerk betreiben; HTTPS oder TLS-Proxy nach Bedarf verwenden.
- Back up data before manual updates. The installer refuses existing destinations and is not a general updater. / Vor manuellen Updates Daten sichern; der Installer überschreibt keine bestehenden Ziele.
- Native Debian/Python deployment is still in preparation. / Native Debian-/Python-Installation ist noch in Vorbereitung.

Publication runbook: [GHCR and Docker Hub](docs/GHCR-RELEASE.md).
