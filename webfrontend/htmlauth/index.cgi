#!/usr/bin/perl

# Einbinden der LoxBerry-Module
use CGI;
use LoxBerry::System;
use LoxBerry::Web;
  
# Die Version des Plugins wird direkt aus der Plugin-Datenbank gelesen.
my $version = LoxBerry::System::pluginversion();
 
# Mit dieser Konstruktion lesen wir uns alle POST-Parameter in den Namespace R.
my $cgi = CGI->new;
$cgi->import_names('R');
# Ab jetzt kann beispielsweise ein POST-Parameter 'form' ausgelesen werden mit $R::form.
 
 
# Wir Übergeben die Titelzeile (mit Versionsnummer), einen Link ins Wiki und das Hilfe-Template.
# Um die Sprache der Hilfe brauchen wir uns im Code nicht weiter zu kümmern.
LoxBerry::Web::lbheader("Xiaomi Mi Flora Flower Monitor", "www.google.com", "help.html");
  
# Wir holen uns die Plugin-Config in den Hash %pcfg. Damit kannst du die Parameter mit $pcfg{'Section.Label'} direkt auslesen.
#my %pcfg;
#tie %pcfg, "Config::Simple", "$lbpconfigdir/miflora.cfg";
my $pcfg = new Config::Simple("$lbpconfigdir/miflora.cfg");
 

# Wir initialisieren unser Template. Der Pfad zum Templateverzeichnis steht in der globalen Variable $lbptemplatedir.

my $template = HTML::Template->new(
    filename => "$lbptemplatedir/index.html",
    global_vars => 1,
    loop_context_vars => 1,
    die_on_bad_params => 0,
	associate => $cgi,
);
  
# Jetzt lassen wir uns die Sprachphrasen lesen. Ohne Pfadangabe wird im Ordner lang nach language_de.ini, language_en.ini usw. gesucht.
# Wir kümmern uns im Code nicht weiter darum, welche Sprache nun zu lesen wäre.
# Mit der Routine wird die Sprache direkt ins Template übernommen. Sollten wir trotzdem im Code eine brauchen, bekommen
# wir auch noch einen Hash zurück.
my %L = LoxBerry::System::readlanguage($template, "language.ini");

my $lastdata;

# ---------------------------------------------------
# Save settings to config file
# ---------------------------------------------------
if ($R::btnSave)
{
	$pcfg->param('MIFLORA.ENABLED', $R::chkPluginEnabled);
	$pcfg->param('MIFLORA.MINISERVER', $R::selMiniServer);
	$pcfg->param('MIFLORA.UDPPORT', $R::txtMsUDPPort);
	$pcfg->param('MIFLORA.POLLFREQUENCY', $R::selPollFrequency);
	$pcfg->param('MIFLORA.LOCALTIME', $R::chkLocaltime);


	$pcfg->save();
}


# ---------------------------------------------------
# Start manual poll
# ---------------------------------------------------
if ($R::btnPoll)
{
	print "DEBUG: manual poll $lbpbindir/miflora.py";

	system("(/usr/bin/python3 -u $lbpbindir/miflora.py) &");

	if (-e "$lbpdatadir/lastdata.dat")
	{
		open my $lastdatahandle, '>', "$lbpdatadir/lastdata.dat" or die "Can't open file $!";

		$lastdata = $L{'MIFLORA.txtPollingMessage'};

		print $lastdatahandle $L{'MIFLORA.txtPollingMessage'};

		close $lastdatahandle;
	}
}

else
{
	# ---------------------------------------------------
	# Read last data if exists
	# ---------------------------------------------------
	

	if (-e "$lbpdatadir/lastdata.dat")
	{
		open my $lastdatahandle, '<', "$lbpdatadir/lastdata.dat" or die "Can't open file $!";

		$lastdata = do { local $/; <$lastdatahandle> };
	}
}




# ---------------------------------------------------
# Control for "frmStart" Form
# ---------------------------------------------------
my $frmStart = $cgi->start_form(
      -name    => 'MiFloraPlugIn',
      -method => 'POST',
  );
$template->param( frmStart => $frmStart );


# ---------------------------------------------------
# Control for "frmEnd" Form
# ---------------------------------------------------
my $frmEnd = $cgi->end_form();
$template->param( frmEnd => $frmEnd );


# ---------------------------------------------------
# Control for "chkPluginEnabled" Flipswitch
# ---------------------------------------------------
@values = ('1', '0' );
%labels = (
      '1' => 'On',
      '0' => 'Off',
  );
my $chkPluginEnabled = $cgi->popup_menu(
      -name    => 'chkPluginEnabled',
      -values  => \@values,
      -labels  => \%labels,
      -default => '1',
  );
