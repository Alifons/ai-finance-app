#!/usr/bin/env python3
"""
Repară baza de date coruptă
"""

import sqlite3
import os
import shutil
from datetime import datetime

def check_database():
    """Verifică dacă baza de date este validă"""
    print("🔍 Verific baza de date...")
    
    try:
        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()
        
        # Verifică dacă tabelele există
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"✅ Tabele găsite: {[t[0] for t in tables]}")
        
        # Verifică tranzacțiile
        cursor.execute("SELECT COUNT(*) FROM tranzactii")
        tranzactii_count = cursor.fetchone()[0]
        print(f"📈 Tranzacții: {tranzactii_count}")
        
        # Verifică obiectele
        cursor.execute("SELECT COUNT(*) FROM obiecte")
        obiecte_count = cursor.fetchone()[0]
        print(f"📦 Obiecte: {obiecte_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Baza de date este coruptă: {e}")
        return False

def backup_corrupted_db():
    """Fă backup la baza coruptă"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'corrupted_finance_{timestamp}.db'
    
    try:
        shutil.copy2('finance.db', backup_name)
        print(f"✅ Baza coruptă salvată ca: {backup_name}")
        return backup_name
    except Exception as e:
        print(f"❌ Nu s-a putut face backup la baza coruptă: {e}")
        return None

def create_new_database():
    """Creează o bază de date nouă"""
    print("🔄 Creez bază de date nouă...")
    
    try:
        # Șterge baza coruptă
        if os.path.exists('finance.db'):
            os.remove('finance.db')
            print("✅ Baza coruptă ștearsă")
        
        # Creează baza nouă
        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()
        
        # Creează tabelul tranzactii
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tranzactii (
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
            CREATE TABLE IF NOT EXISTS obiecte (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nume TEXT UNIQUE NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ Bază de date nouă creată!")
        return True
        
    except Exception as e:
        print(f"❌ Eroare la crearea bazei de date: {e}")
        return False

def restore_from_backup():
    """Încearcă să restaureze din cel mai recent backup"""
    print("🔄 Încerc să restaurez din backup...")
    
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        print("❌ Nu există folderul backups")
        return False
    
    # Găsește cel mai recent backup
    backup_files = []
    for file in os.listdir(backup_dir):
        if file.endswith('.db') and file.startswith('finance_backup_'):
            backup_path = os.path.join(backup_dir, file)
            backup_files.append((file, os.path.getctime(backup_path)))
    
    if not backup_files:
        print("❌ Nu există backup-uri")
        return False
    
    # Sortează după data creării (cel mai recent primul)
    backup_files.sort(key=lambda x: x[1], reverse=True)
    latest_backup = backup_files[0][0]
    latest_backup_path = os.path.join(backup_dir, latest_backup)
    
    try:
        # Verifică dacă backup-ul este valid
        conn = sqlite3.connect(latest_backup_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tranzactii")
        tranzactii_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM obiecte")
        obiecte_count = cursor.fetchone()[0]
        conn.close()
        
        print(f"✅ Backup valid găsit: {latest_backup}")
        print(f"   Tranzacții: {tranzactii_count}")
        print(f"   Obiecte: {obiecte_count}")
        
        # Restaurează backup-ul
        shutil.copy2(latest_backup_path, 'finance.db')
        print("✅ Backup restaurat!")
        return True
        
    except Exception as e:
        print(f"❌ Backup-ul nu este valid: {e}")
        return False

def main():
    """Funcția principală"""
    print("🔧 Reparare bază de date")
    print("=" * 40)
    
    # Verifică baza de date
    if check_database():
        print("✅ Baza de date este OK!")
        return
    
    print("❌ Baza de date este coruptă!")
    
    # Fă backup la baza coruptă
    backup_corrupted_db()
    
    # Încearcă să restaureze din backup
    if restore_from_backup():
        print("✅ Baza de date reparată din backup!")
        return
    
    # Creează bază nouă
    print("🔄 Creez bază de date nouă...")
    if create_new_database():
        print("✅ Bază de date nouă creată!")
        print("💡 Va trebui să reintroduci datele manual sau să faci import de pe Render")
    else:
        print("❌ Nu s-a putut crea bază de date nouă!")

if __name__ == "__main__":
    main() 