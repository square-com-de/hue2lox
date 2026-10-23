> **RC6 preparation — NOT RELEASED.** RC6 downloads/images below are planned references and must not be run until publication is explicitly approved and verified. For isolated tests use the supplied local ZIP/native archive or local build. Published RC5 remains [available unchanged](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.5). This candidate branch intentionally pins RC6; live main retains RC5 until merge approval.

> **RC6-Vorbereitung — NICHT VERÖFFENTLICHT.** RC6-Downloads/Images unten sind geplante Verweise, erst nach freigegebener und geprüfter Veröffentlichung verwenden. Isoliert die lokal bereitgestellten Archive oder lokalen Build nutzen. RC5 bleibt unverändert verfügbar. Dieser Kandidatenbranch bindet RC6; main behält RC5 bis zur Merge-Freigabe.

**Aktueller Downloadstatus / Current downloads:** RC5 bleibt die veröffentlichte Version. RC6 ist [in Vorbereitung](RC6-PREPARATION.md), ohne veröffentlichten Download oder Image-Tag. Die [neue Deployment-Abnahme](DEPLOYMENT-ACCEPTANCE.md) gilt für main, nicht rückwirkend für das RC6-Paket. / RC5 remains the published version. RC6 is being prepared, without published downloads or image tags; new deployment evidence applies to main, not retroactively to RC6.

# RC6: Download und Prüfsumme / Download and checksum

Für die normale Installation verwenden Deutsch, Englisch und der KI-Prompt dasselbe **RC6-Paket**. / The German, English and AI guides use the same **RC6 package** for normal installation.

| Merkmal / Field | Wert / Value |
| --- | --- |
| Version | `v1.0.0-rc.6` |
| Quellstand / Source | [Fester Release-Tag / Fixed release tag](https://github.com/square-com-de/hue2lox/tree/v1.0.0-rc.6); die vollständige Commit-ID steht in den [Release Notes](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.6) / full commit ID in the release notes |
| Paket / Package | [hue2lox-v1.0.0-rc.6.zip](https://github.com/square-com-de/hue2lox/releases/download/v1.0.0-rc.6/hue2lox-v1.0.0-rc.6.zip) |
| Archivordner / Archive root | `hue2lox-v1.0.0-rc.6/` |
| SHA-256 | [SHA256SUMS.txt](https://github.com/square-com-de/hue2lox/releases/download/v1.0.0-rc.6/SHA256SUMS.txt); derselbe Wert steht in den Release Notes / the same value is recorded in the release notes |

## Direkt auf dem Server installieren / Install directly on the server

[Deutsche Anleitung](../INSTALL.de.md#option-1-einfach-und-komfortabel--der-installer) · [English guide](../INSTALL.md)

Beide Anleitungen laden das ZIP und seine Prüfsumme mit `curl` direkt auf den Linux-Server. Erst nach erfolgreichem `grep '  hue2lox-v1.0.0-rc.6.zip$' SHA256SUMS.txt | sha256sum --check -` wird entpackt und gestartet. Ein vorheriger Download auf Mac/PC oder Kopieren per `scp` ist nicht nötig. / Both guides use `curl` to download the ZIP and checksum directly to the Linux server. Extraction and startup happen only after successful verification. No prior download on your Mac/PC or transfer with `scp` is needed.

## Optional: im Browser herunterladen / Download in a browser

Lade die beiden oben verlinkten Assets in denselben Ordner. / Download both assets above into the same directory.

**Linux:**

```sh
grep '  hue2lox-v1.0.0-rc.6.zip$' SHA256SUMS.txt | sha256sum --check -
```

**macOS:**

```sh
grep '  hue2lox-v1.0.0-rc.6.zip$' SHA256SUMS.txt | shasum -a 256 --check -
```

**Windows PowerShell:**

```powershell
Get-FileHash .\hue2lox-v1.0.0-rc.6.zip -Algorithm SHA256
Get-Content .\SHA256SUMS.txt
```

Unter Windows den vollständigen Hash vergleichen. Nur bei Übereinstimmung fortfahren. / On Windows, compare the full hash. Continue only if it matches.

## Container und Beilagen / Container and accompanying materials

Images: `docker.io/dubctrl/hue2lox:1.0.0-rc.6` or / oder `ghcr.io/square-com-de/hue2lox:1.0.0-rc.6` (AMD64/ARM64). [Container guide](DOCKER.md).

Beim [RC6-Release](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.6) liegen zusätzlich `hue2lox-base-sources.tar.gz` (Quellen/Lizenzen), `container-evidence.tar.gz` (Inventare, SBOMs, Scans), `container-release.json` (Quellstand) und `container-digests.json` samt eigener Prüfsumme. / The release also contains corresponding sources/licenses, platform evidence/SBOMs/scans, source metadata and published image digests with their own checksum.

Die ZIP-Prüfbefehle oben wählen gezielt den ZIP-Eintrag aus der gemeinsamen Prüfsummenliste. Die zusätzlichen Beilagen müssen für die Installation nicht heruntergeladen werden. / The commands above select only the ZIP entry from the shared checksum list; installation does not require downloading the other materials.

## Published previous release / Veröffentlichte Vorversion

[RC5](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.5) remains published and unchanged at commit `45237512dcd18db9aaf3611173ce91ad8c654450`. [RC1](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.1) remains unchanged at `1d631cd1231d7cf004c6452c1fad0c262ff92bfd`. / RC5 und RC1 bleiben unter ihren ursprünglichen Tags unverändert.

RC6 is unpublished. Final package hashes and source commit are recorded in the local preparation handoff; future public downloads must match the release evidence before approval. Hardware and stable acceptance remain separate. / RC6 ist unveröffentlicht. Endgültige Paketprüfsummen und Quellcommit stehen in der lokalen Übergabe; öffentliche Downloads müssen später mit den Release-Nachweisen übereinstimmen. Hardware- und Stable-Abnahme bleiben separat.
