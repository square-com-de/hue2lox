# Gemeinsame Abnahme / Joint acceptance

Status: **offen**. Diese Liste ist ein Prüfplan, kein Nachweis bestandener Tests.

Eine Debian-13-Neuinstallation mit Kopplung und Neustart ist vom Nutzer bestätigt. Die folgenden Punkte bilden den Abnahmeplan für den jeweils konkret protokollierten Release-Kandidaten; sie gelten nicht automatisch als bestanden. Automatische Tests ersetzen diese Abnahme nicht. Eine Testinstallation bleibt von der funktionierenden Installation getrennt; dieselbe Lampe nicht gleichzeitig von beiden Instanzen steuern lassen.

## Bisherige Rückmeldungen

- **20.10.2026, Debian 13 in Proxmox:** Installation, Login, Bridge-Suche und Kopplung, Inventar sowie VM-Neustart mit erhaltener Einrichtung vom Nutzer bestätigt. Siehe [Testprotokoll](TEST-RESULTS.md).
- Die genaue Commit-/Image-ID dieses Benutzertests wurde nicht protokolliert. Vollständige Loxone-Abnahme, Passwortwechsel mit erneuter Anmeldung und Wiederherstellungsprobe bleiben offen; andere Plattformen sind dadurch nicht abgenommen.

## Prüfprotokoll

- Datum / Tester:
- Git-Commit / Image-ID:
- Rechner, CPU-Architektur und Betriebssystem:
- Docker- und Compose-Version:
- Hue-Bridge-Modelle / Firmware:
- Loxone Config- und Miniserver-Version:
- Ergebnis je Schritt: bestanden, fehlgeschlagen oder nicht getestet; bereinigter Nachweis:

## 3 — Neuinstallation auf einem frischen Zielsystem

- [ ] Öffentlichen Quellstand mit dokumentierter Version herunterladen oder klonen; Anleitung ausschließlich aus [INSTALL.md](../INSTALL.de.md) befolgen.
- [ ] KI-Installationsprompt mit Voraussetzungen erproben; tatsächlichen Assistenten/Zugriffsmodus und Abweichungen protokollieren.
- [ ] Keine privaten Dateien der bisherigen Installation übernehmen.
- [ ] Leere Testinstallation mit eigenem Verzeichnis, Compose-Projekt und freiem Port vorbereiten.
- [ ] Docker-Image auf der tatsächlich verwendeten Architektur bauen; Start und Healthcheck prüfen.
- [ ] Zertifikatsfingerabdruck prüfen und Browser-Vertrauen einrichten.
- [ ] Erstlogin, Passwortänderung, Abmelden und erneutes Anmelden testen.
- [ ] Deutsch und Englisch, Fehlermeldungen und Tutorial prüfen.
- [ ] Bridge suchen, per Knopfdruck koppeln; Lampen, Räume und Szenen erkennen.
- [ ] Zweite Bridge ergänzen; Namensgleichheit, Filter und Kurzpfade prüfen.
- [ ] Ignorieren, Entfernen, erneute Suche und in der Hue App gelöschte Szenen prüfen.
- [ ] Container und Zielsystem neu starten; Einstellungen, Zertifikat und Tokens bleiben erhalten.
- [ ] Geschützte vollständige Sicherung erstellen und Wiederherstellung in einer getrennten Testinstanz erproben.
- [ ] Den vorgesehenen Updateweg und Rückweg anhand einer definierten Vorversion testen; noch kein allgemeines Updateversprechen geben.

## 5 — Echte Loxone-Abnahme

- [ ] Fähigkeiten mindestens für Ein/Aus, Dimmer, Tunable White und RGB + Weiß vergleichen; vorhandene Geräte dokumentieren.
- [ ] Empfohlene Variante und manuelle Auswahl prüfen; Typ und Fähigkeiten stimmen mit der Bridge überein.
- [ ] Einen HTTP-Ausgang manuell nach Tutorial anlegen und über den Lichtbaustein steuern.
- [ ] Kopierte Header und Body kommen ohne zusätzliches CR/LF im Body an; Ein/Aus und wechselnde Werte prüfen.
- [ ] Einzel-XML: Dateiname, Kurzpfad und ausgewählte Befehlsvarianten stimmen.
- [ ] Mehrfach-XML: ein virtueller Ausgang mit allen gewählten Lampenbefehlen; keine unerwünschten Varianten.
- [ ] RGB-Farben, Helligkeit, Aus bei 0 sowie warmes und kaltes Weiß an echten Lampen prüfen.
- [ ] Lumitech sowohl im Farb- als auch Weißmodus prüfen, nicht nur anhand des API-Statuscodes.
- [ ] Hue-Szene aus Loxone aufrufen; Bearbeiten bleibt in der Hue App.
- [ ] Temporären Monitor testen: Requests sichtbar, Zugangsdaten verborgen, automatisches Ende funktioniert.
- [ ] Abgezogene/unerreichbare Bridge und ungültige Befehle führen zu verständlichen Fehlern.
- [ ] Testkonfiguration sichern; erst danach die gewünschte produktive Übernahme planen.

## Vor Stable

- [x] Eigene Code-Lizenz: Apache 2.0; LICENSE und NOTICE liegen bei.
- [ ] Rechte und Hinweise für Icons, Logo und sonstige Fremdinhalte prüfen.
- [ ] Aktuelle Dateien **und Git-Historie** auf private Daten/Schlüssel prüfen.
- [ ] Automatische GitHub-Prüfungen am vorgesehenen Release-Commit erfolgreich.
- [ ] Unterstützte Zielsysteme und bekannte Einschränkungen anhand echter Ergebnisse benennen.
- [ ] Versionsnummer, Änderungsnotizen und reproduzierbares Installationspaket festlegen.

English: record the exact source and environment, test a clean isolated installation first, then verify real Loxone imports and physical lamp behaviour together. All boxes remain pending until observed; do not interpret a CI pass as hardware or release approval.
