#!/usr/bin/env python3
"""
Script pentru restaurarea automată a datelor din backup-uri
"""

import os
import sqlite3
import shutil
import json
from datetime import datetime
from pathlib import Path

def get_latest_backup():
    """Găsește cel mai recent backup"""
    backup_dir = Path('backups')
    if not backup_dir.exists():
        return None
    
    backup_files = []
    for file in backup_dir.glob('finance_backup_*.db'):
        backup_files.append((file, file.stat().st_mtime))
    
    if not backup_files:
        return None
    
    # Sortează după data modificării (cel mai recent primul)
    backup_files.sort(key=lambda x: x[1], reverse=True)
    return backup_files[0][0]

def check_database_has_data():
    """Verifică dacă baza de date are date"""
    try:
        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tranzactii")
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    except Exception as e:
        print(f"⚠️ Eroare la verificarea bazei de date: {e}")
        return False

def restore_from_backup(backup_path):
    """Restaurează datele din backup"""
    try:
        # Creează backup al bazei curente înainte de restaurare
        if os.path.exists('finance.db'):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safety_backup = f'finance_safety_backup_{timestamp}.db'
            shutil.copy2('finance.db', safety_backup)
            print(f"✅ Backup de siguranță creat: {safety_backup}")
        
        # Restaurează din backup
        shutil.copy2(backup_path, 'finance.db')
        print(f"✅ Date restaurate din: {backup_path.name}")
        
        # Verifică restaurarea
        if check_database_has_data():
            print("✅ Restaurarea a fost reușită!")
            return True
        else:
            print("❌ Restaurarea a eșuat - baza de date este goală")
            return False
            
    except Exception as e:
        print(f"❌ Eroare la restaurare: {e}")
        return False

def main():
    """Funcția principală"""
    print("🔄 Verificare și restaurare date...")
    print("=" * 50)
    
    # Verifică dacă baza de date are date
    if check_database_has_data():
        print("✅ Baza de date are date - nu este necesară restaurarea")
        return
    
    print("⚠️ Baza de date este goală - căutare backup...")
    
    # Găsește cel mai recent backup
    latest_backup = get_latest_backup()
    if not latest_backup:
        print("❌ Nu s-au găsit backup-uri!")
        return
    
    print(f"📦 Backup găsit: {latest_backup.name}")
    print(f"📅 Data: {datetime.fromtimestamp(latest_backup.stat().st_mtime)}")
    
    # Restaurează datele
    if restore_from_backup(latest_backup):
        print("🎉 Datele au fost restaurate cu succes!")
        
        # Afișează informații despre datele restaurate
        try:
            conn = sqlite3.connect('finance.db')
            cursor = conn.cursor()
            
            tranzactii_count = cursor.execute("SELECT COUNT(*) FROM tranzactii").fetchone()[0]
            obiecte_count = cursor.execute("SELECT COUNT(*) FROM obiecte").fetchone()[0]
            
            print(f"📊 Tranzacții restaurate: {tranzactii_count}")
            print(f"📊 Obiecte restaurate: {obiecte_count}")
            
            conn.close()
        except Exception as e:
            print(f"⚠️ Eroare la afișarea statisticilor: {e}")
    else:
        print("❌ Restaurarea a eșuat!")

if __name__ == "__main__":
    main() 