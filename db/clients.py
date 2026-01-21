from db.config import get_connection, query_db


def createTable():
    connection = get_connection()
    connection.execute("""
CREATE TABLE IF NOT EXISTS client (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    about TEXT NOT NULL,
    username TEXT NOT NULL
)
""")


def getAllUsers():
    cur = get_connection().execute("SELECT * FROM client")
    res = cur.fetchall()
    cur.close()
    return res


def getUserById(id):
    connection = get_connection()
    query = "SELECT * FROM client WHERE id = (?)"
    args = (id,)
    cur = connection.execute(query, args)
    res = cur.fetchone()
    cur.close()
    return res


def getUserByEmail(email):
    connection = get_connection()
    query = """SELECT * FROM client WHERE email = (?)"""
    args = (email,)
    cur = connection.execute(query, args)
    res = cur.fetchone()
    cur.close()
    return res


def getUserByUsername(username):
    connection = get_connection()
    query = """SELECT * FROM client WHERE username = (?)"""
    args = (username,)
    cur = connection.execute(query, args)
    res = cur.fetchone()
    cur.close()
    return res


def createUser(email, password, username):
    connection = get_connection()
    query = """INSERT INTO client (email, password, about, username) VALUES (?, ?, ?, ?)"""
    args = (email, password, "", username)
    cur = connection.execute(query, args)
    connection.commit()
    cur.close()


def editUser(id, new_email, new_username, new_about):
    connection = get_connection()
    query = "UPDATE client SET email = (?), username = (?), about = (?) WHERE id = (?)"
    args = (new_email, new_username, new_about, id)
    cur = connection.execute(query, args)
    connection.commit()
    cur.close()