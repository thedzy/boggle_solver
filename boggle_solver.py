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
__version__ = "1.1"
__maintainer__ = "thedzy"
__email__ = "thedzy@hotmail.com"
__status__ = "Developer"

import argparse
import math
import os
import random
import pickle


def main():
    tree_dictionary = pickle.load(options.dictionary)
    options.dictionary.close()

    # Get/make the puzzle
    if options.puzzle is None:
        letters = ''.join(chr(i + 97) for i in range(26))
        row_count = options.puzzle_size
        puzzle = []
        for row in range(row_count):
            puzzle.append(list(random.choice(letters) for _ in range(row_count)))
    else:
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

    if length_min < 2:
        length_min = 2

    # Show the puzzle so tht the user can see what is being solved
    print('Puzzle: ')
    print('\n'.join([''.join(['{:4}'.format(item) for item in row]) for row in puzzle]))
    print('=' * 40)

    # Loop through to find the words
    words_valid = []
    for index_x in range(0, row_count):
        for index_y in range(0, row_count):
            x, y = (index_x, index_y)

            for length in range(length_min, length_max + 1):
                words = []
                print('Finding words starting with {} and of {} characters in length'.format(puzzle[x][y].upper(),
                                                                                             length), end='\r')
                get_words(x, y, length, puzzle[x][y], words, [(x, y)], puzzle, tree_dictionary)

                words_valid.extend(words)

    # Remove duplicates and sort
    words_valid = list(set(words_valid))
    words_valid.sort()
    if options.order_size:
        words_valid.sort(key=len)
    print('Words found that are contained in "{}" {}'.format(options.dictionary.name, ' ' * 40))

    # Print
    if len(words_valid) > 0:
        if options.columns:
            divider = ' | '
            terminal_width, _ = os.get_terminal_size()
            column_width = len(max(words_valid, key=len)) + len(divider)  # 3 to offset the spacer
            columns = int((terminal_width - len(divider)) / column_width)
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
        print('Found {} words found of {} characters in length'.format(len(words_valid), length_max))
    else:
        print('Found {} words found between {} and {} characters in length'.format(len(words_valid), length_min,
                                                                                   length_max))


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
                if 0 <= temp_x < row_count and temp_y >= 0 and temp_y < row_count:
                    if (temp_x, temp_y) not in used_squares:
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


    parser = argparse.ArgumentParser(
        description='Will find all the words in a given/generated puzzle using a dictionary of choice.',
        formatter_class=parser_formatter(argparse.RawTextHelpFormatter, indent_increment=4, max_help_position=12,
                                         width=160))

    parser.add_argument('-l', '--length', type=int,
                        action='store', dest='length', default=None,
                        help='Only a fixed length'
                             '\nNote: Overrides minimum and maximum values')

    parser.add_argument('-x', '--max', type=int,
                        action='store', dest='length_max', default=None,
                        help='Maximum word length, '
                             '\nDefault: puzzle size (not recommended to use default)')
    parser.add_argument('-m', '--min', type=int,
                        action='store', dest='length_min', default=3,
                        help='Minimum word length'
                             '\nDefault: %(default)s')

    # Dictionary/word/phrase
    parser.add_argument('-d', '--dict', type=argparse.FileType('rb'),
                        action='store', dest='dictionary',
                        default=os.path.join(os.path.dirname(__file__), 'dictionary.hd'),
                        help='Dictionary file to use, in .hd format, See convert_dictionary.py'
                             '\nDefault: %(default)s')

    # Puzzle
    parser.add_argument('-p', '--puzzle', dest='puzzle',
                        action='store', nargs='*',
                        help='Puzzle in order of appearance, space separated, top-left to bottom-right'
                             '\nDefault: randomly generated'
                             '\nExample: a b c d e f g h qu')

    parser.add_argument('-s', '--size', type=int,
                        action='store', dest='puzzle_size', default=4,
                        help='Puzzle size if randomly generated randomly generated'
                             '\nDefault: %(default)s'
                             '\nExample: 4 is 4x4')

    # Display
    parser.add_argument('-o', '--order-size',
                        action='store_true', dest='order_size', default=False,
                        help='Display words ordered by size'
                             '\nDefault: %(default)s')

    parser.add_argument('-c', '--columns',
                        action='store_true', dest='columns', default=False,
                        help='Display as columns'
                             '\nDefault: %(default)s')
    options = parser.parse_args()

    main()
