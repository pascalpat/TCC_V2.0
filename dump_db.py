import sqlite3

src = "database/TCC.db"
dst = "backup/data_dump.sql"

conn = sqlite3.connect(src)
with open(dst, "w", encoding="utf-8") as f:
    for line in conn.iterdump():
        f.write(f"{line}\n")
conn.close()
print("✅ Dumped DB to", dst)
