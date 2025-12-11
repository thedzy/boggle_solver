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
__version__ = "1.1.1"
__maintainer__ = "thedzy"
__email__ = "thedzy@hotmail.com"
__status__ = "Development"

import argparse
import pickle
import sys
from pathlib import Path
from typing import Any
import pprint

try:
    from spylls.hunspell.dictionary import Dictionary
    from spylls.hunspell.dictionary import Word
except:
    print('Did not import spylls')
    pass


def main():
    # Initialise
    tree_dictionary: dict[str, dict | str] = {}

    words: list[str] = []
    # If given a source, then convert, otherwise load and test
    if all([options.new_dictionary, options.source]):
        print(f'Creating {options.new_dictionary.name}')
        if Path(options.new_dictionary.name).is_file():
            yn: str = ''
            while not yn.startswith('n') and not yn.startswith('y'):
                yn: str = input('Write file? (y/n) ')
            if yn.startswith('n'):
                exit()

        if options.source.name.endswith('.txt'):
            options.source.seek(0)
            words: list[str] = options.source.readlines()
        if options.source.name.endswith('.dic'):
            if 'spylls' not in sys.modules:
                print('Requires spylls module')
                exit(0)

            words: set[str] = set()
            dictionary_parent: Path = Path(options.source.name).parent
            dictionary_stem: str = Path(options.source.name).stem

            dictionary: Dictionary = Dictionary.from_files(f'{dictionary_parent / dictionary_stem}')
            for word_entry in dictionary.dic.words:
                variants: set[str] = get_variants(word_entry, dictionary.aff)
                words.update(variants)

        options.source.close()

        if options.add_words:
            for add_word in options.add_words:
                words.append(add_word + '\n')

        for word in words:
            if not word.rstrip('\n').isalpha():
                word = ''.join(char for char in word if char.isalnum())
            add_to_dictionary(tree_dictionary, word.lower())

        pickle.dump(tree_dictionary, options.new_dictionary)
    if options.test_dictionary is not None:
        print(f'Loading {options.test_dictionary.name}')
        tree_dictionary = pickle.load(options.test_dictionary)

    if options.word is not None:
        pprint.pp(tree_dictionary.keys())
        if options.exact:
            print(f'Looking for exact match of {options.word}')
            found: bool = lookup_word(tree_dictionary, options.word + '\n')
        else:
            print(f'Looking for partial match of {options.word}')
            found: bool = lookup_word(tree_dictionary, options.word)
        print(f'Found match for {options.word}: {found}')


