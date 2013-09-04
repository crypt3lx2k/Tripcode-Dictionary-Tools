#! /usr/bin/env python

import logging

from tdt.collections import SortedSet
from tdt.core        import classify
from tdt.core        import Post
from tdt.core        import WebEntity
from tdt.solving     import SQLSolver
from tdt.threading   import Pool
from tdt.web         import Links

cache_file = 'bin/cache.bin'

public_db = 'tripcodes/public.db3'
secure_db = 'tripcodes/secure.db3'

num_threads = 32

logger = logging.getLogger('')
console_handler = logging.StreamHandler()

logger.setLevel(logging.INFO)
logger.addHandler(console_handler)

def crack (*links):
    """
    Returns a list of Posts with cracked trips.

    Reads 4chan URLs, scrapes contents and attempts to crack the tripcodes found.
    If any posts were cracked the corresponding Post object is added to a list that
    is returned.

    The list is sorted by time of post.
    """
    posts = SortedSet()
    pool  = Pool(num_threads=num_threads)

    pub_solver = SQLSolver(public_db)
    sec_solver = SQLSolver(secure_db)

    def work (unit):
        if isinstance(unit, Post):
            return unit

        logger.info('working %r', unit)
        for e in unit.process():
            pool.push(work, e)

    for link in map(classify, links):
        pool.push(work, link)

    pool.join()
    logger.info('Join complete, updating with results.')

    posts.update(pool.get_results())
    pool.close()

    solved = []

    for e in sorted(posts, key = lambda post : post.time):
        if e.public:
            e.public.solve(pub_solver)
        if e.secure:
            e.secure.solve(sec_solver)
        if e.solved():
            solved.append(e)

    return solved

if __name__ == '__main__':
    import argparse
    import sys

    parser = argparse.ArgumentParser (
        description='Looks for tripcodes and cracks them.'
    )

    parser.add_argument (
        'link', nargs='+',
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

    parser.add_argument (
        '--public-tripcode-db',
        metavar='file', type=str, default=public_db,
        help='database of tripcodes, defaults to {}'.format(public_db)
    )

    parser.add_argument (
        '--secure-tripcode-db',
        metavar='file', type=str, default=secure_db,
        help='database of secure tripcodes, defaults to {}'.format(secure_db)
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

    public_db = args.public_tripcode_db
    secure_db = args.secure_tripcode_db

    WebEntity.webcache.load(cache_file)

    for e in crack(*args.link):
        print e

    if not args.offline:
        WebEntity.webcache.dump(cache_file)
