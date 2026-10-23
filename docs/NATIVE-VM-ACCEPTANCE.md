> **Historischer Bericht / Historical report:** Die folgenden Ergebnisse und offenen Punkte gelten für die Stände vom 21.10.2026. Für den integrierten Stand aus PR #18 gilt die spätere [Deployment-Abnahme vom 23.10.2026](https://github.com/square-com-de/hue2lox/blob/main/docs/DEPLOYMENT-ACCEPTANCE.md). / Results and pending evidence below apply to the 21 October revisions; see the later acceptance for the merged PR #18 code.

# Native VM-Abnahme / Native VM acceptance — 21.10.2026

## Prüfstand und Herkunft

Manuelle Rückmeldungen und vom Nutzer eingefügte Terminalausgaben aus einer frischen Debian-13-amd64-VM. Die Anwendung lief nativ als systemd-Dienst mit dem Benutzer `hue2lox`; Browserzugriff vom Mac über einen SSH-Tunnel auf die Loopback-Adresse. Der Agent hat die VM nicht selbst bedient. Die Python-Version wurde nicht separat übermittelt. VM-Neustarts und Browseranmeldungen sind Nutzerrückmeldungen, keine vom Agenten beobachteten Automatiktests.

- Update-/Rollback-Versuch: Commit `1652485d1323db29e41a8b3911ca7eb55a534366`, selbst gebaute Pakete `0.0.0-test.1` und `0.0.0-test.2` mit demselben Anwendungscode.
- Nach VM-Reset: Korrekturstand `6dbd8ae78b7933677f659bff87421ca2706f2137`, Paket `0.0.0-test.3`. Der angeleitete Ablauf sah Deinstallation und Wiederinstallation mit `--keep-data` unter `umask 077` vor. Der Nutzer bestätigte Deinstallation, Anmeldung mit dem geänderten Passwort und anschließenden VM-Neustart; vollständige Build-/Installationsausgaben dieses Durchgangs wurden nicht übermittelt.
- Dieser Bericht gilt für diese Stände. Die Integration mit main `e5aba92cad916c070da77f7840d24153ea31fd78` ist ein späterer Stand; ihre isolierten CI-Tests ersetzen keine erneute manuelle VM-Abnahme.

## Bestätigte Ergebnisse und Grenzen

| Prüfung | Ergebnis / Beleg |
| --- | --- |
| Erste native Installation, HTTPS mit Zertifikatsprüfung | Terminalausgabe meldet erfolgreiche Einrichtung; `active`, `enabled` und `{"status":"ok"}` bestätigt. |
| Passwortwechsel und neuer Login | Nutzer bestätigt geändertes Passwort und erfolgreiche Anmeldung. |
| Echter VM-Neustart | Erreichbarkeit und Anmeldung mit geändertem Passwort vom Nutzer bestätigt. |
| Update test.1 → test.2 auf Commit 1652485 | Terminalausgabe: HTTPS-Prüfung bestanden, installierte Version test.2, private Dateiprüfsummen vollständig `OK`, Dienst `active` und `enabled`. |
| Explizites späteres Rollback test.2 → test.1 | Terminalausgabe: HTTPS-Prüfung bestanden, installierte Version test.1, private Dateiprüfsummen vollständig `OK`, Dienst `active` und `enabled`. |
| Passwort-Rücksetzung durch Rollback | **Nicht geprüft.** Der zweite Passwortwechsel fand erst nach dem Rollback statt. Keine Aussage über diesen manuellen Abnahmepunkt. |
| Wiederinstallation des alten Stands unter umask 077 | **Fehler bestätigt:** Programmverzeichnisse 0700, systemd `200/CHDIR`, Dienststart gescheitert. Das war kein erfolgreicher Test. |
| Wiederinstallation mit Korrekturstand 6dbd8ae | Nutzer bestätigt Deinstallation und anschließende Anmeldung mit dem neuen Passwort; Standardpasswort `admin` wird abgewiesen. |
| VM-Neustart nach korrigierter Wiederinstallation | Nutzer bestätigt Erreichbarkeit und Anmeldung mit geändertem Passwort. |
| Verzeichnisrechte und vollständiger Dateivergleich nach korrigierter Wiederinstallation | **Manueller Nachweis offen.** Die angeforderten `ls -ld`- und `sha256sum -c`-Ausgaben wurden bisher nicht übermittelt. Automatische CI-Prüfungen sind davon getrennt. |

Die beiden Updatepakete test.1 und test.2 unterscheiden sich in der Paketversion, nicht im Anwendungscode. Der Versuch belegt den Deployment-Lebenszyklus und den erhaltenen/geprüften Datenstand; er belegt keine beliebige Migration zwischen unterschiedlichen Anwendungsversionen.

## Hardware und übrige offene Abnahmen

Ein früherer Versuch im selben Dialog fand echte Hue Bridges per Discovery. Daher darf der gesamte manuelle Testdialog nicht als vollständig hardwarefrei bezeichnet werden. Pairing, Bridge-TLS, Steuerung und Loxone wurden in dieser nativen Abnahme nicht als bestanden bestätigt. Die späteren Testschritte sollten ohne Discovery oder Kopplung erfolgen. Private Adressen, Passwörter, Schlüssel und Backups werden hier nicht veröffentlicht.

Vor einer weitergehenden Freigabe fehlen insbesondere:

- manueller Rechte- und vollständiger Dateivergleich nach Wiederinstallation des Korrekturstands;
- erneuter VM-Test des mit main integrierten Stands;
- Passwortwechsel **zwischen** Update und Rollback, danach Nachweis des früheren Passwortstands;
- native Zertifikatserneuerung und Wiederherstellung auf einer frischen Zielinstanz;
- separat autorisierte Hardwareabnahmen: Discovery, Pairing, Bridge-TLS, Schalten/Dimmen/Farbe/Weiß/Szenen und Loxone-HTTPS/XML.

## English summary

User-supplied terminal output confirms native installation, verified HTTPS, successful test-package update and explicit rollback on commit 1652485, matching private-file checksums, and an active/enabled service. The user also confirmed browser login/password changes and actual VM reboots. A later fresh-VM test on correction commit 6dbd8ae confirmed retained-password login after reinstall and reboot. Post-reinstall directory permissions and full file-checksum output have not yet been supplied. The manually tested packages test.1/test.2 used identical application code; no real application-version migration was established. Password restoration by rollback was not manually tested because the password was changed afterwards. Earlier discovery reached real bridges, so the full manual session cannot be described as hardware-free. No native control or Loxone hardware acceptance is claimed. The subsequent integration with newer main requires its own manual VM acceptance.
