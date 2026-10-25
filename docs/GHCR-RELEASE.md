# Publishing a container release / Container-Release veröffentlichen

## English

This is the maintainer runbook for versioned releases. Merging this workflow does
not push an image or update an installation. RC1–RC5 releases, tags and assets
remain unchanged. RC6 is published on both registries; Stable 1.0.0 follows the same verified workflow. See [Stable release notes](RELEASE-NOTES-1.0.0.md).

### Before publishing

1. Merge the reviewed installer and publication changes. Choose the exact commit
   on `main` intended for the release; finish the real-device acceptance and
   review the [container compliance evidence](IMAGE-COMPLIANCE.md). Prepare the
   version-specific installation/Compose references in that commit before tagging;
   the release ZIP preserves that exact source and cannot be corrected afterward.
2. Create a new tag, for example `v1.0.0`, at that commit. Never move an
   existing release tag. Create a draft GitHub release with short release notes.
   For an RC, select **Set as a pre-release**; for `v1.0.0`, leave that unchecked.
3. In the notes, link the installation guide and explain that the same version
   will be available as an installer ZIP and a multi-platform image in GHCR and Docker Hub. Link
   the release assets for corresponding sources, notices and platform evidence.
   Do not pre-upload a separately generated ZIP or checksum list: this workflow
   creates them from the tag and refuses to replace different existing files.
4. Check repository Actions permissions allow `GITHUB_TOKEN` to write packages.
   The first package is normally private. Its owner must set the `hue2lox`
   package's visibility to **Public** in its package settings after the first
   upload. A public repository alone does not guarantee a public package.

### Docker Hub setup

Create the **public** `dubctrl/hue2lox` repository. In this GitHub repository's
Settings → Secrets and variables → Actions, store `DOCKERHUB_USERNAME` (`dubctrl`)
and `DOCKERHUB_TOKEN` (a Docker Hub token with Read & Write, no Delete).
These credentials are used only by the release publisher and verification job;
PR tests never log in or push. GHCR continues to use the scoped `GITHUB_TOKEN`.
Missing/invalid credentials fail publication; they never silently skip Docker Hub.
RC5 publication supplies historical registry evidence; verify permissions again for the new release. Mocked PR tests cannot prove current registry access.
Never run the historical RC4 workflow to backfill Docker Hub.

### What publishing the release does

Clicking **Publish release** starts **Publish release images**. Merely pushing a
branch/tag, opening a PR, saving a draft or manually running the preparation
workflow cannot publish an image.

The workflow checks the tag, source commit and prerelease flag, and rejects the
historical RC1–RC5 tags. It runs the source tests, installer smoke tests and
HTTP/HTTPS container tests. Independently, it builds AMD64 and ARM64 candidates,
boots each, inventories them, creates SPDX SBOMs, and blocks on fixable high or
critical vulnerabilities. The source-material job compares both inventories
with the pinned license/source mappings and verifies source download hashes.

Only after every gate passes does the publisher:

- Attach `hue2lox-vVERSION.zip`, `hue2lox-VERSION-native.tar.gz`, `hue2lox-base-sources.tar.gz`,
  `container-evidence.tar.gz`, `container-release.json` and `SHA256SUMS.txt`
  permanently to the release, then verify their downloads without credentials.
- Load and verify the **same images** that were inventoried and scanned. There
  is no untested rebuild in the publishing job.
- Push architecture tags and the combined version tag to
  `ghcr.io/square-com-de/hue2lox` and `docker.io/dubctrl/hue2lox`.
- Pull both published platform digests from **each registry** anonymously and compare their image IDs
  with the candidate evidence; attach `container-digests.json` and its checksum
  to the release. Its `registries` field records both destinations; `platforms`
  retains the GHCR entries for compatibility. Both registries must pass before
  any stable promotion. Cross-registry uploads are not atomic: a partial failure
  may leave one registry published; retry the failed job with the original artifacts.
