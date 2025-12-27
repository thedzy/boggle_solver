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
import configparser
import csv
import ctypes
import json
import math
import mmap
import os
import pickle
import platform
import random
import re
import sys
import time
from configparser import ConfigParser
from decimal import Decimal
from pathlib import Path
from typing import Any

import image_loader

try:
    from Quartz import CGEventCreateKeyboardEvent, CGEventPost, kCGHIDEventTap
    from AppKit import NSWorkspace, NSRunLoop, NSDate, NSDefaultRunLoopMode
except:
    pass
SPEED_STEPS: int = 50


def main() -> None:
    if 'windows' in platform.platform().lower():
        # Capture the window that we are starting with, if we return we can send interrupt
        start_window: ctypes.windll = ctypes.windll.user32.GetForegroundWindow()

    # Get the width of the window
    try:
        terminal_width, _ = os.get_terminal_size()
    except OSError:
        terminal_width: int = 80

    printing: bool = not any([options.json, options.pretty_json, options.csv, options.minimal_csv, options.brute_force])

    start_time: float = time.perf_counter()

    """
    Processing options
    """
    # Load dictionary
    if options.brute_force:
        tree_dictionary = {}
        dictionary_depth = 32
    else:
        try:
            with open(options.dictionary.name, 'rb') as file_handle:
                with mmap.mmap(file_handle.fileno(), 0, access=mmap.ACCESS_READ) as memory_map:
                    tree_dictionary = pickle.loads(memory_map)
        except (UnicodeDecodeError, EOFError):
            print_error('Dictionary may be corrupt or not a dictionary',
                        'Verify file or reprocess dictionary')
        except Exception as err:
            print_error(f'Error loading dictionary:', str(err))

        # Get the dictionaries largest words
        dictionary_depth = 0
        stack = [(tree_dictionary, 1)]

        while stack:
            current_dict, current_depth = stack.pop()
            dictionary_depth = max(dictionary_depth, current_depth)

            for value in current_dict.values():
                if isinstance(value, dict):
                    stack.append((value, current_depth + 1))

    # Get section runtime
    dictionary_load_time: float = time.perf_counter() - start_time
    start_time: float = time.perf_counter()

    # Validate regex before continuing
    if options.filter:
        try:
            pattern: re.Pattern[Any | str] = re.compile(options.filter, re.IGNORECASE)
        except re.error as err:
            print_error('Error in regex statement', err.msg.title())

    # Get/make the puzzle
    if options.puzzle_standard:
        dies: dict[int, list[str]] = {
            0: ['A', 'A', 'E', 'E', 'G', 'N'],
            1: ['A', 'B', 'B', 'J', 'O', 'O'],
            2: ['A', 'C', 'H', 'O', 'P', 'S'],
            3: ['A', 'F', 'F', 'K', 'P', 'S'],
            4: ['A', 'O', 'O', 'T', 'T', 'W'],
            5: ['C', 'I', 'M', 'O', 'T', 'U'],
            6: ['D', 'E', 'I', 'L', 'R', 'X'],
            7: ['D', 'E', 'L', 'R', 'V', 'Y'],
            8: ['D', 'I', 'S', 'T', 'T', 'Y'],
            9: ['E', 'E', 'G', 'H', 'N', 'W'],
            10: ['E', 'E', 'I', 'N', 'S', 'U'],
            11: ['E', 'H', 'R', 'T', 'V', 'W'],
            12: ['E', 'I', 'O', 'S', 'S', 'T'],
            13: ['E', 'L', 'R', 'T', 'T', 'Y'],
            14: ['H', 'I', 'M', 'N', 'U', 'Qu'],
            15: ['H', 'L', 'N', 'N', 'R', 'Z'],
        }

        puzzle_letters: list[str] = []
        while len(dies) > 0:
            random_index: int = random.choice(list(dies.keys()))
            popped_die: list[str] = dies.pop(random_index)

            puzzle_letter: str = random.choice(popped_die)
            puzzle_letters.append(puzzle_letter)

        puzzle: list[list[str]] = []
        row_count: int = 4
        random.shuffle(puzzle_letters)
        for puzzle_x in range(0, row_count):
            row: list[str] = []
            for puzzle_y in range(0, row_count):
                row.append(puzzle_letters[puzzle_x * row_count + puzzle_y].lower())
            puzzle.append(row)
    elif options.image:
        newest_image_path: Path = image_loader.get_newest_image_path(options.image_folder)
        print(f'Loading text from image {newest_image_path}', file=sys.stderr)

        tokens, raw = image_loader.ocr_image(newest_image_path, gutter_px=3, psm=6)
        puzzle_characters: list[str] = [
            token.lower()
            for token in tokens
        ]

        row_count: int = int(math.sqrt(len(puzzle_characters)))
        if not math.sqrt(len(puzzle_characters)).is_integer():
            print(f'Did not get a square puzzle', file=sys.stderr)
            print(f'Got {", ".join(puzzle_characters)}', file=sys.stderr)
            print(raw)
            exit()

        # Create a matrix of tiles
        puzzle: list[list[str]] = []
        for _ in range(row_count):
            puzzle.append(puzzle_characters[0:row_count])
            puzzle_characters = puzzle_characters[row_count:]
    elif options.clipboard:
        print(f'Loading text from clipboard image', file=sys.stderr)

        tokens, raw = image_loader.ocr_image(clipboard=True, gutter_px=3, psm=6)
        puzzle_characters: list[str] = [
            token.lower()
            for token in tokens
        ]

        row_count: int = int(math.sqrt(len(puzzle_characters)))
        if not math.sqrt(len(puzzle_characters)).is_integer():
            print(f'Did not get a square puzzle', file=sys.stderr)
            print(f'Got {", ".join(puzzle_characters)}', file=sys.stderr)
            print(raw)
            exit()

        # Create a matrix of tiles
        puzzle: list[list[str]] = []
        for _ in range(row_count):
            puzzle.append(puzzle_characters[0:row_count])
            puzzle_characters = puzzle_characters[row_count:]
    else:
        letters: list[str] = ['a', 'b', 'c', 'd', 'e', 'f', 'g',
                              'h', 'i', 'j', 'k', 'l', 'm', 'n',
                              'o', 'p', 'qu', 'r', 's', 't', 'u',
                              'v', 'w', 'x', 'y', 'z']
        # Weight the letters for the presence in the english language
        weights: dict[str, float] = {
            'a': 6.5, 'b': 1.2, 'c': 2.2, 'd': 3.4, 'e': 10,
            'f': 1.7, 'g': 1.6, 'h': 4.8, 'i': 5.5, 'j': 0.2,
            'k': 0.6, 'l': 3.1, 'm': 1.9, 'n': 5.3, 'o': 5.9,
            'p': 1.5, 'q': 0.1, 'r': 4.7, 's': 6.3, 't': 7.2,
            'u': 2.2, 'v': 0.8, 'w': 1.9, 'x': 0.2, 'y': 1.6, 'z': 0.3,
        }

        # Get size and generate missing tiles
        if options.puzzle_file:
            file_characters: str = options.puzzle_file.read().lower()
            filtered_characters: str = re.sub(r'[^A-Za-z\s]', '', file_characters)
            puzzle_characters: list[str] = re.split(r'\s+', filtered_characters.strip())
        else:
            puzzle_characters: list[str] = list(options.puzzle[0]) if len(options.puzzle) == 1 else options.puzzle
            puzzle_characters: list[str] = [re.sub(r'[^A-Za-z]', '', char) for char in puzzle_characters]
            puzzle_characters: list[str] = [char.lower() for char in puzzle_characters if len(char) > 0]
        size: int = len(puzzle_characters) if len(options.puzzle) > options.puzzle_size ** 2 else options.puzzle_size ** 2

        generator_count: int = size - len(puzzle_characters)
        puzzle_characters.extend(random.choices(letters, weights=[w[1] for w in weights.items()], k=generator_count))

        puzzle_length: int = len(puzzle_characters)
        row_count: int = int(math.sqrt(puzzle_length))
        if not math.sqrt(puzzle_length).is_integer():
            row_count: int = math.ceil(math.sqrt(puzzle_length))
            generator_count_square: int = (row_count ** 2) - len(puzzle_characters)
            puzzle_characters.extend(random.choices(letters, weights=[w[1] for w in weights.items()], k=generator_count_square))
            print(f'Extending puzzle letters by {generator_count_square} to make a puzzle', file=sys.stderr)

        if options.randomise:
            random.shuffle(puzzle_characters)

        # Create a matrix of tiles
        puzzle: list[list[str]] = []
        for _ in range(row_count):
            puzzle.append(puzzle_characters[0:row_count])
            puzzle_characters = puzzle_characters[row_count:]

    # Set the max/min length of a word
    length_max: int = min(row_count ** 2, dictionary_depth)
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
    if length_max > row_count ** 2:
        length_max: int = row_count ** 2
        # print(f'Max length exceeds puzzle size, setting to {length_max} instead', file=sys.stderr)

    # Min cannot exceed max
    length_min: int = length_max if length_min > length_max else length_min

    results: dict[str, Any] = {'puzzle': puzzle, 'filter': options.filter, 'contains': options.filter_contains, 'dictionary': options.dictionary.name}

    """
    Print Puzzle
    """
    # Show the puzzle so tht the user can see what is being solved
    if printing:
        tile_size: int = len(max([y for x in puzzle for y in x], key=len)) + 1
        print('Puzzle: ')
        print('=' * ((row_count * tile_size) - 1))
        print('\n'.join([''.join([f'{item:^{tile_size}}' for item in row]) for row in puzzle]))
        print('=' * ((row_count * tile_size) - 1))

    # Get section runtime
    puzzle_generation: float = time.perf_counter() - start_time
    start_time: float = time.perf_counter()

    """
    Searching
    """
    # Setup a progressbar
    bar_position: int = 0
    bar_position_max: int = (row_count ** 2)

    # Loop through to find the words
    words_valid: list[str] = []
    lookups: int = 0
    for index_x in range(0, row_count):
        for index_y in range(0, row_count):
            x, y = (index_x, index_y)
            bar_position += 1
            progressbar(bar_position, bar_position_max, puzzle[x][y].upper(), terminal_width)
            # Call to find words starting from and ending at
            regex_compile: re.Pattern[str] | None = re.compile(r'^m[a-z]+') if options.filter else None
            lookups += get_words(x, y,
                                 length=1, max_length=length_max,
                                 word=puzzle[x][y], words=words_valid,
                                 used_squares=[(x, y)], puzzle=puzzle,
                                 dictionary=tree_dictionary,
                                 regex_compile=regex_compile)
    print()

    # Get section runtime
    search_time: float = time.perf_counter() - start_time
    start_time: float = time.perf_counter()

    """
    Sorting and filtering
    """
    # Remove duplicates
    raw_count: int = len(words_valid)
    if options.remove_duplicates:
        words_valid: list[str] = list(dict.fromkeys(words_valid).keys())
    # Filter lengths
    words_valid: list[str] = list(filter(lambda word_valid: length_min <= len(word_valid) <= length_max, words_valid))

    # If a contains filter is used
    if options.filter_contains:
        if printing:
            print(f'Filtering words with patterns "{", ".join(options.filter_contains)}"{" " * 80}')
        results['contains'] = options.filter_contains
        pattern_list: list[str] = ['^.*'] + [f'(?=.*{x})' for x in options.filter_contains] + ['.*']
        pattern2: re.Pattern[Any] = re.compile(''.join(pattern_list), re.IGNORECASE)
        for word in words_valid[:]:
            if not pattern2.fullmatch(word):
                words_valid.remove(word)

    # If a filter is used
    if options.filter:
        if printing:
            print(f'Filtering with "{options.filter}" {" " * 80}')

    if options.order_alpha:
        words_valid.sort()
    if options.order_size or options.order_size_r:
        words_valid.sort(key=len, reverse=options.order_size_r)

    if printing:
        print(f'Words found that are contained in "{options.dictionary.name}"{" " * 80}')

    results['words']: list[str] = words_valid

    # Get section runtime
    filter_time: float = time.perf_counter() - start_time

    # Get runtime
    total_time: float = dictionary_load_time + search_time + filter_time

    """
    Display results
    """
    results['stats']: dict[str, Any] = {'puzzle_size': row_count,
                                        'total_word_count': raw_count,
                                        'word_count': len(words_valid),
                                        'dictionary_load_time': dictionary_load_time,
                                        'search_time': search_time,
                                        'filter_time': filter_time,
                                        'puzzle_generation_time': puzzle_generation,
                                        'time_per_word': 0.0 if len(words_valid) == 0 else search_time / len(words_valid),
                                        'word_lookups': lookups,
                                        'total_time': total_time}
    if options.pretty_json:
        print(json.dumps(results, indent=2))
        return

    if options.json:
        print(json.dumps(results))
        return

    if options.csv:
        writer: csv.writer = csv.writer(options.csv)

        writer.writerow(['puzzle'])
        for grid_row in results['puzzle']:
            writer.writerow(grid_row)

        writer.writerow([''])
        writer.writerow(['words'])
        for word in results['words']:
            writer.writerow([word])

        writer.writerow([''])
        writer.writerow(['stats'])
        for stats_key, stats_value in results['stats'].items():
            writer.writerow([stats_key, stats_value])
        return

    if options.minimal_csv:
        writer: csv.writer = csv.writer(options.minimal_csv)
        for word in results['words']:
            writer.writerow([word])
        return

    # Print words
    if len(words_valid) > 0 and not options.brute_force:
        if not options.list:
            divider: str = ' | '

            column_width: int = len(max(words_valid, key=len)) + len(divider)
            columns: int = int(((terminal_width - 1) - len(divider)) / column_width)
            column_height: int = int(len(words_valid) / columns) + 1

            words_valid_columned: list[Any] = []
            start, end = 0, 0
            while end < len(words_valid):
                end: int = start + column_height
                try:
                    words_valid_columned.append(words_valid[start:end])
                except IndexError:
                    words_valid_columned.append(words_valid[start:])
                start: int = end

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
    print(f'Approximate potential words: {estimated_paths(row_count, length_max)}')
    print(f'Total dictionary lookups {lookups:,}')
    if length_min is length_max:
        print(f'Found {len(words_valid)} {"unique" if options.remove_duplicates else "total"} word(s) of {length_max} characters in length and matching filters')
    else:
        print(f'Found {len(words_valid):,} {"unique" if options.remove_duplicates else "total"} word(s) between {length_min} and {length_max} characters in length and matching filters')
    print('--')

    time_sets: dict[str, float] = dict(
        h=60.0 * 60.0,
        m=60.0,
        s=1.0,
        ms=0.001,
        µs=0.000001,
    )
    for label, value in time_sets.items():
        if search_time >= value:
            time_multiplier: float = value
            time_format: str = label
            break
    print(f'Time to load dictionary  {dictionary_load_time / time_multiplier:12.3f}{time_format}')
    print(f'Time to search           {search_time / time_multiplier:12.3f}{time_format}')
    print(f'Time to filter           {filter_time / time_multiplier:12.3f}{time_format}')
    print(f'Total:                   {total_time / time_multiplier:12.3f}{time_format}')

    """
    Keyboard emulation
    """
    if options.enter is not None:
        # Countdown to start
        print('Starting typing in ', end='')
        count_down_timer: int = options.enter + 1
        for count_down in range(1, count_down_timer):
            print(count_down_timer - count_down)
            time.sleep(1)
        print('Go!')

        speed: float = (SPEED_STEPS - options.speed) / SPEED_STEPS

        if 'windows' in platform.platform().lower():
            # For each word, emulate typing
            for word in words_valid:
                for letter in word:
                    # If interrupting, check if we are back the window
                    if not options.interrupt:
                        focus_window: Any = ctypes.windll.user32.GetForegroundWindow()
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
        if 'macos' in platform.platform().lower():
            if 'Quartz' not in sys.modules or 'AppKit' not in sys.modules:
                print('Keyboard injection unavailable on macOS, requires "Quartz" and "AppKit" modules')
                return
            start_window: str | None = mac_foreground_app()
            for word in words_valid:
                for letter in word:
                    if not options.interrupt:
                        current_bundle_id: str | None = mac_foreground_app()
                        if current_bundle_id != start_window:
                            print(f'Focus lost from {start_window}, aborting typing')
                            return

                    mac_press_key(letter, speed / 2)

                mac_press_key('\n', speed / 2)
                time.sleep(speed)


