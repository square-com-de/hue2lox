# Mit KI installieren

[Startseite](../README.de.md) · [English](AI-INSTALL.md) · [Installationsanleitung](../INSTALL.de.md)

Öffne einen **neuen Chat** in ChatGPT, Claude oder einem anderen KI-Assistenten und kopiere den folgenden Prompt hinein. Die KI hilft bis zum Start des Installers; danach übernimmt dessen Menü.

Du brauchst einen Linux-Zielserver, dessen IP und Benutzernamen, SSH-Zugang und Root-/sudo-Rechte sowie Zugriff auf [Hue2Lox auf GitHub](https://github.com/square-com-de/hue2lox). Der Download ist ohne GitHub-Konto möglich. Passwörter nur im Terminal eingeben. Unterstützte Systeme und Hilfe bei fehlendem SSH oder sudo stehen in der [Installationsanleitung](../INSTALL.de.md).

## Prompt zum Kopieren

```text
Hilf mir, den Hue2Lox-Installer zu starten. Halte es einfach und führe mich
Schritt für Schritt durch genau diesen Ablauf:

1. Frage zuerst, auf welchem Linux-Gerät Hue2Lox laufen soll: Betriebssystem,
   IP/Hostname und Benutzername. Frage auch, ob mein Arbeitsgerät ein Mac
   oder Windows-PC ist. Warte auf die fehlenden Antworten. Mein Arbeitsgerät
   ist nicht automatisch das Installationsziel.
2. Gib mir den SSH-Befehl zum Zielserver mit meinen Angaben. Auf dem Server
   vorhandene sudo-Rechte mit sudo -i verwenden oder mit su - zu Root wechseln.
   Wenn ich bereits Root bin, keinen Wechsel verlangen. sudo nicht installieren
   und keine Benutzergruppen ändern.
3. Folge dem Direktdownload-Ablauf in
   https://github.com/square-com-de/hue2lox/blob/v1.0.0-rc.3/INSTALL.md.
   Auf dem Zielserver als Root ca-certificates, curl und unzip bereitstellen.
   Das feste Paket hue2lox-v1.0.0-rc.3.zip und SHA256SUMS.txt direkt von
   https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.3 laden.
   Kein Download auf dem Arbeitsgerät und kein scp nötig. Kein main-Branch-ZIP.
4. In einem neuen Downloadordner mit sha256sum --check SHA256SUMS.txt prüfen.
   Nur nach erfolgreicher Prüfung entpacken und install-assistant.sh aus
   hue2lox-v1.0.0-rc.3 starten. Bei Fehlern stoppen und nichts überschreiben.
   Danach übernimmt das Installer-Menü.

Beschrifte jeden Befehlsblock mit ARBEITSGERÄT oder ZIELSERVER.
Gib jeweils nur den nächsten Schritt und warte auf mein Ergebnis.
Keine Git-Befehle, Versionsauswahl oder Quellcodeprüfung. Keine eigene
Docker-Installation durch die KI: Das erledigt der Installer.
Fordere keine Passwörter, Tokens oder privaten Schlüssel im Chat an.
Antworte auf Deutsch.
```

**Teststatus:** Der vereinfachte KI-Ablauf muss noch in einem neuen Chat getestet werden. Die bereits bestätigten Systemtests stehen in [INSTALL.md](../INSTALL.de.md).
