# Publishing a container release / Container-Release veröffentlichen

## English

This is a maintainer runbook for a **future** release. Merging this workflow does
not publish RC4, modify RC3, push an image or update an installation. The current
RC3 download remains unchanged.

### Before publishing

1. Merge the reviewed installer and publication changes. Choose the exact commit
   on `main` intended for the release; finish the real-device acceptance and
   review the [container compliance evidence](IMAGE-COMPLIANCE.md).
2. Create a new tag, for example `v1.0.0-rc.4`, at that commit. Never move an
   existing release tag. Create a draft GitHub release with short release notes.
   For an RC, select **Set as a pre-release**; for `v1.0.0`, leave that unchecked.
3. In the notes, link the installation guide and explain that the same version
   will be available as an installer ZIP and a multi-platform GHCR image. Link
   the release assets for corresponding sources, notices and platform evidence.
   Do not pre-upload a separately generated ZIP or checksum list: this workflow
   creates them from the tag and refuses to replace different existing files.
4. Check repository Actions permissions allow `GITHUB_TOKEN` to write packages.
   The first package is normally private. Its owner must set the `hue2lox`
   package's visibility to **Public** in its package settings after the first
   upload. A public repository alone does not guarantee a public package.

### What publishing the release does

Clicking **Publish release** starts **Publish release images**. Merely pushing a
branch/tag, opening a PR, saving a draft or manually running the preparation
workflow cannot publish an image.

The workflow checks the tag, source commit and prerelease flag, and rejects the
historical RC1–RC3 tags. It runs the source tests, installer smoke tests and
HTTP/HTTPS container tests. Independently, it builds AMD64 and ARM64 candidates,
boots each, inventories them, creates SPDX SBOMs, and blocks on fixable high or
critical vulnerabilities. The source-material job compares both inventories
with the pinned license/source mappings and verifies source download hashes.

Only after every gate passes does the publisher:

- Attach `hue2lox-vVERSION.zip`, `hue2lox-base-sources.tar.gz`,
  `container-evidence.tar.gz`, `container-release.json` and `SHA256SUMS.txt`
  permanently to the release, then verify their downloads without credentials.
- Load and verify the **same images** that were inventoried and scanned. There
  is no untested rebuild in the publishing job.
- Push architecture tags and the combined version tag to
  `ghcr.io/square-com-de/hue2lox`.
- Pull both published platform digests anonymously and compare their image IDs
  with the candidate evidence; attach `container-digests.json` to the release.
- For a stable release only, move `latest` if this is also GitHub's latest stable
  release. **An RC never creates or changes `latest`.**

For the example RC4, the version tag is `1.0.0-rc.4` (without the leading `v`):

```sh
docker pull ghcr.io/square-com-de/hue2lox:1.0.0-rc.4
podman pull ghcr.io/square-com-de/hue2lox:1.0.0-rc.4
```

These commands are examples for the future release, **not available downloads
until that release has actually passed publication**. Docker selects AMD64 or
ARM64 automatically. Update user-facing download/Compose links only when those
assets and anonymous pulls work. Existing installations do not update themselves.

### A failed run

A failed check means no publication job starts. A failure during upload may leave
some release assets or platform tags present; do not announce completion until
**verify-public** is green. The scripts refuse different existing version images
or release assets instead of overwriting them.

If the first anonymous pull fails because the package is private, change its
visibility to Public, then use **Re-run failed jobs**. That repeats verification
without rebuilding or replacing the images. Keep the existing successful jobs
and their artifacts: preparation artifacts are retained for 90 days and image
archives for 7 days. A full rebuild can produce a different archive checksum;
do not delete existing published assets to force it through. Investigate and
prepare a new version if necessary.

Retain the release assets and a separate backup as long as the corresponding
images are offered. CI artifacts are temporary and are not the source-delivery
channel. Link this runbook and the matching release from the GHCR package page.
Record the first end-to-end publication result in the release notes; a PR test
cannot prove registry write permissions or package visibility.

## Deutsch

Dieser Ablauf ist für ein **künftiges** Release vorbereitet. Das Zusammenführen
des PR veröffentlicht weder RC4 noch Images und ändert weder RC3 noch laufende
Installationen.

1. Geprüfte Änderungen zusammenführen, den vorgesehenen Commit auf `main`
   auswählen und die Abnahme mit echten Geräten sowie die Lizenzbeilagen prüfen.
2. Einen neuen Tag wie `v1.0.0-rc.4` an diesem Commit und einen Release-Entwurf
   anlegen. Beim RC **Set as a pre-release** aktivieren. Bestehende Tags bleiben
   unverändert. ZIP und Prüfsummen werden vom Workflow erzeugt.
3. Erst **Publish release** startet die Veröffentlichung. PRs, normale Pushes,
   Tags allein und manuelle Vorbereitungsläufe veröffentlichen nichts.
4. Tests, HTTP-/HTTPS-Installation, beide CPU-Architekturen, Schwachstellenscans
   und Quellenabgleich müssen erfolgreich sein. Anschließend werden Quellen,
   vollständige Lizenzbeilagen, Inventare, SBOMs und Prüfsummen dauerhaft am
   Release hinterlegt und ohne Anmeldung heruntergeladen und geprüft.
5. Die exakt geprüften Images werden zu GHCR übertragen. Beide Architekturen
   werden danach ohne Anmeldung geladen und mit den Prüfnachweisen verglichen.
   `container-digests.json` dokumentiert die veröffentlichten Versionen.
6. Das erste GHCR-Paket kann zunächst privat sein. In seinen Einstellungen auf
   **Public** stellen und bei fehlgeschlagener öffentlicher Prüfung **Re-run
   failed jobs** wählen. Den gesamten Build dafür nicht erneut starten.

RC4 erhält `ghcr.io/square-com-de/hue2lox:1.0.0-rc.4`. `latest` wird ausschließlich
für ein stabiles Release aktualisiert, das auch GitHub als aktuelles stabiles
Release führt. Erst nach erfolgreicher Veröffentlichung werden Downloadlinks
und Compose-Beispiele umgestellt. Laufende Installationen ändern sich dadurch
nicht automatisch.

Bei Abbrüchen können bereits einzelne Dateien oder Architektur-Tags vorhanden
sein. Erst ein grüner Abschluss von **verify-public** bestätigt den vollständigen
Ablauf. Abweichende vorhandene Release-Dateien und Versions-Images werden nicht
überschrieben. Bei einem vollständigen Neubau können sich Archivprüfsummen
ändern; dann untersuchen und gegebenenfalls eine neue Version veröffentlichen.
Die Beilagen dauerhaft beim Release und zusätzlich als Sicherung aufbewahren;
befristete CI-Artefakte ersetzen diese Downloads nicht.
