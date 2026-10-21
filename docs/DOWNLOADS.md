# RC5: Download und Prüfsumme / Download and checksum

Für die normale Installation verwenden Deutsch, Englisch und der KI-Prompt dasselbe **RC5-Paket**. / The German, English and AI guides use the same **RC5 package** for normal installation.

| Merkmal / Field | Wert / Value |
| --- | --- |
| Version | `v1.0.0-rc.5` |
| Quellstand / Source | [Fester Release-Tag / Fixed release tag](https://github.com/square-com-de/hue2lox/tree/v1.0.0-rc.5); die vollständige Commit-ID steht in den [Release Notes](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.5) / full commit ID in the release notes |
| Paket / Package | [hue2lox-v1.0.0-rc.5.zip](https://github.com/square-com-de/hue2lox/releases/download/v1.0.0-rc.5/hue2lox-v1.0.0-rc.5.zip) |
| Archivordner / Archive root | `hue2lox-v1.0.0-rc.5/` |
| SHA-256 | [SHA256SUMS.txt](https://github.com/square-com-de/hue2lox/releases/download/v1.0.0-rc.5/SHA256SUMS.txt); derselbe Wert steht in den Release Notes / the same value is recorded in the release notes |

## Direkt auf dem Server installieren / Install directly on the server

[Deutsche Anleitung](../INSTALL.de.md#option-1-einfach-und-komfortabel--der-installer) · [English guide](../INSTALL.md)

Beide Anleitungen laden das ZIP und seine Prüfsumme mit `curl` direkt auf den Linux-Server. Erst nach erfolgreichem `grep '  hue2lox-v1.0.0-rc.5.zip$' SHA256SUMS.txt | sha256sum --check -` wird entpackt und gestartet. Ein vorheriger Download auf Mac/PC oder Kopieren per `scp` ist nicht nötig. / Both guides use `curl` to download the ZIP and checksum directly to the Linux server. Extraction and startup happen only after successful verification. No prior download on your Mac/PC or transfer with `scp` is needed.

## Optional: im Browser herunterladen / Download in a browser

Lade die beiden oben verlinkten Assets in denselben Ordner. / Download both assets above into the same directory.

**Linux:**

```sh
grep '  hue2lox-v1.0.0-rc.5.zip$' SHA256SUMS.txt | sha256sum --check -
```

**macOS:**

```sh
grep '  hue2lox-v1.0.0-rc.5.zip$' SHA256SUMS.txt | shasum -a 256 --check -
```

**Windows PowerShell:**

```powershell
Get-FileHash .\hue2lox-v1.0.0-rc.5.zip -Algorithm SHA256
Get-Content .\SHA256SUMS.txt
```

Unter Windows den vollständigen Hash vergleichen. Nur bei Übereinstimmung fortfahren. / On Windows, compare the full hash. Continue only if it matches.

## Container und Beilagen / Container and accompanying materials

Images: `docker.io/dubctrl/hue2lox:1.0.0-rc.5` or / oder `ghcr.io/square-com-de/hue2lox:1.0.0-rc.5` (AMD64/ARM64). [Container guide](DOCKER.md).

Beim [RC5-Release](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.5) liegen zusätzlich `hue2lox-base-sources.tar.gz` (Quellen/Lizenzen), `container-evidence.tar.gz` (Inventare, SBOMs, Scans), `container-release.json` (Quellstand) und `container-digests.json` samt eigener Prüfsumme. / The release also contains corresponding sources/licenses, platform evidence/SBOMs/scans, source metadata and published image digests with their own checksum.

Die ZIP-Prüfbefehle oben wählen gezielt den ZIP-Eintrag aus der gemeinsamen Prüfsummenliste. Die zusätzlichen Beilagen müssen für die Installation nicht heruntergeladen werden. / The commands above select only the ZIP entry from the shared checksum list; installation does not require downloading the other materials.

## Entwicklung und ältere Versionen / Development and older versions

[main.zip](https://github.com/square-com-de/hue2lox/archive/refs/heads/main.zip) bleibt der bewegliche Entwicklungsstand; es ist nicht das RC5-Paket. Für einen gewöhnlichen Installationstest nicht zwischen diesen Downloads wechseln. / The main ZIP is a moving development snapshot, not RC5. Do not switch between them during an ordinary installation test.

[RC4](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.4) bleibt unverändert verfügbar. / RC4 remains available unchanged.

[RC3](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.3) bleibt unverändert verfügbar. / RC3 remains available unchanged.

[RC2](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.2) bleibt unverändert verfügbar. / RC2 remains available unchanged.

[RC1](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.1) bleibt als ältere Version unverändert verfügbar. Sein Paket heißt `hue2lox-main.zip` und hat SHA-256 `a630235b27d3f2bde5419d146050013c21907ec8862c3d88ef4ed8bc2c2a1f09`, Commit `1d631cd1231d7cf004c6452c1fad0c262ff92bfd`. / RC1 remains available unchanged as an older release, with its original filename, checksum and commit.

RC5 ist ein Release Candidate, kein Stable. Reale Debian-/Loxone-Tests des neuen Pakets bleiben offen; eine spätere Stable-Freigabe erfolgt separat. / RC5 is a release candidate, not stable. Real Debian/Loxone tests of the new package are pending; stable approval is a separate step.
