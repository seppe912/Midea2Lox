#!/usr/bin/perl

use File::HomeDir;
use CGI qw/:standard/;
use Config::Simple;
use HTML::Entities;
use String::Escape qw( unquotemeta );
use warnings;
no strict "refs"; # we need it for template system
use LoxBerry::System;

my  $home = File::HomeDir->my_home;
my  $lang;
my  $installfolder;
my  $cfg;
my  $conf;
our $psubfolder;
our $template_title;
our $namef;
our $value;
our %query;
our $cache;
our $helptext;
our $language;	
our $select_language;
our $udp_port;	
our $debug;
our $select_debug;
our $MideaUser;
our $MideaPassword;
our $LoxberryIP  = LoxBerry::System::get_localip();
our $do;
our $midea2loxstatus;
our $miniserver;
our $select_ms;
our $savedata;

# Read Settings
$cfg             = new Config::Simple("$lbsconfigdir/general.cfg");
$installfolder   = $cfg->param("BASE.INSTALLFOLDER");
$lang            = $cfg->param("BASE.LANG");



print "Content-Type: text/html\n\n";

# Parse URL
foreach (split(/&/,$ENV{"QUERY_STRING"}))
{
  ($namef,$value) = split(/=/,$_,2);
  $namef =~ tr/+/ /;
  $namef =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
  $value =~ tr/+/ /;
  $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
  $query{$namef} = $value;
}

# Set parameters coming in - GET over POST
if ( !$query{'miniserver'} ) { if ( param('miniserver') ) { $miniserver = quotemeta(param('miniserver')); } else { $miniserver = $miniserver;  } } else { $miniserver = quotemeta($query{'miniserver'}); }
if ( !$query{'udp_port'} ) { if ( param('udp_port') ) { $udp_port = quotemeta(param('udp_port')); } else { $udp_port = "7013"; } } else { $udp_port = quotemeta($query{'udp_port'}); }
if ( !$query{'debug'} ) { if ( param('debug') ) { $debug = quotemeta(param('debug')); } else { $debug = "0";  } } else { $debug = quotemeta($query{'debug'}); }

if ( !$query{'MideaPassword'} ) { if ( param('MideaPassword')  ) { $MideaPassword = quotemeta(param('MideaPassword')); } else { $MideaPassword = $MideaPassword;  } } else { $MideaPassword = quotemeta($query{'MideaPassword'}); }
if ( !$query{'MideaUser'} ) { if ( param('MideaUser')  ) { $MideaUser = quotemeta(param('MideaUser')); } else { $MideaUser = $MideaUser;  } } else { $MideaUser = quotemeta($query{'MideaUser'}); }


# Figure out in which subfolder we are installed
$psubfolder = abs_path($0);
$psubfolder =~ s/(.*)\/(.*)\/(.*)$/$2/g;

# Save settings to config file
if (param('savedata')) {
	$conf = new Config::Simple("$lbpconfigdir/midea2lox.cfg");
	if ($debug ne 1) { $debug = 0 }
	$conf->param('MINISERVER', unquotemeta("MINISERVER$miniserver"));	
	$conf->param('UDP_PORT', unquotemeta($udp_port));
	$conf->param('DEBUG', unquotemeta($debug));		
    $conf->param('LoxberryIP', unquotemeta($LoxberryIP));
    $conf->param('MideaUser', unquotemeta($MideaUser));	
	$conf->param('MideaPassword', unquotemeta($MideaPassword));
    
	$conf->save();
	system ("$installfolder/system/daemons/plugins/$psubfolder restart");
}


# Parse config file
$conf = new Config::Simple("$lbpconfigdir/midea2lox.cfg");
$miniserver = encode_entities($conf->param('MINISERVER'));
$udp_port = encode_entities($conf->param('UDP_PORT'));
$debug = encode_entities($conf->param('DEBUG'));
$MideaPassword = encode_entities($conf->param('MideaPassword'));
$MideaUser = encode_entities($conf->param('MideaUser'));

# Set Enabled / Disabled switch
#

if ($debug eq "1") {
	$select_debug = '<option value="0">off</option><option value="1" selected>on</option>';
} else {
	$select_debug = '<option value="0" selected>off</option><option value="1">on</option>';
}


# ---------------------------------------
# Fill Miniserver selection dropdown
# ---------------------------------------
for (my $i = 1; $i <= $cfg->param('BASE.MINISERVERS');$i++) {
	if ("MINISERVER$i" eq $miniserver) {
		$select_ms .= '<option selected value="'.$i.'">'.$cfg->param("MINISERVER$i.NAME")."</option>\n";
	} else {
		$select_ms .= '<option value="'.$i.'">'.$cfg->param("MINISERVER$i.NAME")."</option>\n";
	}
}


# ---------------------------------------
# Start Stop Service
# ---------------------------------------
# Should Midea2Lox Server be started

if ( param('do') ) { 
	$do = quotemeta( param('do') ); 
	if ( $do eq "start") {
		system ("$installfolder/system/daemons/plugins/$psubfolder start");
	}
	if ( $do eq "stop") {
		system ("$installfolder/system/daemons/plugins/$psubfolder stop");
	}
	if ( $do eq "restart") {
		system ("$installfolder/system/daemons/plugins/$psubfolder restart");
	}
	if ( $do eq "discover") {
        system ("$installfolder/data/plugins/$psubfolder/discover.py &");
	}
}

# Title
$template_title = "Midea2Lox";
$midea2loxstatus = qx($installfolder/system/daemons/plugins/$psubfolder status);

# Create help page
$helptext = "<b>Hilfe</b><br>Wenn ihr Hilfe beim Einrichten benĂ¶tigt findet ihr diese im LoxWiki.";
$helptext = $helptext . "<br><a href='https://www.loxwiki.eu/display/LOXBERRY/Midea2Lox' target='_blank'>LoxWiki - Midea2Lox</a>";
$helptext = $helptext . "<br><br><b>Debug/Log</b><br>Um Debug zu starten, den Schalter auf on stellen und speichern.<br>Die Log-Datei kann hier eingesehen werden. ";
$helptext = $helptext . "<a href='/admin/system/tools/logfile.cgi?logfile=plugins/$psubfolder/midea2lox.log&header=html&format=template&only=once' target='_blank'>Log-File - Midea2Lox</a>";
$helptext = $helptext . "<br><br><b>Achtung!</b> Wenn Debug aktiv ist werden sehr viele Daten ins Log geschrieben. Bitte nur bei Problemen nutzen.";


# Currently only german is supported - so overwrite user language settings:
#$lang = "de";

# Load header and replace HTML Markup <!--$VARNAME--> with perl variable $VARNAME
open(F,"$lbstemplatedir/$lang/header.html") || die "Missing template system/$lang/header.html";
  while (<F>) {
    $_ =~ s/<!--\$(.*?)-->/${$1}/g;
    print $_;
  }
close(F);

# Load content from template
open(F,"$lbptemplatedir/$lang/content.html") || die "Missing template $lang/content.html";
  while (<F>) {
    $_ =~ s/<!--\$(.*?)-->/${$1}/g;
    print $_;
  }
close(F);

# Load footer and replace HTML Markup <!--$VARNAME--> with perl variable $VARNAME
open(F,"$lbstemplatedir/$lang/footer.html") || die "Missing template system/$lang/header.html";
  while (<F>) {
    $_ =~ s/<!--\$(.*?)-->/${$1}/g;
    print $_;
  }
close(F);

exit;
