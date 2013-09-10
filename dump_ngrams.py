#! /usr/bin/env python

import collections

from tdt.core      import classify
from tdt.core      import Thread
from tdt.threading import Pool
from tdt.web       import all_boards
from tdt.web.html  import sanitize

from common import logger
from common import parameters

def find_ngrams (n, *links):
    """
    Finds ngrams.

    If no URLs are given it will attempt to scrape all of 4chan.
    """
    import re

    ngrams = collections.Counter()
    pool   = Pool(num_threads=parameters.num_threads)

    token_pattern = re.compile(r'([A-Za-z0-9]\S*[A-Za-z0-9]|[A-Za-z0-9])')

    def generate_ngrams (tokens):
        return zip(*[tokens[i:] for i in range(n)])

    def work (unit):
        logger.info('working %r', unit)

        if isinstance(unit, Thread):
            thread = unit.download_and_decode()
            ngrams = collections.Counter()

            for post in thread['posts']:
                contents = post.get('com', '')
                contents = sanitize(contents).encode('utf8')

                tokens = token_pattern.findall(contents)
                tokens = [token.lower() for token in tokens]

                ngrams.update(generate_ngrams(tokens))

            return ngrams

        for e in unit.process():
            pool.push(work, e)

    if not links:
        links = all_boards

    for link in map(classify, links):
        pool.push(work, link)
        pool.join()

    logger.info('Join complete, updating with results.')

    for counter in pool.get_results():
        ngrams.update(counter)

    pool.close()

    return ngrams

if __name__ == '__main__':
    import argparse

    from common import OfflineParser

    parser = OfflineParser (
        description='Collects ngrams where the tokens are words.',
        epilog='if no links are given all of 4chan is scraped'
    )

    parser.add_argument (
        'outfile',
        type=argparse.FileType('w'),
        help='file to write the ngrams, will be overwritten'
    )

    parser.add_argument (
        'n',
        type=int,
        help='the n in n-gram, 1 gives unigrams, 2 bigrams, ...'
    )

    parser.add_argument (
        'link', nargs='*',
        help='boards/pages/threads, may either be full URLs or names like /g/'
    )

    args = parser.parse_args()

    if parser.sanity_check(args):
        exit(1)

    parser.pre_process(args)
    ngrams = find_ngrams(args.n, *args.link)
    for ngram in sorted(ngrams, key=lambda s : ngrams[s], reverse=True):
        print >> args.outfile, '{} {}'.format (
            ' '.join(ngram), ngrams[ngram]
        )
    parser.post_process(args)
