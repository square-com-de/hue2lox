**Use the 1.0.2 downloads only after its publication workflow succeeds. / Die 1.0.2-Downloads erst nach erfolgreichem Veröffentlichungsworkflow verwenden.**

**Release version: 1.0.2.** Use the fixed 1.0.2 Docker Hub or GHCR image after release publication completes. [Release notes](RELEASE-NOTES-1.0.2.md) describe the installed-version display; the direct desktop login fix from 1.0.1 is retained. The native adapter remains a separate experimental deployment path.

# Running the container image

**Start here:** [Storage, login, networking and HTTPS](CONTAINER-SETUP.md) · [Speicher, Anmeldung, Netzwerk und HTTPS (Deutsch)](CONTAINER-SETUP.de.md).

For Linux Docker Engine hosts; Unraid/Synology examples below are integration examples, not independent platform acceptance. See the [runtime matrix](RUNTIME-SUPPORT.md). Linux hosts that prefer a guided setup can still use `install-assistant.sh` ([INSTALL.md](../INSTALL.md)).

Stable 1.0.2 provides identical images at `docker.io/dubctrl/hue2lox:1.0.2` and
`ghcr.io/square-com-de/hue2lox:1.0.2` for
`linux/amd64` and `linux/arm64`. RC4 remains unchanged on GHCR; RC1–RC3 remain unchanged and ZIP-only.
[1.0.2 release, sources and license materials](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.2).

## Image tags

Use the exact version `1.0.2` for this release. There are no floating `rc`
or minor-version tags. `latest` follows the latest successfully verified stable release. RC releases never move it. Pin `1.0.2` to avoid unintended version changes.

```sh
docker pull ghcr.io/square-com-de/hue2lox:1.0.2
# Alternatively, from Docker Hub:
podman pull docker.io/dubctrl/hue2lox:1.0.2
```

The release workflow publishes only after a GitHub release is published and all
tests, scans and source-material checks pass. Pushing a branch/tag alone cannot
publish images. See [GHCR-RELEASE.md](GHCR-RELEASE.md).

## HTTP and HTTPS

In 1.0.2, direct localhost/private-IP access can leave `HUE_PUBLIC_URL` unset. Explicit values remain authoritative; forwarded headers cannot override them. Use [runtime-specific instructions](RUNTIME-SUPPORT.md).

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

