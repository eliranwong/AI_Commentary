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

def entry_exists(conn, book, chapter, verse):
    """
    Check if an entity exists in the Commentary table.
    """
    if conn is None:
        print("Cannot check: Database connection is not established.")
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Commentary WHERE Book=? AND Chapter=? AND Verse=?", (book, chapter, verse))
        fetch = cursor.fetchone()
        if fetch:
            return True
    except sqlite3.Error as e:
        print(f"An error occurred during insertion: {e}")
    return False

def check_is_commentary(conn, book, chapter, verse):
    """
    Check if an entity exists in the Commentary table.
    """
    if conn is None:
        print("Cannot check: Database connection is not established.")
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Commentary WHERE Book=? AND Chapter=? AND Verse=?", (book, chapter, verse))
        fetch = cursor.fetchone()
        if fetch and not "Conclusion" in fetch[-1] and not "Summary" in fetch[-1] and not "If you’d like" in fetch[-1]:
            return False
        elif fetch and not fetch[-1].strip().endswith("[NO_CONTENT]"):
            return True
    except sqlite3.Error as e:
        print(f"An error occurred during insertion: {e}")
    return False


def insert_commentary(conn, book, chapter, verse, content, update=False):
    """
    Inserts a new entry into the Commentary table.
    
    Args:
        conn (sqlite3.Connection): The database connection object.
        book (int): The book number.
        chapter (int): The chapter number.
        content (str): The text of the commentary.
    """
    if conn is None:
        print("Cannot insert data: Database connection is not established.")
        return

    try:
        cursor = conn.cursor()
        if update:
            update_query = """
                UPDATE Commentary 
                SET Content = ? 
                WHERE Book = ? AND Chapter = ? AND Verse = ?
            """
            cursor.execute(update_query, (content, book, chapter, verse))
        else:
            insert_sql = """
            INSERT INTO Commentary (Book, Chapter, Verse, Content)
            VALUES (?, ?, ?, ?);
            """
            cursor.execute(insert_sql, (book, chapter, verse, content))
        conn.commit()
        print(f"{'Updated' if update else 'Inserted'}: Book={book}, Chapter={chapter}, verse={verse}")
        
    except sqlite3.Error as e:
        print(f"An error occurred during insertion: {e}")

def fetch_all_commentary(conn):
    """Fetches and prints all entries in the Commentary table."""
    if conn is None:
        return
        
    cursor = conn.cursor()
    cursor.execute("SELECT Book, Chapter, Content FROM Commentary")
    rows = cursor.fetchall()
    
    if not rows:
        print("The Commentary table is currently empty.")
        return
        
    print("\n--- All Commentary Entries ---")
    for row in rows:
        print(f"Book: {row[0]}, Chapter: {row[1]}, Text: '{row[2][:50]}...'")
    print("----------------------------")

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
        #for b, c, v, net_verse in fetch_net_verses():
            #if check_is_commentary(db_connection, b, c, v):
            #    continue
        for b, c, v, net_verse in [
            #(19, 103, 18, "to those who keep his covenant, who are careful to obey his commands."),
            (27, 2, 44, "In the days of those kings the God of heaven will raise up an everlasting kingdom that will not be destroyed and a kingdom that will not be left to another people. It will break in pieces and bring about the demise of all these kingdoms. But it will stand forever."),
        ]:
            print("Working on verse:", b, c, v, net_verse)
            error = f"No content for this verse: {b} {c}:{v}"
            ref = parser.bcvToVerseReference(b,c,v)
            interlinear_verse = fetch_ohgbi_verse(b,c,v)
            if not interlinear_verse:
                error = f"No interlinear verse for this verse: {b} {c}:{v}"
                print(error)
                with open("errors.txt", "a") as f:
                    f.write(error+"\n")
                continue
            morpholoygical_data = fetch_morpholoygical_data(b,c,v)
            prompt = f"""# Write a detailed commentary on the following Bible verse:

## {ref}
{net_verse}

## Interlinear ({'Hebrew' if b < 40 else 'Greek'} with literal translation):
{interlinear_verse}

## Morphological data of each word:
{morpholoygical_data}

Commentary:"""
            messages = agentmake(prompt, system="biblemate/commentary", **AGENTMAKE_CONFIG)
            content = messages[-1].get("content") if messages and "content" in messages[-1] else ""
            if not content:
                print(error)
                with open("errors.txt", "a") as f:
                    f.write(error+"\n")
                continue
            content = parser.parseText(content)
            content = f"# Commentary - {ref}\n\n"+content
            # update database
            insert_commentary(db_connection, b, c, v, content, entry_exists(db_connection, b, c, v))
        
        # 4. Close the connection when done
        db_connection.close()
        print(f"\nConnection to '{DATABASE_NAME}' closed.")
    else:
        print("Script execution failed due to database connection error.")