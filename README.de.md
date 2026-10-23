> **RC6 — Release Candidate:** [Release und Downloads](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.6). Vor der Installation den erfolgreichen Veröffentlichungsabschluss und Prüfsummen kontrollieren. Nativ bleibt experimentell. [RC5→RC6 und Steuerungsfreigabe](docs/RECOVERY-CONTROL.de.md).

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
- Auf main: gemeinsamer Docker-/nativer Installer und kopierbare lokale Discovery-Hilfe; in RC6 enthalten.

## So sieht es aus

![Befehle für Loxone im Hue2Lox-Webinterface](web/tutorial-commands.png)

*Beispielansicht mit Testdaten; die aktuelle Oberfläche ist kompakter. Weitere Abbildungen stehen in der [Loxone-Anleitung](docs/TUTORIAL.de.md).*

## Installieren und loslegen

Der gemeinsame **RC6-Installer** bietet Docker oder nativen Betrieb. Die Installationsanleitungen verwenden das versionierte RC6-Quell-ZIP und feste Images; Prüfsummen und den erfolgreichen Release-Abschluss kontrollieren.

| Installationsweg | Für wen? | Anleitung |
| --- | --- | --- |
| **Installer mit Docker** | Geführte Einrichtung; festes Release-Image nach Veröffentlichung oder lokaler Build. | [Installationsanleitung](INSTALL.de.md). Für Quelltests **lokalen Build** wählen. |
| **Docker / Compose** | Bestehende Container-Umgebung, auch mit Reverse Proxy. | [Container-Anleitung (Englisch)](docs/DOCKER.md). Festes RC6-Image verwenden. |
| **Nativ ohne Docker** | Experimenteller systemd-Betrieb auf den ausdrücklich geprüften amd64-Linux-Zielen. | [Native Anleitung](docs/INSTALL-NATIVE.md). Quell-ZIP und natives Archiv erforderlich. |

1. **Installer starten:** Die [Anleitung](INSTALL.de.md) beschreibt Voraussetzungen, Paketprüfung und Auswahl des Installationswegs. Mac oder Windows-PC dienen zur Bedienung des Linux-Servers.
2. **Hue2Lox einrichten:** Der Installer prüft Voraussetzungen; vorhandene funktionierende Docker-Installationen werden weiterverwendet. Neue Installationen erlauben die von der Lampe unterstützten Steuerfunktionen.
3. **Anmelden:** Angezeigte Webadresse öffnen, bei direktem HTTPS Zertifikat prüfen. Erstlogin `admin/admin`, danach Passwort ändern. Hardware erst bei der gesonderten Abnahme koppeln.
4. **Mit Loxone verbinden:** Für den späteren Hardwaretest beschreibt die [bebilderte Anleitung](docs/TUTORIAL.de.md) Befehle und XML für Loxone Config.

**[Installationsanleitung](INSTALL.de.md) · [RC6-Pakete und Prüfsummen](docs/DOWNLOADS.md) · [RC6-Release-Hinweise](docs/RELEASE-NOTES-RC6.md)**

**Bereits installiert?** Den [gesicherten RC5→RC6-Weg mit ausdrücklicher Steuerungsfreigabe](docs/RECOVERY-CONTROL.de.md) verwenden. Ein Update überschreibt keine bewusst gesperrten Funktionen. Für KI-Begleitung gibt es den [Installationsprompt](docs/AI-INSTALL.de.md).

## Feedback & Kontakt

Du hast Hue2Lox ausprobiert? Ich freue mich über dein Feedback – auch darüber, was gut funktioniert!

- **Per E-Mail, ohne GitHub-Konto:** [hue2lox@square-com.de](mailto:hue2lox@square-com.de)
- **Feedback oder Fragen auf GitHub:** [Feedback / Frage erstellen](https://github.com/square-com-de/hue2lox/issues/new?template=feedback_question.md) (GitHub-Konto erforderlich).
- **Fehler oder Verbesserungsideen:** [Passende Issue-Vorlage auswählen](https://github.com/square-com-de/hue2lox/issues/new/choose).

Bei Problemen helfen die Hue2Lox-Version, eine kurze Beschreibung und gegebenenfalls ein Screenshot oder die Fehlermeldung. Bitte keine Passwörter oder Tokens mitschicken. Sicherheitsprobleme vertraulich melden – siehe [Sicherheit](SECURITY.md).

## Release-Status und technische Hinweise

**Release Candidate: RC6. Kein Stable-Release.** PR #18 ist in main integriert. Die reale Ubuntu-26.04-/DietPi-13-Abnahme des gemeinsamen Installers, Docker/nativ sowie Update/Rollback und Datenerhalt ist bestanden. [Abnahme und Grenzen](docs/DEPLOYMENT-ACCEPTANCE.md). Die Nutzerabnahme bestätigt den TV-Strip über Lumitech (Farbe, Warm-/Kaltweiß, Dimmen, Aus), Szenenaktivierung und Datenerhalt nach Neustart; weitere Geräte sind damit nicht pauschal abgenommen. Der eigene Projektcode steht unter Apache 2.0.

Zielversion ist `1.0.0-rc.6`: Quell-ZIP, natives Archiv und später Docker-Hub-/GHCR-Images für AMD64/ARM64. Alle Teile müssen zum selben geprüften Quellstand gehören. Die versionierten Downloads und Images erst nach erfolgreichem Veröffentlichungsabschluss verwenden. Kein `latest` vor Stable. RC1 und RC5 bleiben bei dieser Vorbereitung unverändert; frühere Release-Nachweise ersetzen keine RC6-Abnahme.

Szenen erstellst du weiterhin in der Hue-App. Hue2Lox ruft sie über Loxone ab. Eine Synchronisierung des tatsächlichen Lampenzustands zurück in den Loxone-Lichtsteuerungsbaustein ist nicht vorgesehen.

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

## Tests und Sicherheit

[Automatische Prüfungen auf GitHub](https://github.com/square-com-de/hue2lox/actions/workflows/quality.yml) prüfen Quellcode, Übersetzungen, lokale HTTPS-Installation und einen isolierten Container. Ein grüner Lauf bestätigt nur diese Prüfungen, nicht den Betrieb mit jeder Hue-Lampe oder jedem Miniserver.

Keine Tokens, privaten Schlüssel, Zertifikats-Backups oder XML-Dateien mit echtem Token in Issues oder Pull Requests hochladen. Siehe [Sicherheit](SECURITY.md).

## Lizenzstatus

Hue2Lox steht unter der [Apache License 2.0](LICENSE). Sie erlaubt auch kommerzielle Nutzung und Weitergabe unter ihren Bedingungen. Eigener Code, Dokumentation und eigene Projektgrafiken sind einbezogen, soweit entsprechende Rechte bestehen. Drittanbieterbestandteile behalten ihre eigenen Bedingungen: [Lizenzen und Quellen](THIRD-PARTY-NOTICES.md) · [NOTICE](NOTICE).

Unabhängiges Projekt; keine offizielle Verbindung zu Philips Hue oder Loxone.

<p align="center"><strong>by <a href="https://square-com.de/">square | com</a></strong> · <a href="https://square-com.de/impressum/">Impressum / Legal notice</a></p>
