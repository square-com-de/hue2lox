# Dokumentation / Documentation

**Stand / status:** 1.0.2 ist veröffentlicht; 1.0.3 ist unveröffentlichte Vorbereitung. Die Versionsbefehle der Kandidaten-Dokumentation erst nach dessen Veröffentlichung verwenden. / 1.0.2 is published; 1.0.3 is unreleased preparation. Use candidate-version download/image commands only after publication.

## Einstieg und Bedienung / Getting started

| Thema / Topic | Deutsch | English |
| --- | --- | --- |
| Übersicht / Overview | [README](../README.de.md) | [README](../README.md) |
| Docker, Podman oder nativer Installer / Installation choice | [Installation](../INSTALL.de.md) | [Installation](../INSTALL.md) |
| Container, Speicher, HTTP/HTTPS und Traefik | [Einrichtung](CONTAINER-SETUP.de.md) | [Setup](CONTAINER-SETUP.md) |
| Container-Image und Podman Desktop | [DE-Einstieg](CONTAINER-SETUP.de.md) | [Image / Podman guide](DOCKER.md) |
| Native Installation und Wartung | [Nativ](INSTALL-NATIVE.md) | [Native](INSTALL-NATIVE.en.md) |
| Bedienung und Fehlersuche / Operation | [Handbuch](MANUAL.de.md) | [Manual](MANUAL.md) |
| Loxone-HTTP-Ausgänge und XML | [Tutorial](TUTORIAL.de.md) | [Tutorial](TUTORIAL.md) |
| Szenen Ein/Aus / Scene on/off | [Szenen](features/SCENE-SWITCH.de.md) | [Scenes](features/SCENE-SWITCH.md) |
| Update und Rollback | [Docker](UPDATE-DOCKER.de.md) | [Docker](UPDATE-DOCKER.md) |
| Ältere direkte Installer-Zertifikate / Legacy installer TLS | [Wartung](MAINTENANCE.de.md) | [Maintenance](MAINTENANCE.md) |
| Alte Steuerungssperren bewusst korrigieren / Disabled-control recovery | [Recovery](RECOVERY-CONTROL.de.md) | [Recovery](RECOVERY-CONTROL.md) |
| Tatsächlicher Plattformumfang / Runtime scope | [Runtime](RUNTIME-SUPPORT.de.md) | [Runtime](RUNTIME-SUPPORT.md) |

## Aktueller Kandidat und Freigabe / Candidate and approval

[1.0.3-Vorbereitung](PREPARATION-1.0.3.md) · [DE/EN-Patch-Hinweise](RELEASE-NOTES-1.0.3.md) · [Downloadnamen und Prüfsummen](DOWNLOADS.md) · [Changelog](../CHANGELOG.md) · [Abnahmeplan](ACCEPTANCE.md) · [Offene Hardwaretests #42](https://github.com/square-com-de/hue2lox/issues/42).

Technische Tests, praktische Browser-/VM-Abnahme, Hardwarewirkung, Veröffentlichung und Produktionsrollout sind getrennte Nachweise. / Technical tests, browser/VM acceptance, hardware effects, publication and production rollout are distinct evidence scopes.

## Technik und Quellen / Technical reference and sources

- [Architektur und Datenhaltung](CONTAINER.md), [Login/Token/XML](ADMIN.md), [Bridge-Kopplung](BRIDGES.md), [lokale Suche](DISCOVERY.md), [Szenenschnittstellen](SCENES.md), [HTTP-Monitor](MONITOR.md), [Weboberfläche](WEB.md).
- [Entwicklung / contributing](../CONTRIBUTING.md), [DE/EN-Technik](I18N.md), [Release-Runbook](GHCR-RELEASE.md), [Quellen-/Inventarprüfung](IMAGE-COMPLIANCE.md), [Container-Quellenbeilage](CONTAINER-SOURCES.md).
- [Sicherheit / security](../SECURITY.md), [Apache-2.0-Lizenz](../LICENSE), [NOTICE](../NOTICE), [Drittanbietertexte / third-party notices](../THIRD-PARTY-NOTICES.md), [Modellkatalog](../catalog/README.md).
- [Eigene Lampensymbole und Iconoir-Navigation](ICONS.md), [datierte Modell-/Symbolrecherche](ICON-RESEARCH.md), [Grafikherkunft](LOGO.md).
- [Lessons learned DE](LESSONS-LEARNED.de.md) / [EN](LESSONS-LEARNED.md): historische Fehlerursachen mit aktueller Einordnung; keine Ersatz-Abnahme eines neuen Kandidaten.

## Historische Berichte / Historical records

Die folgenden Texte bleiben ihrem ursprünglichen Datum, Commit und Testumfang zugeordnet. Damalige „offene“ Punkte sind keine aktuelle Gesamtcheckliste. Historische Befehle sind keine allgemeine Installationsanleitung. / These retain their original date, commit and scope. Their pending items are not the current overall checklist; historical commands are not general installation instructions.

| Stand / Scope | Bericht / Record |
| --- | --- |
| 1.0.2-Veröffentlichung und Software-Rollout | [Abgeschlossenes Issue #51](https://github.com/square-com-de/hue2lox/issues/51) · [Release-Hinweise](RELEASE-NOTES-1.0.2.md) |
| 1.0.1 öffentlicher Container, frisches OS, Flags, Portainer | [Abschluss](acceptance/FINAL-CONTAINER-2026-10-25.md) · [frühere Teilabnahme](CONTAINER-ACCEPTANCE-1.0.1.md) · [Proxmox](acceptance/PROXMOX-1.0.1.md) · [Podman Desktop](acceptance/DESKTOP-1.0.1.md) · [Release-Hinweise](RELEASE-NOTES-1.0.1.md) |
| 1.0.0 | [Release-Hinweise](RELEASE-NOTES-1.0.0.md) |
| PR #18, Ubuntu-/DietPi-Deployment | [Abnahme 23.10.2026](DEPLOYMENT-ACCEPTANCE.md) · [frühere native Debian-Abnahme](NATIVE-VM-ACCEPTANCE.md) |
| RC6-Vorbereitung | [Vorbereitung](RC6-PREPARATION.md) · [Technischer Bericht](RC6-TECHNICAL-REVIEW.md) · [Release-Hinweise](RELEASE-NOTES-RC6.md) · [damaliger Review-Stand](STABLE-REVIEW-STATUS.md) |
| Frühe Prototypen | [Erster HTTPS-Prototyp](INITIAL-PROTOTYPE.md) · [erste lokale Tests](INITIAL-TEST-RESULTS.md) · [Status-Prototyp](STATUS-IMPLEMENTATION.txt) · [Schalten/Dimmen](CONTROL.md) · [RGB](COLOR.md) · [Weiß/Lumitech](WHITE.md) · [historischer Testverlauf](TEST-RESULTS.md) |
