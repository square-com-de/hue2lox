# Hue2Lox 1.0.0 — Stable

Released / Veröffentlicht: 2026-10-24.

[Release, ZIP, native archive and checksums](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0) · [English installation](../INSTALL.md) · [Deutsche Installation](../INSTALL.de.md)

## English

The first stable release connects Philips Hue lights and scenes to Loxone with a local German/English interface, generated HTTP commands and XML templates.

- Switching, dimming, RGB and Lumitech/white-temperature controls for supported lights are enabled on fresh installations.
- Scenes now offer **On/off** directly. A unique group with exactly the scene's lights is assigned automatically. No confirmation checkbox or separate Save button. Other group selections save immediately; extra lamps are named before selection.
- ON recalls the scene; OFF switches off the assigned group. Existing recall outputs keep working. Import the new digital commands/XML to use OFF; existing Loxone projects are never rewritten automatically.
- Shared Docker/native installer, fixed images from Docker Hub/GHCR or local build, direct HTTPS or a reverse proxy, and local discovery helpers for macOS, Windows and Linux.
- Native deployment remains **experimental, amd64-only**, on the documented Debian/Ubuntu/DietPi versions. Container images support AMD64 and ARM64; this does not certify every device/platform combination.

### Acceptance and limits

The user confirmed scene changes and final OFF on 24 October 2026 in the Portainer PR45 test stack. Its application/UI correspond to PR head `0b79e37783c7252db6fafd13bf6702394db2a123`; the deployed source `31079cabb50da489c7ed9fcfd51d6a155d042c72` differs only in documentation. 325 isolated tests, 27 independent scene tests and all 11 PR checks passed. Earlier acceptance covers TV-strip Lumitech color/white/dimming/off, login/password changes, restart persistence and Docker/native update/rollback on Ubuntu/DietPi. These are scoped results, not blanket hardware approval.

No actual-light-state feedback to the Loxone Lighting Controller. After a service restart or uncertain result, send ON before OFF. Overlapping active groups and ambiguous command sequences have documented limits: [scene on/off](features/SCENE-SWITCH.md). Mac/Windows container networking can limit multicast discovery; the local helpers or manual IP entry remain available.

### Update

Back up data, secrets, certificates, Compose/env and the exact old image before upgrading. Use the [Docker update guide](UPDATE-DOCKER.md) or [native maintenance](INSTALL-NATIVE.en.md); inspect custom/prototype stacks separately. Preserve passwords, tokens, bridge configuration and intentionally disabled controls. Published RC1–RC6 remain unchanged. Existing installations do not update automatically.

## Deutsch

Das erste stabile Release verbindet Philips-Hue-Lampen und Szenen mit Loxone: lokale deutsche/englische Oberfläche, fertige HTTP-Befehle und XML-Vorlagen.

- Schalten, Dimmen, RGB und Lumitech/Weißtemperatur sind bei Neuinstallationen für passende Lampen direkt aktiviert.
- Szenen bieten **Ein/Aus** direkt an. Genau eine Gruppe mit denselben Lampen wird automatisch zugeordnet. Kein Bestätigungshaken und kein zusätzlicher Speichern-Knopf. Andere Gruppen werden unmittelbar gespeichert; zusätzliche Lampen sind vor der Auswahl benannt.
- EIN aktiviert die Szene, AUS schaltet die zugeordnete Gruppe aus. Alte Recall-Ausgänge bleiben kompatibel. Für AUS die neuen digitalen Befehle/XML übernehmen; bestehende Loxone-Projekte werden nicht automatisch geändert.
- Gemeinsamer Docker-/nativer Installer, feste Images von Docker Hub/GHCR oder lokaler Build, direktes HTTPS oder Reverse Proxy sowie lokale Suchhilfen für Mac, Windows und Linux.
- Nativ bleibt **experimentell und auf amd64 beschränkt**, für die dokumentierten Debian-/Ubuntu-/DietPi-Versionen. Container unterstützen AMD64/ARM64; dies ist keine pauschale Gerätefreigabe.

### Abnahme und Grenzen

Szenenwechsel und abschließendes AUS wurden am 24.10.2026 vom Nutzer im Portainer-Teststack bestätigt. App/UI entsprechen PR-Head `0b79e37783c7252db6fafd13bf6702394db2a123`; der bereitgestellte Stand `31079cabb50da489c7ed9fcfd51d6a155d042c72` unterscheidet sich nur in der Dokumentation. 325 isolierte Tests, 27 unabhängige Szenentests und alle 11 PR-Prüfungen sind bestanden. Frühere Abnahmen umfassen TV-Strip-Lumitech-Farbe/Weiß/Dimmen/AUS, Passwortwechsel, Neustart sowie Docker-/native Updates und Rollback auf Ubuntu/DietPi.

Keine Rückmeldung des echten Lampenzustands an den Loxone-Lichtbaustein. Nach Dienstneustart oder unklarem Ergebnis zuerst EIN senden. Grenzen bei überlappenden Gruppen und mehrdeutigen Befehlsfolgen: [Szenen Ein/Aus](features/SCENE-SWITCH.de.md). Container-Netzwerke auf Mac/Windows können Multicast begrenzen; lokale Suchhilfe oder manuelle IP verwenden.

### Update

Vorher Daten, Secrets, Zertifikate, Compose/env und exaktes altes Image sichern. [Docker-Update](UPDATE-DOCKER.de.md) oder [native Wartung](INSTALL-NATIVE.md) verwenden; angepasste Prototyp-Stacks separat prüfen. Passwörter, Tokens, Bridges und bewusst deaktivierte Funktionen erhalten. RC1–RC6 bleiben unverändert. Laufende Installationen aktualisieren sich nicht automatisch.

## Release materials / Release-Beilagen

One exact release commit binds the ZIP, native archive, checksums, image/source/license materials and both registry images. The workflow publishes immutable version assets and verifies anonymous downloads and both platform pulls before promoting `latest`. The exact source and image digests are recorded in `container-release.json` and `container-digests.json` attached to the release.

Ein exakter Release-Commit bindet ZIP, natives Archiv, Prüfsummen, Quellen-/Lizenzbeilagen und beide Registry-Images. Der Workflow prüft öffentliche Downloads und beide Plattformen vor der Freigabe von `latest`. Quellstand und Digests stehen in den Release-Dateien `container-release.json` und `container-digests.json`.
