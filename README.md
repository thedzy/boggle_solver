# boggle_solver.py

Find all the words in a given/generated puzzle using a dictionary of choice.

```boggle_solver.py -s 4 -ao```

Generate and solve  4x4 puzzle, display results alphabetically and ordered by size

```
WARNING: Max word length is 16
Puzzle:
b   s   w   e
l   i   z   a
e   f   q   g
r   j   m   h
========================================
Words found that are contained in "./dictionary.hd"
 | awe    | fie    | lis    | wis    | file   | lier   | wile   | swiler |
 | bis    | fil    | qis    | wiz    | fils   | life   | filer  |
 | biz    | fiz    | ref    | zag    | gaze   | reif   | flier  |
 | elf    | gae    | rei    | bier   | isle   | reis   | lifer  |
 | els    | lei    | sib    | bile   | leis   | size   | slier  |
 | fer    | lib    | wae    | bize   | libs   | swag   | swile  |
 | fib    | lie    | wag    | fibs   | lief   | wife   | gawsie |
Found 50 words found between 3 and 16 characters in length and matching filters
```

## What?

Give the solver a puzzle and the parameter that it works in and get the results.

Optionally, play the puzzle for you.

```
<<<<<<< HEAD
usage: boggle_solver.py [-h] [-d DICTIONARY] [-p [PUZZLE [PUZZLE ...]]] [-s PUZZLE_SIZE] [-a] [-o] [-r] [--list] [-l LENGTH] [-M LENGTH_MAX] [-m LENGTH_MIN]
=======
usage: boggle_solver.py [-h] [-l LENGTH] [-M LENGTH_MAX] [-m LENGTH_MIN] [-d DICTIONARY] [-p [PUZZLE [PUZZLE ...]]] [-s PUZZLE_SIZE] [-a] [-o] [-r] [--list]
>>>>>>> c229850406f21253ef4efded0fd7a21eed2386f9
                        [-C PATTERN [PATTERN ...]] [-f REGEX] [-e [WAIT_TIME]] [-S SPEED] [-i]

boggle_solver.py will find all the words in a given/generated puzzle using a dictionary of choice.

optional arguments:
    -h, --help
            show this help message and exit
<<<<<<< HEAD

Dictionary:
=======
    -l LENGTH, --length LENGTH
            Only a fixed length
            Note: Overrides minimum and maximum values
    -M LENGTH_MAX, --max LENGTH_MAX
            Maximum word length
            Default: puzzle size or 32 whichever is less
    -m LENGTH_MIN, --min LENGTH_MIN
            Minimum word length
            Default: 3
>>>>>>> c229850406f21253ef4efded0fd7a21eed2386f9
    -d DICTIONARY, --dict DICTIONARY
            Dictionary file to use, in .hd format, See convert_dictionary.py
            Default: ./dictionary.hd

Puzzle:
    Specify or generate a puzzle

    -p [PUZZLE [PUZZLE ...]], --puzzle [PUZZLE [PUZZLE ...]]
            Puzzle in order of appearance, space separated, top-left to bottom-right
            Default: randomly generated
            Example: a b c d e f g h qu
    -s PUZZLE_SIZE, --size PUZZLE_SIZE
            Puzzle size if randomly generated randomly generated
            Default: 4
            Example: 4 is 4x4

Display:
    Viewing and sorting options

    -a, --alpha
            Display words ordered alphabetical
            Default: False
    -o, --order-ascending
            Display words ordered by size ascending, compatible with -a/--alpha
            Default: False
    -r, --order-descending
            Display words ordered by size descending, compatible with -a/--alpha
            Default: False
    --list  Display as list instead of columns
            Default: False
<<<<<<< HEAD

Filtering:
    Filter down the results by length, contents and REGEX

    -l LENGTH, --length LENGTH
            Only a fixed length
            Note: Overrides minimum and maximum values
    -M LENGTH_MAX, --max LENGTH_MAX
            Maximum word length
            Default: puzzle size or 32 whichever is less
    -m LENGTH_MIN, --min LENGTH_MIN
            Minimum word length
            Default: 3
=======
>>>>>>> c229850406f21253ef4efded0fd7a21eed2386f9
    -C PATTERN [PATTERN ...], --contains PATTERN [PATTERN ...]
            Filter results containing the patterns in any order
            Example:
            te a s can find: teas and steady but not seats
            Default: None
    -f REGEX, --filter REGEX
            Filter results after contains filter
            Note: Only exact matches are found.
            Examples:
            z will find only z, z.* will find all words beginning with z
            .{3}|.{5} will find 3 or 5 letter words
            Default: None

Keyboard emulations:
    Emulate key presses in Windows

    -e [WAIT_TIME], --enter [WAIT_TIME]
            After x seconds delay, start entering with keyboard
            This is the time to switch to the app to receive keyboard strokes
            WARNING: It is highly recommended that you leave your console window accessible
            Default: 4
            Note: Windows ONLY
    -S SPEED, --speed SPEED
            Set the keyboard speed from -1 to 50 when using -e/--enter
            Note: -1 will be interpreted as random between each action.
            Note: Some programs have issues with a very high speeds
            Default: 47
    -i, --interrupt-off
            Do not exit when returning to the window where the code ran from when using -e/--enter
            Default: False
```

## Why?
Just about every time I am playing Microsoft Wordament® (boggle knockoff) I can't help but think that it would be an easy thing to code.  Originally, I imagined it similar to a maze solver and convinced that it could be done with little effort.

Sometimes you just need to know your ideas work for sure.

Only way to know for sure, was to do it.  So I did it.  Here it is.

## Improvements?
While sorting the dictionary made huge improvements in speed, ~~it is still a little slow when it gets into long words, big puzzles, or some combination of the two.~~

While I debated multithreading it, just to see the change, I ultimately decided that beyond just proving it could be done.  Solving all the starting points simultaneously would have an ~~huge~~ impact.

## State?
No known bugs.  Works.

## New
### 1.1
- I have made performance improvements by orders of magnitude.  From a 5x5 puzzle and finding words up to 9 in length taking minutes to 100x100 and 32 in length taking seconds.\
- Now uses a custom dictionary format, converter included.  Dictionary is now a hierarchy of letters, allowing fast searches for partial words.

### 1.2
- Added regex filtering to results

### 1.3
- Replaced the dictionary to better align with Wordament, old one still remains
- Made column mode the default with the ability to override
- Listing alphabetically is optional now, otherwise, will display in the order found
- Added option to list is ascending or descending size
- Added option to send key presses on Windows to enter the words into Wordament
- Fixed an issue in convert_dicitonary.py that caused it to require additional words
- If all letters are single, spaces are not required.  ex: `-p a b c d e f g h i j k l m n o p`  =>  `-p abcdefghijklmnop`

### 1.4
- Made the keyboard entry speed settable as well as variable
- Put in checks that keyboard entry only runs on Windows
- By default if you return to where you started the code it will stop, instead of typing into the console window (optional off)
- Changed parameter 'x' to 'M' after seeing Windows respects case
- Added option `-C` to filter words that contain patterns or characters, simpler for those that don't know REGEX
    - Can still use REGEX in addition to the above filter
    
### 1.4.1
- Cleaned up the help to make it more readable



