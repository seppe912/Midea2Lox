# Midea2Lox
Integration von Midea in Loxone

Dieses Loxberry Plugin ermöglicht eine kommunikation zwischen dem Loxberry/Loxone zu Midea Klimaanlagen.

Der Hauptpart, das Python3 Midea Script, stammt von NeoAcheron https://github.com/NeoAcheron/midea-ac-py. Vielen Dank dafür, ohne dieses Plugin hätte das nicht funktioniert.

Installation:
Plugin herunterladen und im Pluginmanager des Loxberry installieren.
Anschließend die Zugangsdaten zur Midea API im Plugin eintragen. Danach kann über start der Service gestartet werden.

Das Plugin übernimmt die Kommunikation zwischen Midea und Loxberry.Auf dem Loxberry läuft ein UDP Server, der bei Befehlseingang diese an Midea schickt. Der Aktuelle Status wird über die Virtuellen Eingänge des Loxberry direkt ausgegeben/geschalten,
daher müssen die Eingänge in Loxone genau den Wortlaut wie in der Beispielkonfig haben.Die Beispielkonfig für Loxone ist auch hier zu finden.

Weitere Infos sind unter https://www.loxwiki.eu/display/LOXBERRY/Midea2Lox zu finden

Ab V2.0 findet die kommunikation direkt über LAN ohne Cloud statt. Lediglich die ID der Geräte muss einmaig von der Cloud ausgelesen werden
