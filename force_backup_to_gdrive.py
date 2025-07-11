#!/usr/bin/env python3
"""
Script pentru forțarea backup-ului pe Google Drive
"""

import os
import sqlite3
from datetime import datetime

def force_backup_to_gdrive():
    """Forțează backup-ul pe Google Drive"""
    print("🔄 Forțare backup pe Google Drive...")
    print("=" * 50)
    
    # 1. Verifică starea inițială
    print("1️⃣ Verificare starea inițială:")
    if os.path.exists('finance.db'):
        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tranzactii")
        transaction_count = cursor.fetchone()[0]
        conn.close()
        print(f"   📊 Baza de date are {transaction_count} tranzacții")
    else:
        print("   ❌ Baza de date nu există")
        return
    
    # 2. Forțează backup-ul pe Google Drive
    print("\n2️⃣ Forțare backup pe Google Drive:")
    
    try:
        from auto_backup import get_backup_system
        
        # Obține sistemul de backup
        backup_system = get_backup_system()
        
        # Creează backup-ul cu upload pe Google Drive
        print("   📦 Creare backup cu upload pe Google Drive...")
        backup_filename = backup_system.create_backup(upload_to_gdrive_flag=True)
        
        print(f"   ✅ Backup creat: {backup_filename}")
        
        # Verifică dacă backup-ul a fost încărcat pe Google Drive
        print("   🔍 Verificare backup pe Google Drive...")
        backups = backup_system.get_backup_list()
        
        # Găsește backup-ul tocmai creat
        latest_backup = None
        for backup in backups:
            if backup['filename'] == backup_filename:
                latest_backup = backup
                break
        
        if latest_backup and latest_backup.get('gdrive_id'):
            print(f"   ✅ Backup încărcat pe Google Drive cu ID: {latest_backup['gdrive_id']}")
            print(f"   📊 Backup conține {latest_backup.get('tables', {}).get('tranzactii', 0)} tranzacții")
        else:
            print("   ⚠️ Backup creat local, dar nu s-a încărcat pe Google Drive")
            
    except Exception as e:
        print(f"   ❌ Eroare la backup: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. Rezumat
    print("\n3️⃣ Rezumat:")
    print("   🎯 Backup-ul forțat pe Google Drive complet")
    print("   📊 Verifică dacă backup-ul apare pe Google Drive")
    print("   🔄 Pentru a testa din nou, rulează acest script din nou")

if __name__ == "__main__":
    force_backup_to_gdrive() 