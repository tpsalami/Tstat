#!/usr/bin/perl -w
###################################################################
# Set Variables
# copyright 2003 by matt hortop

########################COMMON IN LEGION CODE
srand;
use strict;
use CGI qw(:standard);
use LWP::UserAgent;
use Time::localtime;
use Time::Local;
use GD;
########################COMMON IN LEGION CODE
my $mailprog =  "/usr/lib/sendmail";
#my $basedir = "/home/306wd/www/";
my $basedir = "/home/content/m/k/h/mkhortop/html/tstat/";
my $localbasedir = "/data/306wd/tstat/";
my $filename = "index.html";
my $datafile = "tstatstats.hoe";
my $basePlotName = "tstat_base";

my $DB_COL_TOTAL = 14;
my $DB_COL_TIME = 1;
my $DB_COL_YEAR = 2;
my $DB_COL_MONTH = 3;
my $DB_COL_DAY = 4;
my $DB_COL_TEMP1 = 5; #inside
my $DB_COL_RH1 = 6; #inside
my $DB_COL_SETPOINT = 7;
my $DB_COL_TEMP2 = 8; #outside
my $DB_COL_TEMP3 = 9;
my $DB_COL_TEMP4 = 10;
my $DB_COL_RH2 = 11; #outside
my $DB_COL_RH3 = 12;
my $DB_COL_KWH = 13;
my $DB_COL_LIGHT = 14;

#mailproblem("does mailproblem work?");

###########
#vehicle Energy
my $vehicleEnergy_filename = "VehicleEnergyUsage.hoe";
my $vehicleEnergy_html_input = "VehicleEnergyInput.html";
my $vehicleEnergy_html_results = "VehicleEnergyHTML.html";

my $VE_COL_DATE = 0;
my $VE_COL_CARID = 1;
my $VE_COL_GALENERGY = 2;
my $VE_COL_ODOMETER = 3;
my $VE_COL_PRICEPER = 4;
my $VE_COL_COMMENTS = 9;
#
#############



my $cmtoffset=948825000;
my $sessionallowedsecs = 60 * 60 * 24; #1 day
#my $localtest = "/home/306wd/www/index.html";
my $localtest = $localbasedir . $filename;
###############################################
###FOR SWITCHING BETWEEN SYSTEMS IN TEST

my $LOCALTEST= 0;
if (open(FILE,$localtest)){

	#print "local mode\n";
	$basedir = $localbasedir;
	$LOCALTEST = 1;
	print "In LOCALTEST MODE \n\n\n";
	close(FILE);
}
# END TEST	
################################################################3
#
# TO DO
#


my $filetoopen = $basedir . $datafile;
my @olddata = ();

#get info from the web to backup the loss of system sensors



my $temperature = defined(param("t")) ? param("t") : "-999";
my $client = defined(param("c")) ? param("c") : "-999";
my $rh1 = defined(param("rh1")) ? param("rh1") : "-999";
my $dataonly = defined(param("dataonly")) ? param("dataonly") : 0;

my $rhOutside1 = defined(param("rho1")) ? param("rho1") : "-999";
my $temperatureOutside1 = defined(param("to1")) ? param("to1") : "-999";

my $adc2 = defined(param("adc2")) ? param("adc2") : -999;
my $adc3 = defined(param("adc3")) ? param("adc3") : -999;
my $adc4 = defined(param("adc4")) ? param("adc4") : -999;

