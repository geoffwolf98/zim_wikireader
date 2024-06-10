#!/usr/bin/perl -w

use strict;

my $failed=0;

my $page="";

my %already=();

while(<>) {
	$page .= $_;

	if (m/<title>(.+)<\/title>/) {

		my $title=$1;

		if ( exists($already{$title}) ) {
			print STDERR "Rejecting $title - already seen\n";
			$failed=1;
		}

		$already{$title}=1;
	}

	# See if we want to reject this

	if (m/<\/page>/) {
		if ( ! $failed ) {
			print $page;
		} else {
			print STDERR "Not allowing\n";
		}
		$page="";
		$failed=0;
	}

}
