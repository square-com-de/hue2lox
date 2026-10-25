> **Historischer Stand / Historical record:** Aussagen, Befehle und offene Punkte unten gelten ausschließlich für den genannten damaligen Stand, nicht als aktuelle Installationsanleitung oder 1.0.3-Abnahme. / Statements, commands and pending checks below apply only to the recorded revision. [Aktuelle Dokumentation / current documentation](INDEX.md) · [1.0.3-Vorbereitung / preparation](PREPARATION-1.0.3.md).

# Lokale Prüfung – 17.10.2026

> Für die Veröffentlichung anonymisiert: Adressen, Geräte-IDs und Lampennamen sind Beispiele.

- Zertifikat mit installiertem OpenSSL erfolgreich erstellt: RSA 2048, SHA-256, SAN für 192.0.2.96, 127.0.0.1, localhost und hue2lox.local; 365 Tage gültig.
- Zweiter Aufruf verweigert das Überschreiben vorhandener Zertifikate.
- Anwendung unter Python 3.9.6 auf 127.0.0.1:8443 gestartet und anschließend beendet.
- HTTPS GET /health mit explizit vertrautem Zertifikat: 200, application/json, Body exakt {"status":"ok"}.
- Unbekannter Pfad: 404.
- HTTPS ohne explizites Vertrauen: SSLCertVerificationError wie erwartet.
- Netzwerkbindung erforderte Ausführung außerhalb der Workspace-Sandbox; Test ausschließlich lokal.
- Docker ist nicht installiert: Image-Build, Compose-Konfiguration und Container-Healthcheck nicht ausgeführt.
- LoxBerry/DietPi, Netzwerkpfad und Miniserver nicht getestet; kein Remote-Deploy, keine produktive Konfigurationsänderung.
- Testzertifikat nur im temporären Testordner erstellt, nicht ins Projekt übernommen. Auf dem Ziel ein neues Zertifikat erzeugen.
