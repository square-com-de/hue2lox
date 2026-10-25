# Docker aktualisieren und zurücksetzen

[English](UPDATE-DOCKER.md)

Dieser Ablauf gilt für **Standardinstallationen des gemeinsamen Installers**, sowohl lokaler Build als auch festes Release-Image. Native Installationen verwenden die [native Wartung](INSTALL-NATIVE.md). Eigenständige Compose-/Portainer-Installationen mit `/data` verwenden ihren eigenen Stack und vollständige Volume-Sicherungen; das Vorbereitungswerkzeug unten ist dafür nicht geeignet.

RC1 und RC5 werden nicht verändert. Das Werkzeug ist seit dem Merge von PR #18 auf main enthalten; die [Deployment-Abnahme](DEPLOYMENT-ACCEPTANCE.md) ist bestanden. Die Zielversion ist im jeweils geprüften Quellpaket gebunden; den erfolgreichen Release-Abschluss vor einem Image-Update prüfen. Ein erneutes `pull` desselben Versions-Tags ist **kein Versionswechsel**. Ein veröffentlichtes RC5-Image enthält auch nach diesem Vorgang keine Änderungen des PRs. Updates zwischen inkompatiblen Datenschemata werden hier nicht zugesichert; Release-Hinweise prüfen.

## Welcher Updateweg passt?

