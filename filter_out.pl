#!/usr/bin/perl -w
#
# Removes duplicates, bad characters
#
# Version 2.0
#

use strict;

my $failed=0;

my $page="";

my %already=();

my @reject_list;

my $seen=0;

while( my $rej = <DATA> ) {
	chomp($rej);
	push(@reject_list,$rej);
}

print STDERR "Reject list @reject_list\n";

while(<>) {
	$page .= $_;

	if ( m/(<title>.+?:)(.+)<\/title>/) {

		my $res=$1;

		if ( grep { /\Q$res\E/ } @reject_list ) {
			print STDERR "$1$2 : ";
			print STDERR "Fail on reject list\n";	
			$failed=1;
		} else {
			#print STDERR "Okay\n";
		}

		if ( ord($2) > 127 ) {
			print STDERR "$1$2 : ";
			print STDERR "Fail binary code\n";	
			$failed=1;
		}
		if ( ord(substr($1,7)) > 127 ) {
			print STDERR "$1$2 : ";
			print STDERR "Fail binary code\n";	
		}
	}

	if (m/<title>George W. Campbell/) {
		$failed=1;
	}

	if (m/<title>Sow-Hsin Chen/) {
		$failed=1;
	}

	if (m/<title>(.+)<\/title>/) {
		if ( length($1) > 60 ) {
			print STDERR "Rejecting $1 as title length is too long\n";
			$failed=1;
		}
	}

	if (m/<title>(.+)<\/title>/) {

		my $title=$1;

		if ( exists($already{$title}) ) {
			print STDERR "Rejecting $title - already seen\n";
			$failed=1;
		}

		$already{$title}=1;

		if ( ord($title) > 127 ) {
			print STDERR "$title : ";
			print STDERR "Fail binary code\n";	
			$failed=1;
		}
	}

	# See if we want to reject this

	if (m/<\/page>/) {
		if ( ! $failed ) {
			print $page;
			if ( $seen % 10000 eq 0 ) {
				print STDERR "$seen articles\n";
			}
			$seen++;
		} else {
			print STDERR "Not allowing\n";
		}
		$page="";
		$failed=0;
	}

}

__DATA__
<title>Help:
<title>MediaWiki:
<title>Module:
<title>Book:
<title>UN/LOCODE:
<title>ISO 639:
<title>Draft:
<title>Portal:
<title>Template:
<title>File:
<title>Wikipedia:
<title>Category:
