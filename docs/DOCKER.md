# Running the container image

For Docker-native hosts (Unraid, Synology, Portainer, plain Docker). Linux hosts that prefer a guided setup can still use `install-assistant.sh` ([INSTALL.md](../INSTALL.md)).

RC5 provides identical images at `docker.io/dubctrl/hue2lox:1.0.0-rc.5` and
`ghcr.io/square-com-de/hue2lox:1.0.0-rc.5` for
`linux/amd64` and `linux/arm64`. RC4 remains unchanged on GHCR; RC1–RC3 remain unchanged and ZIP-only.
[RC5 release, sources and license materials](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.5).

## Image tags

Use the exact version `1.0.0-rc.5` for this candidate. There are no floating `rc`
or minor-version tags. `latest` is reserved for a future stable release and is
not created by an RC.

```sh
docker pull ghcr.io/square-com-de/hue2lox:1.0.0-rc.5
# Alternatively, from Docker Hub:
podman pull docker.io/dubctrl/hue2lox:1.0.0-rc.5
```

The release workflow publishes only after a GitHub release is published and all
tests, scans and source-material checks pass. Pushing a branch/tag alone cannot
publish images. See [GHCR-RELEASE.md](GHCR-RELEASE.md).

## HTTP and HTTPS

The image serves **plain HTTP**. Like most self-hosted apps, it does not manage certificates: if you want HTTPS, terminate TLS in a reverse proxy in front of it and set `HUE_PUBLIC_URL` to the `https://` address. The proxy must forward the original `Host` header: the admin interface rejects requests whose `Host` or `Origin` differs from `HUE_PUBLIC_URL`. Without a proxy, the admin login and control token cross your network unencrypted, so only expose it on a network you trust.

Built-in HTTPS (as used by `install-assistant.sh`) is still available: set `TLS_CERT` and `TLS_KEY` to certificate and key files mounted into the container. Set both or neither: if only one is set, or either is empty, the container exits with an error instead of falling back to HTTP.

## Data volume

`/data` holds the bridge registry, admin credentials and control token. Back it up. The container runs as UID/GID 10001 and needs to be able to write there.

- **Named volume (the default in `compose.image.yaml`).** A new named volume starts out owned by 10001, so nothing needs preparing.
- **Host folder (bind mount).** Docker creates a missing host folder as `root`, which the container cannot write to. Create it first:

  ```sh
  mkdir -p /path/to/hue2lox/data && chown 10001:10001 /path/to/hue2lox/data
  ```

  If the folder is not writable the container exits immediately and prints this hint.

## Docker Compose

