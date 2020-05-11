#!/usr/bin/env python3
"""
Script:	convert_dictionary.py
Date:	2020-04-11

Platform: macOS/Windows/Linux

Description:
Create a dictionary for the boggle puzzle solver
Converts a list of words to a hierarchy format for fast parsing

"""
__author__ = "thedzy"
__copyright__ = "Copyright 2020, thedzy"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "thedzy"
__email__ = "thedzy@hotmail.com"
__status__ = "Developer"

import json
import pickle
import argparse

def main():
    # Initialise
    tree_dictionary = {}

    # If given a source, then convert, otherwise load and test
    if options.source is not None:
        print('Creating')
        words = options.source.read().splitlines()
        options.source.close()

        for word in words:
            add_to_dictionary(tree_dictionary, word.lower())

        pickle.dump(tree_dictionary, options.dictionary)
    else:
        tree_dictionary = pickle.load(options.dictionary)

    if options.word is not None:
        print('Found match for {}: {}'.format(options.word, lookup_word(tree_dictionary, options.word)))


def add_to_dictionary(dictionary, word):
    """
    Add word to the dictionary
    :param dictionary: (dict) Hierarchy of letters
    :param word: (string) Word to add
    :return: (void)
    """
    if len(word) != 0:
        if word[0] not in dictionary:
            dictionary[word[0]] = {}
        add_to_dictionary(dictionary[word[0]], word[1:])


def lookup_word(dictionary, word):
    """
    Find a word or start of a word in the dictionary
    :param dictionary: (dict) Hierarchy of letters
    :param word: (string) Word to lookup
    :return: (bool) Found status
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


    parser = argparse.ArgumentParser(description='Convert a dictionary to a hierarchy dictionary',
                                     formatter_class=parser_formatter(
                                         argparse.RawTextHelpFormatter,
                                         indent_increment=4, max_help_position=12, width=160))

    parser.add_argument('-s', '--source', type=argparse.FileType('r'),
                        action='store', dest='source', default=None,
                        metavar='PATH',
                        help='Source dictionary to create the hierarchy dictionary from')\

    parser.add_argument('-d', '--dictionary', type=argparse.FileType('rb+'),
                        action='store', dest='dictionary', default=None,
                        metavar='PATH',
                        help='Dictionary to loaded or created',
                        required=True)

    parser.add_argument('-w', '--word',
                        action='store', dest='word', default=None,
                        metavar='WORD',
                        help='Word to lookup')

    options = parser.parse_args()

    main()
