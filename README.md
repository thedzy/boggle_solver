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
usage: boggle_solver.py [-h] [-d DICTIONARY] [-p [PUZZLE ...]] [--randomise] [-s PUZZLE_SIZE] [-S] [-a] [-o] [-r] [--list] [--json] [--pretty_json] [-l LENGTH]
                        [-M LENGTH_MAX] [-m LENGTH_MIN] [-C PATTERN [PATTERN ...]] [-f REGEX] [-e [WAIT_TIME]] [--speed SPEED] [-i]

boggle_solver.py will find all the words in a given/generated puzzle using a dictionary of choice.

options:
    -h, --help
            show this help message and exit

Dictionary:
    -d DICTIONARY, --dict DICTIONARY
            dictionary file to use, in .hd format, See convert_dictionary.py
            default: /Users/syoung/git/boggle_solver/dictionary.hd

Puzzle:
    Specify or generate a puzzle

    -p [PUZZLE ...], --puzzle [PUZZLE ...]
            puzzle tiles in order of appearance, space separated, top-left to bottom-right
            default: randomly generated
            example: a b c d e f g h qu
    --randomise
            randomise specified puzzle letters
    -s PUZZLE_SIZE, --size PUZZLE_SIZE
            puzzle size if randomly generated randomly generated
            default: 1
            example: 4 is 4x4
    -S, --standard
            standard puzzle, consisting on 16 dies in 4x4 grid

Display:
    Viewing and sorting options

    -a, --alpha
            display words ordered alphabetical
            default: False
    -o, --order-ascending
            display words ordered by size ascending, compatible with -a/--alpha
            default: False
    -r, --order-descending
            display words ordered by size descending, compatible with -a/--alpha
            default: False
    --list  display as list instead of columns
            default: False
    --json  display as JSON
    --pretty_json
            display as formatted JSON

Filtering:
    Filter down the results by length, contents and REGEX

    -l LENGTH, --length LENGTH
            Only a fixed length
            Note: Overrides minimum and maximum values
    -M LENGTH_MAX, --max LENGTH_MAX
            maximum word length
            default: puzzle size or 32 whichever is less
    -m LENGTH_MIN, --min LENGTH_MIN
            minimum word length
            default: 3
    -C PATTERN [PATTERN ...], --contains PATTERN [PATTERN ...]
            filter results containing the patterns in any order
            example:
            te a s can find: teas and steady but not seats
            default: None
    -f REGEX, --filter REGEX
            filter results after contains filter
            note: Only exact matches are found.
            examples:
            z will find only z, z.* will find all words beginning with z
            .{3}|.{5} will find 3 or 5 letter words
            default: None

Keyboard emulations:
    Emulate key presses in Windows

    -e [WAIT_TIME], --enter [WAIT_TIME]
            after x seconds delay, start entering with keyboard
            this is the time to switch to the app to receive keyboard strokes
            WARNING: It is highly recommended that you leave your console window accessible
            default: 4
            note: Windows ONLY
    --speed SPEED
            set the keyboard speed from -1 to 50 when using -e/--enter
            note: -1 will be interpreted as random between each action.
            note: some programs have issues with a very high speeds
            default: 47
    -i, --interrupt-off
            do not exit when returning to the window where the code ran from when using -e/--enter
            default: False
```

Benchmark
```commandline
SIZE=5; LOOPS=200; TIME=0; WORDS=0; for x in $(seq $LOOPS); do RESULTS=$(boggle_solver.py -s $SIZE --json); TIME=$((TIME+$(echo $RESULTS |jq .stats.search_time))); WORDS=$((WORDS+$(echo $RESULTS |jq '.words | length' ))); echo $x; done; echo Average pussle time: $((TIME/LOOPS)); echo Time per word: $((TIME/WORDS))
```

Find the best puzzle
```commandline
RECORD=0; while True; do RESULTS=$(~/git/boggle_solver/boggle_solver.py -S --json); LENGTH=$(echo $RESULTS | jq '.words | length'); echo $LENGTH; [ $LENGTH -gt $RECORD ] && RECORD=$LENGTH && echo $(echo $RESULTS | jq '.puzzle'); done
```

## Why?
Just about every time I am playing Microsoft Wordament® (boggle knockoff) I can't help but think that it would be an easy thing to code.  Originally, I imagined it similar to a maze solver and convinced that it could be done with little effort.

Sometimes you just need to know your ideas work for sure.

Only way to know for sure, was to do it.  So I did it.  Here it is.

## Improvements?
~~While sorting the dictionary made huge improvements in speed, it is still a little slow when it gets into long words, big puzzles, or some combination of the two.~~

~~While I debated multithreading it, just to see the change, I ultimately decided that beyond just proving it could be done.  Solving all the starting points simultaneously would have an huge impact.~~ \
Much to my surprise multithreading was slower.  The overhead of the thread management negated the gains. Added ~ %1 seconds to the time.

Add an option to generate a puzzle based on the actual dies used in the game

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

### 1.5.0
- Added a new dictionary from [Aspell](http://app.aspell.net/create)
- Improved long word searched by reducing the amount of variance needed in the search length
- Changed status to a progress bar to make it readable/usable
- Code cleanup
- 
### 1.6.0
- Added json output
- Moved regex filtering to during word validation testing speeding up searches that have filters

### 1.6.1
- Modernisation
  - Type hinting
  - f-strings
  - Clean up help
- Randomisation of puzzle letters options
- Inserts random characters when not a complete puzzle as opposed to alerting user for more characters

### 1.7.0
- Option to use the standard english dice
- Can use size with puzzle to specifying tiles that must appear
- Randomly chooses characters giving weight to characters that appear more in English
  - Prevents "x" and "qu" appearing as frequently as "e" or "s"
- Added dictionary file to json output
- Fixed the calculations of stats in json output
- Added new stat in json, time_per_word
- Added pretty print json output


### New in convert_dictionary.py

#### 1.1.1
- Fixed read/write issue when testing a dictionary