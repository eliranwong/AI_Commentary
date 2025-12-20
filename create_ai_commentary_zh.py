import sqlite3
import os, apsw, re
from agentmake import agentmake
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser
from biblemate import AGENTMAKE_CONFIG

DATABASE_NAME = 'ai_commentary_zh.db'

def request_chinese_response(prompt: str) -> str:
    return prompt + "\n\n# Response Language\n\nTraditional Chinese 繁體中文\n\n请使用繁體中文作所有回應，除了引用工具名稱或希伯來語或希臘語，或我特别要求你使用英文除外。"

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
        if fetch and not fetch[-1].strip().endswith("[NO_CONTENT]"):
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

def fetch_cuv_verses():
    db = os.path.expanduser("~/UniqueBible/marvelData/bibles/CUV.bible")
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
        parser = BibleVerseParser(False, language="tc")
        #for b, c, v, cuv_verse in fetch_cuv_verses():
        for b, c, v, cuv_verse in (
            (41, 9, 43, "倘若你一隻手叫你跌倒，就把它砍下來；你缺了肢體進入〔永〕生，強如有兩〔隻〕手落到地獄，入那不滅的火裏去。"),
            (41, 9, 45, "倘若你一隻腳叫你跌倒，就把它砍下來；你瘸腿進入〔永〕生，強如有兩隻腳被丟在地獄裏。"),
            (44, 19, 40, "今日的擾亂本是無緣無故，我們難免被查問。論到這樣聚眾，我們也說不出所以然來。」說了這話，便叫眾人散去。"),
            (45, 16, 23, "那接待我、也接待全教會的該猶問你們安。城內管銀庫的以拉都和兄弟括土問你們安。"),
            (47, 13, 12, "你們親嘴問安，彼此務要聖潔。眾聖徒都問你們安。"),
            (47, 13, 13, "願主耶穌基督的恩惠、上帝的慈愛、聖靈的感動〔常〕與你們眾人同在！"),
        ):
            #if check_is_commentary(db_connection, b, c, v):
            #    continue
            cuv_verse = re.sub("<[^<>]*?>", "", cuv_verse)
            print("Working on verse:", b, c, v, cuv_verse)
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
{cuv_verse}

## Interlinear ({'Hebrew' if b < 40 else 'Greek'} with literal translation):
{interlinear_verse}

## Morphological data of each word:
{morpholoygical_data}

聖經註釋："""
            messages = agentmake(request_chinese_response(prompt), system="biblemate/commentary", **AGENTMAKE_CONFIG)
            content = messages[-1].get("content") if messages and "content" in messages[-1] else ""
            if not content:
                print(error)
                with open("errors.txt", "a") as f:
                    f.write(error+"\n")
                continue
            content = parser.parseText(content)
            content = f"# 聖經註釋 - {ref}\n\n"+content
            # update database
            insert_commentary(db_connection, b, c, v, content, entry_exists(db_connection, b, c, v))
        
        # 4. Close the connection when done
        db_connection.close()
        print(f"\nConnection to '{DATABASE_NAME}' closed.")
    else:
        print("Script execution failed due to database connection error.")