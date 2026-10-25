# Hue2Lox 1.0.2

Use versioned assets only after the publication workflow succeeds. / Versionierte Dateien erst nach erfolgreichem Veröffentlichungsworkflow verwenden.

## Deutsch

Die Sidebar zeigt die tatsächlich installierte Paket-/Buildversion statt „Version2“. Container erhalten Version und Quellcommit beim Build; PR-/Entwicklungsbuilds werden ausdrücklich gekennzeichnet. Native Pakete verwenden ihr Manifest; fehlende/ungültige Metadaten behaupten keine Releaseversion.

Enthalten bleiben alle bisherigen Funktionen: Szenen-Ein/Aus über die zugeordnete Hue-Gruppe mit Schutz gegen überholtes AUS, reiner Szenenaufruf, RGB/Lumitech/Weiß/Dimmen, gemeinsamer Docker-/nativer Installer, lokale Discovery-Hilfe und DE/EN-Oberfläche. Keine Zustandsrückmeldung an Loxone und kein LoxBerry-Plugin hinzugefügt.

Docker auf Linux ist der bevorzugte Weg. Nativ bleibt experimentell/amd64. Podman bleibt auf den konkret dokumentierten Desktopumfang begrenzt; eine funktionierende Anmeldung beweist keinen LAN-/Bridge-Zugriff. Die historischen1.0.1-Abnahmen bleiben ihrem tatsächlichen Artefakt zugeordnet. Neue1.0.2-Registry-/VM-/Produktionsnachweise müssen am tatsächlich ausgelieferten Digest erfolgen; Hardware bedient der Nutzer.

Vor Updates Datenvolume, Compose/env und bisherige exakte Image-ID kalt sichern. Dasselbe Volume und bewusst deaktivierte Steuerungsflags behalten. Bei Problemen zusammengehörigen alten Image-/Daten-/Konfigurationsstand wiederherstellen. [Update und Rollback](UPDATE-DOCKER.de.md).

Bekannter Tooling-Follow-up: [Issue44](https://github.com/square-com-de/hue2lox/issues/44), Offline-Quell-ZIP-Reproduktion unterUTC durchführen. Bestehende Releases/RCs unverändert lassen.

## English

The sidebar displays the installed package/build version instead of “Version2”. Container builds carry an explicit version and source revision; development builds are labelled honestly. Native packages use their own manifest; missing/malformed metadata never invents a release.

Existing scene on/off group control and stale-OFF protection, recall-only scenes, RGB/Lumitech/white/dimming, the shared installer, local discovery help and DE/EN interface are retained. No Loxone state feedback or LoxBerry plugin is added.

Linux Docker is preferred; native remains experimental/amd64. Podman claims remain limited to documented evidence. Historical 1.0.1 results are not1.0.2 artifact acceptance. Actual new registry/VM/production checks must use the delivered digest; hardware actions remain human-owned.

Keep the same volume, disabled flags and credentials; take a cold data/configuration/exact-image backup and restore the matching old set if needed. [Update and rollback](UPDATE-DOCKER.md). Offline ZIP reproduction still requiresUTC ([Issue44](https://github.com/square-com-de/hue2lox/issues/44)); old releases remain immutable.
