#! /usr/bin/env python

from iwi.collections import SortedSet
from iwi.core        import classify
from iwi.core        import Post
from iwi.solving     import SQLSolver
from iwi.threading   import Pool

from common import logger
from common import parameters

def crack (*links):
    """
    Returns a list of Posts with cracked trips.

    Reads 4chan URLs, scrapes contents and attempts to crack the tripcodes
    found. If any posts were cracked the corresponding Post object is added to
    a list that is returned.

    The list is sorted by time of post.
    """
    posts = SortedSet()
    pool  = Pool(num_threads=parameters.num_threads)

    pub_solver = SQLSolver(parameters.public_file)
    sec_solver = SQLSolver(parameters.secure_file)

    def work (unit):
        if isinstance(unit, Post):
            if unit.public or unit.secure:
                return unit
            return

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
    from common import TripcodeParser

    parser = TripcodeParser (
        description='Looks for tripcodes and cracks them.'
    )

    parser.add_argument (
        'link', nargs='+',
        help='boards/pages/threads, may either be full URLs or names like /g/'
    )

    args = parser.parse_args()

    if parser.sanity_check(args):
        exit(1)

    parser.pre_process(args)
    for e in crack(*args.link):
        print e
    parser.post_process(args)