def mac_foreground_app() -> str | None:
    """
    Return the bundle identifier of the current macOS foreground application.
    :return: bundleid
    """
    NSRunLoop.currentRunLoop().runMode_beforeDate_(
        NSDefaultRunLoopMode,
        NSDate.distantPast()
    )

    active_app = NSWorkspace.sharedWorkspace().frontmostApplication()
    if active_app is None:
        return None
    return active_app.bundleIdentifier()


def mac_press_key(character: str, hold_time: float) -> None:
    """
    Emulate a keyboard press, <enter> default
    :param character: Single character to emulate
    :param hold_time: Key hold time
    :return: (void)
    """
    mac_keycodes: dict[str, int] = {
        'a': 0, 'b': 11, 'c': 8, 'd': 2, 'e': 14, 'f': 3,
        'g': 5, 'h': 4, 'i': 34, 'j': 38, 'k': 40, 'l': 37,
        'm': 46, 'n': 45, 'o': 31, 'p': 35, 'q': 12, 'r': 15,
        's': 1, 't': 17, 'u': 32, 'v': 9, 'w': 13, 'x': 7,
        'y': 16, 'z': 6,
        '\n': 36, '\r': 36,
    }

    key_char: str = character.lower()
    key_code: int | None = mac_keycodes.get(key_char)
    if key_code is None:
        print(f'Unsupported character for macOS keycode: {repr(character)}')
        return

    event_down: Any = CGEventCreateKeyboardEvent(None, key_code, True)
    event_up: Any = CGEventCreateKeyboardEvent(None, key_code, False)
    CGEventPost(kCGHIDEventTap, event_down)
    CGEventPost(kCGHIDEventTap, event_up)
    time.sleep(hold_time)


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


