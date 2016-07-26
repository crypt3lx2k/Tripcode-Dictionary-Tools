__all__ = ['Solver']

class Solver (object):
    """
    Base class for solvers.
    """
    def solve (self, tripcode, *args):
        """
        Every Solver derivative must implement this method.

        It shall accept whatever arguments are relevant and return a key.
        If no key is found, None shall be returned.
        """
        raise NotImplementedError (
            'Solver derivatives must implement this method!'
        )
