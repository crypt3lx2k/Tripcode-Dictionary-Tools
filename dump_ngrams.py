#! /usr/bin/env python

import collections
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

def find_ngrams (n, *links):
    """
    Finds ngrams.

    If no URLs are given it will attempt to scrape all of 4chan.
    """
    import re

    ngrams = collections.Counter()
    pool   = Pool(num_threads=num_threads)

    nlbr_pattern = re.compile(r'(\<br\>)')
    html_pattern = re.compile(r'(\<.*?\>)')
    ref_pattern  = re.compile(r'(\>\>\d+)')

    token_pattern = re.compile(r'([A-Za-z0-9]\S*[A-Za-z0-9]|[A-Za-z0-9])')

    def sanitize (contents):
            contents = nlbr_pattern.sub('\n', contents)
            contents = html_pattern.sub('', contents)
            contents = Thread.html_parser.unescape(contents)
            contents = contents.encode('utf8')
            contents = ref_pattern.sub('', contents)

            return contents

    def generate_ngrams (tokens):
        return zip(*[tokens[i:] for i in range(n)])

    def work (unit):
        logger.info('Working %r', unit)

        if isinstance(unit, Thread):
            thread = unit.download_and_decode()
            ngrams = collections.Counter()

            for post in thread['posts']:
                contents = post.get('com', '')
                contents = sanitize(contents)

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
    import sys

    parser = argparse.ArgumentParser (
        description='Finds every word that\'s a potential tripcode.',
        epilog='if no links are given all of 4chan is scraped'
    )

    parser.add_argument (
        'outfile',
        type=argparse.FileType('w'),
        help='file to write the words, will be overwritten'
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

    ngrams = find_ngrams(args.n, *args.link)
    for ngram in sorted(ngrams, key=lambda s : ngrams[s], reverse=True):
        print >> args.outfile, '{} {}'.format (
            ' '.join(ngram), ngrams[ngram]
        )

    if not args.offline:
        WebEntity.webcache.dump(cache_file)
