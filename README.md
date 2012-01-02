Please consider using [fpart](http://sourceforge.net/projects/fpart/) from [martymac](http://www.martymac.org/). Inspired by packo, [fpart](http://sourceforge.net/projects/fpart/) is a much more powerful tool, rewritten in C.
=============================================================================

Packo
=====

packo is a simple program from a very specific need : I needed to transfer multiple terabytes of data using rsync. In my environment (file server, connectivity, etc...) I can use multiple rsync in parallel to improve the throughput but didn't want to think about what data each rsync should transfer, that's why i wrote this program. it may be of interest to you.

It gathers file size information recursively given a path and splits the whole list in sets of approximatively equal size using [a greedy algorithm](http://en.wikipedia.org/wiki/Partition_problem) with a hack. Oups, i should say "heuristic".

By default, the program just output what it can do. For example, i want to build 5 sets of files from /usr/share/ :

	$ python packo.py /usr/share/doc 5
	11202/11202, 220.7 MBytes (Memsize: 1.1 MBytes)
	
	Pack 0: 44.1 MBytes / 2239 files
	Pack 1: 44.1 MBytes / 2240 files
	Pack 2: 44.1 MBytes / 2239 files
	Pack 3: 44.1 MBytes / 2240 files
	Pack 4: 44.1 MBytes / 2244 files

You can see that there are 11202 files here and the process requires approximatively 1.1 MBytes of memory to run. I print this information because my implementation is simple : i'm building the full files list in memory. It shouldn't be a concern for most usage. In this example, each set of files is about 44 MBytes.

If a want to write the list of files, i just add a filename name :

	$ python packo.py /usr/share/doc 5 mylistoffiles
	11202/11202, 220.7 MBytes (Memsize: 1.1 MBytes)
	
	Pack 0: 44.1 MBytes / 2239 files
	Pack 1: 44.1 MBytes / 2240 files
	Pack 2: 44.1 MBytes / 2239 files
	Pack 3: 44.1 MBytes / 2240 files
	Pack 4: 44.1 MBytes / 2244 files

It will write 5 files that can be used with the rsync '--files-from' option :

	$ head  mylistoffiles*
	==> mylistoffiles0 <==
	/usr/share/doc/ipython/manual/ipython.pdf.gz
	/usr/share/doc/gir1.2-gtk-3.0/changelog.gz
	...
	
	==> mylistoffiles1 <==
	/usr/share/doc/chromium-inspector/copyright
	/usr/share/doc/libgtk-3-0/changelog.gz
	...
	
	==> mylistoffiles2 <==
	/usr/share/doc/chromium/copyright
	/usr/share/doc/libgtk-3-bin/changelog.gz
	...
	
	==> mylistoffiles3 <==
	/usr/share/doc/chromium-browser/copyright
	/usr/share/doc/libgail-3-0/changelog.gz
	...
	
	==> mylistoffiles4 <==
	/usr/share/doc/xserver-common/changelog.gz
	/usr/share/doc/python2.6/html/genindex-all.html
	...

If you try to relaunch the command line, the program will exit to prevent overwriting :

	$ python packo.py /usr/share/doc 5 mylistoffiles
	'mylistoffiles0' already exists, aborting.

Nothing magic or very interesting here :)

Just for fun :

	$ python packo.py /usr 42 out
	112950/112950, 3.7 Gbytes (Memsize: 12.0 MBytes)
	
	Pack 0: 134.2 MBytes / 1 files
	Pack 1: 88.0 MBytes / 2592 files
	Pack 2: 88.0 MBytes / 2612 files
	Pack 3: 88.0 MBytes / 2655 files
	Pack 4: 88.0 MBytes / 2655 files
	Pack 5: 88.0 MBytes / 2655 files
	Pack 6: 88.0 MBytes / 2655 files
	Pack 7: 88.0 MBytes / 2655 files
	Pack 8: 88.0 MBytes / 6802 files
	...
	Pack 41: 88.0 MBytes / 2657 files
	
	$ cat out0
	/usr/share/icons/oxygen/icon-theme.cache
	$ ls -h /usr/share/icons/oxygen/icon-theme.cache
	$ ls -lh /usr/share/icons/oxygen/icon-theme.cache
	-rw-r--r-- 1 root root 135M Sep 30 20:54 /usr/share/icons/oxygen/icon-theme.cache


Dependencies
============

python>=2.6 (including python 3)

