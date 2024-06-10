#!/usr/bin/perl -w

use strict;

my $start=0;

while(<>) {

	if ( m/<title>AccessibleComputing<\/title>/ ) {
		$start=1;
		print STDERR "AC detect\n";
	}

	if ( m/<title>George W. Campbell<\/title>/ ) {
		$start=1;
		print STDERR "GWC detect\n";
	}
	if ( m/<title>Archibald S. Clarke<\/title>/ ) {
		$start=1;
		print STDERR "GWC detect\n";
	}

	if ( m/<title>1978 European Badminton Championships<\/title>/ ) {
		$start=1;
		print STDERR "GWC detect\n";
	}
	if ( m/<title>Zebra moray<\/title>/ ) {
		$start=1;
		print STDERR "GWC detect\n";
	}
	if ( m/<title>A701 road<\/title>/ ) {
		$start=1;
		print STDERR "GWC detect\n";
	}
	if ( m/<title>Wikipedia - Text of Creative Commons Attribution-ShareAlike 3.0 Unported License<\/title>/ ) {
		$start=1;
		print STDERR "GWC detect\n";
	}
	if ( m/<title>Public holidays in Nicaragua<\/title>/ ) {
		$start=1;
		print STDERR "GWC detect\n";
	}
	if ( m/<title>Prudence and the Pill<\/title>/ ) {
		$start=1;
		print STDERR "GWC detect\n";
	}
	if ( m/<title>Pseudomonas resiniphila<\/title>/ ) {
		$start=1;
		print STDERR "GWC detect\n";
	}
	if ( m/<title>Tala, Chhattisgarh<\/title>/ ) {
		$start=1;
		print STDERR "TC detect\n";
	}
	if ( m/<title>Sigrid Alexandersen<\/title>/ ) {
		$start=1;
		print STDERR "Sigrid detect\n";
	}
	if ( m/<title>Salt Ash<\/title>/ ) {
		$start=1;
		print STDERR "Salt Ash detect\n";
	}
	if ( m/<title>2003 Copa AT&T<\/title>/ ) {
		$start=1;
		print STDERR "2003 Copa AT&T main article\n";
	}
	if ( m/#REDIRECT \[\[2003 Copa AT\&T\]\]/ ) {
		$start=1;
		print STDERR "2003 Copa AT&T main redirect\n";
	}
	if ( m/<title>The Fooo<\/title>/ ) {
		$start=1;
		print STDERR "The Fooo\n";
	}
	if ( m/<title>The Fooo Conspiracy<\/title>/ ) {
		$start=1;
		print STDERR "The Fooo\n";
	}

	if ( ! $start) {
		print $_;
	}

	if ( m/<page>/  && ( $start eq 1 )) {
		$start=0;
		print STDERR "off\n";
	}
}
