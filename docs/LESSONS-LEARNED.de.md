# Lessons Learned: Installation, Bedienung und Freigabe

[English](LESSONS-LEARNED.md) · [Runtime-Status](RUNTIME-SUPPORT.de.md) · [Release-Gate](GHCR-RELEASE.md#stable-acceptance-gate)

Stand 24.10.2026. Diese Aufarbeitung ändert keine alten Releases. 1.0.1 wurde bereits veröffentlicht, bevor dieses zusätzliche Gate im Quellstand eingeführt wird. Das Gate verhindert keine rückwirkende Veröffentlichung; es muss vor einer weiteren Freigabe gemergt und erfüllt sein. PLX wird im eigenen Projekt aufgearbeitet; hier stehen ausschließlich Hue2Lox-Belege.

## 1. RC5 installierte eine blockierte Steuerung

- **Fall / Nutzerauswirkung:** Frische Installer-Installation war erreichbar, aber Schalten/RGB/Lumitech blieben gesperrt. Das direkte Image hatte andere Defaults.
- **Belegte Ursache:** RC5 schrieb alle drei `HUE_*_ENABLED`-Werte als `0`: [prepare-install.py:63](https://github.com/square-com-de/hue2lox/blob/v1.0.0-rc.5/scripts/prepare-install.py#L63). Das war eine Produkt-/Installer-Inkonsistenz, kein fehlendes Pairing.
- **Erkennungslücke:** Erreichbarkeit und ein grüner Healthcheck galten als zu weitreichende Funktionsabnahme.
- **Umgesetzte Prävention:** Frische Installerwerte jetzt `1`, weiterhin Token- und Capability-Prüfung. [PR41](https://github.com/square-com-de/hue2lox/pull/41), [aktueller Erzeuger](https://github.com/square-com-de/hue2lox/blob/v1.0.1/scripts/prepare-install.py#L81). README/Install verlinken jetzt die gezielte Recovery und unterscheiden frische von erhaltenen Daten.
- **Owner:** Engineer für Defaults; Deployer für tatsächliche Laufzeitwerte; Nutzer für Lampenwirkung.
- **Abnahme:** [Release-CI 1.0.1](https://github.com/square-com-de/hue2lox/actions/runs/40100051393). Physische Lampenwirkung ist separat und nicht durch diese CI ersetzt.

## 2. Tests bestätigten den falschen Sollzustand

- **Fall / Nutzerauswirkung:** „Grün“ verdeckte Fall 1 statt ihn zu finden.
- **Belegte Ursache:** Der Frischinstallations-Test verlangte [RC5 test_install.py:25](https://github.com/square-com-de/hue2lox/blob/v1.0.0-rc.5/tests/test_install.py#L25) ausdrücklich `0`; [install-color.sh:13](https://github.com/square-com-de/hue2lox/blob/v1.0.0-rc.5/scripts/install-color.sh#L13) verlangte deaktivierte Farbe.
- **Erkennungslücke:** Implementierungserwartung statt fachlichem Vertrag „frisch installiert und nach Pairing steuerbar“. Negative Tests mit absichtlich deaktivierter Steuerung sind dagegen weiterhin sinnvoll.
- **Umgesetzte Prävention:** [Frischinstallation erwartet `1`](https://github.com/square-com-de/hue2lox/blob/v1.0.1/tests/test_install.py#L25); Auth-/Capability-/Sperrtests bleiben bestehen. Neues Stable-Gate verlangt zusätzlich den veröffentlichten Endnutzerablauf und einen dokumentierten Supportumfang, nicht nur die Testanzahl.
- **Owner:** Engineer und Reviewer für den fachlichen Sollzustand; Deployer für einen unabhängigen Ablauf ohne Fixture-Sonderkonfiguration.
- **Abnahme:** Tests und Quellenzuordnung sind nachprüfbar; die neue Gate-Logik wird mit fehlender/falscher Freigabe und gesperrten Registry-Aufrufen isoliert geprüft.

## 3. Update, Recovery und Neustart wurden vermischt

- **Fall / Nutzerauswirkung:** Neues Image/Code konnte mit alten `0`-Werten oder altem Passwort weiterlaufen; bloßes Neustarten übernimmt keine neue Umgebung und kein neues Image.
- **Ursache:** Ein Update muss bewusst gespeicherte Werte erhalten und darf sie nicht als „Fehler“ pauschal überschreiben. Nicht jeder historische Benutzercontainer ist durch einen unveränderlichen Image-/Daten-Nachweis rekonstruierbar; wir weisen ihm deshalb keinen geratenen Tag zu.
- **Erkennungslücke:** „Neuer Download“ oder geänderte Versionsnummer wurden nicht immer gegen tatsächlich laufendes Image, Umgebung und Daten abgeglichen.
- **Umgesetzte Prävention:** [Recovery](RECOVERY-CONTROL.de.md) verlangt eine ausdrückliche Entscheidung über Flags; [Update/Rollback](UPDATE-DOCKER.de.md) sichert das exakte alte Image und private Daten kalt und erstellt neu. README/Install nennen jetzt `pull ≠ recreate ≠ restart` sowie bestehendes Passwort und die Grenzen eigener Portainer-Stacks.
- **Owner:** Deployer für Sicherung/Identitätsvergleich; Betreiber für bewusste Steuerungsfreigabe.
- **Abnahme:** CI prüft Cold-Update/exaktes Rollback und erhaltene Einstellungen; vor der nächsten Freigabe zusätzlich die konsolidierte Anleitung mit geänderten Zugangsdaten und absichtlich gesperrten Flags unabhängig abnehmen. Keine Geheimnisse veröffentlichen.

## 4. PR45 war technisch vorhanden, aber umständlich zu bedienen

- **Fall / Nutzerauswirkung:** Versteckte Verwaltung, Auswahl, Haken und Speichern verhinderten einen selbstverständlichen Ein/Aus-Einstieg.
- **Ursache:** Der [erste PR45-Stand](https://github.com/square-com-de/hue2lox/blob/614d30dec5c668ec547a65f92a3d6cecb921f433/web/scenes.js#L80) bildete die technische Absicherung als Bedienritual ab.
- **Erkennungslücke:** API-/XML-Tests belegten nicht Auffindbarkeit und Aufwand. Ein Review ohne Endnutzerpfad reichte nicht.
- **Umgesetzte Prävention:** [PR45](https://github.com/square-com-de/hue2lox/pull/45): Ein/Aus direkt sichtbar, genau eine exakte Gruppe automatisch, größere/mehrdeutige Gruppen bewusst auswählen, Zusatzlampen vorher benennen, keine Checkbox/extra Save. Zuordnungsänderungen und alte Recall-Befehle bleiben kontrolliert. [Verhalten und Grenzen](features/SCENE-SWITCH.de.md).
- **Owner:** Engineer für UI/Default; Deployer für DE/EN-Ablauf; Nutzer für Szenenwechsel/finales AUS.
- **Abnahme:** 325 Tests, 27 unabhängige Szenentests und [grüne PR-CI](https://github.com/square-com-de/hue2lox/actions/runs/40087905005). Nutzer meldete den Ablauf anschließend als funktionierend und gab Stable frei; das ist keine pauschale Gerätefreigabe und keine gemessene Garantie beliebiger verspäteter Befehle.

## 5. Frischer Podman-Desktop-Login scheiterte

- **Fall / Nutzerauswirkung:** Image/Health liefen, `admin/admin` wurde abgewiesen; die Meldung suggerierte ein falsches Passwort.
- **Belegte Ursache:** Fehlende `HUE_PUBLIC_URL` führte in [1.0.0](https://github.com/square-com-de/hue2lox/blob/v1.0.0/src/loxone_export.py#L14) zu HTTPS als Erwartung, während der Container standardmäßig HTTP diente. [Origin-Prüfung](https://github.com/square-com-de/hue2lox/blob/v1.0.0/src/app.py#L378) wies den Request vor der Passwortprüfung ab. Beobachtet: nicht gesetzte Variable und Login-HTTP-403. Nicht jede ältere fehlgeschlagene Instanz ist eindeutig einem Image-Tag zugeordnet.
- **Erkennungslücke:** Tests setzten die Browseradresse ausdrücklich und prüften damit nicht „öffentliches Image laden → Standardwerte → Login“. Linux-Docker-CI wurde zu weit auf Podman Desktop übertragen.
- **Umgesetzte Prävention:** [PR47](https://github.com/square-com-de/hue2lox/pull/47) behebt direkte lokale Adressen und die DE/EN-Fehlermeldung; explizite URLs, Origin/CSRF und Passworterhalt bleiben geschützt. In der Container-Anleitung wurde die widersprüchliche alte Workaround-Passage durch einen einzigen 1.0.1-Ablauf ersetzt; Runtime-Matrix begrenzt den Support.
- **Owner:** Engineer für Ursache/Regression; Deployer für genau das öffentliche Image und echte GUI-Standardwerte.
- **Abnahme:** [Öffentlicher Desktop-Ablauf](acceptance/DESKTOP-1.0.1.md), Podman Desktop 1.30.5/macOS ARM64, Login/Reload/Neustart; 329 Tests und 14 Release-Jobs grün. Andere Podman-Plattformen/Compose bleiben offen, keine pauschale Inkompatibilitätsbehauptung.

## 6. „Fertig“ und Freigabe wurden zu breit verwendet

- **Fall / Nutzerauswirkung:** Merge, Build, veröffentlichter Download, echte Runtime-Abnahme und Produktion waren nicht immer eindeutig getrennt. Ein nachträglich ausgesprochener Stop kann eine bereits erfolgte Veröffentlichung nicht zurücknehmen.
- **Ursache / Erkennungslücke:** Gesprächsstände statt eines aktuellen, versionsgebundenen GitHub-Gates; technische Checks allein konnten `latest` freigeben.
- **Umgesetzte Prävention:** `compliance/stable-readiness.json` beginnt geschlossen. Der Release-Helfer blockiert Stable-Publish/Promotion bei fehlender/falscher Version, unvollständigen Nachweisen oder geändertem Code/Doku-Inhalt. RC-Vorbereitung bleibt möglich. Das Gate wird nicht automatisch aus grüner CI geöffnet. [Maintainer-Ablauf](GHCR-RELEASE.md#stable-acceptance-gate).
- **Owner:** Maintainer für Freigabedatensatz/Tag; PM für aktuelle Zuordnung von Auftrag, Kandidat und Ergebnis; Deployer für Belege; Nutzer für reale Hardwareabnahme.
- **Abnahme / offen:** Gate-Regressionstests vorhanden. Unabhängiger DE/EN-Dokureview und neue Copy/Paste-/Recovery-Abnahme bleiben vor der nächsten Stable-Freigabe offen. Der Gate-PR muss zuerst gemergt werden; alte Workflows/Releases werden nicht umgeschrieben. Keine Produktion geändert.
