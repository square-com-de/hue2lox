# RC5 → RC6: Update und bewusste Freigabe der Steuerung

[English](RECOVERY-CONTROL.md)

**RC6 ist unveröffentlicht.** Diese Anleitung ist für die isolierte Abnahme mit den übergebenen lokalen RC6-Archiven gedacht; keine RC6-Images aus einer Registry ziehen. Produktion und Hardware bleiben unberührt.

Der RC5-Docker-Installer hat `HUE_WRITES_ENABLED`, `HUE_COLOR_ENABLED` und `HUE_WHITE_ENABLED` mit `0` gespeichert. Das direkte RC5-Image ohne solche Overrides hat dagegen Standardwerte `1`. RC6 setzt nur bei **Neuinstallationen** alle drei auf `1`. Updates behalten vorhandene Werte, auch bewusst gesetzte `0`. Daher ist eine Korrektur immer eine ausdrückliche Betreiberentscheidung. `1` erlaubt nur die von der jeweiligen Lampe unterstützten Schalt-/Dimm-/RGB-/TW-/Lumitech-Funktionen; Tokenpflicht und Capability-Prüfung bleiben bestehen. Pairings, Zugangsdaten und Lampenmodi werden nicht zurückgesetzt.

## 1. Standard-Docker-Installation sichern und vorbereiten

Gilt für den unveränderten RC5-Installer mit `compose.yaml`, `.env`, `data/`, `certs/`, `secrets/` im Installationsordner. Eigene Compose-/Portainer-Stacks, zusätzliche Overrides oder externe Volumes separat prüfen; diese Anleitung ist dafür keine Freigabe. Externe Neustartautomatik pausieren. Niemals `down -v`, Pruning oder globale Neustarts verwenden.

Vorher den neuen Quell-ZIP gegen den **separat übergebenen** SHA256 prüfen und außerhalb der Installation entpacken. `INSTANCE` an die bestehende Installation und `SOURCE` an diesen neuen Quellordner anpassen. Alle folgenden Abschnitte in derselben Root-Shell ausführen; nach einer Unterbrechung Variablen anhand der notierten Pfade neu setzen. `BACKUP` sicher notieren. `set -e` beendet bei Fehlern die Root-Shell; nicht blind fortsetzen.

```sh
su -
```

Erst nach dem Passwort und dem neuen Root-Prompt die folgenden Befehle eingeben:

```sh
set -eu
umask 077
INSTANCE=/opt/hue2lox
SOURCE=/home/lance/hue2lox-v1.0.0-rc.6
CANDIDATE="${INSTANCE}.rc6"
PREVIOUS="${INSTANCE}.before-rc6"
export HUE2LOX_INSTALL_LANG=de
test -d "$INSTANCE"
test -d "$SOURCE"
test ! -e "$CANDIDATE"
test ! -e "$PREVIOUS"
test -z "${COMPOSE_FILE:-}"
for name in compose.override.yaml compose.override.yml docker-compose.override.yaml docker-compose.override.yml; do
  test ! -e "$INSTANCE/$name"
done
python3 "$SOURCE/scripts/recover-control-flags.py" --settings "$INSTANCE/.env" --check
cd "$INSTANCE"
OLD_CONTAINER=$(docker compose ps -q hue2lox)
test -n "$OLD_CONTAINER"
OLD_IMAGE=$(docker inspect --format '{{.Image}}' "$OLD_CONTAINER")
BACKUP=$(mktemp -d /root/hue2lox-rc5-before-rc6-XXXXXXXX)
chmod 700 "$BACKUP"
printf '%s\n' "$OLD_IMAGE" > "$BACKUP/image-id.txt"
docker image save --output "$BACKUP/image.tar" "$OLD_IMAGE"
printf 'Protected backup: %s\n' "$BACKUP"
docker compose down
cp -a "$INSTANCE" "$BACKUP/instance"
(cd "$INSTANCE" && find data secrets -type f -exec sha256sum {} + && if test -d certs; then find certs -type f -exec sha256sum {} +; fi) > "$BACKUP/private-before.sha256"
python3 "$SOURCE/scripts/prepare-docker-update.py" \
  --destination "$INSTANCE" --candidate "$CANDIDATE" --source build
```

Ab `down` besteht Ausfallzeit. Die kalte Vollsicherung enthält Code, Konfiguration, Passwort-Hash, Tokens, Zertifikate und Registry sowie das genaue alte Image. Nur privat aufbewahren; keine Sicherungen oder Hashlisten veröffentlichen. Der Kandidat wird neben der alten Installation erstellt. Fehler beim Build: mit Abschnitt 4 die alte Installation aus der Sicherung starten.

## 2. Bewusst entscheiden und Container neu erstellen

`yes` aktiviert die drei Freigaben ausschließlich im neuen Kandidaten. `no` behält alle Werte; bei alten `0` bleibt die Steuerung entsprechend gesperrt. Die Eingabe ist Pflicht. Das Hilfsprogramm zeigt nur die drei Flags und einen privaten Sicherungspfad, keine Geheimnisse. Es verweigert mehrdeutige/angepasste Dateien, statt sie zu überschreiben.

