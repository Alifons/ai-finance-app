#!/usr/bin/env python3
"""
Importă datele de pe Render și le scrie local (suprascrie tot)
"""

import requests
import sqlite3

def fetch_render_data():
    url = "https://ai-finance-app.onrender.com/api/export"
    try:
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            print("✅ Datele au fost descărcate de pe Render!")
            return r.json()
        else:
            print(f"❌ Eroare la descărcare: {r.status_code}")
            return None
    except Exception as e:
        print(f"❌ Eroare la conectare: {e}")
        return None

def import_local(data):
    try:
        conn = sqlite3.connect('finance.db')
        c = conn.cursor()
        # Șterge tot
        c.execute('DELETE FROM tranzactii')
        c.execute('DELETE FROM obiecte')
        # Reimportă obiecte
        obiecte = data.get('obiecte', [])
        for obj in obiecte:
            # obj[1] = nume
            c.execute('INSERT INTO obiecte (id, nume) VALUES (?, ?)', (obj[0], obj[1]))
        # Reimportă tranzacții
        tranzactii = data.get('tranzactii', [])
        for tr in tranzactii:
            c.execute('''INSERT INTO tranzactii (id, data, suma, comentariu, operator, tip, obiect, persoana, categorie)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', tr)
        conn.commit()
        conn.close()
        print(f"✅ Datele au fost importate local! Obiecte: {len(obiecte)}, Tranzacții: {len(tranzactii)}")
    except Exception as e:
        print(f"❌ Eroare la import local: {e}")

def main():
    print("🔄 Import date de pe Render în local...")
    data = fetch_render_data()
    if not data:
        print("❌ Nu s-au putut descărca datele de pe Render!")
        return
    import_local(data)
    print("🎉 Gata! Datele locale sunt identice cu cele de pe Render.")

if __name__ == "__main__":
    main() 