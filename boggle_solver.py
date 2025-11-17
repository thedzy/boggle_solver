#!/usr/bin/env python3
"""
Script:	boggle_solver.py
Date:	2020-04-11

Platform: macOS/Windows/Linux

Description:
Solve a boggle puzzle
Find all the words in a given/generated puzzle

"""
__author__ = "thedzy"
__copyright__ = "Copyright 2020, thedzy"
__license__ = "GPL"
__version__ = "1.6.1"
__maintainer__ = "thedzy"
__email__ = "thedzy@hotmail.com"
__status__ = "Development"

import argparse
import ctypes
import json
import math
import os
import pickle
import platform
import random
import re
import sys
import time
from typing import Any

SPEED_STEPS = 50


def main() -> None:
    start_time: float = time.time()

    if 'windows' in platform.platform().lower():
        # Capture the window that we are starting with, if we return we can send interrupt
        start_window: ctypes.windll = ctypes.windll.user32.GetForegroundWindow()

    # Get the width of the window
    try:
        terminal_width, _ = os.get_terminal_size()
    except OSError:
        terminal_width: int = 80

    """
    Processing options
    """
    # Load dictionary
    try:
        tree_dictionary: dict[str, str] = pickle.load(options.dictionary)
        options.dictionary.close()
    except (UnicodeDecodeError, EOFError):
        print_error('Dictionary may be corrupt or not a dictionary',
                    'Verify file or reprocess dictionary')
    except Exception as err:
        print_error(f'Error loading dictionary:', str(err))

    # Get stat
    dictionary_load_time = time.time() - start_time

    # Validate regex before continuing
    if options.filter:
        try:
            pattern: re.Pattern[Any | str] = re.compile(options.filter, re.IGNORECASE)
        except re.error as err:
            print_error('Error in regex statement', err.msg.title())

    # Get/make the puzzle
    letters: list[str] = ['a', 'b', 'c', 'd', 'e', 'f', 'g',
                          'h', 'i', 'j', 'k', 'l', 'm', 'n',
                          'o', 'p', 'qu', 'r', 's', 't', 'u',
                          'v', 'w', 'x', 'y', 'z']
    if options.puzzle is None:
        row_count: int = options.puzzle_size
        puzzle: list[list[str]] = []
        for _ in range(row_count):
            puzzle.append(list(random.choice(letters) for _ in range(row_count)))
    else:
        puzzle_length: int = len(options.puzzle)
        root: float = math.sqrt(puzzle_length)

        # if puzzle is not a square kill in the necessary characters
        if not math.sqrt(puzzle_length).is_integer():
            root: int = math.ceil(root)
            missing_characters: int = (root * root) - len(options.puzzle)
            print(f'Extending puzzle letters by {missing_characters} to make a puzzle')
            for _ in range(missing_characters):
                options.puzzle.append(random.choice(letters))
            puzzle_length: int = len(options.puzzle)

        if options.randomise:
            random.shuffle(options.puzzle)

        # If length of one, lets assume they characters are not spaced
        if puzzle_length == 1:
            options.puzzle = list(options.puzzle[0])

        row_count: int = int(root)

        puzzle: list[list[str]] = []
        for puzzle_x in range(0, row_count):
            row: list[str] = []
            for puzzle_y in range(0, row_count):
                row.append(options.puzzle[puzzle_x * row_count + puzzle_y].lower())
            puzzle.append(row)

    # Set the max/min length of a word
    length_max: int = min(row_count ** 2, 32)
    length_min: int = 3
    if options.length:
        length_min = length_max = options.length
    else:
        # Max word length of the puzzle size or 32, whichever is smaller
        if options.length_max:
            length_max: int = options.length_max

        if options.length_min:
            length_min: int = options.length_min

    # Validate length
    if length_max > (row_count ** 2):
        length_max: int = row_count ** 2
        print(f'Max length exceeds puzzle size, setting to {length_max} instead')

    # Min cannot exceed max
    length_min: int = length_max if length_min > length_max else length_min

    # Get minimum search length by taking the minimum word and taking of the longest tile
    puzzle_char_max_size: int = len(max(options.puzzle, key=len)) if options.puzzle else 1
    length_search_min: int = length_min - puzzle_char_max_size + 1
    length_search_min: int = 1 if length_search_min <= 1 else length_search_min

    results: dict[str, Any] = {'puzzle': puzzle, 'filter': options.filter, 'contains': options.filter_contains}

    """
    Print Puzzle
    """
    # Show the puzzle so tht the user can see what is being solved
    if not options.json:
        tile_size: int = len(max([y for x in puzzle for y in x], key=len)) + 1
        print('Puzzle: ')
        print('=' * ((row_count * tile_size) - 1))
        print('\n'.join([''.join([f'{item:^{tile_size}}' for item in row]) for row in puzzle]))
        print('=' * ((row_count * tile_size) - 1))

    """
    Searching
    """
    # Setup a progressbar
    bar_position: int = 0
    bar_position_max: int = (row_count ** 2) * (length_max - length_search_min + 1)

    # Loop through to find the words
    words_valid: list[str] = []
    for index_x in range(0, row_count):
        for index_y in range(0, row_count):
            x, y = (index_x, index_y)

            for length in range(length_search_min, length_max + 1):
                bar_position += 1
                progressbar(bar_position, bar_position_max, puzzle[x][y].upper(), terminal_width)
                # Call to find words starting from and ending at
                get_words(x, y, length, puzzle[x][y], words_valid, [(x, y)], puzzle, tree_dictionary)
    print()

    search_time = time.time() - start_time

    """
    Sorting and filtering
    """
    # Remove duplicates
    words_valid: list[str] = sorted(set(words_valid), key=words_valid.index)
    # Filter lengths
    words_valid: list[str] = list(filter(lambda word_valid: length_min <= len(word_valid) <= length_max, words_valid))

    # If a contains filter is used
    if options.filter_contains:
        if not options.json:
            print(f'Filtering words with patterns "{", ".join(options.filter_contains)}"{" " * 80}')
        else:
            results['contains'] = options.filter_contains
        pattern_list = ['^.*'] + [f'(?=.*{x})' for x in options.filter_contains] + ['.*']
        pattern2 = re.compile(''.join(pattern_list), re.IGNORECASE)
        for word in words_valid[:]:
            if not pattern2.fullmatch(word):
                words_valid.remove(word)

    # If a filter is used
    if options.filter:
        if not options.json:
            print(f'Filtering with "{options.filter}" {" " * 80}')

    if options.order_alpha:
        words_valid.sort()
    if options.order_size or options.order_size_r:
        words_valid.sort(key=len, reverse=options.order_size_r)

    if not options.json:
        print(f'Words found that are contained in "{options.dictionary.name}"{" " * 80}')

    results['words']: list[str] = words_valid

    # Get runtime
    total_time: float = time.time() - start_time

    """
    Display results
    """
    results['stats']: dict[str, Any] = {'puzzle_size': row_count,
                                        'word_count': len(words_valid),
                                        'dictionary_load_time': dictionary_load_time,
                                        'search_time': search_time,
                                        'total_time': total_time}

    if options.json:
        print(json.dumps(results))
        return

    # Print words
    if len(words_valid) > 0:
        if not options.list:
            divider: str = ' | '

            column_width = len(max(words_valid, key=len)) + len(divider)
            columns = int(((terminal_width - 1) - len(divider)) / column_width)
            column_height = int(len(words_valid) / columns) + 1

            words_valid_columned: list[Any] = []
            start, end = 0, 0
            while end < len(words_valid):
                end: int = start + column_height
                try:
                    words_valid_columned.append(words_valid[start:end])
                except IndexError:
                    words_valid_columned.append(words_valid[start:])
                start = end

            for row in range(column_height):
                print(divider, end='')
                for column in words_valid_columned:
                    try:
                        print(column[row].ljust(column_width - len(divider), ' '), end=divider)
                    except IndexError:
                        break
                print()
        else:
            print('\n'.join(words_valid))

    # Print word count and stats
    if length_min is length_max:
        print(f'Found {len(words_valid)} words of {length_max} characters in length and matching filters')
    else:
        print(f'Found {len(words_valid)} words between {length_min} and {length_max} characters in length and matching filters')
    print('--')
    print(f'Time to load dictionary   {dictionary_load_time:0.3f}s')
    print(f'Time to search            {search_time - dictionary_load_time:0.3f}s')
    print(f'Time to filter            {total_time - search_time:0.3f}s')
    print(f'Total:                    {total_time:0.3f}s')

    """
    Keyboard emulation
    """
    if options.enter:
        if 'windows' in platform.platform().lower():
            # Countdown to start
            print('Starting typing in ', end='')
            count_down_timer = options.enter + 1
            for count_down in range(1, count_down_timer):
                print(count_down_timer - count_down)
                time.sleep(1)
            print('Go!')

            # For each word, emulate typing
            speed = (SPEED_STEPS - options.speed) / SPEED_STEPS
            for word in words_valid:
                for letter in word:
                    # If interrupting, check if we are back the window
                    if not options.interrupt:
                        focus_window = ctypes.windll.user32.GetForegroundWindow()
                        if focus_window == start_window:
                            exit()

                    # If speed is -1 random after every character giving a more human appearance
                    if options.speed < 0:
                        speed: float = random.random()

                    win_press_key(letter, None, speed / 2)

                # Send return
                print('Entering:', word)
                win_press_key(None, None, speed / 2)

                # Pause between each word to give program time to score
                time.sleep(speed)


