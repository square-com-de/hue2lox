# Hue2Lox – Handbuch

[Startseite](../README.de.md) · [English](MANUAL.md) · [Installation](../INSTALL.de.md)

## 1. Zugang und Sprache

Öffne die HTTPS-Adresse deiner Installation. Bei einer neuen Einrichtung gilt `admin` / `admin`; das Passwort kann im Kopfbereich geändert werden. Die Browserwarnung verschwindet erst, wenn das passende Zertifikat als vertrauenswürdig eingerichtet wurde. Den Fingerabdruck am Server prüfen; eine neue Installation bekommt ihr eigenes Zertifikat. Details: [Zertifikat erneuern, IP wechseln, sichern und wiederherstellen](MAINTENANCE.de.md).

Deutsch oder Englisch oben auswählen. Die erste Sprache wird aus dem Browser ermittelt. Ein Wechsel lädt die Seite neu; Anmeldung und gespeicherte Nutzungsarten bleiben erhalten, ungespeicherte Eingaben und temporäre XML-Auswahlen werden zurückgesetzt.

## 2. Bridges und Geräte

Unter **Bridges** die Netzwerksuche verwenden oder eine lokale IP und einen Namen eingeben. **Bridge prüfen und hinzufügen** wählen, anschließend **Koppeln**, die Link-Taste an der Bridge drücken und innerhalb des angegebenen Zeitfensters verbinden. Keine Hue-Keys manuell in die Oberfläche kopieren.

**Lampen & Szenen einlesen** aktualisiert den Bestand. Der Bridge-Name ist zugleich der Filtername – er kann etwa ein Geschoss bezeichnen, muss es aber nicht. Räume und Zonen stammen aus Hue. Eine ausbleibende Netzwerksuche kann an Docker, Firewall oder VLANs liegen; die manuelle IP-Eingabe bleibt möglich.

## 3. Lampen

Die Karte zeigt Namen, Modell, Typ, Fähigkeiten und den zuletzt gelesenen Zustand. Eine ausgeschaltete Lampe kann weiterhin eine gespeicherte Helligkeit anzeigen. Diese Anzeige ist keine Rückführung in den Loxone-Lichtbaustein.

Unter **Nutzung & Verwaltung → Für Loxone nutzen** die gewünschten Steuerungsarten anhaken. Die Vorauswahl richtet sich nach den Bridge-Fähigkeiten. RGB + Weiß nutzt vorzugsweise Lumitech; Tunable White unterstützt Weißtemperatur ohne RGB. Eine Nutzungsart muss aktiv bleiben. Die Auswahl konfiguriert Befehle und XML, sie schaltet keine Lampe.

- **Befehle:** Kopierfelder öffnen; bei mehreren Nutzungsarten die Vorschau wählen.
- **XML:** gewählte Nutzungsarten dieser Lampe exportieren.
- **Ignorieren:** dauerhaft in Hue2Lox ausblenden; über **Ignorierte anzeigen** wiederherstellen.
- **Entfernen:** nur aus Hue2Lox entfernen; ein neuer Scan kann die Lampe zurückbringen. Keine Löschung auf der Bridge.

Für mehrere Lampen die Checkboxen verwenden und **Auswahl als XML** wählen. Ein gemeinsamer Import erzeugt einen virtuellen Ausgang mit mehreren Befehlen. Separate Importe legen weitere Ausgänge an. Filter ändern die Ansicht, nicht die bestehende Auswahl.

## 4. Szenen

Szenen in der Hue-App erstellen, bearbeiten und löschen. In Hue2Lox **Szenen einlesen** wählen, um den Bestand abzugleichen. **Befehle** und **XML** funktionieren wie bei Lampen; der Aufruf verwendet einen EIN-Impuls. Verwaltung bietet Ignorieren, Wiederherstellen und Entfernen nur für Hue2Lox.

Eine Hue-Szene kann auch Lampen schalten, die in Hue2Lox ignoriert oder entfernt wurden. Maßgeblich ist ihre Zusammensetzung in Hue.

## 5. Loxone verbinden

Unter **Loxone-Einstellungen** lässt sich der Miniserver suchen und ein Link zu seiner Weboberfläche speichern. Seine Zugangsdaten werden dabei nicht übernommen. Das Hue2Lox-Zugriffstoken kann kurz angezeigt oder mit dem HTTP-Header kopiert werden; es ist nicht der Hue-Bridge-Key.

Die genaue Einrichtung der virtuellen Ausgänge: [TUTORIAL.de.md](TUTORIAL.de.md). Den Header mit sichtbarem `\r\n` exakt übernehmen. Nicht mehrere konkurrierende Ausgänge gleichzeitig an dieselbe Lampe anschließen. XML enthält standardmäßig einen Token-Platzhalter; **Token in XML** muss ausdrücklich gewählt werden.

