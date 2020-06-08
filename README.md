# boggle_solver.py

Find all the words in a given/generated puzzle using a dictionary of choice.

## What?

Give the solver a puzzle and the parameter that it works in and get the results.

Optionally, play the puzzle for you.

```
usage: boggle_solver.py [-h] [-l LENGTH] [-x LENGTH_MAX] [-m LENGTH_MIN] [-d DICTIONARY] [-p [PUZZLE [PUZZLE ...]]] [-s PUZZLE_SIZE] [-a] [-o] [-r] [--list]
                        [-f REGEX] [-e [WAIT_TIME]]

Will find all the words in a given/generated puzzle using a dictionary of choice.

optional arguments:
    -h, --help
            show this help message and exit
    -l LENGTH, --length LENGTH
            Only a fixed length
            Note: Overrides minimum and maximum values
    -x LENGTH_MAX, --max LENGTH_MAX
            Maximum word length,
            Default: puzzle size (not recommended to use default)
    -m LENGTH_MIN, --min LENGTH_MIN
            Minimum word length
            Default: 3
    -d DICTIONARY, --dict DICTIONARY
            Dictionary file to use, in .hd format, See convert_dictionary.py
            Default: ./dictionary.hd
    -p [PUZZLE [PUZZLE ...]], --puzzle [PUZZLE [PUZZLE ...]]
            Puzzle in order of appearance, space separated, top-left to bottom-right
            Default: randomly generated
            Example: a b c d e f g h qu
    -s PUZZLE_SIZE, --size PUZZLE_SIZE
            Puzzle size if randomly generated randomly generated
            Default: 4
            Example: 4 is 4x4
    -a, --alpha
            Display words ordered alphabetical
            Default: False
    -o, --order-ascending
            Display words ordered by size ascending, compatible with -a/--alpha
            Default: False
    -r, --order-descending
            Display words ordered by size ascending, compatible with -a/--alpha
            Default: False
    --list  Display as list instead of columns
            Default: True
    -f REGEX, --filter REGEX
            Filter results
            Note:Only exact matches are found.
            Examples:
            z will find only z, z.* will find all words beginning with z
            .{3}|.{5} will find 3 or 5 letter words
            Default: None
    -e [WAIT_TIME], --enter [WAIT_TIME]
            After x seconds delay, start entering with keyboard
            This is the time to switch to the app to receive keyboard strokes
            Default: 4
            Note: Windows ONLY
```

## Why?
Just about every time I am playing Microsoft Wordament® (boggle knockoff) I can't help but think that it would be an easy thing to code.  Originally, I imagined it similar to a maze solver and convinced that it could be done with little effort.

Sometimes you just need to know your ideas work for sure.

Only way to know for sure, was to do it.  So I did it.  Here it is.

## Improvements?
While sorting the dictionary made huge improvements in speed, it is still a little slow when it gets into long words, big puzzles, or some combination of the two.

While I debated multithreading it, just to see the change, I ultimately decided that beyond just proving it could be done.  Solving all the starting points simultaneously would have a huge impact.

## State?
No known bugs.  Works.

## New
### 1.1
I have made performance improvements by orders of magnitude.  From a 5x5 puzzle and finding words up to 9 in length taking minutes to 100x100 and 32 in length taking seconds.\
Now uses a custom dictionary format, converter included.  Dictionary is now a hierarchy of letters, allowing fast searches for partial words.
### 1.2 
Added regex filtering to results
### 1.3
Replaced the dictionary to better align with Wordament, old one still remains
Made column mode the default with the ability to override
Listing alphabetically is optional now, otherwise, will display in the order found
Added option to list is ascending or descending size
Added option to send key presses on Windows to enter the words into Wordament
Fixed an issue in convert_dicitonary.py that caused it to require additional words