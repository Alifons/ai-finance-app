#!/usr/bin/env python3
"""
Script pentru sincronizarea tuturor backup-urilor pe Google Drive
Creează folderul dedicat și urcă toate backup-urile existente
"""

from auto_backup import AutoBackup
import os

def main():
    """Sincronizează toate backup-urile pe Google Drive"""
    print("🔄 Sincronizare toate backup-urile pe Google Drive")
    print("="*50)
    
    # Inițializează sistemul de backup
    backup_system = AutoBackup()
    
    print(f"📁 Folder local: {backup_system.backup_dir}")
    print(f"☁️ Folder Google Drive ID: {backup_system.gdrive_folder_id}")
    
    if not backup_system.gdrive_folder_id:
        print("❌ Nu s-a putut crea folderul pe Google Drive")
        return False
    
    # Sincronizează toate backup-urile existente
    print("\n=== Sincronizare backup-uri existente ===")
    success = backup_system.sync_all_backups_to_gdrive()
    
    if success:
        print("\n✅ Sincronizare completă!")
        print("Toate backup-urile sunt acum disponibile pe Google Drive.")
        
        # Afișează statistici
        backups = backup_system.get_backup_list()
        local_count = len(backups)
        gdrive_count = sum(1 for b in backups if b.get('gdrive_id'))
        
        print(f"\n📊 Statistici:")
        print(f"   - Backup-uri locale: {local_count}")
        print(f"   - Backup-uri pe Google Drive: {gdrive_count}")
        print(f"   - Folder Google Drive: 'AI Finance App Backups'")
        
        # Creează un backup nou pentru test
        print(f"\n🔄 Creez backup nou cu sincronizare automată...")
        new_backup = backup_system.create_backup(upload_to_gdrive_flag=True)
        print(f"✅ Backup nou creat: {new_backup}")
        
        return True
    else:
        print("\n❌ Sincronizarea a eșuat!")
        return False

if __name__ == "__main__":
    main() 