# Deployment acceptance / Deployment-Abnahme — 23.10.2026

[Deutsch](#deutsch) · [English](#english) · [Hardware plan / Hardwareplan](ACCEPTANCE.md)

## Deutsch

**Deployment-Abnahme bestanden; keine Hardware- oder Stable-Freigabe.** Geprüfter PR-Head: `1b3e85af786c6527edc720b05da6f513957096ca`. PR #18 wurde am 23.10.2026 als `9a1e3ebcb4fa61c391588a2b29b7e998ee1c3278` nach main gemergt; beide Commits haben denselben Dateibaum `aad22796a15f3d59c808373a6fcd770d6ab1cec8`.

Verbindlicher öffentlicher Nachweis: [Abnahmebericht in PR #18](https://github.com/square-com-de/hue2lox/pull/18#issuecomment-6360849616). 30 dokumentierte Prüfgruppen; technische Einzelprotokolle, private Sicherungen und Browserbelege werden nicht mit Zugangsdaten veröffentlicht.

| Bereich | Beobachtetes Ergebnis |
| --- | --- |
| Reale VMs | Ubuntu 26.04 und DietPi 13, amd64, jeweils Docker und nativ |
| Nativer Lebenszyklus | Installation, echter Codewechsel von `66187c4f527269fa1fcb542072549240cfbf2ce0` zum geprüften Stand und exaktes Code-/Daten-Rollback; vorhandene persönliche Passwort-, Wiederinstallations- und Neustartnachweise einschließlich umask 077 erhalten |
| Docker-Lebenszyklus | Echter Code-/Imagewechsel, vollständiges kaltes Backup und manuelles Rollback mit gesichertem Image und expliziter Image-ID; kein Neubau/Download beim Rollback |
| Private Daten | Registry, Anmeldung, Token, Einstellungen, Zertifikate sowie Eigentümer/Dateirechte erhalten bzw. auf Sicherungsstand wiederhergestellt |
| Passwort und Neustart | Nutzer bestätigt Passwort A statt Erstpasswort, Container-/VM-Neustart, A nach Update, Wechsel A→B, nach Rollback B abgelehnt und A akzeptiert |
| Zusätzliche isolierte VM | Lokaler Build und beide Registry-Auswahlwege mit unterschiedlichen lokalen Fixture-Tags; nicht startfähiger Kandidat und erfolgreiche manuelle Wiederherstellung |
| DE/EN und Oberfläche | Tatsächliche Helferausgaben, Navigation, sechs Icons, Lizenzlinks und sechs Kopierhilfen geprüft; Discovery-Befehle nicht ausgeführt |
| Ergänzende Prüfungen | 291 Tests und [Quality CI](https://github.com/square-com-de/hue2lox/actions/runs/39862213204), [Container-Vorbereitung](https://github.com/square-com-de/hue2lox/actions/runs/39862213176); unabhängig 64 gezielte Tests unter Python 3.12.14 ohne konkrete Findings im geprüften Umfang |

**Grenzen:** Keine Hue-/Loxone-Hardwareabnahme, keine echten Windows-/Linux-LAN-Discoverytests, keine neuen veröffentlichten Registry-Downloads durch lokale Fixtures belegt. Reale native VM-Abnahme nur amd64 Ubuntu 26.04/DietPi 13; weitere deklarierte Systeme haben gesonderte CI-/Fixture-Abdeckung. Keine allgemeine Freigabe beliebiger Schema- oder angepasster Compose-Migrationen. Frühere Debian-Nachweise bleiben auf ihre [historischen Stände](NATIVE-VM-ACCEPTANCE.md) begrenzt. Finale RC6-Pakete und ihre öffentliche Auslieferung sind noch nicht abgenommen.

## English

**Deployment acceptance passed; no hardware or stable approval.** Tested PR head: `1b3e85af786c6527edc720b05da6f513957096ca`. PR #18 merged into main on 23 October 2026 as `9a1e3ebcb4fa61c391588a2b29b7e998ee1c3278`; both commits have the same tree `aad22796a15f3d59c808373a6fcd770d6ab1cec8`.

The authoritative public evidence is the [PR #18 acceptance report](https://github.com/square-com-de/hue2lox/pull/18#issuecomment-6360849616), covering 30 documented test groups. Private logs, backups and browser evidence are retained without publishing credentials.

| Area | Observed result |
| --- | --- |
| Real VMs | Ubuntu 26.04 and DietPi 13, amd64, each with Docker and native deployment |
| Native lifecycle | Installation, actual code update from `66187c4f527269fa1fcb542072549240cfbf2ce0` to the tested head, exact code/data rollback; earlier personal password, retained-data reinstall and reboot evidence including umask 077 retained |
| Docker lifecycle | Actual code/image change, full cold backup and manual rollback using the saved image and explicit image ID, without rebuilding or pulling during rollback |
| Private state | Registry, authentication, token, settings, certificates and ownership/modes retained or restored to the backup state |
| Password and reboot | User confirmed password A replacing the initial password, container/VM reboot, A retained after update, A→B, then B rejected and A accepted after rollback |
| Additional isolated VM | Local build and both registry-selection paths with distinct local fixture tags; deliberately broken candidate and successful manual recovery |
| DE/EN and UI | Actual helper output, navigation, six icons, license links and six copy controls checked; discovery commands were not executed |
| Supplementary checks | 291 tests, successful [Quality CI](https://github.com/square-com-de/hue2lox/actions/runs/39862213204) and [container preparation](https://github.com/square-com-de/hue2lox/actions/runs/39862213176); independent review with 64 targeted Python 3.12.14 tests and no actionable findings in scope |

**Limits:** No Hue/Loxone hardware acceptance, real Windows/Linux LAN-discovery testing or proof of new public registry downloads from local fixtures. Real native VM coverage is limited to amd64 Ubuntu 26.04/DietPi 13; other declared targets have separate CI/fixture coverage. No arbitrary schema/custom-Compose migration approval. Earlier Debian results retain their [historical scope](NATIVE-VM-ACCEPTANCE.md). Final RC6 packages and public delivery have not yet been accepted.