- **Docker-/Portainer-Stack mit benanntem Volume:** [Stack-Update und vollständiger Rückweg](DOCKER.md#updating). Das gesamte Volume, Compose-/Proxy-Konfiguration und das exakte alte Image kalt sichern. Nicht den unten beschriebenen Installer-Staging-Helfer verwenden.
- **Podman:** Container mit derselben Volume-Zuordnung und neuer fester Image-Version neu erstellen; vorher Daten, Containerkonfiguration und exaktes altes Image sichern. Die Docker-Werkzeuge unten nicht unter einem Podman-Alias ausführen. [Containerweg und Grenzen](DOCKER.md#podman-desktop-on-macos).
- **Bestehender Docker-Installer:** Nur dafür gilt der folgende Ablauf. Angepasste Mounts/Overrides gesondert prüfen.
- **Nativ:** [Native Wartung und Rollback](INSTALL-NATIVE.md).

## Voraussetzungen und Zielstand

Als root mit `su -` anmelden und anschließend die Variablen setzen. Keine Befehle vor `su -` gesammelt einfügen: der Login startet eine neue Shell. Beispielpfade anpassen. `SOURCE` muss auf den **separaten neuen, geprüften Quellstand** zeigen, nicht auf die bestehende Installation. Checkout-Commit oder Release-Version und Archivprüfsumme dokumentieren. Die Test-VMs bleiben ohne konfigurierte Bridges/Miniserver.

```sh
su -
```

Danach in der Root-Shell:

```sh
set -eu
umask 077
INSTANCE=/opt/hue2lox-test
SOURCE=/home/lance/hue2lox-new
CANDIDATE="${INSTANCE}.update-candidate"
export HUE2LOX_INSTALL_LANG=de
cd "$INSTANCE"
test ! -e "$CANDIDATE"
```

Das Werkzeug akzeptiert nur eine unveränderte Standard-Compose-Datei des Installers. Eigene Mounts, Proxy-Labels oder andere Compose-Anpassungen werden abgelehnt und müssen vorher separat geprüft werden. IP, Port, Browseradresse, Projekt-/Containername, Steuerungsfreigaben und sonstige `.env`-Einstellungen bleiben erhalten. Auch ein bisher deaktivierter Steuerungszugriff bleibt deaktiviert. Keine Adress-/Zertifikatsmigration gleichzeitig durchführen.

## 1. Image ermitteln, stoppen und vollständig sichern

```sh
OLD_CONTAINER=$(docker compose ps -q hue2lox)
test -n "$OLD_CONTAINER"
OLD_IMAGE=$(docker inspect --format '{{.Image}}' "$OLD_CONTAINER")
docker compose down
BACKUP=$(mktemp -d /root/hue2lox-docker-update-XXXXXXXX)
chmod 700 "$BACKUP"
printf '%s\n' "$OLD_IMAGE" > "$BACKUP/image-id.txt"
docker image save --output "$BACKUP/image.tar" "$OLD_IMAGE"
cp -a "$INSTANCE" "$BACKUP/instance"
printf 'Geschützte Sicherung: %s\n' "$BACKUP"
```

Erst weitergehen, wenn **alle** Befehle erfolgreich waren. Die Sicherung enthält Code, `.env`, Compose, Registry, Passwortdaten, Token, Zertifikate und das exakte vorherige Image. Nicht öffentlich hochladen. Kein `down -v`, kein `prune`, keine globale Docker-/Host-Neustartaktion. Externe Neustartautomationen für diese Installation während der Wartung pausieren. Die Ausfallzeit beginnt mit `down`.

## 2. Genau einen Updateweg wählen

**Lokaler Build** – neuer Code aus dem geprüften Checkout, z. B. für ausdrücklich geprüfte Quelländerungen:

```sh
python3 "$SOURCE/scripts/prepare-docker-update.py" \
  --destination "$INSTANCE" --candidate "$CANDIDATE" --source build
cd "$CANDIDATE"
docker compose config --quiet
docker compose build
```

**Festes Release-Image** – statt des obigen Blocks:

```sh
python3 "$SOURCE/scripts/prepare-docker-update.py" \
  --destination "$INSTANCE" --candidate "$CANDIDATE" \
  --source image --registry ghcr
cd "$CANDIDATE"
docker compose config --quiet
docker compose pull hue2lox
```

`--registry dockerhub` ist die Alternative. Die Zielversion kommt aus `SOURCE/install/release-image.json`; diese Datei vorab prüfen. Das Werkzeug zeigt den vorbereiteten Pfad, die gespeicherte Referenz steht in der Kandidaten-`.env` als `HUE2LOX_IMAGE`. Es wird nie automatisch `latest` gewählt. Existiert noch kein neuer Release-Tag, gibt es keinen neuen veröffentlichten Image-Stand zu testen; lokal bauen. CI testet beide Registry-Wege mit ausschließlich lokal erzeugten Test-Images, ohne Release-Tags oder Registries zu verändern.

Das Vorbereitungswerkzeug startet keinen Container und verändert die bisherige Installation nicht. Es kopiert private Daten mit `cp -a`, erhält Eigentümer und Modi und übernimmt das bestehende Zertifikat. Temporär erzeugte Initialdaten des Kandidaten werden vollständig durch die gesicherten vorhandenen Kategorien ersetzt.

## 3. Auf den bisherigen Pfad wechseln und prüfen

```sh
cd /root
PREVIOUS="${INSTANCE}.before-update-$(date +%Y%m%d-%H%M%S)"
test ! -e "$PREVIOUS"
mv "$INSTANCE" "$PREVIOUS"
mv "$CANDIDATE" "$INSTANCE"
cd "$INSTANCE"
docker compose up -d --no-build --pull never --wait --wait-timeout 120
python3 "$SOURCE/scripts/start-install.py" --destination "$INSTANCE"
docker compose ps
```

`start-install.py` prüft die tatsächliche HTTP-/HTTPS-Adresse; bei HTTPS mit dem erhaltenen Zertifikat. Beim lokalen Build führt dieser zusätzliche Prüfaufruf ggf. einen gecachten Build aus; für vollständigen Offline-Betrieb stattdessen die nachfolgende direkte HTTP-/HTTPS-Prüfung verwenden. Bei einem Fehler stoppen und Abschnitt 4 verwenden. Keine Erfolgsmeldung aus einem früheren Schritt als Abnahme behandeln.

Bei HTTPS zusätzlich (IP und Port aus der bestehenden `.env` verwenden):

```sh
curl --noproxy '*' --fail --cacert "$INSTANCE/health-test.crt" \
  https://192.0.2.50:18443/health
```

Bei HTTP entsprechend `http://…/health` ohne `--cacert`; bei Reverse Proxy zusätzlich die öffentliche HTTPS-Adresse und Anmeldung prüfen. Im Browser mit dem **bisher geänderten Passwort** anmelden; Initialpasswort muss weiterhin scheitern. Einstellungen und Daten vergleichen, neues Image und neuen Code nachweisen. Einen Versionswechsel nicht allein aus dem Dateinamen eines Pakets ableiten. Container- und VM-Neustart prüfen. Echte Lampen-/Loxone-Tests separat abnehmen.

## 4. Vollständiges Rollback – Code UND damalige private Daten

`BACKUP` auf den zuvor ausgegebenen Sicherungsordner setzen. Änderungen nach der Sicherung, einschließlich eines später geänderten Passworts, gehen beim Rollback auf den gesicherten Stand zurück. Auch dann anwendbar, wenn Vorbereitung oder Build fehlschlagen und der bisherige Ordner noch aktiv ist.

```sh
cd "$INSTANCE"
docker compose down
cd /root
FAILED="${INSTANCE}.before-rollback-$(date +%Y%m%d-%H%M%S)"
test ! -e "$FAILED"
mv "$INSTANCE" "$FAILED"
cp -a "$BACKUP/instance" "$INSTANCE"
docker image load --input "$BACKUP/image.tar"
OLD_IMAGE=$(cat "$BACKUP/image-id.txt")
docker image inspect "$OLD_IMAGE" >/dev/null
printf 'services:\n  hue2lox:\n    image: "%s"\n' "$OLD_IMAGE" > "$BACKUP/rollback-image.yaml"
cd "$INSTANCE"
docker compose -f compose.yaml -f "$BACKUP/rollback-image.yaml" \
  up -d --no-build --pull never --wait --wait-timeout 120
RESTORED_CONTAINER=$(docker compose ps -q hue2lox)
test "$(docker inspect --format '{{.Image}}' "$RESTORED_CONTAINER")" = "$OLD_IMAGE"
```

Die Zusatzdatei erzwingt genau das gesicherte Image – ohne Neubau und ohne Download, auch beim ursprünglich lokalen Build. Für erneutes `up` während dieses zurückgesetzten Zustands beide `-f`-Dateien behalten; ein gewöhnliches `start-install.py` könnte wieder bauen bzw. die normale Image-Referenz verwenden. Gesundheitsprüfung direkt mit `curl` wie oben und persönliche Anmeldung mit dem **Passwort zum Sicherungszeitpunkt** wiederholen. Sicherungen und vorherige Verzeichnisse erst nach abgeschlossener Abnahme gezielt aufräumen.

## Abnahmekriterien

Neuer Anwendungscode bzw. neue Image-ID tatsächlich aktiv; unveränderte Registry, Token, bestehendes Passwort, Zertifikat, Browseradresse, Schaltfreigaben, Eigentümer und Modi nach Update. Nach Rollback exakt altes Image UND alter Datenstand. Ein bewusst nicht startfähiger Testkandidat darf keinen Erfolg melden; vollständige Rückkehr zur Sicherung muss funktionieren. Das sind Deployment-Prüfungen, keine allgemeine Migrationsfreigabe und keine Hardwareabnahme.

Für RC5→RC6 und ausdrückliche Steuerungsfreigabe die [konkrete Korrekturanleitung](RECOVERY-CONTROL.de.md).
