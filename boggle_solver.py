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
__version__ = "1.4"
__maintainer__ = "thedzy"
__email__ = "thedzy@hotmail.com"
__status__ = "Development"

import argparse
import ctypes
import math
import os
import pickle
import platform
import random
import re
import time

SPEED_STEPS = 50


def main():
    if 'windows' in platform.platform().lower():
        # Capture the window that we are starting with, if we return we can send interrupt
        start_window = ctypes.windll.user32.GetForegroundWindow()

    # Load dictionary
    try:
        tree_dictionary = pickle.load(options.dictionary)
        options.dictionary.close()
    except (UnicodeDecodeError, EOFError):
        print('Dictionary may be corrupt or not a dictionary')
        print('Verify file or reprocess dictionary')
        exit()
    except Exception as err:
        print('Error loading dictionary:')
        print('\t', err)
        exit()

    # Validate regex before continuing
    if options.filter:
        try:
            pattern = re.compile(options.filter, re.IGNORECASE)
        except re.error as err:
            print('Error in regex statement:')
            print('\t', err.msg.title())
            exit()

    # Get/make the puzzle
    if options.puzzle is None:
        letters = ''.join(chr(i + 97) for i in range(26))
        row_count = options.puzzle_size
        puzzle = []
        for _ in range(row_count):
            puzzle.append(list(random.choice(letters) for _ in range(row_count)))
    else:
        puzzle_length = len(options.puzzle)
        # If length of one, lets assume they characters are not spaced
        if puzzle_length == 1:
            options.puzzle = list(options.puzzle[0])
            puzzle_length = len(options.puzzle)

        row_count = math.sqrt(puzzle_length)

        if int(row_count) != row_count:
            print('Puzzle must be square')
            print('Size given is {}, should be 3, 9, 16, 25, ...'.format(puzzle_length))
            exit()

        row_count = int(row_count)

        puzzle = []
        for puzzle_x in range(0, row_count):
            row = []
            for puzzle_y in range(0, row_count):
                row.append(options.puzzle[puzzle_x * row_count + puzzle_y].lower())
            puzzle.append(row)

    # Set the max/min length of a word
    if options.length is None:
        if options.length_max is None:
            # Max word length of the puzzle size or 32, whichever is smaller
            length_max = min(row_count ** 2, 32)
            print('WARNING: Max word length is {}'.format(length_max))
        else:
            length_max = options.length_max

        if options.length_min is None:
            length_min = 3
        else:
            length_min = options.length_min
    else:
        length_min = options.length
        length_max = options.length

    if length_max > (row_count ** 2):
        length_max = row_count ** 2
        print('Max length exceeds puzzle size, setting to {} instead'.format(length_max))

    if length_min > length_max:
        length_min = length_max

    if length_min < 1:
        length_min = 1

    if length_max < 1:
        length_max = 1

    # Show the puzzle so tht the user can see what is being solved
    print('Puzzle: ')
    print('\n'.join([''.join(['{:4}'.format(item) for item in row]) for row in puzzle]))
    print('=' * 40)

    # Loop through to find the words
    words_valid = []
    for index_x in range(0, row_count):
        for index_y in range(0, row_count):
            x, y = (index_x, index_y)

            for length in range(1, length_max + 1):
                words = []
                print('Finding words starting with {} and of {} characters in length'.format(puzzle[x][y].upper(),
                                                                                             length), end='\r')
                get_words(x, y, length, puzzle[x][y], words, [(x, y)], puzzle, tree_dictionary)
                words_valid.extend(words)

    # Remove duplicates, filter and sort
    words_valid = sorted(set(words_valid), key=words_valid.index)
    words_valid = list(filter(lambda word_valid: length_min <= len(word_valid) <= length_max, words_valid))

    # If a contains filter is used
    if options.filter_contains:
        print('Filtering words with patterns "{}"{}'.format(', '.join(options.filter_contains), ' ' * 80))
        pattern_list = ['^.*'] + ['(?=.*{})'.format(x) for x in options.filter_contains] + ['.*']
        pattern2 = re.compile(''.join(pattern_list), re.IGNORECASE)
        for word in words_valid[:]:
            if not pattern2.fullmatch(word):
                words_valid.remove(word)

    # If a filter is used
    if options.filter:
        print('Filtering with "{}" {}'.format(options.filter, ' ' * 80))
        for word in words_valid[:]:
            if not pattern.fullmatch(word):
                words_valid.remove(word)
    if options.order_alpha:
        words_valid.sort()
    if options.order_size or options.order_size_r:
        words_valid.sort(key=len, reverse=options.order_size_r)
    print('Words found that are contained in "{}"{}'.format(options.dictionary.name, ' ' * 80))

    # Print words
    if len(words_valid) > 0:
        if not options.list:
            divider = ' | '
            try:
                terminal_width, _ = os.get_terminal_size()
            except OSError:
                terminal_width = 80
            column_width = len(max(words_valid, key=len)) + len(divider)
            columns = int(((terminal_width - 1) - len(divider)) / column_width)
            column_height = int(len(words_valid) / columns) + 1

            words_valid_columned = []
            start, end = 0, 0
            while end < len(words_valid):
                end = start + column_height
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

    # Print word count
    if length_min is length_max:
        print('Found {} words found of {} characters in length and matching filters'.format(
            len(words_valid), length_max))
    else:
        print('Found {} words found between {} and {} characters in length and matching filters'.format(
            len(words_valid), length_min, length_max))

    # If emulating keyboard
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
                        speed = random.random()

                    win_press_key(letter, None, speed / 2)

                # Send return
                print('Entering:', word)
                win_press_key(None, None, speed / 2)

                # Pause between each word to give program time to score
                time.sleep(speed)


