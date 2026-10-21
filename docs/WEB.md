# Web-Interface mit lokaler Anmeldung

18.10.2026. Übersicht, Lampensuche/Bridge-Filter, Bridge-Verwaltung und geschützte Loxone-Einrichtung. Kein Schalten durch UI oder XML-Export. Oktopus, Modell-Symbole und „by square | com“ liegen lokal im Image, ohne CDN.

## Verwaltung

- Übersicht: aktive Bridges, eingerichtete Lampen, gemeldete Zustände und Fehler.
- Lampen: Namen, Räume, Modell-Symbole, gespeicherte Helligkeit und gültige Weißtemperatur. Reine Schaltaktoren erhalten keinen erfundenen Helligkeitswert.
- Bridges: Name/IP hinzufügen, HTTPS-Identität prüfen, per Link-Taste koppeln, sämtliche vorhandenen Lampen einlesen und bei Bedarf erneut koppeln. Siehe [BRIDGES.md](BRIDGES.md).
- Loxone: Token anzeigen/verbergen, vollständigen Header kopieren, Befehle je Lampe ein-/ausklappen und XML einzeln oder als Auswahl exportieren. Siehe [ADMIN.md](ADMIN.md).

Die Webdaten verlangen eine Admin-Sitzung. Loxone-Steuerung verwendet weiterhin das separate Hue2Lox-Bearer-Token. Hue-Bridge-Keys bleiben intern.

## Registry und mehrere Bridges

Schema-Version 1: Liste von Bridges mit id, name, host, enabled und lights. Aktive Bridges besitzen serverseitig bridge_id und key_file; letzteres ist nur ein Pfad, nie ein ausgegebener Keywert. Neue Keys und Runtime-Registry liegen auf dem geschützten persistenten `/data`-Mount. Die bisherige Registry wird einmal migriert und anschließend vom Installer bewahrt.

Die öffentliche Ausgangskonfiguration ist leer. Bridges werden lokal gesucht (unter anderem per mDNS) oder über eine private IP ergänzt und gekoppelt. Inventur übernimmt die tatsächlichen Lampen. Bestehende IDs und historische Aliase bleiben bei vorhandenen Installationen erhalten. Ein allgemeiner Konfigurationseditor und SSE sind nicht enthalten. Details zur Suche: [DISCOVERY.md](DISCOVERY.md).

Statusabfragen werden je aktiver Bridge gebündelt, mit vier parallelen Bridge-Abfragen, 5-Sekunden-Cache und Aktualisierung im Browser alle 10 Sekunden. Diese Abfragen lesen gemeldete/gespeicherte Zustände und sind keine physische Bestätigung jedes Lampenbefehls.

## Historischer Prüfstand vom 18.10.2026

Der folgende Bericht dokumentiert den damaligen Ausbau, nicht die Abnahme des heutigen Release-Kandidaten. Aktuelle Rückmeldungen: [TEST-RESULTS.md](TEST-RESULTS.md).

45 lokale Tests bestanden, darunter bestehende Steuer-/Farbtests und neue Bridge-Prüfungen. Browser mit Testdaten: Login, Tokenkopie, einklappbare Befehle, Export, Hinzufügen, Kopplung und Inventur geprüft. Echte EG-Bridge rein lesend mit Zertifikats- und Identitätsprüfung erkannt. Produktive Kopplung, Vollinventur und Container-Betrieb des neuen Ausbaus bleiben bis zur Installation offen.


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

## Szenen

Eigener Bereich mit Suche, Einlesen aller gekoppelten aktiven Bridges,
aufklappbaren HTTP-Befehlen, Header-Kopierfunktion und Einzel-/Mehrfach-XML.
Erstellen und Bearbeiten erfolgen in der Hue-App. Details: [SCENES.md](SCENES.md).

