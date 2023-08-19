# Midea2Lox

Integration von Mideagroup Klimaanlagen in Loxone.
----- mit Loxone nicht getestet, folgende Hersteller können aber funktionieren----
Custom Integration for Midea Group(Ariston, Hualing, Senville, Klimaire, Kaysun, AirCon, Century, Pridiom, Thermocore, Comfee, Alpine Home Air, Artel, Beko, Electrolux, Galactic, Idea, Inventor, Kaisai, Mitsui, Mr. Cool, Neoclima, Olimpia Splendid, Pioneer, QLIMA, Royal Clima, Qzen, Toshiba, Carrier, Goodman, Friedrich, Samsung, Kenmore, Trane, Lennox, LG and much more) Air Conditioners via LAN.
----- nicht getestet----

Dieses Loxberry Plugin ermöglicht eine kommunikation zwischen dem Loxberry/Loxone zu Midea Klimaanlagen.

Der Hauptpart, das Python3 Midea Script, stammt im Ursprung von NeoAcheron https://github.com/NeoAcheron/midea-ac-py (Cloud Version bis Midea2Lox 1.1) . Vielen Dank dafür, ohne dieses Plugin hätte das nicht funktioniert.
Für die Steuerung über LAN (ab Midea2Lox V2.0) hat mac_zhou mit msmart https://github.com/mac-zhou/midea-msmart großartige leistung geleistet. Danke dafür! (Thanks mac-zhou!)
msmart wird nun weiterentwickelt von mill1000 --> https://github.com/mill1000/midea-msmart

# Installation:
Plugin herunterladen und im Pluginmanager des Loxberry installieren.
Anschließend gewünschten Empfangsport angeben,danach kann über start der Service gestartet werden.

Das Plugin übernimmt die Kommunikation zwischen Midea und Loxberry.Auf dem Loxberry läuft ein UDP Server, der bei Befehlseingang diese an Midea schickt. Der Aktuelle Status wird über die Virtuellen Eingänge des Loxberry direkt ausgegeben/geschalten,
daher müssen die Eingänge in Loxone genau den Wortlaut wie in der Beispielkonfig haben.Die Beispielkonfig für Loxone ist auch hier zu finden.

Weitere Infos sind unter https://www.loxwiki.eu/display/LOXBERRY/Midea2Lox zu finden

Ab Midea2Lox V2.0 findet die kommunikation direkt über LAN ohne Cloud statt. 

# Midea 8370 Protocol / V3, bspw. EU-OSK103
Ab Midea2Lox V3.0 werden die neueren Sticks mit Protokoll Version 3 über LAN unterstützt.
