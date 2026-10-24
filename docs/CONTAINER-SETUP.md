# Container setup: login, storage, networking and HTTPS

[Deutsch](CONTAINER-SETUP.de.md) · [Container guide](DOCKER.md) · [Linux installer](../INSTALL.md)

These notes apply to the published Hue2Lox image starting with **1.0.1**. A quick desktop test and a persistent deployment need different preparation. Downloading an image does not update an existing container.

## Before starting

| Setting | Value |
|---|---|
| Image | `docker.io/dubctrl/hue2lox:1.0.1` or `ghcr.io/square-com-de/hue2lox:1.0.1` |
| Storage | Named volume `hue2lox-data` → container path `/data`, writable |
| Published port | Free host port such as `18443` → container TCP port `8443` |
| Browser | Without TLS, `http://SERVER-IP:18443`; on the same computer, `http://localhost:18443` also works |
| First login | `admin` / `admin` with fresh data; then change the password in the UI |
| Browser address | Direct localhost/private-IP access needs no `HUE_PUBLIC_URL`; set the exact browser URL for custom DNS names/reverse proxies |

**A port number does not enable HTTPS.** Port 8443 still serves HTTP without TLS configuration. `localhost` means the computer running the browser; a Loxone Miniserver needs a server address it can reach.

## Where is my data?

The image stores its state under **`/data`**, including the bridge registry and pairing data, admin credentials (password hash), control token and saved settings. Back up the entire volume, not just one file. Also back up separately mounted TLS files and deployment configuration.

The image declares `VOLUME /data`. Starting it without choosing a storage mapping normally creates an **anonymous volume** with a random name. Stopping or restarting that container retains the data. A newly created container does not automatically reuse that volume, so the app can appear empty even though the old data still exists. Volume removal, pruning and automatic cleanup can permanently delete it.

For persistent use, choose a **named volume** and mount the same volume at `/data` during updates. Never run two Hue2Lox instances writing to the same data simultaneously. A volume is not a backup.

### Portainer (Docker Standalone)

1. Select the correct environment and create `hue2lox-data` under **Volumes**.
2. When creating the container, select that volume under **Volumes / volume mapping**; container path **`/data`**, writable.
3. Configure ports/networking and any required environment variables, then deploy.
4. Check **Inspect → Mounts**: `Destination: /data`, type `volume`, the selected volume and `RW: true`.

Labels can differ between Portainer versions. Storage lives on the **Docker server managed by the selected environment**, not the computer displaying Portainer. Alternatively deploy the [Compose template](../docker/compose.image.yaml) as a stack; it already declares a named volume. Retain the stack name to preserve the mapping; a different stack name can create another volume.

### Podman Desktop and host folders

On macOS/Windows, managed Podman volumes live inside the **Podman Linux VM**, not automatically in your Documents folder. Back them up before resetting/removing that VM. The [Podman command](DOCKER.md#podman-desktop-on-macos) explicitly assigns a named volume.

A host folder is optional, for example `/srv/hue2lox/data:/data`. On Linux, create it first and make it writable by UID/GID **10001:10001**. Do not use `chmod 777`. SELinux also requires appropriate mount labels; desktop VMs have their own sharing and permission rules. A named volume avoids manual host-folder ownership setup.

## Deployment created by the Linux installer

The Docker installer creates `data/`, `secrets/` and, for direct HTTPS, `certs/` under the chosen installation directory and mounts them through Compose. Back up these directories together with `.env`, Compose configuration and the previous image. The download/extraction folder is not necessarily the data folder. Native installations use different paths: see [native installation](INSTALL-NATIVE.en.md).

## Login

`admin/admin` applies only when the mounted data has no credentials yet. A changed password survives restarts, updates and reuse of the volume. `HUE2LOX_ADMIN_PASSWORD` also initializes new credentials only; it does not reset an existing password.

For a browser-address/configuration mismatch, compare the exact browser URL, including scheme and port, with `HUE_PUBLIC_URL`. Set variables in Portainer's container/stack configuration, Podman Desktop's **Environment variables** when creating the container, or Compose's `environment` section. Configuration changes generally require recreating the container with the same data volume. Do not delete data to fix an address error.

## HTTP or HTTPS?

- **Local HTTP test:** Leave TLS variables unset and open `http://...`. Credentials are unencrypted on that connection; use an appropriate trusted test network.
- **HTTPS through Traefik or another reverse proxy:** The proxy manages the browser certificate and forwards internally to Hue2Lox HTTP. Set `HUE_PUBLIC_URL=https://hue2lox.example.de` to the actual URL. Forward the original `Host` header. Omit `TLS_CERT` and `TLS_KEY` in Hue2Lox. No certificate private key needs to be mounted into Hue2Lox for this mode.
- **HTTPS directly in Hue2Lox:** Mount the certificate and key read-only, for example under `/certs`. Set `TLS_CERT=/certs/server.crt` and `TLS_KEY=/certs/server.key`. Both files must be readable by container UID 10001; keep the key private. The certificate must cover the address, be trusted by the client, and be renewed before expiry. The Linux installer offers direct certificate setup; a self-signed certificate is not automatically trusted by every browser.

Set both TLS variables or omit both. Empty values do not disable TLS; partial configuration prevents startup. After replacing certificates, reload them by restarting the service.

**The Hue Bridge certificate is separate.** Hue2Lox ships the Hue CA for bridge TLS verification. Do not disable certificate verification or replace browser certificates to fix discovery.

## Bridge discovery and direct access are separate tests

- **Automatic discovery** uses local multicast: mDNS UDP 5353 and SSDP UDP 1900. Replies must reach the container. The Docker installer/Compose on Linux uses host networking; VLANs, guest networks and firewalls can still limit discovery.
- **Manual addition** requires a route from the container to the bridge IP and HTTP/HTTPS access to it (TCP 80/443 depending on the check). Publishing the web-interface port alone does not provide this route.
- **Podman Desktop on Mac/Windows** uses a Linux VM. Multicast discovery may fail while manual access succeeds. Host networking there does not automatically mean the physical Mac/Windows LAN. A successful UI login does not prove bridge connectivity.

If only discovery fails, run the local helper under **Bridges** on your computer or obtain the bridge IP from your router and enter it manually. No online service is needed.

If manual addition fails too, save the exact error and compare reachability of that same IP from the host and from the container. Check VPN, guest Wi-Fi, VLAN routing, VM networking, local-network permissions and firewall rules. Allow the required connections instead of disabling the firewall. Certificate or pairing errors against a reachable bridge need separate diagnosis. Entering an IP manually cannot bypass a network block.

## Updating and checking

Back up the data volume, configuration, custom certificates and previous image first. Start the new image using **the same** volume; do not use `down -v`. Verify the existing password, bridge inventory and saved settings afterward. See [update and recovery](UPDATE-DOCKER.md).

Sources: [Docker volumes](https://docs.docker.com/engine/storage/volumes/), [Podman machine](https://podman-desktop.io/docs/podman/creating-a-podman-machine).
