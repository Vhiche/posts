from db.config import get_connection


def getAllPosts():
    connection = get_connection()
    connection.execute("""
CREATE TABLE IF NOT EXISTS post (
    id INTEGER PRIMARY KEY,
    text TEXT NOT NULL,
    filename TEXT,
    datetime DATETIME NOT NULL,
    client_id INTEGER NOT NULL
)
    """)
    query = """SELECT * FROM post ORDER BY post.datetime DESC"""
    cur = connection.execute(query)
    res = cur.fetchall()
    cur.close()
    connection.close()
    return res


def getPostById(id):
    connection = get_connection()
    connection.execute("""
CREATE TABLE IF NOT EXISTS post (
    id INTEGER PRIMARY KEY,
    text TEXT NOT NULL,
    filename TEXT,
    datetime DATETIME NOT NULL,
    client_id INTEGER NOT NULL
)
    """)
    query = """SELECT * FROM post WHERE id = ?"""
    args = [id]
    cur = connection.execute(query, args)
    res = cur.fetchone()
    cur.close()
    connection.close()
    return res


def createPost(text, filename, date_time, client_id):
    connection = get_connection()
    connection.execute("""
CREATE TABLE IF NOT EXISTS post (
    id INTEGER PRIMARY KEY,
    text TEXT NOT NULL,
    filename TEXT,
    datetime DATETIME NOT NULL,
    client_id INTEGER NOT NULL
)
    """)
    query = """INSERT INTO post (text, filename, datetime, client_id) VALUES (?, ?, ?, ?)"""
    args = [text, filename, date_time, client_id]
    cur = connection.execute(query, args)
    connection.commit()
    cur.close()
    connection.close()


def deletePostById(id):
    connection = get_connection()
    connection.execute("""
CREATE TABLE IF NOT EXISTS post (
    id INTEGER PRIMARY KEY,
    text TEXT NOT NULL,
    filename TEXT,
    datetime DATETIME NOT NULL,
    client_id INTEGER NOT NULL
)
    """)
    query = """DELETE FROM post WHERE id = ?"""
    args = [id]
    cur = connection.execute(query, args)
    connection.commit()
    cur.close()
    connection.close()
