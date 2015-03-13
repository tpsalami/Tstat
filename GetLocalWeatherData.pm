package GetLocalWeatherData;
use strict;

use vars qw(@ISA @EXPORT $version
			$mailprog
			$versionNum	);

use Exporter;
use String::Approx qw(amatch);
@ISA = qw(Exporter);
@EXPORT = qw($mailprog
			$basedir);
#######################################################################################

$versionNum = "0.01";
$version = "Ver $versionNum Apr 25, 2005";

$mailprog =  "/usr/sbin/sendmail";


$ERROR_LOGIN1 = 1; #cannot open template file

$LOCALTEST = 0;
#######################################################################################




1;