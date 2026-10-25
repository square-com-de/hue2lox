> **Historischer Stand / Historical record:** Aussagen, Befehle und offene Punkte unten gelten ausschließlich für den genannten damaligen Stand, nicht als aktuelle Installationsanleitung oder 1.0.3-Abnahme. / Statements, commands and pending checks below apply only to the recorded revision. [Aktuelle Dokumentation / current documentation](INDEX.md) · [1.0.3-Vorbereitung / preparation](PREPARATION-1.0.3.md).

# RC6 preparation / RC6-Vorbereitung

**Unpublished prepared candidate branch / Unveröffentlichter vorbereiteter Kandidatenbranch — 23.10.2026.** This document authorizes no tag, release, registry push or production deployment. / Dieses Dokument gibt keinen Tag, kein Release, keinen Registry-Push und kein Produktionsdeployment frei.

## Deutsch

Zielversion: `1.0.0-rc.6`. Funktionsbasis: main `9a1e3ebcb4fa61c391588a2b29b7e998ee1c3278`, identischer Dateibaum zum abgenommenen PR-Head `1b3e85af786c6527edc720b05da6f513957096ca`. Der genaue vorbereitete Kandidaten-Commit steht mit Pakethashes und Prüfläufen in der Vorbereitung-PR/lokalen Übergabe. Dieser RC6-Branch bleibt bis zur separaten Freigabe ungemergt. [Abnahme und Grenzen](DEPLOYMENT-ACCEPTANCE.md).

### Entwurf der Release Notes

- Gemeinsamer deutscher/englischer Installer mit Auswahl Docker oder nativ.
- Docker: festes veröffentlichtes Image von Docker Hub oder GHCR, alternativ lokaler Build; HTTP/HTTPS und Reverse-Proxy-Konfiguration bleiben verfügbar.
- Nativ, weiterhin experimentell: systemd-Dienst ohne Docker auf ausdrücklich geprüften Debian-/Ubuntu-/DietPi-Zielen; Update, Rollback und Deinstallation/Wiederinstallation mit Datenerhalt, einschließlich umask-077-Korrektur.
- Dokumentierter Docker-Updateweg mit separatem Kandidaten, vollständiger kalter Sicherung und manuellem exakten Image-/Daten-Rollback. Eigene Compose-Anpassungen und beliebige Datenmigrationen sind nicht pauschal abgedeckt.
- Lokale Discovery-Hilfe für macOS, Windows und Linux mit Kopierfunktion; kein automatisches Ausführen der Hilfebefehle.
- Sechs lokale Iconoir-Sidebar-Symbole samt MIT-Lizenz; eigene Installer-Meldungen in der gewählten DE/EN-Sprache. Ausgaben externer Werkzeuge behalten deren Sprache.
- Reale Ubuntu-/DietPi-Abnahme für Docker und nativ bestanden. Separate Hue-/Loxone-Hardwaretests sowie finale Paket-/Downloadprüfung bleiben offen. Kein Stable-Release.

### Vor Veröffentlichung abzuarbeiten

- [ ] Finalen Quellcommit festlegen; Quell-ZIP `hue2lox-v1.0.0-rc.6.zip` mit Archivordner `hue2lox-v1.0.0-rc.6/` und SHA256 erstellen und prüfen.
- [ ] Natives Archiv `hue2lox-1.0.0-rc.6-native.tar.gz` aus sauberem Checkout mit Manifest, exaktem Commit und eigener SHA256 erstellen; Paketinhalt sowie Neuinstallation und Wartung auf isolierten VMs prüfen. Natives Archiv ist für den nativen Weg zusätzlich zum Quell-ZIP bereitzustellen: ein ZIP ohne Git-Identität kann kein identifiziertes natives Paket selbst erzeugen.
- [x] Nativer Asset-Schritt implementiert: Der Publisher baut Quell-ZIP und natives Archiv aus demselben unveränderten Commit, prüft das native Manifest und nimmt beide in `SHA256SUMS.txt`, unveränderlichen Upload und anonyme Downloadprüfung auf. Der tatsächliche öffentliche RC6-Download bleibt bis zur Veröffentlichung ungeprüft.
- [ ] CI/Inventare/Scans und Quellen-/Lizenzbeilagen am endgültigen Commit prüfen; AMD64-/ARM64-Container vorbereiten. ARM64-Containerprüfung bedeutet keine native ARM-Freigabe.
- [x] Versionsbindung im separaten RC6-Kandidatenbranch auf `1.0.0-rc.6` vorbereitet und mit Compose/DE/EN-Anleitungen abgestimmt. Main bleibt bis zur separaten Merge-Freigabe auf RC5. Der Publisher lehnt eine Abweichung vom späteren Tag ab. Reihenfolge und letzte Prüfungen anhand [Registry-Runbook](GHCR-RELEASE.md) festlegen; RC6 erst nach vollständig erfolgreicher Veröffentlichung als installierbar ankündigen. Bis dahin für die neue Anwendung lokalen Build oder natives Paket verwenden.
- [ ] Nach separater Veröffentlichungsfreigabe feste RC6-Images in beiden Registries ausliefern, Digests/Quellenbeilagen dokumentieren und echte anonyme Downloads mit den geprüften Images vergleichen. Downloadanleitungen erst dann als verfügbar kennzeichnen; gleiche Registry-Imageinhalte sicherstellen.
- [ ] Finale ZIP-/native Downloadanleitungen DE/EN, Downloadtabellen, Release Notes und [Release-Übersicht](../RELEASE.md) auf tatsächlich vorhandene Assets umstellen. Bis dahin keine RC6-Downloadlinks als verfügbar darstellen.
- [ ] [Hardwareplan](ACCEPTANCE.md) am exakten Kandidaten abarbeiten oder klar als offen kennzeichnen. Vor Stable vollständige Freigabeentscheidung; RC6 ist keine Hardware- oder Stable-Freigabe.