#assuming that minimum data is the temperature, then when it is not present default to spitting out the last set of data
if($temperature> -100){
	#check if we need the web based info
	if(($rhOutside1 eq "-999") or ($temperatureOutside1 eq "-999")) {
		my($outsideStatus, $outsideTempBackup, $outsideRHbackup) = getWeatherInfo();

		if($rhOutside1 eq -999) {
			if($outsideStatus eq 0){ $rhOutside1 = $outsideRHbackup; }
			else {$rhOutside1 = "0";}
		}
		if($temperatureOutside1 eq -999) {
			if($outsideStatus eq 0){ $temperatureOutside1 = $outsideTempBackup;}
		}
	}



	my $hi_e = 0;
	my $heatindex1 = 0 ;
	#my $deletekey = defined(param("dk")) ? param("dk") : 0;

	my $nn =0;
	my $search_temp = "<!--temp here-->";
	my $search_updated = "<!--updated-->";

	my $nowtime = time() - $cmtoffset;

	
	

	my $datestuff = getDateString();
	my @datestuff = split(/ /,$datestuff);
	my $stringtowrite = "";
	for (my $nn=1; $nn<= $DB_COL_TOTAL; $nn++) {
		if($nn=$DB_COL_TIME) { $stringtowrite = $stringtowrite . $nowtime . "|"; }
		if($nn=$DB_COL_YEAR) { $stringtowrite = $stringtowrite . $datestuff[0] . "|"; }
		if($nn=$DB_COL_MONTH){ $stringtowrite = $stringtowrite . $datestuff[1] . "|"; }
		if($nn=$DB_COL_DAY) { $stringtowrite = $stringtowrite . $datestuff[2] . "|"; }
		if($nn=$DB_COL_TEMP1) { $stringtowrite = $stringtowrite . $temperature . "|"; }
		if($nn=$DB_COL_RH1) { $stringtowrite = $stringtowrite . $rh1 . "|"; }
		if($nn=$DB_COL_SETPOINT) { $stringtowrite = $stringtowrite . "0|"; }
		if($nn=$DB_COL_TEMP2) { $stringtowrite = $stringtowrite . $temperatureOutside1 . "|"; }
		if($nn=$DB_COL_TEMP3) { $stringtowrite = $stringtowrite . "0|"; }
		if($nn=$DB_COL_TEMP4) { $stringtowrite = $stringtowrite . "0|"; }
		if($nn=$DB_COL_RH2) { $stringtowrite = $stringtowrite . $rhOutside1 . "|"; }
		if($nn=$DB_COL_RH3) { $stringtowrite = $stringtowrite . $adc2 . "|"; }
		if($nn=$DB_COL_KWH) { $stringtowrite = $stringtowrite . $adc3 . "|"; }
		if($nn=$DB_COL_LIGHT) { $stringtowrite = $stringtowrite . $adc4 . "|"; }
	}
  
	$filetoopen = $basedir . $datafile;
	if(open(FILE,"$filetoopen")){
		@olddata = <FILE>;
		close(FILE);
		$olddata[@olddata] = $stringtowrite . "\n";
		plotData(\@olddata);
	}
	else {
		mailproblem("1 cannot open $filetoopen\n");
	}
	#now store all the information

	if(open(FILE,">>$filetoopen")) {
		print FILE $stringtowrite . "\n";
		close(FILE);
	}
	else {
		if($client == 0) {
			mailproblem("3 cannot open $filetoopen\n");
		}
	}


	$filetoopen = $basedir . $filename;
	if(open(FILE,"$filetoopen")){
		@olddata = <FILE>;
		close(FILE);
		open(FILE,">$filetoopen");
		
		my $heatindex = calcHeatIndex($temperature, $rh1);
		for($nn=0; $nn<@olddata; $nn++) {
			if($olddata[$nn] =~ /$search_temp/){
				print FILE "$olddata[$nn]";
				print FILE "$temperature °F @ $rh1 \%rH\n";
				$nn++;
			}
			elsif ($olddata[$nn] =~ /$search_updated/) {
				print FILE "$olddata[$nn]";
				my $datedata = getDateString();
				my $timedata = getTimeString();
				print FILE "$datedata at $timedata\n";
				$nn++;
			}
			else {
				print FILE "$olddata[$nn]";
			}
		}
		close(FILE);
		if($client == 1) {
			print "Location: http://www.306wd.com/tstat\n\n";
		}
		else {
			print "1";
		}
	}
	else {
		mailproblem("2 cannot open $filetoopen");
		if($client == 1) {
			print "Location: http://www.306wd.com/tstat\n\n";
		}
		else {
			print "0";
		}
	}



	#plot the data

		
		

	print "Location: http://www.306wd.com/tstat\n\n";
}
else {
  $filetoopen = $basedir . $datafile;
	if(open(FILE,"$filetoopen")){
		@olddata = <FILE>;
		close(FILE);
		my $datastring = $olddata[@olddata-1];
		unless ($dataonly gt 0){
			print "Content-type: text/html\n\n";
		}
		print $datastring;
	}

}

exit;

