**Release-Version / Release version: 1.0.0.** Der erfolgreiche Veröffentlichungsworkflow bestätigt Downloads, Prüfsummen und beide Registries; [Release-Hinweise](RELEASE-NOTES-1.0.0.md). / The successful publication workflow verifies downloads, checksums and both registries; see the release notes.

# 1.0.0: Download und Prüfsumme / Download and checksum

Für die normale Installation verwenden Deutsch, Englisch und der KI-Prompt dasselbe **1.0.0-Paket**. / The German, English and AI guides use the same **1.0.0 package** for normal installation.

| Merkmal / Field | Wert / Value |
| --- | --- |
| Version | `v1.0.0` |
| Quellstand / Source | [Fester Release-Tag / Fixed release tag](https://github.com/square-com-de/hue2lox/tree/v1.0.0); die vollständige Commit-ID steht in den [Release Notes](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0) / full commit ID in the release notes |
| Paket / Package | [hue2lox-v1.0.0.zip](https://github.com/square-com-de/hue2lox/releases/download/v1.0.0/hue2lox-v1.0.0.zip) |
| Archivordner / Archive root | `hue2lox-v1.0.0/` |
| SHA-256 | [SHA256SUMS.txt](https://github.com/square-com-de/hue2lox/releases/download/v1.0.0/SHA256SUMS.txt); derselbe Wert steht in den Release Notes / the same value is recorded in the release notes |

## Direkt auf dem Server installieren / Install directly on the server

[Deutsche Anleitung](../INSTALL.de.md#option-1-einfach-und-komfortabel--der-installer) · [English guide](../INSTALL.md)

Beide Anleitungen laden das ZIP und seine Prüfsumme mit `curl` direkt auf den Linux-Server. Erst nach erfolgreichem `grep '  hue2lox-v1.0.0.zip$' SHA256SUMS.txt | sha256sum --check -` wird entpackt und gestartet. Ein vorheriger Download auf Mac/PC oder Kopieren per `scp` ist nicht nötig. / Both guides use `curl` to download the ZIP and checksum directly to the Linux server. Extraction and startup happen only after successful verification. No prior download on your Mac/PC or transfer with `scp` is needed.

## Optional: im Browser herunterladen / Download in a browser

Lade die beiden oben verlinkten Assets in denselben Ordner. / Download both assets above into the same directory.

**Linux:**

```sh
grep '  hue2lox-v1.0.0.zip$' SHA256SUMS.txt | sha256sum --check -
```

**macOS:**

```sh
grep '  hue2lox-v1.0.0.zip$' SHA256SUMS.txt | shasum -a 256 --check -
```

**Windows PowerShell:**

```powershell
Get-FileHash .\hue2lox-v1.0.0.zip -Algorithm SHA256
Get-Content .\SHA256SUMS.txt
```

Unter Windows den vollständigen Hash vergleichen. Nur bei Übereinstimmung fortfahren. / On Windows, compare the full hash. Continue only if it matches.

## Container und Beilagen / Container and accompanying materials

Images: `docker.io/dubctrl/hue2lox:1.0.0` or / oder `ghcr.io/square-com-de/hue2lox:1.0.0` (AMD64/ARM64). [Container guide](DOCKER.md).

Beim [1.0.0-Release](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0) liegen zusätzlich `hue2lox-base-sources.tar.gz` (Quellen/Lizenzen), `container-evidence.tar.gz` (Inventare, SBOMs, Scans), `container-release.json` (Quellstand) und `container-digests.json` samt eigener Prüfsumme. / The release also contains corresponding sources/licenses, platform evidence/SBOMs/scans, source metadata and published image digests with their own checksum.

Die ZIP-Prüfbefehle oben wählen gezielt den ZIP-Eintrag aus der gemeinsamen Prüfsummenliste. Die zusätzlichen Beilagen müssen für die Installation nicht heruntergeladen werden. / The commands above select only the ZIP entry from the shared checksum list; installation does not require downloading the other materials.

## Published previous release / Veröffentlichte Vorversion

[RC5](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.5) remains published and unchanged at commit `45237512dcd18db9aaf3611173ce91ad8c654450`. [RC1](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.1) remains unchanged at `1d631cd1231d7cf004c6452c1fad0c262ff92bfd`. / RC5 und RC1 bleiben unter ihren ursprünglichen Tags unverändert.

Use the source commit and checksums recorded on the 1.0.0 release. Successful public verification must match these artifacts to the tested images. The scene on/off hardware acceptance passed on 24 October 2026; see the release notes for scope. / Quellcommit und Prüfsummen beim 1.0.0-Release verwenden. Die öffentliche Prüfung muss diese Dateien den geprüften Images zuordnen. Die Szenen-Ein/Aus-Hardwareabnahme ist am 24.10.2026 bestanden; Umfang siehe Release-Hinweise.
