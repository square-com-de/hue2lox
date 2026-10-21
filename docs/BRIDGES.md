# Bridge-Verwaltung, Kopplung und automatische Lampenerkennung

Stand: 18.10.2026.

## Ablauf im Webinterface

1. Als Administrator anmelden und „Bridges“ öffnen.
2. Neue Bridge: Namen und lokale IPv4-Adresse eingeben, „Bridge prüfen und hinzufügen“ wählen. Vorbereitete Einträge für OG und UG können direkt gekoppelt werden.
3. „Koppeln“ wählen. An genau dieser Bridge die physische Link-Taste drücken und anschließend „Link-Taste gedrückt · verbinden“ wählen. Wenn die Taste noch nicht erkannt wurde, erscheint eine entsprechende Meldung; danach erneut versuchen.
4. Nach erfolgreicher Kopplung werden alle vorhandenen Hue-v2-Lichtressourcen dieser Bridge automatisch eingelesen. Räume, Namen, Modellkennung, Produkttyp und Fähigkeiten erscheinen in der Lampenliste und der Loxone-Exportliste.
5. Bereits eingerichtete EG-Bridge: „Lampen einlesen“ verwenden; ihr vorhandener Key wird weiterverwendet. Neue Lampen später mit derselben Schaltfläche nachladen.

„Neu koppeln“ ermöglicht die Erneuerung einer ungültig gewordenen Hue-Berechtigung. Dazu ist wieder die physische Taste nötig. Vorhandene Schlüsseldateien unter `/run/secrets` werden nicht überschrieben, und andere Hue-Anwendungen werden nicht widerrufen. Beim regulären erneuten Einlesen wird kein neuer Hue-Key erzeugt.

Die Verwaltung findet bereits in der Hue Bridge vorhandene Lampen. Sie startet keine Zigbee-Suche, setzt keine Lampen zurück und sendet keine Lichtbefehle. Räume werden nur übernommen, nicht verändert. Bridge-Adressen werden manuell eingegeben; es findet kein automatischer Scan des gesamten LANs und keine Cloud-Abfrage statt.

## Was wird übernommen?

Eine lesende Abfrage von `/clip/v2/resource` liefert Geräte, Räume und Lichtressourcen. Gerätedaten werden über den Owner der Lichtressource zugeordnet; Räume über ihre Device-Children. Dimmen, RGB und Farbtemperatur werden nur übernommen, wenn die entsprechende Fähigkeit in der API vorhanden ist. Ein reiner Schaltaktor braucht keinen erfundenen Helligkeitswert.

Vorhandene IDs, `/hue-go/state` und explizite Icon-Zuordnungen bleiben erhalten. Neue Lampen verwenden `/api/lights/<bridge-id>/<light-id>/state`. Nicht mehr gefundene Ressourcen werden als `present:false` markiert, nicht gelöscht; sie sind für neue Exporte und generische Steuerpfade gesperrt. Ein erneutes Auftauchen derselben ID hebt diese Markierung auf. Raum-/Namensänderungen aus Hue werden bei der Inventur übernommen.

Die Statusübersicht liest danach je aktiver Bridge eine Sammlung von Lichtzuständen, statt jede Lampe separat anzufragen. Weiterhin 5-Sekunden-Cache und Aktualisierung im Browser alle 10 Sekunden. Diese REST-Abfrage ist keine Streaming-Schnittstelle und kein Nachweis, dass eine ausgeschaltete/unerreichbare physische Lampe den zuletzt bekannten Zustand aktuell erreicht hat.

## Speicherung und Migration

Im Container bleibt das Root-Dateisystem read-only. Hinzu kommt genau ein schreibbarer Bind-Mount:

```text
Host: data/                         Container: /data/
  admin_auth.json                   Admin-Passwort-Hash für Web-Passwortwechsel
  registry.json                     Aktive Bridge-/Lampenregistry
  registry.previous.json            Metadaten vor der letzten Änderung
  bridge-keys/<bridge-id>.key        Neu erzeugte Hue-Anwendungsschlüssel
```

Der Root-Installer legt den Host-Ordner mit UID/GID 10001 und Modus 700 an. Beim ersten Update wird die bisherige lokale `registry.json` einmal übernommen. Bei späteren Updates wird die Runtime-Registry nicht überschrieben. Neue Schlüssel haben Modus 600 und werden dem Browser nie ausgegeben. `data/` ist sowohl in `.gitignore` als auch `.dockerignore` ausgeschlossen. Die bisherigen Read-only-Mounts für EG-Hue-Key, Steuerungstoken und HTTPS-Zertifikat bleiben bestehen. Der Admin-Hash wird für den Passwortwechsel in den geschützten `/data`-Mount migriert.

`HUE_STATE_DIR=/data` und `HUE_REGISTRY_FILE=/data/registry.json` werden durch Compose gesetzt. Bridge-Schlüssel, Registry und letztes Metadatenbackup werden atomar ersetzt; konkurrierende Änderungen an verschiedenen Bridges werden zusammengeführt. Je Bridge läuft nur ein Kopplungs-/Inventurvorgang gleichzeitig. Misslingt die Inventur nach erfolgreicher Kopplung, bleibt die Key-Referenz gespeichert; ein erneuter Versuch erstellt dadurch keinen zusätzlichen Key.

