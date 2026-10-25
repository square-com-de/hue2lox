**Use 1.0.3 links only after its publication workflow succeeds. / Die 1.0.3-Links erst nach erfolgreichem Veröffentlichungsworkflow verwenden.**

**Unveröffentlichter Kandidat / unreleased candidate: 1.0.3.** Der erfolgreiche Veröffentlichungsworkflow bestätigt Downloads, Prüfsummen und beide Registries; [Release-Hinweise](RELEASE-NOTES-1.0.3.md). / The successful publication workflow verifies downloads, checksums and both registries; see the release notes.

# 1.0.3: Download und Prüfsumme / Download and checksum

Für die normale Installation verwenden die deutsche und englische Anleitung dasselbe **1.0.3-Paket**. / The German and English guides use the same **1.0.3 package** for normal installation.

| Merkmal / Field | Wert / Value |
| --- | --- |
| Version | `v1.0.3` |
| Quellstand / Source | [Fester Release-Tag / Fixed release tag](https://github.com/square-com-de/hue2lox/tree/v1.0.3); die vollständige Commit-ID steht in den [Release Notes](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.3) / full commit ID in the release notes |
| Quellpaket / Source package | [hue2lox-v1.0.3.zip](https://github.com/square-com-de/hue2lox/releases/download/v1.0.3/hue2lox-v1.0.3.zip) |
| Natives Archiv / Native archive | [hue2lox-1.0.3-native.tar.gz](https://github.com/square-com-de/hue2lox/releases/download/v1.0.3/hue2lox-1.0.3-native.tar.gz), zusätzlich für nativ / additionally required for native |
| Archivordner / Archive root | `hue2lox-v1.0.3/` |
| SHA-256 | [SHA256SUMS.txt](https://github.com/square-com-de/hue2lox/releases/download/v1.0.3/SHA256SUMS.txt); derselbe Wert steht in den Release Notes / the same value is recorded in the release notes |

## Direkt auf dem Server installieren / Install directly on the server

[Deutsche Anleitung](../INSTALL.de.md) · [English guide](../INSTALL.md)

Für nativ laden beide Anleitungen das ZIP, das native Archiv und die Prüfsummen mit `curl` direkt auf den Linux-Server. Erst nach erfolgreicher Prüfung **beider** Paketdateien wird entpackt und gestartet. Ein vorheriger Download auf Mac/PC oder Kopieren per `scp` ist nicht nötig. / For native installation both guides use `curl` to download the ZIP, native archive and checksums directly to the Linux server. Extraction and startup happen only after successful verification. No prior download on your Mac/PC or transfer with `scp` is needed.

## Optional: im Browser herunterladen / Download in a browser

Quell-ZIP und Prüfsummenliste in denselben Ordner laden; für nativ zusätzlich das native Archiv und dessen Prüfsummeneintrag prüfen. / Download source ZIP and checksum list into the same directory; for native also download the native archive and verify its checksum entry.

**Linux:**

```sh
grep '  hue2lox-v1.0.3.zip$' SHA256SUMS.txt | sha256sum --check -
```

**macOS:**

```sh
grep '  hue2lox-v1.0.3.zip$' SHA256SUMS.txt | shasum -a 256 --check -
```

**Windows PowerShell:**

```powershell
Get-FileHash .\hue2lox-v1.0.3.zip -Algorithm SHA256
Get-Content .\SHA256SUMS.txt
```

Unter Windows den vollständigen Hash vergleichen. Nur bei Übereinstimmung fortfahren. / On Windows, compare the full hash. Continue only if it matches.

## Container und Beilagen / Container and accompanying materials

Images: `docker.io/dubctrl/hue2lox:1.0.3` or / oder `ghcr.io/square-com-de/hue2lox:1.0.3` (AMD64/ARM64). [Container guide](DOCKER.md).

Beim [1.0.3-Release](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.3) liegen zusätzlich `hue2lox-base-sources.tar.gz` (Quellen/Lizenzen), `container-evidence.tar.gz` (Inventare, SBOMs, Scans), `container-release.json` (Quellstand) und `container-digests.json` samt eigener Prüfsumme. / The release also contains corresponding sources/licenses, platform evidence/SBOMs/scans, source metadata and published image digests with their own checksum.

Die ZIP-Prüfbefehle oben wählen gezielt den ZIP-Eintrag aus der gemeinsamen Prüfsummenliste. Die zusätzlichen Beilagen müssen für die Installation nicht heruntergeladen werden. / The commands above select only the ZIP entry from the shared checksum list; installation does not require downloading the other materials.

## Veröffentlichte Version und historische RCs / Published version and historical RCs

Aktuell veröffentlicht / currently published: [1.0.2](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.2).

[RC5](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.5) remains published and unchanged at commit `45237512dcd18db9aaf3611173ce91ad8c654450`. [RC1](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.1) remains unchanged at `1d631cd1231d7cf004c6452c1fad0c262ff92bfd`. / RC5 und RC1 bleiben unter ihren ursprünglichen Tags unverändert.

Use the source commit and checksums recorded on the 1.0.3 release. Successful public verification must match these artifacts to the tested images. The scene on/off hardware acceptance on24October2026 belongs to 1.0.0/1.0.1, not a new 1.0.3 qualification. / Quellcommit und Prüfsummen beim 1.0.3-Release verwenden. Die öffentliche Prüfung muss diese Dateien den geprüften Images zuordnen. Die Szenen-Hardwareabnahme vom24.10.2026 gehört zu 1.0.0/1.0.1, nicht zu einer neuen1.0.3-Abnahme.