RC1 `1d631cd1231d7cf004c6452c1fad0c262ff92bfd` und RC5 `45237512dcd18db9aaf3611173ce91ad8c654450` einschließlich Releases/Assets unverändert lassen. Kein `latest` vor Stable. Kein allgemeines RC1→RC6- oder Prototyp-Migrationsversprechen; angepasste Installationen separat prüfen. Keine neuen Schalter-/BWM-Eingänge, Statusrückmeldung oder LoxBerry-Plugin-Funktion in RC6 zugesichert.

## English

Target version: `1.0.0-rc.6`. Functional baseline: main `9a1e3ebcb4fa61c391588a2b29b7e998ee1c3278`, with the same tree as accepted PR head `1b3e85af786c6527edc720b05da6f513957096ca`. The preparation PR/local handoff records the exact prepared candidate commit, package hashes and checks. Keep this RC6 branch unmerged until separate approval. [Acceptance and limits](DEPLOYMENT-ACCEPTANCE.md).

### Draft release notes

- Shared German/English installer with Docker or native deployment selection.
- Docker: fixed published Docker Hub or GHCR image, or local build; HTTP/HTTPS and reverse-proxy configuration retained.
- Native remains experimental: systemd service without Docker on explicitly targeted Debian/Ubuntu/DietPi systems; update, rollback and uninstall/reinstall retaining data, including the umask-077 fix.
- Documented Docker update with a separate candidate, full cold backup and manual exact-image/data rollback. Custom Compose files and arbitrary data migrations are not generally covered.
- Local macOS/Windows/Linux discovery help with copy controls; helper commands are never run automatically.
- Six local Iconoir sidebar icons with MIT license; installer-owned output follows the chosen DE/EN language. External tools retain their own output language.
- Real Ubuntu/DietPi Docker and native acceptance passed. Hue/Loxone hardware tests and final package/download checks remain separate and open. This is not a stable release.

### Before publication

- [ ] Select final source commit; create and verify `hue2lox-v1.0.0-rc.6.zip`, root directory `hue2lox-v1.0.0-rc.6/`, and SHA256.
- [ ] Build `hue2lox-1.0.0-rc.6-native.tar.gz` from a clean checkout with manifest, exact commit and its own SHA256; verify package contents and fresh installation/maintenance on isolated VMs. Supply it alongside the source ZIP: a ZIP without Git identity cannot generate its own identified native package.
- [x] Native asset handling implemented: the publisher builds source ZIP and native archive from the same immutable commit, verifies the native manifest and includes both in `SHA256SUMS.txt`, immutable upload and anonymous download verification. Actual public RC6 downloads remain untested until publication.
- [ ] Check final-commit CI, inventories, scans, corresponding sources/licenses and AMD64/ARM64 container candidates. ARM64 container checks do not approve native ARM support.
- [x] Version `1.0.0-rc.6` prepared in the separate candidate branch and synchronized with Compose/DE/EN guides. Main retains RC5 until separate merge approval. The publisher rejects a mismatch against the eventual tag. Plan publication and final checks using the [registry runbook](GHCR-RELEASE.md); advertise RC6 as installable only after the entire publication succeeds. Use local builds or native packages for new app code meanwhile.
- [ ] After separate publication approval, publish fixed RC6 images to both registries, document digests/sources and verify actual anonymous downloads against tested images. Only then mark download instructions as available, ensuring matching image contents across registries.
- [ ] Align DE/EN ZIP/native download guides, tables, release notes and [release overview](../RELEASE.md) with real available assets. Do not advertise unavailable RC6 downloads.
- [ ] Execute the [hardware plan](ACCEPTANCE.md) on the exact candidate or leave it explicitly open. Stable approval is separate; RC6 alone is no hardware/stable approval.

Keep RC1 `1d631cd1231d7cf004c6452c1fad0c262ff92bfd` and RC5 `45237512dcd18db9aaf3611173ce91ad8c654450`, their releases and assets unchanged. No `latest` before stable. No general RC1→RC6/prototype migration guarantee; inspect customized deployments separately. RC6 does not promise switch/motion inputs, state feedback or a LoxBerry plugin.

## Isolierte Paketprüfung / Isolated package checks

Der Offline-Befehl erstellt ausschließlich lokale Dateien aus einem Commit; er benötigt weder Release-Event noch Registry-Zugang und ändert keinen Image-Pin. / This offline command creates local files from one commit, without release events, registry access or image-pin changes:

```sh
python3 scripts/release-image.py source-packages --version 1.0.0-rc.6 --output /tmp/hue2lox-rc6-packages
(cd /tmp/hue2lox-rc6-packages && sha256sum --check SHA256SUMS.txt)
python3 scripts/check-release-packages.py --version 1.0.0-rc.6
```

Der Ausgabeordner muss neu sein. Der letzte Befehl erstellt eigene temporäre Pakete, testet die entpackte ZIP-Anwendung und das native Archiv mit leerem Zustand über Loopback-HTTPS, Passwortwechsel und Prozessneustart und prüft die native Übergabe aus dem ZIP ohne Git-Metadaten. Kein systemd-Eingriff auf dem Host. / The output directory must be new. The last command creates its own temporary packages, tests the extracted source application and native archive over loopback HTTPS with empty state, password change and process restart, and checks native handoff from a ZIP without Git metadata. It does not modify host systemd.

CI prüft zusätzlich Docker aus dem Quell-ZIP und den nativen systemd-Lebenszyklus mit dem RC6-Archiv in vier netzlosen Wegwerfcontainern. Ein zusätzliches Entwicklungspaket testet Update/Rollback; das ist keine beliebige Schemamigration und keine Hardwareabnahme. / CI also tests Docker from the source ZIP and the RC6 native archive's systemd lifecycle in four disposable containers without networking. An additional development fixture exercises update/rollback; this is not arbitrary schema-migration or hardware approval.

Current technical handoff / Aktuelle technische Übergabe: [RC6 technical review](RC6-TECHNICAL-REVIEW.md) and [release-note draft](RELEASE-NOTES-RC6.md). Remaining unchecked release-package items refer to the final approved/published source; local candidate tests are recorded in the preparation PR. / Offene finale Paketpunkte beziehen sich auf den endgültig freigegebenen/veröffentlichten Stand; lokale Kandidatenprüfungen stehen in der Vorbereitungs-PR.

## Control defaults and existing installations / Steuerung und Bestandsinstallationen

Fresh Docker/native installations now set the three control flags to `1`; existing values remain unchanged on update/reinstall. Token and per-light capability enforcement are retained. Actual RC5 installer deployments stored `0`, whereas direct RC5 images without overrides defaulted to `1`. RC5 did not include native packages. The explicit offline correction tool changes only the three flags after operator opt-in, with a private settings backup. Docker requires container recreation, native requires a service restart. Full update/rollback and independent acceptance: [English procedure](RECOVERY-CONTROL.md), [deutscher Ablauf](RECOVERY-CONTROL.de.md). The final integrated candidate must pass renewed tests and independent practical acceptance; previous green runs do not approve this integration.

Neue Docker-/native Installationen setzen die drei Steuerungsflags auf `1`; Updates/Wiederinstallationen behalten bestehende Werte. Token- und Lampenfähigkeitsprüfung bleiben aktiv. Der reale RC5-Installer speicherte `0`, direkte RC5-Images ohne Overrides verwendeten `1`. RC5 enthielt kein natives Paket. Eine bewusste Freigabe erfolgt offline mit privater Sicherung, bei Docker anschließend durch Neuerstellen des Containers. Die endgültige Integration benötigt erneute Tests und unabhängige praktische Abnahme; frühere grüne Läufe ersetzen diese nicht.
