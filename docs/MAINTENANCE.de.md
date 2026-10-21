# Wartung: Zertifikat, IP-Wechsel und Wiederherstellung

[English](MAINTENANCE.md)

Diese Anleitung gilt für die mit `prepare-install.py` vorbereitete Installation ab dem Stand, der `scripts/renew-certificate.py` enthält. RC1 enthält dieses neue Werkzeug noch nicht. Für alte Prototyp-Installationen ist sie nicht geeignet. Alle Befehle laufen auf dem Linux-Zielserver. Pfade und Beispiel-IP anpassen; keine echte Installation für einen Test verwenden.

**Betriebsabnahme noch offen:** Der Ablauf ist für echte Browser-/Miniserververbindungen noch unbestätigt. Automatische Tests sind keine Betriebsfreigabe.

## Vorbereiten und vollständig sichern

`INSTANCE` ist der vom Installer gewählte Zielordner, `SOURCE` der entpackte neue Quellstand. Als root anmelden (`sudo -i` oder `su -`). Nur diese Compose-Installation stoppen; keine globalen Docker-Neustarts. Auch externe Neustart-Automationen für die Wartung pausieren.

```sh
sudo -i
INSTANCE=/opt/hue2lox
SOURCE=/home/lance/hue2lox-main
cd "$INSTANCE"
docker compose down
BACKUP="/root/hue2lox-backup-$(date +%Y%m%d-%H%M%S)"
install -d -m 700 "$BACKUP"
cp -a "$INSTANCE" "$BACKUP/instance"
printf 'Backup: %s\n' "$BACKUP"
```

Die Sicherung enthält private Bridge-Zugänge, Steuerungstoken, Passwortdaten und Zertifikatsschlüssel. Privat aufbewahren, bei Übertragung verschlüsseln; nicht an GitHub/Issues anhängen. `cp -a` erhält Rechte und Eigentümer. Zusätzlich den verwendeten Quellstand bzw. das Image und seine Version sichern, damit ein späterer Neubau nicht unbemerkt andere Abhängigkeiten verwendet. Der vollständige Zielordner enthält `.env`, Compose, `data`, `secrets`, `certs`, `health-test.crt` und Build-Dateien. Eine Sicherung nur von `registry.json` reicht nicht.

## Zertifikat erneuern – gleiche IP

Nach dem Backup bei gestopptem Dienst:

```sh
python3 "$SOURCE/scripts/renew-certificate.py" --destination "$INSTANCE"
docker compose up -d --force-recreate --wait --wait-timeout 120
```

Das Werkzeug erzeugt ein neues selbstsigniertes Zertifikat für 365 Tage. Es ersetzt Zertifikat, Schlüssel und `health-test.crt` gemeinsam mit der passenden `.env`; der private Schlüssel bleibt Modus 600 und im Container UID 10001 zugeordnet. Registry, Token, Passwortdaten, Port und Installationsname bleiben erhalten. Zusätzlich entsteht ein privater `.hue2lox-tls-backup-*`-Ordner neben der Installation. Bei einem Schreibfehler wird zurückgerollt; nach einem Stromausfall die vollständige Sicherung wiederherstellen.

## IP-Adresse ändern

Zuerst eine feste Adresse/DHCP-Reservierung auf Server und Router einrichten. Das Werkzeug konfiguriert weder Netzwerk noch Firewall. Die neue Adresse muss dem Server bereits gehören. Nach Stop und Backup **anstelle** der normalen Erneuerung ausführen:

```sh
python3 "$SOURCE/scripts/renew-certificate.py" --destination "$INSTANCE" --host 192.168.1.50
docker compose up -d --force-recreate --wait --wait-timeout 120
```

Dabei werden `HUE2LOX_BIND_IP`, `HUE_PUBLIC_URL`, Zertifikat-SAN und Healthcheck-Vertrauen konsistent geändert. Port und Projektname bleiben erhalten. Compose muss den Container neu erstellen; ein einfaches `restart` übernimmt eine geänderte Umgebung nicht.

## Nachkontrolle und Client-Vertrauen

IP/Port im folgenden Beispiel durch die Werte aus `.env` ersetzen:

```sh
docker compose ps
openssl x509 -in certs/server.crt -noout -dates -ext subjectAltName
curl --fail --cacert health-test.crt https://192.168.1.50:18443/health
```

Danach im Browser unter der neuen URL anmelden: Bridge-Zuordnung, Lampen/Szenen und Einstellungen prüfen. Das neue selbstsignierte Zertifikat muss in verwendeten Clients erneut bewusst als vertrauenswürdig eingerichtet werden. Nicht mit `curl -k` die Zertifikatsprüfung umgehen. Bei IP-Wechsel auch Loxone-Ausgangsadressen, importierte Befehle und gespeicherte Browser-Links aktualisieren; eine reale Loxone-Schaltung gesondert prüfen. Die mitgelieferte **Hue-CA** betrifft die Verbindung zur Bridge und wird durch diese Wartung weder ersetzt noch entfernt.

## Vollständige Wiederherstellung

`BACKUP` auf den zuvor ausgegebenen Sicherungsordner setzen. Das Beispiel stellt denselben Zielpfad wieder her und behält den misslungenen Stand zur Untersuchung. Vorher sicherstellen, dass die in der Sicherung gespeicherte IP noch auf dem Server verfügbar ist; andernfalls nach dem Kopieren bei gestopptem Dienst den IP-Wechsel durchführen.

```sh
cd "$INSTANCE"
docker compose down
cd /root
mv "$INSTANCE" "${INSTANCE}.before-restore-$(date +%Y%m%d-%H%M%S)"
cp -a "$BACKUP/instance" "$INSTANCE"
cd "$INSTANCE"
docker compose up -d --force-recreate --wait --wait-timeout 120
```

Anschließend die Nachkontrolle wiederholen. Kein `docker compose down -v`, keine globale Docker-Bereinigung und keine Token-Neugenerierung nötig. Auf einem anderen Rechner dieselbe Architektur bzw. ein passendes gesichertes Image verwenden; Netzwerk und Portbelegung vorher prüfen.

## Nachweis und Grenzen

Automatische Tests verwenden nur temporäre Installationen: echte Zertifikate, Schreibfehler-Rollback, Ablehnung eines belegten Ports und Erhalt privater Zustandsdateien. Linux-Docker-CI prüft Erneuerung, Wechsel auf eine zweite Loopback-IP, HTTPS/Login und vollständige Wiederherstellung. Das ersetzt nicht die Abnahme mit dem eigenen Browser und Loxone-Miniserver. Laufende Installationen werden von diesen Tests nicht berührt.
