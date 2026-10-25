# Changelog

## 1.0.2

- Consolidate DE/EN runtime support and installation guidance; distinguish tested Podman Desktop 1.30.5/macOS ARM64 from Linux Docker/Compose and experimental native deployment.
- Remove obsolete contradictory Podman workaround; retain existing passwords, explicit URLs, origin/CSRF checks and control restrictions.
- Record RC5 defaults/test-expectation errors, retained-state recovery, scene usability and desktop-login lessons with owners and evidence.
- Block future stable publication/latest promotion until version-specific documentation/user-flow/recovery/scope acceptance is explicitly approved and bound to the exact tracked source/docs. Existing releases remain unchanged.

- Display the installed Hue2Lox package/build version in the sidebar instead of the static “Version2”. Container release identity is generated at build time from exact-tag CI metadata; development images are labelled explicitly. Native packages use their own manifest; invalid metadata is shown as unknown.
- Anzeige der installierten Paket-/Buildversion statt „Version2“; Entwicklungsbuilds werden ausdrücklich gekennzeichnet. Bestehende Daten und veröffentlichte Releases bleiben unverändert.

## 1.0.1 — 2026-10-24

Fix first login when an image is started directly in Podman Desktop without environment variables. Direct localhost/private-IP access now uses the actual HTTP/HTTPS address and mapped port; explicitly configured proxy URLs remain authoritative. Correct DE/EN errors distinguish address/configuration failures from bad credentials. Existing passwords and volumes are unchanged.

Direkter Start in Podman Desktop ohne Zusatzkonfiguration: Anmeldung mit admin/admin bei frischen Daten funktioniert. Adressfehler werden nicht mehr als falsches Passwort gemeldet. Bestehende Passwörter und Daten bleiben unverändert.

[Details / Hinweise](docs/RELEASE-NOTES-1.0.1.md)

## 1.0.0 — 2026-10-24

First stable release / Erstes Stable-Release. Scene on/off with visible defaults and automatic exact-group assignment; immediate selection without confirmation checkbox. Existing recall commands remain compatible. / Szenen-Ein/Aus mit sichtbaren Defaults und automatischer exakter Gruppenzuordnung; direkte Auswahl ohne Bestätigungshaken. Bestehende Recall-Befehle bleiben kompatibel.

[Full DE/EN notes / Vollständige Hinweise](docs/RELEASE-NOTES-1.0.0.md). Native remains experimental / Nativ bleibt experimentell.

[Historical RC6 plan / Historischer RC6-Plan](docs/RC6-PREPARATION.md) · [Released RC5 / Veröffentlichtes RC5](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.5)

## 1.0.0-rc.6 — historical / historisch

### Deutsch

- Gemeinsamer Docker-/nativer Installer; native Installation bleibt experimentell.
- Auswahl fester Docker-Hub-/GHCR-Images oder lokaler Build; dokumentierter Docker-Update-/Rollbackweg mit Datenerhalt.
- Native Wartung mit Update, Rollback und Deinstallation/Wiederinstallation mit Datenerhalt; korrigierte Rechte unter umask 077.
- DE/EN-Helfermeldungen, lokale Discovery-Kopierhilfen für macOS/Windows/Linux und sechs Iconoir-Sidebar-Symbole mit Lizenzbeilage.
- Reale Ubuntu-/DietPi-Deployment-Abnahme abgeschlossen; [genauer Umfang und Grenzen](docs/DEPLOYMENT-ACCEPTANCE.md). Hardware- und finale Release-Paketabnahme bleiben separat.

### English

- Shared Docker/native installer; native deployment remains experimental.
- Fixed Docker Hub/GHCR image selection or local build; documented Docker update/rollback with preserved state.
- Native update, rollback and uninstall/reinstall retaining data; corrected permissions with umask 077.
- DE/EN helper messages, local macOS/Windows/Linux discovery copy helpers and six Iconoir sidebar icons with license materials.
- Real Ubuntu/DietPi deployment acceptance complete; [exact scope and limits](docs/DEPLOYMENT-ACCEPTANCE.md). Hardware and final release-package acceptance remain separate.

## 1.0.0-rc.5 and earlier / und früher

Historical release notes remain authoritative and unchanged: [RC5](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.5), [RC4](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.4), [RC3](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.3), [RC2](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.2), [RC1](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.1). / Historische Release Notes bleiben maßgeblich und unverändert.
