"""
This file holds the default values for the various programs.
"""
import sys

__all__ = ['defaults']

defaults = {
    # filenames
    'cache_file'  : 'bin/cache.bin',
    'public_file' : 'tripcodes/public.db3',
    'secure_file' : 'tripcodes/secure.db3',
    'log_file'    : sys.stderr,

    # values
    'num_threads' : 16,

    # flags
    'debug'       : False,
    'https'       : False,
    'offline'     : False,
    'quiet'       : False
}