Szenen bieten ebenfalls **Ignorieren**, **Wieder einblenden** und **Entfernen**.
Der obere Button **Aktualisieren** führt im Szenenbereich eine neue Inventur
der aktiven, gekoppelten Bridges aus. In der Hue-App gelöschte Szenen
verschwinden nach erfolgreichem Einlesen vollständig aus der Liste.

## Gerätesuche und Dashboard

Unter Loxone lässt sich ein Miniserver suchen oder eine lokale HTTP-/HTTPS-Adresse
manuell als Link speichern. Die Übersicht zeigt dann **Loxone öffnen** und die
Anzahl aktiver Szenen. Die bisherigen zwei Lampenkarten entfallen. Unter Bridges
steht eine lokale Hue-Suche zur Verfügung; Ergebnisse werden vor dem Koppeln
weiterhin geprüft. Bei Docker-/Netzwerkgrenzen bleibt die manuelle Eingabe
verfügbar. Details: [DISCOVERY.md](DISCOVERY.md).

## HTTP-Monitor

Eigener Bereich **HTTP-Monitor** mit zehnminütigem Testlauf, automatischer Anzeige
der letzten 200 bereinigten Steuerungsanfragen, Stoppen, Leeren und Kopieren.
Auch abgelehnte Bodies werden bereinigt angezeigt, inklusive Zahlenwerten,
Feldtypen und JSON-Fehlerposition. Kein Token, Schlüssel oder Roh-Body im Protokoll. Die Funktion schaltet selbst
keine Lampen. Nutzung und Grenzen: [MONITOR.md](MONITOR.md).

## Bridge- und Raumfilter

Lampen und Szenen haben kombinierbare Filter **Bridge** und **Raum/Zone**
zusätzlich zur Textsuche. Bridge bezeichnet den frei vergebenen Bridge-Namen,
keine festgelegte Geschossstruktur. Räume stammen aus der Hue-Inventur; Szenen
können auch einer Hue-Zone zugeordnet sein. Bei Lampen wird der Hue-Raum benutzt.
Die Raumauswahl enthält nur vorhandene Zuordnungen der gewählten Bridge.
Nicht zugeordnete Einträge sind als **Ohne Raum/Zone** filterbar.

Eine passende Auswahl bleibt bei Statusaktualisierungen erhalten. Fällt die
Zuordnung weg oder ist sie nach einem Bridgewechsel nicht mehr vorhanden, wird
der betroffene Filter auf **Alle** gesetzt. Die Filter der beiden Listen sind
unabhängig und werden nach Abmelden zurückgesetzt.

Bei Szenen wählt **Gefilterte auswählen** nur sichtbare, verfügbare Treffer für
XML aus. Schon ausgewählte Szenen bleiben beim Filterwechsel ausgewählt;
**Auswahl leeren** setzt die gesamte Auswahl zurück.

## Befehle und Export direkt bei Lampen

**Lampen** vereint Status, Bridge-/Raumfilter, Ignorieren/Entfernen und die
Loxone-Anbindung in einer Liste. Jede Lampenkarte bietet eine XML-Auswahl,
**Befehle anzeigen**, Kopierfunktionen einschließlich HTTP-Header mit Token
und den Einzel-XML-Download. Befehlsdetails sind standardmäßig eingeklappt;
es ist jeweils höchstens eine Lampenkarte geöffnet.

**Gefilterte auswählen** ergänzt nur sichtbare, verfügbare Lampen zur XML-Auswahl.
Die Auswahl bleibt beim Filtern erhalten; **Auswahl leeren** setzt sie zurück.
Der optionale Token-Export gehört ebenfalls zu Lampen. Eine zweite Lampenliste
im Loxone-Bereich gibt es nicht mehr.

**Loxone-Einstellungen** enthält ausschließlich Miniserver-Suche und -Link sowie
die zentrale Anzeige/Kopierfunktion für das Zugriffstoken.
**Szenen** bleibt unverändert mit Befehlen, XML sowie Bridge-/Raum-/Zonenfiltern
und kombinierbarer Suche.

## Reihenfolge der Kopierfelder

