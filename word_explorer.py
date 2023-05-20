import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QTextEdit, QLabel, QPushButton, QComboBox, QMainWindow, QAction, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from word_database import WordDatabase
from word_shape import WordShape
from dictionary_processor import DictionaryProcessor
from letter_wheel import LetterWheel

class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MatplotlibCanvas, self).__init__(self.fig)

class WordShapeApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.word_shape = WordShape()
        self.letter_wheel = LetterWheel()
        self.letter_wheel_canvas = MatplotlibCanvas(self, width=5, height=4, dpi=100)

        self.mode_selection = QComboBox()
        self.mode_columns = {}
        self.mode_selection.addItem("Graph Shape")
        self.mode_columns["Graph Shape"] = "normalized_shape"
        self.mode_selection.addItem("Polygonal Shape")
        self.mode_columns["Polygonal Shape"] = "polygonal_area"
        self.mode_selection.addItem("Perimeter")
        self.mode_columns["Perimeter"] = ("perimeter")
        self.mode_selection.currentIndexChanged.connect(self.update_display_mode)
        self.current_display_mode = "Graph Shape"

        self.dictionary_path = ''
        self.database_path = ''

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Word Shape Explorer")
        self.setGeometry(500, 500, 400, 300)
        
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        shape_menu = menubar.addMenu('Create Shapes')

        self.open_file = QAction('Load Database', self)
        self.open_file.triggered.connect(self.load_database)
        file_menu.addAction(self.open_file)

        self.new_file = QAction('New Database', self)
        self.new_file.triggered.connect(self.new_database)
        file_menu.addAction(self.new_file)

        self.open_dictionary = QAction('Open Dictionary', self)
        self.open_dictionary.triggered.connect(self.load_dictionary)
        file_menu.addAction(self.open_dictionary)

        self.populate_database = QAction('Create Shapes', self)
        self.populate_database.triggered.connect(self.run_shape_creation)
        shape_menu.addAction(self.populate_database)

        self.widget = QWidget()
        self.setCentralWidget(self.widget)

        self.layout = QVBoxLayout(self.widget)
        self.layout.addWidget(self.mode_selection)
        self.layout.addWidget(self.letter_wheel_canvas)
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter a word")
        self.input_field.returnPressed.connect(self.search_word)

        self.output_field = QTextEdit()
        self.output_field.setReadOnly(True)

        self.common_shape_button = QPushButton('Find most common word shape')
        self.common_shape_button.clicked.connect(self.most_common_word_shape)

        self.unique_percentage_button = QPushButton('Find percentage of unique word shapes')
        self.unique_percentage_button.clicked.connect(self.percentage_unique_shapes)

        self.total_shapes_button = QPushButton('Find total number of shapes')
        self.total_shapes_button.clicked.connect(self.total_shapes)

        self.longest_word_button = QPushButton('Find longest word with a shared shape')
        self.longest_word_button.clicked.connect(self.longest_shared_shape_word)
        
        self.random_word_button = QPushButton('Find random word with a shared shape')
        self.random_word_button.clicked.connect(self.random_word_shared_shape)

        self.layout.addWidget(QLabel("Enter a word to find others with the same shape:"))
        self.layout.addWidget(self.input_field)
        self.layout.addWidget(QLabel("Words with the same shape:"))
        self.layout.addWidget(self.output_field)
        self.layout.addWidget(self.common_shape_button)
        self.layout.addWidget(self.unique_percentage_button)
        self.layout.addWidget(self.total_shapes_button)
        self.layout.addWidget(self.longest_word_button)
        self.layout.addWidget(self.random_word_button)
        self.display_many_words('')

    def update_display_mode(self, index):
        self.current_display_mode = self.mode_selection.itemText(index)
        self.display_many_words([self.input_field.text().strip()])

    def load_database(self):
        fname = QFileDialog.getOpenFileName(self, 'Open database file', directory='./database')
        if fname[0]:
            try:
                self.word_database = WordDatabase(fname[0])
                self.word_database.validate_database()
                self.database_path = fname[0]
            except Exception as e:
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setWindowTitle("Database Load Error")
                error_dialog.setText("Failed to load the database.")
                error_dialog.setInformativeText(str(e))
                error_dialog.exec_()

    def new_database(self):
        fname = QFileDialog.getSaveFileName(self, 'Create database file', directory='./database')
        if fname[0]:
            try:
                self.word_database = WordDatabase(fname[0])
                self.database_path = fname[0]
            except Exception as e:
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setWindowTitle("Database Load Error")
                error_dialog.setText("Failed to load the database.")
                error_dialog.setInformativeText(str(e))
                error_dialog.exec_()

    def load_dictionary(self):
        fname = QFileDialog.getOpenFileName(self, 'Open dictionary file', directory='./dictionary')
        if fname[0]:
            try:
                self.dictionary_path = fname[0]
            except Exception as e:
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setWindowTitle("Dictionary Load Error")
                error_dialog.setText("Failed to load the dictionary.")
                error_dialog.setInformativeText(str(e))
                error_dialog.exec_()
    
    def run_shape_creation(self):
        if len(self.dictionary_path) == 0:
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setWindowTitle("Shape Creation Error")
            error_dialog.setText("Failed to load a dictionary.")
            error_dialog.exec_()
        else:
            self.dictionary_processor = DictionaryProcessor(self.dictionary_path, self.database_path)
            self.dictionary_processor.process_dictionary()

    def display_many_words(self, words):
        self.letter_wheel_canvas.axes.clear()
        self.letter_wheel_canvas.axes.set_yticklabels([])
        self.letter_wheel_canvas.axes.set_xticklabels([])
        self.letter_wheel_canvas.axes.set_yticks([])
        self.letter_wheel_canvas.axes.set_xticks([])
        self.letter_wheel_canvas.axes.set_xlim([-1.5,1.5])
        self.letter_wheel_canvas.axes.set_ylim([-1.5,1.5])
        self.letter_wheel_canvas.axes.set_aspect('equal', adjustable='datalim')

        circle = plt.Circle((0, 0), 1, color='gray', fill=False)
        self.letter_wheel_canvas.axes.add_artist(circle)

        for letter, coords in self.letter_wheel.letter_mapping.items():
            self.letter_wheel_canvas.axes.plot(*coords, 'r.')
            self.letter_wheel_canvas.axes.text(coords[0] * 1.1 - .06, coords[1] * 1.1-.06, letter, fontsize=12)
        
        cmap = plt.cm.get_cmap("viridis", len(words))
        cmap = cmap.reversed()
        if self.current_display_mode == "Polygonal Shape" and len(words) > 0:
            for i, word in enumerate(reversed(words)):
                if len(word) < 1:
                    continue
                polygon_shape = self.word_shape.get_polygon_shape(word)
                x_values = [coord[0] for coord in polygon_shape]
                y_values = [coord[1] for coord in polygon_shape]
                x_values.append(x_values[0])
                y_values.append(y_values[0])
                color = cmap(i)
                self.letter_wheel_canvas.axes.plot(
                    x_values,
                    y_values,
                    color=color,
                    linewidth = 2 if i == len(words) - 1 else 1,
                    alpha = 1 if i == len(words) - 1 else 0.05
                )
                self.letter_wheel_canvas.axes.fill(
                    x_values,
                    y_values,
                    color=color,
                    alpha = 0.2 if i == len(words) - 1 else 0,
                )
        else:
            for i, word in enumerate(reversed(words)):
                if len(word) < 1:
                    continue
                letter_coords = [self.letter_wheel.get_coordinates(letter) for letter in word]
                x_values = [coord[0] for coord in letter_coords]
                y_values = [coord[1] for coord in letter_coords]
                color = cmap(i)
                self.letter_wheel_canvas.axes.plot(
                    x_values,
                    y_values,
                    color=color,
                    linewidth = 2 if i == len(words) - 1 else 1,
                    alpha = 1 if i == len(words) - 1 else 0.3
                )

        self.letter_wheel_canvas.draw_idle()
        self.adjustSize()

    def search_word(self):
        word = self.input_field.text().strip()
        if not word:
            return
        try:
            words_with_same_shape = self.word_database.find_words_with_same_shape(word, self.mode_columns[self.current_display_mode])
            shape_of_word = self.word_database.get_shape_of_word(word, self.mode_columns[self.current_display_mode])
            index_of_input = words_with_same_shape.index(word)
            words_with_same_shape.insert(0, words_with_same_shape.pop(index_of_input))
            self.display_many_words(words_with_same_shape)
            self.output_field.setText(f"Word shape is: {shape_of_word[0]}\n" + '\n'.join(words_with_same_shape))
        except ValueError as e:
            self.output_field.setText(str(e))

    def most_common_word_shape(self):
        result = self.word_database.most_common_word_shape(self.mode_columns[self.current_display_mode])
        shape_of_word = self.word_database.get_shape_of_word(result[0], self.mode_columns[self.current_display_mode])
        self.display_many_words(result)
        self.output_field.setText(f"The most common word shape is: {shape_of_word[0]}\n" + '\n'.join(result))

    def percentage_unique_shapes(self):
        result = self.word_database.percentage_unique_shapes(self.mode_columns[self.current_display_mode])
        self.output_field.setText(f"The percentage of words with unique shapes is: {result}")

    def total_shapes(self):
        result = self.word_database.total_shapes(self.mode_columns[self.current_display_mode])
        self.output_field.setText(f"The total number of shapes is: {result}")

    def longest_shared_shape_word(self):
        result = self.word_database.longest_shared_shape_word(self.mode_columns[self.current_display_mode])
        shape_of_word = self.word_database.get_shape_of_word(result[0], self.mode_columns[self.current_display_mode])
        self.display_many_words(result)
        self.output_field.setText(f"The longest word with a shared shape is: {shape_of_word[0]}\n" + '\n'.join(result))

    def random_word_shared_shape(self):
        result = self.word_database.random_word_shared_shape(self.mode_columns[self.current_display_mode])
        shape_of_word = self.word_database.get_shape_of_word(result[0], self.mode_columns[self.current_display_mode])
        try:
            words_with_same_shape = self.word_database.find_words_with_same_shape(result[0],self.mode_columns[self.current_display_mode])
            self.display_many_words(words_with_same_shape)
            self.output_field.setText(f"Word shape is: {shape_of_word[0]}\n" + '\n'.join(words_with_same_shape))
        except ValueError as e:
            self.output_field.setText(str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = WordShapeApp()
    window.show()

    sys.exit(app.exec_())
