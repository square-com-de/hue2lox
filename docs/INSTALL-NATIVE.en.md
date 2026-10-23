# Native Linux installation without Docker

The web app also includes optional local discovery help for macOS, Windows and Linux. It is included in native packages and local Docker builds of this development checkout. A published RC5 image selected in the assistant does not yet include this new help. Users explicitly run the helper commands on their computer on the local network; the installer does not start device discovery.

[Deutsch](INSTALL-NATIVE.md) · [Docker installation](../INSTALL.md)

This additional deployment on main uses the same application and interface as Docker. RC1 remains unchanged. For RC6, use the versioned native archive and checksum alongside the source ZIP; see the RC6 section below. **The native path is experimental.** Explicit test targets are Debian 12/13, Ubuntu 24.04/26.04 and DietPi on Debian 12/13, currently amd64 only. This is not hardware approval.

## Shared interactive installer (development)

RC5 remains unchanged and does not include this native installer. Use a clean, reviewed main checkout after the PR #18 merge and record its exact commit. Do not use a mutable main download as a released native package. Start the existing assistant as root (`su -`, or `sudo -i` on Ubuntu):

```sh
bash /absolute/path/to/hue2lox/install-assistant.sh
```

After language selection choose **With Docker** or **Native, without Docker**. The Docker menu retains its existing HTTP/HTTPS and proxy options. The native menu provides:

1. Read-only platform/prerequisite status.
2. Optional SSH setup.
3. Explicit base-package installation (no Docker repository or Docker installation).
4. Local preparation of a development package from the clean Git checkout. The assistant records the commit, computes and verifies the package checksum and removes its temporary package directory when it exits.
5. Native installation after IP/HTTPS-port selection and explicit confirmation. Use the server's LAN address for direct browser access; loopback is also available via manual address entry. A tunnel is required only for remote access to a loopback listener.
6. Verified HTTPS check of the existing native service (does not pair devices).
7. Maintenance: update with backup, reinstall retaining data, explicit rollback, or uninstall retaining data. Rollback restores the historical private data including passwords. There is no purge option in the menu.

For a separately obtained native archive, pass its independently checked SHA-256:

```sh
bash /absolute/path/to/hue2lox/install-assistant.sh --deployment native \
  --native-package /absolute/path/native.tar.gz --native-sha256 VERIFIED_SHA256
```

A source ZIP without Git identity does not fabricate a source commit or download main. The native package step instead asks for a verified archive and its SHA-256. No native release asset is published yet. A prepared development package uses `0.0.0-dev.<commit>`; it is not a release. Restart the assistant from the newly reviewed checkout when updating code. Reinstall requires the same package identity as the retained data; use the old verified archive when necessary. Native data paths remain fixed and are independent of the Docker installation directory.

