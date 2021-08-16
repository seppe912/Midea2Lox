# Midea2Lox
Integration von Midea in Loxone

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

# Token und K1
- Download [LDplayer4](https://en.ldplayer.net/?from=en)
- Download [Midea app](https://www.mediafire.com/file/g38vhkdf4r3icbv/Midea-Air-gettoken-only-oversea.apk/file)  (thanks mac_zhou) --> in der App wurde das Loglevel erhöt um den Token zu bekommen.
- Download [platform-tools.zip](https://github.com/seppe912/Midea2Lox/files/6986140/platform-tools.zip)

--- Midea Klimaanlage muss bereits mit dem Midea Account (der APP) registriert sein und im WLAN angemeldet sein ---
1. Installiere und starte LDplayer4
2. LDplayer4--> Einstellungen(rechts oben) --> andere Einstellungen --> ADB Debug auf "open connection" ändern und speichern.
3. MideaApp installieren (rechts im Menü +APK / APK installieren --> Midea-Air-gettoken-only-oversea.apk)
4. platform-tools am PC entpacken und darin enthaltene "Midea get Key and K1.bat" starten
5. Midea App in LDplayer öffnen, mit Account anmelden.
6. Anschließend wird im cmd Fenster (platform-tools) die Device Informationen angezeigt. Diese können dann kopiert werden und müssen über Loxone an Midea2Lox zur steuerung von V3 Sticks mit gesendet werden.
Details zur Loxone Konfig und weitere Infos sind im [LoxWiki](https://www.loxwiki.eu/display/LOXBERRY/Midea2Lox) zu finden
