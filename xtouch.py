#!/usr/bin/env python3
"""
================================================================================
Xtouch automates GNU touch by creating a given number of randomly-named files.
This is useful for creating mock files or creating and opening several new files
for editing in other programs.

Features:
* Define filenames via a pattern: prefix.integer.suffix.extension.
* Default pattern.
* Increment filenames
* Set case of generated files.
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
# from subprocess import run
import subprocess
__author__ = "Ike Davis"

_options = dict(uppercase=False, lowercase=False, pos_options=False,
                increment=False)


def match_args(args):
    # executed by file_factory
    # use regex to parse the --generate option's arguments
    # matches against pattern "str.int.str.str||int"
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
    # executed by gen_filename
    # defaults to Linux word dictionary to get random word for filenames
    if not Path(dictionary).is_file():
        dictionary = input('Enter path to a newline-separated word list: ')
    with open(dictionary) as words:
        word_list = words.read().splitlines()
    random_words = [random.choice(word_list) for item in word_list]
    word = [line[:-2] if line.endswith("\'s")
            else line for line in random_words]
    return word[0]


def increment_filename(zeros, count):
    # executed by gen_filename
    # returns incrementing count with proper leading zeros
    place = len(str(count))
    zeroCount = int(zeros) - place
    file_count = '0' * zeroCount + str(count)
    return file_count


def gen_filename(switch=_options, prefix='/', size=8, suffix='/', ext="txt", sep='_',
                 zeros=5, count=1):
    # executed by gen_files_set within file_factory
    characters = string.printable[0:62]
    sizeList = []
    extList = []
    size = int(size)
    try:  # convert ext to int if possible
        if type(int(ext)) is int:
            ext = int(ext)
    except ValueError:
        pass
    # either use increment feature or use size to build random names
    if switch['increment'] and size > 0:
        filename = increment_filename(zeros, count)
    else:
        for i in range(1, size + 1):
            sizeList.append(random.choice(characters))
        filename = "".join(sizeList)
    # either use increment feature or use ext to build random names
    if type(ext) is int:
        if switch['increment']:
            extzeros = int(ext)
            extension = increment_filename(extzeros, count)
        else:
            for i in range(1, ext + 1):
                extList.append(random.choice(characters))
            extension = "".join(extList)
    else:
        extension = ext

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
    if switch['uppercase']:
        return filename.upper()
    elif switch['lowercase']:
        return filename.lower()
    else:
        return filename


def gen_files_set(numberOfFiles, zeros, default, match, sep, switch=_options, ):
    # executed by file_factory
    # create set of unique filenames
    try:  # calculate maximum unique files to avoid infinite loop at set build
        sizeMaxUniqueFiles = int(
            ''.join(['9' for i in range(int(match['size']))]))
    except ValueError:
        sizeMaxUniqueFiles = 1
    try:
        extMaxUniqueFiles = int(
            ''.join(['9' for i in range(int(match['extension']))]))
    except ValueError:
        extMaxUniqueFiles = 1
    maxUniqueFiles = sizeMaxUniqueFiles * extMaxUniqueFiles
    if maxUniqueFiles < numberOfFiles:
        sys.exit('Error: max number of files for pattern ({}) exceeded'.format(
            maxUniqueFiles))

    if default:
        return {gen_filename(switch=_options, size=zeros, count=i)
                for i in range(numberOfFiles)}
    else:
        return {gen_filename(switch=_options, prefix=match['prefix'], size=match['size'],
                             suffix=match['suffix'], ext=match['extension'],
                             sep=sep, zeros=zeros, count=i)
                for i in range(numberOfFiles)
                }


def file_factory(pattern='/.8./.txt', nFiles=1, sep='_', default=True,
                 switch=_options, cmd=subprocess):
    # executed by main
    # use user-supplied arguments to produce unique files
    match = match_args(pattern)
    numberOfFiles = int(nFiles)
    # avoid looping clobber
    if switch['increment'] and int(match['size']) > 0:
        maxFiles = int(''.join(['9' for i in range(int(match['size']))]))
        if numberOfFiles > maxFiles:
            sys.exit(dedent("""\
                                Error: requested number of files exceeds
                                maximum. Increase 'int' amount."""))

    names = gen_files_set(numberOfFiles, str(
        match['size']), default, match, sep)
    # build set until requested number of filenames in set
    if len(names) != numberOfFiles:
        print('Building unique filenames...')
        while len(names) < numberOfFiles:
            diff = numberOfFiles - len(names)
            remainder = gen_files_set(
                diff, str(match['size']), default, match, sep)
            names = names.union(remainder)
    names = list(names)

    # resolve positional arguments for run string
    if switch['pos_options']:
        pos_options = switch['pos_options']
    else:
        pos_options = ''

    # write files and report
    for i in range(numberOfFiles):
        cmd.run('touch {} {}'.format(pos_options, names[i]), shell=True)
    print('Generated {} files.'.format(len(names)))


def main(*args):
    """
    COMMANDLINE OPTIONS
    """
    parser = argparse.ArgumentParser(
        prog='xtouch', prefix_chars='+',
        description=dedent("""\
            %(prog)s is an automation wrapper for GNU touch. It creates a given
            number of files with either a user-defined or default pattern.
            Pattern is string.integer.string.string|integer.
            Examples: 
            xtouch +ig page_.3._mock.html 1 creates page_000_mock.html
            xtouch +g /.1.log 2 creates 0.log and 1.log
            xtouch +ig mock_./.3 14 creates mock_.000 ... mock_.013
            xtouch +g mock_./.3 14 creates mock_.sI0 ... mock_.Ghy
            The integer defaults to a number of random alphanumeric characters
            equal to the integer, unless +i is used to increment the filename.
            """),
        epilog='Author: Ike Davis, distributed under the MIT license')
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
        _options['pos_options'] = ' '.join(args.options)
    if args.files:  # default filename pattern
        file_factory(nFiles=args.files)
    elif args.generate:  # employ user-defined filename pattern
        file_factory(args.generate[0], args.generate[1], default=False)
    else:
        subprocess.run('touch {}'.format(_options['pos_options']), shell=True)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
