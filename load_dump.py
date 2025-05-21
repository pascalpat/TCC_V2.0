# load_dump.py
import sqlite3

DB = "database/TCC.db"
DUMP = "backup/data_dump.sql"

conn = sqlite3.connect(DB)
c = conn.cursor()

# 1) Drop Alembic’s version table so the dump can recreate it cleanly
c.execute("DROP TABLE IF EXISTS alembic_version;")
conn.commit()

# 2) Read & execute the full dump
with open(DUMP, "r", encoding="utf-8") as f:
    sql = f.read()
conn.executescript(sql)

conn.close()
print("✅ Data reloaded (including alembic_version).")