The optional `--check --deployment native` is read-only. No installation changes occur merely by selecting a backend or viewing status. Real Ubuntu 26.04/DietPi 13 amd64 acceptance passed, including actual code update and rollback. It applies to the recorded commit; native hardware tests remain separately open. See [current deployment acceptance](https://github.com/square-com-de/hue2lox/blob/main/docs/DEPLOYMENT-ACCEPTANCE.md).

## Requirements and limits

Use a fresh, isolated test instance with systemd, OS Python 3.11 or newer, OpenSSL and root access. Native targets: Debian 12/13, Ubuntu 24.04/26.04 and DietPi on Debian 12/13, amd64 only. Ubuntu 22.04, unknown derivatives, Raspberry Pi OS, ARM and 32-bit operating systems are currently rejected by the native adapter. Docker retains its separate platform support. Python/OpenSSL come from the operating system; a virtual environment does not replace the TLS runtime. No application pip packages are required. Prerequisites are checked, but the installer does not upgrade the operating system.

The installer creates a system service and system directories. Do not try it on a workstation or production installation. Docker is neither required nor modified. Docker state is not migrated automatically. Parallel operation requires separate state, names and ports; for example, reserve port 18443 for the native test.

## Prepare a package

Until a native release exists, a developer builds a package from a reviewed checkout:

```sh
python3 scripts/build-native-package.py --version VERSION --output /tmp/hue2lox-native-package
```

Replace `VERSION` with the intended package version. The manifest records the commit and package contents. A package from a modified working tree is not an immutable tagged release. Packages contain the application, web assets, catalogue, trust anchor, configuration template, licence texts and native tools, without production data.

Obtain the package and its SHA-256 through a trusted, independently verifiable handover. Calculating a hash yourself does not establish provenance. Do not treat a changing main download as an approved native release.

## Fresh installation

Extract the package into a temporary working directory. In the extracted package, show options without installing:

```sh
bash deployment/native/install.sh --help
```

On the isolated target, replace the paths, checksum and IP:

```sh
sudo bash deployment/native/install.sh \
  --package /tmp/hue2lox-native.tar.gz \
  --sha256 VERIFIED_SHA256 \
  --host 192.168.1.50 --port 18443
```

`192.168.1.50` is only an example; use your server's fixed LAN address. The installer currently accepts only local IPv4 addresses and ports starting at 1024. It refuses to initialize existing state again. It creates credentials and a certificate, starts the service and checks HTTPS with certificate verification. It does not discover bridges or control lights. A failed initial HTTPS check retains files for diagnosis and does not constitute success. Do not initialize them again; fix the cause or explicitly uninstall.

After success, open the displayed HTTPS address, verify the certificate fingerprint through a trusted channel and sign in with `admin` / `admin`. Change the password in the interface. Control, RGB and Lumitech are enabled immediately for supported lights on fresh installations. Control commands still require a valid token. Updates and reinstalls retaining data preserve existing settings unchanged. Pairing and Loxone setup require separately authorized hardware acceptance; see the [acceptance plan](ACCEPTANCE.md).

## Files and operation

| Path | Purpose |
| --- | --- |
| `/opt/hue2lox/releases/<version>-<commit>-<id>/` | Root-owned application, not writable by the service |
| `/opt/hue2lox/current` | Active application version |
| `/etc/hue2lox/settings.env` | Operating settings explicitly loaded by systemd |
| `/etc/hue2lox/` | Protected certificates and control token |
| `/var/lib/hue2lox/` | Registry, password file and bridge keys |
| `/var/backups/hue2lox/` | Protected update backups |

The service runs under its own non-login `hue2lox` account. Configuration and private files are not world-readable. The service can write its state, but cannot modify application files or system configuration. No fixed container UID is used.

```sh
sudo systemctl status hue2lox
sudo journalctl -u hue2lox --since today
sudo systemctl restart hue2lox
```

Review logs for private information before sharing. Never upload tokens, keys, password hashes or complete backups to issues.

## Update and recovery

Use a fixed native package. From its extracted directory:

```sh
sudo bash deployment/native/update.sh \
  --package /tmp/hue2lox-native-new.tar.gz \
  --sha256 VERIFIED_SHA256
```

The updater verifies and stages the application, stops the service, backs up private state and the complete previous application code, then switches versions. Password, token, certificate and inventory are retained. Failed startup/HTTPS checks trigger restoration of the previous code and matching state. Only registry schema 1 is currently supported; other schemas are rejected before switching, without automatic migration. Check the final message and indicated backup. If an error persists, stop the service and retain the backup; do not replace the installation with fresh setup.

There is no unattended update timer or automatic main update. Data migrations need an explicitly supported migration and recovery path. Do not start arbitrary older versions against newer state.


### Later rollback after an initially successful update

New update backups contain complete application code, configuration and state with checksums. Explicitly select the backup directory printed by the update:

```sh
sudo sh deployment/native/rollback.sh --backup /var/backups/hue2lox/TIMESTAMP-ID
```

Rollback verifies the backup before stopping the service, backs up the current installation, then restores code **and the matching historical private state**. Password, inventory and key changes made since that backup revert to their historical values. If startup fails, the immediately preceding installation is restored. If recovery also fails, inspect the service/logs and retain the recovery backup identified by the error. A power failure during replacement may require manual recovery. Older backups without complete code and `snapshot.json` are rejected. Successful updates and rollbacks enable service startup at boot.

## Backup and restore

Stop the service for a consistent manual backup. Preserve `/etc/hue2lox` and `/var/lib/hue2lox`, including ownership and permissions, and record the active package version/commit. Restart the service afterwards. Keep an encrypted or root-only copy on separate storage. Backups contain secrets and allow control of configured devices.

Test recovery in isolation first: provide the matching application version, stop the service, restore configuration/state with original permissions, then check startup and HTTPS. Do not operate two restored instances against real bridges at the same time. Local startup does not establish successful hardware recovery.

## Certificate renewal and address changes

The certificate must include the public IP or hostname as a Subject Alternative Name. Before expiry or address changes, create a full backup and stop the service. Generate a matching certificate/key pair for the new address, retain the paths configured in `settings.env`, and update public/bind addresses where necessary. Keep the private key readable only by root and the service group. Start the service and verify HTTPS with the new certificate before renewing browser and Miniserver trust. Do not permanently disable TLS verification.

For the unchanged default layout, renew the certificate after backing up as follows. Replace the example IP. Run this block in a root shell (`sudo -i`):

```sh
set -eu
umask 077
systemctl stop hue2lox
renew_dir=$(mktemp -d /etc/hue2lox/certs/.renew-XXXXXX)
trap 'rm -rf "$renew_dir"' EXIT
openssl req -x509 -newkey rsa:2048 -sha256 -nodes -days 365 \
  -keyout "$renew_dir/server.key" -out "$renew_dir/server.crt" \
  -subj /CN=hue2lox.local \
  -addext 'subjectAltName=IP:192.168.1.50,IP:127.0.0.1,DNS:localhost' \
  -addext extendedKeyUsage=serverAuth
install -o root -g hue2lox -m 0640 "$renew_dir/server.key" /etc/hue2lox/certs/server.key
install -o root -g hue2lox -m 0640 "$renew_dir/server.crt" /etc/hue2lox/certs/server.crt
# For an IP change, update BIND_HOST and HUE_PUBLIC_URL in settings.env before starting.
systemctl start hue2lox
openssl x509 -in /etc/hue2lox/certs/server.crt -noout -fingerprint -sha256
```

An error may leave the service stopped; restore the original certificate/key from backup and investigate. Native management still expects IPv4 addresses in `BIND_HOST` and `HUE_PUBLIC_URL`. Custom DNS-based configurations are not currently supported.

This maintenance procedure needs a separate target-system test. Do not rerun the fresh installer: password, token, registry and bridge keys must survive.

## Uninstall

```sh
sudo bash deployment/native/uninstall.sh
```

Removes the service and native application files. Private configuration, state and backups are retained by default. To deliberately discard private data:

```sh
sudo bash deployment/native/uninstall.sh --purge-data
```

Backups and the system account are retained even with `--purge-data`. Retained private data prevents fresh reinstallation; do not overwrite it with the installer. Create a separate backup first. Private-data deletion cannot be undone. Docker installations are not removed.


### Reinstall with retained private data

After uninstalling without `--purge-data`, use the **same verified package** (version, commit and dirty flag) as before removal. Preserve the IP address and port from the retained settings:

```sh
sudo sh deployment/native/install.sh --keep-data \
  --package /tmp/hue2lox-native.tar.gz --sha256 VERIFIED_SHA256 \
  --host 192.168.1.50 --port 18443
```

Credentials, certificates and registry are not initialized again. Regular updates are possible afterwards. Existing state remains protected without `--keep-data`. Retry an interrupted uninstall using the same uninstall command; foreign service files and symbolic links are rejected before changes.

## Test status and remaining acceptance

Local tests and CI establish only their documented checks. Real Debian startup, systemd permissions and restoration require a disposable target instance. Discovery, pairing, bridge TLS, Loxone HTTPS/XML and actual light behaviour remain separate hardware acceptance. Untested platforms are not supported.

A future LoxBerry plugin can reuse the application and state preparation. Its directories, service integration and update hooks are a separate work package.

[Manual VM acceptance and remaining evidence](NATIVE-VM-ACCEPTANCE.md).

The language selected in the shared assistant also applies to its own Python helper status and error messages. Direct CLI calls can use `export HUE2LOX_INSTALL_LANG=en` or `de`. Output from external tools (apt, Docker, systemd) and their original logs is not rewritten.

## RC6 source ZIP and native archive

**RC6 native archive.** Supply `hue2lox-1.0.0-rc.6-native.tar.gz` alongside `hue2lox-v1.0.0-rc.6.zip`. Verify both hashes from the same `SHA256SUMS.txt`; use the versioned release assets after publication completes. The native archive is separate from the extracted source ZIP. From the extracted source ZIP as root:

```sh
bash install-assistant.sh --deployment native \
  --native-package /absolute/path/hue2lox-1.0.0-rc.6-native.tar.gz \
  --native-sha256 VERIFIED_SHA256
```

The assistant verifies the archive without requiring Git. The versioned native archive contains its manifest, application and lifecycle tools. Publication and hardware approval remain separate.

Existing native development installation? Use the [separate native recovery/rollback procedure](RECOVERY-CONTROL.md).
