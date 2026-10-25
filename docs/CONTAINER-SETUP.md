# Container setup: login, storage, networking and HTTPS

Preferred: Docker Compose inside a Linux VM, for example on Proxmox. [Test status and limits](RUNTIME-SUPPORT.md).

[Deutsch](CONTAINER-SETUP.de.md) · [Container guide](DOCKER.md) · [Linux installer](../INSTALL.md)

These notes apply to the published Hue2Lox image starting with **1.0.1**. A quick desktop test and a persistent deployment need different preparation. Downloading an image does not update an existing container.

## Quick start: Docker on a Linux server

Docker Engine and Docker Compose must already be installed. Use a new directory and a free TCP port 18443. Run these commands from that directory with Docker permissions (for example, use `su -`, then change into the directory). The download uses the publicly available tested file at a fixed commit; using a new directory avoids overwriting an existing installation:

```sh
curl --fail --location --output compose.yaml https://raw.githubusercontent.com/square-com-de/hue2lox/bd8b4d172cafd8db9e602c992ec3e9704a4ce420/docker/compose.quickstart.yaml &&
docker compose up -d --wait &&
docker compose ps
```

Open **http://SERVER-IP:18443** from your browser. Replace `SERVER-IP` with the Linux server's private IP. Fresh data uses **admin / admin**; change the password after login. No URL variable, certificate, host directory or permission adjustment is needed for this direct-IP HTTP setup. Compose creates persistent storage automatically. Keep the same project/directory for updates. Existing installations keep their current Compose file and volume mapping; this template is for fresh installations.

This default is HTTP on a trusted LAN. HTTPS needs a certificate trusted by your browser or a reverse proxy; a port number does not enable encryption. Automatic bridge discovery may be limited by container networking: use the local discovery help or enter the bridge IP. The container must still be able to reach that IP. After adding a bridge, press its physical link button when prompted.

In Portainer, create a **Stack**, paste the same Compose file and deploy it. The volume is created automatically; no separate folder setup is required. This describes Docker Standalone, not Swarm.

If port 18443 is already occupied, choose a free port with `HUE2LOX_HTTP_PORT=18444 docker compose up -d --wait` and use that port in the browser. Keep this setting in the project’s `.env` file for later recreations.

## Before starting

| Setting | Value |
|---|---|
| Image | `docker.io/dubctrl/hue2lox:1.0.1` or `ghcr.io/square-com-de/hue2lox:1.0.1` |
| Storage | Compose creates named volume `<project>_data` → container path `/data`, writable |
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

1. Select the **Linux server’s Docker Standalone environment**, then **Stacks → Add stack**; name the stack `hue2lox`.
2. Paste the complete [Compose file from this checkout](../docker/compose.quickstart.yaml) into the web editor and choose **Deploy the stack**. Port **18443** must be free. Do not create another volume or port mapping: storage and port publishing are already defined.
3. Open **http://SERVER-IP:18443**, using that Docker server’s LAN IP. Fresh data: **admin/admin**, then change the password. This is HTTP on a trusted LAN; see below for HTTPS.
4. Under **Inspect → Mounts**, check `Destination: /data`, type `volume`, `RW: true`. The container must be healthy; also check browser login.

Keep the same stack and its volume during updates. A different stack name can create fresh data. Storage lives on the **Docker server managed by the selected environment**, not the browser computer. This is not a Swarm or Docker Desktop profile. The actual stack flow passed with Portainer CE2.45.3 LTS on Ubuntu26.04.1/Docker29.9.2 ([evidence](acceptance/FINAL-CONTAINER-2026-10-25.md)); the published `v1.0.1` tag’s Compose file remains unchanged.

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

- **Automatic discovery** uses local multicast: mDNS UDP 5353 and SSDP UDP 1900. Replies must reach the container. The guided Docker installer uses host networking on Linux; the quick-start Compose file uses port forwarding; VLANs, guest networks and firewalls can still limit discovery.
- **Manual addition** requires a route from the container to the bridge IP and HTTP/HTTPS access to it (TCP 80/443 depending on the check). Publishing the web-interface port alone does not provide this route.
- **Podman Desktop on Mac/Windows** uses a Linux VM. Multicast discovery may fail while manual access succeeds. Host networking there does not automatically mean the physical Mac/Windows LAN. A successful UI login does not prove bridge connectivity.

If only discovery fails, run the local helper under **Bridges** on your computer or obtain the bridge IP from your router and enter it manually. No online service is needed.

If manual addition fails too, save the exact error and compare reachability of that same IP from the host and from the container. Check VPN, guest Wi-Fi, VLAN routing, VM networking, local-network permissions and firewall rules. Allow the required connections instead of disabling the firewall. Certificate or pairing errors against a reachable bridge need separate diagnosis. Entering an IP manually cannot bypass a network block.

## Updating and checking

Back up the data volume, configuration, custom certificates and previous image first. Start the new image using **the same** volume; do not use `down -v`. Verify the existing password, bridge inventory and saved settings afterward. See [update and recovery](UPDATE-DOCKER.md).

Sources: [Docker volumes](https://docs.docker.com/engine/storage/volumes/), [Podman machine](https://podman-desktop.io/docs/podman/creating-a-podman-machine).
