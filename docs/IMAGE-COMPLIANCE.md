# Container license and source materials

[Deutsch](#deutsch) | [English](#english)

## English

The container installation code can be merged independently of publishing images.
The workflow currently builds **without registry login or push**, for both amd64
and arm64, and saves an inventory of each actual image as a GitHub Actions artifact.
No existing RC ZIP, tag or running installation is changed. RC1–RC3 remain ZIP-only.

The candidate base is pinned by its multi-platform digest in both Dockerfiles.
`compliance/base-image.json` records the platform manifests. Changing this pin
requires regenerating and reviewing the materials; the current source locks must
not be used as approval for a different base.

### Materials prepared on 21 October 2026

- Base package inventory: 38 APK records per platform (including the virtual
  `.python-rundeps` dependency record), with versions, licenses and source commits.
- 27 Alpine package-origin recipe records, including build and installation files
  where retrieved; completeness is recorded explicitly in `compliance/recipes.json`.
- 180 Alpine source/patch inputs downloaded and verified against the SHA512 values
  in the matching APKBUILDs; lock: `compliance/source-checksums.json`.
- Python 3.12.15 source verified against the SHA256 embedded in the base image;
  pip 25.0.1 source verified against PyPI metadata. Locks are in
  `compliance/python-sources.json`. These archives contain additional license,
  copyright and vendored-component notices, which have been extracted for review.
- The local preparation archive contains collected sources, recipes, extracted
  notices and provenance. It is a review bundle, not a public source offer.

The large source archives are not committed to Git. Before distribution they must
be retained and made available beside the matching release. A checksum list alone
is **not** a source-delivery mechanism. GitHub Actions artifacts expire and require
access; they are also **not** a permanent recipient-facing source download.

### Remaining release checks

1. Download the amd64 and arm64 image-evidence artifacts. Map every actual runtime
   component, including pip's vendored libraries, to full licenses, copyright
   notices and matching sources/build recipes. Package license identifiers alone
   do not constitute a complete notice package. Resolve any missing recipe files.
2. Review components whose notices are in source headers rather than standalone
   LICENSE files, notably Alpine base files, signing keys and CA-package sources.
   Preserve applicable upstream text without inventing copyright holders.
3. Keep the existing Hue trust bundle unchanged as requested; this preparation
   does not independently establish certificate redistribution rights.
4. Record final image digests, source commit and both architectures; archive the
   exact matching source and notice bundle, its checksum and retrieval instructions.
   Fulfil the applicable source-delivery/retention terms for each license.
5. Test anonymous image and source downloads and actual container startup on each
   supported architecture. Choose and verify the first public image version.
6. Only then restore publishing in a reviewed change. Restrict `latest` to stable
   version tags, never RCs or branch runs. Intended registries: GHCR and Docker Hub;
   use the same versions/content on both. Docker Hub setup is still pending.

See [RELEASE.md](../RELEASE.md) for the complete release gate. Functional and
security test success does not imply license approval.

## Deutsch

Die Container-Unterstützung und der öffentliche Vertrieb fertiger Images sind
getrennte Schritte. Die Vorbereitung baut beide Architekturen, veröffentlicht aber
keine Images. RC3 und laufende Installationen bleiben unverändert.

Die Basis ist festgeschrieben; Paketlisten, Quellen-Prüfsummen und Herkunft sind
unter `compliance/` dokumentiert. Quellen, Patches und vorhandene Lizenztexte wurden
lokal gesammelt. Die Beilage muss vor Veröffentlichung noch mit den tatsächlichen
Images abgeglichen und vollständig zugeordnet werden. Insbesondere ersetzen weder
eine Paketliste noch befristete CI-Artefakte die erforderlichen Lizenz-/Quellen-
Downloads für Empfänger. Die englische Liste oben beschreibt die verbleibenden
Freigabeschritte. GHCR und Docker Hub sind als spätere Vertriebswege vorgesehen.
