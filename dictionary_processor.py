import string
import argparse
from tqdm import tqdm
from word_database import WordDatabase
from word_shape import WordShape

class DictionaryProcessor:
    def __init__(self, dictionary_path, db_name):
        self.word_shape = WordShape()
        self.word_db = WordDatabase(db_name)
        self.dictionary_path = dictionary_path

    def sanitize_word(self, word):
        word = word.strip().lower()
        if not all(char in string.ascii_lowercase for char in word):
            return None
        return word

    def process_dictionary(self):
        with open(self.dictionary_path, 'r') as f:
            lines = f.readlines()
        for line in tqdm(lines, desc="Processing dictionary", unit="words"):
            word = self.sanitize_word(line)
            if word is not None:
                shape = self.word_shape.get_shape(word)
                normalized_shapes = self.word_shape.normalize_shape(word, shape)
                polygonal_shape = self.word_shape.get_polygon_shape(word)
                polygonal_area = self.word_shape.get_polygon_area(polygonal_shape)
                perimeter = self.word_shape.get_perimeter(word)
                self.word_db.store_word(word, shape, normalized_shapes, polygonal_shape, polygonal_area, perimeter)
        self.word_db.flush()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process dictionary.')
    parser.add_argument('dictionary_path', help='Path to the dictionary file')
    parser.add_argument('db_path', help='Path to the database file; will create a new databse if one does not exist')
    args = parser.parse_args()

    processor = DictionaryProcessor(args.dictionary_path, args.db_path)
    processor.process_dictionary()
