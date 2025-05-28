export $(grep -v '^#' .env | xargs)

python3 <<'PYCODE'
import os, psycopg2

# Conexión
url  = os.environ["DATABASE_URL"]
conn = psycopg2.connect(url)
cur  = conn.cursor()

# Para cada uno de tus scripts SQL
for path in ("sql/create_tables.sql", "sql/functions.sql"):
    sql = open(path).read()
    # Partimos por ';' y ejecutamos sólo si no está en blanco
    for stmt in sql.split(";"):
        if stmt.strip():
            cur.execute(stmt)

conn.commit()
cur.close()
conn.close()
print("✅ Tablas y funciones creadas exitosamente.")
PYCODE
