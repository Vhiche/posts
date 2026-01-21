import sqlite3
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = '\\sqlite.db'
DATABASE = ROOT + DB

def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = dict_factory
    return connection


# @app.teardown_appcontext
# def close_connection(exception):
#     db = getattr(g, '_database', None)
#     if db is not None:
#         db.close()
#
#
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def query_db(query, args=(), one=False):
    cur = get_connection().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv