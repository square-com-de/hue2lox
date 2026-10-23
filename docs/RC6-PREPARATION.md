# RC6 preparation / RC6-Vorbereitung

**Unpublished draft / Unveröffentlichter Entwurf — 23.10.2026.** This document authorizes no tag, release, registry push or production deployment. / Dieses Dokument gibt keinen Tag, kein Release, keinen Registry-Push und kein Produktionsdeployment frei.

## Deutsch

Zielversion: `1.0.0-rc.6`. Funktionsbasis: main `9a1e3ebcb4fa61c391588a2b29b7e998ee1c3278`, identischer Dateibaum zum abgenommenen PR-Head `1b3e85af786c6527edc720b05da6f513957096ca`. Der endgültige RC6-Commit wird erst nach den Dokumentationsänderungen und erfolgreichen Prüfungen festgelegt. [Abnahme und Grenzen](DEPLOYMENT-ACCEPTANCE.md).

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
- [ ] Nativen Asset-Schritt im Veröffentlichungsablauf ergänzen oder einen separat geprüften Upload festlegen: Der aktuelle Container-Publisher erzeugt nur das Quell-ZIP und Containerbeilagen, kein natives Archiv. Vor RC6 den endgültigen Asset-Satz tatsächlich testen.
- [ ] CI/Inventare/Scans und Quellen-/Lizenzbeilagen am endgültigen Commit prüfen; AMD64-/ARM64-Container vorbereiten. ARM64-Containerprüfung bedeutet keine native ARM-Freigabe.
- [ ] Während dieser unveröffentlichten Vorbereitung `install/release-image.json` auf RC5 lassen. Erst im separat freigegebenen endgültigen Release-Commit muss der Pin zur Zielversion RC6 passen: Der Publisher lehnt eine Abweichung ab. Reihenfolge und letzte Prüfungen anhand [Registry-Runbook](GHCR-RELEASE.md) festlegen; RC6 erst nach vollständig erfolgreicher Veröffentlichung als installierbar ankündigen. Bis dahin für die neue Anwendung lokalen Build oder natives Paket verwenden.
- [ ] Nach separater Veröffentlichungsfreigabe feste RC6-Images in beiden Registries ausliefern, Digests/Quellenbeilagen dokumentieren und echte anonyme Downloads mit den geprüften Images vergleichen. Downloadanleitungen erst dann als verfügbar kennzeichnen; gleiche Registry-Imageinhalte sicherstellen.
- [ ] Finale ZIP-/native Downloadanleitungen DE/EN, Downloadtabellen, Release Notes und [Release-Übersicht](../RELEASE.md) auf tatsächlich vorhandene Assets umstellen. Bis dahin keine RC6-Downloadlinks als verfügbar darstellen.
- [ ] [Hardwareplan](ACCEPTANCE.md) am exakten Kandidaten abarbeiten oder klar als offen kennzeichnen. Vor Stable vollständige Freigabeentscheidung; RC6 ist keine Hardware- oder Stable-Freigabe.

RC1 `1d631cd1231d7cf004c6452c1fad0c262ff92bfd` und RC5 `45237512dcd18db9aaf3611173ce91ad8c654450` einschließlich Releases/Assets unverändert lassen. Kein `latest` vor Stable. Kein allgemeines RC1→RC6- oder Prototyp-Migrationsversprechen; angepasste Installationen separat prüfen. Keine neuen Schalter-/BWM-Eingänge, Statusrückmeldung oder LoxBerry-Plugin-Funktion in RC6 zugesichert.

## English

Target version: `1.0.0-rc.6`. Functional baseline: main `9a1e3ebcb4fa61c391588a2b29b7e998ee1c3278`, with the same tree as accepted PR head `1b3e85af786c6527edc720b05da6f513957096ca`. Select the final RC6 commit after documentation changes and successful checks. [Acceptance and limits](DEPLOYMENT-ACCEPTANCE.md).

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
- [ ] Add native-asset handling to publication or define a separately verified upload: the current container publisher creates the source ZIP and container materials, not a native archive. Test the actual final asset set before RC6.
- [ ] Check final-commit CI, inventories, scans, corresponding sources/licenses and AMD64/ARM64 container candidates. ARM64 container checks do not approve native ARM support.
- [ ] During this unpublished preparation keep `install/release-image.json` on RC5. The separately approved final release commit must pin RC6 to match its tag; the publisher rejects mismatches. Plan publication and final checks using the [registry runbook](GHCR-RELEASE.md); advertise RC6 as installable only after the entire publication succeeds. Use local builds or native packages for new app code meanwhile.
- [ ] After separate publication approval, publish fixed RC6 images to both registries, document digests/sources and verify actual anonymous downloads against tested images. Only then mark download instructions as available, ensuring matching image contents across registries.
- [ ] Align DE/EN ZIP/native download guides, tables, release notes and [release overview](../RELEASE.md) with real available assets. Do not advertise unavailable RC6 downloads.
- [ ] Execute the [hardware plan](ACCEPTANCE.md) on the exact candidate or leave it explicitly open. Stable approval is separate; RC6 alone is no hardware/stable approval.

Keep RC1 `1d631cd1231d7cf004c6452c1fad0c262ff92bfd` and RC5 `45237512dcd18db9aaf3611173ce91ad8c654450`, their releases and assets unchanged. No `latest` before stable. No general RC1→RC6/prototype migration guarantee; inspect customized deployments separately. RC6 does not promise switch/motion inputs, state feedback or a LoxBerry plugin.
