# Install Hue2Lox

[Deutsch](INSTALL.de.md)

Choose one of three paths. Containers need no Hue2Lox installer; use the guided installer for native installation.

| Path | Use | Guide |
| --- | --- | --- |
| Docker | Recommended on a Linux server with Docker Engine and Compose. | [Start Docker](docs/CONTAINER-SETUP.md#quick-start-docker-on-a-linux-server) |
| Podman | Container with persistent storage; observe desktop networking limits. | [Start Podman](docs/DOCKER.md#podman-desktop-on-macos) |
| Native | Experimental, systemd and explicitly tested amd64 systems. | [Native installer](#native-installer) |

## HTTP or HTTPS?

Docker/Podman images start with **HTTP** when TLS variables are absent, even on internal port 8443. The Docker quickstart publishes `http://SERVER-IP:18443`. The native installer configures **HTTPS with a self-signed certificate**. With **Traefik**, the browser uses HTTPS and Traefik forwards HTTP to Hue2Lox. `HUE_PUBLIC_URL` alone does not enable TLS. [Configuration location and complete Traefik example](docs/CONTAINER-SETUP.md#http-or-https).

## Native installer

Requirements: Debian 12/13, Ubuntu 24.04/26.04 or DietPi on Debian 12/13, **amd64**, systemd and root access. Native ARM/Raspberry Pi OS is currently unsupported. [Details and maintenance](docs/INSTALL-NATIVE.en.md).

On the Linux server, run `su -` and enter the root password first (Ubuntu alternatively `sudo -i`). **Then** run the following commands in the root shell. The download directory must not already exist.

```sh
apt update &&
apt install -y --no-install-recommends ca-certificates curl unzip python3 openssl &&
mkdir /root/hue2lox-native-1.0.2 &&
cd /root/hue2lox-native-1.0.2 &&
curl --fail --location --output hue2lox-v1.0.2.zip https://github.com/square-com-de/hue2lox/releases/download/v1.0.2/hue2lox-v1.0.2.zip &&
curl --fail --location --output hue2lox-1.0.2-native.tar.gz https://github.com/square-com-de/hue2lox/releases/download/v1.0.2/hue2lox-1.0.2-native.tar.gz &&
curl --fail --location --output SHA256SUMS.txt https://github.com/square-com-de/hue2lox/releases/download/v1.0.2/SHA256SUMS.txt &&
grep '  hue2lox-v1.0.2.zip$' SHA256SUMS.txt | sha256sum --check - &&
grep '  hue2lox-1.0.2-native.tar.gz$' SHA256SUMS.txt | sha256sum --check - &&
unzip -q hue2lox-v1.0.2.zip &&
cd hue2lox-v1.0.2 &&
bash install-assistant.sh --deployment native \
  --native-package /root/hue2lox-native-1.0.2/hue2lox-1.0.2-native.tar.gz \
  --native-sha256 "$(sha256sum /root/hue2lox-native-1.0.2/hue2lox-1.0.2-native.tar.gz | cut -d ' ' -f1)"
```

Both files must report `OK` before startup. In the menu check prerequisites, install missing base packages if required, verify the package and install natively using the server LAN IP and a free port. Open the displayed HTTPS address, verify its certificate fingerprint, sign in with `admin/admin` and change the password. Retained data keeps its existing password.

## Existing installation

Do not use fresh installation as an updater. [Docker update and rollback](docs/UPDATE-DOCKER.md) · [Native maintenance, rollback and retained data](docs/INSTALL-NATIVE.en.md). Existing Docker-installer deployments retain their documented maintenance path.