def win_press_key(key: str | None = None, modifier: str | None = None, hold_time: float = 0.1) -> None:
    """
    Emulate a keyboard press, <enter> default
    :param key: Single character to emulate
    :param modifier: Hold modifier key during key press
    :param hold_time: Key hold time
    :return: (void)
    """
    modifiers: dict[str, ord] = {
        'shift': 0x10,
        'ctrl': 0x11,
        'alt': 0x12,
    }
    # If no key, return
    code: ord = ord(key.upper()) if key else 0x0D
    if modifier:
        ctypes.windll.user32.keybd_event(modifiers[modifier], 0, 0, 0)
    ctypes.windll.user32.keybd_event(code, 0, 0, 0)
    time.sleep(hold_time)
    if modifier:
        ctypes.windll.user32.keybd_event(modifiers[modifier], 0, 0x0002, 0)
    ctypes.windll.user32.keybd_event(code, 0, 0x0002, 0)


def get_words(x: int, y: int, length: int, word: str, words: list[str], used_squares: list[tuple], puzzle: list[list[str]], dictionary: dict[str, Any]) -> None:
    """
    Get a word starting from a position and to a length
    Note: Recursive
    :param x: X Position
    :param y: Y Position
    :param length: Length of word to find
    :param word: For recursion, should start empty
    :param words: List of found words
    :param used_squares: For recursion, track used positions
    :param puzzle: Puzzle matrix
    :param dictionary: Hierarchy dictionary
    :return: (void)
    """
    row_count = len(puzzle)

    # If we haven't reached the end of the path, move to the next positions and recurse
    if length > 1:
        for pos_x in (-1, 0, 1):
            for pos_y in (-1, 0, 1):
                temp_x: int = x + pos_x
                temp_y: int = y + pos_y
                # Are the coordinates in bounds?
                if 0 <= temp_x < row_count and 0 <= temp_y < row_count:
                    if (temp_x, temp_y) not in used_squares:
                        new_used_squares: list[tuple] = used_squares.copy()
                        new_used_squares.append((temp_x, temp_y))
                        # Check that part of the word is in the dictionary before continuing
                        if options.filter:
                            regex: re.Match[str] = re.match(options.filter, word)
                        else:
                            regex: bool = True
                        if lookup_word(dictionary, word + puzzle[temp_x][temp_y]) and regex:
                            get_words(temp_x, temp_y, length - 1, word + puzzle[temp_x][temp_y], words,
                                      new_used_squares, puzzle, dictionary)

    # Append the word to the list
    if length <= 1:
        if lookup_word(dictionary, word + '\n'):
            words.append(word)
        return


