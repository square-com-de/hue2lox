> **Historischer Stand / Historical record:** Aussagen, Befehle und offene Punkte unten gelten ausschließlich für den genannten damaligen Stand, nicht als aktuelle Installationsanleitung oder 1.0.3-Abnahme. / Statements, commands and pending checks below apply only to the recorded revision. [Aktuelle Dokumentation / current documentation](INDEX.md) · [1.0.3-Vorbereitung / preparation](PREPARATION-1.0.3.md).

# Hue2Lox 1.0.0-rc.6 — Release Candidate

**Release Candidate, not Stable 1.0.** Publication is complete only when the release workflow and anonymous download/image verification succeed. / Veröffentlichung erst nach erfolgreichem Workflow und öffentlicher Download-/Imageprüfung abgeschlossen.

## Deutsch

- Gemeinsamer Installer mit Docker-/nativer Auswahl und deutschen/englischen Meldungen.
- Docker: feste RC6-Version von Docker Hub/GHCR oder lokaler Build; HTTP/HTTPS und Reverse Proxy weiterhin möglich.
- Nativ: experimenteller systemd-Betrieb ohne Docker auf den deklarierten amd64-Zielen; eigenes verifiziertes natives Release-Archiv zusätzlich zum Quell-ZIP.
- Updates mit Sicherung, exaktes Rollback und Deinstallation/Wiederinstallation mit Datenerhalt; umask-077-Korrektur.
- Lokale Discovery-Kopierhilfen und sechs Iconoir-Sidebar-Symbole mit vollständigen Lizenzhinweisen.
- Hue-Szenen bleiben reine Aktivierungsbefehle ohne AUS-Funktion oder Zustandsrückmeldung an den Loxone-Lichtbaustein; DE/EN-Handbuch erklärt die separate Ausschaltung und Konfiguration als digitalen Impulsausgang.
- Technische Paket-/Docker-/systemd-Prüfungen und Sicherheits-/Quellenprüfung protokolliert. Die Nutzerabnahme bestätigt TV-Strip-Steuerung aus Loxone über Lumitech einschließlich Farben, Warm-/Kaltweiß, Dimmen und Aus sowie Szenenaktivierung; keine allgemeine Freigabe aller Geräte.

Erstlogin bleibt `admin/admin`, danach Passwort ändern. RC1/RC5 unverändert. Kein `latest` für RCs. Native ARM-/Raspberry-Pi-OS-Unterstützung, Statusrückmeldung, Schalter/BWM und LoxBerry-Plugin sind nicht Bestandteil dieses Kandidaten. Angepasste Compose-/Prototyp-Installationen benötigen eine eigene Migrationsprüfung.

## English

- Shared installer with Docker/native selection and German/English helper output.
- Docker: fixed RC6 Docker Hub/GHCR version or local build; HTTP/HTTPS and reverse proxy retained.
- Native: experimental systemd deployment on declared amd64 targets; verified native archive supplied alongside the source ZIP.
- Backed-up updates, exact rollback and retained-data uninstall/reinstall; umask-077 permission fix.
- Local discovery copy helpers and six Iconoir sidebar icons with complete notices.
- Hue scenes remain activation-only commands, without scene OFF or Lighting Controller state feedback; the DE/EN manuals explain separate switch-off and digital pulse-output configuration.
- Technical package/Docker/systemd and security/source checks recorded. Human acceptance confirms a TV strip from Loxone via Lumitech (colors, warm/cold white, dimming and off) plus scene activation; no blanket device qualification.

Initial login remains admin/admin; change it afterwards. RC1/RC5 stay unchanged. RCs do not set latest. Native ARM/Raspberry Pi OS, status feedback, switch/motion inputs and a LoxBerry plugin are outside this candidate. Custom Compose/prototype deployments need separate migration review.

## Publication handoff / Übergabe

The exact source commit, ZIP/native checksums, container candidates, license/source bundle and CI run IDs belong to one final release. Obtain the local preparation manifest; no hashes or download availability are invented here. Before publishing, confirm the candidate is merged into main, the tag/version pin matches, all release jobs pass and both registries/downloads are anonymously verified. Publication requires separate user approval. / Exakten Quellcommit, Prüfsummen und Prüfläufe aus der lokalen Übergabe verwenden; keine Veröffentlichung ohne separate Nutzerfreigabe.

## Control defaults and existing installations / Steuerung und Bestandsinstallationen

Fresh Docker/native installations now set the three control flags to `1`; existing values remain unchanged on update/reinstall. Token and per-light capability enforcement are retained. Actual RC5 installer deployments stored `0`, whereas direct RC5 images without overrides defaulted to `1`. RC5 did not include native packages. The explicit offline correction tool changes only the three flags after operator opt-in, with a private settings backup. Docker requires container recreation, native requires a service restart. Full update/rollback and independent acceptance: [English procedure](RECOVERY-CONTROL.md), [deutscher Ablauf](RECOVERY-CONTROL.de.md). The final integrated candidate must pass renewed tests and independent practical acceptance; previous green runs do not approve this integration.

Neue Docker-/native Installationen setzen die drei Steuerungsflags auf `1`; Updates/Wiederinstallationen behalten bestehende Werte. Token- und Lampenfähigkeitsprüfung bleiben aktiv. Der reale RC5-Installer speicherte `0`, direkte RC5-Images ohne Overrides verwendeten `1`. RC5 enthielt kein natives Paket. Eine bewusste Freigabe erfolgt offline mit privater Sicherung, bei Docker anschließend durch Neuerstellen des Containers. Die endgültige Integration benötigt erneute Tests und unabhängige praktische Abnahme; frühere grüne Läufe ersetzen diese nicht.
