import sqlite3
import json
import atexit

class WordDatabase:
    def __init__(self, db_name, batch_size=1000):
        self.conn = sqlite3.connect(db_name)
        self.create_table()
        self.conn.commit()
        self.batch_size = batch_size
        self.batch = []
        atexit.register(self.flush)

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS word_shapes (
                word TEXT PRIMARY KEY,
                shape TEXT,
                normalized_shape TEXT,
                polygonal_shape TEXT,
                polygonal_area REAL,
                perimeter REAL
            )
        """)
        self.conn.commit()

    def store_word(self, word, shape, normalized_shape, polygonal_shape, polygonal_area, perimeter):
        self.batch.append((word, json.dumps(shape), json.dumps(normalized_shape), json.dumps(polygonal_shape), polygonal_area, perimeter))
        if len(self.batch) >= self.batch_size:
            self.flush()

    def flush(self):
        if self.batch:
            cursor = self.conn.cursor()
            cursor.executemany("INSERT OR IGNORE INTO word_shapes (word, shape, normalized_shape, polygonal_shape, polygonal_area, perimeter) VALUES (?, ?, ?, ?, ?, ?)", self.batch)
            self.conn.commit()
            self.batch = []

    def __del__(self):
        self.flush()

    def validate_database(self):
        cursor = self.conn.cursor()
        cursor.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='word_shapes'""")
        table_exists = cursor.fetchone()
        if not table_exists:
            raise Exception("Database validation failed: Table 'word_shapes' does not exist.")

        cursor.execute("PRAGMA table_info(word_shapes)")
        columns = [column[1] for column in cursor.fetchall()]
        required_columns = ["word", "shape", "normalized_shape", "polygonal_shape", "polygonal_area", "perimeter"]

        for required_column in required_columns:
            if required_column not in columns:
                raise Exception(f"Database validation failed: Column '{required_column}' does not exist in table 'word_shapes'.")

    def get_shape_of_word(self, word, column):
        if column not in {"normalized_shape", "polygonal_area", "perimeter"}:
            raise ValueError("Invalid column name: " + column)
        cursor = self.conn.cursor()
        query = f"SELECT {column} FROM word_shapes WHERE word = ?"
        cursor.execute(query, (word,))
        result = cursor.fetchone()

        if result is None:
            raise ValueError(f"No shape data found for word '{word}'")

        return result

    def find_words_with_same_shape(self, word, column):
        if column not in {"normalized_shape", "polygonal_area", "perimeter"}:
            raise ValueError("Invalid column name: " + column)

        word_shape = self.get_shape_of_word(word, column)

        cursor = self.conn.cursor()

        query = f"SELECT word FROM word_shapes WHERE {column} IN (?)"
        cursor.execute(query, (word_shape))

        words_with_same_shape = [row[0] for row in cursor.fetchall()]

        return words_with_same_shape

    def most_common_word_shape(self, column):
        if column not in {"normalized_shape", "polygonal_area", "perimeter"}:
            raise ValueError("Invalid column name: " + column)

        cursor = self.conn.cursor()
        query = f"""
        SELECT {column}, COUNT(*) as count 
        FROM word_shapes
        GROUP BY {column}
        ORDER BY count DESC 
        LIMIT 1
        """
        cursor.execute(query)
        common_shape = cursor.fetchone()[0]
        
        query_words = f"SELECT word FROM word_shapes WHERE {column}=?"
        cursor.execute(query_words, (common_shape,))
        words_with_common_shape = [row[0] for row in cursor.fetchall()]

        return words_with_common_shape

    def percentage_unique_shapes(self, column: str) -> float:
        if column not in {"normalized_shape", "polygonal_area", "perimeter"}:
            raise ValueError("Invalid column name: " + column)

        cursor = self.conn.cursor()
        query_total = "SELECT COUNT(*) FROM word_shapes"
        query_unique = f"""
        SELECT COUNT(*) 
        FROM (
            SELECT {column} 
            FROM word_shapes
            GROUP BY {column}
            HAVING COUNT(*) = 1
        )
        """
        cursor.execute(query_total)
        total_words = cursor.fetchone()[0]
        cursor.execute(query_unique)
        unique_words = cursor.fetchone()[0]

        return (unique_words / total_words) * 100

    def total_shapes(self, column: str) -> int:
        if column not in {"normalized_shape", "polygonal_area", "perimeter"}:
            raise ValueError("Invalid column name: " + column)

        cursor = self.conn.cursor()
        query = f"SELECT COUNT(DISTINCT {column}) FROM word_shapes"
        cursor.execute(query)
        return cursor.fetchone()[0]

    def longest_shared_shape_word(self, column: str) -> str:
        if column not in {"normalized_shape", "polygonal_area", "perimeter"}:
            raise ValueError("Invalid column name: " + column)

        cursor = self.conn.cursor()
        query = f"""
        SELECT word, MAX(LENGTH(word)) as len
        FROM word_shapes
        WHERE {column} IN (
            SELECT {column}
            FROM (
                SELECT {column}, COUNT(*) as count 
                FROM word_shapes
                GROUP BY {column}
                HAVING count > 1
            )
        )
        ORDER BY len DESC
        LIMIT 1
        """
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            return self.find_words_with_same_shape(result[0], column)
        else:
            return None

    def random_word_shared_shape(self, column: str) -> str:
        if column not in {"normalized_shape", "polygonal_area", "perimeter"}:
            raise ValueError("Invalid column name: " + column)

        cursor = self.conn.cursor()
        query = f"""
        SELECT word, LENGTH(word) as len
        FROM word_shapes
        WHERE {column} IN (
            SELECT {column}
            FROM (
                SELECT {column}, COUNT(*) as count
                FROM word_shapes
                GROUP BY {column}
                HAVING count > 2
            )
        )
        GROUP BY word
        HAVING len > 1
        ORDER BY RANDOM()
        LIMIT 1
        """
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            return result
        else:
            return None