def lookup_word(dictionary: dict[str, str | dict], word: str) -> bool:
    """
    Find full or partial record of word in dictionary
    :param dictionary: Hierarchy dictionary
    :param word: String to locate
    :return: Found
    """
    for letter in word:
        try:
            dictionary = dictionary[letter]
        except KeyError:
            return False
    return True


def progressbar(position: int = 0, maximum: int = 100, title: str = 'Loading', width: int | None = None) -> None:
    """
    Draw a very simple progress bar to the width specified
    :param position: Position relative to max value
    :param maximum:  Max position
    :param title:  Title at the end of the progress
    :param width: Display width of the bar
    :return:
    """
    bar_width: int = width - 3 - len(title)
    bar_fill: int = int(position / maximum * bar_width)
    bar_empty: int = bar_width - bar_fill

    print(f'{"█" * bar_fill}{"░" * bar_empty} | {title}', end='\r', file=sys.stderr)


def print_error(message: str, detail: str, exit_puzzle: bool = True) -> None:
    """
    Print error message and exit
    :param message: Error message
    :param detail: Details of error message
    :param exit_puzzle: Exit?
    :return:
    """
    if options.json:
        print(json.dumps({'error': str(message), 'detail': detail}))
    else:
        print(f'Error: {message}\n\t{detail}')

    if exit_puzzle:
        exit(1)


