#!/usr/bin/env python3
"""
Script:	boggle_solver.py
Date:	2020-04-11

Platform: macOS/Windows/Linux

Description:
Visualise a dictionary structure starting from

"""
__author__ = "thedzy"
__copyright__ = "Copyright 2020, thedzy"
__license__ = "GPL"
__version__ = "1.6.1"
__maintainer__ = "thedzy"
__email__ = "thedzy@hotmail.com"
__status__ = "Development"

import argparse
import configparser
import mmap
import pickle
from configparser import ConfigParser
from pathlib import Path
from typing import Any


def main() -> None:
    # Load dictionary
    try:
        print(f'Displaying {options.dictionary.name}')
        with open(options.dictionary.name, 'rb') as file_handle:
            with mmap.mmap(file_handle.fileno(), 0, access=mmap.ACCESS_READ) as memory_map:
                tree_dictionary = pickle.loads(memory_map)
    except (UnicodeDecodeError, EOFError):
        print('Dictionary may be corrupt or not a dictionary',
              'Verify file or reprocess dictionary')
        exit()
    except Exception as err:
        print(f'Error loading dictionary:', str(err))
        exit()

    word: str = options.word
    sample: dict[str, str | dict] = {}
    current: dict[str, str | dict] = sample

    for letter in word[:-1]:
        current[letter]: dict[str, str | dict] = {}
        current: dict[str, str | dict] = current[letter]

    current[word[-1]]: dict[str, str | dict] = lookup_fragment(tree_dictionary, options.word)
    print_tree(sample, indent='', style=options.style - 1,
               quote='', equals='=',
               key_colour=options.key_colour, key_bold=options.key_bold, key_inverted=options.key_inverted,
               value_colour=options.value_colour, value_bold=options.value_bold, value_inverted=options.value_inverted,
               other_colour=options.other_colour, other_bold=options.other_bold, other_inverted=options.other_inverted,
               printer=print, width=options.width, display_type=False
               )


def lookup_fragment(dictionary: dict[str, str | dict], word: str) -> dict[str, str]:
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
            return {}
    return trie_node