###################################################################
sub mailproblem { 
	if ($LOCALTEST) {
		print STDERR "\n     MAILPROBLEM CALLED:\n";
		print STDERR "$_[0]\n\n";
	} 
	else {
		my $recipient = 'webmaster_backdoor@306wd.com';
		open (MAIL, "|$mailprog -t" ) || die "Can't open $mailprog!\n";
	    print MAIL "To: $recipient\n";
		print MAIL "Subject: Problem with tstat.cgi\n";
		print MAIL "\n $_[0] \n";
		close(MAIL);
	}
} # end sub mail problem

sub getDateString {
	#return string of date in format yyyymmdd
	my $tm = localtime;
	my $year = 1900 + $tm->year;
	my $mon = $tm->mon;
	my $day = $tm->mday;
	$mon=$mon+1;
	if($mon<10) {
		$mon = "0" . $mon;
	}
	if($day<10) {		$day = "0" . $day;
	}	
	
	return $year . " " . $mon . " " . $day;
}

sub getTimeString {	
	my $tm  = localtime;
	my $m = "am";
	my $hours = 3 + $tm->hour;
	if($hours > 11) {
		$m = "pm";
	}
	
	if($hours > 12) {
		$hours = $hours - 12;
	}
	my $min = $tm->min;
	if($min<10) {
		$min = "0" . $min;
	}	
	my $sec = $tm->sec;
	if($sec<10) {
		$sec = "0" . $sec;
	}	
	return $hours . ":" . $min . ":" . "$sec" . " $m";
}

sub makePlot {
	#take in file contents
	my @input = defined(@_) ? @_ : (0,0);
	my @dataset1 = (0);
	my @dataset2 = (0);
	
	my @line = split(/|/,$input[0]);
	my $initial= $line[1];
	my $initialsetpoint=$line[2];
	for (my $i=1; $i<@input; $i++){
		@line = split(/\|/,$input[$i]);
		$dataset1[$i]=$line[1];
		$dataset2[$i]=$line[2];
	}
	plotData(@dataset1, @dataset2);
	return 1;
}