Copy the [RC5 Compose file](https://github.com/square-com-de/hue2lox/blob/v1.0.0-rc.5/docker/compose.image.yaml), save it as `compose.yaml`, set `PORT` and `HUE_PUBLIC_URL`, then:

```sh
docker compose up -d
```

On Linux, host networking is used so bridges can be discovered on the LAN; the service listens on `PORT`, so choose one that is free on the host.

The Compose example uses GHCR. To use Docker Hub, change only its `image` value
to `docker.io/dubctrl/hue2lox:1.0.0-rc.5`; both registries contain the same images.

## Podman Desktop on macOS

Pulling the image and pressing Play alone does not configure the browser address.
For a new local test, run this in the Mac terminal (choose another container and
volume name if these already exist):

```sh
podman run -d --name hue2lox-rc5-test \
  -p 127.0.0.1:18443:8443 \
  -e PORT=8443 \
  -e HUE_PUBLIC_URL=http://localhost:18443 \
  -v hue2lox-rc5-data:/data \
  --read-only --tmpfs /tmp --cap-drop=ALL \
  --security-opt=no-new-privileges \
  docker.io/dubctrl/hue2lox:1.0.0-rc.5
```

Open **http://localhost:18443** exactly. Initial login is `admin` / `admin`
for a fresh data volume; change the password after login. Keep `HUE_PUBLIC_URL`
aligned with the URL used in the browser. A mismatch can currently appear as an
incorrect-password error even with valid credentials.

Podman Desktop runs containers in a Linux VM on macOS. LAN multicast discovery
may not reach Hue bridges. If the search finds nothing, enter the bridge's LAN IP
in **Add Hue Bridge / Hue Bridge hinzufügen** below the search and pair it using
the bridge button. The bridge must be reachable from the VM. This localhost-only
example is for testing on the Mac, not for Loxone access from another machine.

## Unraid (Compose Manager)

Create a stack and paste the contents of `docker/compose.image.yaml`. The named volume works as is. To keep the data under appdata instead, prepare the folder from the Unraid terminal, then replace `hue2lox-data:/data` with the path and delete the `volumes:` block at the bottom:

```sh
mkdir -p /mnt/user/appdata/hue2lox/data && chown 10001:10001 /mnt/user/appdata/hue2lox/data
```

No source checkout or local build is needed.

## Lamp control

Lamp control is **on by default**: switching, dimming, RGB and tunable white all work once a bridge is paired. Control requests must carry the control token as `Authorization: Bearer ...`. The container creates the token on first start; the admin interface shows it and the Loxone export includes it. Without TLS or a reverse proxy the token crosses your network unencrypted, so only use it on a network you trust.

To run read-only (commands answer `403 writes_disabled` and nothing is sent to your bridges), set `HUE_WRITES_ENABLED=0`. The other two flags disable only RGB or tunable-white commands, respectively:

| Variable | Default | Controls |
| --- | --- | --- |
| `HUE_WRITES_ENABLED` | `1` | Switching and dimming. Setting it to `0` blocks every control command. |
| `HUE_COLOR_ENABLED` | `1` | RGB colour commands (also need `HUE_WRITES_ENABLED`). |
| `HUE_WHITE_ENABLED` | `1` | Tunable-white commands (also need `HUE_WRITES_ENABLED`). |

## Updating

```sh
docker compose pull && docker compose up -d
```

`/data` is kept across upgrades and existing files are never overwritten by the container. Back up `/data` first: the data format is not yet versioned for compatibility between release candidates.

## Settings

| Variable | Default | Meaning |
| --- | --- | --- |
| `PORT` | `8443` | Listen port |
| `HUE_PUBLIC_URL` | `https://localhost:8443` | Address used in the generated Loxone commands; an `https://` value also marks the login cookie `Secure` |
| `HUE2LOX_ADMIN_PASSWORD` | `admin` | Initial admin password, applied only when no credentials exist yet |
| `HUE_WRITES_ENABLED` | `1` | Allow switching and dimming (see Lamp control) |
| `HUE_COLOR_ENABLED` | `1` | Allow RGB colour commands |
| `HUE_WHITE_ENABLED` | `1` | Allow tunable-white commands |
| `TLS_CERT`, `TLS_KEY` | unset | Optional built-in HTTPS; set both or neither |

### Local bridge discovery from your computer

If container discovery finds no bridges, open **Bridges → No bridge found? Find its IP address locally** in the web interface. Choose macOS, Windows or Linux, copy the complete command and run it in your computer’s terminal (outside the container). Enter a returned IPv4 address in **Add Hue Bridge**.

The commands query only local mDNS, never an online discovery service. macOS uses `dns-sd`; Windows PowerShell 5.1/PowerShell 7 uses the built-in .NET UDP client; Linux requires `avahi-browse` and a running Avahi daemon. Installation hints appear in the Linux panel. The browser only displays and copies the commands; it does not execute them.

The computer or test VM must be on a network that can reach the bridges and receive local multicast replies. An isolated VM network, VPN, guest Wi-Fi or firewall may still prevent discovery. In that case, use the bridge address shown by your router. Do not disable your firewall to run the search.

### Lokale Bridge-Suche auf deinem Computer

Findet die Containersuche keine Bridges, öffne **Bridges → Keine Bridge gefunden? IP-Adresse lokal ermitteln**. Wähle Mac, Windows oder Linux, kopiere den gesamten Befehl und führe ihn im Terminal deines Computers aus (außerhalb des Containers). Trage eine gefundene IPv4-Adresse unter **Hue Bridge hinzufügen** ein.

Die Befehle fragen ausschließlich lokales mDNS ab, keinen Onlinedienst. macOS verwendet `dns-sd`, Windows PowerShell 5.1/PowerShell 7 den integrierten .NET-UDP-Client. Linux benötigt `avahi-browse` und einen laufenden Avahi-Dienst; Installationshinweise stehen im aufklappbaren Bereich. Der Browser zeigt und kopiert die Befehle, führt sie aber nicht aus.

Computer oder Test-VM müssen die Bridges im lokalen Netzwerk erreichen und Multicast-Antworten empfangen können. Bei isoliertem VM-Netz, VPN, Gast-WLAN oder Firewall kann auch diese Suche scheitern. Dann die Bridge-Adresse im Router nachsehen. Die Firewall für die Suche nicht abschalten.
