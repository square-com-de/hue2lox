# Development and quality checks / Entwicklung

Hue2Lox 1.0.2 is published; 1.0.3 is being prepared and is not released. Evidence and remaining acceptance are version-specific; see [runtime status](docs/RUNTIME-SUPPORT.md). The main branch can contain changes newer than the published release. Original project code is licensed under [Apache License 2.0](LICENSE). Contributions intended for inclusion are submitted under that license unless explicitly stated otherwise. Third-party terms are in [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).

## Work from a clean clone

Clone `https://github.com/square-com-de/hue2lox.git` into a separate development directory. Record the commit being tested. Do not copy production `.env`, keys, credentials, certificates or runtime data into the clone. Never run the prototype installation scripts on an unrelated installation.

CI and the container use Python 3.15. Native experimental targets use OS Python >=3.11. Separate offline systemd jobs cover Debian 12/13 and Ubuntu 24.04/26.04 amd64; DietPi recognition has fixtures; real Ubuntu/DietPi VM evidence remains bound to the commits in [deployment acceptance](docs/DEPLOYMENT-ACCEPTANCE.md). For local development use a compatible Python version, Node.js 22 (JavaScript syntax and helper tests), OpenSSL and, for container testing, Linux with Docker Engine and Compose v2. The application uses the Python standard library; there is no pip dependency installation.

```sh
python3 scripts/check-quality.py
python3 -m unittest discover -s tests -t . -p 'test_*.py'
python3 scripts/smoke-install.py
```

The smoke test creates a temporary empty installation, binds only to localhost and removes its files afterwards. It does not contact Hue bridges. Tests that bind local ports need permission to do so.

After changing translations or tutorial content:

```sh
python3 tools/build_locales.py
python3 tools/build_tutorial.py
python3 tools/build_tutorial.py --english
```

Commit the generated assets with their sources. Translate interface text, not user-defined bridge, room, lamp or scene names.

## Automated checks

[Quality checks](.github/workflows/quality.yml) runs on pushes to `main`, pull requests and manual dispatch. It checks syntax, tests, translation keys, generated assets, documentation links and a disposable HTTPS installation. A separate job builds and starts an empty Docker installation, checks its non-root user and read-only application, then repeats API checks after restart.

Trivy checks the current source checkout for secrets and the built image for fixable HIGH/CRITICAL vulnerabilities. Secret reports remain temporary on the runner: matched secret text is neither printed nor uploaded. Image vulnerability reports are retained separately as CI artifacts. A failed scan must be reviewed privately; do not paste the report into an issue. A separate history-security job runs Gitleaks across reachable history using individually recorded finding fingerprints; neither scanner proves that no secrets or vulnerabilities exist. Dependabot proposes action and Docker dependency updates weekly. There are no application pip/npm dependencies to update.

The container script requires root and `CI=true` and is intended only for a disposable Linux runner. Real hardware, target CPU support, browser certificate trust, backups and Loxone XML import remain separate [acceptance tests](docs/ACCEPTANCE.md).

## Changes and reports

Keep changes focused, describe the user-visible result and record which checks actually ran. Use synthetic device names and addresses in fixtures and screenshots. Never commit or log authorization headers, Hue application keys, session cookies, passwords or private TLS keys. Review staged changes and scan history before public release. A green automated run does not replace real-device acceptance.

Deutsch: 1.0.2 ist veröffentlicht; 1.0.3 ist unveröffentlichte Vorbereitung. Historische Hardware- und VM-Ergebnisse gelten nur für ihren protokollierten Stand. Änderungen in einem getrennten Klon testen; keine produktiven Zugangsdaten übernehmen. Eine Debian-13-Neuinstallation mit Kopplung und Neustart wurde bestätigt. Fehlerberichte bitte ohne Tokens, Keys oder unbereinigte Protokolle.

## Repository layout

- `src/`: Python application modules; run locally with `python3 src/app.py`.
- `docker/`: Compose variants and the installer Dockerfile. Compose overrides are combined with the root `compose.yaml`; keep the repository root as the project directory.
- `deployment/native/`: native systemd installation, update and removal; see [English](docs/INSTALL-NATIVE.en.md) / [Deutsch](docs/INSTALL-NATIVE.md). Docker entry points stay in place.
- `config/registry.json`: empty source template, separate from live `data/registry.json`.
- `scripts/`: installation helpers and historical prototype update scripts. The native guided entry point is `bash install-assistant.sh --deployment native`; existing Docker-installer helpers remain for compatibility.
- `tests/`, `docs/`, `web/`: automated tests, detailed guides and browser assets.

The prototype update scripts require the complete source tree in their explicitly configured staging directory, including `scripts/copy-runtime.sh`. They are not a general updater for RC1 installations.

## Native deployment development

Build a native package from a recorded, reviewed commit:

```sh
python3 scripts/build-native-package.py --version VERSION --output /tmp/hue2lox-native-package
```

Use a disposable Debian 13 amd64 system for installation and systemd lifecycle tests. The installer requires root and changes system paths; never run it on a developer workstation or an existing installation. Obtain and verify the package SHA-256 independently before installation. Do not distribute packages containing unreviewed working-tree changes as a tagged release.

Native and Docker deployment share the application and state preparation; changes must preserve existing Docker defaults. Native state initialization must accept explicit directories, have no fixed UID and make no systemd changes. Keep native lifecycle tests separate from application and Docker tests. No automated check establishes Hue/Loxone hardware acceptance. A future LoxBerry package can reuse state preparation while providing its own paths, service integration and update hooks.

Containers are offered directly through Docker or Podman; the documented assistant starts in native mode. Existing Docker-installer code remains compatible and is still covered by CI. Test both languages, declined actions, dirty-source refusal and native umask 077. Native local package preparation must never download main or require Docker. RC1 and RC5 are immutable.

## Documentation maintenance

Use [the documentation index](docs/INDEX.md) to distinguish current guides from historical evidence. Check both languages, protocol defaults, configuration locations, persistent storage and scene modes against the code. Regenerate both tutorial HTML files when editing their Markdown sources. Keep dated test identities and verbatim upstream license texts; do not relabel old tests as new release acceptance.
