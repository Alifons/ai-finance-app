#!/usr/bin/env python3
"""
Script pentru forțarea backup-ului pe Google Drive și testarea restaurarei
"""

import os
import sqlite3
from datetime import datetime

def force_gdrive_backup():
    """Forțează backup-ul pe Google Drive"""
    print("🔄 Forțare backup pe Google Drive...")
    print("=" * 50)
    
    try:
        from auto_backup import get_backup_system
        
        # Verifică dacă există date în baza de date
        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()
        tranzactii_count = cursor.execute("SELECT COUNT(*) FROM tranzactii").fetchone()[0]
        obiecte_count = cursor.execute("SELECT COUNT(*) FROM obiecte").fetchone()[0]
        conn.close()
        
        print(f"📊 Date în baza de date: {tranzactii_count} tranzacții, {obiecte_count} obiecte")
        
        if tranzactii_count == 0:
            print("❌ Nu există date de backup!")
            return False
        
        # Creează backup-ul
        backup_system = get_backup_system()
        backup_filename = backup_system.create_backup(upload_to_gdrive_flag=True)
        
        print(f"✅ Backup creat: {backup_filename}")
        
        # Verifică dacă backup-ul a fost urcat pe Google Drive
        backups = backup_system.get_backup_list()
        latest_backup = None
        
        for backup in backups:
            if backup.get('gdrive_id'):
                latest_backup = backup
                break
        
        if latest_backup:
            print(f"✅ Backup urcat pe Google Drive cu ID: {latest_backup['gdrive_id']}")
            print(f"📦 Nume fișier: {latest_backup['filename']}")
            print(f"📅 Data: {latest_backup.get('created_at', 'N/A')}")
            return True
        else:
            print("❌ Backup-ul nu a fost urcat pe Google Drive")
            return False
            
    except Exception as e:
        print(f"❌ Eroare la backup: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gdrive_restore():
    """Testează restaurarea din Google Drive"""
    print("\n🔄 Testare restaurare din Google Drive...")
    print("=" * 50)
    
    try:
        # Simulează mediul Render
        os.environ['RENDER'] = 'true'
        
        # Importează funcția de restaurare
        from app import restore_from_google_drive
        
        # Testează restaurarea
        success, message = restore_from_google_drive()
        
        if success:
            print(f"✅ Restaurare reușită: {message}")
            
            # Verifică datele restaurate
            conn = sqlite3.connect('finance.db')
            cursor = conn.cursor()
            tranzactii_count = cursor.execute("SELECT COUNT(*) FROM tranzactii").fetchone()[0]
            obiecte_count = cursor.execute("SELECT COUNT(*) FROM obiecte").fetchone()[0]
            conn.close()
            
            print(f"📊 Date restaurate: {tranzactii_count} tranzacții, {obiecte_count} obiecte")
            return True
        else:
            print(f"❌ Restaurare eșuată: {message}")
            return False
            
    except Exception as e:
        print(f"❌ Eroare la testarea restaurarei: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Funcția principală"""
    print("🧪 TEST BACKUP ȘI RESTAURARE GOOGLE DRIVE")
    print("=" * 60)
    
    # Forțează backup-ul
    backup_success = force_gdrive_backup()
    
    if backup_success:
        print("\n✅ Backup pe Google Drive reușit!")
        
        # Testează restaurarea
        restore_success = test_gdrive_restore()
        
        if restore_success:
            print("\n🎉 TEST COMPLET REUȘIT!")
            print("✅ Backup pe Google Drive funcționează")
            print("✅ Restaurare din Google Drive funcționează")
            print("✅ Render va putea restaura datele la restart")
        else:
            print("\n⚠️ Backup reușit, dar restaurarea a eșuat")
            print("💡 Verifică configurația Google Drive")
    else:
        print("\n❌ Backup pe Google Drive a eșuat")
        print("💡 Verifică configurația Google Drive")

if __name__ == "__main__":
    main() 