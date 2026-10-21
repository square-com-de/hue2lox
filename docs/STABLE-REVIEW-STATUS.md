# Stable review: disposition / Zuordnung

Stand: 20.10.2026, Vorbereitung in drei getrennten PRs auf Basis von main `132737ba7e6d4cc18e3f04c6503e65ecc386a1bf`. Kein Stable-Release und keine Hardwarefreigabe. Diese Tabelle ordnet die Befunde aus dem Stable-Review den Änderungen zu; für Testergebnisse und Commit-Zuordnung die jeweiligen PR-Checks verwenden.

| Befund | Behandlung |
| --- | --- |
| B01 Paket-/Versionsbindung | Doku-PR: ein zentraler RC1-Download mit Commit, SHA-256 und Archivordner; main ausdrücklich Entwicklung. Stable-Paket noch nicht vorhanden. |
| B02 Hardwareabnahme | Offen: [Abnahmeplan](ACCEPTANCE.md). Frühere Debian-Rückmeldungen haben keine vollständige Commit-/Image-Zuordnung. |
| B03 Hue-CA | Herausgeberentscheidung: unverändert beibehalten. Keine neue rechtliche Freigabe behauptet. Herkunftshinweise bleiben erhalten. |
| B04 öffentlich/RC/Lizenz | Bereits in PR #9 korrigiert; nicht erneut als neuer Fix gezählt. |
| B05 Prototyp-Dokumentation | Doku-PR: leere Registry, vorhandenes mDNS, Hostnetzwerk gegenüber historischem Portmapping abgegrenzt. |
| B06 Szenenheader | Doku-PR: eine Zeile mit sichtbarem `\r\n`, entsprechend Kopierfeld und XML. |
| B07 Zertifikat/Restore | Wartungs-PR: DE/EN-Ablauf und isolierte Tests; reale Betriebsabnahme bleibt offen. |
| B08 Teststand/Port | Teststand bereits PR #9; Doku-PR korrigiert festen Diagnoseport auf konfigurierten Port. |
| B09 Prototyp-Updater | Doku-PR kennzeichnet historische Zielbindung, korrigiert scripts-Pfad und HUE_PUBLIC_URL; kein allgemeiner RC1-Updater. |
| B10 Cache/Deadline | Robustheits-PR: Netzwerk außerhalb Cache-Lock, Generation gegen veraltete Ergebnisse, absolute Bridgefrist und Parallelitäts-/TLS-Tests. |
| B11 Docker-Wartbarkeit | Robustheits-PR: Rezeptgleichheit geprüft, beide Dependabot-Verzeichnisse, Basisdigest/Architektur im CI-Protokoll. Kein Image-Vertrieb. |
| B12 Englisch | Doku-/Wartungs-/Robustheits-PRs: gemeinsamer Installationsweg, englische Wartung und übersetzbare Diagnosemarker. Weiterführende deutschsprachige Spezialanleitungen sind in der englischen Anleitung benannt. |

RC1 (`v1.0.0-rc.1`, `1d631cd1231d7cf004c6452c1fad0c262ff92bfd`) bleibt samt Release-Text und Assets unverändert. `admin/admin` bleibt die bewusste Erstlogin-Einstellung. Laufende Installationen werden nicht verändert. Ein RC1-zu-Stable-Updateweg oder eine parallele Neuinstallation braucht weiterhin eine separate Abnahme.

English: these are proposed fixes grouped into documentation, maintenance, and robustness PRs. CI validates isolated fixtures only. Real Loxone controls, certificate trust, hardware recovery and the final release-package installation remain acceptance gates; neither the immutable RC1 nor existing installations are updated.
