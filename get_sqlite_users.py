import sqlite3
import json

conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()
cur.execute("SELECT id, first_name, last_name, phone FROM apps_user")
users = cur.fetchall()
print("SQLite users:", users)
conn.close()