- For a stable release only, move `latest` if this is also GitHub's latest stable
  release. **An RC never creates or changes `latest`.**

For Stable 1.0.0, the version tag is `1.0.0` (without the leading `v`):

```sh
docker pull ghcr.io/square-com-de/hue2lox:1.0.0
podman pull docker.io/dubctrl/hue2lox:1.0.0
```

Use these versioned commands after the release publication workflow succeeds. Docker selects AMD64 or
ARM64 automatically. Announce the new download/Compose links only when those
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
channel. Link this runbook and the matching release from both registry descriptions.
Docker Hub and GHCR distribute the same binaries and corresponding source/license
assets; keep those links available in both places.
Record the first end-to-end publication result in the release notes; a PR test
cannot prove registry write permissions or package visibility.

## Deutsch

Dies ist der Maintainer-Ablauf für versionierte Releases. Das Zusammenführen
des PR veröffentlicht keine Images und ändert weder RC1–RC5 noch laufende
Installationen. RC6 ist auf Docker Hub und GHCR veröffentlicht. Stable 1.0.0 verwendet denselben geprüften Ablauf; siehe [Release-Hinweise](RELEASE-NOTES-1.0.0.md).

Vorher das öffentliche Docker-Hub-Repository `dubctrl/hue2lox` anlegen und im
GitHub-Repository unter Settings → Secrets and variables → Actions die Secrets
`DOCKERHUB_USERNAME` (`dubctrl`) und `DOCKERHUB_TOKEN` (Read & Write, ohne Delete)
hinterlegen. Nur Release-Jobs verwenden sie; PR-Tests melden sich nicht an und
veröffentlichen nichts. GHCR verwendet weiterhin `GITHUB_TOKEN`. Fehlende oder
ungültige Zugangsdaten stoppen den Ablauf. RC5 liefert historische Veröffentlichungsnachweise; aktuelle Schreibrechte beim
nächsten Release erneut bestätigen. Den alten RC4-Workflow nicht zum Nachliefern
nach Docker Hub starten. Beide Registry-Beschreibungen sollen auf die passenden
Release-, Quellen- und Lizenzbeilagen verweisen.

1. Geprüfte Änderungen zusammenführen, den vorgesehenen Commit auf `main`
   auswählen und die Abnahme mit echten Geräten sowie die Lizenzbeilagen prüfen.
   Versionsbezogene Installations-/Compose-Verweise vor dem Tag im Quellstand
   vorbereiten: Das Release-ZIP enthält exakt diesen Stand.
2. Einen neuen Tag wie `v1.0.0` an diesem Commit und einen Release-Entwurf
   anlegen. Beim RC **Set as a pre-release** aktivieren. Bestehende Tags bleiben
   unverändert. ZIP und Prüfsummen werden vom Workflow erzeugt.
3. Erst **Publish release** startet die Veröffentlichung. PRs, normale Pushes,
   Tags allein und manuelle Vorbereitungsläufe veröffentlichen nichts.
4. Tests, HTTP-/HTTPS-Installation, beide CPU-Architekturen, Schwachstellenscans
   und Quellenabgleich müssen erfolgreich sein. Anschließend werden Quellen,
   das native Archiv `hue2lox-VERSION-native.tar.gz`, vollständige Lizenzbeilagen, Inventare, SBOMs und Prüfsummen dauerhaft am
   Release hinterlegt und ohne Anmeldung heruntergeladen und geprüft.
5. Die exakt geprüften Images werden zu GHCR und Docker Hub übertragen. Beide Architekturen
   werden danach aus beiden Registries ohne Anmeldung geladen und mit den Prüfnachweisen verglichen.
   `container-digests.json` dokumentiert die veröffentlichten Versionen.
6. Das erste GHCR-Paket kann zunächst privat sein. In seinen Einstellungen auf
   **Public** stellen und bei fehlgeschlagener öffentlicher Prüfung **Re-run
   failed jobs** wählen. Den gesamten Build dafür nicht erneut starten.

