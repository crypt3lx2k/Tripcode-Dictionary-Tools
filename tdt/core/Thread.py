import HTMLParser

from ..web import Links

from . import Public, Secure
from . import WebEntity
from . import Post

__all__ = ['Thread']

class Thread (WebEntity):
    """
    Represents a thread.
    """
    html_parser    = HTMLParser.HTMLParser()
    default_object = {'posts':[]}

    def __init__ (self, board, thread):
        """
        Initializes an instance from a board and a thread number.
        """
        self.board  = board
        self.thread = thread

    def __repr__ (self):
        """
        Returns a string representation fit for eval.
        """
        return (
            '{self.__class__.__name__}({self.board!r}, {self.thread!r})'.format (
                self=self
            )
        )

    @property
    def apiurl (self):
        """
        Returns an url to the corresponding API json page.
        """
        return Links.createAPIURL (
            '/{self.board}/res/{self.thread}.json'.format(self=self)
        )

    @property
    def url (self):
        """
        Returns an url to the thread.
        """
        return Links.createURL (
            '/{self.board}/res/{self.thread}'.format(self=self)
        )

    def process (self):
        """
        Returns the Post instances you get by evaluating the thread.
        """
        thread = self.download_and_decode()
        posts  = []

        for post in thread['posts']:
            # ignore posts that don't have tripcodes
            if not 'trip' in post:
                continue

            post['trip'] = str(post['trip'])
            pub_match = Public.pattern.match (post['trip'])
            sec_match = Secure.pattern.search(post['trip'])

            # FIXME: should access to Thread.html_parser be synchronized? 
            # FIXED: not if all we use is the undocumented unescape method.
            name = Thread.html_parser.unescape(post.get('name', ''))
            name = str(name.encode("utf8"))

            public = Public(pub_match.group(1)) if pub_match else None
            secure = Secure(sec_match.group(1)) if sec_match else None

            posts.append (
                Post (
                    name   = name,
                    time   = post['time'],
                    board  = self.board,
                    thread = self.thread,
                    post   = post['no'],
                    public = public,
                    secure = secure
                )  
            )

        return posts
