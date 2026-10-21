# Install Hue2Lox on Linux

[Deutsch](INSTALL.de.md) · [RC3 release and ZIP](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.3) · [English manual](docs/MANUAL.md)

This guide installs **RC3** directly on the Linux server. The [version, package and checksum](docs/DOWNLOADS.md) belong together. The German manual development path uses `main` and is separate from this release installation.

## Requirements and supported systems

You need a Linux server or VM, its address and user account, root or sudo access, Internet access for packages and the Docker base image, and access to your Hue Bridge on the local network. Install the OS and SSH first; the installer cannot establish an SSH connection to a server without SSH. macOS and Windows are clients, not installation targets.

| 64-bit system | Automatic package setup | Observed test scope |
| --- | --- | --- |
| Ubuntu 22.04 / 24.04 / 26.04 LTS | amd64, arm64 | Ubuntu 26.04 amd64 through HTTPS health check; other variants pending |
| Debian 12 / 13 | amd64, arm64 | Debian 13 VM: installation, login, pairing, inventory and reboot confirmed by user on 20 October 2026; Debian 12/ARM pending |
| Raspberry Pi OS based on Debian 12 / 13 | arm64 | Detection tested automatically; physical Pi acceptance pending |
| DietPi based on Debian 12 / 13 | amd64, arm64 | Detection tested automatically; full platform acceptance pending |
| Other Linux distributions | Install prerequisites manually; existing Docker and Compose can be reused | No general compatibility claim |

A 64-bit processor with a 32-bit OS is not sufficient. Existing working Docker Engine and Compose are reused. The installer does not automatically remove conflicting Docker packages or overwrite existing installation directories. Images are built locally from source; no prebuilt Hue2Lox image is distributed.

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

## 3. Download RC3, verify and start

**Still on the server as root.** Copy the whole block. It creates a new download directory, downloads the fixed RC3 package and SHA-256 checksum, verifies and extracts it, then starts the installer. Existing directories are not overwritten.

```sh
HUE2LOX_DOWNLOAD_DIR=$(mktemp -d "$HOME/hue2lox-rc3-XXXXXXXX") &&
cd "$HUE2LOX_DOWNLOAD_DIR" &&
curl --fail --location --output hue2lox-v1.0.0-rc.3.zip \
  https://github.com/square-com-de/hue2lox/releases/download/v1.0.0-rc.3/hue2lox-v1.0.0-rc.3.zip &&
curl --fail --location --output SHA256SUMS.txt \
  https://github.com/square-com-de/hue2lox/releases/download/v1.0.0-rc.3/SHA256SUMS.txt &&
sha256sum --check SHA256SUMS.txt &&
unzip -tq hue2lox-v1.0.0-rc.3.zip &&
unzip -q hue2lox-v1.0.0-rc.3.zip &&
bash "$HUE2LOX_DOWNLOAD_DIR/hue2lox-v1.0.0-rc.3/install-assistant.sh"
```

Continue only when verification succeeds. On `FAILED`, download or extraction errors, stop; do not start the installer separately. The checksum must come from the same release as the ZIP. `Code → Download ZIP` downloads the development branch instead.

**Open again:** repeat the final `bash` command in the same root session. After reconnecting, use the actual download directory; `ls -d /root/hue2lox-rc3-*` lists the default paths. This extraction directory is separate from the eventual installation directory, such as `/opt/hue2lox-test`.

## 4. Continue in the installer

Select English when prompted. The menu offers:

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
