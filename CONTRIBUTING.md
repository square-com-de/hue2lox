# Development and quality checks / Entwicklung

Hue2Lox is publicly available as Release Candidate 3. End-to-end testing with a Loxone Miniserver is still in progress. The main branch can contain changes newer than the published release. Original project code is licensed under [Apache License 2.0](LICENSE). Contributions intended for inclusion are submitted under that license unless explicitly stated otherwise. Third-party terms are in [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).

## Work from a clean clone

Clone `https://github.com/square-com-de/hue2lox.git` into a separate development directory. Record the commit being tested. Do not copy production `.env`, keys, credentials, certificates or runtime data into the clone. Never run the prototype installation scripts on an unrelated installation.

Use Python 3.12, Node.js 22 (JavaScript syntax and helper tests), OpenSSL and, for container testing, Linux with Docker Engine and Compose v2. The application uses the Python standard library; there is no pip dependency installation.

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

Trivy checks the current source checkout for secrets and the built image for fixable HIGH/CRITICAL vulnerabilities. Reports remain temporary on the runner: matched secret text is neither printed nor uploaded. A failed scan must be reviewed privately; do not paste the report into an issue. This is not a full history audit or a guarantee that no vulnerabilities exist. Dependabot proposes action and Docker dependency updates weekly. There are no application pip/npm dependencies to update.

The container script requires root and `CI=true` and is intended only for a disposable Linux runner. Real hardware, target CPU support, browser certificate trust, backups and Loxone XML import remain separate [acceptance tests](docs/ACCEPTANCE.md).

## Changes and reports

Keep changes focused, describe the user-visible result and record which checks actually ran. Use synthetic device names and addresses in fixtures and screenshots. Never commit or log authorization headers, Hue application keys, session cookies, passwords or private TLS keys. Review staged changes and scan history before public release. A green automated run does not replace real-device acceptance.

Deutsch: Hue2Lox ist als Release Candidate 3 öffentlich verfügbar. Der durchgängige Funktionstest mit einem Loxone Miniserver ist noch nicht abgeschlossen. Änderungen in einem getrennten Klon testen; keine produktiven Zugangsdaten übernehmen. Eine Debian-13-Neuinstallation mit Kopplung und Neustart wurde bestätigt. Fehlerberichte bitte ohne Tokens, Keys oder unbereinigte Protokolle.

## Repository layout

- `src/`: Python application modules; run locally with `python3 src/app.py`.
- `docker/`: Compose variants and the installer Dockerfile. Compose overrides are combined with the root `compose.yaml`; keep the repository root as the project directory.
- `config/registry.json`: empty source template, separate from live `data/registry.json`.
- `scripts/`: installation helpers and historical prototype update scripts. The interactive entry point remains `install-assistant.sh` at the root.
- `tests/`, `docs/`, `web/`: automated tests, detailed guides and browser assets.

The prototype update scripts require the complete source tree in their explicitly configured staging directory, including `scripts/copy-runtime.sh`. They are not a general updater for RC1 installations.
