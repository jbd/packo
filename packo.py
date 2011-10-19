#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2011 Jean-Baptiste Denis <jbd@jbdenis.net>

# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.


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

from __future__ import print_function
import pprint
import random

import sys
import os
import glob
import platform


major, minor, revision = platform.python_version_tuple()
if major == 2 and minor < 6:
    sys.stderr.write("You need python python >= 2.6 to run this program (3 years old).")
    sys.exit(1)



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
    results = [ list() for _ in range(pack)]
    sum_results = [0] * pack
    while len(items) > 0:
        item = items.pop()
        # we select the result list with the smaller sum...
        index = sum_results.index(min(sum_results)) 
        # ...and we add the item to it
        results[index].append(item)
        sum_results[index] += item[1]

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
                print("""Cannot read '%s'""" % fullname, file=sys.stderr)
                pass


def main():
    if len(sys.argv) < 3:
        print("usage:", sys.argv[0], "path packnum [packpattern]", file=sys.stderr)
        sys.exit(1)
    
    pathname = sys.argv[1]

    if not os.path.exists(pathname):
        print(pathname, "does not exist.", file=sys.stderr)
        sys.exit(1)
        
    packnum  = int(sys.argv[2])
    doout = len(sys.argv) == 4
    if doout:
        packpattern = sys.argv[3]
        collisions = glob.glob("%s*" % packpattern)
        if len(collisions) > 0:
            print("'%s' pattern match existing filenames, aborting." % packpattern, file=sys.stderr)
            sys.exit(1)


    files_sizes = [ (filename, size) for filename, size in walkdir(pathname) ]
    files_sizes.sort(key = lambda item: item[1]) # sort by size
    results = repartition(files_sizes, packnum)

    print("\n")

    for i,result in enumerate(results):
        packsize = sum(x[1] for x in result)
        if doout:
            outfile = file(packpattern + str(i), 'w')
            for name, _ in result:
                print(name, file=outfile)
            outfile.close()
        print("Pack %d: %s / %d files" % (i,human(packsize),len(result)))


if __name__ == '__main__':
    main()