def win_press_key(key=None, modifier=None, hold_time=0.1):
    """
    Emulate a keyboard press, <enter> default
    :param key: (string) Single character to emulate
    :param modifier: (string) Hold modifier key during key press
    :param hold_time: (int) Key hold time
    :return: (void)
    """
    modifiers = {
        'shift': 0x10,
        'ctrl': 0x11,
        'alt': 0x12,
    }
    # If no key, return
    code = ord(key.upper()) if key else 0x0D
    if modifier:
        ctypes.windll.user32.keybd_event(modifiers[modifier], 0, 0, 0)
    ctypes.windll.user32.keybd_event(code, 0, 0, 0)
    time.sleep(hold_time)
    if modifier:
        ctypes.windll.user32.keybd_event(modifiers[modifier], 0, 0x0002, 0)
    ctypes.windll.user32.keybd_event(code, 0, 0x0002, 0)


def get_words(x, y, length, word, words, used_squares, puzzle, dictionary):
    """
    Get a word starting from a position and to a length
    Note: Recursive
    :param x: (int) X Position
    :param y:  (int) Y Position
    :param length: (int) Length of word to find
    :param word: (string) For recursion, should start empty
    :param words: (list)(string) List of found words
    :param used_squares: (list)(tuples) For recursion, track used positions
    :param puzzle: (list)(list)(string) Puzzle matrix
    :param dictionary: (dict) Hierarchy dictionary
    :return: (void)
    """
    row_count = len(puzzle)

    # If we haven't reached the end of the path, move to the next positions and recurse
    if length > 1:
        for pos_x in (-1, 0, 1):
            for pos_y in (-1, 0, 1):
                temp_x = x + pos_x
                temp_y = y + pos_y
                # Are the coordinates in bounds?
                if 0 <= temp_x < row_count and 0 <= temp_y < row_count:
                    if (temp_x, temp_y) not in used_squares:
                        new_used_squares = used_squares.copy()
                        new_used_squares.append((temp_x, temp_y))
                        # Check that part of the word is in the dictionary before continuing
                        if lookup_word(dictionary, word + puzzle[temp_x][temp_y]):
                            get_words(temp_x, temp_y, length - 1, word + puzzle[temp_x][temp_y], words,
                                      new_used_squares, puzzle, dictionary)

    # Append the word to the list
    if length <= 1:
        if lookup_word(dictionary, word + '\n'):
            words.append(word)
        return


def lookup_word(dictionary, word):
    """
    Find full or partial record of word in dictionary
    :param dictionary: (dict) Hierarchy dictionary
    :param word: (string) String to locate
    :return: (bool) Found
    """
    for letter in word:
        try:
            dictionary = dictionary[letter]
        except KeyError:
            return False
    return True


