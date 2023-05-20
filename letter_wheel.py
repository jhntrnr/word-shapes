import math

class LetterWheel:
    def __init__(self):
        self.letter_mapping = self.generate_letter_mapping()
        self.high_precision_letter_mapping = self.generate_letter_mapping(True)

    def generate_letter_mapping(self, high_precision = False):
        """Iterate over the English alphabet and return a dictionary mapping each letter to an angle."""
        letter_mapping = {}
        for i, letter in enumerate('abcdefghijklmnopqrstuvwxyz'):
            angle = (2 * math.pi * i) / 26
            if high_precision:
                letter_mapping[letter] = (math.cos(angle), math.sin(angle))
            else:
                letter_mapping[letter] = (round(math.cos(angle), 2), round(math.sin(angle), 2))
        return letter_mapping

    def get_coordinates(self, letter, high_precision = False):
        """Fetch the coordinates of a letter from the mapping."""
        if high_precision:
            return self.high_precision_letter_mapping[letter]
        return self.letter_mapping[letter]

    def reflect_letter(self, letter):
        """Reflect a letter across the x-axis."""
        x, y = self.get_coordinates(letter)
        return (x, -y)
    
    def get_letter_from_coordinates(self, coordinates):
        """Return the letter corresponding to given coordinates."""
        for letter, coord in self.letter_mapping.items():
            if coord[0] == coordinates[0] and coord[1] == coordinates[1]:
                return letter
        return None