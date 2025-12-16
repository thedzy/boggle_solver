# boggle_solver.py

Find all the words in a given/generated puzzle using a dictionary of choice.

```boggle_solver.py -s 4 -ao```

Generate and solve  4x4 puzzle, display results alphabetically and ordered by size

```
Puzzle:
=======
v h l a
s t l d
n o n a
g e d h
=======
████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████ | H
Words found that are contained in "/Users/syoung/git/boggle_solver/dictionary.hd"
 | ado      | dos      | log      | son      | dent     | gens     | loge     | snog     | aland    | hadal    | tonal    | soldan   |
 | ala      | dot      | lot      | sot      | dhal     | gent     | lone     | snot     | alane    | halal    | toned    | stoned   |
 | all      | edh      | nah      | tod      | doge     | gold     | long     | soda     | alant    | halon    | adland   | tolane   |
 | alt      | ego      | neg      | toe      | doll     | gone     | lost     | sola     | allod    | halos    | alants   | tonged   |
 | and      | end      | nod      | tog      | dolt     | gosh     | loth     | sold     | allot    | halts    | allots   | allonge  |
 | ane      | eng      | nog      | ton      | dona     | goth     | lots     | sone     | alone    | hants    | anenst   | daltons  |
 | ant      | ens      | nos      | ados     | done     | hade     | nada     | song     | along    | laden    | dalton   | endlong  |
 | dad      | eon      | not      | alan     | dong     | hall     | nala     | soth     | altos    | llano    | enhalo   | enhalos  |
 | dah      | ged      | nth      | aloe     | dons     | halo     | neon     | toed     | anent    | loden    | haloed   | gonadal  |
 | dal      | gen      | oda      | alto     | dosh     | halt     | node     | tola     | anode    | longe    | halons   | halogen  |
 | dan      | god      | ode      | alts     | dost     | hand     | nona     | told     | dados    | neons    | ladens   | halogens |
 | den      | gos      | old      | anon     | doth     | hant     | none     | toll     | dents    | nodal    | llanos   |
 | doe      | got      | one      | ants     | dots     | lade     | nosh     | tone     | dolts    | solan    | lodens   |
 | dog      | had      | ons      | dada     | egos     | land     | odah     | tong     | gents    | sonde    | longed   |
 | dol      | lad      | sod      | dado     | enol     | lane     | olla     | tons     | gonad    | stone    | shlong   |
 | don      | lah      | sol      | dens     | eons     | lode     | sned     | tosh     | goths    | tolan    | soland   |
Total dictionary lookups 38,565
Found 187 unique word(s) between 3 and 16 characters in length and matching filters
--
Time to load dictionary         0.169s
Time to search                  0.021s
Time to filter                  0.000s
Total:                          0.190s
```

## What?

Give the solver a puzzle and the parameter that it works in and get the results.

Optionally, play the puzzle for you.

```
usage: boggle_solver.py [-h] [-d DICTIONARY] [-p [PUZZLE ...] | -S | --puzzle-file PUZZLE_FILE] [--randomise] [-s PUZZLE_SIZE] [-a] [-o] [-r] [--list]
                        [--json | --pretty-json | --csv CSV | --minimal-csv MINIMAL_CSV] [-l LENGTH] [-M LENGTH_MAX] [-m LENGTH_MIN] [-C PATTERN [PATTERN ...]]
                        [-f REGEX] [--keep-duplicates] [-e [WAIT_TIME]] [--speed SPEED] [-i]

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
    -S, --standard
            standard puzzle, consisting on 16 dies in 4x4 grid
    --puzzle-file PUZZLE_FILE
            load a file of characters, will filter for characters and split on spaces
    --randomise
            randomise specified puzzle letters
    -s PUZZLE_SIZE, --size PUZZLE_SIZE
            puzzle size if randomly generated randomly generated
            default: 1
            example: 4 is 4x4

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
    --pretty-json
            display as formatted JSON
    --csv CSV
            export as csv
    --minimal-csv MINIMAL_CSV
            export words as csv

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
    --keep-duplicates
            keep duplicates in found words for raw word count and/or performance stats

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
RECORD=0; while True; do RESULTS=$(boggle_solver.py -S --json); LENGTH=$(echo $RESULTS | jq '.words | length'); echo $LENGTH; [ $LENGTH -gt $RECORD ] && RECORD=$LENGTH && echo $(echo $RESULTS | jq '.puzzle'); done
```

