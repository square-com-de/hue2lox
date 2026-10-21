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

## So sieht es aus

![Befehle für Loxone im Hue2Lox-Webinterface](web/tutorial-commands.png)

*Beispielansicht mit Testdaten; die aktuelle Oberfläche ist kompakter. Weitere Abbildungen stehen in der [Loxone-Anleitung](docs/TUTORIAL.de.md).*

## Installieren und loslegen

Du brauchst einen Linux-Server, eine VM oder einen Raspberry Pi mit unterstütztem 64-Bit-Betriebssystem, eine Hue Bridge und einen Loxone Miniserver für die Steuerung. Dein Mac oder Windows-PC begleitet dich bei der Einrichtung.

1. **Installer starten:** Die [Installationsanleitung](INSTALL.de.md) führt dich durch Anmeldung am Server, direkten RC3-Download mit Prüfsumme und Start des Installers.
2. **Hue2Lox einrichten:** Der Installer prüft dein System und kann fehlende Pakete und Docker installieren. Vorhandene funktionierende Docker-Installationen werden weiterverwendet.
3. **Bridge koppeln:** Öffne die angezeigte HTTPS-Adresse, prüfe das Zertifikat und melde dich mit `admin` / `admin` an. Das Passwort kannst du in der Oberfläche ändern.
4. **Mit Loxone verbinden:** Wähle Lampen oder Szenen aus und folge der [bebilderten Anleitung](docs/TUTORIAL.de.md), um Befehle zu kopieren oder XML in Loxone Config zu importieren.

**[Zur Installationsanleitung](INSTALL.de.md) · [RC3 als ZIP herunterladen](https://github.com/square-com-de/hue2lox/releases/download/v1.0.0-rc.3/hue2lox-v1.0.0-rc.3.zip) · [Download prüfen](docs/DOWNLOADS.md)**

Lieber mit KI-Begleitung? Nutze den [Installationsprompt für ChatGPT oder Claude](docs/AI-INSTALL.de.md). Er führt dich bis zum selben interaktiven Installer.

## Feedback & Kontakt

Du hast Hue2Lox ausprobiert? Ich freue mich über dein Feedback – auch darüber, was gut funktioniert!

- **Per E-Mail, ohne GitHub-Konto:** [hue2lox@square-com.de](mailto:hue2lox@square-com.de)
- **Feedback oder Fragen auf GitHub:** [Feedback / Frage erstellen](https://github.com/square-com-de/hue2lox/issues/new?template=feedback_question.md) (GitHub-Konto erforderlich).
- **Fehler oder Verbesserungsideen:** [Passende Issue-Vorlage auswählen](https://github.com/square-com-de/hue2lox/issues/new/choose).

Bei Problemen helfen die Hue2Lox-Version, eine kurze Beschreibung und gegebenenfalls ein Screenshot oder die Fehlermeldung. Bitte keine Passwörter oder Tokens mitschicken. Sicherheitsprobleme vertraulich melden – siehe [Sicherheit](SECURITY.md).

## Release-Status und technische Hinweise

**Release Candidate 3.** Deutsch und Englisch sind verfügbar. Eine frühere frische Debian-13-Installation mit Bridge-Kopplung, Lampenanzeige und Neustart wurde erfolgreich getestet. Der erneute Debian-Test des RC3-Pakets und der durchgängige Funktionstest mit einem Loxone Miniserver stehen noch aus. Der eigene Projektcode steht unter Apache 2.0.

Der öffentliche Download enthält den **Quellcode samt Installer und Dockerfile**. Der Installer baut das Hue2Lox-Image auf deinem Linux-Rechner; ein fertiges Hue2Lox-Image bieten wir vorerst nicht an.

RC3 ist ein unveränderter Versionsstand. [Version, Commit und Prüfsumme](docs/DOWNLOADS.md) prüfen. `main` ist der getrennte Entwicklungsstand.

Szenen erstellst du weiterhin in der Hue-App. Hue2Lox ruft sie über Loxone ab. Eine Synchronisierung des tatsächlichen Lampenzustands zurück in den Loxone-Lichtsteuerungsbaustein ist nicht vorgesehen.

**Bestehende Installationen:** Ein allgemeiner Release-Updater ist noch nicht verfügbar. Zugangsdaten und gespeicherte Geräte erhalten; eine vorhandene Installation nicht mit einer Neuinstallation überschreiben.

Details stehen in den [Release-Hinweisen](RELEASE.md) und den [dokumentierten Testergebnissen](docs/TEST-RESULTS.md).

## Dokumentation

| Thema | Einstieg |
| --- | --- |
| Bedienung, Fehlerbehebung, Backup | [Handbuch](docs/MANUAL.de.md) |
| Neue Testinstallation | [Installation](INSTALL.de.md) |
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
