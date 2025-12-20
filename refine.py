import sqlite3
import os, apsw, re
from agentmake import agentmake
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser
from biblemate import AGENTMAKE_CONFIG

DATABASE_NAME = 'ai_commentary.db'

def initialize_db(db_name=DATABASE_NAME):
    """
    Connects to the SQLite database and creates the 'Commentary' table 
    if it does not already exist.
    """
    try:
        # Connect to the SQLite database (creates the file if it doesn't exist)
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # SQL command to create the table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS Commentary (
            Book INTEGER,
            Chapter INTEGER,
            Verse INTEGER,
            Content TEXT
        );
        """
        
        # Execute the table creation command
        cursor.execute(create_table_sql)
        conn.commit()
        
        print(f"Database '{db_name}' initialized successfully.")
        return conn
    except sqlite3.Error as e:
        print(f"An error occurred during database initialization: {e}")
        return None

def insert_commentary(conn, book, chapter, verse, scripture):
    """
    Inserts a new entry into the Commentary table.
    
    Args:
        conn (sqlite3.Connection): The database connection object.
        book (int): The book number.
        chapter (int): The chapter number.
        scripture (str): The text of the commentary/scripture.
    """
    if conn is None:
        print("Cannot insert data: Database connection is not established.")
        return

    try:
        cursor = conn.cursor()
        
        # Use parameterized query (?) to safely insert data
        # This prevents SQL injection attacks
        insert_sql = """
        INSERT INTO Commentary (Book, Chapter, Verse, Content)
        VALUES (?, ?, ?, ?);
        """
        
        # The values are passed as a tuple
        cursor.execute(insert_sql, (book, chapter, verse, scripture))
        conn.commit()
        print(f"Inserted: Book={book}, Chapter={chapter}, verse={verse}")
        
    except sqlite3.Error as e:
        print(f"An error occurred during insertion: {e}")

def fetch_all_commentary(conn):
    """Fetches and prints all entries in the Commentary table."""
    if conn is None:
        return
        
    cursor = conn.cursor()
    cursor.execute("SELECT Book, Chapter, Scripture FROM Commentary")
    rows = cursor.fetchall()
    
    if not rows:
        print("The Commentary table is currently empty.")
        return
        
    print("\n--- All Commentary Entries ---")
    for row in rows:
        print(f"Book: {row[0]}, Chapter: {row[1]}, Text: '{row[2][:50]}...'")
    print("----------------------------")

def get_commentary(b, c, v):
    db = os.path.expanduser("bible_commentary.db")
    with apsw.Connection(db) as connn:
        cursor = connn.cursor()
        cursor.execute("SELECT * FROM Commentary WHERE Book=? AND Chapter=? AND Verse=?", (b,c,v))
        fetch = cursor.fetchone()
    return fetch

def fetch_net_verses():
    db = os.path.expanduser("~/UniqueBible/marvelData/bibles/NET.bible")
    with apsw.Connection(db) as connn:
        cursor = connn.cursor()
        cursor.execute("SELECT * FROM Verses")
        fetches = cursor.fetchall()
    return fetches

def fetch_ohgbi_verse(b,c,v):
    db = os.path.expanduser("~/UniqueBible/marvelData/bibles/OHGBi.bible")
    with apsw.Connection(db) as connn:
        cursor = connn.cursor()
        cursor.execute("SELECT Scripture FROM Verses WHERE Book=? AND Chapter=? AND Verse=?", (b,c,v))
        fetch = cursor.fetchone()
    if not fetch: return ""
    content = fetch[0]
    content = content.replace("<gloss>", " <gloss>")
    return re.sub("<.*?>", "", content)

def fetch_morpholoygical_data(b,c,v):
    db = os.path.expanduser("~/UniqueBible/marvelData/morphology.sqlite")
    with apsw.Connection(db) as connn:
        cursor = connn.cursor()
        cursor.execute("SELECT * FROM morphology WHERE Book=? AND Chapter=? AND Verse=? ORDER BY WordID", (b,c,v))
        fetches = cursor.fetchall()
    if not fetches: return ""
    results = []
    for wordID, clauseID, book, chapter, verse, word, lexicalEntry, morphologyCode, morphology, lexeme, transliteration, pronunciation, interlinear, translation, gloss in fetches:
        results.append(f"Word: {word} | Lexeme: {lexeme} | Morphology: {morphology} | Interlinear: {interlinear}")
    return "\n".join(results)

if __name__ == '__main__':
    # 1. Initialize the database and get the connection object
    db_connection = initialize_db()

    if db_connection:
        parser = BibleVerseParser(False)
        for b, c, v, _ in fetch_net_verses():
            if comment := get_commentary(b,c,v):
                insert_commentary(db_connection, *comment)