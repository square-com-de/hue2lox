# Hue2Lox – third-party notices / Quellen und Lizenzen

Reviewed: 20 October 2026. Original Hue2Lox code, documentation and project assets are licensed under Apache License 2.0, to the extent applicable rights exist. See LICENSE and NOTICE. Third-party components retain their own licenses; the project license does not replace the terms below.

## Sidebar navigation icons – Iconoir

Six Regular icons from Iconoir v7.12.1: dashboard, light-bulb, sparks, network, activity and settings. Original geometry is combined into the local SVG symbol sprite `web/sidebar-icons.svg`; no CDN, font or JavaScript dependency is used. These navigation icons are separate from the original Hue2Lox lamp-shape icons below.

- Source: https://github.com/iconoir-icons/iconoir/tree/v7.12.1/icons/regular
- Copyright (c) 2021 Luca Burgio. License: MIT. The complete original notice is retained in `web/sidebar-icons-LICENSE.txt` and served at `/assets/sidebar-icons-license.txt`.
- Upstream license: https://github.com/iconoir-icons/iconoir/blob/v7.12.1/LICENSE

## Original light icons

The current lamp icons are original geometric SVG drawings created for Hue2Lox, approved on 19 October 2026. See docs/ICONS.md and `web/lamp-icons/`. The former third-party icon bundle is no longer shipped in the current source or new builds. Historical releases/commits and existing backups retain their original license obligations; they are not retroactively relicensed. Original project assets are covered by Apache License 2.0 to the extent applicable rights exist.

## Model catalog – zigbee-herdsman-converters

- Source: https://github.com/Koenkk/zigbee-herdsman-converters/blob/master/src/devices/philips.ts
- License: MIT; original copyright notice and full license retained in `catalog/LICENSE-zigbee-herdsman-converters`, also served at `/assets/catalog-license.txt`.
- Adaptation: model identifiers, descriptions and declared capabilities extracted into JSON/CSV by `tools/build_hue_catalog.py`. Source date and hash are in `catalog/hue-models.json`.
- Community-maintained data, not a complete manufacturer directory. Live bridge capabilities take precedence.

## Hue certificate trust anchor

`trust/huebridge-ca.pem` was sourced from the Raycast Hue extension at revision `eb2e5bff8a2ed8b12208f0835827d9bd35027692`:
https://github.com/raycast/extensions/blob/eb2e5bff8a2ed8b12208f0835827d9bd35027692/extensions/hue/assets/huebridge_cacert.pem

This is a public trust certificate, not a private key. Source provenance is recorded; certificate redistribution terms and applicable upstream notices must still be verified before a public release. The repository's general license is not assumed to grant rights to every third-party asset it contains.

## Container/runtime dependencies

The image uses the official `python:3.12-alpine` base image, pinned by digest in both Dockerfiles. Candidate package/source inventories are recorded under `compliance/`; see [image preparation status](docs/IMAGE-COMPLIANCE.md). These preparation records do not yet constitute full image-distribution approval. Python and its standard library have the PSF license and additional notices: https://docs.python.org/3.12/license.html . Alpine packages, OpenSSL and other runtime components retain their respective licenses. Hue2Lox installs no additional pip packages, but the base image can include pip and its vendored libraries. These and all transitive runtime components must be included in any image inventory.

The planned release distributes source code, installer and Dockerfiles only. Users build locally and obtain the base image directly from its upstream provider. No prebuilt Hue2Lox images, image archives or VM/appliance images are currently offered. This does not remove the license obligations for third-party materials actually bundled in our source archive, including the catalog and certificate bundle.

Before distributing a built image: pin and record the actual base-image digest, generate an inventory/SBOM of the built image and preserve relevant license/source-offer obligations. This document is not a complete binary-image license audit. The release gate is documented in RELEASE.md; passing security scans does not satisfy it.

## Branding and screenshots

The octopus assets were generated with Imagegen for this project; provenance is in docs/LOGO.md. No third-party lamp manufacturer endorsement is implied. Hue/Philips Hue and Loxone names identify compatible products; this is an independent project. Verify naming/branding and screenshot publication rights before a public release. Tutorial screenshots currently show German UI.

## Deutsch: Status vor Veröffentlichung

Hue2Lox steht unter Apache 2.0; siehe LICENSE und NOTICE. Drittanbieterbedingungen bleiben bestehen. Die aktuellen Lampensymbole sind eigenständig gezeichnete SVGs. Das bisherige Iconpaket wurde aus dem aktuellen Stand entfernt; historische Kopien behalten ihre ursprünglichen Lizenzbedingungen. Der MIT-Hinweis des Modellkatalogs bleibt enthalten. Zertifikatsweitergabe und Marken-/Screenshotrechte bleiben zu prüfen. Vorerst ist nur Quellcode-Verteilung mit lokalem Docker-Build geplant; vor einem späteren Vertrieb fertiger Images müssen deren komponentenspezifische Lizenz- und Quellenunterlagen vollständig vorliegen. Siehe RELEASE.md.

The standalone catalog download bundles CSV, source notice and full upstream MIT license. Pinned catalog source commit: `499535e092401a6c21e8c3b5e3aeca8062c11841`.
