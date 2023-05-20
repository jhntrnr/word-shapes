import sys
import os
import math
import scott as st
import numpy as np
import hashlib
from letter_wheel import LetterWheel

class WordShape:
    def __init__(self):
        self.letter_wheel = LetterWheel()

    def get_shape(self, word):
        """Returns the rounded coordinates of a word to guard against float imprecision when mirroring."""
        return [self.letter_wheel.get_coordinates(letter) for letter in word]

    def get_polygon_shape(self, word):
        """Returns the polygonal shape of a word: letter coordinates trimmed to unique letters and alphabetized."""
        unique_letters = sorted(set(word))
        return [self.letter_wheel.get_coordinates(letter, True) for letter in unique_letters]

    def get_polygon_area(self, shape):
        """Finds the area of the given polygonal shape.
        Returns 0 if one point;
        Returns length of line if two points;
        Returns area if more than two points"""
        if len(shape) < 3:
            return 0

        x = [coord[0] for coord in shape]
        y = [coord[1] for coord in shape]
        area = self.polygon_area(x, y)
        return np.format_float_positional(area, precision=10, unique=False, fractional=False, trim='k')

    def polygon_area(self, x, y):
        return 0.5 * abs(sum(x[i - 1] * y[i] - x[i] * y[i - 1] for i in range(len(x))))

    def get_perimeter(self, word):
        """Calculate the perimeter of a word."""
        letter_coords = [self.letter_wheel.get_coordinates(letter, True) for letter in word]
        perimeter = 0
        for i in range(len(letter_coords) - 1):
            perimeter += np.linalg.norm(np.array(letter_coords[i+1]) - np.array(letter_coords[i]))
        return np.format_float_positional(perimeter, precision=10, unique=False, fractional=False, trim='k')

    def get_angle(self, point1, point2):
            return point2[1] - point1[1]

    def get_first_edge_angle(self, word):
        """Returns the angle of the first 'edge' (pair of non-identical letters) in the word."""
        for a, b in zip(word, word[1:]):
            if a != b:
                return self.get_angle(self.letter_wheel.get_coordinates(a), self.letter_wheel.get_coordinates(b))
        return 0.0

    def rotate_to_a(self, word):
        """Shifts or rotates a word so that it begins with the letter 'a'."""
        shift = ord('a') - ord(word[0])

        rotated_word = ''.join(chr((ord(c) - ord('a') + shift) % 26 + ord('a')) for c in word)

        return rotated_word

    def reflect_word(self, word):
        """Rotates the word such that the first 'edge' is in the 'positive' direction."""
        angle = self.get_first_edge_angle(word)
        if angle < 0:
            reflected_coordinates = [self.letter_wheel.reflect_letter(c) for c in word]
            return ''.join(self.letter_wheel.get_letter_from_coordinates(coord) for coord in reflected_coordinates)
        return word

    def create_graph(self, word):
        """Turns a word into a graph, letters connected by edges."""
        graph = st.structs.graph.Graph()
        node_dict = {}

        for letter in word:
            if letter not in node_dict:
                node = st.structs.node.Node(letter, letter)
                graph.add_node(node)
                node_dict[letter] = node

        for letter1, letter2 in zip(word, word[1:]):
            if letter1 != letter2:
                edge = st.structs.edge.Edge(''.join(sorted([letter1, letter2])), node_dict[letter1], node_dict[letter2])
                with HiddenPrints():
                    graph.add_edge(edge)
        return graph


    def normalize_shape(self, word, shape):
        """'Rotate' a word such that it begins with 'a'.
        Also reverse the word and perform the same rotation.
        Create a graph from each word and compute its canonical form using scott.
        Hash each word and return the hash of highest value.
        """
        while word[0:2] == word[-2:][::-1] and len(word) > 2:
            word = word[:-1]
        rotated_word = self.rotate_to_a(word)
        reversed_rotated_word = self.rotate_to_a(word[::-1])
        reflected_word = self.reflect_word(rotated_word)
        reversed_reflected_word = self.reflect_word(rotated_word[::-1])

        graph = self.create_graph(rotated_word)
        reversed_graph = self.create_graph(reversed_rotated_word)
        reflected_graph = self.create_graph(reflected_word)
        reversed_reflected_graph = self.create_graph(reversed_reflected_word)

        cgraph = st.canonize.to_cgraph(graph)
        reversed_cgraph = st.canonize.to_cgraph(reversed_graph)
        reflected_cgraph = st.canonize.to_cgraph(reflected_graph)
        reversed_reflected_cgraph = st.canonize.to_cgraph(reversed_reflected_graph)

        hash1 = int(hashlib.sha224(str(cgraph).encode()).hexdigest(), 16)
        hash2 = int(hashlib.sha224(str(reversed_cgraph).encode()).hexdigest(), 16)
        hash3 = int(hashlib.sha224(str(reflected_cgraph).encode()).hexdigest(), 16)
        hash4 = int(hashlib.sha224(str(reversed_reflected_cgraph).encode()).hexdigest(), 16)

        return max(hash1, hash2, hash3, hash4)

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout