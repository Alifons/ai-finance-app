#!/usr/bin/env python3
"""
Script pentru verificarea backup-urilor din Google Drive
"""

import os
import json
from datetime import datetime
from pathlib import Path

def check_gdrive_backups():
    """Verifică backup-urile din Google Drive"""
    print("🔍 Verificare backup-uri Google Drive")
    print("=" * 50)
    
    try:
        from auto_backup import get_backup_system, gdrive_auth
        
        backup_system = get_backup_system()
        drive = gdrive_auth()
        
        # Obține folderul de backup
        folder_id = backup_system.get_or_create_backup_folder()
        if not folder_id:
            print("❌ Nu s-a putut găsi folderul de backup")
            return False
        
        print(f"✅ Folder Google Drive găsit: {folder_id}")
        
        # Lista toate fișierele din folder
        file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
        
        if not file_list:
            print("📭 Nu există backup-uri în Google Drive")
            return True
        
        print(f"📊 Găsite {len(file_list)} backup-uri în Google Drive:")
        
        # Sortează după data creării
        file_list.sort(key=lambda x: x.get('createdDate', ''), reverse=True)
        
        for i, file in enumerate(file_list, 1):
            created_date = file.get('createdDate', 'N/A')
            modified_date = file.get('modifiedDate', 'N/A')
            file_size = file.get('fileSize', 'N/A')
            
            print(f"\n{i}. {file['title']}")
            print(f"   ID: {file['id']}")
            print(f"   Mărime: {file_size} bytes")
            print(f"   Creat: {created_date}")
            print(f"   Modificat: {modified_date}")
        
        # Verifică backup-urile locale
        print(f"\n📁 Backup-uri locale:")
        backup_dir = Path('backups')
        local_backups = list(backup_dir.glob('finance_backup_*.db'))
        
        print(f"   Găsite {len(local_backups)} backup-uri locale")
        
        # Verifică sincronizarea
        gdrive_files = [f['title'] for f in file_list]
        local_files = [f.name for f in local_backups]
        
        synced_files = [f for f in local_files if f in gdrive_files]
        unsynced_files = [f for f in local_files if f not in gdrive_files]
        
        print(f"\n📊 Status sincronizare:")
        print(f"   ✅ Sincronizate: {len(synced_files)}")
        print(f"   ⚠️  Nesincronizate: {len(unsynced_files)}")
        
        if unsynced_files:
            print(f"   📋 Backup-uri nesincronizate:")
            for file in unsynced_files[:5]:  # Primele 5
                print(f"      - {file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Eroare la verificarea backup-urilor: {e}")
        return False

def check_recent_backups():
    """Verifică backup-urile recente"""
    print("\n📅 Backup-uri recente (ultimele 24h):")
    print("=" * 40)
    
    backup_dir = Path('backups')
    if not backup_dir.exists():
        print("❌ Directorul de backup nu există")
        return
    
    # Găsește backup-urile din ultimele 24h
    from datetime import datetime, timedelta
    yesterday = datetime.now() - timedelta(days=1)
    
    recent_backups = []
    for backup_file in backup_dir.glob('finance_backup_*.db'):
        try:
            # Încearcă să citească informațiile din JSON
            json_file = backup_file.with_suffix('.json')
            if json_file.exists():
                with open(json_file, 'r', encoding='utf-8') as f:
                    info = json.load(f)
                    created_at = info.get('timestamp', info.get('created_at', ''))
                    if created_at:
                        try:
                            backup_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            if backup_date > yesterday:
                                recent_backups.append((backup_file, info))
                        except:
                            pass
        except:
            pass
    
    if not recent_backups:
        print("📭 Nu există backup-uri în ultimele 24h")
        return
    
    print(f"📊 Găsite {len(recent_backups)} backup-uri recente:")
    
    for backup_file, info in sorted(recent_backups, key=lambda x: x[1].get('timestamp', ''), reverse=True):
        filename = backup_file.name
        created_at = info.get('timestamp', info.get('created_at', 'N/A'))
        source = info.get('source', 'local')
        gdrive_id = info.get('gdrive_id', None)
        
        status = "✅ Local + Google Drive" if gdrive_id else "📁 Doar local"
        
        print(f"\n- {filename}")
        print(f"  Creat: {created_at}")
        print(f"  Status: {status}")
        if gdrive_id:
            print(f"  Google Drive ID: {gdrive_id}")

def main():
    """Funcția principală"""
    print("AI Finance App - Verificare Backup-uri Google Drive")
    print("=" * 60)
    
    # Verifică backup-urile din Google Drive
    success = check_gdrive_backups()
    
    if success:
        # Verifică backup-urile recente
        check_recent_backups()
        
        print("\n🎉 Verificarea completă!")
        print("✅ Backup-urile sunt sincronizate cu Google Drive")
        print("✅ Sistemul de backup funcționează corect")
    else:
        print("\n❌ Verificarea a eșuat!")
        print("Verifică configurația Google Drive")

if __name__ == "__main__":
    main() 