def get_words(x: int, y: int, length: int, max_length: int,
              word: str, words: list[str],
              used_squares: list[tuple], puzzle: list[list[str]],
              dictionary: dict[str, Any],
              regex_compile: re.Pattern[str] | None = None) -> int:
    """
    Get a word starting from a position and to a length
    Note: Recursive
    :param x: X Position
    :param y: Y Position
    :param length: Length of word to find
    :param max_length: Max Length of word to find
    :param word: For recursion, should start empty
    :param words: List of found words
    :param used_squares: For recursion, track used positions
    :param puzzle: Puzzle matrix
    :param dictionary: Hierarchy dictionary
    :param regex_compile: regex to match
    :return: (void)
    """
    row_count: int = len(puzzle)
    count: int = 0

    # If we haven't reached the end of the path, move to the next positions and recurse
    if length <= max_length:
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
                        if regex_compile:
                            regex: regex_compile.Match[str] = re.match(options.filter, word)
                            if not regex:
                                return count
                        count += 1
                        partial_match, full_match = lookup_word(dictionary, word + puzzle[temp_x][temp_y])
                        if full_match:
                            words.append(word + puzzle[temp_x][temp_y])
                        if partial_match or full_match:
                            count += get_words(
                                x=temp_x, y=temp_y, length=length + 1, max_length=max_length,
                                word=word + puzzle[temp_x][temp_y], words=words,
                                used_squares=new_used_squares,
                                puzzle=puzzle, dictionary=dictionary,
                                regex_compile=regex_compile
                            )
    return count


