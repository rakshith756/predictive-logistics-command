import sqlite3
from contextlib import contextmanager
from config import DATABASE_PATH
@contextmanager
def get_db():
    con=sqlite3.connect(DATABASE_PATH); con.row_factory=sqlite3.Row; con.execute('PRAGMA foreign_keys=ON')
    try: yield con
    finally: con.close()
def rows(sql,args=()):
    with get_db() as c: return [dict(r) for r in c.execute(sql,args).fetchall()]
def row(sql,args=()):
    with get_db() as c:
        r=c.execute(sql,args).fetchone(); return dict(r) if r else None