## Why?
Just about every time I am playing Microsoft Wordament® (boggle knockoff) I can't help but think that it would be an easy thing to code.  Originally, I imagined it similar to a maze solver and convinced that it could be done with little effort.

Sometimes you just need to know your ideas work for sure.

Only way to know for sure, was to do it.  So I did it.  Here it is.

## Improvements?
~~While sorting the dictionary made huge improvements in speed, it is still a little slow when it gets into long words, big puzzles, or some combination of the two.~~

~~While I debated multithreading it, just to see the change, I ultimately decided that beyond just proving it could be done.  Solving all the starting points simultaneously would have an huge impact.~~ \
Much to my surprise multithreading was slower.  The overhead of the thread management negated the gains. Added ~ %1 seconds to the time.

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

### 1.8.0
- Speed optimisations
  - Faster sorting
  - Search speed optimisations, about 15-30% faster
  - Filtering is about (maybe) 0.5 % faster, negligible
  - Faster search when using a minimum length
- Refined formating of text output
- Corrected option pretty_json to pretty-json
  - also proper json formating
- New options 
  - All duplicate in results options
  - Load a puzzle file option
  - Export 2 csv
- Filtering for non-ascii characters in puzzle option
- Added stat for how many full/partial words were looked up in the dictionary
- Included benchmarking puzzle file [puzzle.dat](benchmark/puzzle32.dat)

### 1.8.1
- Spelling correction of "word_lokups" -> "word_lookups"
- Benchmark tests
  - Moved puzzle.dat -> benchmark/puzzle32.dat
  - Created a benchmark/puzzle64.dat
  - Created a benchmark/puzzle128.dat
  - Created 2 scripts to benchmark, a sh (earlier) and a python, significantly better
  - Doc

### 1.8.2
- Removed unintended sorting when filtering originals
- Added a `total_word_count` to json output regardless of options
- Added a puzzle
  - clusters.txt, example: `boggle_solver.py -s 12 --puzzle-file puzzle_files/clusters.txt --randomise`
```
  Puzzle:
===============================================
 d   s   o   e   p   o   o   t   e   h   s   t
 o   g   t   c   t   i   n   h  thr  d   m   m
 fl  u   o   pl  a   a   cr  m   r   a   h  shr
 o   a   m   x   bl  sk  c  scr  sn  t   h   fr
 l   n   e   e   sl  e   a   r   l   e   f   gl
 tw str  e   v   n   r   l   e   k   sp  f   o
 sw  d   l   r   tr  k   t   e   w   g   gr  dr
 n   e   cl  n   w   n   w   k   c   c   o   sm
 t   st  h   o   d   f   e   l   n   pr  j   w
 h   l   l   i   n   i   i   r   t   s   l   o
 r  spl  s   e   e   sc  a   a   b   br  r   o
 c   o   e  spr  n   b   n   s   u   l   b   a
===============================================
```

### 1.9.0
- Added the ability to simulate keyboard input on mac like windows

### 1.9.1
- Saves last dictionary, speed and time to enter the next window as the defaults for the next run
  - You no longer need to specify then everytime
- Moved default dictionary to dictionaries folder `dictionary.hd` -> `dictionaries/default.hd`
- Cleaned up the helkp and changed a few options 
  - `-C` -> `-c`, contains
  - `-r` -> `-O`, reverse order
  - `-r`, became the options for randomise
  - `-D`, keep duplicates

### 1.10.0
- On average 25x faster on puzzles larger than 5, 5-20x faster on 3-5
  - Was looking at code after counting lookups and realised I was doing alot of duplicate lookups
- Fixed an output on stdout that would have affected json parsing
- Updated benchmarks with new run

### New in convert_dictionary.py

#### 1.1.1
- Fixed read/write issue when testing a dictionary

#### 2.0
- What started as an update became an overhaul
  - Added support for hunspell dictionaries *.dic
  - Type hinting
  - Improved lookup function for solver
  - Reorganising parameters