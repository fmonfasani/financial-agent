#!/usr/bin/env python3
import os, psycopg2

# Carga variables
from dotenv import load_dotenv
load_dotenv(".env")

conn = psycopg2.connect(os.environ["DATABASE_URL"])
cur  = conn.cursor()

for path in ("sql/create_tables.sql", "sql/functions.sql"):
    print("Ejecutando", path)
    with open(path) as f:
        statements = [s for s in f.read().split(";") if s.strip()]
        for stmt in statements:
            cur.execute(stmt)

conn.commit()
cur.close()
conn.close()
print("✅ Tablas y funciones creadas.")
