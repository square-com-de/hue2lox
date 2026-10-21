# Hue-Szenen aus Loxone aufrufen

Szenen werden ausschließlich in der Hue-App erstellt und bearbeitet. Hue2Lox
liest gespeicherte Hue-v2-Ressourcen vom Typ `scene` ein und ruft sie statisch auf.
Smart Scenes (z. B. natürliches Licht mit Tagesverlauf), dynamische Wiedergabe,
Szenenerstellung, Änderung und Löschung sind nicht Teil dieser Erweiterung.

## Webinterface

Unter **Szenen → Szenen einlesen** werden Lampen und Szenen aller aktivierten,
gekoppelten Bridges neu eingelesen. Alternativ pro Bridge **Lampen & Szenen
einlesen** wählen. Beide Wege lesen nur; sie aktivieren keine Szene.
Die gemeinsame Inventur aktualisiert auch die Lampenliste. Zuvor lokal entfernte
Lampen können dadurch wieder erscheinen; ignorierte Lampen bleiben ignoriert.

Die Szenenliste zeigt Bridge und Raum bzw. Zone. Suche nach Name, Bridge oder
Raum, klappe **Befehle anzeigen** auf oder wähle eine bzw. mehrere Szenen für den
XML-Export. Das Hue2Lox-Token lässt sich als kompletter HTTP-Header kopieren.
Standardmäßig enthält XML nur einen Token-Platzhalter; die Option **Token in XML
aufnehmen** legt die Zugangsdaten ausdrücklich in der Exportdatei ab.

Eine Hue-Szene kann ignorierte oder lokal entfernte Lampen schalten, wenn diese
in der Hue-App zur Szene gehören. Hue2Lox verändert die Szenenmitgliedschaft
nicht. Bekannte betroffene Lampen werden zusätzlich in der Szenenliste genannt.
Nach dem Löschen einer Szene in der Hue-App erneut einlesen: Hue2Lox entfernt
sie aus seiner Liste und sperrt ihren Export und Steuerungspfad. Im Szenenbereich
liest auch der obere Button **Aktualisieren** die Bridges neu ein. Scheitert
eine Inventur, bleiben vorherige Daten erhalten; sie sind dann ggf. veraltet.

## Loxone Config

XML als virtuelle Ausgänge importieren oder Werte aus **Befehle anzeigen** übernehmen:

- Basisadresse: HTTPS-Adresse von Hue2Lox.
- Befehl bei EIN: `/api/scenes/<bridge-id>/<scene-id>/recall`.
- Methode bei EIN: `PUT`.
- HTTP-Header bei EIN als **eine Zeile**: `Authorization: Bearer DEIN_HUE2LOX_TOKEN\r\nContent-Type: application/json`. `\r\n` sind sichtbare Zeichen, keine echten Zeilenumbrüche; keine End-Leerzeile. Am besten **Header mit Token kopieren** oder XML verwenden, wie bei Lampen.
- HTTP-Body bei EIN: `{"recall":true}`.
- Digitalausgang verwenden, Wiederholung `0`.
- AUS-Befehl, AUS-Header und AUS-Body leer lassen.

Mit einem Impuls bzw. Taster aufrufen; für erneutes Aktivieren braucht es eine
neue EIN-Flanke. Es gibt keinen allgemeinen AUS-Aufruf für eine Szene. Lampen
lassen sich weiterhin über ihre vorhandenen Ein/Aus-Befehle ausschalten.
Hue2Lox speichert oder ändert keine Loxone-Konfiguration automatisch.

## Schnittstellen und Schutz

- `GET /api/admin/scenes`: Sitzungsanmeldung erforderlich, nur registrierte Metadaten.
- `POST /api/admin/scenes/export`: Sitzung, gleicher Ursprung und CSRF-Token;
  Body `{"scenes":["eg1/SCENE_ID"],"include_token":false}`.
- `PUT /api/scenes/<bridge-id>/<scene-id>/recall`: exakt `{"recall":true}`,
  gültiges Bearer-Token und `HUE_WRITES_ENABLED=1` erforderlich.
- Nur gespeicherte, vorhandene Szenen einer aktivierten Bridge sind aufrufbar.
- Hue-Aufruf intern: `PUT /clip/v2/resource/scene/<id>` mit
  `{"recall":{"action":"active"}}`, über den bestehenden TLS-geprüften Client.
- HTTP 200 mit `accepted:true` bestätigt eine erfolgreiche Hue-API-Antwort,
  keine nachträgliche Messung des Zustands aller beteiligten Lampen.

API-Referenz des Herstellers (Developer-Anmeldung ggf. erforderlich):
https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_scene__id__put

## Prüfung und Grenzen

Automatische Tests verwenden ausschließlich simulierte Hue-Antworten. Im Browser
wurden Einlesen, Auswahl, Befehlsansicht und XML-Download mit Testdaten geprüft.
Keine echte Szene wurde während der Entwicklung aktiviert. Der reale Aufruf und
XML-Import in Loxone Config müssen nach der Installation geprüft werden.

## Ignorieren und lokal entfernen

**Ignorieren** blendet eine Szene aus der Standardliste aus und sperrt Aufruf
und XML-Export. Die Einstellung bleibt bei Neustart und erneutem Einlesen
erhalten. **Ignorierte anzeigen → Wieder einblenden** macht sie rückgängig.

**Entfernen** nimmt die Szene nur aus Hue2Lox. Eine Bestätigung erklärt, dass
sie beim nächsten erfolgreichen Einlesen wieder erscheinen kann, solange sie
noch in der Hue-App besteht. Die Hue-Szene wird nicht gelöscht oder geändert.
Beide Aktionen ändern nur lokale Metadaten und benötigen Anmeldung sowie
CSRF-Schutz; es gibt keine Hue-Schreibanfrage. Ignorierte Szenen bleiben auch
nach lokalem Entfernen und Wiederfinden ignoriert.

Ein erfolgreiches vollständiges Einlesen ist für Szenen maßgeblich: auf der
Bridge gelöschte Szenen werden samt lokalen Einstellungen entfernt. Ein Fehler
bei der Inventur löscht keine bisherigen Daten. Bereits in Loxone importierte
Ausgänge bleiben bestehen und müssen dort bei Bedarf manuell entfernt werden.

Szenen lassen sich nach **Bridge** und **Raum/Zone** filtern, kombiniert mit der
Textsuche. **Gefilterte auswählen** ergänzt nur sichtbare, verfügbare Szenen zur
XML-Auswahl. Die bestehende Auswahl bleibt beim Filterwechsel erhalten.
