#!/usr/bin/env python3
"""
Creează o bază de date nouă
"""

import sqlite3
import os

def create_new_database():
    """Creează o bază de date nouă"""
    print("🔄 Creez bază de date nouă...")
    
    # Șterge fișierul dacă există
    if os.path.exists('finance.db'):
        try:
            os.remove('finance.db')
            print("✅ Fișierul vechi ștears")
        except Exception as e:
            print(f"❌ Nu s-a putut șterge: {e}")
            return False
    
    try:
        # Creează baza nouă
        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()
        
        # Creează tabelul tranzactii
        cursor.execute('''
            CREATE TABLE tranzactii (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                suma REAL NOT NULL,
                comentariu TEXT NOT NULL,
                operator TEXT NOT NULL,
                tip TEXT NOT NULL,
                obiect TEXT NOT NULL,
                persoana TEXT NOT NULL,
                categorie TEXT NOT NULL
            )
        ''')
        
        # Creează tabelul obiecte
        cursor.execute('''
            CREATE TABLE obiecte (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nume TEXT UNIQUE NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ Bază de date nouă creată cu succes!")
        return True
        
    except Exception as e:
        print(f"❌ Eroare la crearea bazei de date: {e}")
        return False

if __name__ == "__main__":
    create_new_database() 