# Hue2Lox 1.0.0-rc.6 — unpublished release-note draft

**NICHT VERÖFFENTLICHT / NOT RELEASED.** Hardware tests are pending. No stable approval.

## Deutsch

- Gemeinsamer Installer mit Docker-/nativer Auswahl und deutschen/englischen Meldungen.
- Docker: feste RC6-Version von Docker Hub/GHCR oder lokaler Build; HTTP/HTTPS und Reverse Proxy weiterhin möglich.
- Nativ: experimenteller systemd-Betrieb ohne Docker auf den deklarierten amd64-Zielen; eigenes verifiziertes natives Release-Archiv zusätzlich zum Quell-ZIP.
- Updates mit Sicherung, exaktes Rollback und Deinstallation/Wiederinstallation mit Datenerhalt; umask-077-Korrektur.
- Lokale Discovery-Kopierhilfen und sechs Iconoir-Sidebar-Symbole mit vollständigen Lizenzhinweisen.
- Technische Paket-/Docker-/systemd-Prüfungen und Sicherheits-/Quellenprüfung protokolliert. Echte Hue-/Loxone-Hardwareabnahme bleibt offen und wird gemeinsam durchgeführt.

Erstlogin bleibt `admin/admin`, danach Passwort ändern. RC1/RC5 unverändert. Kein `latest` für RCs. Native ARM-/Raspberry-Pi-OS-Unterstützung, Statusrückmeldung, Schalter/BWM und LoxBerry-Plugin sind nicht Bestandteil dieses Kandidaten. Angepasste Compose-/Prototyp-Installationen benötigen eine eigene Migrationsprüfung.

## English

- Shared installer with Docker/native selection and German/English helper output.
- Docker: fixed RC6 Docker Hub/GHCR version or local build; HTTP/HTTPS and reverse proxy retained.
- Native: experimental systemd deployment on declared amd64 targets; verified native archive supplied alongside the source ZIP.
- Backed-up updates, exact rollback and retained-data uninstall/reinstall; umask-077 permission fix.
- Local discovery copy helpers and six Iconoir sidebar icons with complete notices.
- Technical package/Docker/systemd and security/source checks recorded. Real Hue/Loxone hardware acceptance remains pending for the joint test.

Initial login remains admin/admin; change it afterwards. RC1/RC5 stay unchanged. RCs do not set latest. Native ARM/Raspberry Pi OS, status feedback, switch/motion inputs and a LoxBerry plugin are outside this candidate. Custom Compose/prototype deployments need separate migration review.

## Publication handoff / Übergabe

The exact source commit, ZIP/native checksums, container candidates, license/source bundle and CI run IDs belong to one final release. Obtain the local preparation manifest; no hashes or download availability are invented here. Before publishing, confirm the candidate is merged into main, the tag/version pin matches, all release jobs pass and both registries/downloads are anonymously verified. Publication requires separate user approval. / Exakten Quellcommit, Prüfsummen und Prüfläufe aus der lokalen Übergabe verwenden; keine Veröffentlichung ohne separate Nutzerfreigabe.
