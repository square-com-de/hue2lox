# Runtime- und Versionsstatus

[English](RUNTIME-SUPPORT.md) · [Installation](../INSTALL.de.md) · [Lessons Learned](LESSONS-LEARNED.de.md)

Stand 25.10.2026: veröffentlicht ist **1.0.2**, Commit `2af13f603c97064fd01585ea04d893a5fdad1081`; **1.0.3 ist unveröffentlichte Vorbereitung**. [1.0.2-Software-/Rolloutnachweis](https://github.com/square-com-de/hue2lox/issues/51) · [1.0.3-Vorbereitung](PREPARATION-1.0.3.md). Die folgenden älteren Plattformabnahmen bleiben ihren ausdrücklich genannten Versionen zugeordnet. „Image startet“, „Login funktioniert“, „Lebenszyklus geprüft“ und „echte Lampenwirkung bestätigt“ sind unterschiedliche Nachweise.

| Weg | Belegter Umfang | Grenze |
|---|---|---|
| Linux Docker Engine + Compose-Plugin (`docker compose`) | [Release-CI](https://github.com/square-com-de/hue2lox/actions/runs/40100051393): frischer Start, HTTPS/Login, Installer/ZIP, Image-Update und exaktes Rollback; AMD64-/ARM64-Images gebaut, gestartet und anonym geladen | Kein Nachweis jeder Docker-/Compose-Version. Die neue Proxmox-Teilabnahme unten erfasst Docker29.9.2/Compose5.6.1; historische Abnahmen anderer Stände enthalten diese Versionsbindung nicht. Compose muss die im Update verwendeten Optionen `--wait`/`--wait-timeout` unterstützen. |
| Portainer CE **2.45.3 LTS**, Linux Docker Standalone | Echte GUI: Webeditor/Deploy, automatisches Volume, Browserlogin, Restart/Recreate mit erhaltenem Passwort und Daten. [Abnahme](acceptance/FINAL-CONTAINER-2026-10-25.md) | Ubuntu26.04.1 amd64/Docker29.9.2; kein Swarm, Rootless oder pauschaler Versionssupport. |
| Podman Desktop **1.30.5, macOS ARM64** | Öffentliches 1.0.1-ARM64-Image: echter GUI-Pull, **Run Image → Create and start**, frische Daten, Browserlogin `admin/admin`, Reload und GUI-Neustart mit erneutem Login; zusätzlich Named-Volume-CLI-Ablauf unter macOS 27.0.1, Client/VM-Engine **6.1.4**, geprüft. [Abnahme](acceptance/DESKTOP-1.0.1.md) | Lokaler Desktop-Ablauf. Keine Freigabe für `podman compose`, den Docker-Installer unter Podman, Windows-/Linux-Podman oder LAN-Multicast. CLI-Version allein belegt diesen GUI-Weg nicht. |
| Nativ, systemd, **amd64**, experimentell | CI: Debian **12/13**, Ubuntu **24.04/26.04** isolierte Lebenszyklen. Reale frühere VMs: Ubuntu **26.04**, DietPi **13** auf dem [dort genannten Commit](DEPLOYMENT-ACCEPTANCE.md) | Historische Nachweise gelten nicht rückwirkend für jedes neue Archiv. Native ARM-/Raspberry-Pi-Abnahme fehlt. Python **3.11+** laut [nativer Anleitung](INSTALL-NATIVE.md), nicht allein durch OS-Namensähnlichkeit freigegeben. |
| LoxBerry | Bestehender Linux-/Docker-Weg auf einer konkreten LoxBerry-VM wurde separat betrieben | **Kein eigenes LoxBerry-Plugin und kein Plugin-ZIP.** Native Basis ist keine Plugin-Abnahme. |
| Unraid/Synology, Docker Desktop auf Mac/Windows, weitere Derivate | Container-/Compose-Beispiele sind Integrationshinweise | Keine pauschale Plattformfreigabe aus Linux-CI oder dem Mac-Podman-Test ableiten. Eigene Abnahme nötig. |

Die Distributionserkennung des Installers ist keine Hardwareabnahme. Die [native Anleitung](INSTALL-NATIVE.md) nennt die nativen OS-Ziele; diese Tabelle begrenzt die tatsächlich nachgewiesenen Wege. Ein `amd64`-Image ist kein ARM-Image; ein 64-Bit-Prozessor mit 32-Bit-OS reicht nicht.

## Den richtigen Einstieg verwenden

- Docker auf Linux: [feste Compose-Datei](CONTAINER-SETUP.de.md#schnellstart-docker-auf-einem-linux-server), ohne Hue2Lox-Installer. Vorbereitete 1.0.3-Befehle erst nach Veröffentlichung verwenden; bis dahin ist 1.0.2 veröffentlicht.
- Geprüfter Mac-Desktop-Weg: [vier konkrete GUI-Schritte](DOCKER.md#podman-desktop-on-macos). Seit 1.0.1 ist für localhost/private IP keine zusätzliche Browseradresse nötig. Eigene DNS-Namen/Reverse Proxy erfordern eine passende `HUE_PUBLIC_URL`.
- Nativ: [separates natives Archiv](INSTALL-NATIVE.md), dessen Version/Commit zum Quell-ZIP passt; keine Container-Flags auf einen systemd-Dienst übertragen.

## Update ist nicht Neustart

Eine neue Image-Version wird erst mit einem **neu erstellten Container** wirksam. Geänderte Umgebungsvariablen ebenfalls. `pull` lädt nur; `restart` startet denselben Container mit seinem alten Image/seiner alten Umgebung. Vorher Daten, Secrets, Zertifikate, Compose/env und exaktes altes Image sichern. [Docker-Update/Rollback](UPDATE-DOCKER.de.md) oder [native Wartung](INSTALL-NATIVE.md) verwenden; eigene Portainer-/Compose-Stacks getrennt behandeln. Kein `down -v`/Pruning der einzigen Datenkopie.

Frische Daten verwenden `admin/admin`. Erhaltene Daten behalten das bisherige Passwort, die Bridge-Keys und absichtlich gesetzte Steuerungssperren. Für RC5-Altbestand erklärt die [gezielte Recovery](RECOVERY-CONTROL.de.md), warum ein gewöhnliches Update `0` nicht still in `1` umwandelt. Tokenpflicht und Lampenfähigkeiten gelten auch nach Freigabe.

Die gewählte veröffentlichte Version statt `latest` pinnen oder ihren Digest verwenden. Der [1.0.2-Digest-Nachweis](https://github.com/square-com-de/hue2lox/releases/download/v1.0.2/container-digests.json) bindet Plattform und Commit. Alte Releases bleiben unverändert.

## Historische Proxmox-Abnahme für 1.0.1

Ubuntu **26.04.1 amd64**, Docker **29.9.2**, Compose **5.6.1**: Image-/API-Login, Datenerhalt, Update und Restore/Rollback bestanden. Die exakte Quickstart-Datei ist inzwischen auch auf neuem Betriebssystem mit leerem Docker geprüft; Recovery mit deaktivierten Flags und echte Portainer-GUI bestanden. Reale Hardware bleibt separat. [Abschlussnachweis](acceptance/FINAL-CONTAINER-2026-10-25.md). [Nachweise und Grenzen](acceptance/PROXMOX-1.0.1.md). Die früheren fehlenden Runtime-Versionen sind damit für diese neue Teilabnahme erfasst.

## Offene Freigabe für 1.0.3

Die alten Clean-OS-, Flag-Recovery-, Portainer- und Deployment-Ergebnisse werden nicht als neue 1.0.3-Abnahme umetikettiert. Für den endgültigen Kandidaten gelten [Vorbereitung und offene Freigaben](PREPARATION-1.0.3.md). Die Veröffentlichungssperre bleibt geschlossen. Gemeinsame Hardwareprüfungen sind getrennt in [#42](https://github.com/square-com-de/hue2lox/issues/42) erfasst. Keine pauschale Plattform-, Miniserver-TLS- oder Hardwarefreigabe aus grüner CI ableiten.
