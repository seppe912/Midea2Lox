# Midea2Lox

Integration von Mideagroup Klimaanlagen in Loxone.
----- mit Loxone nicht getestet, folgende Hersteller können aber funktionieren----
Custom Integration for Midea Group(Hualing, Senville, Klimaire, AirCon, Century, Pridiom, Thermocore, Comfee, Alpine Home Air, Artel, Beko, Electrolux, Galactic, Idea, Inventor, Kaisai, Mitsui, Mr. Cool, Neoclima, Olimpia Splendid, Pioneer, QLIMA, Royal Clima, Qzen, Toshiba, Carrier, Goodman, Friedrich, Samsung, Kenmore, Trane, Lennox, LG and much more) Air Conditioners via LAN.
----- nicht getestet----

Dieses Loxberry Plugin ermöglicht eine kommunikation zwischen dem Loxberry/Loxone zu Midea Klimaanlagen.

Der Hauptpart, das Python3 Midea Script, stammt im Ursprung von NeoAcheron https://github.com/NeoAcheron/midea-ac-py (Cloud Version bis Midea2Lox 1.1) . Vielen Dank dafür, ohne dieses Plugin hätte das nicht funktioniert.
Für die Steuerung über LAN (ab Midea2Lox V2.0) hat mac_zhou mit msmart https://github.com/mac-zhou/midea-msmart großartige leistung geleistet. Danke dafür! (Thanks mac-zhou!)

# Installation:
Plugin herunterladen und im Pluginmanager des Loxberry installieren.
Anschließend gewünschten Empfangsport angeben,danach kann über start der Service gestartet werden.

Das Plugin übernimmt die Kommunikation zwischen Midea und Loxberry.Auf dem Loxberry läuft ein UDP Server, der bei Befehlseingang diese an Midea schickt. Der Aktuelle Status wird über die Virtuellen Eingänge des Loxberry direkt ausgegeben/geschalten,
daher müssen die Eingänge in Loxone genau den Wortlaut wie in der Beispielkonfig haben.Die Beispielkonfig für Loxone ist auch hier zu finden.

Weitere Infos sind unter https://www.loxwiki.eu/display/LOXBERRY/Midea2Lox zu finden

Ab Midea2Lox V2.0 findet die kommunikation direkt über LAN ohne Cloud statt. 

# Midea 8370 Protocol / V3, bspw. EU-OSK103
Ab Midea2Lox V3.0 werden die neueren Sticks mit Protokoll Version 3 über LAN unterstützt.
Diese benötigen einen Token und K1 Key, der über die Android-App ausgelesen werden kann. Details dazu auch bei https://github.com/mac-zhou/midea-ac-py#how-to-get-token-and-k1 zu finden.
Es wird kein Android Handy benötigt, man kann die Key´s auch über einen Emulator entnehmen. Die Klimaanlagen mit V3 USB Stick müssen vorher mit der Midea App registriert werden, anschließend wird die App nicht mehr benötigt.

# Token und Key
Token und Key können ab V3.1 über die Cloud extrahiert werden. Dazu wird der Midea App zugang benötigt, bei dem die Klimaanlagen registriert sind. 
Es wird nur Token und Key abgefragt, die steuerung erfolgt dann lokal über LAN/Wlan
Details zur Loxone Konfig und weitere Infos sind im [LoxWiki](https://www.loxwiki.eu/display/LOXBERRY/Midea2Lox) zu finden
