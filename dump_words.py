#! /usr/bin/env python

from tdt.core      import classify
from tdt.core      import Thread
from tdt.threading import Pool
from tdt.web       import all_boards
from tdt.web.html  import sanitize

from common import logger
from common import parameters

def find_words (*links):
    """
    Finds words.

    If no URLs are given it will attempt to scrape all of 4chan.
    """
    import re

    words = set()
    pool  = Pool(num_threads=parameters.num_threads)

    word_pattern = re.compile(r'([^\s\#]+)')

    def work (unit):
        logger.info('working %r', unit)

        if isinstance(unit, Thread):
            thread = unit.download_and_decode()
            words  = set()

            for post in thread['posts']:
                for field in ('name', 'email', 'sub', 'com', 'filename'):
                    contents = post.get(field, '')
                    contents = sanitize(contents).encode('utf8')

                    words.update(word_pattern.findall(contents))

            return words

        for e in unit.process():
            pool.push(work, e)

    if not links:
        links = all_boards

    for link in map(classify, links):
        pool.push(work, link)
        pool.join()

    logger.info('Join complete, updating with results.')
    words.update(*pool.get_results())
    pool.close()

    return words

if __name__ == '__main__':
    import argparse

    from common import OfflineParser

    parser = OfflineParser (
        description='Finds every word that\'s a potential tripcode.',
        epilog='if no links are given all of 4chan is scraped'
    )

    parser.add_argument (
        'outfile',
        type=argparse.FileType('w'),
        help='file to write the words, will be overwritten'
    )

    parser.add_argument (
        'link', nargs='*',
        help='boards/pages/threads, may either be full URLs or names like /g/'
    )

    args = parser.parse_args()

    if parser.sanity_check(args):
        exit(1)

    parser.pre_process(args)
    for word in find_words(*args.link):
        print >> args.outfile, word
    parser.post_process(args)