def print_tree(dict_obj: dict, indent: str = '', style: int = 0, null: str = None,
               quote: str = '\'', equals='=',
               key_colour: str = 'blue', key_bold: bool = True, key_inverted: bool = False,
               value_colour: str = 'green', value_bold: bool = True, value_inverted: bool = False,
               other_colour: str = 'white', other_bold: bool = False, other_inverted: bool = False,
               printer: callable = print, width: int = 1, display_type: bool = False
               ) -> None:
    """
    Pretty print a dictionary as a tree (recursive)
    :param dict_obj: (dict) Object to parse
    :param indent: (int) Indent level
    :param style: (list) Hide value if value does not match pattern
    :param null: String to display for null values
    :param quote: String to display for quotes
    :param key_colour: Name of colour od escape sequence
    :param key_bold: Use bold colours
    :param key_inverted: Use inverted colours
    :param value_colour: Name of colour od escape sequence
    :param value_bold: Use bold colours
    :param value_inverted: Use inverted colours
    :param other_colour: Name of colour od escape sequence
    :param other_bold: Use bold colours
    :param other_inverted: Use inverted colours
    :param printer: Function to use for printing (ex logger.info)
    :param width: The indent width
    :param display_type: Display the value type with the value
    :return: None
    """
    kwargs = {
        'style': style,
        'null': null,
        'key_colour': key_colour,
        'key_bold': key_bold,
        'key_inverted': key_inverted,
        'quote': quote,
        'equals': equals,
        'value_colour': value_colour,
        'value_bold': value_bold,
        'value_inverted': value_inverted,
        'other_colour': other_colour,
        'other_bold': other_bold,
        'other_inverted': other_inverted,
        'printer': printer,
        'width': width,
        'display_type': display_type
    }

    def get_style(s):
        symbols_sets = [
            ('├─', '└─', '│ ', '  ', '─' * width + '┐ ', '┘'),
            ('┠─', '┖─', '┃ ', '  ', '─' * width + '┒ ', '┘'),
            ('┣━', '┗━', '┃ ', '  ', '━' * width + '┓ ', '┛'),
            ('╟─', '╙─', '║ ', '  ', '─' * width + '╖ ', '┘'),
            ('╠═', '╚═', '║ ', '  ', '═' * width + '╗ ', '╝'),
            ('├─', '╰─', '│ ', '  ', '─' * width + '╮ ', '╯'),
            ('╏╺', '┗╺', '╏ ', '  ', '╺' * width + '┓ ', '╸╸╸╸'),
            ('▕╲', ' ╲', '▕ ', '  ', '▁' * width + '▁ ', '╳╳╳╳╲'),
            (' -', ' -', ' ', '  ', '-' * width + '  ', ' -- '),
        ]
        if s >= len(symbols_sets):
            s = 0

        inset: str = ' ' * width if len(indent) > 0 else ''

        return {
            'mid': inset + symbols_sets[s][0],
            'end': inset + symbols_sets[s][1],
            'cont': inset + symbols_sets[s][2],
            'none': inset + symbols_sets[s][3],
            'unnamed': symbols_sets[s][4],
            'null': symbols_sets[s][5]
        }

    null: str = get_style(style)['null'] if null is None else null

    # get colour
    def get_colour(colour: str = 'none', bold: bool = False, inverted: bool = False) -> str:
        """
        Get the colour is specified by name
        :param colour:
        :param bold:
        :param inverted:
        :return:
        """
        colours: dict[str, str] = dict(
            black='\x1B[30m',
            red='\x1B[31m',
            green='\x1B[32m',
            yellow='\x1B[33m',
            blue='\x1B[34m',
            magenta='\x1B[35m',
            cyan='\x1B[36m',
            white='\x1B[37m',
            none='\x1B[0m'
        )
        if colour in colours:
            temp_colour: str = colours['none']
            temp_colour += colours[colour]
            if bold:
                temp_colour += "\x1B[1m"
            if inverted:
                temp_colour += "\x1B[7m"
            # temp_colour += colours['none']
        else:
            return colour

        return temp_colour

    # Get indent symbols
    def symbol(i, l):
        return f'{get_colour(other_colour, other_bold, other_inverted)}{get_style(style)["mid"] if i + 1 != l else get_style(style)["end"]}{get_colour()}'

    def next_symbol(i, l):
        return f'{get_colour(other_colour, other_bold, other_inverted)}{get_style(style)["cont"] if i + 1 != l else get_style(style)["none"]}{get_colour()}'

    # Format keys
    def format_key(k):
        k = k if k.isprintable() else repr(k)[1:-1]
        if isinstance(k, str) and quote:
            return f'{get_colour(key_colour, key_bold, key_inverted)}{quote}{k}{quote}{get_colour()}'
        else:
            return f'{get_colour(key_colour, key_bold, key_inverted)}{k}{get_colour()}'

    def format_value(v):
        instance_type = f'({type(v).__name__})' if display_type else ''
        if isinstance(v, str):
            return f'{get_colour(value_colour, value_bold, value_inverted)}{quote}{v}{quote} {instance_type}{get_colour()}'
        else:
            return f'{get_colour(value_colour, value_bold, value_inverted)}{v} {instance_type}{get_colour()}'

    def format_type(t):
        instance_type: str = f'({type(t).__name__})' if display_type else ''
        return f'{get_colour(value_colour, value_bold, value_inverted)}{instance_type}{get_colour()}'

    def format_other(o):
        return f'{get_colour(other_colour, other_bold)}{o}{get_colour()}'

    # Draw keys and values
    length: int = len(dict_obj)
    if isinstance(dict_obj, dict):
        if length == 0:
            printer(f'{indent}{symbol(0, 1)}{format_other(null)}')
        for index, key_value in enumerate(dict_obj.items()):
            key, value = key_value
            if isinstance(dict_obj[key], dict):
                printer(f'{indent}{symbol(index, length)} {format_key(key)}')
                print_tree(dict_obj[key], indent + next_symbol(index, length), **kwargs)
            elif isinstance(dict_obj[key], (list, tuple, set, frozenset)):
                printer(f'{indent}{symbol(index, length)} {format_key(key)}')
                print_tree(dict_obj[key], indent + next_symbol(index, length), **kwargs)
            else:
                printer(f'{indent}{symbol(index, length)} {format_key(key)} {format_other(equals)} {format_value(value)}')
    if isinstance(dict_obj, (list, tuple, set, frozenset)):
        if length == 0:
            printer(f'{indent}{symbol(0, 1)}{format_other(null)}')
        for index, value in enumerate(dict_obj):
            if isinstance(value, dict):
                printer(f'{indent}{symbol(index, length)}{format_other(get_style(style)["unnamed"])} {format_type(dict_obj)}')
                print_tree(value, indent + next_symbol(index, length), **kwargs)
            elif isinstance(value, (list, tuple, set, frozenset)):
                printer(f'{indent}{symbol(index, length)}{format_other(get_style(style)["unnamed"])} {format_type(dict_obj)}')
                print_tree(value, indent + next_symbol(index, length), **kwargs)
            else:
                printer(f'{indent}{symbol(index, length)} {format_value(value)}')


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


    def number_range(low: int, high: int, obj_type: type = float) -> Any:
        """
        Validate integer is between low and high values
        :param low: Low range
        :param high: High range
        :param obj_type: Data type, ex int, float
        :return: argument, exception
        """

        def number_range_parser(argument):
            try:
                argument: type = obj_type(argument)
            except ValueError:
                argparse.ArgumentError(f'Must be of type {obj_type.__name__}')

            if low <= argument <= high:
                return argument
            else:
                parser.error(f'Value is not in the range of {low} and {high}')

        return number_range_parser


    # Load options
    settings_path: Path = Path(__file__).parent.joinpath('config.ini')
    config: configparser.ConfigParser = ConfigParser()
    config.read_dict(dict(options=dict()))
    if settings_path.exists():
        config.read(settings_path)

    # Load options
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description='%(prog)s will find all the words in a given/generated puzzle using a dictionary of choice.',
        formatter_class=parser_formatter(argparse.RawTextHelpFormatter, indent_increment=4, max_help_position=12,
                                         width=160))

    # Dictionary/word/phrase
    dictionary_group = parser.add_argument_group(title='Dictionary',
                                                 description=None)
    dictionary_group.add_argument('-d', '--dict', type=argparse.FileType('rb'),
                                  action='store', dest='dictionary',
                                  default=config['options'].get('dictionary', Path(__file__).parent.joinpath('dictionaries', 'default.hd').as_posix()),
                                  help='dictionary file to use, in .hd format, See convert_dictionary.py\n'
                                       'default: %(default)s')

    colours = [
        'black', 'white', 'none',
        'red', 'green', 'yellow',
        'blue', 'magenta', 'cyan',
    ]

    # Display
    display_group = parser.add_argument_group(title='Display',
                                              description='Viewing and sorting options')
    display_group.add_argument('-p', '--partial', default='a',
                               action='store', dest='word',
                               required=True,
                               help='partial word to match, default=%(default)s')

    display_group.add_argument('-s', '--style', type=number_range(1, 9, int), default=6,
                               action='store', dest='style',
                               help='line style, default=%(default)s')

    for section in ('key', 'value', 'other'):
        display_group.add_argument(f'--{section}-colour', default='none',
                                   choices=colours,
                                   action='store', dest=f'{section}_colour',
                                   help=f'set the {section} colour, default=%(default)s')

    for section in ('key', 'value', 'other'):
        display_group.add_argument(f'--{section}-bold', default=False,
                                   action='store_true', dest=f'{section}_bold',
                                   help=f'is the {section} bold')

    for section in ('key', 'value', 'other'):
        display_group.add_argument(f'--{section}-inverted', default=False,
                                   action='store_true', dest=f'{section}_inverted',
                                   help=f'is the {section} bold')

    display_group.add_argument('-w', '--width', type=int, default=0,
                               action='store', dest=f'width',
                               help=f'width, default=%(default)s')

    options: argparse.Namespace = parser.parse_args()

    main()
