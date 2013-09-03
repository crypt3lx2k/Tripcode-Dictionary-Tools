#! /usr/bin/env python

import logging

from tpt.core      import classify
from tpt.core      import Thread
from tpt.core      import WebEntity
from tpt.threading import Pool
from tpt.web       import all_boards
from tpt.web       import Links

cache_file = 'bin/cache.bin'

num_threads = 32

logger = logging.getLogger('')
console_handler = logging.StreamHandler()

logger.setLevel(logging.INFO)
logger.addHandler(console_handler)

def build_cache (*links):
    """
    Builds up the internal WebEntity.webcache with a snapshot of the provided
    URLs.

    If no URLs are given, it will attempt to update the cache with a snapshot
    of the entirety of 4chan.
    """
    pool = Pool(num_threads=num_threads)

    def work (unit):
        logger.info('Working %r', unit)

        if isinstance(unit, Thread):
            unit.download()
        else:
            for e in unit.process():
                pool.push(work, e)

    if not links:
        links = all_boards

    for link in map(classify, links):
        pool.push(work, link)
        pool.join()

    logger.info('Join complete.')

if __name__ == '__main__':
    import argparse
    import sys

    parser = argparse.ArgumentParser (
        description='Finds every word that\'s a potential tripcode.',
        epilog='if no links are given all of 4chan is scraped'
    )

    parser.add_argument (
        'link', nargs='*',
        help='boards/pages/threads, may either be full URLs or names like /g/'
    )

    parser.add_argument (
        '--quiet',
        action='store_true',
        help='don\'t print progress to logfile'
    )

    parser.add_argument (
        '--debug',
        action='store_true',
        help='print debug information to logfile'
    )

    parser.add_argument (
        '--logfile',
        metavar='file', type=argparse.FileType('w'), default=sys.stderr,
        help='where to log progress/errors, defaults to stderr'
    )

    parser.add_argument (
        '--cache-file',
        metavar='file', type=str, default=cache_file,
        help='which file to use as cache, defaults to {}'.format(cache_file)
    )

    parser.add_argument (
        '--https',
        action='store_true',
        help='use HTTPS instead of HTTP'
    )

    parser.add_argument (
        '--threads',
        metavar='n', type=int, default=num_threads,
        help='how many threads to use, defaults to {}'.format(num_threads)
    )

    args = parser.parse_args()

    if args.quiet and args.debug:
        print >> sys.stderr, 'both --quiet and --debug set'
        exit(1)

    if args.quiet:
        logger.setLevel(logging.WARNING)

    if args.debug:
        logger.setLevel(logging.DEBUG)

    if args.logfile is not sys.stderr:
        logger.removeHandler(console_handler)
        logger.addHandler (
            logging.StreamHandler(args.logfile)
        )

    cache_file = args.cache_file

    if args.https:
        Links.scheme = 'https'

    num_threads = args.threads

    WebEntity.webcache.load(cache_file)
    build_cache(*args.link)
    WebEntity.webcache.dump(cache_file)
