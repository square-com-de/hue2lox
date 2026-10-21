# Maintenance: certificates, IP changes and recovery

[Deutsch](MAINTENANCE.de.md)

This guide applies to installations prepared with `prepare-install.py` and a source version containing `scripts/renew-certificate.py`. RC1 does not contain this new tool. Legacy prototype installations are not supported. Run commands on the Linux target server, adjust paths/IPs, and use a disposable installation for testing.

**Operational acceptance pending:** This procedure remains unconfirmed for real browser/Miniserver connections. Automated tests are not operational approval.

## Stop and take a complete backup

`INSTANCE` is the installation directory selected in the installer; `SOURCE` is the extracted new source tree. Become root using `sudo -i` or `su -`. Stop only this Compose installation and pause any external restart automation during maintenance.

```sh
sudo -i
INSTANCE=/opt/hue2lox
SOURCE=/home/lance/hue2lox-main
cd "$INSTANCE"
docker compose down
BACKUP="/root/hue2lox-backup-$(date +%Y%m%d-%H%M%S)"
install -d -m 700 "$BACKUP"
cp -a "$INSTANCE" "$BACKUP/instance"
printf 'Backup: %s\n' "$BACKUP"
```

The backup contains private bridge credentials, control tokens, password records and certificate keys. Keep it private, encrypt transfers and never attach it to GitHub/issues. `cp -a` preserves permissions and ownership. Also retain the source/image version so a later rebuild cannot silently introduce different dependencies. Back up the entire directory, including `.env`, Compose, `data`, `secrets`, `certs`, `health-test.crt` and build files. The registry alone is insufficient.

## Renew the certificate at the same address

After stopping and backing up:

```sh
python3 "$SOURCE/scripts/renew-certificate.py" --destination "$INSTANCE"
docker compose up -d --force-recreate --wait --wait-timeout 120
```

The tool creates a new self-signed certificate valid for 365 days. It replaces the certificate, key and `health-test.crt` along with the matching `.env`. The private key remains mode 600 and owned by container UID 10001. Registry, token, password records, port and installation name are preserved. A private `.hue2lox-tls-backup-*` directory is also retained beside the installation. Write failures roll back; after a power failure restore the complete backup.

## Change the IP address

First configure a fixed address/DHCP reservation on the server/router. The tool does not change networking or firewalls. The new address must already belong to the server. After stopping and backing up, run this **instead of** same-address renewal:

```sh
python3 "$SOURCE/scripts/renew-certificate.py" --destination "$INSTANCE" --host 192.168.1.50
docker compose up -d --force-recreate --wait --wait-timeout 120
```

This updates `HUE2LOX_BIND_IP`, `HUE_PUBLIC_URL`, certificate SAN and healthcheck trust together, preserving the port and project name. Recreate the container: `restart` alone does not apply environment changes.

## Verify and update client trust

Replace the example IP/port with the values from `.env`:

```sh
docker compose ps
openssl x509 -in certs/server.crt -noout -dates -ext subjectAltName
curl --fail --cacert health-test.crt https://192.168.1.50:18443/health
```

Sign in using the new browser URL and verify bridge associations, lights/scenes and settings. Configure trust for the new self-signed certificate in each client that requires it. Do not bypass certificate verification with `curl -k`. After an IP change, update Loxone output addresses, imported commands and browser bookmarks, then test an actual Loxone action separately. The bundled **Hue CA** verifies bridge connections and is not changed or removed by this procedure.

## Restore the complete installation

Set `BACKUP` to the previously printed backup directory. This restores to the same installation path and retains the failed state for investigation. Ensure that the backed-up IP is still assigned to the server; otherwise apply the IP-change procedure after copying and before starting.

```sh
cd "$INSTANCE"
docker compose down
cd /root
mv "$INSTANCE" "${INSTANCE}.before-restore-$(date +%Y%m%d-%H%M%S)"
cp -a "$BACKUP/instance" "$INSTANCE"
cd "$INSTANCE"
docker compose up -d --force-recreate --wait --wait-timeout 120
```

Repeat verification afterwards. No `docker compose down -v`, global Docker cleanup or token regeneration is needed. On another host, use the same architecture or a compatible retained image, and verify networking and port availability first.

## Evidence and limits

Automated tests use temporary installations only: real certificates, rollback on write failure, occupied-port refusal and preserved private state. Linux Docker CI exercises renewal, a second loopback address, HTTPS/login and complete restoration. This does not replace acceptance testing with your browser and Loxone Miniserver. Tests do not access running installations.
