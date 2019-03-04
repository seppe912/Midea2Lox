# Midea2Lox
Integration von Midea in Loxone

Dieses Loxberry Plugin ermöglicht eine kommunikation zwischen dem Loxberry/Loxone zu Midea Klimaanlagen.

Der Hauptpart, das Python3 Midea Script stammt von NeoAcheron https://github.com/NeoAcheron/midea-ac-py. Vielen Dank dafür, ohne dieses Plugin hätte das nicht funktioniert.

Installation:
Plugin herunterladen und im Pluginmanager des Loxberry installieren.
Anschließend die Zugangsdaten zur Midea API im Plugin eintragen. Danach muss ein Loxberry Neustart durchgeführt werden.
Das Plugin übernimmt die Kommunikation zwischen Midea und Loxberry. Es werden die Virtuellen Eingänge des Loxberry direkt geschalten,
daher müssen die Eingänge genau den Wortlaut wie in der Beispielkonfig haben.Die Beispielkonfig für Loxone ist auch hier zu finden.
