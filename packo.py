#!/usr/bin/python

import pprint
import random
import sys
import os
import glob


def print_update(data):
    sys.stdout.write("\r\x1b[K"+data.__str__())
    sys.stdout.flush()


def human(num, power="Bytes"):
    powers = ["Bytes", "KBytes","MBytes","Gbytes","Tbytes"]
    while num >= 1000: #4 digits
        num /= 1024.0
        power = powers[powers.index(power)+1]
    return "%.1f %s" % (num,power)


def repartition(items, pack):
    # greedy repartion algorithm
    # this is an heuristic for an NP-complete problem
    # see http://en.wikipedia.org/wiki/Partition_problem
    results = list()
    sum_results = [0] * pack
    for i in xrange(pack):
	results.append(list())
    while True:
	item = items.pop()
	# we select the result list with the smaller sum...
	index = sum_results.index(min(sum_results)) 
	# ...and we add the item to it
        results[index].append(item)
        sum_results[index] += item[1]
	if len(items) == 0:
		return results


def files_number(pathname):
	numfiles = 0
	for _, _, files in os.walk(pathname):
		numfiles += len(files)
	return numfiles


def walkdir(pathname):
	total_files = files_number(pathname)
	currentsize = 0
	numfiles = 0
	for root, dirs, files in os.walk(pathname):
	    for name in files:
                fullname = os.path.join(root, name)
		numfiles += 1
		try:
		    sz = os.path.getsize(fullname)
		    currentsize += sz
		    print_update("%d/%d, %s" % (numfiles, total_files, human(currentsize)))
           	    yield fullname, sz
		except OSError:
                    print >>sys.stderr, """Cannot read '%s'""" % fullname
		    pass


def main():
    if len(sys.argv) < 4:
	print >>sys.stderr, "usage:", sys.argv[0], "path packnum packpattern"
	sys.exit(1)
    
    pathname = sys.argv[1]

    if not os.path.exists(pathname):
	print >>sys.stderr, pathname, "does not exist."
	sys.exit(1)
	
    packnum  = int(sys.argv[2])
    packpattern = sys.argv[3]

    collisions = glob.glob("%s*" % packpattern)
    if len(collisions) > 0:
	print >>sys.stderr, "'%s' pattern match existing filenames, aborting." % packpattern
	sys.exit(1)

    files_sizes = [ (filename, size) for filename, size in walkdir(pathname) ]
    files_sizes.sort(key = lambda item: item[1]) # sort by size
    results = repartition(files_sizes, packnum)

    for i,result in enumerate(results):
	packsize = sum(x[1] for x in result)
	outfile = file(packpattern + str(i), 'w')
	for name, _ in result:
	    print >>outfile, name
	outfile.close()
	print "Pack %d: %s" % (i,human(packsize))


if __name__ == '__main__':
    main()
