# word-shapes
Applying various concepts of shape to English words

## Installation
```sh
git clone https://github.com/jhntrnr/word-shapes.git
cd word-shapes
pip install -r requirements.txt
```

## Usage
```sh
# word_explorer.py is the GUI application
py word_explorer.py

# dictionary_processor.py can optionally be run from the command line
# dictionary_processor.py creates a databse of word shapes from a supplied dictionary
py dictionary_processor.py path_to_dictionary_file path_to_database_file
```
In the GUI application `word_explorer.py`, you must first load a database of word shapes. `File -> Load Database`

For convenience, an abridged database already populated with around 11,500 word shapes has been supplied in the `./database` directory of this repository.

To create a databse from a new word list, you must load a dictionary file (a collection of words delimited by newlines). `File -> Open Dictionary`

Then, choose a name and location for the database. `File -> New Database`

Then, populate the database. `Create Shapes -> Create Shapes`

Creating shapes will take anywhere from a few minutes to several hours depending on the number of words in the dictionary. Progress can be monitored in the command line.

## Word Shapes
Words are projected onto a unit circle "letter wheel" that has been subdivided into 26 segments of PI/13 radians.
This gives the words a shape that can be defined in a number of ways.

- Perimeter shapes
  - The distance between sequential letters in a word is calculated
  - The total distance covered is the word's perimeter shape
  - Two words with the same total distance are considered to have the same perimeter shape
    - Example: `snail` and `chump`

![snailchump](https://github.com/jhntrnr/word-shapes/assets/90057903/c5f1f19e-8f65-4e26-b3a7-7fbbd57949e6)

- Polygonal area
  - A bounding polygon is created by connecting each unique letter of a word alphabetically
  - The area of this polygon is the word's polygonal area
  - Two words with the same total polygonal area are considered to have the same polygonal shape
    - Example: `machine` and `triumph`

![machinetriumph](https://github.com/jhntrnr/word-shapes/assets/90057903/e960ad1b-3766-41fd-93cb-8f3aa42452ca)

- Graph shapes
  - Each unique letter in the word is a node
  - Adjacent letters in a word are connected by edges
  - Only unique edges are allowed; self-loops are not allowed
  - Word graphs are normalized (rotated to being with `a`; flipped over the x-axis; reversed)
  - Words whose normalized graphs are isomorphic are considered to have the same graph shape
    - Example: `bunny` and `sleep`

![bunnysleep](https://github.com/jhntrnr/word-shapes/assets/90057903/8dc0eec0-141e-453a-9ef4-dde6e8ef8872)

## Findings
It is rare for two or more words to have the same graph shape. Roughly 85-95% of words (depending on the wordlist used) have unique graph shapes.
Many words that share graph shapes with one another are prefixed or suffixed forms of the same word (`transcendentalist` and `transcendentalists`, for example).
The rarity of shared graph shapes is due to the relatively strict definition compared to that of polygonal or perimeter shapes.

It is considerably more common for words to share perimeter shapes. Roughly 50% of words have unique perimeter shapes.
This is due to the relatively small number of unique coordinates on the letter wheel.
Words can be made up of entirely different letters that don't share relative positions on the letter wheel, but still share a perimeter.

Polygonal shape is by far the most common shared word shape. Around 0.1 - 1% of words have unique polygonal shapes.
This is due to a number of factors, including those that make shared perimeter shapes relatively common.
Additionally, words that are anagrams--or even near-anagrams that don't necessarily have a 1:1 letter mapping but share a set of unique letters (`ball` and `lab`, for example)--will always share a polygonal shape.
Further, words with only one or two unique letters will necessarily have a polygonal shape of 0, as their bounding "polygon" is a point or line with no area.
