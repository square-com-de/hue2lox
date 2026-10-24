# Install Hue2Lox on Linux

**Preferred: Docker Compose in a Linux VM:** [container setup](docs/CONTAINER-SETUP.md) · [Compose guide](docs/DOCKER.md#docker-compose) · [test status](docs/RUNTIME-SUPPORT.md). The guided installer below is an alternative; native remains experimental. Start with the [tested download/start commands and login](docs/CONTAINER-SETUP.md#quick-start-docker-on-a-linux-server), without source code or mode selection. [Proxmox evidence and remaining limits](docs/CONTAINER-ACCEPTANCE-1.0.1.md).

### Simple start

Prerequisites: Linux with Docker Engine, the Compose plugin and curl; Docker permissions (for example `su -`) and free port **18443**. Run from the desired parent directory. The new `hue2lox` folder must not exist; maintain existing installations using the update procedure.

```sh
mkdir hue2lox &&
cd hue2lox &&
curl --fail --location --output compose.yaml https://raw.githubusercontent.com/square-com-de/hue2lox/bd8b4d172cafd8db9e602c992ec3e9704a4ce420/docker/compose.quickstart.yaml &&
docker compose up -d --wait &&
docker compose ps
```

Open **http://SERVER-IP:18443** using the Linux server’s private IP. Fresh data: **admin / admin**, then change the password. Storage is created automatically; retain the folder/project and volume during updates. HTTP is for a trusted LAN; HTTPS and other optional settings are described in the [container guide](docs/CONTAINER-SETUP.md). The isolated VM acceptance used the same file with test port **18444**, because 18443 was occupied there; the normal default is 18443.

Before starting a container: **[login, persistent storage, network access and HTTP/HTTPS](docs/CONTAINER-SETUP.md)**. Includes Portainer and Podman Desktop; explains why discovery and manual bridge access are different checks.

**Stable 1.0.1:** the shared installer offers Docker/native deployment. [Deployment acceptance passed](docs/DEPLOYMENT-ACCEPTANCE.md); [1.0.1 release notes](docs/RELEASE-NOTES-1.0.1.md). Native operation remains experimental and is included in 1.0.1; use the separate native archive with the source-ZIP assistant. See the [native guide](docs/INSTALL-NATIVE.en.md).

## Optional: guided installer or native installation

The installer on this page runs on **Linux with Docker Engine and the Compose plugin (`docker compose`)**, or in the explicitly selected native mode. **Podman is not a drop-in replacement for Docker in this installer.** For the tested local macOS ARM64 desktop flow, see [Podman Desktop](docs/DOCKER.md#podman-desktop-on-macos). See [runtime status](docs/RUNTIME-SUPPORT.md) for versions and acceptance limits; Linux Compose tests do not certify Docker Desktop, Windows Podman or every NAS platform.

Fresh data: `admin/admin`; retained data: the existing password. A healthy endpoint does not establish successful login or lamp control. Upgrade by replacing the container/service while retaining data using [Docker update/rollback](docs/UPDATE-DOCKER.md) or [native maintenance](docs/INSTALL-NATIVE.en.md). A restart alone adopts neither a new image nor changed environment variables. Ordinary updates preserve RC5 control restrictions: [intentional recovery](docs/RECOVERY-CONTROL.md).

[Deutsch](INSTALL.de.md) · [1.0.1 release and ZIP](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.1) · [English manual](docs/MANUAL.md)

This guide installs **1.0.1** directly on the Linux server. The [version, package and checksum](docs/DOWNLOADS.md) belong together. The German manual development path uses `main` and is separate from this release installation.

## Installer on main: Docker/native and prebuilt images

The installer defaults to a fixed release image from Docker Hub, with GHCR and local builds as alternatives. This choice is included in the 1.0.1 source ZIP. This release pins `1.0.1`; use the fixed image for normal installation, or **local build** to test a reviewed source checkout. See [image selection and scripted setup](docs/INSTALLER-IMAGES.md).

## HTTP or HTTPS in the installer

1.0.1 includes this choice. The older RC3 ZIP remains unchanged.
In step 5 choose:

1. **Direct HTTPS (default):** the installer creates a self-signed certificate and key.
   Open the displayed HTTPS address. Certificate renewal remains available.
2. **HTTP, for example behind Traefik:** the installer creates no server certificate
   and omits both TLS variables. Enter the browser address, e.g. `https://hue.example.org`,
   without a path or trailing slash. Press Enter to use the displayed direct HTTP address.

For a reverse proxy, route that browser address to `http://SERVER-IP:PORT`, preserve
its original Host header, and manage HTTPS/certificate renewal at the proxy.
Backend HTTP is unencrypted; restrict access to trusted clients/the proxy.
The installer checks the local backend, not the proxy configuration. Configure the
proxy before opening the HTTPS browser address. HTTPS browser addresses use Secure
session cookies even when the backend uses HTTP. Hue Bridge certificate validation
remains enabled in both modes.

The saved protocol, browser address and installation name are reused at start.
Existing installations are not converted or overwritten. For a separate trial,
choose a new directory and an unused port. For scripted preparation:

```sh
python3 scripts/prepare-install.py --destination /opt/hue2lox-proxy \
  --host 192.0.2.50 --port 18443 --scheme http --public-url https://hue.example.org
```

Omitting `--scheme` retains direct HTTPS. The script prepares files; start through
installer step 6 on the server. Certificate renewal on an HTTP installation is
handled by the proxy, not Hue2Lox.

## Requirements and supported systems

You need a Linux server or VM, its address and user account, root or sudo access, Internet access for packages and the Docker base image, and access to your Hue Bridge on the local network. Install the OS and SSH first; the installer cannot establish an SSH connection to a server without SSH. The guided installer itself runs on Linux. macOS/Windows can be clients; the separately tested macOS Podman Desktop path uses a Linux VM.

| 64-bit system | Automatic package setup | Observed test scope |
| --- | --- | --- |
| Ubuntu 22.04 / 24.04 / 26.04 LTS | amd64, arm64 | Main: Ubuntu 26.04 amd64 Docker/native update, rollback and reboot accepted; other variants separate |
| Debian 12 / 13 | amd64, arm64 | Debian 13 VM: installation, login, pairing, inventory and reboot confirmed by user on 20 October 2026; Debian 12/ARM pending |
| Raspberry Pi OS based on Debian 12 / 13 | arm64 | Detection tested automatically; physical Pi acceptance pending |
| DietPi based on Debian 12 / 13 | amd64, arm64 | Main: DietPi 13 amd64 Docker/native update, rollback and reboot accepted; DietPi 12/ARM separate |
| Other Linux distributions | Install prerequisites manually; existing Docker and Compose can be reused | No general compatibility claim |

The table separates automatic platform support from real testing. New VM evidence applies to the main commit in the [acceptance report](docs/DEPLOYMENT-ACCEPTANCE.md), not retroactively to the 1.0.1 ZIP.

A 64-bit processor with a 32-bit OS is not sufficient. Existing working Docker Engine and Compose are reused. The installer does not automatically remove conflicting Docker packages or overwrite existing installation directories. The 1.0.1 installer offers a fixed release image or a local build. For the prebuilt 1.0.1 image, use the separate [container guide](docs/DOCKER.md).

## 1. Connect to the server

**On your Mac in Terminal or on Windows in PowerShell:** replace `anna` with your server username and `192.0.2.50` with its IP.

```sh
ssh anna@192.0.2.50
```

In the server console, `whoami` shows the username and `hostname -I` shows addresses. You can also use PuTTY or the server's local console. Verify the SSH host fingerprint through the server console on first connection. If SSH is missing, run `apt update && apt install openssh-server` as root in the Linux console, then `systemctl enable --now ssh` and retry.

## 2. Use root and prepare the download tools

**Run the following commands as root on the Linux server.** If you are not already logged in as root:

- **Debian:** `su -` → enter the root password.
- **Ubuntu:** `sudo -i` → enter your own password.

Then continue in the same root session:

```sh
apt update &&
apt install -y --no-install-recommends ca-certificates curl unzip
```

This applies to the Ubuntu/Debian-based systems above. On other systems, provide these three tools using their package manager. Stop on errors; if you see “Not live until”, check the server clock first.

## 3. Download 1.0.1, verify and start

**Still on the server as root.** Copy the whole block. It creates a new download directory, downloads the fixed 1.0.1 package and SHA-256 checksum, verifies and extracts it, then starts the installer. Existing directories are not overwritten.

```sh
HUE2LOX_DOWNLOAD_DIR=$(mktemp -d "$HOME/hue2lox-rc6-XXXXXXXX") &&
cd "$HUE2LOX_DOWNLOAD_DIR" &&
curl --fail --location --output hue2lox-v1.0.1.zip \
  https://github.com/square-com-de/hue2lox/releases/download/v1.0.1/hue2lox-v1.0.1.zip &&
curl --fail --location --output SHA256SUMS.txt \
  https://github.com/square-com-de/hue2lox/releases/download/v1.0.1/SHA256SUMS.txt &&
(grep '  hue2lox-v1.0.1.zip$' SHA256SUMS.txt | sha256sum --check -) &&
unzip -tq hue2lox-v1.0.1.zip &&
unzip -q hue2lox-v1.0.1.zip &&
bash "$HUE2LOX_DOWNLOAD_DIR/hue2lox-v1.0.1/install-assistant.sh"
```

Continue only when verification succeeds. On `FAILED`, download or extraction errors, stop; do not start the installer separately. The checksum must come from the same release as the ZIP. `Code → Download ZIP` downloads the development branch instead.

**Open again:** repeat the final `bash` command in the same root session. After reconnecting, use the actual download directory; `ls -d /root/hue2lox-rc6-*` lists the default paths. This extraction directory is separate from the eventual installation directory, such as `/opt/hue2lox-test`.

## 4. Continue in the installer

Select English, then **Docker** for the steps below. For **native, without Docker**, follow the [native 1.0.1 handoff](docs/INSTALL-NATIVE.en.md#stable-source-zip-and-native-archive). The Docker menu offers:

1. Check the system and prerequisites without changes.
2. Check/configure SSH (optional; skip if already active).
3. Install base packages: Python, OpenSSL, curl, CA certificates and unzip.
4. Check/configure Docker and Compose. Existing working installations are reused.
5. Prepare Hue2Lox: choose the reachable server IPv4 address and an unused port; review and confirm them.
6. Start Hue2Lox and run its health check.
7. Choose another installation directory.

Use a separate installation directory (for example `/opt/hue2lox-test`). The installer refuses to overwrite an existing destination. Required dependencies are installed without optional package recommendations. An animated octopus shows progress; detailed output goes into protected logs whose location is displayed. Use `--verbose` for full terminal output.

The installation stores its generated container/project name in `.env`; preserve it for maintenance. Other Docker projects should remain running: do not stop Docker globally or run a system-wide prune.

## 5. Open and pair

Server commands below continue in the same root session. Adjust paths if you selected a different installation directory.

Open the HTTPS address printed by the installer, for example `https://192.0.2.50:18443`. The certificate is locally generated. Compare its SHA-256 fingerprint with the server output before adding a browser exception:

```sh
openssl x509 -in /opt/hue2lox-test/certs/server.crt -noout -fingerprint -sha256
```

Fresh installations enable control, RGB and Lumitech for supported lights immediately. Control commands still require a valid token. Updates and reinstalls retaining data preserve existing settings unchanged. The installer itself does not send light commands.

Initial login is **admin / admin**. You can change the password in the interface. Pair a bridge via **Bridges**, pressing its physical button when instructed. Check the inventory, then follow the [English Loxone tutorial](docs/TUTORIAL.md). Scenes are created in the Hue app. Actual Hue state is not synchronized back into the Loxone Lighting Controller.

For persistent browser trust, import only the public server certificate after checking its fingerprint; never share `server.key`. Certificates last 365 days and require renewal. Trust and HTTPS compatibility with the Miniserver are separate checks.

## Troubleshooting and maintenance

- **Incorrect time / “Not live until”:** check `date -u` and `timedatectl status` on the server; correct clock synchronization before retrying package installation.
- **Port already in use:** choose another free port. Do not stop unrelated containers.
- **Wrong IP or existing destination:** stop and inspect the installation before retrying. A changed IP can require a new certificate. Do not erase a paired installation to retry setup.
- **Bridge not found:** check the VM's LAN connectivity and firewall; manual bridge entry may be needed when multicast discovery cannot cross networks.
- **Start failed:** inspect the installation's own Compose project, replacing paths if you chose another directory:

```sh
docker compose --project-directory /opt/hue2lox-test --env-file /opt/hue2lox-test/.env -f /opt/hue2lox-test/compose.yaml ps
docker compose --project-directory /opt/hue2lox-test --env-file /opt/hue2lox-test/.env -f /opt/hue2lox-test/compose.yaml logs --tail=60
```

Read logs locally and remove credentials and personal details before sharing. Report the source version, OS/architecture, failing step and sanitized error in [Issues](https://github.com/square-com-de/hue2lox/issues).

The installer is for fresh installations, not a general updater. Preserve the whole installation including `.env`, data, secrets and certificates; follow [backup and recovery guidance](docs/MANUAL.md). Do not copy individual newer files into an existing release installation. The [German extended guide](INSTALL.de.md) also documents manual setup and specific network migration procedures; those sections are not yet translated.

## Maintenance / Wartung

[Certificate renewal, IP change, backup and restore / Zertifikat, IP-Wechsel und Sicherung](docs/MAINTENANCE.md)

For updates of deployments created by the development installer, follow [Docker update and rollback](docs/UPDATE-DOCKER.md). This adds a separate reviewed staging workflow; the fresh-install menu does not overwrite installations.

Existing installation? Use the [backup, update and rollback guide](docs/UPDATE-DOCKER.md).
