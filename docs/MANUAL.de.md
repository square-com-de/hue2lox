# Hue2Lox – Handbuch

[Startseite](../README.de.md) · [English](MANUAL.md) · [Installation](../INSTALL.de.md)

## 1. Zugang und Sprache

Öffne die tatsächlich konfigurierte HTTP- oder HTTPS-Adresse. Docker/Podman verwenden ohne TLS-Konfiguration HTTP; der Compose-Schnellstart nutzt `http://SERVER-IP:18443`. Nativ richtet der Installer HTTPS mit selbstsigniertem Zertifikat ein. Für Traefik und direktes Container-HTTPS siehe [Konfiguration und Beispiele](CONTAINER-SETUP.de.md#http-oder-https). Bei frischen Daten gilt `admin/admin`; das Passwort im Kopfbereich ändern. Erhaltene Daten behalten ihr bisheriges Passwort. Bei HTTPS Zertifikat und Fingerabdruck prüfen; Browservertrauen gilt nicht automatisch für den Miniserver.

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

Szenen in der Hue-App erstellen, bearbeiten und löschen. **Szenen einlesen** gleicht die gespeicherten Daten ab. Die Steuerungsart steht direkt in jeder Szenenzeile:

- **Ein/Aus:** Standard für neue bzw. bisher unentschiedene Einträge. EIN aktiviert die Hue-Szene; AUS schaltet die gesamte zugeordnete Hue-Gruppe aus. Eine genau passende, eindeutige Gruppe wird automatisch zugeordnet. Bei Mehrdeutigkeit oder zusätzlichen Lampen die Gruppe ausdrücklich wählen und die angezeigten Lampen prüfen. Ohne gültige Zuordnung ist der Export gesperrt.
- **Nur aktivieren:** Reiner Szenenaufruf ohne AUS. In Loxone als Digitalausgang per EIN-Impuls aufrufen, Wiederholung 0 und AUS-Felder leer lassen. Ein zusätzlicher Recall beim Ausschalten würde die Lampen erneut einschalten.

Für **Ein/Aus** die neuen digitalen EIN- **und** AUS-Befehle aus XML oder den Kopierfeldern übernehmen; kein Dimmerwert. Bestehende Recall-Befehle werden durch ein Update nicht geändert. AUS stellt keine früheren Lampenwerte wieder her und kann auch zusätzliche oder in Hue2Lox ausgeblendete Lampen der Gruppe betreffen.

Bei A → B auf derselben Gruppe wird ein überholtes A-AUS ignoriert, wenn B bereits übernommen wurde. Überlappende Gruppen zuerst ausschalten. Nach Neustart zunächst EIN senden; ohne bekannte Zuordnung wird AUS abgewiesen. Die Zuordnung ist Befehlshistorie, **keine gemessene Zustandsrückmeldung an den Loxone-Lichtbaustein**. Hue-App oder andere Steuerwege werden nicht automatisch synchronisiert. Details und Grenzen: [Szenen Ein/Aus](features/SCENE-SWITCH.de.md) · [Szenenschnittstellen](SCENES.md).

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

Vor Wartung die betroffene Instanz stoppen und Daten, Konfiguration sowie das exakte bisherige Image bzw. native Paket zusammen sichern. Die richtige Sicherung hängt vom Installationsweg ab:

| Installation | Vollständig sichern |
| --- | --- |
| Docker/Podman mit benanntem Volume | Gesamtes an `/data` eingebundenes Volume, Compose-/Containerkonfiguration und exaktes Image; separat eingebundene Zertifikate zusätzlich |
| Älterer Docker-Installer | Installationsordner einschließlich `.env`, Compose, `data/`, `secrets/`, `certs/` sowie das exakte Image |
| Nativ | `/etc/hue2lox`, `/var/lib/hue2lox`, Paketidentität/Programmstand und die zugehörige Updatesicherung |

**Ein Archiv nur des Compose-Ordners enthält ein benanntes Volume nicht.** In Podman Desktop liegt dieses Volume in der Linux-VM. Vor deren Löschen/Zurücksetzen separat sichern. Es gibt keine Datenbank; Registry, Kopplungsdaten, Passwort-Hash und Einstellungen liegen in geschützten Dateien. Sitzungen und der temporäre HTTP-Monitor sind nur im Arbeitsspeicher.

[Docker-/Stack-Update und Rollback](UPDATE-DOCKER.de.md) · [Native Wartung](INSTALL-NATIVE.md#aktualisieren-und-rückweg) · [Speicherorte](CONTAINER-SETUP.de.md#wo-bleiben-meine-daten). Rückweg immer mit zusammengehörigem altem Code/Image **und** damaligen Daten durchführen; Passwortänderungen seit der Sicherung werden dabei ebenfalls zurückgenommen. Sicherungen privat und getrennt aufbewahren; `down -v` und Pruning sind kein Updateweg. Wiederherstellung zuerst isoliert prüfen. Hardwarewirkung und Miniserver-Zertifikatsvertrauen bleiben gesonderte Tests.

## 8. Grenzen und Quellen

Die [Release-Checkliste](../RELEASE.md) nennt offene Prüfungen. Eigener Projektcode und eigene SVG-Symbole stehen unter der [Apache License 2.0](../LICENSE); Drittanbieterbestandteile behalten ihre jeweiligen Bedingungen. [Quellen und Lizenztexte](../THIRD-PARTY-NOTICES.md) sind auch über den Footer erreichbar.

Unter **Nutzung & Verwaltung → Lampensymbol** kannst du die Form pro Lampe wählen. **Automatisch** verwendet Modell und Bridge-Daten; unbekannte Geräte erhalten ein Glühbirnensymbol. Die Auswahl bleibt bei Neustarts und erneutem Einlesen erhalten und verändert keine Loxone-Befehle.
