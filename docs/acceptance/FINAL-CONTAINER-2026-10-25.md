# Abschließende Container-Abnahmen / Final container acceptance

25.10.2026 — **die drei beauftragten Software-Abnahmen bestanden; keine Release- oder Hardwarefreigabe.** / All three commissioned software checks passed; no release or hardware approval.

## Prüfstand / Tested identities

- Anwendung / application: veröffentlichtes **1.0.1**, Quellcommit `f245a4ddd8857706f6ded748fb6945ea5aa88a38`.
- Hue2Lox-Imageindex / image index: `sha256:7e12e1491937c36cec763850b3db1c60916e727bf9bbdb82a4f5447e5812076b`.
- Anleitungsbasis / guide baseline: main `06b6578867e3e6fbf8e83156bf25dc41ccae5af1`.
- Unveränderte öffentliche Datei / unchanged public file: [`docker/compose.quickstart.yaml` at bd8b4d1](https://github.com/square-com-de/hue2lox/blob/bd8b4d172cafd8db9e602c992ec3e9704a4ce420/docker/compose.quickstart.yaml), SHA256 `c519baada5bc731a3087b54e517b535b69f6e021bf1037557f4e1b79b402d652`.
- Neue Proxmox-VM122: **Ubuntu26.04.1 amd64**, Docker **29.9.2**, Compose **5.6.1**, 2vCPU/2GiB RAM/24GiB Disk. Frisches Betriebssystem aus offiziellem Cloudimage, kein Clone einer App-VM; Image-SHA256 `5645d0318ad21f643ebb1ac4567514620e9893380b07b0201fda163baa5b7eb5`. Vor erster App-Installation: keine Docker-Container, Images oder Volumes. / Fresh OS from the verified official cloud image, not an app-VM clone; empty Docker inventory recorded before the first app installation.
- Portainer Community Edition **2.45.3 LTS**, Digest `sha256:3609c307943bca8e5c492f69ddd6965df177208b50678a4cff28391c8dd4e96e`.

Bereinigte maschinenlesbare Belege / sanitized machine-readable evidence: [14 Prüfrecords](FINAL-CONTAINER-2026-10-25.json). Passwörter, Steuerungstokenwerte, private Schlüssel, Sitzungen und Archive mit Zugangsdaten werden nicht veröffentlicht. / No passwords, token values, private keys, sessions or credential-containing archives are published.

## 1. Frisches Betriebssystem / Fresh OS — PASS

Nach alleiniger Bereitstellung von Ubuntu, Docker und Compose wurde genau der dokumentierte Block ausgeführt, mit Standardport **18443**, ohne `.env` und ohne YAML-Anpassung:

```sh
mkdir hue2lox &&
cd hue2lox &&
curl --fail --location --output compose.yaml https://raw.githubusercontent.com/square-com-de/hue2lox/bd8b4d172cafd8db9e602c992ec3e9704a4ce420/docker/compose.quickstart.yaml &&
docker compose up -d --wait &&
docker compose ps
```

Container healthy; automatisch angelegtes schreibbares `hue2lox_data`; echte Browseranmeldung über `http://SERVER-IP:18443` mit `admin/admin` und Neuladen bestanden. Kein `HUE_PUBLIC_URL`, Zertifikat oder nachträgliches `chown` nötig. Passwort anschließend über die App-HTTP-API geändert, altes Passwort abgelehnt, Sitzung und Origin-Schutz geprüft. / Healthy container, automatically writable volume, real browser default login and reload passed. No URL, certificate or ownership workaround; password change and security checks passed through the app HTTP API.

## 2. Deaktivierte Flags bei Recovery / Disabled controls during recovery — PASS

Ein eigenes Projekt mit leerer Registry setzte `HUE_WRITES_ENABLED=0`, `HUE_COLOR_ENABLED=0`, `HUE_WHITE_ENABLED=0`. Der 1.0.0-Ausgangsstand erhielt ausdrücklich die passende `HUE_PUBLIC_URL`, weil dessen historischer HTTP-Login sonst nicht funktioniert; das ist eine Recovery-Fixture, keine Zusatzanforderung des 1.0.1-Schnellstarts.

Alle fünf Phasen bestanden / all five phases passed:

1. 1.0.0 mit geändertem Passwort und drei Flags0 / baseline.
2. Update auf1.0.1 / upgrade.
3. Container neu erstellen / recreate.
4. Kalte Sicherung von Daten **und Compose/env**, Restore in ein zusätzliches Volume, Rollback auf die zuvor gespeicherte exakte alte Image-ID / cold backup, separate restored volume and exact old image.
5. Wiederhergestellte Daten erneut mit1.0.1 starten / restored state with current image.

In jeder Phase waren alle drei Werte0; selbst ein PUT mit gültigem Steuerungstoken wurde mit **403 `writes_disabled`** abgewiesen. Geändertes Passwort funktionierte, `admin` nicht; Passwortdatei, Token und Registry blieben bytegleich. Originalvolumes und Sicherung blieben erhalten. Die Flags stehen in der Deployment-Konfiguration: Ein Datenvolume allein ersetzt deren Sicherung nicht. / Flags remained0, valid-token PUTs were rejected, changed credentials worked and state hashes matched. Deployment configuration must be restored alongside data.

## 3. Portainer-Oberfläche / Portainer GUI — PASS

Auf derselben isolierten VM wurde eine eigene Portainer-Testinstanz bereitgestellt. Das lokale Testkonto wurde per CLI-Datei initialisiert; geprüft wurde der Hue2Lox-Stackworkflow in der echten Oberfläche, nicht Portainers erstmaliger Admin-Setup-Assistent. Zugriff auf die Portainer-Verwaltung nur über Loopback und SSH-Tunnel. / A separate test Portainer instance used CLI-initialized credentials. The actual GUI stack workflow was tested, not Portainer's first-admin wizard; management access was loopback/SSH only.

Tatsächlich im Browser / actual browser flow:

1. Anmelden → lokale Docker-Standalone-Umgebung → **Stacks → Add stack**.
2. Neuer Name `hue2lox-portainer` → **Web editor** → vollständige öffentliche Vorlage unverändert einfügen → **Deploy the stack**. Keine manuelle Volumeanlage, keine Umgebungsvariablen.
3. Gespeicherte Portainer-YAML bytegleich zum öffentlichen Download; Port18443 und schreibbares `hue2lox-portainer_data` automatisch angelegt, Container healthy.
4. Hue2Lox-Browserlogin, Passwortwechsel per App-API und Browserlogin mit geändertem Passwort bestanden.
5. In Portainer **Restart**, danach **Recreate** ohne Imagewechsel: Startzeit beziehungsweise Container-ID änderten sich; dasselbe Volume und identische Zustandshashes blieben erhalten. Anschließende tatsächliche Browseranmeldung mit geändertem Passwort bestanden.

Das ist kein Portainer-Releaseupgrade, kein Swarm-/Rootless-/Windows-Test und keine Freigabe aller Portainer-Versionen. / This is not a Portainer-managed application version upgrade or blanket platform approval.

## Grenzen, Beobachtungen und Rückweg / Limits, observations and recovery

- Keine Hardware gekoppelt; alle Registries leer. Private LAN-Ziele und Multicast im Testgast gesperrt, IPv6 einschließlich NIC deaktiviert. Eng begrenzte lokale Container-/Portausnahmen sind Test-Infrastruktur, keine Endnutzerpflicht. / No hardware, empty registries, guest isolation; lab firewall rules are not end-user steps.
- Der HTTP-Standard wurde geprüft, keine vertrauenswürdige HTTPS-Browserkette behauptet. / HTTP tested, no claim of trusted HTTPS browser certificates.
- Eigene Compose-/Recovery-Projekte sind nach der Prüfung gestoppt, ihre Volumes erhalten; final läuft der gesunde Portainer-Appstack. Gestoppte Container meldeten Exit137 bei `OOMKilled=false`; diese Abnahme belegt keine sanfte SIGTERM-Beendigung oder Stromausfallsicherheit bei laufenden Schreibvorgängen. Kein Datenverlust in den geprüften Zustandshashes. / Stopped fixtures reported137 without OOM; graceful termination and in-flight power-loss safety were not established.
- Die neue VM wurde nicht erneut rebootet; die separate koordinierte VM121-Neustartabnahme bleibt im [vorherigen Bericht](../CONTAINER-ACCEPTANCE-1.0.1.md) dokumentiert. / No repeated reboot of this new VM; prior reboot evidence remains separately scoped.
- Keine App-Code-, Image-, Tag-, Release- oder Produktionsänderung. Diese Nachweise beziehen sich auf1.0.1, nicht automatisch auf eine künftig anders gebaute Version. / No app/image/release/production change; acceptance is bound to1.0.1.

## Nächster Schritt durch den Menschen / Human hardware handoff

In einer bewusst gewählten Hardware-Testumgebung: eine Bridge suchen oder manuell hinzufügen und per physischer Taste koppeln; eine festgelegte Lampe aus Loxone an/aus/dimmen und entsprechend ihrer Fähigkeit Farbe/Weißtemperatur prüfen; gewünschte Szenenwechsel und abschließendes AUS prüfen; tatsächliche Zielversion und bereinigte Monitorbelege festhalten. Erst danach finale versions-/inhaltsgebundene Releaseentscheidung. / Human-owned pairing, one chosen test light, supported controls, scene changes/final off, exact version and redacted evidence; then final release decision.

Bestehende Installationen behalten vor jedem späteren Go-live eine kalte Sicherung von Daten, Compose/env/TLS sowie exaktem vorherigen Image. Bei Rückkehr zuerst stoppen und den zusammenpassenden alten Image-/Daten-/Konfigurationsstand wiederherstellen: [Update/Rollback DE](../UPDATE-DOCKER.de.md), [EN](../UPDATE-DOCKER.md). Kein automatisches Update produktiver Instanzen durch diese Abnahme.

## Review und Releasegrenze / Review and release boundary

Separater lesender Agentenreview der acht Dokumentations-/Nachweisdateien auf Basis06b6578: keine konkreten Findings; JSON stimmt mit den gesicherten Rohbelegen überein, Skripthashes und Screenshots geprüft. Der Reviewer führte die Laufzeittests nicht nochmals aus. / Separate read-only agent review found no concrete issues; it checked receipt equality, script hashes and screenshots, without rerunning runtime tests.

Die geprüfte Distribution ist ausdrücklich das bestehende1.0.1-Containerimage. Für eine neue Release-Version müssen endgültiger Quellcommit, Version, Pakete und Image-Digests erst gebunden und die betroffenen Prüfungen an diesen tatsächlichen Artefakten bestätigt werden. Eine neuere Doku allein ersetzt diesen Schritt nicht; [Gate-Board#51](https://github.com/square-com-de/hue2lox/issues/51) und das geschlossene Readiness-Manifest bleiben maßgeblich. / A new release still needs its own exact version/source/artifact binding and appropriate validation; newer documentation is not a new image acceptance.