```sh
printf 'Unterstuetzte Steuerung bewusst freigeben? [yes/no]: '
read -r ENABLE_CONTROL
case "$ENABLE_CONTROL" in
  yes) python3 "$SOURCE/scripts/recover-control-flags.py" \
         --settings "$CANDIDATE/.env" --enable-supported-control ;;
  no) python3 "$SOURCE/scripts/recover-control-flags.py" \
        --settings "$CANDIDATE/.env" --check ;;
  *) echo 'Abgebrochen: yes oder no erforderlich.'; exit 1 ;;
esac
(cd "$CANDIDATE" && docker compose config --quiet && docker compose build)
cd /root
mv "$INSTANCE" "$PREVIOUS"
mv "$CANDIDATE" "$INSTANCE"
cd "$INSTANCE"
docker compose up -d --no-build --pull never --wait --wait-timeout 120
sha256sum --check "$BACKUP/private-before.sha256"
NEW_CONTAINER=$(docker compose ps -q hue2lox)
NEW_IMAGE=$(docker inspect --format '{{.Image}}' "$NEW_CONTAINER")
test "$NEW_IMAGE" != "$OLD_IMAGE"
python3 "$SOURCE/scripts/recover-control-flags.py" --settings "$INSTANCE/.env" --check
```

**`docker compose restart` genügt nicht:** geänderte Umgebungsvariablen werden erst beim Neuerstellen übernommen. Kein erneutes Pairing und kein neuer Token. RC6 wird vor Veröffentlichung aus dem neuen lokalen Quellstand gebaut; später ist der [gepinnte Image-Updateweg](UPDATE-DOCKER.de.md) separat verfügbar.

## 3. Tatsächliche Anwendung und Datenerhalt prüfen

Im Beispiel wurde bereits vorher `127.0.0.1:18443` mit HTTPS verwendet. Die URL durch den **bisherigen echten Endpunkt** ersetzen; für HTTP ohne `--cacert`. Keine Netzwerk-/Zertifikatsmigration mit diesem Update verbinden. Die zweite Prüfung vergleicht eine echte RC6-Datei, die RC5 noch nicht enthält; eine geänderte Versionsnummer allein ist kein Code-Update.

```sh
curl --noproxy '*' --fail --cacert "$INSTANCE/health-test.crt" \
  https://127.0.0.1:18443/health
curl --noproxy '*' --fail --cacert "$INSTANCE/health-test.crt" \
  https://127.0.0.1:18443/assets/sidebar-icons.svg --output /root/rc6-sidebar-icons.svg
cmp "$SOURCE/web/sidebar-icons.svg" /root/rc6-sidebar-icons.svg
```

Im Browser mit dem bisherigen geänderten Passwort anmelden; `admin` als Passwort muss weiterhin abgewiesen werden. Discovery-Hilfe und neue Symbole ansehen. Registry, Tokens, Zertifikate sowie Besitzer und Dateimodi mit der kalten Sicherung vergleichen, ohne Inhalte auszugeben. Privatdateihashes müssen übereinstimmen; `.env` darf ausschließlich die gewählte Deployment-Quelle und die ausdrücklich freigegebenen Flags ändern. Nach Container- und VM-Neustart erneut HTTPS/Login prüfen. Ohne gekoppelte Hardware testen; Steuer-/Token-/Capability-Tests verwenden ausschließlich isolierte Fixtures. Echte Hue-/Loxone-Abnahme bleibt offen.

## 4. Exaktes Rollback: altes Image UND alter Zustand

`BACKUP` muss auf den zuvor gedruckten Pfad zeigen. Passwort-/Datenänderungen seit der Sicherung werden zurückgesetzt. Auch nach Vorbereitung-/Buildfehlern bei noch unverändertem `INSTANCE` anwendbar. Einen fehlgeschlagenen RC6-Ordner aufbewahren.

```sh
# BACKUP=/root/hue2lox-rc5-before-rc6-EXACT_PRINTED_SUFFIX
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
sha256sum --check "$BACKUP/private-before.sha256"
cmp "$BACKUP/instance/.env" "$INSTANCE/.env"
```

Erneut den direkten Healthcheck und Login mit dem **Passwort zum Sicherungszeitpunkt** prüfen. Für spätere `up`-Befehle beide `-f`-Dateien beibehalten; der normale Starthilfebefehl könnte sonst ein anderes Image bauen/auswählen. Sicherung und vorherige/fehlgeschlagene Ordner bis zur vollständigen Abnahme behalten.

## 5. Native Entwicklungsinstallation: eigener Weg

RC5 hatte **kein natives Release-Paket**. Der folgende Weg gilt ausschließlich für bereits protokollierte experimentelle native Installationen, nicht als „native RC5-Migration“. Quell-ZIP und natives RC6-Archiv separat gegen die übergebenen SHA256 prüfen. In einer Root-Shell:

```sh
python3 "$SOURCE/scripts/recover-control-flags.py" --settings /etc/hue2lox/settings.env --check
sh "$SOURCE/deployment/native/update.sh" \
  --package /home/lance/hue2lox-1.0.0-rc.6-native.tar.gz \
  --sha256 "$VERIFIED_NATIVE_SHA256"
```

`VERIFIED_NATIVE_SHA256` vorher auf den unabhängig übergebenen Hash setzen. Den **vom Updater gedruckten** geschützten Sicherungspfad unter `/var/backups/hue2lox/` notieren. Der Updater behält vorhandene Flags. Falls die Steuerung ausdrücklich freigegeben werden soll (sonst diesen Block überspringen):

```sh
systemctl stop hue2lox
python3 "$SOURCE/scripts/recover-control-flags.py" \
  --settings /etc/hue2lox/settings.env --enable-supported-control
systemctl restart hue2lox
python3 "$SOURCE/scripts/native-assistant.py" health
```

Bei Fehlern abbrechen. Rollback mit dem exakt notierten Sicherungspfad, anschließend Healthcheck und bisherige Anmeldung prüfen:

```sh
sh "$SOURCE/deployment/native/rollback.sh" --backup /var/backups/hue2lox/EXACT_PRINTED_BACKUP
python3 "$SOURCE/scripts/native-assistant.py" health
```

Das native Rollback stellt Code **und** den damaligen privaten Zustand einschließlich alter Flags wieder her. Keine unbekannten Schemamigrationen oder nativen ARM-Plattformen zugesichert.