Stable 1.0.0 erhält `ghcr.io/square-com-de/hue2lox:1.0.0` und
`docker.io/dubctrl/hue2lox:1.0.0` ; diese Referenzen erst nach erfolgreicher Veröffentlichung verwenden. Beide Registries müssen vor einer
Stable-Promotion erfolgreich geprüft sein. Uploads in zwei Registries sind nicht
atomar; bei Teilfehlern bleiben vorhandene Ergebnisse bestehen und der
fehlgeschlagene Job wird mit denselben Artefakten wiederholt. `latest` wird ausschließlich
für ein stabiles Release aktualisiert, das auch GitHub als aktuelles stabiles
Release führt. Die neuen Downloads und Compose-Beispiele erst nach erfolgreicher
Veröffentlichung als verfügbar ankündigen. Laufende Installationen ändern sich dadurch
nicht automatisch.

Bei Abbrüchen können bereits einzelne Dateien oder Architektur-Tags vorhanden
sein. Erst ein grüner Abschluss von **verify-public** bestätigt den vollständigen
Ablauf. Abweichende vorhandene Release-Dateien und Versions-Images werden nicht
überschrieben. Bei einem vollständigen Neubau können sich Archivprüfsummen
ändern; dann untersuchen und gegebenenfalls eine neue Version veröffentlichen.
Die Beilagen dauerhaft beim Release und zusätzlich als Sicherung aufbewahren;
befristete CI-Artefakte ersetzen diese Downloads nicht.

## Installer version for the next release / Installer-Version

Before creating a new release tag, set `install/release-image.json` to the same version without the leading `v` (for example, tag `v1.0.0` → version `1.0.0`). Release publication refuses a mismatch so a new ZIP cannot silently install the previous release image. Do not retag or replace RC5. During development, the file continues to name the last published version; select local build to test `main`.

Vor einem neuen Release-Tag muss `install/release-image.json` dieselbe Version ohne führendes `v` enthalten. Die Veröffentlichung stoppt bei Abweichungen, damit ein neues ZIP nicht unbemerkt das vorherige Image installiert. RC5 nicht neu taggen oder ersetzen. Während der Entwicklung bleibt die letzte veröffentlichte Version eingetragen; Änderungen aus `main` mit lokalem Build testen.

## Native release asset / Natives Release-Asset

`prepare` builds the native archive in a clean local clone of the exact release commit, alongside the source ZIP. It rejects dirty identity, wrong version/commit, unexpected entries and mismatching file hashes. The common `SHA256SUMS.txt` covers the native archive; `publish` uses the same immutable-asset and anonymous-byte-verification path as the ZIP. A different existing asset is never overwritten. No native pip packages, container or hardware access are required for package creation. Native runtime support remains experimental and amd64-only, independent of ARM64 container availability.

`prepare` baut das native Archiv in einem sauberen lokalen Klon desselben Release-Commits wie das Quell-ZIP. Falsche Version/Commit-ID, unsaubere Identität, unerwartete Einträge oder falsche Dateihashes stoppen den Ablauf. Die gemeinsame `SHA256SUMS.txt` enthält das native Archiv; Upload und anonyme Byteprüfung verwenden denselben unveränderlichen Asset-Pfad wie das ZIP. Abweichende vorhandene Assets werden nicht überschrieben. Für den Paketbau sind weder pip-Pakete noch Container oder Hardwarezugriff nötig. Native Laufzeitunterstützung bleibt experimentell und auf amd64 begrenzt, unabhängig von ARM64-Containern.

Use the [offline RC6 package check](RC6-PREPARATION.md#isolierte-paketprüfung--isolated-package-checks) before publication. / Vor Veröffentlichung die isolierte Paketprüfung verwenden. It creates no tag or release. / Sie erstellt keinen Tag und kein Release.

## Stable acceptance gate

**Applies to release commits containing this gate, after its PR is merged.** Published 1.0.0/1.0.1 and their older workflow checkouts are unchanged. The current `compliance/stable-readiness.json` deliberately approves no next version. Green CI alone cannot open it.

Before creating a stable tag or publishing a GitHub stable release:

1. Choose an unused SemVer from the actual releases/tags. Prepare the versioned README/install/Compose references and candidate code first. Keep it immutable while the Deployer tests the exact documented user flow, update/recovery and declared runtime scope. Record container/desktop versions, data state, exact commands or GUI clicks, image digest, observed login/restart and hardware boundaries.
2. Obtain independent DE/EN documentation review and operator/user acceptance. Link public, sanitized GitHub evidence for `documentation_review`, `published_user_flow`, `update_recovery` and `support_scope`. The last check must describe missing/experimental platforms and hardware scope, not pretend every device passed. Do not publish private backup paths, keys or tokens as evidence. The validator checks the record and content binding, not the truth of a linked report; the reviewer must inspect actual observations rather than approve from links or green test counts.
3. On the committed, clean accepted candidate, run:

   ```sh
   python3 scripts/release-image.py source-fingerprint
   ```

   Copy its `source_sha256` into `compliance/stable-readiness.json`, set the exact target `version`, each evidenced `passed` to `true`, and `approved` to `true` only after explicit release approval. Commit **only that approval record** after acceptance. Any other code/documentation change invalidates the fingerprint and requires renewed approval and validation of the affected scope. The fingerprint covers tracked content, excluding only the approval record; a version match alone is insufficient.
4. Before tagging, run the offline check for the chosen version, for example:

   ```sh
   python3 scripts/release-image.py check-readiness --version 1.0.2
   ```

   The example is not an instruction to reuse an existing tag. A blocked result is a release stop, not an installer error. Do not bypass it or blindly mark missing checks passed. RC preparation/source packages stay available without stable approval and must remain prereleases; no `latest` promotion.
5. Follow the existing immutable tag/material/public-pull process above. The workflow checks readiness before publication and again before public verification/latest promotion. Approval does not update production. Report source commit, version, assets/digests, tested scope and remaining limits separately.

### Deutsch

Das Gate gilt erst für neue Release-Commits nach Merge dieses PRs; alte Releases/Workflows bleiben unverändert. Der Datensatz ist bewusst geschlossen und nennt noch keine freigegebene nächste Version. Vor Stable-Tag/GitHub-Veröffentlichung: Version und endgültige Anleitungen vorbereiten, exakten Kandidaten unabhängig abnehmen lassen, DE/EN-Review und Betreiberfreigabe mit bereinigten GitHub-Nachweisen für die vier Prüfbereiche dokumentieren. `source-fingerprint` auf dem sauberen Commit ausführen; erst danach ausschließlich den Freigabedatensatz mit Version, Inhaltsfingerprint, Nachweisen und ausdrücklicher Genehmigung committen. Andere Code-/Dokuänderungen entwerten die Abnahme. `check-readiness --version GEWAEHLTE_VERSION` muss vor dem Taggen erfolgreich sein. Keine Checkliste automatisch aus grüner CI freischalten. Das Gate ersetzt keine Hardwareabnahme und erlaubt kein Produktivupdate; RC-/lokale Kandidatenvorbereitung bleibt möglich.

### Reproduzierbare Offline-Archive / reproducible offline archives

Der Release-Builder setzt für `git archive` ausdrücklich `TZ=UTC`, damit dieselbe Commit-ID unabhängig von der Zeitzone des Build-Hosts dasselbe Quellcode-ZIP erzeugt. Für historische RC6-Stände ohne diese Normalisierung muss bei manueller Reproduktion `TZ=UTC` gesetzt werden. Bestehende Release-Dateien werden nicht ersetzt.

The release builder explicitly sets `TZ=UTC` for `git archive` so the same commit produces identical source ZIP bytes regardless of the build host timezone. When manually reproducing historical RC6 sources without this normalization, set `TZ=UTC`. Existing release assets remain unchanged.
