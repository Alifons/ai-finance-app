#!/usr/bin/env python3
"""
Debug sistem backup
"""

import os
import sys
from pathlib import Path

def test_backup_system():
    """Testează sistemul de backup"""
    print("🔍 Debug sistem backup")
    print("=" * 40)
    
    # Verifică dacă există fișierele necesare
    print("📁 Verific fișierele:")
    files_to_check = [
        'app.py',
        'auto_backup.py',
        'finance.db',
        'backups'
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✅ {file} - există")
        else:
            print(f"❌ {file} - NU există")
    
    # Verifică folderul backups
    backup_dir = Path('backups')
    if backup_dir.exists():
        print(f"✅ Folder backups există: {backup_dir}")
        backup_files = list(backup_dir.glob('*'))
        print(f"   Fișiere în backups: {len(backup_files)}")
        for f in backup_files[:5]:  # Primele 5
            print(f"   - {f.name}")
    else:
        print("❌ Folder backups NU există")
        try:
            backup_dir.mkdir()
            print("✅ Folder backups creat")
        except Exception as e:
            print(f"❌ Nu s-a putut crea folder backups: {e}")
    
    # Testează importul auto_backup
    print("\n📦 Test import auto_backup:")
    try:
        from auto_backup import get_backup_system
        print("✅ Import auto_backup reușit")
        
        # Testează inițializarea sistemului
        try:
            backup_system = get_backup_system()
            print("✅ Sistem backup inițializat")
            
            # Testează crearea unui backup
            try:
                print("🔄 Testez crearea unui backup...")
                backup_filename = backup_system.create_backup(upload_to_gdrive_flag=False)
                print(f"✅ Backup creat: {backup_filename}")
            except Exception as e:
                print(f"❌ Eroare la crearea backup-ului: {e}")
                
        except Exception as e:
            print(f"❌ Eroare la inițializarea sistemului: {e}")
            
    except Exception as e:
        print(f"❌ Eroare la import auto_backup: {e}")
    
    # Verifică permisiuni
    print("\n🔐 Verific permisiuni:")
    try:
        test_file = Path('test_write.txt')
        test_file.write_text('test')
        test_file.unlink()
        print("✅ Permisiuni de scriere OK")
    except Exception as e:
        print(f"❌ Probleme cu permisiunile: {e}")

if __name__ == "__main__":
    test_backup_system() 