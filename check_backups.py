#!/usr/bin/env python3
"""
Script pentru verificarea backup-urilor disponibile
"""

import os
import sqlite3
from pathlib import Path

def check_all_backups():
    """Verifică toate backup-urile disponibile"""
    backup_dir = Path('backups')
    if not backup_dir.exists():
        print("❌ Nu există directorul backups!")
        return
    
    print("🔍 Verificare backup-uri disponibile...")
    print("=" * 50)
    
    backup_files = list(backup_dir.glob('finance_backup_*.db'))
    if not backup_files:
        print("❌ Nu s-au găsit backup-uri!")
        return
    
    print(f"📦 Găsite {len(backup_files)} backup-uri:")
    print("-" * 50)
    
    backups_with_data = []
    
    for backup_file in backup_files:
        try:
            conn = sqlite3.connect(backup_file)
            cursor = conn.cursor()
            
            # Verifică tranzacții
            tranzactii_count = cursor.execute("SELECT COUNT(*) FROM tranzactii").fetchone()[0]
            
            # Verifică obiecte
            obiecte_count = cursor.execute("SELECT COUNT(*) FROM obiecte").fetchone()[0]
            
            conn.close()
            
            status = "✅" if tranzactii_count > 0 else "❌"
            print(f"{status} {backup_file.name}: {tranzactii_count} tranzacții, {obiecte_count} obiecte")
            
            if tranzactii_count > 0:
                backups_with_data.append((backup_file, tranzactii_count, obiecte_count))
                
        except Exception as e:
            print(f"⚠️ Eroare la verificarea {backup_file.name}: {e}")
    
    print("-" * 50)
    
    if backups_with_data:
        print(f"✅ Găsite {len(backups_with_data)} backup-uri cu date:")
        for backup_file, tranzactii, obiecte in backups_with_data:
            print(f"   📦 {backup_file.name}: {tranzactii} tranzacții, {obiecte} obiecte")
        
        # Recomandă cel mai recent backup cu date
        latest_backup = max(backups_with_data, key=lambda x: x[0].stat().st_mtime)
        print(f"\n💡 Recomandare: {latest_backup[0].name} (cel mai recent cu date)")
        
        return latest_backup[0]
    else:
        print("❌ Nu s-au găsit backup-uri cu date!")
        return None

if __name__ == "__main__":
    check_all_backups() 