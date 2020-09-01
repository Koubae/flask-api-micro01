from flask import g
import sqlite3
import os


app_db = 'user.db'
basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), app_db)

def connect_db():
    sql = sqlite3.connect(basedir)
    sql.row_factory = sqlite3.Row
    return sql

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


    