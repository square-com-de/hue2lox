<p align="center">
  <img src="web/hue2lox-logo.png" width="360" alt="Hue2Lox">
</p>

<h1 align="center">Hue2Lox</h1>
<p align="center">Connect Philips Hue lights and scenes to Loxone with ready-to-use HTTP commands and XML templates.</p>
<p align="center">English · <a href="README.de.md">Deutsch</a> · <a href="#quick-start">Quick start</a> · <a href="docs/MANUAL.md">Manual</a></p>

![Hue2Lox 1.0.2 overview before pairing a bridge](docs/images/hue2lox-1.0.2.png)

*Actual published 1.0.2 interface, shown in German with an empty registry before pairing. [Screenshot provenance and validation scope](docs/README-STRUCTURE.md#hue2lox-reference).*

## Features

- **Multiple Hue Bridges:** pair locally and read their lights, rooms and scenes.
- **Controls that fit your lights:** switching, dimming, RGB, Lumitech and white temperature, based on bridge capabilities.
- **Ready for Loxone Config:** copy HTTP commands or export selected lights and scenes as XML.
- **Scene on/off:** activate a Hue scene and switch off its assigned group; recall-only mode remains available.
- **Find and organize devices:** local discovery help, bridge/room filters and saved usage preferences.
- **Local operation:** German/English UI, persistent files and a temporary sanitized HTTP monitor; no cloud account during normal use.

## Quick start

For a **new installation** on a Linux server or VM with Docker Engine, Docker Compose and `curl` already installed. Use an account with Docker permissions (for example a root shell opened with `su -`). Port **18443** must be free. Run from the desired parent directory; `hue2lox` must not exist yet.

```sh
mkdir hue2lox &&
cd hue2lox &&
curl --fail --location --output compose.yaml https://raw.githubusercontent.com/square-com-de/hue2lox/v1.0.2/docker/compose.quickstart.yaml &&
docker compose up -d --wait &&
docker compose ps
```

1. Open **http://SERVER-IP:18443**, replacing `SERVER-IP` with your Linux server's LAN address.
2. With fresh data, sign in as **admin / admin** and **change the password**. An existing volume keeps its existing password.
3. Keep this project directory and its named data volume. Compose creates storage automatically; the data lives in the volume, not inside `compose.yaml`.

**This starts HTTP, without TLS.** Use it only on a trusted LAN. HTTPS requires explicit setup: [Traefik/reverse proxy or direct certificates](docs/CONTAINER-SETUP.md#http-or-https). For a custom hostname/proxy, configure `HUE_PUBLIC_URL` in the container environment. It does not enable TLS by itself. Port 8443/18443 alone does not mean HTTPS.

This quick start pins the currently published **1.0.2**, not an unpublished candidate or `latest`. [Release and checksums](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.2) · [Runtime scope](docs/RUNTIME-SUPPORT.md).

## First use

1. Open **Bridges**, search locally or enter the bridge IP, then pair using its physical link button. If multicast discovery fails, use the local discovery helper; the container must still be able to reach the bridge directly.
2. Read the lights and scenes. Choose the required light control modes; inspect the assigned OFF group before using scene on/off.
3. Copy commands or import XML into Loxone Config, check the address/token/actuator type, and test a selected light. [Illustrated guide](docs/TUTORIAL.md).

Scene OFF affects the entire assigned group. Hue2Lox does **not** feed measured light states back into the Loxone Lighting Controller. [Scene behavior and limits](docs/features/SCENE-SWITCH.md).

## Other installation options

| Path | Guide |
| --- | --- |
| Portainer, Docker Standalone | Use the same Compose file as a Stack: [setup](docs/CONTAINER-SETUP.md#portainer-docker-standalone) |
| Podman Desktop | [Steps and tested platform limits](docs/DOCKER.md#podman-desktop-on-macos) |
| Native Linux installer | [Installation and maintenance](docs/INSTALL-NATIVE.en.md); experimental, supported amd64/systemd targets only |
| Custom networking, storage or HTTPS | [Container configuration](docs/CONTAINER-SETUP.md) |

**Already installed?** Use [backup, update and rollback](docs/UPDATE-DOCKER.md) or [native maintenance](docs/INSTALL-NATIVE.en.md). Back up the full data volume and configuration; pulling/restarting alone does not replace a container. No dedicated LoxBerry plugin is available.

## Documentation and help

[Manual and troubleshooting](docs/MANUAL.md) · [Loxone tutorial](docs/TUTORIAL.md) · [Certificates and recovery](docs/MAINTENANCE.md) · [Changelog](CHANGELOG.md) · [Lessons learned](docs/LESSONS-LEARNED.md).

Questions or feedback: [GitHub](https://github.com/square-com-de/hue2lox/issues/new?template=feedback_question.md) or [hue2lox@square-com.de](mailto:hue2lox@square-com.de). Report bugs using an [issue template](https://github.com/square-com-de/hue2lox/issues/new/choose); include your version and a sanitized error. Never post passwords, tokens, private keys or token-bearing XML. [Security reporting](SECURITY.md) · [Contributing](CONTRIBUTING.md).

## License

[Apache License 2.0](LICENSE) for original project material; third-party terms remain applicable. [Notices and sources](THIRD-PARTY-NOTICES.md) · [NOTICE](NOTICE). Independent project; not officially affiliated with Philips Hue or Loxone.

<p align="center"><strong>by <a href="https://square-com.de/">square | com</a></strong> · <a href="https://square-com.de/impressum/">Legal notice</a></p>
