#! /usr/bin/env python

import logging

from tpt.core      import classify
from tpt.core      import Post
from tpt.core      import WebEntity
from tpt.threading import Pool
from tpt.web       import boards
from tpt.web       import Links

cache_file = 'bin/cache.bin'

num_threads = 32

logger = logging.getLogger('')
console_handler = logging.StreamHandler()

logger.setLevel(logging.INFO)
logger.addHandler(console_handler)

def find_hashes (*links):
    """
    Finds unique tripcodes.

    If no URLs are given it will attempt to scrape all of 4chan where tripcodes are
    allowed.
    """
    hashes = set()
    pool   = Pool(num_threads=num_threads)

    def work (unit):
        if isinstance(unit, Post):
            if unit.public:
                return unit.public.cipher
            return

        logger.info('Working %r', unit)
        for e in unit.process():
            pool.push(work, e)

    if not links:
        links = boards

    for link in map(classify, links):
        pool.push(work, link)
        pool.join()

    logger.info('Join complete, updating with results.')

    for e in pool.get_results():
        hashes.add(e)
    pool.close()

    return hashes

if __name__ == '__main__':
    import argparse
    import sys

    parser = argparse.ArgumentParser (
        description='Finds every unique regular tripcode.',
        epilog='if no links are given all of 4chan where tripcodes are allowed is scraped'
    )

    parser.add_argument (
        'outfile',
        type=argparse.FileType('w'),
        help='file to write the tripcodes, will be overwritten'
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

    parser.add_argument (
        '--offline',
        action='store_true',
        help='run in offline mode, only uses the web cache'
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

    if args.offline:
        WebEntity.webcache.set_offline_mode()

    WebEntity.webcache.load(cache_file)

    for h in find_hashes(*args.link):
        print >> args.outfile, h

    if not args.offline:
        WebEntity.webcache.dump(cache_file)