Lampen und Szenen zeigen zuerst den **Namen des Ausgangsbefehls** (identisch
mit dem XML-Titel), danach **Befehl bei EIN**, **HTTP header bei EIN**,
**HTTP body bei EIN** und **HTTP Methode bei EIN**. Ein/Aus-Befehle zeigen
anschließend die entsprechenden AUS-Felder. **HTTP-Antwort speichern** bleibt
leer. Die Basisadresse des virtuellen Ausgangs ist separat darunter aufklappbar.
Der Header wird mit Platzhalter angezeigt; **Header mit Token kopieren** holt
das aktuelle Token über die geschützte Schnittstelle und kopiert den fertigen
Header. Es wird nicht automatisch in der Ansicht ausgegeben.

## Bebilderte Anleitung

Der Footer-Link **Anleitung: Loxone-Ausgänge** öffnet `/tutorial` mit der
Schritt-für-Schritt-Anleitung einschließlich drei Bildern. Sie umfasst manuelle
Einrichtung, Ein/Aus, Dimmen, RGB/Lumitech, Hue-Szenen, XML-Import und Fehlersuche.
Die Repository-Fassung liegt in [TUTORIAL.de.md](TUTORIAL.de.md). Die Hilfeseite ist
statisch, enthält keine Zugangsdaten und ist auch ohne Anmeldung lesbar.

## Lampentyp, Fähigkeiten und Nutzungsarten

Die Lampenkarte zeigt Produktname, Modellkennung, Typ und Badges für Ein/Aus,
Dimmer, Tunable White und RGB. Die Bridge-Felder bleiben maßgeblich; der lokale
Katalog ergänzt nur Modellnamen. Unter **Für Loxone nutzen** werden passende
Nutzungsarten per Checkbox gewählt und im State unter `enabled_modes` gespeichert.
Die Auswahl überlebt Neustart und Inventur. Mindestens eine passende Variante
bleibt aktiv. Die Auswahl schaltet keine Lampe.

Die Vorauswahl ist Lumitech für Farbe + Weißtemperatur, RGB für Farblampen,
Tunable White für reine Weißtemperatur-Lampen, sonst Dimmen oder Ein/Aus.
Eine Befehlsvorschau zeigt jeweils eine angehakte Variante mit gemeinsamen
Kopierfeldern. Einzel-/Mehrfach-XML enthalten sämtliche angehakten Varianten,
standardmäßig eine pro Lampe. Bestehende UUID- und Kurzpfade bleiben bestehen.
Tunable White verwendet den Lumitech-Body und den entsprechenden Loxone-Aktortyp
im Weißmodus; RGB muss dafür serverseitig nicht freigeschaltet sein.

Der Download **Hue-Modelltabelle (CSV)** umfasst 949 recherchierte Modellkennungen.
Quelle, Lizenz und Grenzen sind in `catalog/README.md` dokumentiert. Kein
Vollständigkeitsversprechen; unbekannte Modelle bleiben anhand der Bridge nutzbar.

## Kurze Lampenpfade

GUI und XML verwenden `/<bridge>/<lampe>/state`, etwa
`/erdgesch/eg-wohne/state`. Beide Namen sind maximal acht Zeichen lang, klein
und URL-tauglich; Umlaute werden umgeschrieben. Kollisionen erhalten eine kurze
Hash-Endung innerhalb der acht Zeichen. Die Kurzpfade werden einmalig im
persistenten Registry-Datensatz unter `short_name` gespeichert. Umbenennen,
Ignorieren, Entfernen und erneutes Einlesen behalten sie bei. Alle registrierten
Lampen bekommen einen Kurzpfad; ignorierte, entfernte oder nicht verfügbare
Lampen bleiben für Steuerung gesperrt.

