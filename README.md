# boggle_solver.py

Find all the words in a given/generated puzzle using a dictionary of choice.

## What?

Give the solver a puzzle and the parameter that it works in and get the results.

```bash
usage: boggle_solver.py [-h] [-l LENGTH] [-x LENGTH_MAX] [-m LENGTH_MIN] [-d DICTIONARY] [-p [PUZZLE [PUZZLE ...]]] [-s PUZZLE_SIZE] [-o] [-c]

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
            Default: /Users/syoung/Documents/GitHub/boggle_solver/dictionary.hd
    -p [PUZZLE [PUZZLE ...]], --puzzle [PUZZLE [PUZZLE ...]]
            Puzzle in order of appearance, space separated, top-left to bottom-right
            Default: randomly generated
            Example: a b c d e f g h qu
    -s PUZZLE_SIZE, --size PUZZLE_SIZE
            Puzzle size if randomly generated randomly generated
            Default: 4
            Example: 4 is 4x4
    -o, --order-size
            Display words ordered by size
            Default: False
    -c, --columns
            Display as columns
            Default: False
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
