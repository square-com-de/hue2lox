# Hue2Lox 1.0.3 — vorbereitet / unreleased

**Noch nicht veröffentlicht. Keine Freigabe für Veröffentlichung oder Produktionsrollout. / Not published. Publication and production rollout are not authorized.**

## Deutsch

Änderungen gegenüber dem veröffentlichten 1.0.2:

- Sidebar zeigt nur noch „Hue2Lox“ mit der dynamischen installierten Version. Grüner Punkt und redundante Netzwerk-/Verwaltungstexte entfallen ([#54](https://github.com/square-com-de/hue2lox/pull/54)).
- Offline-Quell-ZIP wird mit UTC-Zeitstempeln unabhängig von der Host-Zeitzone erzeugt. Ein echter Zeitzonen-Bytevergleich deckt den bisherigen Fehler ab ([#55](https://github.com/square-com-de/hue2lox/pull/55), [#44](https://github.com/square-com-de/hue2lox/issues/44)). Historische Release-Dateien werden nicht ersetzt.
- DE/EN erklären die Standards ausdrücklich: Container HTTP; nativ direktes HTTPS; Traefik terminiert Browser-HTTPS und verwendet intern HTTP. Konkrete Konfigurationsorte, vollständige Traefik-Vorlage und Auswirkungen auf Loxone-URLs sind dokumentiert ([#56](https://github.com/square-com-de/hue2lox/pull/56)).
- Installationsauswahl: Docker, Podman und nativer Installer. AI-Installationsprompts entfernt. Bestehende Docker-Installer behalten ihre Wartungswerkzeuge. Kein natives Traefik-Profil zugesichert.

Anwendungskern, Lampen-/Szenensteuerung, Zugangsdaten und Datenformat bleiben gegenüber 1.0.2 unverändert. Nativ bleibt experimentell/amd64; Podman nur im dokumentierten Umfang. Die Traefik-Vorlage ist ein Konfigurationsbeispiel, keine reale Traefik-Abnahme. Historische Hardwaretests werden nicht als neue 1.0.3-Abnahme ausgegeben; offene Hardwareliste: [#42](https://github.com/square-com-de/hue2lox/issues/42).

Vor einem späteren Update Datenvolume, Konfiguration, Zertifikate und exaktes altes Image kalt sichern. Dasselbe Volume und absichtlich deaktivierte Flags behalten. Vorhandene Container müssen neu erstellt werden; ein Neustart allein aktualisiert weder Image noch Variablen. [Docker-Update und Rollback](UPDATE-DOCKER.de.md) · [Native Wartung](INSTALL-NATIVE.md). Veröffentlichung, tatsächliche öffentliche Artefaktprüfung und Produktionsrollout sind separate Schritte.

## English

Changes since published 1.0.2:

- Keep only the dynamic installed Hue2Lox version in the sidebar; remove the green dot and redundant local-network/administration labels (#54).
- Normalize git archive to UTC for host-timezone-independent source ZIP bytes, with a real cross-timezone byte regression (#55, fixes #44). Historical release assets remain immutable.
- Explain container HTTP/native HTTPS defaults, exact environment configuration locations, the complete existing-Traefik Compose example and Loxone URL implications in both languages (#56).
- Offer Docker, Podman and the native installer. Remove AI installation prompts; preserve maintenance for existing Docker-installer deployments. No native Traefik profile is promised.

Application core, lighting/scene commands, credentials and data format are unchanged from 1.0.2. Native remains experimental/amd64; Podman scope stays limited to documented evidence. The Traefik template is a configuration example, not a real deployment acceptance. Historical hardware tests are not new 1.0.3 evidence; open hardware checklist: [#42](https://github.com/square-com-de/hue2lox/issues/42).

Before any later update take a cold backup of data, configuration, certificates and the exact old image. Retain the volume and intentionally disabled flags. Recreate containers; restart alone updates neither image nor environment. [Docker update/rollback](UPDATE-DOCKER.md) · [Native maintenance](INSTALL-NATIVE.en.md). Publication, actual public-artifact verification and production rollout are separate actions.
