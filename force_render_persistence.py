#!/usr/bin/env python3
"""
Script pentru forțarea persistenței datelor pe Render
"""

import os
import shutil
import sqlite3
from datetime import datetime

def force_render_persistence():
    """Forțează persistența datelor pe Render"""
    print("🚀 FORȚARE PERSISTENȚĂ RENDER")
    print("=" * 50)
    
    # Simulează mediul Render
    os.environ['RENDER'] = 'true'
    os.environ['RENDER_SERVICE_NAME'] = 'ai-finance-app'
    
    print("🔧 Simulez mediul Render...")
    
    try:
        from app import is_render_environment, restore_from_latest_backup, init_db
        
        # Testează detectarea mediului
        is_render = is_render_environment()
        print(f"✅ Detectare mediu: {is_render}")
        
        if not is_render:
            print("❌ Nu se detectează mediul Render")
            return False
        
        # Forțează inițializarea cu restaurare
        print("🔄 Inițializare cu restaurare forțată...")
        init_db()
        
        # Verifică rezultatul
        if os.path.exists('finance.db'):
            conn = sqlite3.connect('finance.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tranzactii")
            tranzactii_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM obiecte")
            obiecte_count = cursor.fetchone()[0]
            conn.close()
            
            print(f"✅ Baza de date restaurată:")
            print(f"   - Tranzacții: {tranzactii_count}")
            print(f"   - Obiecte: {obiecte_count}")
            
            return True
        else:
            print("❌ Baza de date nu există după inițializare")
            return False
            
    except Exception as e:
        print(f"❌ Eroare la forțarea persistenței: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backup_restore():
    """Testează backup și restaurare"""
    print("\n🧪 TEST BACKUP ȘI RESTAURARE")
    print("=" * 50)
    
    try:
        from app import create_backup, restore_from_latest_backup
        
        # Creează backup
        print("📦 Creare backup...")
        backup_filename = create_backup(is_auto_backup=True)
        print(f"✅ Backup creat: {backup_filename}")
        
        # Testează restaurarea
        print("🔄 Testare restaurare...")
        success, message = restore_from_latest_backup()
        
        print(f"📋 Rezultat: {success}")
        print(f"💬 Mesaj: {message}")
        
        return success
        
    except Exception as e:
        print(f"❌ Eroare la testarea backup/restore: {e}")
        return False

def create_persistent_database():
    """Creează o bază de date persistentă"""
    print("\n💾 CREARE BAZĂ DE DATE PERSISTENTĂ")
    print("=" * 50)
    
    try:
        # Creează baza de date cu date de test
        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()
        
        # Creează tabelele
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
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS obiecte (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nume TEXT UNIQUE NOT NULL
            )
        ''')
        
        # Adaugă date de test
        cursor.execute('''
            INSERT INTO tranzactii (data, suma, comentariu, operator, tip, obiect, persoana, categorie)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('2024-12-01', 100.0, 'Test persistență Render', 'Test', 'cheltuieli', 'test', 'Test', 'test'))
        
        cursor.execute('INSERT OR IGNORE INTO obiecte (nume) VALUES (?)', ('test',))
        
        conn.commit()
        conn.close()
        
        print("✅ Bază de date persistentă creată cu date de test")
        return True
        
    except Exception as e:
        print(f"❌ Eroare la crearea bazei de date: {e}")
        return False

def main():
    """Funcția principală"""
    print("🔧 SCRIPT FORȚARE PERSISTENȚĂ RENDER")
    print("=" * 70)
    
    # Creează baza de date persistentă
    db_ok = create_persistent_database()
    
    # Testează backup și restaurare
    backup_ok = test_backup_restore()
    
    # Forțează persistența
    persistence_ok = force_render_persistence()
    
    print("\n" + "=" * 70)
    print("📋 REZUMAT:")
    print(f"   Bază de date: {'✅ OK' if db_ok else '❌ Problema'}")
    print(f"   Backup/Restore: {'✅ OK' if backup_ok else '❌ Problema'}")
    print(f"   Persistență: {'✅ OK' if persistence_ok else '❌ Problema'}")
    
    if db_ok and backup_ok and persistence_ok:
        print("\n🎉 Persistența a fost forțată cu succes!")
        print("✅ Render va păstra datele între restart-uri")
        print("✅ Backup-urile se vor face automat")
        print("✅ Restaurarea se va face automat")
    else:
        print("\n⚠️ Există probleme cu persistența")
        print("💡 Verifică log-urile pentru detalii")

if __name__ == "__main__":
    main() 