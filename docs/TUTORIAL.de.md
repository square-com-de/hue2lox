# Hue2Lox: HTTP-Ausgänge in Loxone Config

Beispiel für Loxone Config 17.2. Hue2Lox und die eingelesene Lampe müssen vom
Miniserver erreichbar sein. Lade dessen aktuellen Programmstand und sichere ihn
vor der Änderung. Die Bilder enthalten keine echten Zugangsdaten.

## 1. Steuerungsart wählen

Unter **Lampen** stehen Produkt-/Modellname, Lampentyp und Fähigkeits-Badges aus
der Hue Bridge: Ein/Aus, Dimmer, Tunable White und RGB. Ein lokaler Modellkatalog
kann den Produktnamen ergänzen; er überschreibt keine erkannten Fähigkeiten.

Unter **Für Loxone nutzen** die gewünschten Nutzungsarten anhaken. Die Auswahl
wird dauerhaft gespeichert und bleibt nach erneutem Einlesen der Bridge erhalten.
Standardmäßig ist eine passende Variante gewählt:

| Lampenfunktionen | Vorauswahl |
| --- | --- |
| Farbe und Weißtemperatur | Lumitech RGB + Weiß |
| Farbe | RGB |
| Weißtemperatur ohne Farbe | Tunable White |
| Helligkeit ohne Weißtemperatur | Dimmen |
| Nur schaltbar | Ein/Aus |

**XML enthält alle angehakten Varianten.** Unter **Befehlsvorschau** eine davon
zum Kopieren anzeigen; gemeinsame Felder werden dabei nur einmal dargestellt.
Mindestens eine Nutzungsart muss aktiv bleiben. Die Auswahl ändert keine Lampe
und bestehende Loxone-Befehle bleiben unverändert.

Es werden nur erkannte und auf dem Server freigeschaltete Varianten angeboten.
Für Tunable White in Loxone **Lumitech** verwenden und **Weiße Lichtfarbe**
wählen. Für einen sichtbaren Weißtest die Helligkeit über 0 % einstellen.
Der Body lautet auch hier `{"loxone_lumitech":<v>}`. Lumitech RGB + Weiß nutzt
 denselben Body, unterstützt zusätzlich Farbauswahl.

![Steuerungsart und zu kopierende Felder in Hue2Lox](../web/tutorial-commands.png)

## 2. Virtuellen Ausgang anlegen

1. In Loxone Config **Virtuelle Ausgänge** markieren und einen **Virtuellen Ausgang** anlegen, etwa `Hue2Lox`.
2. Als Adresse die Hue2Lox-Basisadresse eintragen, beispielsweise `https://192.0.2.96:8443`.
3. Darunter einen **Virtuellen Ausgang Befehl** anlegen.

Die Adresse gehört zum Hue2Lox-Server. Lampenpfad und `/health` gehören nicht in
diese Basisadresse.

## 3. Felder aus Hue2Lox übernehmen

Die Kopierfelder stehen in der Reihenfolge der Loxone-Eigenschaften:

| Hue2Lox | Loxone Config |
| --- | --- |
| Name des Ausgangsbefehls | Name des Befehls |
| Befehl bei EIN | Befehl bei EIN |
| HTTP header bei EIN | HTTP header bei EIN |
| HTTP body bei EIN | HTTP body bei EIN |
| HTTP Methode bei EIN | HTTP Methode bei EIN: PUT |

**Header mit Token kopieren** kopiert den fertigen Header einschließlich
Berechtigung und `Content-Type`. Der Header ist eine einzige Zeile mit der
sichtbaren Zeichenfolge `\r\n` zwischen den beiden Feldern. Diese Zeichen genau
so übernehmen; nicht durch Enter ersetzen und keine Leerzeile am Ende ergänzen.

```text
Authorization: Bearer DEIN_HUE2LOX_TOKEN\r\nContent-Type: application/json
```

Nach einem Update bestehende EIN-Header (und bei Ein/Aus auch AUS-Header) vollständig
durch die neue Kopie ersetzen. Ein Update ändert vorhandene Loxone-Befehle nicht.
XML-Exporte verwenden dasselbe Format. Zum Korrigieren bestehender Ausgänge ist
kein neuer Import nötig; nur deren Header austauschen.

 Den Platzhalter `DEIN_HUE2LOX_TOKEN` nicht als
echtes Token verwenden. `<v>` im Body unverändert und ohne Anführungszeichen
übernehmen: Loxone ersetzt es durch den Ausgangswert.

