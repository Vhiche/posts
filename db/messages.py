from db.config import get_connection


def getMessagesByChatId(id):
    connection = get_connection()
    connection.execute("""
CREATE TABLE IF NOT EXISTS message (
    id INTEGER PRIMARY KEY,
    text TEXT NOT NULL,
    datetime DATETIME NOT NULL,
    chat_id INTEGER NOT NULL,
    sender_id INTEGER NOT NULL,
    FOREIGN KEY (chat_id) REFERENCES chat(id),
    FOREIGN KEY (sender_id) REFERENCES client(id)
)
    """)
    query = """SELECT * FROM message WHERE chat_id = ?"""
    args = [id]
    cur = connection.execute(query, args)
    res = cur.fetchall()
    cur.close()
    connection.close()
    return res


def createMessage(text, datetime, chat_id, sender_id):
    connection = get_connection()
    connection.execute("""
CREATE TABLE IF NOT EXISTS message (
    id INTEGER PRIMARY KEY,
    text TEXT NOT NULL,
    datetime DATETIME NOT NULL,
    chat_id INTEGER NOT NULL,
    sender_id INTEGER NOT NULL,
    FOREIGN KEY (chat_id) REFERENCES chat(id),
    FOREIGN KEY (sender_id) REFERENCES client(id)
)
""")
    query = """INSERT INTO message (text, datetime, chat_id, sender_id) VALUES (?, ?, ?, ?)"""
    args = [text, datetime, chat_id, sender_id]
    cur = connection.execute(query, args)
    connection.commit()
    cur.close()
    connection.close()