def get_variants(word_entry: Any, affixes) -> set[str]:
    """
    Added prefixes and suffixes
    :param word_entry: dictionary item
    :param affixes: affix lookup for dictionary
    :return: variants
    """
    result_words: set[str] = set()

    if affixes.FORBIDDENWORD and affixes.FORBIDDENWORD in word_entry.flags:
        return result_words

    if not (affixes.NEEDAFFIX and affixes.NEEDAFFIX in word_entry.flags):
        result_words.add(word_entry.stem + '\n')

    suffixes: list[Any] = [
        suffix for flag in word_entry.flags for suffix in affixes.SFX.get(flag, [])
        if suffix.cond_regexp.search(word_entry.stem)
    ]
    prefixes: list[Any] = [
        prefix for flag in word_entry.flags for prefix in affixes.PFX.get(flag, [])
        if prefix.cond_regexp.search(word_entry.stem)
    ]

    for suffix in suffixes:
        root: str = word_entry.stem[0:-len(suffix.strip)] if suffix.strip else word_entry.stem
        suffixed: str = root + suffix.add

        if not (affixes.NEEDAFFIX and affixes.NEEDAFFIX in suffix.flags):
            result_words.add(suffixed + '\n')

        secondary_suffixes: list[Any] = [
            secondary_suffix for flag in suffix.flags for secondary_suffix in affixes.SFX.get(flag, [])
            if secondary_suffix.cond_regexp.search(suffixed)
        ]
        for secondary_suffix in secondary_suffixes:
            root: str = suffixed[0:-len(secondary_suffix.strip)] if secondary_suffix.strip else suffixed
            result_words.add(root + secondary_suffix.add + '\n')

    for prefix in prefixes:
        root: str = word_entry.stem[len(prefix.strip):]
        prefixed: str = prefix.add + root
        if not (affixes.NEEDAFFIX and affixes.NEEDAFFIX in prefix.flags):
            result_words.add(prefixed + '\n')

        if prefix.crossproduct:
            additional_suffixes: list[Any] = [
                suffix for flag in prefix.flags for suffix in affixes.SFX.get(flag, [])
                if suffix.crossproduct
                   and suffix not in suffixes
                   and suffix.cond_regexp.search(prefixed)
            ]
            for suffix in suffixes + additional_suffixes:
                root: str = prefixed[0:-len(suffix.strip)] if suffix.strip else prefixed
                suffixed: str = root + suffix.add
                result_words.add(suffixed + '\n')

                secondary_suffixes: list[Any] = [
                    secondary_suffix
                    for flag in suffix.flags
                    for secondary_suffix in affixes.SFX.get(flag, [])
                    if secondary_suffix.crossproduct
                       and secondary_suffix.cond_regexp.search(suffixed)
                ]
                for secondary_suffix in secondary_suffixes:
                    root: str = suffixed[0:-len(secondary_suffix.strip)] if secondary_suffix.strip else suffixed
                    result_words.add(root + secondary_suffix.add + '\n')

    return result_words


def add_to_dictionary(dictionary: dict[str, dict | str], word: str) -> None:
    """
    Add word to the dictionary
    :param dictionary:  Hierarchy of letters
    :param word: Word to add
    :return:
    """
    if len(word) != 0:
        if word[0] not in dictionary:
            dictionary[word[0]] = {}
        add_to_dictionary(dictionary[word[0]], word[1:])


def lookup_word(dictionary: dict[str, str | dict], word: str) -> bool:
    """
    Find full or partial record of word in dictionary
    :param dictionary: Hierarchy dictionary
    :param word: String to locate
    :return: Found
    """
    trie_node: dict[str, str | dict] = dictionary
    for letter in word:
        trie_node: [dict | None] = trie_node.get(letter)
        if trie_node is None:
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


    parser = argparse.ArgumentParser(description='Convert a dictionary to a hierarchy dictionary\n'
                                                 'If no source, test the dictionary'
                                                 'If you are looking for a dictionary check http://app.aspell.net/create',
                                     formatter_class=parser_formatter(
                                         argparse.RawTextHelpFormatter,
                                         indent_increment=4, max_help_position=12, width=160))

    # Source
    parser.add_argument('-s', '--source', type=argparse.FileType('r'),
                        action='store', dest='source', default=None,
                        metavar='PATH',
                        help='source dictionary to create the hierarchy dictionary from')
    parser.add_argument('-a', '--add',
                        action='store', dest='add_words', default=None, nargs='*',
                        metavar='ADDITIONAL_WORD',
                        help='words to add in addition to the source')

    # Destination
    parser.add_argument('-d', '--new-dictionary', type=argparse.FileType('wb+'),
                        action='store', dest='new_dictionary', default=None,
                        metavar='PATH',
                        help='dictionary to create')

    parser.add_argument('-D', '--test-dictionary', type=argparse.FileType('rb'),
                        action='store', dest='test_dictionary', default=None,
                        metavar='PATH',
                        help='dictionary to test')

    # Lookups
    parser.add_argument('-w', '--word',
                        action='store', dest='word', default=None,
                        metavar='WORD',
                        help='word or partial word to lookup')
    parser.add_argument('-e', '--exact',
                        action='store_true', dest='exact', default=False,
                        help='match only whole word\n'
                             'default: %(default)s')

    options = parser.parse_args()

    main()
