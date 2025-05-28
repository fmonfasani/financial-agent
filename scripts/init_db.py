#!/usr/bin/env python3
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(".env")

DATABASE_URL = os.environ["DATABASE_URL"]

def run_script(cur, path):
    with open(path, 'r') as f:
        cur.execute(f.read())

def main():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()

    # primero las tablas
    run_script(cur, "sql/create_tables.sql")
    # luego las funciones corregidas
    run_script(cur, "sql/functions.sql")

    cur.close()
    conn.close()
    print("✅ Tablas y funciones creadas o actualizadas correctamente")

if __name__ == "__main__":
    main()
