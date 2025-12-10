#!/usr/bin/env python3

__author__ = 'thedzy'
__copyright__ = 'Copyright 2024, thedzy'
__license__ = 'GPL'
__version__ = '1.0'
__maintainer__ = 'thedzy'
__email__ = 'thedzy@hotmail.com'
__status__ = 'Development'
__date__ = '2025-11-28'
__description__ = \
    """
    benchmark.py: 
    Benchmark boggle_solver.py
    
    A more stable benchmark that does not require multiple loops for better consistency, but can
    It smore stable in its results because it uses the same puzzle as the based, reducing random variation
    """

import argparse
import contextlib
import csv
import io
import json
import logging.config
import pprint
import runpy
import sys
from pathlib import Path
from typing import Any


def main() -> None:
    # Get puzzle and size
    with open(options.puzzle_file, 'r', encoding='utf-8') as file_handle:
        matrix: list[list[str]] = [line.strip().split() for line in file_handle.read().splitlines()]
    max_size: int = len(matrix[0])

    # Get puzzle stats
    total_time = 0.0
    results: list[dict[str, int]] = []
    max_size = min([options.max_size, max_size])
    try:
        for size in range(2, max_size + 1):
            for iteration in range(1, options.iterations + 1):
                logger.info(f'Running size of {size} of {max_size}, interation {iteration} or {options.iterations}')
                puzzle: list[list[str]] = [matrix[x][0:size] for x in range(size)]
                puzzle_characters: list[str] = [elem for row in puzzle for elem in row]

                stdout_buffer = io.StringIO()
                sys.argv = [str(options.script), '-p', puzzle_characters, '--json']
                logger.debug(sys.argv)

                with contextlib.redirect_stdout(stdout_buffer):
                    runpy.run_path(str(options.script), run_name='__main__')

                output: str = stdout_buffer.getvalue()
                data: dict[str, Any] = json.loads(output)
                results.append(data['stats'])

                logger.debug(pprint.pformat(data['stats']))
                logger.info(f'Took {data["stats"]["total_time"]} seconds')

                total_time += data['stats']['total_time']
    except KeyboardInterrupt:
        logger.info(f'Stopping run at {size - 1}')
        pass

    # Write results
    with open(options.csv, 'w+') as csv_file:
        csv_writer: csv.DictWriter = csv.DictWriter(csv_file, fieldnames=results[0].keys())
        csv_writer.writeheader()
        csv_writer.writerows(results)
    logger.info(f'Write results to "{options.csv}"')

    # print end/total time
    minutes, seconds = divmod(total_time, 60)
    hours, minutes = divmod(minutes, 60)
    logger.info(f'Time to complete: {int(hours):02d}:{int(minutes):02d}:{seconds:04.1f}')


def create_logger(name: str = __file__, levels: dict[str, Any] = {}) -> logging.Logger:
    # Create log level
    def make_log_level(level_name: str, level_int: int) -> None:
        logging.addLevelName(level_int, level_name.upper())
        setattr(new_logger, level_name, lambda *args: new_logger.log(level_int, *args))

    new_logger: logging.Logger = logging.getLogger(name)

    logging_config: dict[str, Any] = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'stderr': {
                'style': '{', 'format': '{message}',
            },
            'file': {
                'style': '{', 'format': '[{asctime}] [{levelname:8}] {message}'
            }
        },
        'handlers': {
            'stderr': {
                'class': 'logging.StreamHandler',
                'formatter': 'stderr',
                'stream': 'ext://sys.stderr',
            }
        },
        'loggers': {
            name: {
                'level': 10 if options.debug else 20,
                'handlers': [
                    'stderr'
                ]
            }
        }
    }

    logging.config.dictConfig(logging_config)

    # Create custom levels
    for level in levels.items():
        make_log_level(*level)

    return new_logger


if __name__ == '__main__':
    def valid_path(path):
        parent: Path = Path(path).parent
        if not parent.is_dir():
            print(f'{parent} is not a directory, make it?', end=' ')
            if input('y/n: ').lower()[0] == 'y':
                parent.mkdir(parents=True, exist_ok=True)
                return Path(path)
            raise argparse.ArgumentTypeError(f'{path} is an invalid path')
        return Path(path)


    # Create argument parser
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description=__description__)

    # Files
    parser.add_argument('-s', '--script', type=valid_path, default=Path(__file__).parent.parent / 'boggle_solver.py',
                        action='store', dest='script',
                        help='script file')

    parser.add_argument('-c', '--csv', type=valid_path, default=Path(__file__).parent / 'results.csv',
                        action='store', dest='csv',
                        help='csv file')

    parser.add_argument('-p', '--benchmark_puzzle', type=valid_path, default=Path(__file__).parent / 'puzzle128.dat',
                        action='store', dest='puzzle_file',
                        help='puzzle file')

    # Settings
    parser.add_argument('-m', '--max-size', type=int, default=64,
                        action='store', dest='max_size',
                        help='max size, ceiling 64')

    parser.add_argument('-i', '--iterations', type=int, default=1,
                        action='store', dest='iterations',
                        help='iterations of each puzzle, not required for good results and rather redundant')

    # Debug/verbosity option
    parser.add_argument('--debug', default=False,
                        action='store_true', dest='debug',
                        help=argparse.SUPPRESS)

    options: argparse.Namespace = parser.parse_args()

    logger: logging.Logger = create_logger()
    logger.debug('Debug ON')
    logger.debug(pprint.pformat(options))

    main()
