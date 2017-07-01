#!/usr/bin/env python3
"""
===============================================================================
Xtouch automates GNU touch by creating a given number of randomly-named files 
within the present working directory. This is useful for creating dummy/mock
files or creating and opening several new files for editing in other programs.

Features:
* Define filenames via a pattern: prefix.integer.suffix.extension.
* Default to 8.txt pattern.
* Set case of generated files.

NOTE: This program does not currently support GNU touch options.
Written by Ike Davis

License: MIT
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

_state = dict(uppercase=False, lowercase=False)


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


def gen_random_name(prefix='/', randStrLen=8, suffix='/', ext="txt", sep='_'):
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
    if not randStrLenList:
        filename = ''
    else:
        filename = "".join(randStrLenList)

    # attach any prefix, suffix, and extension from arguments
    if prefix == '%':
        filename = random_word() + sep + filename
    elif prefix != '/':
        filename = prefix + filename
    if suffix == '%':
        filename += sep + random_word()
    elif suffix != '/':
        filename += suffix
    if extension != '/':
        filename += '.' + extension

    # convert filename to upper or lower case
    if _state['uppercase']:
        return filename.upper()
    elif _state['lowercase']:
        return filename.lower()
    else:
        return filename


def file_factory(matchf, nFiles, sep='_'):
    # use user args to produce unique files
    try:
        match = matchf  # per
        numberOfFiles = int(nFiles)  # per

        def fileSet(numberOfFiles):
            return {
                gen_random_name(match['prefix'], match['size'],
                                match['suffix'],
                                match['extension'], sep)
                for i in range(0, numberOfFiles)
            }

        name = fileSet(numberOfFiles)
        # ensure proper number of unique files are created
        if len(name) != numberOfFiles:
            while len(name) < numberOfFiles:
                dif = numberOfFiles - len(name)
                print('Filenames remaining: {}'.format(dif))
                remainder = fileSet(dif)
                name = name.union(remainder)
                print('Deduping run...')
            else:
                print(dedent("""\
                             Created {} files.
                             Increasing "int" reduces duplicate name generation.
                             """).format(len(name)))

        name = list(name)
        for i in range(0, numberOfFiles):
            run('touch {}'.format(name[i]),
                shell=True)
    except ValueError as error:
        sys.exit(error)


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
                        version='!(prog)s 0.1 "Touchy"', action='version')
    parser.add_argument('--generate', '-g', nargs=2,
                        metavar=('PATTERN', 'NUMBER_OF_FILES'),
                        help=dedent("""\
                                    Create a NUMBER_OF_FILES according to a
                                    PATTERN, in the form: 'str.int.str.str'. The 
                                    'int' is required, but any other str may be
                                    '/' in order to exclude it. Example:
                                    'tmp_.2._work.log 1' may yield 'tmp_Yz_work.log'
                                    where 'int' is an integer and produces a 
                                    random alphanumeric string of 'int' characters.
                                    Use '%%' to replace 'str' with a random dictionary
                                    word. Using 0 for 'int' requires that at least
                                    one 'str' contains a character other than '/'.
                                    """))
    parser.add_argument('--files', '-f', nargs='?', const=1, type=int,
                        metavar=('NUMBER_OF_FILES'),
                        help=dedent("""Create a given NUMBER_OF_FILES in an 
                            '8.txt' pattern, defaulting to one file."""))
    parser.add_argument('--uppercase', '-u', action='store_true',
                        help=dedent("""Make all filenames uppercase."""))
    parser.add_argument('--lowercase', '-l', action='store_true',
                        help=dedent("""Make all filenames lowercase."""))
    args = parser.parse_args()
    _state['uppercase'] = args.uppercase
    _state['lowercase'] = args.lowercase
    # produce required number of files
    try:
        if args.generate:  # consume pattern
            file_factory(match_args(args.generate[0]), args.generate[1])
            # match = match_args(args.generate[0])
            # numberOfFiles = int(args.generate[1]) + 1
            # for i in range(1, numberOfFiles):
            #     name = gen_random_name(match['prefix'], match['size'],
            #                            match['suffix'],
            #                            match['extension'])
            #     run('touch {}'.format(name),
            #         shell=True)
        elif args.files:  # default
            numberOfFiles = args.files + 1
            for i in range(1, numberOfFiles):
                run('touch {}'.format(gen_random_name()), shell=True)
    except ValueError as error:
        sys.exit(error)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