sub plotData {
	#comes in as pointer to text dataset (divided by |'s), pointer to array of columns to be plotted, pointer to array of titles, column of the x-axis
	my @baseVars = ($DB_COL_TEMP1 - 1, $DB_COL_RH1 - 1);
	my @baseTitles = ("Inside Temp","\%rH");
	my $dataSetText = defined($_[0]) ? $_[0] : 0;
	my $plotsets = defined($_[1]) ? $_[1] : \@baseVars;
	my $titles = defined($_[2]) ? $_[2] : \@baseTitles;
	my $xaxiscolumn = defined($_[3]) ? $_[3] : 0;
	
	my @dataset = ();

	#these are the margins and size of the plot
	my $plotSizeHorizonal = 300;
	my $plotSizeVertical = 200;
	my $maxplotsize=250;
	my $leftMargin=40;
	my $rightMargin=10;
	my $highLevel=10;
	my $lowLevel=180;
	my $stepsize=1;
	
	my $leftside = $leftMargin;
	my $rightside = $plotSizeHorizonal - $rightMargin;
		
	my $maxwidth = $rightside - $leftside;
	
	# create a new image
	my $im = new GD::Image($plotSizeHorizonal,$plotSizeVertical);
	
	my $pp = 0;
	my $sp = @$dataSetText - $maxplotsize;
	if ($sp < 0) { $sp = 1; }
	
	my @line = split(/|/,$$dataSetText[0]);
	my $numberOfRows = @$dataSetText;
	for (my $i=0; $i<$numberOfRows; $i++){
		@line = split(/\|/,$$dataSetText[$i]);
		for(my $j=0; $j<@line; $j++) {
			$dataset[$i][$j] = $line[$j];
		}
	}
	my $numberOfCols = @line;
	
		
	if($LOCALTEST) {
		print("working\n\n");
	}
	
	# allocate some colors
	my $white = $im->colorAllocate(255,255,255);
	my $black = $im->colorAllocate(0,0,0);       
	my $red = $im->colorAllocate(255,0,0);      
	my $blue = $im->colorAllocate(0,0,255);
	my $green = $im->colorAllocate(0,255,0);
	my $violet = $im->colorAllocate(200,0,200);
	my $grey = $im->colorAllocate(133,133,133);
	my $lightgrey = $im->colorAllocate(190,190,190);
	my @colorOrder = ($red, $blue, $green, $violet);

	my $minValue = 50;
	my $maxValue = 100;
	my $scale=($lowLevel-$highLevel)/($maxValue-$minValue);
	my $nullLevel = $lowLevel;# - ($highLevel - $scale * $minValue);
	
	$im->line($leftside,$lowLevel,$leftside,$highLevel,$black);		#vertical axis
	
	#tic values
	my $yaxisTicValue1 = 50;
	my $yaxisTicValue2 = 60;
	my $yaxisTicValue3 = 65;
	my $yaxisTicValue4 = 70;
	my $yaxisTicValue5 = 75;
	my $yaxisTicValue6 = 80;
	my $yaxisTicValue7 = 85;	
	my $yaxisTicValue8 = 90;
	my $yaxisTicValue9 = 100;
	
	#tic marks
	$im->line($leftside,$lowLevel - (($yaxisTicValue1-$minValue)*$scale),$leftside+6,$lowLevel - (($yaxisTicValue1-$minValue)*$scale),$black);
	$im->line($leftside,$lowLevel - (($yaxisTicValue2-$minValue)*$scale),$leftside+6,$lowLevel - (($yaxisTicValue2-$minValue)*$scale),$black);
	$im->line($leftside,$lowLevel - (($yaxisTicValue3-$minValue)*$scale),$leftside+6,$lowLevel - (($yaxisTicValue3-$minValue)*$scale),$black);
	$im->line($leftside,$lowLevel - (($yaxisTicValue4-$minValue)*$scale),$leftside+6,$lowLevel - (($yaxisTicValue4-$minValue)*$scale),$black);
	$im->line($leftside,$lowLevel - (($yaxisTicValue5-$minValue)*$scale),$leftside+6,$lowLevel - (($yaxisTicValue5-$minValue)*$scale),$black);
	$im->line($leftside,$lowLevel - (($yaxisTicValue6-$minValue)*$scale),$leftside+6,$lowLevel - (($yaxisTicValue6-$minValue)*$scale),$black);
	$im->line($leftside,$lowLevel - (($yaxisTicValue7-$minValue)*$scale),$leftside+6,$lowLevel - (($yaxisTicValue7-$minValue)*$scale),$black);
	$im->line($leftside,$lowLevel - (($yaxisTicValue8-$minValue)*$scale),$leftside+6,$lowLevel - (($yaxisTicValue8-$minValue)*$scale),$black);
	$im->line($leftside,$lowLevel - (($yaxisTicValue9-$minValue)*$scale),$leftside+6,$lowLevel - (($yaxisTicValue9-$minValue)*$scale),$black);
	
	#tic labels
	$im->string(GD::Font->Tiny,$leftside-25,$lowLevel - (($yaxisTicValue9-$minValue)*$scale)-2,"$yaxisTicValue9",$black);
	$im->string(GD::Font->Tiny,$leftside-25,$lowLevel - (($yaxisTicValue8-$minValue)*$scale)-2,"$yaxisTicValue8",$black);
	$im->string(GD::Font->Tiny,$leftside-25,$lowLevel - (($yaxisTicValue7-$minValue)*$scale)-2,"$yaxisTicValue7",$black);
	$im->string(GD::Font->Tiny,$leftside-25,$lowLevel - (($yaxisTicValue6-$minValue)*$scale)-2,"$yaxisTicValue6",$black);
	$im->string(GD::Font->Tiny,$leftside-25,$lowLevel - (($yaxisTicValue5-$minValue)*$scale)-2,"$yaxisTicValue5",$black);
	$im->string(GD::Font->Tiny,$leftside-25,$lowLevel - (($yaxisTicValue4-$minValue)*$scale)-2,"$yaxisTicValue4",$black);
	$im->string(GD::Font->Tiny,$leftside-25,$lowLevel - (($yaxisTicValue3-$minValue)*$scale)-2,"$yaxisTicValue3",$black);
	$im->string(GD::Font->Tiny,$leftside-25,$lowLevel - (($yaxisTicValue2-$minValue)*$scale)-2,"$yaxisTicValue2",$black);
	$im->string(GD::Font->Tiny,$leftside-25,$lowLevel - (($yaxisTicValue1-$minValue)*$scale)-2,"$yaxisTicValue1",$black);

	#horizontal lines
#	$im->line($leftside,$lowLevel - (($yaxisTicValue1-$minValue)*$scale),$rightside,$lowLevel - (($yaxisTicValue1-$minValue)*$scale),$lightgrey);	
#	$im->line($leftside,$lowLevel - (($yaxisTicValue2-$minValue)*$scale),$rightside,$lowLevel - (($yaxisTicValue2-$minValue)*$scale),$lightgrey);	
	$im->line($leftside,$lowLevel - (($yaxisTicValue3-$minValue)*$scale),$rightside,$lowLevel - (($yaxisTicValue3-$minValue)*$scale),$lightgrey);	
#	$im->line($leftside,$lowLevel - (($yaxisTicValue4-$minValue)*$scale),$rightside,$lowLevel - (($yaxisTicValue4-$minValue)*$scale),$lightgrey);	
	$im->line($leftside,$lowLevel - (($yaxisTicValue5-$minValue)*$scale),$rightside,$lowLevel - (($yaxisTicValue5-$minValue)*$scale),$lightgrey);	
#	$im->line($leftside,$lowLevel - (($yaxisTicValue6-$minValue)*$scale),$rightside,$lowLevel - (($yaxisTicValue6-$minValue)*$scale),$lightgrey);	
	$im->line($leftside,$lowLevel - (($yaxisTicValue7-$minValue)*$scale),$rightside,$lowLevel - (($yaxisTicValue7-$minValue)*$scale),$lightgrey);	
#	$im->line($leftside,$lowLevel - (($yaxisTicValue8-$minValue)*$scale),$rightside,$lowLevel - (($yaxisTicValue8-$minValue)*$scale),$lightgrey);	
#	$im->line($leftside,$lowLevel - (($yaxisTicValue9-$minValue)*$scale),$rightside,$lowLevel - (($yaxisTicValue9-$minValue)*$scale),$lightgrey);	
									
	$im->line($leftside+15,$highLevel+2,$leftside+22,$highLevel+2,$red);
	$im->line($leftside+15,$highLevel+12,$leftside+22,$highLevel+12,$blue);
	$im->string(GD::Font->Tiny,$leftside+25,$highLevel,"Temp",$red);
	$im->string(GD::Font->Tiny,$leftside+25,$highLevel+10,"\%rH",$blue);

	
	#$im->line($leftside,$nullLevel,$leftside+1,$nullLevel-$dataset1[$sp],$red);
	my $oo=0;
	for (my $ii=$sp; $ii<$numberOfRows; $ii++){
		$pp = $ii - $sp;
		for(my $jj=0; $jj<@$plotsets; $jj++) {
			#print "ds:" . $dataset[$ii-1][$$plotsets[$jj]]. "     total " . ($lowLevel-(($dataset[$ii-1][$$plotsets[$jj]]-50)*$scale)) . "\n";
			$im->line($leftside+$pp,$lowLevel - (($dataset[$ii-1][$$plotsets[$jj]]-$minValue)*$scale),$leftside+1+$pp,$lowLevel - (($dataset[$ii][$$plotsets[$jj]]-$minValue)*$scale),$colorOrder[$jj]);
		}
	}

	my $graphname = $basedir . $basePlotName . ".png";
	if(open(FILE, ">$graphname")){
		binmode FILE;
		print FILE $im->png;
		close(FILE);
	}
	else {
		mailproblem("cannot open $graphname\n");
	}

	return 1;
}