Die erste Registry-Lesung im beschreibbaren State-Verzeichnis ergänzt die Namen
atomar und legt vorher `registry.previous.json` an. Registry-Dateien im Image
werden nicht beschrieben. Bei vollständig gelöschten Registry-/State-Daten gelten
die Stabilitätsgarantien nicht. Alte `/api/lights/<bridge-id>/<light-id>/state`-
Pfade und `/hue-go/state` bleiben kompatibel. Bestehende Loxone-Ausgänge werden
nicht automatisch geändert. Szenenpfade bleiben unverändert.

Kurze Pfade sind noch kein bestätigter Fix für die CR/LF-Verschiebung. Für einen
Vergleich nur den Befehlspfad in Loxone ersetzen und Header/Body gleich lassen;
der temporäre HTTP-Monitor erfasst auch Kurzpfade samt Byte-Diagnose.

## Header-Format für Loxone

Anzeige, Kopieren und XML liefern eine Zeile mit sichtbarem `\r\n` zwischen
Authorization und Content-Type, ohne echte Zeilenumbrüche oder End-Leerzeile.
Bestehende EIN-/AUS-Header nach dem Update neu kopieren; vorhandene Loxone-Befehle
werden nicht automatisch geändert. Der Miniserver-Livetest muss anschließend
korrekte Byte-Längen und eine erfolgreiche Antwort bestätigen.

Der CSV-Download lädt die Datei zunächst per Fetch und übergibt sie als lokale
Blob-Datei an den Browser, wie beim XML-Export. Die Antwort setzt zusätzlich
`Content-Disposition` mit `Hue-Modelltabelle.csv`. Ladefehler werden direkt neben
dem Button angezeigt; ein gestarteter Download ist keine Bestätigung, dass der
Browser die Datei bereits auf die Festplatte gespeichert hat.

## Kompakte Lampenansicht

Die Exportleiste zeigt Auswahl, XML-Export und Token-Option direkt nebeneinander.
Erklärungen und CSV-Download stehen im standardmäßig geschlossenen Bereich
**Hilfe & Modelltabelle**. Filter und Lampen folgen unmittelbar darunter.
Unkritische Aktualisierungshinweise entfallen auf der Lampenseite; Fehlerhinweise
bleiben sichtbar. Alle bisherigen Funktionen und Auswahlzustände bleiben erhalten.

Die Lampenkarten sind ebenfalls verdichtet: Name mit Ein/Aus-Badge, Bridge/Raum,
Typ und Fähigkeiten sowie Messwerte bleiben sichtbar. XML-Auswahl, Befehle und
Einzelexport liegen in einer kurzen Aktionszeile. **Nutzung & Verwaltung** öffnet
Produktname, Nutzungs-Checkboxen, Ignorieren und Entfernen. Die Befehlsvorschau
erscheint erst bei geöffneten Befehlen. Geöffnete Verwaltungsbereiche bleiben
während Aktualisierungen erhalten; beim Abmelden werden sie zurückgesetzt.

### Kompakte Szenenliste
Szenen zeigen Name, Bridge, Raum und Lampenanzahl in einer schmalen Karte. Befehle und XML bleiben direkt erreichbar; Ignorieren und Entfernen stehen unter „Verwaltung“. Der aufklappbare Bereich bleibt bei einer Neudarstellung geöffnet. Hinweise zum Einlesen und Export stehen unter „Hilfe“. Warnungen zu mitgeschalteten ausgeblendeten Lampen bleiben sichtbar.

### Deutsch / English – 19.10.2026

Sprachwahl bei Login und im Kopfbereich, automatische Erkennung und lokale Speicherung. Sprache wechseln lädt die aktuelle Seite neu; nicht gespeicherte Eingaben und temporäre XML-Auswahl werden zurückgesetzt. Bedienung, Meldungen, Hilfe und erzeugte XML-Beschriftungen werden übersetzt; Gerätenamen und technische Steuerungsdaten bleiben erhalten. Anleitung unter `/tutorial` und `/tutorial/en`, zweisprachige Quellen-/Lizenzseite unter `/licenses`. Details: I18N.md.
