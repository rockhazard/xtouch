#!/usr/bin/env python3
"""
===============================================================================
Xtouch creates a given number of random files within the parent directory.
===============================================================================
"""


from textwrap import dedent
from pathlib import Path
import sys
import argparse
import random
import re
import string
from subprocess import run
__author__ = "Ike Davis"

_state = dict(upper=False, lower=False, prefix=False, suffix=False)


# use regex to parse the --generate option's arguments
# matches against pattern "str.int.str.str"
def match_args(args):
    pattern = r'^(?P<prefix>\S*)\.(?P<size>\d+)\.(?P<suffix>\S*)\.(?P<extension>\S*)$'
    if re.compile(pattern).match(args):
        matcher = re.search(pattern, args)
        groups = dict(prefix=matcher.group('prefix'),
                      size=matcher.group('size'),
                      suffix=matcher.group('suffix'),
                      extension=matcher.group('extension'))
        if sum([len(groups['prefix']), int(groups['size']), len(groups['suffix']),
                len(groups['extension'])]) <= 255:
            return groups
        else:
            sys.exit('Error: filename too long!')
    else:
        sys.exit('Error: see --help for acceptable filename pattern.')


def random_word(dictionary="/usr/share/dict/words"):
    # defaults to Linux word dictionary to get random word for filenames
    if not Path(dictionary).is_file():
        dictionary = input('Enter path to a newline-separated word list: ')
    with open(dictionary) as words:
        word_list = words.read().splitlines()
    random_words = [random.choice(word_list) for item in word_list]
    word = [line[:-2] if line.endswith("\'s")
            else line for line in random_words]
    return word[0]


def gen_random_name(prefix='/', randStrLen=8, suffix='/', ext="txt"):
    characters = string.printable[0:62]
    randStrLenList = []
    extList = []
    # randStrLen = int(randStrLen)
    for i in range(1, int(randStrLen) + 1):
        randStrLenList.append(random.choice(characters))
    try:
        for i in range(1, int(ext) + 1):
            extList.append(random.choice(characters))
        extension = "".join(extList)
    except ValueError:
        extension = ext

    name = "".join(randStrLenList)
    randName = name

    # attach any prefix, suffix, and extension from arguments
    if prefix == '%':
        randName = random_word() + '_' + name
    elif prefix != '/':
        randName = prefix + name
    if suffix == '%':
        randName += '_' + random_word()
    elif suffix != '/':
        randName += suffix
    if extension != '/':
        randName += '.' + extension

    # convert filename to upper or lower case
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
            !(prog)s creates a given number of files with random names in the 
            parent directory."""),
        epilog='Author: Ike Davis License: MIT')
    parser.add_argument('--version', help='print version info then exit',
                        version='!(prog)s 0.1 "Touchy"', action='version')
    parser.add_argument('--generate', '-g', nargs=2,
                        metavar=('PATTERN', 'NUMBER'),
                        help=dedent("""\
                                    Create a NUMBER of files according to 
                                    PATTERN, in the form: 'str.int.str.str'. The 
                                    'int' is required, but any other str may be
                                    '/' in order to exclude it. Example:
                                    'tmp_.2._work.log 1' may yield 'tmp_Yz_work.log'
                                    where 'int' is an integer and produces a 
                                    random alphanumeric string of 'int' characters.
                                    Use '%' to replace 'str' with a random dictionary
                                    word.
                                    """))
    parser.add_argument('--files', '-f', nargs='?', const=4, type=int,
                        metavar=('NUMBER_OF_FILES'),
                        help=dedent("""Create a given NUMBER_OF_FILES in an 
                            '8.txt' pattern, defaulting to 4 files."""))
    parser.add_argument('--uppercase', '-u', action='store_true',
                        help=dedent("""Make all filenames uppercase."""))
    parser.add_argument('--lowercase', '-l', action='store_true',
                        help=dedent("""Make all filenames lowercase."""))
    args = parser.parse_args()
    _state['upper'] = args.uppercase
    _state['lower'] = args.lowercase

    # produce required number of files
    try:
        if args.generate:
            match = match_args(args.generate[0])
            numberOfFiles = int(args.generate[1]) + 1
            for i in range(1, numberOfFiles):
                run('touch {}'.format(gen_random_name(match['prefix'],
                                                      match['size'],
                                                      match['suffix'],
                                                      match['extension'])),
                    shell=True)
        elif args.files:
            numberOfFiles = args.files + 1
            for i in range(1, numberOfFiles):
                run('touch {}'.format(gen_random_name()), shell=True)
    except ValueError as error:
        sys.exit(error)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
