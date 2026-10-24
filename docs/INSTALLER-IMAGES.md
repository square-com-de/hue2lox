**Release version / Release-Version:** The 1.0.1 source ZIP pins `1.0.1` in both registry selections. Verify release publication before using prebuilt images. Local builds remain an explicit alternative. / Das 1.0.1-Quell-ZIP bindet bei beiden Registries `1.0.1`. Vor Verwendung fertiger Images den erfolgreichen Release-Abschluss prüfen. Lokale Builds bleiben eine ausdrückliche Alternative.

# Installer image selection

[English](#english) | [Deutsch](#deutsch)

## English

This describes the shared 1.0.1 installer. Its fixed image reference is `1.0.1`; it becomes usable only after successful publication. Local builds use the supplied source.

In **step 5**, choose:

1. **Docker Hub (default):** download the prebuilt release image.
2. **GHCR:** download the same release from GitHub's registry instead.
3. **Local build:** build the downloaded source files. Choose this to test changes on `main`.

Then choose HTTP or HTTPS as before. Step 6 uses the saved selection, shows the image reference and checks the configured endpoint. A cached image is reused; a missing image is pulled. There is no automatic switch to `latest`, another registry or a source build when a download fails. Check connectivity or registry limits; a new installation can select the alternative registry.

For scripted preparation, as root on the Linux server:

```sh
# Default: release image from Docker Hub, direct HTTPS
python3 scripts/prepare-install.py --destination /opt/hue2lox-new \
  --host 192.0.2.50 --port 18443

# Alternative: GHCR, HTTP backend behind your HTTPS proxy
python3 scripts/prepare-install.py --destination /opt/hue2lox-proxy \
  --host 192.0.2.50 --port 18444 --registry ghcr \
  --scheme http --public-url https://hue.example.org

# Development: explicitly build this checkout
python3 scripts/prepare-install.py --destination /opt/hue2lox-dev \
  --host 192.0.2.50 --port 18445 --source build
```

Choose **one** example and replace the IP, directory and port. Start that directory with `python3 scripts/start-install.py --destination /opt/hue2lox-new` (adjust the path).

The choice is recorded in `.env` and the generated `compose.yaml`. Source files are retained, but image mode does not build or run those local files. Linux host networking, HTTP/HTTPS setup, Hue CA validation, credentials, control settings and restart behavior are preserved. This changes installation packaging, not the default lamp-control policy. Existing directories are never overwritten. Old prepared installations without the new source setting retain their local-build behavior; this is not an upgrade/migration command.

## Deutsch

Dies beschreibt den gemeinsamen 1.0.1-Installer. Seine feste Image-Referenz ist `1.0.1`; sie wird erst nach erfolgreicher Veröffentlichung nutzbar. Lokale Builds verwenden den bereitgestellten Quellstand.

In **Schritt 5** auswählen:

1. **Docker Hub (Standard):** fertiges Release-Image herunterladen.
2. **GHCR:** dasselbe Release aus der GitHub-Registry herunterladen.
3. **Lokal bauen:** die heruntergeladenen Quelldateien bauen. Diese Option für neue Änderungen aus `main` verwenden.

Danach wie bisher HTTP oder HTTPS auswählen. Schritt 6 verwendet die gespeicherte Auswahl, zeigt die Image-Adresse und prüft den konfigurierten Zugang. Ein vorhandenes Image wird wiederverwendet; ein fehlendes wird heruntergeladen. Bei einem Downloadfehler gibt es keinen automatischen Wechsel zu `latest`, einer anderen Registry oder einem lokalen Build. Verbindung bzw. Registry-Limits prüfen; für eine neue Installation kann die alternative Quelle gewählt werden.

Für die Vorbereitung per Befehl als Root auf dem Linux-Server:

```sh
# Standard: Release-Image von Docker Hub, direktes HTTPS
python3 scripts/prepare-install.py --destination /opt/hue2lox-neu \
  --host 192.0.2.50 --port 18443

# Alternative: GHCR, HTTP-Backend hinter deinem HTTPS-Proxy
python3 scripts/prepare-install.py --destination /opt/hue2lox-proxy \
  --host 192.0.2.50 --port 18444 --registry ghcr \
  --scheme http --public-url https://hue.example.org

# Entwicklung: ausdrücklich diesen Quellstand bauen
python3 scripts/prepare-install.py --destination /opt/hue2lox-dev \
  --host 192.0.2.50 --port 18445 --source build
```

**Ein** Beispiel wählen, IP, Verzeichnis und Port anpassen. Anschließend das gewählte Verzeichnis mit `python3 scripts/start-install.py --destination /opt/hue2lox-neu` starten (Pfad anpassen).

Die Auswahl wird in `.env` und der erzeugten `compose.yaml` gespeichert. Quelldateien bleiben vorhanden, werden im Image-Modus aber weder gebaut noch ausgeführt. Linux-Hostnetzwerk, HTTP/HTTPS-Einrichtung, Hue-CA-Prüfung, Zugangsdaten, Steuerungseinstellungen und Neustartverhalten bleiben erhalten. Die Änderung betrifft den Installationsweg, nicht die bisherige Voreinstellung zur Lampensteuerung. Vorhandene Verzeichnisse werden niemals überschrieben. Alte vorbereitete Installationen ohne die neue Quellenauswahl behalten ihren lokalen Build; dies ist kein Update-/Migrationsbefehl.

## Update / Aktualisierung

For existing installer deployments, use the complete [update and rollback procedure](UPDATE-DOCKER.md). Für vorhandene Installer-Installationen gilt der vollständige [Update- und Rollback-Ablauf](UPDATE-DOCKER.de.md).