if __name__ == '__main__':

    def parser_formatter(format_class, **kwargs):
        """
        Use a raw parser to use line breaks, etc
        :param format_class: (class) formatting class
        :param kwargs: (dict) kwargs for class
        :return: (class) formatting class
        """
        try:
            return lambda prog: format_class(prog, **kwargs)
        except TypeError:
            return format_class


    def number_range(low, high, obj_type=int):
        """
        Validate integer is between low and high values
        :param low: (int) Low range
        :param high: (int) High range
        :param obj_type: (class) Data type, ex int, float
        :return: argument, exception
        """

        def number_range_parser(argument):
            try:
                argument = obj_type(argument)
            except ValueError:
                argparse.ArgumentError('Must be of type {}'.format(obj_type.__name__))

            if low <= argument <= high:
                return argument
            else:
                parser.error('Value is not in the range of {} and {}'.format(low, high))

        return number_range_parser


    parser = argparse.ArgumentParser(
        description='Will find all the words in a given/generated puzzle using a dictionary of choice.',
        formatter_class=parser_formatter(argparse.RawTextHelpFormatter, indent_increment=4, max_help_position=12,
                                         width=160))

    parser.add_argument('-l', '--length', type=int,
                        action='store', dest='length', default=None,
                        help='Only a fixed length\n'
                             'Note: Overrides minimum and maximum values')
    parser.add_argument('-M', '--max', type=int,
                        action='store', dest='length_max', default=None,
                        help='Maximum word length \n'
                             'Default: puzzle size or 32 whichever is less')
    parser.add_argument('-m', '--min', type=int,
                        action='store', dest='length_min', default=3,
                        help='Minimum word length\n'
                             'Default: %(default)s')

    # Dictionary/word/phrase
    parser.add_argument('-d', '--dict', type=argparse.FileType('rb'),
                        action='store', dest='dictionary',
                        default=os.path.join(os.path.dirname(__file__), 'dictionary.hd'),
                        help='Dictionary file to use, in .hd format, See convert_dictionary.py\n'
                             'Default: %(default)s')

    # Puzzle
    parser.add_argument('-p', '--puzzle', dest='puzzle',
                        action='store', nargs='*',
                        help='Puzzle in order of appearance, space separated, top-left to bottom-right\n'
                             'Default: randomly generated\n'
                             'Example: a b c d e f g h qu')
    parser.add_argument('-s', '--size', type=int,
                        action='store', dest='puzzle_size', default=4,
                        help='Puzzle size if randomly generated randomly generated\n'
                             'Default: %(default)s\n'
                             'Example: 4 is 4x4')

    # Display
    parser.add_argument('-a', '--alpha',
                        action='store_true', dest='order_alpha', default=False,
                        help='Display words ordered alphabetical\n'
                             'Default: %(default)s')
    parser.add_argument('-o', '--order-ascending',
                        action='store_true', dest='order_size', default=False,
                        help='Display words ordered by size ascending, compatible with -a/--alpha\n'
                             'Default: %(default)s')
    parser.add_argument('-r', '--order-descending',
                        action='store_true', dest='order_size_r', default=False,
                        help='Display words ordered by size descending, compatible with -a/--alpha\n'
                             'Default: %(default)s')
    parser.add_argument('--list',
                        action='store_true', dest='list', default=False,
                        help='Display as list instead of columns\n'
                             'Default: %(default)s')
    parser.add_argument('-C', '--contains',
                        action='store', dest='filter_contains', default=None, nargs='+',
                        metavar='PATTERN',
                        help='Filter results containing the patterns in any order\n'
                             'Example:\n'
                             'te a s can find: teas and steady but not seats\n'
                             'Default: %(default)s')
    parser.add_argument('-f', '--filter',
                        action='store', dest='filter', default=None,
                        metavar='REGEX',
                        help='Filter results after contains filter\n'
                             'Note: Only exact matches are found. \n'
                             'Examples:\n'
                             'z will find only z, z.* will find all words beginning with z \n'
                             '.{3}|.{5} will find 3 or 5 letter words\n'
                             'Default: %(default)s')

    # Emulate the keyboard
    parser.add_argument('-e', '--enter', type=int,
                        action='store', dest='enter', default=None, nargs='?',
                        const=4,
                        metavar='WAIT_TIME',
                        help='After x seconds delay, start entering with keyboard\n'
                             'This is the time to switch to the app to receive keyboard strokes\n'
                             'WARNING: It is highly recommended that you leave your console window accessible\n'
                             'Default: %(const)s\n'
                             'Note: Windows ONLY')
    parser.add_argument('-S', '--speed', type=number_range(-1, SPEED_STEPS),
                        action='store', dest='speed', default=int(SPEED_STEPS * 0.95),
                        help='Set the keyboard speed from -1 to {} when using -e/--enter \n'.format(SPEED_STEPS) +
                             'Note: -1 will be interpreted as random between each action. \n'
                             'Note: Some programs have issues with a very high speeds\n'
                             'Default: %(default)s')
    parser.add_argument('-i', '--interrupt-off',
                        action='store_true', dest='interrupt', default=False,
                        help='Do not exit when returning to the window where the code ran from when using -e/--enter \n'
                             'Default: %(default)s')

    options = parser.parse_args()

    main()
