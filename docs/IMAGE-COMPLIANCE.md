# Container license and source materials

[Deutsch](#deutsch) | [English](#english)

## English

The source/notice bundle is assembled by `scripts/build-source-bundle.py` from
checksum-locked upstream inputs. The workflow builds AMD64 and ARM64 images,
compares their runtime inventories with the bundle, then saves the archive and
checksum. It does **not** log into or push to a registry.

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

### At the first image publication

Attach this bundle and checksum as permanent, anonymously downloadable release
assets alongside the application source. Record the final published image digests,
source commit and architectures, link the source assets from each registry, and
verify startup/downloads for the actual published image. CI artifacts expire and
are not the recipient-facing download. Keep the source assets while their images
are offered and retain an archived copy.

Publishing remains disabled until that release step is implemented and tested.
Only stable version tags may receive `latest`; RCs and branch builds must not.
Intended registries are GHCR and Docker Hub. RC1–RC3 and running installations
remain unchanged. See [RELEASE.md](../RELEASE.md) for application acceptance.

## Deutsch

Die Lizenz- und Quellenbeilage wird jetzt automatisch aus festgeschriebenen,
prüfsummengeprüften Originalquellen gebaut und mit beiden Container-Architekturen
abgeglichen. Erfasst sind 22 Alpine-Paketursprünge mit vollständigen Rezepten,
211 Quellen/Patches, Python, pip und alle 18 darin enthaltenen Bibliotheken.
Lizenztexte, Copyrightangaben und Hinweise in Quelldateien bleiben erhalten;
fehlende Urheberangaben werden nicht erfunden.

[CONTAINER-SOURCES.md](CONTAINER-SOURCES.md) beschreibt Inhalt und Archivbau.
Beim ersten öffentlichen Image-Release müssen Archiv und Prüfsumme als dauerhafte
Downloads neben dem passenden Anwendungsquellcode angehängt und von der Registry
verlinkt werden. Erst dann wird die Veröffentlichung der Images aktiviert.
CI-Artefakte ersetzen diesen dauerhaften Download nicht. RC3 und laufende
Installationen bleiben unverändert; die Hue-CA bleibt wie vereinbart enthalten.
