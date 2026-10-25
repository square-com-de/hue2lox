> **Historischer Stand / Historical record:** Aussagen, Befehle und offene Punkte unten gelten ausschließlich für den genannten damaligen Stand, nicht als aktuelle Installationsanleitung oder 1.0.3-Abnahme. / Statements, commands and pending checks below apply only to the recorded revision. [Aktuelle Dokumentation / current documentation](INDEX.md) · [1.0.3-Vorbereitung / preparation](PREPARATION-1.0.3.md).

# Hue2Lox 1.0.1 — desktop login fix / Desktop-Anmeldung

## English

Fresh image startup in Podman Desktop now works without environment variables: load the image, choose Run Image → Create and start, open the published HTTP port and sign in with `admin / admin`. Existing data keeps its existing password.

Direct access via localhost or a private IP uses the actual HTTP/HTTPS address and mapped port for origin checks, cookies and generated URLs. An explicitly configured `HUE_PUBLIC_URL` still takes precedence for reverse proxies/custom DNS names; forwarding headers cannot override it. Cross-origin requests and unconfigured arbitrary DNS hosts remain rejected.

Login failures now distinguish wrong credentials from an address/configuration mismatch in German and English. No password resets or data migration. Version 1.0.0 and older releases remain unchanged. Native support remains experimental.

## Deutsch

Ein frisches Image funktioniert jetzt direkt in Podman Desktop: Image laden, Run Image → Create and start, veröffentlichten HTTP-Port öffnen und mit `admin / admin` anmelden. Vorhandene Daten behalten ihr bisheriges Passwort.

Für localhost oder private IP-Adressen werden Protokoll und weitergeleiteter Port automatisch berücksichtigt. Eine ausdrücklich gesetzte `HUE_PUBLIC_URL` bleibt für Reverse Proxies/eigene DNS-Namen maßgeblich. Fremde Browserursprünge werden weiterhin abgewiesen.

Die Anmeldung unterscheidet nun falsche Zugangsdaten von einer unpassenden Browseradresse. Keine Passwort-Rücksetzung und keine Datenmigration. 1.0.0 und ältere Releases bleiben unverändert. Native Unterstützung bleibt experimentell.