if __name__ == '__main__':

    def parser_formatter(format_class: type[argparse.RawTextHelpFormatter], **kwargs) -> callable:
        """
        Use a raw parser to use line breaks, etc
        :param format_class: formatting class
        :param kwargs: kwargs for class
        :return: formatting class
        """
        try:
            return lambda prog: format_class(prog, **kwargs)
        except TypeError:
            return format_class


    def number_range(low: int, high: int, obj_type: type = int) -> Any:
        """
        Validate integer is between low and high values
        :param low: Low range
        :param high: High range
        :param obj_type: Data type, ex int, float
        :return: argument, exception
        """

        def number_range_parser(argument):
            try:
                argument = obj_type(argument)
            except ValueError:
                argparse.ArgumentError(f'Must be of type {obj_type.__name__}')

            if low <= argument <= high:
                return argument
            else:
                parser.error(f'Value is not in the range of {low} and {high}')

        return number_range_parser


    parser = argparse.ArgumentParser(
        description='%(prog)s will find all the words in a given/generated puzzle using a dictionary of choice.',
        formatter_class=parser_formatter(argparse.RawTextHelpFormatter, indent_increment=4, max_help_position=12,
                                         width=160))

    # Dictionary/word/phrase
    dictionary_group = parser.add_argument_group(title='Dictionary',
                                                 description=None)
    dictionary_group.add_argument('-d', '--dict', type=argparse.FileType('rb'),
                                  action='store', dest='dictionary',
                                  default=os.path.join(os.path.dirname(__file__), 'dictionary.hd'),
                                  help='dictionary file to use, in .hd format, See convert_dictionary.py\n'
                                       'default: %(default)s')

    # Puzzle
    puzzle_group = parser.add_argument_group(title='Puzzle',
                                             description='Specify or generate a puzzle')
    puzzle_group.add_argument('-p', '--puzzle', dest='puzzle',
                              action='store', nargs='*',
                              help='puzzle in order of appearance, space separated, top-left to bottom-right\n'
                                   'default: randomly generated\n'
                                   'example: a b c d e f g h qu')

    puzzle_group.add_argument('--randomise', dest='randomise',
                              action='store_true',
                              help='randomise specified puzzle letters')

    puzzle_group.add_argument('-s', '--size', type=int,
                              action='store', dest='puzzle_size', default=4,
                              help='puzzle size if randomly generated randomly generated\n'
                                   'default: %(default)s\n'
                                   'example: 4 is 4x4')

    # Display
    display_group = parser.add_argument_group(title='Display',
                                              description='Viewing and sorting options')
    display_group.add_argument('-a', '--alpha',
                               action='store_true', dest='order_alpha', default=False,
                               help='display words ordered alphabetical\n'
                                    'default: %(default)s')
    display_group.add_argument('-o', '--order-ascending',
                               action='store_true', dest='order_size', default=False,
                               help='display words ordered by size ascending, compatible with -a/--alpha\n'
                                    'default: %(default)s')
    display_group.add_argument('-r', '--order-descending',
                               action='store_true', dest='order_size_r', default=False,
                               help='display words ordered by size descending, compatible with -a/--alpha\n'
                                    'default: %(default)s')
    display_group.add_argument('--list',
                               action='store_true', dest='list', default=False,
                               help='display as list instead of columns\n'
                                    'default: %(default)s')
    display_group.add_argument('--json',
                               action='store_true', dest='json', default=False,
                               help='display as JSON\n')

    # Filtering
    filter_group = parser.add_argument_group(title='Filtering',
                                             description='Filter down the results by length, contents and REGEX')
    filter_group.add_argument('-l', '--length', type=int,
                              action='store', dest='length', default=None,
                              help='Only a fixed length\n'
                                   'Note: Overrides minimum and maximum values')
    filter_group.add_argument('-M', '--max', type=number_range(1, 32),
                              action='store', dest='length_max', default=None,
                              help='maximum word length \n'
                                   'default: puzzle size or 32 whichever is less')
    filter_group.add_argument('-m', '--min', type=number_range(1, 32),
                              action='store', dest='length_min', default=3,
                              help='minimum word length\n'
                                   'default: %(default)s')
    filter_group.add_argument('-C', '--contains',
                              action='store', dest='filter_contains', default=None, nargs='+',
                              metavar='PATTERN',
                              help='filter results containing the patterns in any order\n'
                                   'example:\n'
                                   'te a s can find: teas and steady but not seats\n'
                                   'default: %(default)s')
    filter_group.add_argument('-f', '--filter',
                              action='store', dest='filter', default=None,
                              metavar='REGEX',
                              help='filter results after contains filter\n'
                                   'note: Only exact matches are found. \n'
                                   'examples:\n'
                                   'z will find only z, z.* will find all words beginning with z \n'
                                   '.{3}|.{5} will find 3 or 5 letter words\n'
                                   'default: %(default)s')

    # Emulate the keyboard
    keyboard_group = parser.add_argument_group(title='Keyboard emulations',
                                               description='Emulate key presses in Windows')
    keyboard_group.add_argument('-e', '--enter', type=int,
                                action='store', dest='enter', default=None, nargs='?',
                                const=4,
                                metavar='WAIT_TIME',
                                help='after x seconds delay, start entering with keyboard\n'
                                     'this is the time to switch to the app to receive keyboard strokes\n'
                                     'WARNING: It is highly recommended that you leave your console window accessible\n'
                                     'default: %(const)s\n'
                                     'note: Windows ONLY')
    keyboard_group.add_argument('-S', '--speed', type=number_range(-1, SPEED_STEPS),
                                action='store', dest='speed', default=int(SPEED_STEPS * 0.95),
                                help=f'set the keyboard speed from -1 to {SPEED_STEPS} when using -e/--enter \n'
                                     'note: -1 will be interpreted as random between each action. \n'
                                     'note: some programs have issues with a very high speeds\n'
                                     'default: %(default)s')
    keyboard_group.add_argument('-i', '--interrupt-off',
                                action='store_true', dest='interrupt', default=False,
                                help='do not exit when returning to the window where the code ran from when using -e/--enter \n'
                                     'default: %(default)s')

    options = parser.parse_args()

    main()
