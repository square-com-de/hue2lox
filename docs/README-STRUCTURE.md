# Product README structure

A reusable structure for project entry pages. Inspired by the ordering of the [Herdr README](https://github.com/herdrdev/herdr), not by copying its text, assets or installation commands.

1. Existing approved logo, project name and one sentence explaining its purpose.
2. Real current screenshot or short demo, with source version and any test-data limitations stated.
3. Five or six supported features, with no unverified compatibility promises.
4. One default quick start using an available, verified release. Include prerequisites, actual access URL, initial login/password change, persistence and essential TLS/URL requirements.
5. First-use steps leading to one useful result.
6. Links to alternative deployment paths and custom configuration, with limits.
7. Documentation, help, security, contribution and license links.

English is the default public README; link the German equivalent and preserve information parity. Keep installation, update, migration, certificate, recovery and troubleshooting details in their existing guides. A README refactor must not change release pins, application behavior or deployments. Before merging, check links/anchors, command provenance, screenshot privacy and GitHub desktop/mobile rendering. A landing page can use this order without inventing extra functionality.

## Hue2Lox reference

The README quick start uses the published `v1.0.2/docker/compose.quickstart.yaml`, fetched and checked against the current release on 25 October 2026. It publishes HTTP port 18443 and creates a named `/data` volume. The current release source is `2af13f603c97064fd01585ea04d893a5fdad1081`; the [published platform digests](https://github.com/square-com-de/hue2lox/releases/download/v1.0.2/container-digests.json) record index `sha256:5943a9ac4b2889c767d2e884572a99b64ab45d6f95aeb80a1b944f40545340f7`.

`images/hue2lox-1.0.2.png` is an actual browser capture from the final published 1.0.2 acceptance on 25 October 2026, not a generated mockup. The registry is empty; the German UI and old release footer are intentionally shown as shipped. It contains no credentials, real device inventory or private network addresses. The capture itself is unchanged; it is not proof of a new fresh-install test.

[Final 1.0.2 acceptance](https://github.com/square-com-de/hue2lox/issues/51) establishes public image identity, retained-password browser login, restart and preserved data. Historical fresh-OS/Portainer tests remain bound to 1.0.1 in their reports. A fresh 1.0.2 quick-start/Portainer default-login observation must be identified separately before describing it as newly tested. This reference does not promote 1.0.3, claim hardware results or change the runtime support matrix.
