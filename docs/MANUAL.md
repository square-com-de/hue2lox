# Hue2Lox – user manual

[Home](../README.md) · [Deutsch](MANUAL.de.md) · [Installation](../INSTALL.md)

## Access and language

Open the actual configured HTTP or HTTPS address. Docker/Podman use HTTP without TLS configuration; the Compose quickstart uses `http://SERVER-IP:18443`. The native installer configures HTTPS with a self-signed certificate. See [configuration and examples](CONTAINER-SETUP.md#http-or-https) for Traefik or direct container HTTPS. Fresh data uses `admin/admin`; change the password in the header. Retained data keeps its existing password. For HTTPS verify the certificate/fingerprint; browser trust does not automatically establish Miniserver trust.

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

Create, edit and delete scenes in the Hue app. **Scan scenes** synchronizes saved metadata. Each scene row directly shows its control mode:

- **On/off:** Default for new or previously undecided records. ON recalls the Hue scene; OFF switches off the entire assigned Hue group. A unique exact-match group is assigned automatically. For ambiguous/larger groups choose explicitly and inspect the listed lamps. Export is blocked without a valid assignment.
- **Recall only:** Scene activation without OFF. Configure a digital output with an ON pulse, repetition 0 and empty OFF fields. Another recall on switch-off would turn the lamps back on.

For **On/off**, copy/import the new digital ON **and** OFF commands, with no dimming value. Updating does not modify existing recall commands. OFF does not restore previous values and may affect additional or hidden lamps in the assigned group.

For A → B on the same group, superseded A OFF is ignored if B has already been accepted. Switch overlapping groups off first. After restart send ON first; OFF without known ownership is rejected. Ownership is command history, **not measured state feedback to the Loxone Lighting Controller**. The Hue app and other control paths are not synchronized automatically. [Scene on/off details and limits](features/SCENE-SWITCH.md) · [Scene interfaces (German)](SCENES.md).

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

Stop the affected instance for maintenance and back up its data, configuration and exact old image/native package together. Backup contents depend on deployment:

| Installation | Complete backup |
| --- | --- |
| Docker/Podman named volume | Entire volume mounted at `/data`, Compose/container configuration, exact image and separately mounted certificates |
| Existing Docker installer | Installation directory including `.env`, Compose, `data/`, `secrets/`, `certs/`, plus exact image |
| Native | `/etc/hue2lox`, `/var/lib/hue2lox`, package/source identity and matching update backup |

**Archiving only the Compose directory does not back up a named volume.** Podman Desktop volumes live in its Linux VM; back them up before resetting/deleting it. There is no database: registry, pairing data, password hash and settings are protected files. Sessions and the temporary HTTP monitor live only in memory.

[Docker/stack update and rollback](UPDATE-DOCKER.md) · [Native maintenance](INSTALL-NATIVE.en.md) · [Storage locations](CONTAINER-SETUP.md#where-is-my-data). Rollback restores the matching old code/image **and** historical data, including the password at backup time. Keep backups private and separate; `down -v` and pruning are not update procedures. Rehearse restoration in isolation. Physical effects and Miniserver certificate trust are separate tests.

## Limits and licensing

See [release readiness](../RELEASE.md) and [third-party notices](../THIRD-PARTY-NOTICES.md). Original project code and original SVG icons are licensed under [Apache License 2.0](../LICENSE); third-party materials retain their respective terms.

Under **Usage & management → Light icon**, choose a shape per light. **Automatic** uses model and bridge metadata; unknown devices receive a bulb symbol. The choice survives restarts and rescans and does not change Loxone commands.
