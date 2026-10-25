> **Historischer Stand / Historical record:** Aussagen, Befehle und offene Punkte unten gelten ausschließlich für den genannten damaligen Stand, nicht als aktuelle Installationsanleitung oder 1.0.3-Abnahme. / Statements, commands and pending checks below apply only to the recorded revision. [Aktuelle Dokumentation / current documentation](../INDEX.md) · [1.0.3-Vorbereitung / preparation](../PREPARATION-1.0.3.md).

# Public Podman Desktop flow — 1.0.1

Recorded 24 October 2026 by the deployment task, independently reconciled with release metadata. This is a manual GUI record, not an inference from the unit tests. No real Hue/Loxone control was exercised.

| Item | Evidence |
|---|---|
| Source | [PR47](https://github.com/square-com-de/hue2lox/pull/47), release commit `f245a4ddd8857706f6ded748fb6945ea5aa88a38` |
| Runtime scope | Podman Desktop **1.30.5**, macOS **ARM64**. Local CLI `podman --version` later captured **6.1.4**; the GUI report did not separately capture the VM/server version, so no broader Engine-version claim is made. |
| Actual public flow | Images → Pull `docker.io/dubctrl/hue2lox:1.0.1` → Run Image → Create and start with defaults and a fresh writable data volume → Open Browser on mapped HTTP port → `admin/admin` successful |
| Persistence | Browser reload retains session; Podman Desktop restart allows relogin. Existing volumes were not reset. |
| Errors | Wrong password remains rejected; address/configuration rejection has a distinct DE/EN message. These error cases were exercised on the pre-publication candidate, not claimed as a second test of the public image. |
| Public ARM64 manifest | `sha256:d415055ab232f43adc8bd57bbbd70eb4d476de451aada411062a8702c8305aa4` |
| Pulled image ID | `sha256:5926b148c1529034f6f27ae0bc224470f06bda25cf1c20f7cfb4edcad56b70e6` |
| Shared index, both registries | `sha256:7e12e1491937c36cec763850b3db1c60916e727bf9bbdb82a4f5447e5812076b` |
| Technical evidence | [Release workflow](https://github.com/square-com-de/hue2lox/actions/runs/40100051393): 329 tests and all 14 jobs successful, public downloads and both architectures/registries verified. [Published digests](https://github.com/square-com-de/hue2lox/releases/download/v1.0.1/container-digests.json). |

The older failed attempt had no `HUE_PUBLIC_URL`; requests reached the app and login returned HTTP 403. In [1.0.0](https://github.com/square-com-de/hue2lox/blob/v1.0.0/src/loxone_export.py#L14), an absent URL fell back to `https://localhost:8443`, while the default container served HTTP. [Origin checking](https://github.com/square-com-de/hue2lox/blob/v1.0.0/src/app.py#L378) rejected that mismatch before password verification. This establishes the address/login defect; it is not evidence of generic Podman incompatibility. The precise image identity of every earlier user attempt was not retained, so the failed container is not retrospectively assigned an unverified release tag.

[PR47](https://github.com/square-com-de/hue2lox/pull/47) makes direct local/private addresses request-scoped while retaining explicit URL precedence, origin/CSRF protections and existing passwords. The shipped path needs no manual environment workaround. Custom proxy/DNS setups remain separate.

Still outside this acceptance: Windows/Linux Podman, `podman compose`, Docker Desktop, actual bridge discovery/pairing and Loxone LAN commands from the desktop VM. The source repository gate added after 1.0.1 cannot retroactively block its already published workflow; it gates future release commits only after that gate is merged.

## Additional isolated source reproduction

[Machine-readable result](login-origin-reproduction.json): launch the actual tagged sources `v1.0.0` and `v1.0.1` separately with the same synthetic credentials, empty registry, HTTP loopback binding and **no HUE_PUBLIC_URL/TLS variables**. Writes are disabled and a Python audit guard rejects all non-loopback connections. Health is 200 in both; login is 403 `invalid_origin` in 1.0.0 and 200 in 1.0.1. Processes and temporary data are isolated; this confirms the address-origin defect, not an additional Podman runtime or hardware acceptance. No real passwords/tokens or old user-container data are used.

## Additional named-volume CLI check

[Result](podman-named-volume-1.0.1.json): the named-volume `podman run` options from the container guide were exercised on macOS 27.0.1 ARM64, Podman client **6.1.4** and VM engine **6.1.4** (linux/arm64). Only disposable unique container/volume names and a free loopback host port replaced the example values. The actual public image ID matched the published ARM64 image. No HUE_PUBLIC_URL/TLS overrides: fresh login, writable named volume, restart/relogin and unchanged credential file passed. The registry remained empty. Only this temporary container/volume were removed; no other container, image, user volume or hardware was changed. This adds a CLI-path observation, not Windows/Linux/Podman-Compose or LAN acceptance.