def lookup_word(dictionary: dict[str, str | dict], word: str) -> (bool, bool):
    """
    Find full or partial record of word in dictionary
    :param dictionary: Hierarchy dictionary
    :param word: String to locate
    :return: Found
    """
    if options.brute_force:
        return True, True
    trie_node: dict[str, str | dict] = dictionary
    for letter in word:
        trie_node: [dict | None] = trie_node.get(letter)
        if trie_node is None:
            return False, False
    return True, '\n' in trie_node


def estimated_paths(grid_size: int, max_length: int) -> str:
    """
    Estimates paths for a specific length limit (e.g. 1-32).
    Does a decent job as estimating, with small puzzles of know possibilities, its within 1%
    But drop most of the digits, so its off by more, but its a general guideline

    Formula logic:
    - Assume a growth factor (2.76)
    - Scale by the number of starting cells (grid_size^2).
    - Cap the length at the total number of cells (cannot reuse dice).
    """
    total_cells = grid_size ** 2
    effective_length = min(max_length, total_cells)

    # Base Calculation (The formula above)
    base = Decimal('2.76')
    multiplier = Decimal('1.1')

    # Calculate the core complexity for a path of this length
    value = multiplier * (base ** effective_length)

    # Scaling
    # If we have a 10x10 board (100 cells) but only want paths of length 5,
    # we have 20x more places to start than a 5-cell board would.
    space_ratio = Decimal(total_cells) / Decimal(effective_length)
    final_value = value * space_ratio

    # Remove insignificant numbers
    zeros_to_remove = max([0, ((len(f'{final_value:0.0f}') // 3) * 3) - 3])
    mask = 10 ** zeros_to_remove
    clean_number = (final_value // mask) * mask

    return f'{clean_number:,.0f}'


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


    def valid_path(path):
        path = Path(path)
        if not path.is_dir():
            raise argparse.ArgumentTypeError(f'{path} is an invalid folder/directory')
        return path


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

    # Puzzle
    puzzle_group = parser.add_argument_group(title='Puzzle',
                                             description='Specify or generate a puzzle')
    puzzle_parser = puzzle_group.add_mutually_exclusive_group()
    puzzle_parser.add_argument('-p', '--puzzle', default=[],
                               action='store', dest='puzzle', nargs='*',
                               help='puzzle tiles in order of appearance, space separated, top-left to bottom-right\n'
                                    'default: randomly generated\n'
                                    'example: a b c d e f g h qu')

    puzzle_parser.add_argument('-i', '--image', default=False,
                               action='store_true', dest='image',
                               help='load image from a folder and OCR')

    puzzle_group.add_argument('--image-folder', type=valid_path,
                              action='store', dest='image_folder',
                              default=config['options'].get('image-folder', Path('/tmp').as_posix()),
                              help='folder to load image from')

    puzzle_parser.add_argument('-c', '--clipboard', default=False,
                               action='store_true', dest='clipboard',
                               help='use image in clipboard and OCR')

    puzzle_parser.add_argument('-S', '--standard', default=False,
                               action='store_true', dest='puzzle_standard',
                               help='standard puzzle, consisting on 16 dies in 4x4 grid')

    puzzle_parser.add_argument('--puzzle-file', type=argparse.FileType(),
                               action='store', dest='puzzle_file',
                               help='load a file of characters, will filter for characters and split on spaces')

    puzzle_group.add_argument('-r', '--randomise', dest='randomise',
                              action='store_true',
                              help='randomise specified puzzle letters')

    puzzle_group.add_argument('-s', '--size', type=int,
                              action='store', dest='puzzle_size', default=2,
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
    display_group.add_argument('-O', '--order-descending',
                               action='store_true', dest='order_size_r', default=False,
                               help='display words ordered by size descending, compatible with -a/--alpha\n'
                                    'default: %(default)s')
    display_group.add_argument('--list',
                               action='store_true', dest='list', default=False,
                               help='display as list instead of columns\n'
                                    'default: %(default)s')
    display_parser = display_group.add_mutually_exclusive_group()
    display_parser.add_argument('--json',
                                action='store_true', dest='json', default=False,
                                help='display as JSON')
    display_parser.add_argument('--pretty-json',
                                action='store_true', dest='pretty_json', default=False,
                                help='display as formatted JSON')
    display_parser.add_argument('--csv', type=argparse.FileType('w+'),
                                action='store', dest='csv', default=None,
                                help='export as csv')
    display_parser.add_argument('--minimal-csv', type=argparse.FileType('w+'),
                                action='store', dest='minimal_csv', default=None,
                                help='export words as csv')

    # Filtering
    filter_group = parser.add_argument_group(title='Filtering',
                                             description='Filter down the results by length, contents and REGEX')
    filter_group.add_argument('-l', '--length', type=int,
                              action='store', dest='length', default=None,
                              help='only a fixed length\n'
                                   'note: Overrides minimum and maximum values')
    filter_group.add_argument('-M', '--max', type=number_range(1, 32, int),
                              action='store', dest='length_max', default=32,
                              help='maximum word length \n'
                                   'default: puzzle size or 32 whichever is less')
    filter_group.add_argument('-m', '--min', type=number_range(1, 32, int),
                              action='store', dest='length_min', default=3,
                              help='minimum word length\n'
                                   'default: %(default)s')
    filter_group.add_argument('-C', '--contains',
                              action='store', dest='filter_contains', default=None, nargs='+',
                              metavar='PATTERN',
                              help='filter results containing the patterns in any order\n'
                                   'example:\n'
                                   '\tte a s can find: teas and steady but not seats\n'
                                   'default: %(default)s')
    filter_group.add_argument('-f', '--filter',
                              action='store', dest='filter', default=None,
                              metavar='REGEX',
                              help='filter results after contains filter\n'
                                   'note: Only exact matches are found. \n'
                                   'examples:\n'
                                   '\tz will find only z, z.* will find all words beginning with z \n'
                                   '\t.{3}|.{5} will find 3 or 5 letter words\n'
                                   'default: %(default)s')
    filter_group.add_argument('-D', '--keep-duplicates',
                              action='store_false', dest='remove_duplicates', default=True,
                              help='keep duplicates in found words for raw word count and/or performance stats')

    # Emulate the keyboard
    keyboard_group = parser.add_argument_group(title='Keyboard emulations',
                                               description='Emulate key presses')
    keyboard_group.add_argument('-e', '--enter', type=int,
                                action='store', dest='enter', default=None, nargs='?',
                                const=int(config['options'].get('enter', '4')),
                                metavar='WAIT_TIME',
                                help='after x seconds delay, start entering with keyboard\n'
                                     'this is the time to switch to the app to receive keyboard strokes\n'
                                     'WARNING: It is highly recommended that you leave your console window accessible\n'
                                     'default: %(const)s')
    keyboard_group.add_argument('--speed', type=number_range(-1, SPEED_STEPS),
                                action='store', dest='speed', default=float(config['options'].get('speed', int(SPEED_STEPS * 0.95))),
                                help=f'set the keyboard speed from -1 to {SPEED_STEPS} when using -e/--enter \n'
                                     'note: -1 will be interpreted as random between each action. \n'
                                     'note: some programs have issues with a very high speeds\n'
                                     'default: %(default)s')
    keyboard_group.add_argument('--interrupt-off',
                                action='store_true', dest='interrupt', default=False,
                                help='on Windows: do not exit when returning to the window where the code ran from when using -e/--enter \n'
                                     'on macOS:   do not exit when leaving the windows which is entering the key presses -e/--enter \n'
                                     'default: %(default)s')

    parser.add_argument('--brute-force', default=False,
                        action='store_true', dest='brute_force',
                        help='brute force every possibility, very processor intensive, does not use the dictiionary to validate words')

    options: argparse.Namespace = parser.parse_args()

    # Save options
    config.setdefault('options', {})
    config['options']['dictionary'] = options.dictionary.name
    config['options']['image-folder'] = options.image_folder.as_posix()
    config['options']['speed'] = str(options.speed)
    if options.enter is not None:
        config['options']['enter'] = str(options.enter)

    with settings_path.open('w+', encoding='utf-8') as target_file:
        config.write(target_file)

    main()
