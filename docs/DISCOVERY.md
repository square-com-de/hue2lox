# Lokale Gerätesuche und Miniserver-Link

## Einrichtung

Unter **Loxone → Dein Miniserver → Miniserver im Netzwerk suchen** erscheinen
lokal gemeldete Geräte. **Adresse übernehmen** füllt Name und Webadresse aus.
Adresse und HTTP/HTTPS-Port prüfen, dann **Link speichern** wählen. Die Übersicht
zeigt anschließend **Loxone öffnen**; der Link öffnet das Webinterface in einem
neuen Tab. Die Anmeldung erfolgt direkt bei Loxone. Hue2Lox speichert keine
Miniserver-Zugangsdaten und ändert keine Einstellungen auf dem Miniserver.

Alternativ Name und Webadresse manuell eingeben: lokale IPv4 oder `.local`-Name,
HTTP oder HTTPS, optional ein Port. Zusätzliche Pfade, Parameter und eingebettete
Zugangsdaten sind nicht vorgesehen. Ein leeres Adressfeld beim Speichern entfernt
den Link. Das Speichern selbst ruft die Zieladresse nicht auf und bestätigt keine
Erreichbarkeit oder Zertifikatsprüfung. Der Browser behandelt Weiterleitungen
und Zertifikate beim späteren Öffnen wie bei einem normalen Webaufruf.

Unter **Bridges → Hue Bridges suchen** lassen sich gefundene IP-Adressen mit
**Zum Hinzufügen übernehmen** in das vorhandene Formular eintragen. Danach
**Bridge prüfen und hinzufügen** wählen, ggf. Name anpassen und über die physische
Link-Taste koppeln. Die bestehende Prüfung von Hue-Zertifikatskette und Bridge-ID
bleibt Teil dieses getrennten Schritts. Die Suche koppelt keine Bridge automatisch.

## Übersicht

Die früheren zwei beliebig ausgewählten Lampenkarten entfallen. Sichtbar sind
aktive Bridges, eingerichtete Lampen, eingeschaltete Lampen, Hue-Szenen und der
Miniserver-Link sowie die Bridge-Verbindungsübersicht. Die Szenenanzahl umfasst
nur vorhandene, nicht ignorierte oder lokal entfernte Szenen aktivierter Bridges.

## Verfahren und Grenzen

- Miniserver: UDP-Suchpaket auf 7070 mit Empfang auf 7071; parallel SSDP-Suche
  auf 239.255.255.250:1900 mit Antworten an einen temporären UDP-Port.
- Hue: mDNS-Dienst `_hue._tcp.local` auf 224.0.0.251:5353 mit angeforderter
  Unicast-Antwort an einen temporären UDP-Port, Auswertung von PTR/SRV/A.
- Je Suchlauf ca. 2,5 Sekunden, begrenzte Paket- und Ergebnisanzahl, keine
  Subnetz-Portscans, keine Cloud-Abfragen, keine Zugangsdaten und keine Schreibbefehle.
- Ergebnisse sind lokale Suchmeldungen, keine kryptografisch bestätigte Identität.
  Miniserver-Antworten werden auf lokale IPv4, passende Absenderadresse und
  gültige Ports geprüft. Für Hue folgt die Geräteprüfung erst beim Hinzufügen.
- Es läuft nur eine Suche gleichzeitig. Anmeldung und CSRF-Schutz sind erforderlich.
- Gespeichert wird der Link in `/data/registry.json`; Netzwerkresultate bleiben
  vorübergehend im Browser. Es gibt keinen zusätzlichen Dienst oder Container.

**Neue Linux-Installationen:** `docker/compose.install.yaml` verwendet Host-Netzwerk, sodass die Suche direkt im LAN der VM erfolgt. Web-IP, Port und HTTPS-Healthcheck folgen den Installationswerten. Die tatsächliche Suche im LAN muss weiterhin getestet werden; Details und Umstellung bestehender Testinstallationen stehen in [INSTALL.md](../INSTALL.md).

**Ältere Installationen und Netzwerkgrenzen:** Broadcast/Multicast kann im Docker-Bridge-Netz,
bei VLANs oder Firewalls fehlen. Ein erfolgreicher Test auf Mac oder LoxBerry-Host
beweist nicht, dass die Suche auch im Container Antworten erhält. Deshalb zeigt
die Oberfläche bei ausbleibenden Ergebnissen die manuelle Alternative an. Dieses
Update ändert weder Docker-Netzwerkmodus noch Firewall oder Portfreigaben.
Der Betrieb der Suche im tatsächlichen Container muss nach Installation geprüft
werden; `loxberry` besitzt keine Docker-Berechtigung.

Optional als root nach Installation prüfen (nur Suchpakete):

```sh
cd /opt/loxberry/hue2lox-prototype
docker compose exec -T hue2lox python -c 'import json,discovery; print(json.dumps({k:discovery.search(k) for k in ("miniserver","hue")}))'
```

## Entwicklung und Prüfung am 18.10.2026

Reale Suche vom Mac und anschließend vom LoxBerry-Host erfolgreich: ein
Miniserver unter `192.0.2.10` (gemeldeter HTTP-Port 80) und Hue Bridges unter
`192.0.2.253`, `192.0.2.136` und `192.0.2.137`. Dies sind die Geräte dieser
Testinstallation, keine Standardadressen für neue Installationen. Es wurde kein
Weblogin getestet und keine erfolgreiche TLS-Prüfung des Miniservers behauptet.

Browserprüfung mit ausschließlich Testdaten: Suchen, Ergebnisübernahme für
Miniserver und Hue, Link speichern und Dashboard-Anzeige erfolgreich.
Automatische Tests decken Parser, DNS-Kompression und fehlerhafte Pakete,
Suchsperre, Fehlerfälle, URL-Validierung, Speicherung, Dashboard-Zählung und
Anmeldung/CSRF/Origin ab. Keine Kopplung oder Lampensteuerung durch diese Tests.

Quellen für die Suchverfahren:

- Loxone, Ports und Domains: https://www.loxone.com/enen/wp-content/uploads/sites/3/2016/10/Loxone_PortsDomains.pdf
- Protokollbeobachtungen des Autors: https://github.com/sarnau/Inside-The-Loxone-Miniserver/blob/master/LoxoneMiniserverNetworking.md
- Philips Hue, lokale mDNS-Suche: https://developers.meethue.com/develop/get-started-2/
