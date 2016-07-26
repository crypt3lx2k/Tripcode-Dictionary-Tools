#! /usr/bin/env python

from iwi.core      import classify
from iwi.core      import Post
from iwi.threading import Pool
from iwi.web       import boards

from common import logger
from common import parameters

def find_hashes (*links):
    """
    Finds unique tripcodes.

    If no URLs are given it will attempt to scrape all of 4chan where tripcodes
    are allowed.
    """
    hashes = set()
    pool   = Pool(num_threads=parameters.num_threads)

    def work (unit):
        if isinstance(unit, Post):
            if unit.public:
                return unit.public.cipher
            return

        logger.info('working %r', unit)
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

    from common import OfflineParser

    parser = OfflineParser (
        description='Finds every unique regular tripcode.',
        epilog=''.join ((
                'if no links are given all of 4chan where ',
                'tripcodes are allowed is scraped'
        ))
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

    args = parser.parse_args()

    if parser.sanity_check(args):
        exit(1)

    parser.pre_process(args)
    for h in find_hashes(*args.link):
        print >> args.outfile, h
    parser.post_process(args)
