#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
GitStats
--------

A program for displaying statics from a git repository.

Copyright (c) 2007-2014
Heikki Hokkanen <hoxu@users.sf.net> & others (see doc/AUTHOR)

License:  GPLv2 / GPLv3

--------
"""
# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------


from __future__ import print_function

# ---- Standard Libraries
import getopt

# ---- Custom Libraries
from gitstats.git_data_collector import GitDataCollector
from gitstats.get_functions import *
from gitstats.report_creators import HTMLReportCreator

# ---- Python version check
if sys.version_info < (2, 6):
    print("Python 2.6 or higher is required for gitstats.py", file=sys.stderr)
    sys.exit(1)


def usage():
    print("""
Usage: gitstats.py [options] <gitpath..> <outputpath>

Options:
-c key=value     Override configuration value

Default config values:
%s

Please see the manual page for more details.
""" % conf.conf)


class GitStats:
    def run(self, args_orig):
        optlist, args = getopt.getopt(args_orig, 'hc:', ["help"])
        for o,v in optlist:
            if o == '-c':
                key, value = v.split('=', 1)
                if key not in conf:
                    raise KeyError('no such key "%s" in config' % key)
                if isinstance(conf.conf[key], int):
                    conf.conf[key] = int(value)
                else:
                    conf.conf[key] = value
            elif o in ('-h', '--help'):
                usage()
                sys.exit()

        if len(args) < 2:
            usage()
            sys.exit(0)

        outputpath = os.path.abspath(args[-1])
        rundir = os.getcwd()

        try:
            os.makedirs(outputpath)
        except OSError:
            pass
        if not os.path.isdir(outputpath):
            print('FATAL: Output path is not a directory or does not exist')
            sys.exit(1)

        if not getgnuplotversion():
            print('gnuplot not found')
            sys.exit(1)

        print('Output path: %s' % outputpath)
        cachefile = os.path.join(outputpath, 'gitstats.py.cache')

        data = GitDataCollector()
        data.loadCache(cachefile)

        for gitpath in args[0:-1]:
            print('Git path: %s' % gitpath)

            prevdir = os.getcwd()
            os.chdir(gitpath)

            print('Collecting data...')
            data.collect(gitpath)

            os.chdir(prevdir)

        print('Refining data...')
        data.saveCache(cachefile)
        data.refine()

        os.chdir(rundir)

        print('Generating report...')
        report = HTMLReportCreator()
        report.create(data, outputpath)

        conf.exectime_internal = time.time() - conf.time_start
        print('Execution time %.5f secs, %.5f secs (%.2f %%) in external commands)'
              % (conf.exectime_internal, conf.exectime_external,
                 (100.0 * conf.exectime_external) / conf.exectime_internal))
        if sys.stdin.isatty():
            print('You may now run:')
            print()
            print('   sensible-browser \'%s\'' \
                  % os.path.join(outputpath, 'index.html').replace("'", "'\\''"))
            print()

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------


def main():
    """ Runs the script as a stand alone app """
    GitStats().run(sys.argv[1:])

# ----------------------------------------------------------------------------
# Name
# ----------------------------------------------------------------------------


if __name__ == '__main__':
    main()
