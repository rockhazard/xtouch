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


def gen_random_name(filename=8, ext="txt"):
    characters = string.printable[0:63]
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
    randName = name + "." + extension
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
                        version='%(prog)s 1.0', action='version')
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
    args = parser.parse_args()
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
