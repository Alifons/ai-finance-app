import sqlite3

# Conectare la baza de date
conn = sqlite3.connect('finance.db')
cursor = conn.cursor()

# Afișează tabelele
print("=== TABELE ÎN BAZA DE DATE ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(f"- {table[0]}")

print("\n=== STRUCTURA TABELULUI TRANZACTII ===")
cursor.execute("PRAGMA table_info(tranzactii)")
columns = cursor.fetchall()
for col in columns:
    print(f"- {col[1]} ({col[2]})")

print("\n=== ULTIMELE 5 TRANZACTII ===")
cursor.execute("SELECT * FROM tranzactii ORDER BY id DESC LIMIT 5")
transactions = cursor.fetchall()
for trans in transactions:
    print(f"ID: {trans[0]}, Data: {trans[1]}, Suma: {trans[2]}, Comentariu: {trans[3]}, Operator: {trans[4]}")

print("\n=== STATISTICI ===")
cursor.execute("SELECT COUNT(*) FROM tranzactii")
total = cursor.fetchone()[0]
print(f"Total tranzacții: {total}")

cursor.execute("SELECT operator, COUNT(*) FROM tranzactii GROUP BY operator")
operators = cursor.fetchall()
for op in operators:
    print(f"{op[0]}: {op[1]} tranzacții")

conn.close() 