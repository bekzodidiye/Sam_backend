import sqlite3
conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()
cur.execute("SELECT count(*) FROM apps_user")
print("SQLite users:", cur.fetchone()[0])
conn.close()
