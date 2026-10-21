# Hue2Lox – user manual

[Home](../README.md) · [Deutsch](MANUAL.de.md) · [Installation](../INSTALL.md)

## Access and language

Open your installation's HTTPS address. New installations use `admin` / `admin`; change the password in the header. Verify the certificate fingerprint on the server before trusting its public certificate on a client. Every new installation generates its own certificate; see [certificate renewal, IP changes, backup and recovery](MAINTENANCE.md).

Select Deutsch or English. The browser's language is used initially. Switching language reloads the page: your login and saved control modes remain, but unsaved form inputs and temporary XML selections reset.

## Bridges and inventory

Under **Bridges**, discover a bridge or enter its local IP and a name. Select **Check and add bridge**, then **Pair**, press its physical link button and connect within the displayed time window. Do not paste Hue keys into the interface.

**Scan lights & scenes** refreshes inventory. Bridge names also serve as filter names; they may represent floors or any other grouping. Rooms/zones come from Hue. Docker networking, firewalls and VLANs may limit discovery; manual IP entry is available.

## Lights

Cards show the name, model, type, capabilities and last reported state. A switched-off light may still show stored brightness. This display does not synchronize state back into the Loxone Lighting Controller.

Under **Usage & management → Use with Loxone**, check the required control modes. Defaults follow bridge capabilities. Lumitech combines color and white; Tunable White handles white temperature without RGB. At least one mode must remain selected. These choices configure commands and XML; they do not control the light.

- **Commands:** open copy fields and select a preview if multiple modes are enabled.
- **XML:** export this light's checked modes.
- **Ignore:** hide persistently in Hue2Lox; restore via **Show ignored**.
- **Remove:** remove only from Hue2Lox; scanning may restore it. The bridge is unchanged.

For multiple lights, select their checkboxes and **Export selection as XML**. A combined import creates one virtual output with several commands. Separate imports create additional outputs. Changing filters does not clear your selection.

## Scenes

Create, edit and delete scenes in the Hue app. Use **Scan scenes** to synchronize inventory. **Commands** and **XML** work as for lights; recall uses an ON pulse. Management allows ignoring, restoring and removing only from Hue2Lox.

Scenes can still control ignored/removed lights included in their Hue definition.

## Loxone

**Loxone settings** discovers the Miniserver and stores a link to its web interface, not its credentials. Reveal the Hue2Lox access token briefly or copy it with the HTTP header. This is not the Hue Bridge key.

Follow the [illustrated guide](TUTORIAL.md) for virtual outputs. Preserve the literal `\r\n` header separator. Do not let competing outputs control the same light. XML uses a token placeholder by default; including real credentials requires **Token in XML**.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Certificate warning | Address, expiry, fingerprint and client trust |
| Bridge unreachable | IP, network, power and bridge identity |
| Unexpected type | Rescan and inspect actual bridge capabilities |
| HTTP 401 | Hue2Lox authorization token |
| HTTP 403 | Control flags; admin requests also need a session and CSRF |
| HTTP 400 | Sanitized body, number type, placeholder and header formatting |
| HTTP 415 | Content-Type and header separator |
| HTTP 200 but wrong effect | Actuator type, chosen mode, brightness and physical light |
| No monitor entry | Loxone output, address, port and TLS; pre-HTTP failures are not recorded |

Start the **HTTP monitor**, then trigger one command. Recording lasts at most ten minutes, with 200 in-memory entries. Tokens, keys and unknown free text are excluded. Review even sanitized logs for personal names/addresses before sharing.

## Update, backup and restore

Stop the service briefly and back up the **entire installation directory**, preserving permissions. Include `.env`, Compose files, `data/`, `certs/`, `secrets/` and the source version. Paired bridge keys live in `data/bridge-keys/`. A Git clone is not a private-state backup.

For the isolated test instance in INSTALL.md, as root:

```sh
cd /opt/hue2lox-test
docker compose stop
install -d -m 700 /opt/hue2lox-private-backups
umask 077
tar -czpf /opt/hue2lox-private-backups/test-backup.tar.gz -C /opt hue2lox-test
docker compose start
```

Choose a new archive filename for each backup. Store archives encrypted/offline, never on GitHub. File backups do not contain Docker images: record the exact image version/digest and save the image separately if offline rollback is needed.

Rehearse restoration on an isolated target: stop containers, retain the current state separately, restore files with their permissions, check paths/address/port and UID/GID 10001 ownership of private directories, then start. A changed address needs a matching certificate. Verify health, login, inventory, token and finally a deliberate light command. The full restore rehearsal is still pending joint acceptance testing.

The prototype updater's limited rollback copy is not a complete backup. A general public updater/rollback mechanism is not released yet.

## Limits and licensing

See [release readiness](../RELEASE.md) and [third-party notices](../THIRD-PARTY-NOTICES.md). Original project code and original SVG icons are licensed under [Apache License 2.0](../LICENSE); third-party materials retain their respective terms.

Under **Usage & management → Light icon**, choose a shape per light. **Automatic** uses model and bridge metadata; unknown devices receive a bulb symbol. The choice survives restarts and rescans and does not change Loxone commands.
