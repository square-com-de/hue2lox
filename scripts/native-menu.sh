#!/usr/bin/env bash
# Sourced by the common assistant. No host changes at load time.
DEPLOYMENT=docker
NATIVE_PACKAGE=
NATIVE_SHA256=
NATIVE_WORK=

choose_deployment() {
  local answer
  printf '\n%s\n' "$(translate 'WIE MÖCHTEST DU HUE2LOX INSTALLIEREN?' 'HOW WOULD YOU LIKE TO INSTALL HUE2LOX?')"
  printf '%s\n' "$(translate '1  Mit Docker' '1  With Docker')"
  printf '%s\n' "$(translate '2  Nativ, ohne Docker (experimentell)' '2  Native, without Docker (experimental)')"
  while true; do
    read -r -p "$(translate 'Installationsweg [1/2]: ' 'Installation method [1/2]: ')" answer || return 1
    case "$answer" in
      1) DEPLOYMENT=docker; return;;
      2) DEPLOYMENT=native; return;;
      *) printf '%s\n' "$(translate 'Bitte 1 oder 2 wählen.' 'Please choose 1 or 2.')";;
    esac
  done
}
native_package_platform() {
  if ! detect_package_platform || [[ "$DOCKER_ARCH" != amd64 || "$PLATFORM_LABEL" == 'Raspberry Pi OS' || ( "$DOCKER_FAMILY" == ubuntu && "$DOCKER_SUITE" == jammy ) ]]; then
    feedback error "$(translate 'Native Testziele: Debian 12/13, Ubuntu 24.04/26.04, DietPi auf Debian 12/13; derzeit amd64. Python ab 3.11 und systemd erforderlich.' 'Native test targets: Debian 12/13, Ubuntu 24.04/26.04, DietPi on Debian 12/13; currently amd64. Python 3.11+ and systemd required.')"
    return 1
  fi
}
native_prerequisites() {
  root_required || return
  command -v python3 >/dev/null || { feedback error "$(translate 'Zuerst Grundpakete installieren.' 'Install base packages first.')"; return 1; }
  run python3 "$SOURCE/deployment/native/manage.py" check
}
native_status() {
  printf '\n%s\n' "$(translate 'NATIVER BETRIEB – EXPERIMENTELL' 'NATIVE DEPLOYMENT – EXPERIMENTAL')"
  if native_package_platform; then printf '%s: %s (%s)\n' "$(translate 'Testplattform' 'Test platform')" "$PLATFORM_LABEL" "$DOCKER_ARCH"; fi
  local cmd
  for cmd in python3 openssl systemctl useradd groupadd; do
    if command -v "$cmd" >/dev/null; then status_row ok "$cmd" "$(translate 'vorhanden' 'installed')"; else status_row missing "$cmd" "$(translate 'noch installieren' 'needs installation')"; fi
  done
  printf '%s\n' "$(translate 'Code: /opt/hue2lox · Konfiguration: /etc/hue2lox · Daten: /var/lib/hue2lox' 'Code: /opt/hue2lox · Configuration: /etc/hue2lox · State: /var/lib/hue2lox')"
  if [[ -e /etc/hue2lox/install.json ]]; then feedback note "$(translate 'Vorhandene native Einrichtung erkannt. Für Update oder Wiederinstallation die Wartung wählen.' 'Existing native deployment detected. Select maintenance for update or reinstall.')"; fi
}
native_cleanup() {
  if [[ -n "$NATIVE_WORK" ]]; then rm -rf -- "$NATIVE_WORK"; NATIVE_WORK=; fi
}
native_prepare_package() {
  native_prerequisites || return
  if [[ -n "$NATIVE_PACKAGE" || -n "$NATIVE_SHA256" ]]; then
    [[ -n "$NATIVE_PACKAGE" && -n "$NATIVE_SHA256" ]] || { feedback error "$(translate 'Paketdatei und SHA-256 gehören zusammen.' 'Package file and SHA-256 are both required.')"; return 1; }
    run python3 "$SOURCE/scripts/native-assistant.py" inspect --package "$NATIVE_PACKAGE" --sha256 "$NATIVE_SHA256" || return
    return
  fi
  if [[ -e "$SOURCE/.git" ]]; then
    confirm "$(translate 'Entwicklungspaket lokal aus diesem sauberen, geprüften Git-Stand erstellen? Kein Download und kein Release.' 'Build a development package locally from this clean, reviewed Git checkout? No download or release.')" || return 0
    [[ -n "$NATIVE_WORK" ]] || NATIVE_WORK=$(mktemp -d /tmp/hue2lox-assistant.XXXXXXXX) || return
    run python3 "$SOURCE/scripts/native-assistant.py" build --output "$NATIVE_WORK" || return
    NATIVE_PACKAGE=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["package"])' "$NATIVE_WORK/package.json") || return
    NATIVE_SHA256=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["sha256"])' "$NATIVE_WORK/package.json") || return
  else
    feedback note "$(translate 'Dieser Quellordner hat keine Git-Identität. Ein separat geprüftes natives Paket mit SHA-256 auswählen. RC5 enthält kein natives Paket.' 'This source directory has no Git identity. Select an independently verified native package and SHA-256. RC5 contains no native package.')"
    read -r -p "$(translate 'Absoluter Paketpfad: ' 'Absolute package path: ')" NATIVE_PACKAGE || return 1
    read -r -p "$(translate 'Unabhängig geprüfte SHA-256: ' 'Independently verified SHA-256: ')" NATIVE_SHA256 || return 1
    run python3 "$SOURCE/scripts/native-assistant.py" inspect --package "$NATIVE_PACKAGE" --sha256 "$NATIVE_SHA256" || return
  fi
}
native_require_package() {
  if [[ -z "$NATIVE_PACKAGE" ]]; then native_prepare_package || return; fi
  [[ -n "$NATIVE_PACKAGE" && -n "$NATIVE_SHA256" ]] || { feedback note "$(translate 'Kein Paket vorbereitet; nichts installiert.' 'No package prepared; nothing installed.')"; return 1; }
}
prepare_native_setup() {
  native_prerequisites || return
  if [[ -e /opt/hue2lox || -L /opt/hue2lox || -e /etc/hue2lox || -L /etc/hue2lox || -e /var/lib/hue2lox || -L /var/lib/hue2lox ]]; then
    feedback error "$(translate 'Native Dateien existieren bereits. Wartung wählen: Update oder Wiederinstallation mit Datenerhalt. Nichts überschrieben.' 'Native files already exist. Choose maintenance: update or reinstall with retained data. Nothing overwritten.')"
    return 1
  fi
  native_require_package || return
  choose_server_ip || return
  local ip=$SELECTED_IP port
  read -r -p "$(translate 'HTTPS-Port [18443]: ' 'HTTPS port [18443]: ')" port || return 1
  port=${port:-18443}
  confirm "$(translate "Nativ unter https://$ip:$port installieren? systemd-Dienst und feste Systemverzeichnisse werden angelegt. Steuerung bleibt aus." "Install natively at https://$ip:$port? Creates a systemd service and fixed system directories. Control stays disabled.")" || return 0
  run python3 "$SOURCE/deployment/native/manage.py" install --package "$NATIVE_PACKAGE" --sha256 "$NATIVE_SHA256" --host "$ip" --port "$port"
}
native_health() {
  native_prerequisites || return
  run python3 "$SOURCE/scripts/native-assistant.py" health
}
native_maintenance() {
  native_prerequisites || return
  local choice saved endpoint ip port
  printf '\n%b\n' "$(translate '1  Update mit Sicherung\n2  Wiederinstallation mit Datenerhalt (gleiches Paket)\n3  Rollback aus vollständiger Sicherung\n4  Deinstallation mit Datenerhalt\n0  Zurück' '1  Update with backup\n2  Reinstall retaining data (same package)\n3  Roll back from a complete backup\n4  Uninstall retaining data\n0  Back')"
  read -r -p "$(translate 'Wartung wählen: ' 'Choose maintenance: ')" choice || return 1
  case "$choice" in
    1)
      native_require_package || return
      confirm "$(translate 'Dienst stoppen, sichern und mit dem gewählten Paket aktualisieren?' 'Stop service, back up and update using the selected package?')" || return 0
      run python3 "$SOURCE/deployment/native/manage.py" update --package "$NATIVE_PACKAGE" --sha256 "$NATIVE_SHA256";;
    2)
      native_require_package || return
      endpoint=$(python3 "$SOURCE/scripts/native-assistant.py" endpoint) || return
      read -r ip port <<< "$endpoint"
      confirm "$(translate 'Gleiches Paket mit erhaltenen Daten wieder installieren? Vorherige Deinstallation erforderlich.' 'Reinstall the same package with retained data? Requires prior uninstall.')" || return 0
      run python3 "$SOURCE/deployment/native/manage.py" install --keep-data --package "$NATIVE_PACKAGE" --sha256 "$NATIVE_SHA256" --host "$ip" --port "$port";;
    3)
      read -r -p "$(translate 'Vollständiger Backup-Pfad unter /var/backups/hue2lox/: ' 'Complete backup path under /var/backups/hue2lox/: ')" saved || return 1
      confirm "$(translate 'Code UND damaligen Datenstand wiederherstellen? Spätere Passwort-/Inventaränderungen werden zurückgesetzt.' 'Restore code AND historical data? Later password/inventory changes will be reverted.')" || return 0
      run python3 "$SOURCE/deployment/native/manage.py" rollback --backup "$saved";;
    4)
      confirm "$(translate 'Nativen Dienst und Code entfernen? Private Daten und Sicherungen bleiben erhalten.' 'Remove native service and code? Private data and backups are retained.')" || return 0
      run python3 "$SOURCE/deployment/native/manage.py" uninstall;;
    0) return 0;;
    *) feedback error "$(translate 'Ungültige Auswahl; nichts geändert.' 'Invalid choice; nothing changed.')"; return 1;;
  esac
}
