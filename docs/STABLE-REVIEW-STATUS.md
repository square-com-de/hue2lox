# Stable review status / Stable-Review-Stand — 23.10.2026

**Main: `9a1e3ebcb4fa61c391588a2b29b7e998ee1c3278`. RC5 veröffentlicht, RC6 in Vorbereitung; kein Stable. / RC5 published, RC6 being prepared; no stable release.**

PR #18 ist gemergt. Die [Deployment-Abnahme](DEPLOYMENT-ACCEPTANCE.md) am identischen Quellbaum ist bestanden. Die folgende Zuordnung aktualisiert den Bericht vom 20.10.2026; sie ist keine erneute unabhängige Vollprüfung aller ursprünglichen Befunde. / PR #18 is merged and deployment acceptance of the identical source tree passed. This disposition updates the 20 October report; it is not a new independent audit of every original finding.

| Befund / Finding | Aktueller Stand / Current disposition |
| --- | --- |
| B01 Paket-/Versionsbindung / Package identity | RC5 mit festen Downloads verfügbar; RC6-Commit, ZIP/native Assets und finale Downloadprüfung noch festzulegen. / Fixed RC5 downloads exist; final RC6 commit/assets/download acceptance pending. |
| B02 Hardwareabnahme / Hardware acceptance | Weiter offen gemäß [Plan](ACCEPTANCE.md); VM-Deployment-Abnahme ist davon getrennt. / Open under the plan; VM deployment evidence is separate. |
| B03 Hue-CA | Herkunftshinweise beibehalten; keine zusätzliche rechtliche Freigabe behauptet. / Provenance retained; no additional legal clearance claimed. |
| B04 öffentlich/RC/Lizenz / Public/RC/license | Öffentliches Projekt, veröffentlichter RC5, Apache 2.0 für eigene Bestandteile; Drittanbieterhinweise gelten. / Public project, published RC5, Apache 2.0 for original material; third-party notices apply. |
| B05 Prototyp-Dokumentation / Prototype docs | Historische Berichte behalten ihren Stand; aktuelle Guides trennen Standard-Installer und angepasste Compose-/Prototyp-Installationen. / Historical scope retained; current guides separate standard and customized deployments. |
| B06 Szenenheader / Scene headers | Kopierfelder/XML und Anleitungen verwenden sichtbares `\r\n`; tatsächlicher Loxone-Import bleibt Hardwareabnahme. / Copy fields/XML and guides use visible separators; actual Loxone import remains a hardware gate. |
| B07 Zertifikat/Restore / Certificates/recovery | Reale Deployment-Abnahme belegt Zertifikatserhalt und exaktes Backup/Rollback. Erneuerung, Adresswechsel und Miniserver-Vertrauen nicht dadurch pauschal freigegeben. / Real evidence covers retained certificates and exact backup/rollback, not blanket renewal/address-change/Miniserver trust approval. |
| B08 Teststand/Port / Test scope/port | Aktuelle Nachweise mit Commit getrennt von historischen Berichten verlinkt; Diagnose nutzt konfigurierten Port. / Current commit-specific evidence separated from historical reports; diagnostics use configured ports. |
| B09 Prototyp-Updater / Prototype updater | Dokumentierter Standard-Docker-Updateweg und native Wartung; keine automatische Prototyp-/RC1-Migration zugesichert. / Standard Docker update and native maintenance documented; no automatic prototype/RC1 migration guarantee. |
| B10 Cache/Deadline | Vorherige Robustheitskorrekturen integriert; isolierte Tests ersetzen keine Hardwarefreigabe. / Earlier robustness fixes integrated; isolated tests do not qualify hardware. |
| B11 Docker-Wartbarkeit / Docker maintenance | Gepinntes Basisimage, AMD64/ARM64-CI, Quellen-/Lizenzbeilagen und Vertrieb über Docker Hub/GHCR seit RC5. Neue RC6-Auslieferung noch offen. / Pinned base, architecture CI and sources/licenses; Docker Hub/GHCR distribution since RC5. RC6 delivery pending. |
| B12 Englisch / English | Gemeinsamer DE/EN-Installer, Anleitungen und eigene Helfermeldungen; reale zweisprachige Abnahme bestanden. Externe Werkzeugausgaben behalten ihre Sprache. / Shared bilingual installer/guides/helper output with real acceptance; external tools keep their language. |

## Verbleibend / Remaining

- [Hardware und Loxone](ACCEPTANCE.md), echte Windows-/Linux-LAN-Discovery, gegebenenfalls Zertifikatserneuerung/Adresswechsel im vorgesehenen Betriebsweg. / Hardware/Loxone, real Windows/Linux LAN discovery, and intended certificate renewal/address changes.
- [RC6-Vorbereitung](RC6-PREPARATION.md): endgültiger Commit, Pakete, Quellen-/Lizenz-/Scanprüfung und tatsächliche Downloads; danach separate Stable-Entscheidung. / Final commit, packages, sources/licenses/scans and actual downloads, then separate stable approval.
- Unterstützte Plattformen nur im belegten Umfang benennen. Native Installation bleibt experimentell und amd64-begrenzt. / Declare support within evidence; native remains experimental and amd64-only.

RC1 `1d631cd1231d7cf004c6452c1fad0c262ff92bfd` und RC5 `45237512dcd18db9aaf3611173ce91ad8c654450` einschließlich Tags, Releases und Assets bleiben unverändert. `admin/admin` bleibt bewusster Erstlogin mit Passwortwechsel. Keine Veröffentlichung durch diese Dokumentationsvorbereitung. / RC1/RC5 tags, releases and assets remain unchanged. The intentional initial login stays admin/admin with password change; documentation preparation publishes nothing.
