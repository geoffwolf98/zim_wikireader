# zim_wikireader
Python scripts to extract html from zim file to feed into wikireader build process

Supplied :-
	extract.py
	filter_out.pl
	duplicate.pl
	remove.pl

==========

- Download wikipedia_en_all_nopic_*zim from  https://download.kiwix.org/zim/wikipedia/
- Seems to lag behind database backup by 1 to 2 months, I assume the processing required is immense given they do all the other zims too.

mkdir OUTPUT2

- This chokes so that only 70 processes extract.py run at once, and suspends the others
- I have a x99 board with 72 processes on it, so it runs lovely... ymmv
- I need to implement python queuing when I've learnt it

perl watcher.pl &


- So this takes the zim file, and sequentially processes each page, each page is html, but with lots of extra formatting that is not needed and bloats/breaks the wikireader build
- so it filters it out the best it can
- Apologies for awful python code


python3 extract.py wikipedia_en_all_nopic_2024-04.zim 1024 2024-04
	Parameters 
		ZIM file
		Number of workers
		File_name

- This creates 1024 "chunks" of files, because they get bigger when processed sequentially - due to how origianl wikipedia was built -
- ends up with 1 or 2 processes taking many more times than the average.  Hence the "sort -R" below makes it random and mostly makes each stream roughly the same size.

- The below assembles it into on ~50gb file

cd OUTPUT2

cat \`ls *.wiki | sort -R | xargs echo\` > full.txt

- Now do some tidying, as some articles still "break" wikireader build (usually to do with utf8 corruption).  Seems to vary between extracts

cat full.txt | grep -v "^    This article is issued from Wikipedia. The text is licensed under Creative Commons - Attribution - Sharealike. Additional terms may apply for the media files." |  perl filter_out.pl |  perl duplicate.pl |  perl remove.pl >> enwiki.xml

- Now feed enwiki.xml into the wikireader-master build process as normal

i.e.

export PATH=$PATH:/u01/WIKI/BUILD/wikireader-master/scripts/
./scripts/Run --verbose --machines=1 --parallel=64 --farm=1 en:::NO::::

make WORKDIR=work DESTDIR=image combine install

