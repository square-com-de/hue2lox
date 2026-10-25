# Container license and source materials

[Deutsch](#deutsch) | [English](#english)

## English

The source/notice bundle is assembled by `scripts/build-source-bundle.py` from
checksum-locked upstream inputs. The workflow builds AMD64 and ARM64 images,
compares their runtime inventories with the bundle, then saves the archive and
checksum. This preparation workflow does **not** log into or push to a registry; the separate
[release workflow](GHCR-RELEASE.md) publishes only after these checks pass.

### Completed source and notice collection

- 33 APK records per platform, including the virtual `.python-rundeps` record.
- Complete build/install recipe directories for 22 Alpine package origins.
- 211 Alpine source/patch inputs checked against the exact APKBUILD SHA512 values.
  Inline checksum declarations are checked too.
- Python 3.15.0 and pip 26.2.1 sources, hash-checked.
- All 18 pip-vendored library entries mapped to original notices and sources,
  including indented entries in pip's vendor manifest.
- Original notice texts and source-header notices, including CA-package headers;
  complete referenced MIT, MPL-2.0 and GPL-2.0 texts are included.
- Alpine generated data/configuration and public-key packages retain their exact
  upstream recipes and files. No copyright holder is inferred from a maintainer.
- The exact official Python image Dockerfile and its license are included.
- 86 component records in total (both platform inventories, Python/pip,
  and the 18 vendored entries). Every mapped path is verified to exist.

The base digest is pinned in both Dockerfiles and recorded in
`compliance/base-image.json`. A base or runtime-dependency change requires updated
source locks and mappings. The builder refuses missing APKBUILD inputs, checksum
mismatches and inventories that differ from the recorded runtime components.

See [CONTAINER-SOURCES.md](CONTAINER-SOURCES.md) for bundle contents, regeneration
and delivery instructions. Full upstream archives preserve per-file notices,
not merely package license identifiers. Hue2Lox's own license/catalog notices
remain in the application source release. The Hue trust bundle stays unchanged
as agreed; this work makes no new claim about its redistribution rights.

### At each image publication

Attach this bundle and checksum as permanent, anonymously downloadable release
assets alongside the application source. Record the final published image digests,
source commit and architectures, link the source assets from each registry, and
verify startup/downloads for the actual published image. CI artifacts expire and
are not the recipient-facing download. Keep the source assets while their images
are offered and retain an archived copy.

RC5 uses the gated release workflow and permanent assets on its
[release page](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.5).
Only stable version tags may receive `latest`; RCs and branch builds must not.
RC5 targets GHCR and Docker Hub with the same verified images. RC1–RC4 and running installations
remain unchanged. See [RELEASE.md](../RELEASE.md) for application acceptance.

## Deutsch

Die Lizenz- und Quellenbeilage wird jetzt automatisch aus festgeschriebenen,
prüfsummengeprüften Originalquellen gebaut und mit beiden Container-Architekturen
abgeglichen. Erfasst sind 22 Alpine-Paketursprünge mit vollständigen Rezepten,
211 Quellen/Patches, Python, pip und alle 18 darin enthaltenen Bibliotheken.
Lizenztexte, Copyrightangaben und Hinweise in Quelldateien bleiben erhalten;
fehlende Urheberangaben werden nicht erfunden.

[CONTAINER-SOURCES.md](CONTAINER-SOURCES.md) beschreibt Inhalt und Archivbau.
Bei jedem öffentlichen Image-Release müssen Archiv und Prüfsumme als dauerhafte
Downloads neben dem passenden Anwendungsquellcode angehängt und von der Registry
verlinkt werden. Der Release-Workflow prüft diese Downloads vor dem
Upload zu GHCR und Docker Hub. Beide Registries erhalten dieselben geprüften Images.
CI-Artefakte ersetzen diesen dauerhaften Download nicht. Bestehende Releases und laufende
Installationen bleiben unverändert; die Hue-CA bleibt wie vereinbart enthalten.

## Runtime package tooling / Paketwerkzeuge im Laufzeitimage

Hue2Lox requires only Python's standard library. The final image removes pip and
ensurepip (including bundled wheels). The base-image pip sources and notices
remain in this bundle for provenance, marked `runtime: false`, along with pip's
vendored dependencies. They must not appear in the final runtime inventory.
No vulnerability exclusions are used.

Hue2Lox benötigt nur die Python-Standardbibliothek. Im fertigen Image werden pip
und ensurepip samt eingebetteten Paketen entfernt. Ihre Quellen und Lizenztexte
bleiben zur Dokumentation der Basis enthalten (`runtime: false`), dürfen aber
nicht im Inventar des fertigen Images erscheinen. Es gibt keine Scan-Ausnahmen.
