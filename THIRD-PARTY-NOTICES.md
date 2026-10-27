# Hue2Lox – third-party notices / Quellen und Lizenzen

Reviewed: 23 October 2026 for the unpublished RC6 preparation. Original Hue2Lox code, documentation and project assets are licensed under Apache License 2.0, to the extent applicable rights exist. See LICENSE and NOTICE. Third-party components retain their own licenses; the project license does not replace the terms below.

## Navigation and header icons – Iconoir

Ten Regular icons from Iconoir v7.12.1: dashboard, light-bulb, sparks, network, activity, settings, refresh, key, log-out and arrow-right. Original geometry is combined into the local SVG symbol sprite `web/sidebar-icons.svg` and the inline login arrow in `web/index.html`; no CDN, font or JavaScript dependency is used. These navigation icons are separate from the original Hue2Lox lamp-shape icons below.

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

The two public trust certificates are not private keys. The bundle is byte-identical to the pinned source (SHA256 `2ff54626fc51de587cce0f3f0339552f89da781b5d5949fa0c90ec30ddf8acfa`). That revision declares MIT in the Hue extension package.json and carries the root MIT license, copyright (c) 2021 Raycast. The complete original text is retained in `trust/LICENSE-raycast.txt` and below so it accompanies source, native and Docker distributions. Certificate issuers remain Philips Hue and Signify Hue; no endorsement, ownership transfer or Apache relicensing is implied.

## Container/runtime dependencies

The Docker image uses official `python:3.15-alpine`, pinned by digest in both Dockerfiles and `compliance/base-image.json`. Python is 3.15.0 in the locked candidate; native deployment uses the supported operating system's Python (minimum 3.11), not the Docker base. Python and its standard library have the PSF license and additional notices: https://docs.python.org/3.15/license.html . Alpine, OpenSSL and other runtime components retain their individual terms.

No application pip packages are installed. pip and ensurepip, including vendored wheels, are removed from the final Docker runtime. Their original sources/notices remain in the source-material bundle as non-runtime provenance. Actual AMD64/ARM64 inventories, SPDX SBOMs and scans are compared with the checksum-locked component/source records. See [container sources](docs/CONTAINER-SOURCES.md) and [compliance evidence](docs/IMAGE-COMPLIANCE.md).

RC5 already distributes prebuilt images through Docker Hub and GHCR with permanent source/license assets on its unchanged release page. RC6 is unpublished preparation. Its source ZIP, native archive, exact container candidates and corresponding source/license evidence must share the release commit. The publication workflow checks inventories and downloads and refuses differing existing version assets. CI artifacts alone are not the permanent source-delivery channel. No VM/appliance image is offered.

## Branding and screenshots

The octopus assets were generated with Imagegen for this project; provenance is in docs/LOGO.md. No third-party lamp manufacturer endorsement is implied. Hue/Philips Hue and Loxone names identify compatible products; this is an independent project. The original generated project artwork and original geometric light icons are recorded in docs/LOGO.md and docs/ICONS.md. Tutorial illustrations use project test data; they are not official manufacturer artwork or a compatibility certification. No right to third-party trademarks is granted by this project license.

## Deutsch: Lizenz- und Quellenstand

Eigene Bestandteile stehen unter Apache 2.0. Iconoir-Symbole, Modellkatalog und das unverändert aus dem MIT-lizenzierten Raycast-Quellstand übernommene öffentliche CA-Bundle behalten ihre Originalhinweise. Vollständige MIT-Texte sind beigefügt; die eigene Lizenz ersetzt diese nicht. Oktopus-Grafiken und geometrische Lampensymbole wurden für das Projekt erstellt; fremde Marken bezeichnen kompatible Produkte und keine offizielle Verbindung.

Docker verwendet Python 3.15 auf Alpine, gepinnt und mit Inventar-/Quellenabgleich für AMD64/ARM64. Nativ verwendet Hue2Lox das unterstützte System-Python ab 3.11 und bleibt experimentell. pip/ensurepip sind nicht im fertigen Docker-Laufzeitimage enthalten. RC5-Images und ihre Quellenbeilagen sind veröffentlicht; RC6 samt nativem Archiv ist noch unveröffentlicht. Die finalen Beilagen und tatsächlichen anonymen Downloads werden im Release-Ablauf geprüft. Hardware- und Stable-Freigabe sind davon getrennt.

The standalone catalog download bundles CSV, source notice and full upstream MIT license. Pinned catalog source commit: `499535e092401a6c21e8c3b5e3aeca8062c11841`.

## Complete Raycast upstream MIT notice / Vollständiger MIT-Originalhinweis

MIT License

Copyright (c) 2021 Raycast

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
