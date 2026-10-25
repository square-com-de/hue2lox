# Hue2Lox 1.0.3 — unveröffentlichte Vorbereitung

Basis: main `3493f5f22fdfc3d31a24c2a668e879b54118dafd`, einschließlich PR #54, #55 und #56. Anschließend im selben Vorbereitungs-PR: vollständiger Dokumentationsdurchgang mit aktualisiertem Handbuch, beiden Tutorials, Architektur-/Sicherheits-/Runtime-Referenzen und klarem historischem Index. Die genaue Kandidaten-Commit-ID und CI-Ergebnisse stehen im zugehörigen Vorbereitungs-PR. Kein Tag und kein GitHub-Release wird in diesem Arbeitsschritt angelegt. Keine Images werden gepusht, `latest` bleibt unverändert und es gibt keinen Produktionsrollout.

## Inhalt und Grenzen

[DE/EN-Release-Hinweise](RELEASE-NOTES-1.0.3.md). Versionsgebunden sind Installer-Manifest, Compose-Vorlagen, DE/EN-Installationsanleitungen und Downloadnamen. Die öffentlich orientierten READMEs übernehmen die in PR #58 eingeführte Struktur und behalten ihren funktionierenden 1.0.2-Schnellstart bis zu einer ausdrücklich genehmigten neuen Veröffentlichung. Der 1.0.3-Kandidatenstatus und seine Anleitungen sind separat verlinkt. Bereits veröffentlichte 1.0.2-/RC-Dateien bleiben unverändert. Die Traefik-Datei ist ein Beispiel für vorhandenen Traefik; sie installiert keinen Proxy und bescheinigt keine praktische Traefik-Abnahme. Anwendungskern und Datenformat werden nicht geändert.

## Isolierte technische Prüfung

Die folgenden Befehle benötigen keine Hue Bridge oder Loxone-Hardware und veröffentlichen nichts:

```sh
python3 scripts/check-quality.py
python3 -m unittest discover -s tests -t . -p 'test_release_readiness.py'
python3 -m unittest discover -s tests -t . -p 'test_release_image.py'
python3 -m unittest discover -s tests -t . -p 'test_release_version.py'
python3 scripts/check-release-packages.py --version 1.0.3
```

Der Pakettest baut Quell-ZIP und natives Archiv aus einem festen Commit, prüft Prüfsummen, übergibt das native Archiv aus dem ZIP und führt HTTPS-/Passwort-/Neustart-Prüfungen nur über Loopback aus. Die reguläre PR-CI prüft zusätzlich Docker-Neuinstallation, Image-/Installerweg, Update und Rollback, ZIP-Docker-Build sowie native systemd-Ziele und beide Image-Architekturen. Ergebnisse im PR nachlesen, keine historischen Tests als neue 1.0.3-Abnahme ausgeben.

## Absichtlich geschlossene Veröffentlichungssperre

`compliance/stable-readiness.json` gehört zu 1.0.3 und hat `approved: false`. Nachfolgender Befehl muss derzeit mit „Stable blocked“ fehlschlagen:

```sh
python3 scripts/release-image.py check-readiness --version 1.0.3
```

Vor Veröffentlichung fehlen die Abnahme des endgültigen Kandidaten (DE/EN-Browserfluss mit sichtbarer Version, vorhandenes Passwort/Daten, Update/Rollback und Supportumfang), deren Bindung an den exakten Quellfingerabdruck und die ausdrückliche Veröffentlichungsfreigabe. Erst danach darf der Freigabedatensatz separat abgeschlossen werden. Prüfungen der tatsächlich öffentlichen Artefakte erfolgen zusätzlich nach einer später genehmigten Veröffentlichung. Produktionsrollout benötigt einen eigenen Auftrag. Hardware bleibt separat in [#42](https://github.com/square-com-de/hue2lox/issues/42).
