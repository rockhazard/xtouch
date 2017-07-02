#!/usr/bin/env python3
"""
================================================================================
Xtouch automates GNU touch by creating a given number of randomly-named files. 
This is useful for creating mock files or creating and opening several new files
for editing in other programs.

Features:
* Define filenames via a pattern: prefix.integer.suffix.extension.
* Default to 8.txt pattern.
* Set case of generated files.
* Pass standard gnu touch options to generated files.

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

_options = dict(uppercase=False,
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
    if _options['uppercase']:
        return filename.upper()
    elif _options['lowercase']:
        return filename.lower()
    else:
        return filename


def shell_args(dictionary=_options):
    # return options string for a shell command; takes dictionary in form
    #  dict[opt, bool], where returned options' bools are either a string
    # (an argument) or True (a flag).
    argString = ''
    for key, value in dictionary.items():
        if key not in ('uppercase', 'lowercase'):
            bool_test = dictionary[key][1]
            # options with arguments
            if type(bool_test) != bool:
                argString += ' ' + dictionary[key][0] + ' ' + \
                    dictionary[key][1] + ' '
            # flags
            if bool_test != str and bool_test == True:
                argString += ' ' + dictionary[key][0] + ' '
    return argString


def file_factory(pattern='/.8./.txt', nFiles=1, sep='_', default=True):
    # use user-supplied arguments to produce unique files
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
        # build set until all filenames are unique
        if len(name) != numberOfFiles:
            print('Building unique filenames...')
            while len(name) < numberOfFiles:
                diff = numberOfFiles - len(name)
                remainder = gen_files_set(diff)
                name = name.union(remainder)

        # write files
        options = shell_args()
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
    parser.add_argument('--accesstime', '-a', action='store_true',
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
    parser.add_argument('--mtime', '-m', action='store_true',
                        help=dedent("""Change only the modification time."""))
    parser.add_argument('--reference', '-r', nargs=1, metavar=('REFERENCE'),
                        help=dedent("""Use this file's times instead of current time."""))
    parser.add_argument('--stamp', '-t', nargs=1, metavar=('STAMP'),
                        help=dedent("""Use [[CC]YY]MMDDhhmm[.ss] instead of 
                                    current time."""))
    parser.add_argument('--original', '-o', nargs='*', metavar=('FILE'),
                        help=dedent("""Basic touch without automation or options."""))

    args = parser.parse_args()
    # set options dictionary values
    # GNU touch
    if args.accesstime:
        _options['accesstime'][1] = args.accesstime
    if args.nocreate:
        _options['nocreate'][1] = args.nocreate
    if args.date:
        _options['date'][1] = args.date[0]
    if args.nodereference:
        _options['nodereference'][1] = args.nodereference
    if args.mtime:
        _options['modtime'][1] = args.mtime
    if args.reference:
        _options['reference'][1] = args.reference[0]
    if args.stamp:
        _options['stamp'][1] = args.stamp[0]
    # xtouch custom option values
    # add these xtouch-only options in _options to ignored tuple in shell_args
    _options['uppercase'] = args.uppercase
    _options['lowercase'] = args.lowercase

    # create options string and write requested files
    if args.files:  # default filename pattern
        file_factory(nFiles=args.files)
    elif args.generate:  # employ user filename pattern
        file_factory(args.generate[0], args.generate[1], default=False)
    else:  # for direct access to gnu touch
        touch_str = input('Enter touch arguments: ')
        run('touch {}'.format(touch_str), shell=True)

if __name__ == '__main__':
    main(sys.argv[1:])