sub limitdecimal {
	#pass number, number of points
	my $raw = defined($_[0]) ? $_[0] : 0.0;
	my $dec = defined($_[1]) ? $_[1] : 2;
	
	my @after = (0,0,0,0);
	my @pieces = split(/\./,$raw);
	if(@pieces>1){
		@after = split(//,$pieces[1]);
	}
	my $i = 0;

	if($dec < 1) {
		return $pieces[0];
	}
	else {
		my $chunk = $after[0];
		if($dec > 1) {
			if($dec <= @after){
				for($i = 1; $i<$dec; $i++) { $chunk = $chunk . $after[$i]; }
			}
			else {
				for($i = 1; $i<@after; $i++) {
					$chunk = $chunk . $after[$i];
				}
				for ($i = @after; $i < $dec; $i++) {
					$chunk = $chunk . "0";
				}
			}
		}
		return $pieces[0] . "." . $chunk;
	}
}

sub calcHeatIndex {
	#inputs T, Rh
	my $T = defined($_[0]) ? $_[0] : 0;
	my $rh = defined($_[1]) ? $_[1] : 0;
	
	my $order0 = 16.923;
	my $order1 = .185212*$T + 5.37941*$rh - .100254*$T*$rh;
	my $order2 = .00941695*$T*$T + .00728898*$rh*$rh + .000345372*$T*$T*$rh -.000814971*$T*$rh*$rh + .0000102102*$T*$T*$rh*$rh;
	my $order3 = -.000038646*$T*$T*$T + .0000291583*$rh*$rh*$rh + .00000142721*$T*$T*$T*$rh + .000000197483*$T*$rh*$rh*$rh - .000000218429*$T*$T*$T*$rh*$rh + .000000000843296*$T*$T*$rh*$rh*$rh -.00000000004819*$T*$T*$T*$rh*$rh*$rh;
	
	return $order0 + $order1 + $order2 + $order3;
}

sub isanumber {
	my $sut = defined($_[0]) ? $_[0] : 1;
	
	$sut =~ s/^\s+//;
	$sut =~ s/\s+$//;
	
	if($sut =~ /^([+-]?)(?=\d|\.\d)\d*(\.\d*)?([Ee]([+-]?\d+))?$/) {
		return 1;
	}
	else {
		return 0;
	}
}

sub getWeatherInfo {
	
	my $url = "http://www.weather.gov/data/current_obs/KARB.xml";
		
	my $ua = LWP::UserAgent ->new();
	$ua->agent("Windows CE");				#say what i am
	my $req = HTTP::Request->new(GET=> $url);
	$req->referer("http://www.306wd.com/tstat");	#say who I am
	
	my $response = $ua->request($req);
	my $status = $response->status_line;
	my $stuff = $response->content();

	my @outstuff = split(/\n/,$stuff);

	my $temperature = "none";
	my $humidity = "none";
	my @temp = ();
	
	for(my $i=0; $i<@outstuff;$i++){
		my $searchstring = "<temp_f>";
		my $searchstring2 = "<relative_humidity>";

		if($outstuff[$i] =~ /$searchstring/i){
			@temp = split(/>/,$outstuff[$i]);
			@temp = split(/</,$temp[1]);
			$temperature = $temp[0];
		}
		
		if($outstuff[$i] =~ /$searchstring2/i){
			@temp = split(/>/,$outstuff[$i]);
			@temp = split(/</,$temp[1]);
			$humidity = $temp[0];
		}
	}
	chomp($temperature);
	chomp($humidity);
	$temperature =~ s/,//gs;
	$temperature = $temperature + 0;
	$humidity = $humidity + 0;
	if (isanumber($temperature) and isanumber($humidity)) {	return (0, $temperature,$humidity); }
	else { 
		mailproblem("temperature found is:$temperature\n");
		return (1, 0, 0);
	}
	
	
}



sub vehicleEnergy_processInput {
	my $date = defined(param("d")) ? param("d") : "-1";
	my $carid = defined(param("car")) ? param("car") : "-1";
	my $gallons = defined(param("gal")) ? param("gal") : "0";
	my $odometer = defined(param("odo")) ? param("odo") : "0";
	my $totalcost = defined(param("cost")) ? param("cost") : "0";
	my $comment = defined(param("comment")) ? param("comment") : "";

	if($date eq "-1") {
		$date = time() - $cmtoffset;
	}
	else {
		my @stuff = split($date,//);
		if(@stuff eq 6) {
			my $day = $stuff[2] . $stuff[3];
			my $month = $stuff[0] . $stuff[1]; 
			my $year = $stuff[4] . $stuff[5];
			$date = timelocal(0,0,0,$day,$month,$year);
		}
		else {
			$date = time() - $cmtoffset;
		}
	}
	
	$filetoopen = $basedir . $vehicleEnergy_filename;
	if(open(FILE,">$filetoopen")) {
		print "$date|$carid|$gallons|$odometer|$totalcost|0|0|0|0|$comment\n";
			
		close(FILE);
	}
	
	
	
	
	return 0;
}