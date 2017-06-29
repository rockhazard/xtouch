#!/usr/bin/env python3
"""
===============================================================================
Xtouch creates a given number of random files within the parent directory.
===============================================================================
"""


from textwrap import dedent
# from pathlib import Path
import sys
import argparse
import random
import string
from subprocess import run
__author__ = "Ike Davis"

_state = dict(upper=False, lower=False, prefix=False, suffix=False)


def gen_random_name(filename=8, ext="txt"):
    characters = string.printable[0:62]
    filenameList = []
    extList = []

    for i in range(1, filename + 1):
        filenameList.append(random.choice(characters))
    try:
        for i in range(1, int(ext) + 1):
            extList.append(random.choice(characters))
        extension = "".join(extList)
    except ValueError:
        extension = ext

    name = "".join(filenameList)
    randName = name
    if _state['prefix']:
        randName = _state['prefix'] + name
    if _state['suffix']:
        randName += _state['suffix']

    randName += '.' + extension

    if _state['upper']:
        return randName.upper()
    elif _state['lower']:
        return randName.lower()
    else:
        return randName


def main(*args):
    """
    COMMANDLINE OPTIONS
    """
    parser = argparse.ArgumentParser(
        prog=sys.argv[0][2:],
        description=dedent("""\
            %(prog)s creates a given number of files with random names in the 
            parent directory."""),
        epilog='Author: Ike Davis License: MIT')
    parser.add_argument('--version', help='print version info then exit',
                        version='%(prog)s 0.1 "Touchy"', action='version')
    parser.add_argument('--generate', '-g', nargs=3,
                        metavar=('NAME_LENGTH', 'EXT_LENGTH', 'NUMBER'),
                        help=dedent("""\
                                    Create a NUMBER of files with random names 
                                    of NAME_LENGTH with extension EXT_LENGTH. If
                                    EXT_LENGTH is a string instead of an integer,
                                    that string will be used for each new file. 
                                    The default extension is "txt".
                                    """))
    parser.add_argument('--files', '-f', nargs='?', const=4, type=int,
                        metavar=('NUMBER_OF_FILES'),
                        help=dedent("""Create a given NUMBER_OF_FILES in an 
                            '8.txt' pattern, defaulting to 4 files."""))
    parser.add_argument('--prefix', '-p', nargs='?', help=dedent("""Prepend the 
                            given string of PREFIX to all files."""))
    parser.add_argument('--suffix', '-s', nargs='?', help=dedent("""Append the 
                            given string of SUFFIX to all files."""))
    parser.add_argument('--uppercase', '-u', action='store_true',
                        help=dedent("""Make all filenames uppercase."""))
    parser.add_argument('--lowercase', '-l', action='store_true',
                        help=dedent("""Make all filenames lowercase."""))
    args = parser.parse_args()
    _state['upper'] = args.uppercase
    _state['lower'] = args.lowercase
    _state['prefix'] = args.prefix
    _state['suffix'] = args.suffix
    try:
        if args.generate:
            numberOfFiles = int(args.generate[2]) + 1
            for i in range(1, numberOfFiles):
                run('touch {}'.format(gen_random_name(
                    int(args.generate[0]), args.generate[1])), shell=True)
        elif args.files:
            numberOfFiles = args.files + 1
            for i in range(1, numberOfFiles):
                run('touch {}'.format(gen_random_name()), shell=True)
    except ValueError as error:
        sys.exit(error)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
