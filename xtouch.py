#!/usr/bin/env python3
"""
================================================================================
Xtouch automates GNU touch by creating a given number of randomly-named files. 
This is useful for creating mock files or creating and opening several new files
for editing in other programs.

Features:
* Define filenames via a pattern: prefix.integer.suffix.extension.
* Default pattern.
* Set case of generated files.
* Pass standard gnu touch options to generated files.
* Full use of gnu touch from xtouch.

Written by Ike Davis

License: MIT
================================================================================
"""


import sys
import argparse
import random
import re
import string
from textwrap import dedent
from pathlib import Path
from subprocess import run
__author__ = "Ike Davis"

_options = dict(uppercase=False, lowercase=False, touch_options=False,
                increment=False)


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


def increment_filename(zeroes, count):
    place = len(str(count))
    zeroCount = int(zeroes) - place
    file_count = '0' * zeroCount + str(count)
    return file_count


def gen_filename(prefix='/', randStrLen=8, suffix='/', ext="txt", sep='_', zeroes=5, count=5):
    characters = string.printable[0:62]
    randStrLenList = []
    extList = []

    if _options['increment']:
        filename = increment_filename(zeroes, count)
    else:
        for i in range(1, int(randStrLen) + 1):
            randStrLenList.append(random.choice(characters))
    try:
        for i in range(1, int(ext) + 1):
            extList.append(random.choice(characters))
        extension = "".join(extList)
    except ValueError:
        extension = ext
    if not filename:
        filename = ''
    elif randStrLenList:
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
    if _options['uppercase']:
        return filename.upper()
    elif _options['lowercase']:
        return filename.lower()
    else:
        return filename


def file_factory(pattern='/.8./.txt', nFiles=1, sep='_', default=True):
    # use user-supplied arguments to produce unique files
    try:
        match = match_args(pattern)
        numberOfFiles = int(nFiles)
        maxFiles = int(''.join(['9' for i in range(int(match['size']))]))
        if _options['increment']:
            if numberOfFiles > maxFiles:
                sys.exit('Error: requested number of files exceeds maximum.')

        # create set of unique filenames
        def gen_files_set(numberOfFiles):
            if default:
                return {gen_filename(zeroes=str(match['size']), count=i)
                        for i in range(numberOfFiles)}
            else:
                return {gen_filename(match['prefix'], match['size'],
                                     match['suffix'],
                                     match['extension'], sep,
                                     zeroes=str(match['size']), count=i)
                        for i in range(numberOfFiles)
                        }

        name = gen_files_set(numberOfFiles)
        # build set until all filenames are unique
        if len(name) != numberOfFiles:
            print('Building unique filenames...')
            while len(name) < numberOfFiles:
                diff = numberOfFiles - len(name)
                remainder = gen_files_set(diff)
                name = name.union(remainder)

        # write files
        if _options['touch_options']:
            options = _options['touch_options']
        else:
            options = ''
        name = list(name)
        for i in range(numberOfFiles):
            run('touch {} {}'.format(options, name[i]), shell=True)
        print('Generated {} files.'.format(len(name)))
    except ValueError as error:
        sys.exit(error)


def main(*args):
    """
    COMMANDLINE OPTIONS
    """
    parser = argparse.ArgumentParser(
        prog='xtouch', prefix_chars='+',
        description=dedent("""\
            %(prog)s is an automation wrapper for GNU touch. It creates a given 
            number of files with either a user-defined or default pattern."""),
        epilog='Author: Ike Davis, distributed via the MIT license')
    parser.add_argument('options', nargs='*', metavar=('TOUCH_ARGS'),
                        default='', help=dedent("""\
                            Use original gnu touch options.
                            """))
    parser.add_argument('++version', help='print version info then exit',
                        version='!(prog)s 0.1 "Touchy"', action='version')
    parser.add_argument('++generate', '+g', nargs=2,
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
    parser.add_argument('++files', '+f', nargs='?', const=1, type=int,
                        metavar=('NUMBER_OF_FILES'),
                        help=dedent("""Create a given NUMBER_OF_FILES in an 
                            '8.txt' pattern, defaulting to one file."""))
    parser.add_argument('++increment', '+i', action='store_true',
                        help=dedent("""Increment filenames instead of generating
                            random characters to replace 'int'."""))
    parser.add_argument('++uppercase', '+u', action='store_true',
                        help=dedent("""Make all filenames uppercase."""))
    parser.add_argument('++lowercase', '+l', action='store_true',
                        help=dedent("""Make all filenames lowercase."""))
    args = parser.parse_args()
    _options['uppercase'] = args.uppercase
    _options['lowercase'] = args.lowercase

    # create options string and write requested files
    if args.increment:
        _options['increment'] = args.increment
    if args.options:
        _options['touch_options'] = ' '.join(args.options)
    if args.files:  # default filename pattern
        file_factory(nFiles=args.files)
    elif args.generate:  # employ user-defined filename pattern
        file_factory(args.generate[0], args.generate[1], default=False)
    else:
        run('touch {}'.format(_options['touch_options']), shell=True)


if __name__ == '__main__':
    main(sys.argv[1:])
