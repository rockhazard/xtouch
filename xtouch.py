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

_state = dict(uppercase=False,
              lowercase=False,
              accesstime=['-a', False],
              nocreate=['-c', False],
              date=['-d', False],
              nodereference=['-h', False],
              modtime=['-m', False],
              reference=['-r', False],
              stamp=['-t', False],
              time=['--time', False])


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


def touch_args():
    # create options string to feed to GNU touch
    argString = ''
    for key, value in _state.items():
        if key != 'uppercase' and key != 'lowercase':
            option_test = _state[key][1]
            if type(option_test) != bool:
                argString += ' ' + _state[key][0] + ' ' + _state[key][1] + ' '
            if option_test != str and option_test == True:
                argString += ' ' + _state[key][0] + ' '
    return argString


def file_factory(pattern='/.8./.txt', nFiles=1, sep='_', default=True):
    # use user args to produce unique files
    try:
        match = match_args(pattern)
        numberOfFiles = int(nFiles)
        # create set of unique filenames

        def gen_files_set(numberOfFiles):
            if default:
                return {gen_random_name() for i in range(numberOfFiles)}
            else:
                return {gen_random_name(match['prefix'], match['size'],
                                        match['suffix'],
                                        match['extension'], sep)
                        for i in range(numberOfFiles)
                        }

        name = gen_files_set(numberOfFiles)
        # if random module generates duplicate names, build set of unique names
        if len(name) != numberOfFiles:
            print('Building unique filenames...')
            while len(name) < numberOfFiles:
                diff = numberOfFiles - len(name)
                remainder = gen_files_set(diff)
                name = name.union(remainder)

        # write files
        options = touch_args()
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
        prog=sys.argv[0][2:],
        description=dedent("""\
            %(prog)s is an automation wrapper for GNU touch. It creates a given 
            number of files with random names in the present working directory.
            """),
        epilog='Author: Ike Davis License: MIT')
    # Xtouch specific options
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

    # GNU Touch Options
    parser.add_argument('--accesstime', '-a', nargs=1, metavar=('ATIME'),
                        help=dedent("""Change only the access time."""))
    parser.add_argument('--nocreate', '-c', action='store_true',
                        help=dedent("""Do not create any files."""))
    parser.add_argument('--date', '-d', nargs=1, metavar=('STRING'),
                        help='parse STRING and use it instead of current time.')
    parser.add_argument('--nodereference', '-n',  action='store_true',
                        help=dedent("""\
                            affect each symbolic link instead of any referenced 
                            file (useful only on systems that can change the 
                            timestamps of a symlink)"""))
    parser.add_argument('--mtime', '-m', nargs=1, metavar=('MTIME'),
                        help=dedent("""Change only the modification time."""))
    parser.add_argument('--reference', '-r', nargs=1, metavar=('REFERENCE'),
                        help=dedent("""Use this file's times instead of current time."""))
    parser.add_argument('--stamp', '-t', nargs=1, metavar=('STAMP'),
                        help=dedent("""Use [[CC]YY]MMDDhhmm[.ss] instead of 
                                    current time."""))
    parser.add_argument('--time', nargs=1, metavar=('WORD'),
                        help=dedent("""Change the specified time: WORD is access, 
                            atime, or use: equivalent to '-a WORD' is modify or 
                            mtime: equivalent to '-m'."""))
    parser.add_argument('--original', '-o', action='store_true',
                        help=dedent("""Use this option when using touch in its
                            traditional manner."""))

    args = parser.parse_args()
    # set options dictionary
    # xtouch
    _state['uppercase'] = args.uppercase
    _state['lowercase'] = args.lowercase
    # GNU touch
    if args.accesstime:
        _state['accesstime'][1] = args.accesstime
    if args.nocreate:
        _state['nocreate'][1] = args.nocreate
    if args.date:
        _state['date'][1] = args.date[0]
    if args.nodereference:
        _state['nodereference'][1] = args.nodereference
    if args.mtime:
        _state['modtime'][1] = args.mtime[0]
    if args.reference:
        _state['reference'][1] = args.reference[0]
    if args.stamp:
        _state['stamp'][1] = args.stamp[0]
    if args.time:
        _state['time'][1] = '=' + args.time[0]
    # create options string

    if args.files:  # default 8.txt filename pattern
        file_factory(nFiles=args.files)
    elif args.generate:  # consume user filename pattern
        file_factory(args.generate[0], args.generate[1], default=False)
    elif args.original:
        run('touch {}'.format(' '.join(sys.argv[2:])), shell=True)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
