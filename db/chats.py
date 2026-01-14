from db.config import get_connection


def getChatById(id):
    connection = get_connection()
    connection.execute("""
CREATE TABLE IF NOT EXISTS chat (
    id INTEGER PRIMARY KEY,
    first_client_id INTEGER NOT NULL,
    second_client_id INTEGER NOT NULL
)""")
    query = """SELECT * FROM chat WHERE id = ?"""
    args = [id]
    cur = connection.execute(query, args)
    res = cur.fetchone()
    cur.close()
    connection.close()
    return res


def getChatsWithClientById(client_id):
    connection = get_connection()
    connection.execute("""
CREATE TABLE IF NOT EXISTS chat (
    id INTEGER PRIMARY KEY,
    first_client_id INTEGER NOT NULL,
    second_client_id INTEGER NOT NULL
)""")
    query = """SELECT * FROM chat WHERE first_client_id = ? OR second_client_id = ?"""
    args = [client_id, client_id]
    connection = get_connection()
    cur = connection.execute(query, args)
    res = cur.fetchall()
    cur.close()
    connection.close()
    return res


def getChatBetweenClients(first_id, second_id):
    connection = get_connection()
    connection.execute("""
CREATE TABLE IF NOT EXISTS chat (
    id INTEGER PRIMARY KEY,
    first_client_id INTEGER NOT NULL,
    second_client_id INTEGER NOT NULL
)""")
    query = """SELECT * FROM chat WHERE (first_client_id = ? AND second_client_id = ?) OR (first_client_id = ? AND second_client_id = ?)"""
    args = [first_id, second_id, second_id, first_id]
    connection = get_connection()
    cur = connection.execute(query, args)
    res = cur.fetchone()
    cur.close()
    connection.close()
    return res


def createChat(first_client_id, second_client_id):
    connection = get_connection()
    connection.execute("""
CREATE TABLE IF NOT EXISTS chat (
    id INTEGER PRIMARY KEY,
    first_client_id INTEGER NOT NULL,
    second_client_id INTEGER NOT NULL
)""")
    query = """INSERT INTO chat (first_client_id, second_client_id) VALUES (?, ?)"""
    args = [first_client_id, second_client_id]
    connection = get_connection()
    cur = connection.execute(query, args)
    connection.commit()
    cur.close()
    connection.close()
    return cur.lastrowid