- **Ein/Aus:** Digitalausgang aktivieren und die angezeigten AUS-Felder ebenfalls übernehmen.
- **Dimmen, Tunable White, RGB, Lumitech:** Einheit auf `<v>` setzen. Digitalausgang deaktivieren, AUS-Felder leer lassen. Wert 0 schaltet aus. Dimmen verwendet 0–100 %; RGB bzw. Lumitech benötigt den entsprechenden Aktortyp am Lichtsteuerungsbaustein.

![Eigenschaften eines virtuellen Ausgangsbefehls in Loxone Config](../web/tutorial-config.png)

## Alternative: XML importieren

**Empfehlung:** Mehrere Lampen markieren und gemeinsam über **Auswahl als XML**
exportieren. Beim Import entsteht ein virtueller Ausgang mit den Befehlen aller
ausgewählten Lampen. Jeder separate XML-Import legt einen weiteren Ausgang an;
ein bereits vorhandener Ausgang wird nicht automatisch ergänzt. Für spätere
Ergänzungen kannst du einen Befehl am bestehenden Ausgang manuell anlegen und
die Felder aus Hue2Lox kopieren.

**XML** lädt alle angehakten Nutzungsarten dieser Lampe herunter. Für mehrere
Lampen die gewünschten Einträge markieren und den gemeinsamen XML-Export nutzen.
Jede angehakte Nutzungsart erhält einen eigenen Befehl; ohne Änderung gilt die
Empfehlung. Nicht mehrere parallel verbundene Ausgänge auf dieselbe Lampe wirken lassen. Filter grenzen die sichtbare Liste ein.

Die Vorlage in Loxone Config bei den virtuellen Ausgängen importieren, anschließend
Basisadresse, Token und Aktortyp prüfen. Standardmäßig enthält XML einen
Token-Platzhalter. Der Export mit echtem Token muss ausdrücklich gewählt werden;
diese Datei enthält Zugangsdaten und gehört nicht in öffentliche Ablagen.

## 4. Vom Miniserver testen

Den Befehl mit einem passenden Testausgang verbinden, das Programm im Miniserver
speichern und gezielt auslösen. Im **HTTP-Monitor** die Antwort kontrollieren:
HTTP 200 bestätigt einen erfolgreichen Aufruf. Erst die sichtbare Reaktion der
Lampe bestätigt die gewünschte Wirkung.

![Beispiel einer erfolgreichen Antwort im HTTP-Monitor](../web/tutorial-monitor.png)

Bei 401 Token prüfen, bei 403 Freischaltung der Steuerung. Bei **HTTP 400** den
**HTTP-Monitor** in Hue2Lox starten und den Befehl erneut auslösen. Unter
**Body (bereinigt)** den tatsächlich empfangenen Wert prüfen: Zahl statt
Zeichenkette, ersetztes `<v>` und passende Steuerungsart (RGB oder Lumitech).
Bei ungültigem JSON zeigt der Monitor Zeile und Spalte des Fehlers.

`<v.1>` ist als Ursache des bisherigen Fehlers nicht bestätigt. Der RGB-/Lumitech-
Parser akzeptiert auch ganzzahlige JSON-Zahlen wie `84013.0`; Werte mit echtem
Nachkommaanteil werden abgelehnt. Deshalb den empfangenen Body prüfen, statt aus
der Anzeigeformatierung allein auf die Ursache zu schließen.

 Bei Verbindungsproblemen Adresse, tatsächlich konfigurierten Port (Installer-Vorgabe 18443) und Zertifikat prüfen.
Die temporäre Logfunktion unter **HTTP-Monitor** zeigt eingegangene
Befehle ohne Tokens. Ein Browser-Zertifikatsvertrauen gilt nicht automatisch für
den Miniserver; dessen HTTPS-Aufruf muss separat funktionieren.

## Szenen

Szenen werden in der Hue App erstellt und geändert. Unter **Szenen** die Liste
synchronisieren und den angezeigten Abrufbefehl oder XML verwenden. Eine Szene
wird per EIN-Impuls abgerufen; AUS-Felder bleiben leer.

## Kurze Lampenpfade

Den Befehlspfad direkt aus der Lampenkarte kopieren. GUI und XML verwenden
`/<bridge>/<lampe>/state` mit höchstens acht Zeichen je Name. Die Namen bleiben
nach Umbenennen oder erneutem Einlesen stabil. Alte lange Pfade und der bisherige
Hue-Go-Pfad funktionieren weiterhin. Vorhandene Loxone-Befehle werden nicht
automatisch geändert; zum Vergleich nur den Pfad ersetzen, Header und Body
unverändert lassen. Ob damit das CR/LF-Problem verschwindet, muss der Test zeigen.
