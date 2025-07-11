#!/usr/bin/env python3
"""
Script pentru crearea unui backup de test în Google Drive
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path

def create_test_backup():
    """Creează un backup de test în Google Drive"""
    print("🧪 Creare backup de test în Google Drive")
    print("=" * 50)
    
    try:
        # Importă sistemul de backup
        from auto_backup import get_backup_system, gdrive_auth
        
        print("✅ Modulele Google Drive sunt disponibile")
        
        # Inițializează sistemul de backup
        backup_system = get_backup_system()
        print("✅ Sistemul de backup inițializat")
        
        # Testează autentificarea
        print("🔐 Testez autentificarea Google Drive...")
        drive = gdrive_auth()
        print("✅ Autentificarea Google Drive funcționează")
        
        # Creează folderul de backup (dacă nu există)
        print("📁 Creez/verific folderul de backup...")
        folder_id = backup_system.get_or_create_backup_folder()
        
        if folder_id:
            print(f"✅ Folder Google Drive găsit/creat: {folder_id}")
        else:
            print("❌ Nu s-a putut crea/găsi folderul pe Google Drive")
            return False
        
        # Creează un backup de test
        print("📦 Creez backup de test...")
        test_backup_filename = backup_system.create_backup(upload_to_gdrive_flag=True)
        
        print(f"✅ Backup de test creat: {test_backup_filename}")
        
        # Verifică dacă backup-ul există local
        backup_path = backup_system.backup_dir / test_backup_filename
        if backup_path.exists():
            print(f"✅ Backup-ul există local: {backup_path}")
            print(f"   Mărime: {os.path.getsize(backup_path)} bytes")
        else:
            print("❌ Backup-ul nu există local")
            return False
        
        # Verifică dacă backup-ul există pe Google Drive
        print("🔍 Verific dacă backup-ul există pe Google Drive...")
        
        # Lista fișierele din folderul de backup
        file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
        
        print(f"📊 Fișiere găsite în folder: {len(file_list)}")
        
        # Caută backup-ul de test
        test_backup_found = False
        for file in file_list:
            print(f"   - {file['title']} (ID: {file['id']})")
            if test_backup_filename in file['title']:
                test_backup_found = True
                print(f"✅ Backup-ul de test găsit pe Google Drive!")
                print(f"   ID: {file['id']}")
                print(f"   Mărime: {file['fileSize']} bytes")
                print(f"   Data creării: {file['createdDate']}")
        
        if not test_backup_found:
            print("❌ Backup-ul de test nu a fost găsit pe Google Drive")
            return False
        
        # Testează descărcarea backup-ului
        print("⬇️ Testez descărcarea backup-ului...")
        test_download_path = backup_system.backup_dir / f"test_download_{test_backup_filename}"
        
        # Găsește fișierul de test
        test_file = None
        for file in file_list:
            if test_backup_filename in file['title']:
                test_file = file
                break
        
        if test_file:
            # Descarcă fișierul
            test_file.GetContentFile(str(test_download_path))
            print(f"✅ Backup descărcat cu succes: {test_download_path}")
            
            # Compară mărimea fișierelor
            original_size = os.path.getsize(backup_path)
            downloaded_size = os.path.getsize(test_download_path)
            
            if original_size == downloaded_size:
                print(f"✅ Mărimea fișierelor este identică: {original_size} bytes")
            else:
                print(f"⚠️ Mărimea fișierelor diferă: {original_size} vs {downloaded_size}")
            
            # Șterge fișierul de test descărcat
            test_download_path.unlink()
            print("🧹 Fișierul de test descărcat a fost șters")
        
        print("\n🎉 Testul de backup Google Drive a trecut cu succes!")
        print("✅ Backup-ul de test a fost creat și verificat")
        print("✅ Sistemul de backup Google Drive funcționează corect")
        
        return True
        
    except ImportError as e:
        print(f"❌ Eroare la importul modulelor: {e}")
        print("   Rulează: pip install PyDrive2")
        return False
    except Exception as e:
        print(f"❌ Eroare la testarea backup-ului: {e}")
        return False

def list_gdrive_backups():
    """Listează toate backup-urile din Google Drive"""
    print("\n📋 Lista backup-urilor din Google Drive")
    print("=" * 40)
    
    try:
        from auto_backup import get_backup_system, gdrive_auth
        
        backup_system = get_backup_system()
        drive = gdrive_auth()
        
        folder_id = backup_system.get_or_create_backup_folder()
        if not folder_id:
            print("❌ Nu s-a putut găsi folderul de backup")
            return
        
        # Lista toate fișierele din folder
        file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
        
        if not file_list:
            print("📭 Nu există backup-uri în Google Drive")
            return
        
        print(f"📊 Găsite {len(file_list)} backup-uri în Google Drive:")
        
        for i, file in enumerate(file_list, 1):
            print(f"\n{i}. {file['title']}")
            print(f"   ID: {file['id']}")
            print(f"   Mărime: {file.get('fileSize', 'N/A')} bytes")
            print(f"   Creat: {file.get('createdDate', 'N/A')}")
            print(f"   Modificat: {file.get('modifiedDate', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Eroare la listarea backup-urilor: {e}")

def main():
    """Funcția principală"""
    print("AI Finance App - Test Backup Google Drive")
    print("=" * 50)
    
    # Creează backup de test
    success = create_test_backup()
    
    if success:
        # Listează toate backup-urile
        list_gdrive_backups()
        
        print("\n🎉 Testul complet a trecut cu succes!")
        print("✅ Backup-ul de test a fost creat în Google Drive")
        print("✅ Poți verifica în browser la: https://drive.google.com")
        print("✅ Caută folderul 'AI Finance App Backups'")
    else:
        print("\n❌ Testul a eșuat!")
        print("Verifică:")
        print("   - Conexiunea la internet")
        print("   - Credențialele Google Drive")
        print("   - Modulele instalate (pip install PyDrive2)")

if __name__ == "__main__":
    main() 