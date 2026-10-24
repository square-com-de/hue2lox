<p align="center"><a href="README.de.md">Deutsch</a> | <a href="README.md">English</a></p>

<p align="center">
  <img src="web/hue2lox-logo.png" width="360" alt="Hue2Lox – unser Oktopus hält den Schriftzug">
</p>
<h1 align="center">Hue im Griff. Mit Hue2Lox.</h1>
<p align="center">Philips Hue mit Loxone verbinden – lokal, übersichtlich und mit acht helfenden Armen.</p>
<p align="center"><a href="docs/MANUAL.de.md">Handbuch</a> · <a href="INSTALL.de.md">Installation</a></p>

**Deine Hue-Lampen in Loxone. Einfach eingebunden. Komfortabel gesteuert.**

Bringe deine Philips-Hue-Lampen und Szenen in deine Loxone-Steuerung – ohne Programmierung und mit automatisch erzeugten Vorlagen für Loxone Config.

Hue2Lox liest die Lampen und Szenen deiner Bridges ein und bietet die passenden Steuerungsarten an: Schalten, Dimmen, Farbe und Weißtemperatur. Wähle deine Geräte aus und übernimm die fertigen Befehle per Kopieren oder XML-Import in Loxone Config.

Alles bleibt übersichtlich: mehrere Bridges, deine Lampen und Szenen in einer Oberfläche. Hue2Lox läuft lokal auf deinem Linux-Server, lässt sich auf Deutsch oder Englisch bedienen und benötigt im laufenden Betrieb kein Cloudkonto.

## Was Hue2Lox kann

- Mehrere Hue Bridges koppeln und Lampen sowie Hue-Szenen einlesen.
- Ein/Aus, Dimmen, RGB und Weißtemperatur passend zu den Lampenfähigkeiten anbieten.
- Lampen und Szenen nach Bridge und Raum filtern, ignorieren und wieder einblenden.
- Loxone-HTTP-Befehle kopieren oder eine Auswahl als XML exportieren.
- Loxone-Anfragen mit einem zeitlich begrenzten, bereinigten HTTP-Monitor prüfen.
- Lokal über HTTPS verwalten – ohne Cloudkonto für den laufenden Betrieb.
- Gemeinsamer Docker-/nativer Installer und lokale Suchhilfen für macOS, Windows und Linux.
- Szenen als digitale Ein/Aus-Lichtkreise mit automatisch zugeordneten, eindeutig passenden Gruppen.

## So sieht es aus

![Befehle für Loxone im Hue2Lox-Webinterface](web/tutorial-commands.png)

*Beispielansicht mit Testdaten; die aktuelle Oberfläche ist kompakter. Weitere Abbildungen stehen in der [Loxone-Anleitung](docs/TUTORIAL.de.md).*

## Installieren und loslegen

**Bevorzugt: Container mit Docker Compose auf einer Linux-VM**, beispielsweise unter Proxmox. Proxmox stellt die VM bereit; Docker Engine und Compose laufen innerhalb von Linux. Ein privilegierter LXC wird dadurch nicht als Installationsziel freigegeben.

[Runtime- und Versionsstatus](docs/RUNTIME-SUPPORT.de.md) · [Speicher, Anmeldung, Netzwerk und TLS](docs/CONTAINER-SETUP.de.md)