$template->param( chkPluginEnabled => $chkPluginEnabled );


# ---------------------------------------------------
# Control for "selMiniServer" Dropdown
# ---------------------------------------------------
my %miniservers = LoxBerry::System::get_miniservers();

my @miniserverarray;
my %miniserverhash;
my $i = 1;

foreach my $ms (sort keys %miniservers)
{
	push @miniserverarray, "MINISERVER$ms";

	$miniserverhash{"MINISERVER$ms"} = $miniservers{$ms}{Name};

	$i++;
}

my $selMiniServer = $cgi->popup_menu(
      -name    => 'selMiniServer',
      -values  => \@miniserverarray,
      -labels  => \%miniserverhash,
      -default => $pcfg->param('MIFLORA.MINISERVER'),
  );
$template->param( selMiniServer => $selMiniServer );


# ---------------------------------------------------
# Control for "txtMsUDPPort" Textfield
# ---------------------------------------------------
my $txtMsUDPPort = $cgi->textfield(
      -name    => 'txtMsUDPPort',
      -default => $pcfg->param('MIFLORA.UDPPORT'),
  );
$template->param( txtMsUDPPort => $txtMsUDPPort );


# ---------------------------------------------------
# Control for "chkLocaltime" Flipswitch
# ---------------------------------------------------
@values = ('1', '0' );
%labels = (
      '1' => 'On',
      '0' => 'Off',
  );
my $chkLocaltime = $cgi->popup_menu(
      -name    => 'chkLocaltime',
      -values  => \@values,
      -labels  => \%labels,
      -default => '1',
  );
$template->param( chkLocaltime => $chkLocaltime );


# ---------------------------------------------------
# Control for "btnSave" Button
# ---------------------------------------------------
my $btnSave = $cgi->submit(
      -name    => 'btnSave',
      -value => $L{'MIFLORA.btnSave'},
  );
$template->param( btnSave => $btnSave );


# ---------------------------------------------------
# Control for "btnPoll" Button
# ---------------------------------------------------
my $btnPoll = $cgi->submit(
      -name    => 'btnPoll',
      -value => $L{'MIFLORA.btnPoll'},
  );
$template->param( btnPoll => $btnPoll );


# ---------------------------------------------------
# Control for "selPollFrequency" Dropdown
# ---------------------------------------------------
@values = ('1', '2', '4', '8', '12', '24' );
%labels = (
      '1' => $L{'MIFLORA.selPollFrequency1h'},
      '2' => $L{'MIFLORA.selPollFrequency2h'},
      '4' => $L{'MIFLORA.selPollFrequency4h'},
      '8' => $L{'MIFLORA.selPollFrequency8h'},
      '12' => $L{'MIFLORA.selPollFrequency12h'},
      '24' => $L{'MIFLORA.selPollFrequency24h'},
  );
my $selPollFrequency = $cgi->popup_menu(
      -name    => 'selPollFrequency',
      -values  => \@values,
      -labels  => \%labels,
      -default => $pcfg->param('MIFLORA.POLLFREQUENCY'),
  );
$template->param( selPollFrequency => $selPollFrequency );


# ---------------------------------------------------
# Control for "txtLastData" Textarea
# ---------------------------------------------------
my $txtLastData = $cgi->textarea(
      -name    => 'txtLastData',
      -rows	   => 10,
	  -columns => 50,
      -default => "$lastdata"
  );
$template->param( txtLastData => $txtLastData );


# ---------------------------------------------------
# Control for "btnRefresh" Button
# ---------------------------------------------------
my $btnRefresh = $cgi->defaults(
      -name    => 'btnRefresh',
      -value => $L{'MIFLORA.btnRefresh'},
  );
$template->param( btnRefresh => $btnRefresh );


# ---------------------------------------------------
# Localized Labels from language.ini
# ---------------------------------------------------
$template->param( lblPluginEnabled => $L{'MIFLORA.lblPluginEnabled'} );
$template->param( lblMiniServer => $L{'MIFLORA.lblMiniServer'} );
$template->param( lblMsUDPPort => $L{'MIFLORA.lblMsUDPPort'}  );
$template->param( lblPollFrequency => $L{'MIFLORA.lblPollFrequency'}  );
$template->param( lblLastData => $L{'MIFLORA.lblLastData'}  );
$template->param( lblLocaltime => $L{'MIFLORA.lblLocaltime'}  );


# Nun wird das Template ausgegeben.
print $template->output();
  
# Schlussendlich lassen wir noch den Footer ausgeben.
LoxBerry::Web::lbfooter();
