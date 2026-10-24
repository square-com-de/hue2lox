# Szenen als Ein/Aus-Lichtkreis

Seit Stable 1.0.0 verfügbar. Szenenwechsel und abschließendes AUS wurden am 24.10.2026 vom Nutzer im Portainer-Teststack mit Hue und Loxone bestätigt. Bestehende Loxone-Befehle werden nicht umgeschrieben.

## Einrichtung

**Ein/Aus ist direkt in jeder Szenenzeile sichtbar und der Standard.** Gibt es genau eine Gruppe mit exakt denselben Lampen wie die Szene, ordnet Hue2Lox sie beim Start bzw. bei der Inventur automatisch zu. Kein Haken, kein zusätzlicher Speichern-Schritt. Die Zuordnung wird lokal gespeichert; es wird keine Szene aktiviert.

1. Szenen einlesen. Eine bereits bekannte, eindeutig passende Gruppe funktioniert nach dem Update ohne erneute Auswahl.
2. Direkt neben **Steuerung: Ein/Aus** steht die Gruppe für AUS. Ihre Lampen einschließlich ausgeblendeter Lampen und Überschneidungen sind direkt sichtbar.
3. Gibt es mehrere exakt passende Gruppen oder nur größere Gruppen, eine Gruppe auswählen. Die Auswahl wird unmittelbar gespeichert. Größere Gruppen werden nie automatisch gewählt; zusätzliche Lampen werden ausdrücklich mit Namen gezeigt. Bis zur Auswahl gibt es kein Ein/Aus-XML und keine irreführenden Ersatzbefehle.
4. XML exportieren und den **digitalen**, nicht analogen Ausgang als eigenen Lichtkreis im Loxone-Lichtbaustein verwenden. EIN sendet `{"on":true}`, AUS `{"on":false}` an `/api/scenes/<bridge>/<scene>/state`. Wiederholung bleibt 0.
5. Wer nur den bisherigen Szenenaufruf benötigt, wählt direkt **Nur aktivieren**. Diese Wahl bleibt nach Neustart und Inventur erhalten; der Export enthält dann wie bisher nur Recall.

EIN aktiviert die gespeicherte Hue-Szene ohne zusätzlichen Dimmwert. AUS schaltet **die ganze zugeordnete Gruppe** aus, auch zusätzliche Lampen. Es gibt keinen nativen Hue-Szene-AUS-Endpunkt. Nach Änderungen in Hue erneut einlesen. Ändert sich die gespeicherte Gruppenmitgliedschaft oder Szenenzuordnung, wird nicht still eine neue Gruppe gewählt: Die Oberfläche zeigt die aktuellen Lampen und fordert zur erneuten Gruppenauswahl auf. Dabei erscheint der Auswahlplatzhalter, damit auch dieselbe geänderte Gruppe mit einer Auswahl neu übernommen werden kann. Eine zwischenzeitlich veraltete Auswahl wird abgewiesen; keine Bestätigungscheckbox.

Vorhandene ausdrückliche Gruppenzuordnungen werden beibehalten. Bereits bestehende Recall-Endpunkte und importierte Loxone-Befehle funktionieren weiter und werden nicht umgeschrieben. Für neue Exporte gilt der angezeigte Modus. Ein Altstand ohne gespeicherten Modus/Gruppe gilt als unentschieden: Ein/Aus ist dort der neue Standard, automatisch nutzbar nur bei eindeutig exakter Gruppe. Der erste PR45-Stand hatte eine zurückgesetzte Recall-Wahl nicht gespeichert; solche früheren Entscheidungen sind nachträglich nicht erkennbar. Die neue ausdrückliche Recall-Wahl wird gespeichert. Veröffentlichte RC-Pakete bleiben unverändert.

## Szenenwechsel und Grenzen

Hue2Lox verarbeitet Szenenbefehle ohne künstlichen Einschaltverzug nacheinander. Für A und B auf derselben Gruppe funktionieren beide Folgen: A EIN → A AUS → B EIN sowie A EIN → B EIN → A AUS. Im zweiten Fall wird das überholte A AUS ohne Hue-Aufruf ignoriert. Ein ignorierter Befehl wird im Monitor ausdrücklich als solcher angezeigt, nicht als Hue-Bestätigung. Bei der ersten Folge kann vor B ein kurzes Ausschalten auftreten; flackerfreier Wechsel ist nicht zugesichert.

Wiederholtes AUS einer bereits ausgeschalteten Szene wird ignoriert. Wiederholtes EIN ruft die Szene erneut auf; es gibt keine verzögerten Hintergrundaktionen. Für überlappende Gruppen muss zuerst die aktive Gruppe ausgeschaltet werden. Andernfalls antwortet EIN mit HTTP 409 und sendet nichts an Hue. Disjunkte Gruppen bleiben unabhängig; die Ausführung wird trotzdem serialisiert.

Die Zuordnung ist **Befehlshistorie, kein gemessener Lampenzustand** und keine Rückmeldung an Loxone. Nach Neustart, geänderter Konfiguration oder reinem Recall ist sie unbekannt: zunächst EIN der gewünschten Szene senden; AUS ohne eindeutige Zuordnung wird mit HTTP 409 abgewiesen. Nach Timeout oder Hue-Teilfehler wird kein Erfolg behauptet (HTTP 502); der Ausgang ist möglicherweise unklar. Überlappende Gruppen bleiben in diesem Fall gesperrt, bis ein erfolgreiches EIN derselben Gruppe die Zuordnung wiederherstellt. Kein automatisches Wiederholen oder Wiederanschalten. Ein bewusstes EIN kann dabei die Beleuchtung erneut aktivieren.

**Nicht lösbare Grenze ohne Ereigniskennung:** Bei A EIN → B EIN → A EIN → A AUS kann der letzte Befehl sowohl ein verspätetes AUS der ersten A-Aktivierung als auch das echte AUS der neuen A-Aktivierung sein. Die statischen Loxone-Ausgänge liefern keine Aktivierungskennung. Die Reihenfolge gilt ab Aufnahme des vollständig validierten Befehls in die Warteschlange, nicht ab Netzwerkankunft. Hier gilt diese Reihenfolge: das letzte A AUS schaltet die aktuell zugeordnete Gruppe aus. Es gibt keine Garantie gegen beliebig verspätete Befehle und kein pauschales Delay, das diese Mehrdeutigkeit behebt.

Hue-App, physische Schalter, normale Lampenausgänge und andere Integrationen können Lampen unabhängig verändern. Diese Änderungen werden nicht in die Szenen-Befehlshistorie zurückgeführt. Für konsistentes Verhalten die Ein/Aus-Szenenkreise nicht mit parallelen Steuerwegen derselben Lampen mischen. Bestehende reine Recall-Endpunkte und Recall-XML bleiben verfügbar.

## Noch abzunehmen

Automatisierte Tests verwenden ausschließlich künstliche Bridge-Antworten und prüfen beide Reihenfolgen, schnelle Wechsel, Wiederholungen, abschließendes AUS, Gruppenisolierung/Überlappung, Gleichzeitigkeit, Neustart, Timeout/Teilfehler, Token/CSRF und XML. Das ist kein Nachweis realer Hue- oder Loxone-Reihenfolgen. Vor Freigabe in einer ausdrücklich gewählten Testumgebung reale A/B-Wechsel, schnelle A/B/C-Wechsel, finales AUS und die sichtbare Gruppenwirkung prüfen; Monitorbelege ohne Token/Schlüssel erfassen. Keine Produktionsmessung oder automatische Migration.