| Installationsweg | Einordnung | Anleitung |
| --- | --- | --- |
| **Docker Compose auf Linux-VM** | Bevorzugter Containerweg, feste Version **1.0.1**, dauerhaftes Volume und zur Browseradresse passende Konfiguration. | [Container-Anleitung](docs/DOCKER.md#docker-compose) · [Einrichtung DE](docs/CONTAINER-SETUP.de.md) |
| Geführter Docker-Installer | Alternative für geführte Einrichtung mit direktem HTTPS; festes Image oder lokaler Build. | [Linux-Installer](INSTALL.de.md) |
| Podman Desktop auf macOS ARM64 | Separat geprüfter lokaler Testweg, keine pauschale LAN-/Proxmox-Freigabe. | [Geprüfter Ablauf und Grenzen](docs/DOCKER.md#podman-desktop-on-macos) |
| Nativ ohne Docker | Experimentelle Alternative für ausdrücklich geprüfte amd64-systemd-Ziele. | [Native Anleitung](docs/INSTALL-NATIVE.md) |

1. **Container vorbereiten:** Die [Compose-Schnellstartdatei](docker/compose.quickstart.yaml) nach der [kurzen Anleitung](docs/CONTAINER-SETUP.de.md#schnellstart-docker-auf-einem-linux-server) starten. Docker/Compose müssen vorhanden und Port 18443 frei sein. Browserlogin und Datenerhalt sind unabhängig geprüft; [genauer Testumfang und Grenzen](docs/CONTAINER-ACCEPTANCE-1.0.1.md).
2. **Anmelden:** Angezeigte HTTP-/HTTPS-Adresse verwenden; Port 8443 allein bedeutet kein HTTPS. Frische Daten: `admin/admin`; erhaltene Daten: bisheriges Passwort. Bei HTTPS das Zertifikat prüfen.
3. **Bridge einrichten:** Container muss die Bridge im LAN erreichen können. Fehlende Multicast-Suche und fehlender direkter Netzwerkzugriff sind unterschiedliche Probleme; eine manuelle IP umgeht keine Netzsperre.
4. **Mit Loxone verbinden:** [Bebilderte Anleitung](docs/TUTORIAL.de.md) für Befehle und XML. Für Szenen-AUS die neuen digitalen Befehle übernehmen; alte Recall-Ausgänge bleiben unverändert.

**Bereits installiert?** [Backup, Update und Rollback](docs/UPDATE-DOCKER.de.md) statt Neuinstallation. `pull` und `restart` ersetzen keinen bestehenden Container. Eigene Portainer-/Compose-Stacks getrennt behandeln; keine bewusst gesperrten Funktionen oder gespeicherten Passwörter überschreiben. [1.0.1-Download/Prüfsummen](docs/DOWNLOADS.md) · [Release-Hinweise](docs/RELEASE-NOTES-1.0.1.md). Ein LoxBerry-Plugin gibt es noch nicht.

## Feedback & Kontakt

Du hast Hue2Lox ausprobiert? Ich freue mich über dein Feedback – auch darüber, was gut funktioniert!

- **Per E-Mail, ohne GitHub-Konto:** [hue2lox@square-com.de](mailto:hue2lox@square-com.de)
- **Feedback oder Fragen auf GitHub:** [Feedback / Frage erstellen](https://github.com/square-com-de/hue2lox/issues/new?template=feedback_question.md) (GitHub-Konto erforderlich).
- **Fehler oder Verbesserungsideen:** [Passende Issue-Vorlage auswählen](https://github.com/square-com-de/hue2lox/issues/new/choose).

Bei Problemen helfen die Hue2Lox-Version, eine kurze Beschreibung und gegebenenfalls ein Screenshot oder die Fehlermeldung. Bitte keine Passwörter oder Tokens mitschicken. Sicherheitsprobleme vertraulich melden – siehe [Sicherheit](SECURITY.md).

## Release-Status und technische Hinweise

**Stable 1.0.1.** Enthält den gemeinsamen Installer, lokale Suchhilfen und Szenen-Ein/Aus. Die Nutzerabnahme umfasst TV-Strip-Lumitech-Farbe, warmes/kaltes Weiß, Dimmen, AUS, Szenenwechsel und abschließendes AUS. Docker-/native Lebenszyklustests auf Ubuntu und DietPi prüfen Neustart, Update/Rollback und Datenerhalt. Siehe [Release-Hinweise und Grenzen](docs/RELEASE-NOTES-1.0.1.md).

Versioniertes ZIP oder `1.0.1`-Images von Docker Hub/GHCR verwenden (AMD64/ARM64). `latest` folgt dem neuesten erfolgreich geprüften Stable-Release; für reproduzierbare Installationen `1.0.1` fest einstellen. Nativ bleibt experimentell und auf amd64 beschränkt. Frühere RC-Pakete bleiben unverändert.

Szenen in der Hue-App erstellen und bearbeiten. [Szenen Ein/Aus](docs/features/SCENE-SWITCH.de.md) aktiviert eine Szene und schaltet ihre zugeordnete Gruppe aus. Bestehende Recall-Befehle bleiben nutzbar; für AUS die neuen digitalen Befehle importieren. Eine Rückmeldung des tatsächlichen Lampenzustands in den Loxone-Lichtbaustein ist nicht enthalten.

**Bestehende Installationen:** Für Standard-Docker-Installationen gilt der [gesicherte Update-/Rollbackweg](docs/UPDATE-DOCKER.de.md), für native Installationen die [native Wartung](docs/INSTALL-NATIVE.md). Angepasste Compose-/Prototyp-Installationen separat prüfen. Eine Neuinstallation ist kein allgemeiner Updater.

Änderungen stehen im [Changelog](CHANGELOG.md), der [historischen RC6-Vorbereitung](docs/RC6-PREPARATION.md) und den [Release-Hinweisen](RELEASE.md).

## Dokumentation

| Thema | Einstieg |
| --- | --- |
| Bedienung, Fehlerbehebung, Backup | [Handbuch](docs/MANUAL.de.md) |
| Nativer Installer und VM-Nachweise | [Native Anleitung](docs/INSTALL-NATIVE.md) · [Aktuelle VM-Abnahme](docs/DEPLOYMENT-ACCEPTANCE.md) |
| Neue Testinstallation | [Installation](INSTALL.de.md) |
| Fertiges Docker-Image (AMD64/ARM64) | [Container-Anleitung (Englisch)](docs/DOCKER.md) |
| HTTP-Ausgänge und XML in Loxone | [Bebilderte Anleitung](docs/TUTORIAL.de.md) |
| Architektur und Container | [Technik](docs/CONTAINER.md) |
| Qualitätsprüfungen und Mitarbeit | [Entwicklung](CONTRIBUTING.md) |
| Was wir gemeinsam testen | [Abnahmeplan](docs/ACCEPTANCE.md) |
| Quellen, Icons und Lizenzstatus | [Drittanbieterhinweise](THIRD-PARTY-NOTICES.md) |
| Release-Stand und Grenzen | [Release-Hinweise](RELEASE.md) |

**Nach einem Update:** Neuerstellen statt nur Neustarten; vorhandene Daten behalten ihr Passwort und absichtlich gesetzte Steuerungssperren. Bei RC5-Altbestand zuerst die [gezielte Recovery-Anleitung](docs/RECOVERY-CONTROL.de.md) lesen. [Lessons Learned und offene Freigabekriterien](docs/LESSONS-LEARNED.de.md).

## Tests und Sicherheit

[Automatische Prüfungen auf GitHub](https://github.com/square-com-de/hue2lox/actions/workflows/quality.yml) prüfen Quellcode, Übersetzungen, lokale HTTPS-Installation und einen isolierten Container. Ein grüner Lauf bestätigt nur diese Prüfungen, nicht den Betrieb mit jeder Hue-Lampe oder jedem Miniserver.

Keine Tokens, privaten Schlüssel, Zertifikats-Backups oder XML-Dateien mit echtem Token in Issues oder Pull Requests hochladen. Siehe [Sicherheit](SECURITY.md).

## Lizenzstatus

Hue2Lox steht unter der [Apache License 2.0](LICENSE). Sie erlaubt auch kommerzielle Nutzung und Weitergabe unter ihren Bedingungen. Eigener Code, Dokumentation und eigene Projektgrafiken sind einbezogen, soweit entsprechende Rechte bestehen. Drittanbieterbestandteile behalten ihre eigenen Bedingungen: [Lizenzen und Quellen](THIRD-PARTY-NOTICES.md) · [NOTICE](NOTICE).

Unabhängiges Projekt; keine offizielle Verbindung zu Philips Hue oder Loxone.

<p align="center"><strong>by <a href="https://square-com.de/">square | com</a></strong> · <a href="https://square-com.de/impressum/">Impressum / Legal notice</a></p>