Ein Backup der vollständigen Bridge-Verwaltung benötigt `data/` einschließlich seiner Schlüssel, zusätzlich zu den vorhandenen Zertifikats-/Secret-Dateien. Dieses Backup privat und geschützt aufbewahren, niemals ins Git-Repository laden. Das Installationsbackup enthält von `/data` nur eine Kopie der Registry-Metadaten, keine neuen Bridge-Key-Inhalte.

## Zugriff und TLS

Alle Verwaltungsrouten verlangen die bestehende Admin-Sitzung. Änderungen zusätzlich CSRF, Host-/Origin-/Fetch-Site-Prüfung. Die neuen Routen sind:

- `GET /api/admin/bridges`
- `POST /api/admin/bridges/add` mit `name`, `host`
- `POST /api/admin/bridges/pair` mit `id`, optional `replace:true` für ausdrückliche Wiederkopplung
- `POST /api/admin/bridges/scan` mit `id`

Neue Ziele müssen private IPv4-Adressen aus 10/8, 172.16/12 oder 192.168/16 sein. Kein frei wählbarer Port, URL, DNS-Name, Loopback oder Link-Local-Ziel. HTTPS läuft fest auf Port 443. Höchstens 32 Bridges, 1000 Lampen je Inventur, Antwortgröße bis 4 MiB. Login und TLS-Prüfung werden nicht umgangen.

Bei einer neuen IP ist die Bridge-ID zunächst unbekannt: Der erste TLS-Verbindungsaufbau prüft bereits die Hue-CA-Kette, Signatur und Gültigkeit (`CERT_REQUIRED`), lernt danach die signierte Bridge-ID aus dem Zertifikat. Erst dann erfolgt die HTTPS-Konfigurationsabfrage mit zusätzlicher Namensprüfung gegen genau diese ID. Die gemeldete `bridgeid` muss übereinstimmen. Alle weiteren Hue-Anfragen prüfen ebenfalls Kette, Laufzeit und Identität. Der SHA256-Fingerabdruck ist im Interface einsehbar. Es gibt keinen HTTP- oder `CERT_NONE`-Fallback.

Der Kopplungsaufruf ist ausschließlich `POST /api` mit einem Hue2Lox-App-Namen. Er erzeugt einen Anwendungsschlüssel nach Link-Tastendruck; `clientkey` für Entertainment wird nicht angefordert. Keine Hue-Light-PUTs oder DELETEs durch Hinzufügen/Kopplung/Inventur. Die existierenden globalen Schreib-/Farb-/Weißfreigaben bleiben für spätere Loxone-Steuerbefehle maßgeblich.

## Tests und Grenzen

- Automatisierte Tests mit simulierten Bridges: IP-Grenzen, TLS-Identitätslernen, Zertifikatsfehler, Link-Taste, Schlüsselrechte/Redaktion, Wiederverwendung/Erneuerung, Inventur, Raum-/Modellzuordnung, fehlende Ressourcen, unveränderte Hue-Go-Aliase, Zugriffsschutz und gebündelte Statusabfragen.
- Browser mit ausschließlich Testdaten: Bridge hinzufügen, Kopplungsschritte, automatische Inventur und Übernahme in die Loxone-Auswahlliste geprüft.
- Echte lesende Prüfung auf LoxBerry: EG-Bridge `192.0.2.253`, ID `001788FFFE000001`, BSB002, Firmware `1978418030`, Zertifikatsprüfung erfolgreich. Zertifikat-SHA256: `2A:41:4C:25:34:78:62:ED:00:0E:66:DF:74:99:B9:24:7E:8D:CB:AA:AA:C0:30:75:BC:10:11:75:4E:E8:B2:F0`.
- Keine reale neue Kopplung oder Inventur aller produktiven Lampen durch die Entwicklung. Root-Installation, Link-Tastendruck und anschließende Live-Prüfung bleiben erforderlich.
- Hue-v2/HTTPS vorausgesetzt. Hue Bridge v1 und andere Zertifikatsprofile sind nicht als unterstützt/testbestätigt ausgewiesen. Lokale mDNS-Suche ist implementiert; siehe [DISCOVERY.md](DISCOVERY.md). IPv6, Cloud-Discovery, Widerrufen von Bridge-Keys auf der Bridge und SSE sind nicht enthalten.

Herstellerreferenz für den Link-Tasten-Ablauf:
https://developers.meethue.com/develop/get-started-2/


## Lampen ausblenden und entfernen

Unter **Lampen** hat jede Karte die Aktionen **Ignorieren** und **Entfernen**.
Ignorieren blendet die Lampe aus Übersicht, Standardliste und Loxone-Export aus.
Mit **Ignorierte anzeigen** und **Wieder einblenden** lässt sich das rückgängig machen.
Die Auswahl bleibt nach Container-Neustart und erneutem Einlesen erhalten.

Entfernen nimmt die Lampe nur aus Hue2Lox; eine Bestätigung erklärt, dass sie beim
nächsten Einlesen wieder erscheinen kann. Intern bleibt ein lokaler Merkeintrag
erhalten, damit bestehende Pfad-Aliase beim Wiederfinden erhalten bleiben.
Für dauerhaftes Ausblenden ist Ignorieren vorgesehen.

Beide Aktionen ändern ausschließlich `/data/registry.json`, benötigen Anmeldung
und CSRF-Schutz und senden keine Änderung an die Hue Bridge. Steuerungswege
(auch der alte Hue-Go-Pfad) sind für ignorierte/entfernte Lampen gesperrt. Bereits
importierte Loxone-Konfigurationen werden nicht automatisch geändert.
