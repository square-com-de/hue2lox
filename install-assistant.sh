#!/usr/bin/env bash
# Optional interactive setup; no changes until a step is selected and confirmed.
set -Eeuo pipefail
SOURCE=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
DEST=/opt/hue2lox-test
# Selected language also reaches the Python preparation/start helpers.
export HUE2LOX_INSTALL_LANG=${HUE2LOX_INSTALL_LANG:-de}
translate() {
  if [[ "$HUE2LOX_INSTALL_LANG" == en ]]; then printf '%s' "$2"; else printf '%s' "$1"; fi
}
# Keep feedback distinct from menus, also in plain terminals and copied output.
feedback() {
  local kind=$1 message=$2 colour= reset= label
  case "$kind" in
    success) label=OK; colour='\033[1;32m';;
    error) label=$(translate 'FEHLER' 'ERROR'); colour='\033[1;31m';;
    *) label=$(translate 'HINWEIS' 'NOTE'); colour='\033[1;36m';;
  esac
  if [[ -t 1 && "${TERM:-dumb}" != dumb && -z "${NO_COLOR+x}" ]]; then
    reset='\033[0m'
  else
    colour=
  fi
  printf '\n%b  --> [%s] %s%b\n\n' "$colour" "$label" "$message" "$reset"
}
clear_screen() {
  # Clear the visible screen only; preserve scrollback and plain redirected output.
  if [[ -t 1 && "${TERM:-dumb}" != dumb ]]; then printf '\033[2J\033[H'; fi
}
installer_banner() {
  local rows=32 columns=80 colour= reset= size=
  if [[ -t 1 ]]; then
    size=$(stty size 2>/dev/null) || size=
    if [[ "$size" =~ ^([0-9]+)[[:space:]]+([0-9]+)$ ]]; then
      rows=${BASH_REMATCH[1]}; columns=${BASH_REMATCH[2]}
    fi
  fi
  if [[ -t 1 && "${TERM:-dumb}" != dumb && -z "${NO_COLOR+x}" ]]; then
    colour='\033[1;32m'; reset='\033[0m'
  fi
  printf '%b' "$colour"
  # Keep the menu and input visible in smaller terminal windows.
  if (( rows < 32 || columns < 62 )); then
    cat <<'ART'
       .----.
      ( o  o )   HUE2LOX
     __\ -- /__
    / / /||\ \ \   ~ ~ ~
    \_\_\||/_/_/
ART
  else
    cat <<'ART'
                         .-""""-.
                       .'        '.
                      /   o    o   \
                     |      __      |
               _      \   \____/   /      _
              / \   _.-'-.______.-'-._   / \
              \  \_/  /  / || \  \  \_/  /
               \_____/  /  ||  \  \_____/
                \______/   ||   \______/
                    \_____/  \_____/

   _   _ _   _ _____ ____  _     _____  __
  | | | | | | | ____|___ \| |   / _ \ \/ /
  | |_| | | | |  _|   __) | |  | | | \  /
  |  _  | |_| | |___ / __/| |__| |_| /  \
  |_| |_|\___/|_____|_____|_____\___/_/\_\
ART
  fi
  printf '%b\n  %s\n\n' "$reset" "$(translate 'ACHT ARME. ALLES IM GRIFF.' 'EIGHT ARMS. ALL UNDER CONTROL.')"
}
step_heading() {
  local number=$1 title colour= reset=
  case "$number" in
    1) title=$(translate 'SYSTEM & VORAUSSETZUNGEN' 'SYSTEM & PREREQUISITES');;
    2) title=$(translate 'SSH-SERVER' 'SSH SERVER');;
    3) title=$(translate 'GRUNDPAKETE INSTALLIEREN' 'INSTALL BASE PACKAGES');;
    4) title=$(translate 'DOCKER & COMPOSE' 'DOCKER & COMPOSE');;
    5) title=$(translate 'HUE2LOX VORBEREITEN' 'PREPARE HUE2LOX');;
    6) title=$(translate 'START & HEALTHCHECK' 'START & HEALTH CHECK');;
    7) title=$(translate 'INSTALLATIONSORDNER' 'INSTALLATION DIRECTORY');;
  esac
  if [[ -t 1 && "${TERM:-dumb}" != dumb && -z "${NO_COLOR+x}" ]]; then
    colour='\033[1;34m'; reset='\033[0m'
  fi
  printf '\n%b============================================================\n  %s %s | %s\n============================================================%b\n\n' \
    "$colour" "$(translate 'SCHRITT' 'STEP')" "$number" "$title" "$reset"
}
continue_to_menu() {
  local answer
  printf '\n------------------------------------------------------------\n'
  read -r -p "$(translate '[ Enter ] Weiter zum Menü ' '[ Enter ] Continue to menu ')" answer
}
status_row() {
  local kind=$1 name=$2 message=$3 colour= reset= marker
  case "$kind" in
    ok) marker=OK; colour='\033[1;32m';;
    missing) marker=$(translate 'FEHLT' 'MISSING'); colour='\033[1;33m';;
    *) marker=$(translate 'PRÜFEN' 'CHECK'); colour='\033[1;33m';;
  esac
  if [[ -t 1 && "${TERM:-dumb}" != dumb && -z "${NO_COLOR+x}" ]]; then reset='\033[0m'; else colour=; fi
  printf '  %b[%-7s]%b %-16s %s\n' "$colour" "$marker" "$reset" "$name" "$message"
}
welcome_heading() {
  local colour= reset=
  if [[ -t 1 && "${TERM:-dumb}" != dumb && -z "${NO_COLOR+x}" ]]; then
    colour='\033[1;36m'; reset='\033[0m'
  fi
  printf '\n\n%b================================================\n  HUE2LOX INSTALLER\n  Willkommen / Welcome\n================================================%b\n\n' "$colour" "$reset"
  printf '  Bitte Sprache wählen / Please select a language\n\n  [1] Deutsch\n  [2] English\n\n'
}
choose_language() {
  local language
  while true; do
    read -r -p 'Sprache / Language [1 Deutsch / 2 English]: ' language || return 1
    case "$language" in
      1|de|DE|Deutsch|deutsch) export HUE2LOX_INSTALL_LANG=de; return;;
      2|en|EN|English|english) export HUE2LOX_INSTALL_LANG=en; return;;
      *) printf 'Bitte 1 oder 2 wählen / Please choose 1 or 2.\n';;
    esac
  done
}
confirm() {
  local answer
  while true; do
    read -r -p "$1 $(translate '[J/n]' '[Y/n]'): " answer || return 1
    case "$answer" in
      ''|[jJ]|[jJ][aA]|[yY]|[yY][eE][sS]) return 0;;
      [nN]|[nN][eE][iI][nN]|[nN][oO]) return 1;;
      *) printf '%s\n' "$(translate 'Bitte ja/j oder nein/n eingeben.' 'Please enter yes/y or no/n.')";;
    esac
  done
}
run() {
  local label
  if [[ "$1" == apt-get ]]; then
    # Never continue with stale indexes after a signature/download failure.
    if [[ "${2:-}" == update ]]; then
      set -- apt-get -o APT::Update::Error-Mode=any "${@:2}"
      label=$(translate 'Paketlisten aktualisieren' 'Refreshing package lists')
    else
      label=$(translate 'Linux-Pakete einrichten' 'Setting up Linux packages')
    fi
    if [[ "${HUE2LOX_INSTALL_COMPACT:-0}" == 1 ]]; then
      if command -v python3 >/dev/null; then
        python3 "$SOURCE/scripts/installer_progress.py" "$label" "$1" -o Dpkg::Use-Pty=0 "${@:2}" || return $?
      else
        bash "$SOURCE/scripts/installer_bootstrap.sh" "$label" "$1" -o Dpkg::Use-Pty=0 "${@:2}" || return $?
      fi
      return
    fi
  elif [[ "$1" == systemctl && "${HUE2LOX_INSTALL_COMPACT:-0}" == 1 ]] && command -v python3 >/dev/null; then
    python3 "$SOURCE/scripts/installer_progress.py" "$(translate 'Dienst aktivieren' 'Enabling service')" "$@" || return $?
    return
  fi
  "$@" || return $?
}

root_required() {
  if (( EUID != 0 )); then
    printf "$(translate 'Für diesen Schritt bitte neu starten: sudo bash "%s/install-assistant.sh"\n' 'For this step, restart with: sudo bash "%s/install-assistant.sh"\n')" "$SOURCE"
    return 1
  fi
}
# Only explicitly supported releases/architectures may change host packages.
# Values are assigned only after all checks pass; derivatives are not guessed from ID_LIKE.
select_package_platform() {
  local distro=$1 version=$2 codename=$3 arch=$4 dietpi=$5 debian_version=$6 raspberry=$7
  local family suite label major
  DOCKER_FAMILY= DOCKER_SUITE= DOCKER_ARCH= PLATFORM_LABEL=
  case "$arch" in amd64|arm64) ;; *) return 1;; esac
  case "$distro" in
    ubuntu)
      [[ "$dietpi" == 0 ]] || return 1
      family=ubuntu; label=Ubuntu
      case "$version" in
        22.04) suite=jammy;;
        24.04) suite=noble;;
        26.04) suite=resolute;;
        *) return 1;;
      esac;;
    debian|raspbian|dietpi)
      family=debian; label=Debian
      major=${version%%.*}
      # DietPi release numbers are not Debian release numbers.
      if [[ "$distro" == dietpi ]]; then major=${debian_version%%.*}; fi
      case "$major" in 12) suite=bookworm;; 13) suite=trixie;; *) return 1;; esac
      if [[ "$distro" == raspbian || "$raspberry" == 1 ]]; then
        [[ "$arch" == arm64 ]] || return 1
        label='Raspberry Pi OS'
      fi
      if [[ "$dietpi" == 1 || "$distro" == dietpi ]]; then label=DietPi; fi;;
    *) return 1;;
  esac
  [[ -z "$codename" || "$codename" == "$suite" ]] || return 1
  DOCKER_FAMILY=$family DOCKER_SUITE=$suite DOCKER_ARCH=$arch PLATFORM_LABEL=$label
}
detect_package_platform() {
  # Optional filesystem root is used by fixture tests, never a CLI/environment override.
  local fsroot=${1:-} ID= VERSION_ID= VERSION_CODENAME= arch dietpi=0 raspberry=0 debian_version=
  [[ -r "$fsroot/etc/os-release" ]] || return 1
  . "$fsroot/etc/os-release"
  arch=$(dpkg --print-architecture) || return 1
  [[ ! -f "$fsroot/boot/dietpi/.version" ]] || dietpi=1
  [[ ! -f "$fsroot/etc/rpi-issue" ]] || raspberry=1
  if [[ -r "$fsroot/etc/debian_version" ]]; then read -r debian_version < "$fsroot/etc/debian_version" || true; fi
  select_package_platform "$ID" "$VERSION_ID" "$VERSION_CODENAME" "$arch" "$dietpi" "$debian_version" "$raspberry"
}
package_platform() {
  if ! detect_package_platform || ! command -v apt-get >/dev/null || ! command -v systemctl >/dev/null; then
    printf '%s\n' "$(translate 'Automatische Pakete: Ubuntu 22.04/24.04/26.04, Debian 12/13 oder Raspberry Pi OS/DietPi auf Debian 12/13, jeweils 64 Bit (amd64/arm64). System nicht eindeutig unterstützt: Voraussetzungen bitte manuell einrichten; vorhandenes Docker kann weiterverwendet werden.' 'Automatic packages: Ubuntu 22.04/24.04/26.04, Debian 12/13 or Raspberry Pi OS/DietPi based on Debian 12/13, 64-bit (amd64/arm64). System not clearly supported: install prerequisites manually; existing Docker can still be reused.')"
    return 1
  fi
  printf '%s: %s (%s, %s)\n' "$(translate 'Paketbasis erkannt' 'Package platform detected')" "$PLATFORM_LABEL" "$DOCKER_SUITE" "$DOCKER_ARCH"
}
docker_source() {
  printf 'Types: deb\nURIs: https://download.docker.com/linux/%s\nSuites: %s\nComponents: stable\nArchitectures: %s\nSigned-By: /etc/apt/keyrings/docker.asc\n' "$DOCKER_FAMILY" "$DOCKER_SUITE" "$DOCKER_ARCH"
}
status() {
  printf '\n=== %s ===\n\n' "$(translate 'SYSTEM & VORAUSSETZUNGEN' 'SYSTEM & PREREQUISITES')"
  printf 'System: '
  if [[ -r /etc/os-release ]]; then (. /etc/os-release; printf '%s\n' "$PRETTY_NAME"); else uname -s; fi
  if detect_package_platform; then
    printf '%s: %s (%s, %s)\n' "$(translate 'Automatische Paketinstallation' 'Automatic package installation')" "$PLATFORM_LABEL" "$DOCKER_SUITE" "$DOCKER_ARCH"
  else
    printf '%s\n' "$(translate 'Automatische Paketinstallation nicht unterstützt. Vorhandenes Docker kann genutzt werden.' 'Automatic package installation not supported. Existing Docker can be reused.')"
  fi
  printf "$(translate 'Architektur: ' 'Architecture: ')"; uname -m
  local cmd missing=0
  printf '\n'
  for cmd in python3 openssl curl unzip docker; do
    if command -v "$cmd" >/dev/null; then
      status_row ok "$cmd" "$(translate 'vorhanden' 'installed')"
    else
      status_row missing "$cmd" "$(translate 'noch installieren' 'needs installation')"
      missing=$((missing+1))
    fi
  done
  if command -v systemctl >/dev/null && systemctl is-active --quiet ssh; then
    status_row ok SSH "$(translate 'aktiv' 'active')"
  elif [[ -x /usr/sbin/sshd ]]; then status_row check SSH "$(translate 'installiert, Dienst nicht aktiv' 'installed, service is not active')"
  else status_row check SSH "$(translate 'nicht erkannt (optional)' 'not detected (optional)')"; fi
  if command -v docker >/dev/null; then
    if docker compose version >/dev/null 2>&1; then status_row ok Compose "$(translate 'verfügbar' 'available')"; else status_row missing Compose "$(translate 'nicht verfügbar' 'unavailable')"; fi
    if docker info >/dev/null 2>&1; then status_row ok Docker "$(translate 'Dienst erreichbar' 'service available')"; else status_row check Docker "$(translate 'Dienst/Rechte prüfen' 'check service/permissions')"; fi
  fi
  printf '\n'
  printf "$(translate 'Serveradressen: ' 'Server addresses: ')"; hostname -I 2>/dev/null || true
  printf "$(translate 'Installationsziel: %s\n' 'Installation directory: %s\n')" "$DEST"
  if (( missing > 0 )); then
    feedback note "$(translate 'Fehlende Grundpakete: Schritt 3. Docker/Compose: Schritt 4.' 'Missing base packages: step 3. Docker/Compose: step 4.')"
  fi
  if [[ -e "$DEST" ]]; then printf "$(translate 'Ziel existiert bereits – wird nicht neu vorbereitet oder überschrieben.\n' 'Destination already exists; it will not be prepared again or overwritten.\n')"; fi
}
ssh_setup() {
  root_required || return
  if systemctl is-active --quiet ssh; then feedback success "$(translate 'SSH ist bereits aktiv. Nichts zu tun.' 'SSH is already active. Nothing to do.')"; return; fi
  package_platform || return
  confirm "$(translate 'OpenSSH-Server installieren und SSH-Dienst aktivieren? Kein Root-Login wird freigeschaltet' 'Install OpenSSH server and enable SSH? Root login will not be enabled')" || return 0
  run apt-get update || return
  run apt-get install -y --no-install-recommends openssh-server || return
  run systemctl enable --now ssh || return
  feedback success "$(translate 'SSH ist einsatzbereit.' 'SSH is ready.')"
}
base_packages() {
  root_required || return
  package_platform || return
  confirm "$(translate 'Grundpakete python3, openssl, curl, ca-certificates und unzip installieren/aktualisieren?' 'Install/update python3, openssl, curl, ca-certificates and unzip?')" || return 0
  run apt-get update || return
  run apt-get install -y --no-install-recommends python3 openssl curl ca-certificates unzip || return
  feedback success "$(translate 'Grundpakete sind installiert.' 'Base packages are installed.')"
}
docker_setup() {
  root_required || return
  if command -v docker >/dev/null; then
    if docker compose version && docker info >/dev/null 2>&1; then
      feedback success "$(translate 'Docker und Compose sind einsatzbereit. Nichts zu tun.' 'Docker and Compose are ready. Nothing to do.')"; return
    fi
    printf "$(translate 'Vorhandene Docker-Installation erkannt, aber nicht vollständig erreichbar. Bitte Dienst/Rechte/Compose prüfen; kein automatisches Ersetzen.\n' 'Existing Docker installation is not fully available. Check the service, permissions and Compose; it will not be replaced automatically.\n')"; return 1
  fi
  package_platform || return
  local package
  for package in docker.io docker-compose docker-compose-v2 docker-doc docker-buildx podman-docker containerd runc docker-ce; do
    if dpkg-query -W -f='${Status}' "$package" 2>/dev/null | grep -q '^install ok installed$'; then
      printf "$(translate 'Vorhandenes Paket %s erkannt. Docker-Installation zuerst manuell klären; nichts entfernt.\n' 'Existing package %s detected. Check Docker installation manually first; nothing was removed.\n')" "$package"; return 1
    fi
  done
  if [[ -e /etc/apt/sources.list.d/docker.sources || -e /etc/apt/sources.list.d/docker.list ]]; then
    printf "$(translate 'Vorhandene Docker-Paketquelle erkannt. Bitte zuerst manuell prüfen; nichts überschrieben.\n' 'Existing Docker package source detected. Check it manually first; nothing was overwritten.\n')"; return 1
  fi
  confirm "$(translate 'Docker Engine, Buildx und Compose aus dem offiziellen Docker-Repository installieren und den Dienst aktivieren?' 'Install Docker Engine, Buildx and Compose from the official Docker repository and enable the service?')" || return 0
  run apt-get update || return
  run apt-get install -y --no-install-recommends ca-certificates curl || return
  run install -m 0755 -d /etc/apt/keyrings || return
  run curl -fsSL "https://download.docker.com/linux/$DOCKER_FAMILY/gpg" -o /etc/apt/keyrings/docker.asc || return
  run chmod a+r /etc/apt/keyrings/docker.asc || return
  docker_source > /etc/apt/sources.list.d/docker.sources || return
  run apt-get update || return
  run apt-get install -y --no-install-recommends docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin || return
  run systemctl enable --now docker || return
  run docker compose version || return
  run docker info >/dev/null || return
  feedback success "$(translate 'Docker und Compose sind einsatzbereit.' 'Docker and Compose are ready.')"
}
local_ipv4_addresses() {
  local addresses
  addresses=$(hostname -I 2>/dev/null) || addresses=
  python3 - "$addresses" <<'IPLIST'
import ipaddress, sys
seen = set()
for value in sys.argv[1].split():
    try:
        address = ipaddress.IPv4Address(value)
    except ValueError:
        continue
    if address.is_loopback or address.is_link_local or address.is_unspecified or address.is_multicast:
        continue
    if address not in seen:
        print(address)
        seen.add(address)
IPLIST
}
choose_server_ip() {
  local addresses address choice index
  local -a options=()
  SELECTED_IP=
  addresses=$(local_ipv4_addresses) || return 1
  while IFS= read -r address; do
    [[ -z "$address" ]] || options+=("$address")
  done <<< "$addresses"
  printf '%s\n' "$(translate 'IPv4-Adressen dieses Servers – wähle die im Heimnetz erreichbare Adresse:' 'IPv4 addresses of this server – choose the address reachable on your home network:')"
  if (( ${#options[@]} == 0 )); then
    printf '%s\n' "$(translate 'Keine IPv4-Adresse automatisch gefunden.' 'No IPv4 address found automatically.')"
  else
    for ((index=0; index<${#options[@]}; index++)); do
      printf '%s  %s\n' "$((index+1))" "${options[index]}"
    done
  fi
  printf '0  %s\n' "$(translate 'Adresse manuell eingeben' 'Enter address manually')"
  printf 'q  %s\n' "$(translate 'Abbrechen' 'Cancel')"
  while true; do
    read -r -p "$(translate 'Nummer wählen: ' 'Choose a number: ')" choice || return 1
    case "$choice" in
      q|Q) return 1;;
      0)
        read -r -p "$(translate 'Lokale IPv4-Adresse: ' 'Local IPv4 address: ')" SELECTED_IP || return 1
        [[ -n "$SELECTED_IP" ]] && return 0;;
      *)
        # Compare strings, never evaluate user input as a shell arithmetic expression.
        for ((index=0; index<${#options[@]}; index++)); do
          if [[ "$choice" == "$((index+1))" ]]; then
            SELECTED_IP=${options[index]}
            return 0
          fi
        done;;
    esac
    printf '%s\n' "$(translate 'Bitte eine angezeigte Nummer oder q wählen.' 'Please choose a listed number or q.')"
  done
}
prepare_setup() {
  root_required || return
  if [[ -e "$DEST" || -L "$DEST" ]]; then
    printf "$(translate 'Ziel %s existiert bereits. Schritt Starten wählen oder unter Fehlerbehebung nachlesen. Nichts überschrieben.\n' 'Destination %s already exists. Choose Start or see Troubleshooting. Nothing was overwritten.\n')" "$DEST"; return 1
  fi
  command -v python3 >/dev/null || { printf "$(translate 'Python fehlt: zuerst Grundpakete auswählen.\n' 'Python is missing: select Base packages first.\n')"; return 1; }
  command -v openssl >/dev/null || { printf "$(translate 'OpenSSL fehlt: zuerst Grundpakete auswählen.\n' 'OpenSSL is missing: select Base packages first.\n')"; return 1; }
  local ip port
  choose_server_ip || return
  ip=$SELECTED_IP
  read -r -p "$(translate 'Web-Port [18443]: ' 'Web port [18443]: ')" port
  port=${port:-18443}
  # Validate address ownership and availability before creating files or certificates.
  python3 - "$ip" "$port" <<'PY' || return
import ipaddress,socket,sys,os
en = os.environ.get("HUE2LOX_INSTALL_LANG") == "en"
try:
    host=str(ipaddress.IPv4Address(sys.argv[1])); port=int(sys.argv[2])
    if not 1024 <= port <= 65535: raise ValueError('Port must be between 1024 and 65535' if en else 'Port muss zwischen 1024 und 65535 liegen')
    with socket.socket() as sock: sock.bind((host,port))
except (ValueError,OSError) as error:
    sys.exit(('Address/port unavailable: ' if en else 'Adresse/Port nicht nutzbar: ')+str(error))
PY
  confirm "$(translate "Neue Installation in $DEST für https://$ip:$port vorbereiten?" "Prepare a new installation in $DEST for https://$ip:$port?")" || return 0
  run python3 "$SOURCE/scripts/prepare-install.py" --destination "$DEST" --host "$ip" --port "$port" || return
  feedback success "$(translate 'Vorbereitung abgeschlossen. Weiter mit Schritt 6.' 'Preparation complete. Continue with step 6.')"
}
start_setup() {
  root_required || return
  command -v python3 >/dev/null || { printf "$(translate 'Python fehlt: zuerst Grundpakete auswählen.\n' 'Python is missing: select Base packages first.\n')"; return 1; }
  confirm "$(translate "Installation in $DEST bauen/starten und HTTPS prüfen?" "Build/start installation in $DEST and check HTTPS?")" || return 0
  run python3 "$SOURCE/scripts/start-install.py" --destination "$DEST" || return
}
main() {
  export HUE2LOX_INSTALL_COMPACT=1
  if [[ "${1:-}" == --verbose ]]; then export HUE2LOX_INSTALL_COMPACT=0; shift; fi
  if [[ "${1:-}" == --check ]]; then status; return; fi
  if [[ -n "${1:-}" ]]; then printf "$(translate 'Aufruf: bash install-assistant.sh [--verbose] [--check]\n' 'Usage: bash install-assistant.sh [--verbose] [--check]\n')"; return 1; fi
  if [[ ! -t 0 ]]; then printf "$(translate 'Bitte interaktiv im Server-Terminal starten, nicht über eine Pipe.\n' 'Run interactively in the server terminal, not through a pipe.\n')"; return 1; fi
  welcome_heading
  choose_language || return 0
  local choice
  while true; do
    clear_screen
    installer_banner
    printf "$(translate 'Hue2Lox Installationsassistent – Linux: Ubuntu, Debian, Raspberry Pi OS 64 Bit und DietPi\nKeine Bridge wird gekoppelt; Lampensteuerung bleibt bei Neuinstallation aus.\n' 'Hue2Lox installation assistant – Linux: Ubuntu, Debian, Raspberry Pi OS 64-bit and DietPi\nNo bridge will be paired; light control stays disabled on a new installation.\n')"
    printf "$(translate '\n1  System und Voraussetzungen prüfen (nur lesen)\n2  SSH-Server prüfen/einrichten (optional)\n3  Grundpakete installieren\n4  Docker und Compose prüfen/einrichten\n5  Hue2Lox vorbereiten (IP und Port abfragen)\n6  Hue2Lox starten / Healthcheck\n7  Anderen Installationsordner wählen\n0  Beenden\n' '\n1  Check system and prerequisites (read only)\n2  Check/set up SSH server (optional)\n3  Install base packages\n4  Check/set up Docker and Compose\n5  Prepare Hue2Lox (choose IP and port)\n6  Start Hue2Lox / health check\n7  Choose another installation directory\n0  Exit\n')"
    read -r -p "$(translate 'Schritt wählen: ' 'Choose a step: ')" choice || return 0
    case "$choice" in
      [1-7]) clear_screen; step_heading "$choice";;
    esac
    case "$choice" in
      1) status || feedback error "$(translate 'Prüfung nicht vollständig.' 'Check incomplete.')";;
      2) ssh_setup || feedback error "$(translate 'SSH-Schritt gestoppt. Ursache prüfen, bevor du fortfährst.' 'SSH setup stopped. Check the cause before continuing.')";;
      3) base_packages || feedback error "$(translate 'Paketinstallation gestoppt. Ursache prüfen.' 'Package installation stopped. Check the cause.')";;
      4) docker_setup || feedback error "$(translate 'Docker-Schritt gestoppt. Ursache prüfen.' 'Docker setup stopped. Check the cause.')";;
      5) prepare_setup || feedback error "$(translate 'Vorbereitung gestoppt. Vorhandene Installation nicht überschrieben.' 'Preparation stopped. Existing installation was not overwritten.')";;
      6) start_setup || feedback error "$(translate 'Start nicht bestätigt. Fehlermeldung prüfen.' 'Startup not confirmed. Check the error message.')";;
      7) printf "$(translate 'Jede neue Installation erhält einen eigenen Namen. Bitte einen freien Port wählen.\n' 'Each new installation gets its own name. Please choose an unused port.\n')"; read -r -p "$(translate 'Absoluter Zielpfad: ' 'Absolute destination path: ')" choice; if [[ "$choice" == /* && "$choice" != / ]]; then DEST=$choice; else printf "$(translate 'Ungültiger Pfad.\n' 'Invalid path.\n')"; fi;;
      0) return 0;;
      *) printf "$(translate 'Bitte eine Zahl von 0 bis 7 wählen.\n' 'Please choose a number from 0 to 7.\n')";;
    esac
    continue_to_menu || return 0
  done
}
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then main "$@"; fi
