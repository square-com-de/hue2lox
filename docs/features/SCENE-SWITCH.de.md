# Szenen als Ein/Aus-Lichtkreis — Entwicklung nach RC6

Diese optionale Erweiterung gehört zum Feature-PR für [Issue 42](https://github.com/square-com-de/hue2lox/issues/42), nicht zum veröffentlichten RC6. Keine automatische Umstellung bestehender Konfigurationen. Hardwareabnahme noch offen.

## Einrichtung

1. Unter **Szenen** die Inventur erneut einlesen. Dies aktiviert keine Szene.
2. Bei der Szene **Verwaltung → Nutzungsart der Szene** öffnen. Standard bleibt **Nur aktivieren**.
3. Zielgruppe auswählen und **alle aufgeführten Lampen** prüfen. Es werden auch ausgeblendete Lampen und überlappende Gruppen angezeigt. Angeboten werden nur vollständig zuordenbare Hue-Räume/Zonen, die alle Szenenlampen enthalten und einen eindeutigen Gruppenendpunkt besitzen.
4. Ganze Gruppenwirkung ausdrücklich bestätigen und speichern. Eine zwischenzeitlich geänderte Inventur muss erneut bestätigt werden.
5. XML neu exportieren und den **digitalen**, nicht analogen Ausgang als eigenen Lichtkreis im Loxone-Lichtbaustein verwenden. EIN sendet `{"on":true}`, AUS `{"on":false}` an `/api/scenes/<bridge>/<scene>/state`. Wiederholung bleibt 0. Bestehende Loxone-Projekte werden nicht automatisch geändert.

EIN aktiviert die gespeicherte Hue-Szene ohne zusätzlichen Dimmwert. AUS schaltet **die gesamte bestätigte Gruppe** aus, auch Lampen, die die Szene selbst nicht verändert. Es gibt keinen nativen Hue-Szene-AUS-Endpunkt. Änderungen an Gruppenmitgliedschaft oder Szenenzuordnung sperren den Ein/Aus-Endpunkt bis zur erneuten Bestätigung nach Inventur. Änderungen außerhalb Hue2Lox sind erst nach erneuter Inventur bekannt; deshalb nach Änderungen in Hue vor weiterer Nutzung neu einlesen.

## Szenenwechsel und Grenzen

Hue2Lox verarbeitet Szenenbefehle ohne künstlichen Einschaltverzug nacheinander. Für A und B auf derselben Gruppe funktionieren beide Folgen: A EIN → A AUS → B EIN sowie A EIN → B EIN → A AUS. Im zweiten Fall wird das überholte A AUS ohne Hue-Aufruf ignoriert. Ein ignorierter Befehl wird im Monitor ausdrücklich als solcher angezeigt, nicht als Hue-Bestätigung. Bei der ersten Folge kann vor B ein kurzes Ausschalten auftreten; flackerfreier Wechsel ist nicht zugesichert.

Wiederholtes AUS einer bereits ausgeschalteten Szene wird ignoriert. Wiederholtes EIN ruft die Szene erneut auf; es gibt keine verzögerten Hintergrundaktionen. Für überlappende Gruppen muss zuerst die aktive Gruppe ausgeschaltet werden. Andernfalls antwortet EIN mit HTTP 409 und sendet nichts an Hue. Disjunkte Gruppen bleiben unabhängig; die Ausführung wird trotzdem serialisiert.

Die Zuordnung ist **Befehlshistorie, kein gemessener Lampenzustand** und keine Rückmeldung an Loxone. Nach Neustart, geänderter Konfiguration oder reinem Recall ist sie unbekannt: zunächst EIN der gewünschten Szene senden; AUS ohne eindeutige Zuordnung wird mit HTTP 409 abgewiesen. Nach Timeout oder Hue-Teilfehler wird kein Erfolg behauptet (HTTP 502); der Ausgang ist möglicherweise unklar. Überlappende Gruppen bleiben in diesem Fall gesperrt, bis ein erfolgreiches EIN derselben Gruppe die Zuordnung wiederherstellt. Kein automatisches Wiederholen oder Wiederanschalten. Ein bewusstes EIN kann dabei die Beleuchtung erneut aktivieren.

**Nicht lösbare Grenze ohne Ereigniskennung:** Bei A EIN → B EIN → A EIN → A AUS kann der letzte Befehl sowohl ein verspätetes AUS der ersten A-Aktivierung als auch das echte AUS der neuen A-Aktivierung sein. Die statischen Loxone-Ausgänge liefern keine Aktivierungskennung. Die Reihenfolge gilt ab Aufnahme des vollständig validierten Befehls in die Warteschlange, nicht ab Netzwerkankunft. Hier gilt diese Reihenfolge: das letzte A AUS schaltet die aktuell zugeordnete Gruppe aus. Es gibt keine Garantie gegen beliebig verspätete Befehle und kein pauschales Delay, das diese Mehrdeutigkeit behebt.

Hue-App, physische Schalter, normale Lampenausgänge und andere Integrationen können Lampen unabhängig verändern. Diese Änderungen werden nicht in die Szenen-Befehlshistorie zurückgeführt. Für konsistentes Verhalten die Ein/Aus-Szenenkreise nicht mit parallelen Steuerwegen derselben Lampen mischen. Bestehende reine Recall-Endpunkte und Recall-XML bleiben verfügbar.

## Noch abzunehmen

Automatisierte Tests verwenden ausschließlich künstliche Bridge-Antworten und prüfen beide Reihenfolgen, schnelle Wechsel, Wiederholungen, abschließendes AUS, Gruppenisolierung/Überlappung, Gleichzeitigkeit, Neustart, Timeout/Teilfehler, Token/CSRF und XML. Das ist kein Nachweis realer Hue- oder Loxone-Reihenfolgen. Vor Freigabe in einer ausdrücklich gewählten Testumgebung reale A/B-Wechsel, schnelle A/B/C-Wechsel, finales AUS und die sichtbare Gruppenwirkung prüfen; Monitorbelege ohne Token/Schlüssel erfassen. Keine Produktionsmessung oder automatische Migration.
