> **RC6 preparation — NOT RELEASED.** RC6 downloads/images below are planned references and must not be run until publication is explicitly approved and verified. For isolated tests use the supplied local ZIP/native archive or local build. Published RC5 remains [available unchanged](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.5). This candidate branch intentionally pins RC6; live main retains RC5 until merge approval.

> **RC6-Vorbereitung — NICHT VERÖFFENTLICHT.** RC6-Downloads/Images unten sind geplante Verweise, erst nach freigegebener und geprüfter Veröffentlichung verwenden. Isoliert die lokal bereitgestellten Archive oder lokalen Build nutzen. RC5 bleibt unverändert verfügbar. Dieser Kandidatenbranch bindet RC6; main behält RC5 bis zur Merge-Freigabe.

# Install with AI

[Home](../README.md) · [Deutsch](AI-INSTALL.de.md) · [Installation guide](../INSTALL.md)

Open a **new chat** in ChatGPT, Claude or another AI assistant and paste the prompt below. The AI guides you up to starting the installer; its menu takes over from there.

You need a Linux target server, its IP and username, SSH access and root/sudo rights, plus access to [Hue2Lox on GitHub](https://github.com/square-com-de/hue2lox). No GitHub account is required to download it. Enter passwords only in the terminal. Supported systems and help with missing SSH or sudo are in the [installation guide](../INSTALL.md).

## Copyable prompt

```text
This prompt is prepared for RC6 after publication. First check whether RC6 is actually published. If not, do not attempt downloads; use locally supplied verified packages for an isolated test.

Help me start the Hue2Lox installer. Keep it simple and guide me step by
step through exactly this workflow:

1. First ask which Linux device should run Hue2Lox: OS, IP/hostname and
   username. Also ask whether my workstation is a Mac or Windows PC.
   Wait for any missing answers. My workstation is not automatically the
   installation target.
2. Give me the SSH command for the target using my details. On the server,
   use existing sudo access with sudo -i or switch to root with su -.
   If already root, skip the switch. Do not install sudo or change user groups.
3. Follow the direct-download steps in
   https://github.com/square-com-de/hue2lox/blob/v1.0.0-rc.6/INSTALL.md.
   As root on the target server, provide ca-certificates, curl and unzip.
   Download the fixed hue2lox-v1.0.0-rc.6.zip and SHA256SUMS.txt directly from
   https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.6.
   No workstation download or scp is needed. No main-branch ZIP.
4. In a new download directory, verify with grep '  hue2lox-v1.0.0-rc.6.zip$' SHA256SUMS.txt | sha256sum --check -.
   Only after verification succeeds, extract and start install-assistant.sh
   from hue2lox-v1.0.0-rc.6. Stop on errors and do not overwrite anything.
   The installer menu takes over from here.

Label each command block WORKSTATION or TARGET SERVER.
Give only the next step and wait for my result.
No Git commands, revision selection or source code inspection. Do not
install Docker yourself: the installer handles that.
Never request passwords, tokens or private keys in chat.
Respond in English.
```

**Test status:** This simplified AI workflow still needs testing in a new chat. Previously confirmed platform tests are recorded in [INSTALL.md](../INSTALL.md).
