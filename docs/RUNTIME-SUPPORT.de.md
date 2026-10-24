# Runtime- und Versionsstatus

[English](RUNTIME-SUPPORT.md) · [Installation](../INSTALL.de.md) · [Lessons Learned](LESSONS-LEARNED.de.md)

Stand 24.10.2026, veröffentlichte Version **1.0.1**, Commit `f245a4ddd8857706f6ded748fb6945ea5aa88a38`. „Image startet“, „Login funktioniert“, „Lebenszyklus geprüft“ und „echte Lampenwirkung bestätigt“ sind unterschiedliche Nachweise.

| Weg | Belegter Umfang | Grenze |
|---|---|---|
| Linux Docker Engine + Compose-Plugin (`docker compose`) | [Release-CI](https://github.com/square-com-de/hue2lox/actions/runs/40100051393): frischer Start, HTTPS/Login, Installer/ZIP, Image-Update und exaktes Rollback; AMD64-/ARM64-Images gebaut, gestartet und anonym geladen | Kein Nachweis jeder Docker-/Compose-Version. Exakte Engine-/Compose-Versionen der historischen VM-Abnahme wurden im öffentlichen Bericht nicht erfasst; vor neuer Freigabe vom Deployer ergänzen. Compose muss die im Update verwendeten Optionen `--wait`/`--wait-timeout` unterstützen. |
| Podman Desktop **1.30.5, macOS ARM64** | Öffentliches 1.0.1-ARM64-Image: echter GUI-Pull, **Run Image → Create and start**, frische Daten, Browserlogin `admin/admin`, Reload und GUI-Neustart mit erneutem Login; zusätzlich Named-Volume-CLI-Ablauf unter macOS 27.0.1, Client/VM-Engine **6.1.4**, geprüft. [Abnahme](acceptance/DESKTOP-1.0.1.md) | Lokaler Desktop-Ablauf. Keine Freigabe für `podman compose`, den Docker-Installer unter Podman, Windows-/Linux-Podman oder LAN-Multicast. CLI-Version allein belegt diesen GUI-Weg nicht. |
| Nativ, systemd, **amd64**, experimentell | CI: Debian **12/13**, Ubuntu **24.04/26.04** isolierte Lebenszyklen. Reale frühere VMs: Ubuntu **26.04**, DietPi **13** auf dem [dort genannten Commit](DEPLOYMENT-ACCEPTANCE.md) | Historische Nachweise gelten nicht rückwirkend für jedes neue Archiv. Native ARM-/Raspberry-Pi-Abnahme fehlt. Python **3.11+** laut [nativer Anleitung](INSTALL-NATIVE.md), nicht allein durch OS-Namensähnlichkeit freigegeben. |
| LoxBerry | Bestehender Linux-/Docker-Weg auf einer konkreten LoxBerry-VM wurde separat betrieben | **Kein eigenes LoxBerry-Plugin und kein Plugin-ZIP.** Native Basis ist keine Plugin-Abnahme. |
| Unraid/Synology, Docker Desktop auf Mac/Windows, weitere Derivate | Container-/Compose-Beispiele sind Integrationshinweise | Keine pauschale Plattformfreigabe aus Linux-CI oder dem Mac-Podman-Test ableiten. Eigene Abnahme nötig. |

Die Distributionserkennung des Installers ist keine Hardwareabnahme. Die [Installationsmatrix](../INSTALL.de.md) nennt erkannte OS-Versionen; diese Tabelle begrenzt die tatsächlich nachgewiesenen Wege. Ein `amd64`-Image ist kein ARM-Image; ein 64-Bit-Prozessor mit 32-Bit-OS reicht nicht.

## Den richtigen Einstieg verwenden

- Linux: [versioniertes Quell-ZIP und geführter Installer](../INSTALL.de.md), oder [feste Compose-Datei](DOCKER.md#docker-compose). Den Docker-Installer nicht mit einem Podman-Alias ausführen.
- Geprüfter Mac-Desktop-Weg: [vier konkrete GUI-Schritte](DOCKER.md#podman-desktop-on-macos). Für localhost/private IP ist in 1.0.1 keine zusätzliche Browseradresse nötig. Eigene DNS-Namen/Reverse Proxy erfordern eine passende `HUE_PUBLIC_URL`.
- Nativ: [separates natives Archiv](INSTALL-NATIVE.md), dessen Version/Commit zum Quell-ZIP passt; keine Container-Flags auf einen systemd-Dienst übertragen.

## Update ist nicht Neustart

Eine neue Image-Version wird erst mit einem **neu erstellten Container** wirksam. Geänderte Umgebungsvariablen ebenfalls. `pull` lädt nur; `restart` startet denselben Container mit seinem alten Image/seiner alten Umgebung. Vorher Daten, Secrets, Zertifikate, Compose/env und exaktes altes Image sichern. [Docker-Update/Rollback](UPDATE-DOCKER.de.md) oder [native Wartung](INSTALL-NATIVE.md) verwenden; eigene Portainer-/Compose-Stacks getrennt behandeln. Kein `down -v`/Pruning der einzigen Datenkopie.

Frische Daten verwenden `admin/admin`. Erhaltene Daten behalten das bisherige Passwort, die Bridge-Keys und absichtlich gesetzte Steuerungssperren. Für RC5-Altbestand erklärt die [gezielte Recovery](RECOVERY-CONTROL.de.md), warum ein gewöhnliches Update `0` nicht still in `1` umwandelt. Tokenpflicht und Lampenfähigkeiten gelten auch nach Freigabe.

`1.0.1` statt `latest` pinnen, oder den veröffentlichten Digest verwenden. Der [Digest-Nachweis](https://github.com/square-com-de/hue2lox/releases/download/v1.0.1/container-digests.json) bindet Plattform und Commit. Alte Releases bleiben unverändert.

## Vor der nächsten Stable-Freigabe

Noch offen: unabhängige Abnahme der hier konsolidierten Anleitungen, Aufzeichnung der Docker-/Compose-Versionen und der tatsächlich ausgeführten Copy/Paste-Befehle, Prüfung von Recovery mit erhaltenem Passwort und bewusst deaktivierten Flags. Hardwareumfang explizit protokollieren; keine neuen Lampen-/Miniserver-Erfolge aus Mocks ableiten. Maintainer öffnet das [technische Stable-Gate](GHCR-RELEASE.md#stable-acceptance-gate) erst anhand dieser Nachweise. Die bereits veröffentlichten 1.0.0/1.0.1 werden nicht umgeschrieben.