Use the single [quick-start procedure](CONTAINER-SETUP.md#quick-start-docker-on-a-linux-server) / [deutscher Schnellstart](CONTAINER-SETUP.de.md#schnellstart-docker-auf-einem-linux-server). After publication it downloads the versioned Compose file and starts the fixed 1.0.2 image and creates persistent storage automatically. Open **http://SERVER-IP:18443**, sign in with **admin/admin** for fresh data and change the password. Portainer Docker Standalone uses that same file as a Stack.

HTTP is intentional and for a trusted LAN. HTTPS requires the [certificate/proxy setup](CONTAINER-SETUP.md#http-or-https). Bridge discovery can be limited by container networking; use local discovery help or the bridge IP. Direct bridge access still needs a network route. The guided installer and `compose.image.yaml` remain Linux host-network alternatives; they are not a second default installation path.

## Podman Desktop on macOS

**Historical verified scope:** Podman Desktop **1.30.5, macOS ARM64**, public `1.0.1` ARM64 image, fresh data, actual GUI pull/create/login/reload/restart. The instructions below target 1.0.2 after publication; they do not turn that historical evidence into a 1.0.2 public-image test. This is a local desktop test, not certification of Linux/Windows Podman, `podman compose`, multicast discovery or Loxone LAN access. [Evidence and limits](RUNTIME-SUPPORT.md).

1. In **Images → Pull an image**, enter `docker.io/dubctrl/hue2lox:1.0.2` (or the identical GHCR reference).
2. Choose **Run Image → Create and start**. Keep the displayed defaults and port mapping. Stop an older test container if its host port is occupied; keep its data volume.
3. Choose **Open Browser** and use the actual mapped **HTTP** URL. With a fresh writable `/data` volume, sign in with **admin / admin**. No URL/TLS environment variables are needed for direct localhost/private-IP access in 1.0.2.
4. Reload, restart the same container through Podman Desktop, and sign in again. Existing data always retains its previous password; pulling a newer image does not update an existing container.

For custom DNS/reverse proxies, set `HUE_PUBLIC_URL` to the exact browser URL and keep the original Host header. An address mismatch now has its own configuration error, not an incorrect-password message. Do not disable origin/CSRF checks or reset retained passwords to work around it.

Podman Desktop uses a Linux VM. Multicast may not cross its network. If discovery finds nothing, use **Bridges → No bridge found?** or enter the bridge IP; do not infer that a working GUI proves LAN discovery. A localhost URL cannot be used by a separate Loxone Miniserver. Pairing and real lamp effects need their own acceptance.

Deutsch: **Podman Desktop 1.30.5 auf macOS ARM64** wurde mit dem öffentlichen 1.0.1-Image geprüft; die folgenden Installationsangaben zielen nach Veröffentlichungsabschluss auf 1.0.2. Das ist noch keine 1.0.2-Registryabnahme: **Images → Pull an image → Run Image → Create and start → Open Browser → admin/admin** bei frischen Daten. Standard-Portzuordnung beibehalten, tatsächlich angezeigte HTTP-Adresse verwenden; keine zusätzlichen URL-/TLS-Variablen erforderlich. Neuladen und Neustart desselben Containers sind geprüft. Erhaltene Daten behalten ihr Passwort. Der Linux-Installer und `podman compose` sind dadurch nicht freigegeben. [Versionsstatus](RUNTIME-SUPPORT.de.md).

The [named-volume CLI variant](acceptance/DESKTOP-1.0.1.md#additional-named-volume-cli-check) was also checked on macOS ARM64 with Podman client/VM engine 6.1.4. For a persistent local test with an explicitly named volume, use the Mac terminal
(choose another container/volume name if occupied and a free localhost port; use the same port in the browser):

```sh
podman run -d --name hue2lox-test \
  -p 127.0.0.1:18443:8443 \
  -v hue2lox-data:/data \
  --read-only --tmpfs /tmp --cap-drop=ALL \
  --security-opt=no-new-privileges \
  docker.io/dubctrl/hue2lox:1.0.2
```

Open **http://localhost:18443**. Keep the named volume for subsequent containers.
Existing data retains its changed password. This localhost-only example is for
Mac testing, not access from a separate Loxone Miniserver.


See [storage and direct network diagnostics](CONTAINER-SETUP.md). Manual IP entry cannot bypass an unreachable VM-to-LAN route.

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

**Installer-created deployments:** use the complete [update/rollback guide](UPDATE-DOCKER.md) / [deutsche Anleitung](UPDATE-DOCKER.de.md), including a cold backup and the exact previous image. It covers local builds and pinned release images.

**Standalone Compose stacks using `/data`:** first stop the service and back up the complete named volume/bind mount, Compose/env/proxy/TLS configuration and exact current image. Change `image:` explicitly to the reviewed target release tag before `docker compose pull` and `docker compose up -d --no-build --wait`. Pulling the unchanged 1.0.2 tag is not a version upgrade. Verify health, image identity and login with the existing password. For rollback restore the saved Compose settings, exact old image and matching pre-update volume contents while stopped; image-only downgrades can leave incompatible data. Never use `down -v` or delete the only volume copy. Follow the stack provider's volume backup/restore procedure; the installer staging tool is not for standalone stacks.

## Settings

| Variable | Default | Meaning |
| --- | --- | --- |
| `PORT` | `8443` | Listen port |
| `HUE_PUBLIC_URL` | unset | Direct localhost/private-IP HTTP(S) uses the actual browser address/mapped port in 1.0.2. Set an exact URL for a proxy/custom DNS; explicit HTTPS uses Secure cookies |
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