## 6. Fehler eingrenzen

| Symptom | Prüfen |
| --- | --- |
| Browser meldet Zertifikatsfehler | Serveradresse, Zertifikatsgültigkeit und Fingerabdruck; Vertrauen auf diesem Gerät einrichten |
| Bridge nicht erreichbar | Lokale IP, Netzwerk, Bridge-Stromversorgung; bei Identitätsfehler nicht einfach die Zertifikatsprüfung abschalten |
| Lampentyp unerwartet | Bridge erneut einlesen und Fähigkeiten ansehen; Modellkatalog überschreibt die Bridge nicht |
| HTTP 401 | Hue2Lox-Token im Header |
| HTTP 403 | Freischaltung der Steuerung; Admin-Anfragen benötigen zusätzlich Sitzung und CSRF |
| HTTP 400 | Empfangenen bereinigten Body, Zahlentyp, Platzhalter und Headerformat prüfen |
| HTTP 415 | Content-Type und Header-Trennzeichen prüfen |
| HTTP 200, aber falsche Wirkung | Aktortyp, Steuerungsart, Helligkeit und tatsächliche Lampe prüfen |
| Kein Monitoreintrag | Loxone-Ausgang, Zieladresse, Port und TLS; Fehler vor HTTP erscheinen nicht im Monitor |

Unter **HTTP-Monitor** das Testprotokoll starten, dann gezielt einen Loxone-Befehl auslösen. Aufzeichnung maximal zehn Minuten und 200 Einträge im Arbeitsspeicher. Tokens, Keys und unbekannte Freitexte werden nicht protokolliert. Vor Weitergabe auch bereinigte Logs auf persönliche Namen und Adressen prüfen.

## 7. Update, Backup und Wiederherstellung

Vor Updates den Dienst kurz stoppen und das **vollständige Installationsverzeichnis** geschützt sichern. Es enthält `.env`, Compose-Dateien, `data/`, `certs/`, `secrets/` und den verwendeten Quellstand. Insbesondere neue Bridge-Keys liegen in `data/bridge-keys/`. Nicht nur das GitHub-Repo sichern: Private Dateien gehören absichtlich nicht hinein.

Beispiel für die separate Testinstallation aus INSTALL.de.md, als root; Backup-Ziel außerhalb des Installationsordners wählen:

```sh
cd /opt/hue2lox-test
docker compose stop
install -d -m 700 /opt/hue2lox-private-backups
umask 077
tar -czpf /opt/hue2lox-private-backups/test-backup.tar.gz -C /opt hue2lox-test
docker compose start
```

Einen neuen Backup-Dateinamen wählen, um ältere Sicherungen zu behalten. Archive verschlüsselt/offline verwahren und nie auf GitHub hochladen. Ein Dateibackup enthält kein Docker-Image: zusätzlich die verwendete Image-Version bzw. den Digest dokumentieren; für vollständig offline verfügbare Rückkehr das Image separat sichern.

Wiederherstellung zuerst auf einem getrennten Ziel testen: Container stoppen, vorhandenen Stand beiseite sichern, Archiv mit erhaltenen Rechten entpacken, Compose-Pfade/IP/Port prüfen, Eigentümer der privaten Verzeichnisse UID/GID 10001 kontrollieren und erst dann starten. Bei geänderter Adresse ein passendes Zertifikat erzeugen; einen verlorenen privaten Schlüssel nicht aus GitHub erwarten. Health, Anmeldung, Inventar, Token und danach einen kontrollierten Lampentest prüfen. Die vollständige Wiederherstellungsprobe ist noch Teil unserer gemeinsamen Abnahme.

Das bestehende Prototyp-Update legt nur eine begrenzte Rückrollkopie an; sie ersetzt kein vollständiges Backup. Ein allgemeiner öffentlicher Update-/Rollback-Mechanismus steht noch aus.

## 8. Grenzen und Quellen

Die [Release-Checkliste](../RELEASE.md) nennt offene Prüfungen. Eigener Projektcode und eigene SVG-Symbole stehen unter der [Apache License 2.0](../LICENSE); Drittanbieterbestandteile behalten ihre jeweiligen Bedingungen. [Quellen und Lizenztexte](../THIRD-PARTY-NOTICES.md) sind auch über den Footer erreichbar.

Unter **Nutzung & Verwaltung → Lampensymbol** kannst du die Form pro Lampe wählen. **Automatisch** verwendet Modell und Bridge-Daten; unbekannte Geräte erhalten ein Glühbirnensymbol. Die Auswahl bleibt bei Neustarts und erneutem Einlesen erhalten und verändert keine Loxone-Befehle.
