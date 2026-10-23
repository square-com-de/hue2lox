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
- Auf main: gemeinsamer Docker-/nativer Installer und kopierbare lokale Discovery-Hilfe; RC6 noch unveröffentlicht.

## So sieht es aus

![Befehle für Loxone im Hue2Lox-Webinterface](web/tutorial-commands.png)

*Beispielansicht mit Testdaten; die aktuelle Oberfläche ist kompakter. Weitere Abbildungen stehen in der [Loxone-Anleitung](docs/TUTORIAL.de.md).*

## Installieren und loslegen

Wähle den Installationsweg, der zu dir passt:

| Installationsweg | Für wen? | Status und Anleitung |
| --- | --- | --- |
| **Installer mit Docker** | Für Einsteiger: RC5 baut lokal; main bietet ein festes Image oder lokalen Build. | **In RC5 verfügbar** · [Installationsanleitung](INSTALL.de.md) |
| **Docker / Compose mit fertigem Image** | Für bestehende Container-Umgebungen, auch hinter einem Reverse Proxy wie Traefik. | **In RC5 verfügbar** · [Container-Anleitung (Englisch)](docs/DOCKER.md) |
| **Python-Installer, ohne Docker** | Für experimentellen direkten Dienstbetrieb auf ausdrücklich unterstützten Linux-Testsystemen. | **Experimentell auf main** · [Gemeinsamer Installer und native Anleitung](docs/INSTALL-NATIVE.md). Nicht in RC5 enthalten. |

Wähle den geführten Installer oder nutze direkt das versionierte Docker-Hub- oder GHCR-Image. Der Entwicklungsinstaller bietet Docker oder nativen Betrieb; der native Weg ist experimentell und gehört nicht zu RC5. Für Docker bietet der Entwicklungsinstaller ein festes Release-Image oder einen lokalen Build. Neue App-Funktionen einschließlich Discovery-Hilfe werden mit dem lokalen Build getestet; veröffentlichte RC5-Images bleiben unverändert.

### Mit dem Docker-Installer loslegen (RC5)

Du brauchst einen Linux-Server, eine VM oder einen Raspberry Pi mit unterstütztem 64-Bit-Betriebssystem, eine Hue Bridge und einen Loxone Miniserver für die Steuerung. Dein Mac oder Windows-PC begleitet dich bei der Einrichtung.

1. **Installer starten:** Die [Installationsanleitung](INSTALL.de.md) führt dich durch Anmeldung am Server, direkten RC5-Download mit Prüfsumme und Start des Installers.
2. **Hue2Lox einrichten:** Der Installer prüft dein System und kann fehlende Pakete und Docker installieren. Vorhandene funktionierende Docker-Installationen werden weiterverwendet.
3. **Bridge koppeln:** Öffne die angezeigte Webadresse (bei direktem HTTPS das Zertifikat prüfen) und melde dich mit `admin` / `admin` an. Das Passwort kannst du in der Oberfläche ändern.
4. **Mit Loxone verbinden:** Wähle Lampen oder Szenen aus und folge der [bebilderten Anleitung](docs/TUTORIAL.de.md), um Befehle zu kopieren oder XML in Loxone Config zu importieren.

**[Zur Installationsanleitung](INSTALL.de.md) · [RC5 als ZIP herunterladen](https://github.com/square-com-de/hue2lox/releases/download/v1.0.0-rc.5/hue2lox-v1.0.0-rc.5.zip) · [Download prüfen](docs/DOWNLOADS.md)**

Lieber mit KI-Begleitung? Nutze den [Installationsprompt für ChatGPT oder Claude](docs/AI-INSTALL.de.md). Er führt dich bis zum selben interaktiven Installer.

## Feedback & Kontakt

Du hast Hue2Lox ausprobiert? Ich freue mich über dein Feedback – auch darüber, was gut funktioniert!

- **Per E-Mail, ohne GitHub-Konto:** [hue2lox@square-com.de](mailto:hue2lox@square-com.de)
- **Feedback oder Fragen auf GitHub:** [Feedback / Frage erstellen](https://github.com/square-com-de/hue2lox/issues/new?template=feedback_question.md) (GitHub-Konto erforderlich).
- **Fehler oder Verbesserungsideen:** [Passende Issue-Vorlage auswählen](https://github.com/square-com-de/hue2lox/issues/new/choose).

Bei Problemen helfen die Hue2Lox-Version, eine kurze Beschreibung und gegebenenfalls ein Screenshot oder die Fehlermeldung. Bitte keine Passwörter oder Tokens mitschicken. Sicherheitsprobleme vertraulich melden – siehe [Sicherheit](SECURITY.md).

## Release-Status und technische Hinweise

**Veröffentlicht: RC5. In Vorbereitung: RC6, noch nicht veröffentlicht.** PR #18 ist in main integriert. Die reale Ubuntu-26.04-/DietPi-13-Abnahme des gemeinsamen Installers, Docker/nativ sowie Update/Rollback und Datenerhalt ist bestanden. [Abnahme und Grenzen](docs/DEPLOYMENT-ACCEPTANCE.md). Hue-/Loxone-Hardwaretests und die Prüfung der endgültigen RC6-Pakete bleiben separat offen. Der eigene Projektcode steht unter Apache 2.0.

RC5 bietet **Quellcode samt Installer** und ein **fertiges Docker-Hub-/GHCR-Image für AMD64/ARM64**: `ghcr.io/square-com-de/hue2lox:1.0.0-rc.5`. Der Installer baut weiterhin lokal. Quellen- und Lizenzbeilagen stehen beim [Release](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.5). Vor einem stabilen Release gibt es keinen `latest`-Tag.

RC5 ist ein unveränderter Versionsstand. [Version, Commit und Prüfsumme](docs/DOWNLOADS.md) prüfen. `main` ist der getrennte Entwicklungsstand.

Szenen erstellst du weiterhin in der Hue-App. Hue2Lox ruft sie über Loxone ab. Eine Synchronisierung des tatsächlichen Lampenzustands zurück in den Loxone-Lichtsteuerungsbaustein ist nicht vorgesehen.

**Bestehende Installationen:** Für Standard-Docker-Installationen gilt der [gesicherte Update-/Rollbackweg](docs/UPDATE-DOCKER.de.md), für native Installationen die [native Wartung](docs/INSTALL-NATIVE.md). Angepasste Compose-/Prototyp-Installationen separat prüfen. Eine Neuinstallation ist kein allgemeiner Updater.

Änderungen stehen im [Changelog](CHANGELOG.md), der [unveröffentlichten RC6-Vorbereitung](docs/RC6-PREPARATION.md) und den [Release-Hinweisen](RELEASE.md).

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
