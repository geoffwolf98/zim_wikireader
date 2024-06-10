#!/usr/bin/perl -w

use strict;

my @procs =();
my @wiki=();
my $top=();

while(1) {

	@wiki=();

	$top=`ps -ef| grep -E "python3 extract"|grep -v grep| grep -v /bin/sh|  sort -t"=" -k5 -n |awk '{print \$2}'|head -1`;

	chomp($top);

	print "Top proc is [$top]\n";


	if ( $top eq "" ) {
		$top="NONONO";
	}

	@procs = `ps -ef| grep -E "python3 extract"|grep -v grep| grep -v /bin/sh|  sort -t"=" -r |awk '{print \$2}'|grep -v $top`;

	my @procs2=($top);

	
	if ( $top ne "NONONO" ) {
		@procs=(@procs2,@procs);
	}


	my $c;


	for $c (@procs) {
		chomp($c);
		push(@wiki,$c);
	}

	#@wiki = sort {$a <=> $b} @wiki;

	my $top=70;

	my $i=0;

	my $running=0;
	my $stopped=0;

	for $a (@wiki) {
		if ( $i < $top ) {
			print "Run  : $a\n";
			system("kill -SIGCONT $a");
			$running++;
		} else {
			print "Stop : $a\n";
			system("kill -SIGSTOP $a");
			$stopped++;
		}
		$i++;
	}	
	print "Running:$running Stopped:$stopped\n";

	sleep 10;

	#print ".";

}
