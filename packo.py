#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Simple program from a very specific need. I needed to transfer multiple
terabytes of data using rsync. I can use multiple rsync in parallel to 
improve the throughput but i didn't want to think about what data each rsync
should transfer, that's why i wrote this program.

It gathers file size information recursively given a path and split the whole list
in set of approximatively equal size using a greedy algorithm
(http://en.wikipedia.org/wiki/Partition_problem) with a hack. Oups, i should say "heuristic".

Nothing magic or very interesting here :)
"""

import pickle
import pprint
import random
import sys
import os
import glob


def print_update(data):
    """
    Print 'data' on the same line as before
    """
    sys.stdout.write("\r\x1b[K"+data.__str__())
    sys.stdout.flush()


def human(num, power="Bytes"):
    """
    Stolen from the ps_mem.py project for nice size output :)
    """
    powers = ["Bytes", "KBytes","MBytes","Gbytes","Tbytes"]
    while num >= 1000: #4 digits
        num /= 1024.0
        power = powers[powers.index(power)+1]
    return "%.1f %s" % (num,power)


def repartition(items, pack):
    """
    greedy repartion algorithm that split items ( (filename, size) ) in 
    'pack' set of approximatively equal size.
    this is an heuristic for an NP-complete problem
    see http://en.wikipedia.org/wiki/Partition_problem

    This function takes a sorted item list and the number of set we want and returns
    a list of list of item (filename, size). The difference
    between the total amount of data in each of them should be acceptable.
    """
    results = [ list() for _ in xrange(pack)]
    sum_results = [0] * pack
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
    """
    Recursively count the number of files under 'pathname'
    """
    numfiles = 0
    for _, _, files in os.walk(pathname):
            numfiles += len(files)
            print_update("Counting files: %d" % numfiles)
    return numfiles


def walkdir(pathname):
    total_files = files_number(pathname)
    currentsize = 0
    memsizeapprox = 0
    numfiles = 0
    sizeofint = sys.getsizeof(int())
    for root, dirs, files in os.walk(pathname):
        for name in files:
            fullname = os.path.join(root, name)
            numfiles += 1
            try:
                if not os.path.isfile(fullname):
                    sz = 0
                else:
                    sz = os.path.getsize(fullname)
                # i should use sys.getsizeof here
                memsizeapprox += sys.getsizeof(fullname) + sizeofint
                currentsize += sz
                print_update("%d/%d, %s (Memsize: %s)" % (numfiles, total_files, human(currentsize), human(memsizeapprox)))
                yield fullname, sz
            except OSError:
                print >>sys.stderr, """Cannot read '%s'""" % fullname
                pass


def main():
    if len(sys.argv) < 3:
        print >>sys.stderr, "usage:", sys.argv[0], "path packnum [packpattern]"
        sys.exit(1)
    
    pathname = sys.argv[1]

    if not os.path.exists(pathname):
        print >>sys.stderr, pathname, "does not exist."
        sys.exit(1)
        
    packnum  = int(sys.argv[2])
    doout = len(sys.argv) == 4
    if doout:
        packpattern = sys.argv[3]
        collisions = glob.glob("%s*" % packpattern)
        if len(collisions) > 0:
            print >>sys.stderr, "'%s' pattern match existing filenames, aborting." % packpattern
            sys.exit(1)


    files_sizes = [ (filename, size) for filename, size in walkdir(pathname) ]
    #files_sizes.sort(key = lambda item: item[1]) # sort by size
    pickle.dump(files_sizes, open("files_sizes", 'w'))
    results = repartition(files_sizes, packnum)

    print "\n"

    for i,result in enumerate(results):
        packsize = sum(x[1] for x in result)
        if doout:
            outfile = file(packpattern + str(i), 'w')
            for name, _ in result:
                print >>outfile, name
            outfile.close()
        print "Pack %d: %s" % (i,human(packsize))


if __name__ == '__main__':
    main()
