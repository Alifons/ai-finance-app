#!/usr/bin/env python3
"""
Script pentru testarea și configurarea backup-ului pe Google Drive
"""

import os
import sys
from pathlib import Path

def test_gdrive_setup():
    """Testează configurarea Google Drive"""
    print("🔧 Testare configurare Google Drive")
    print("=" * 40)
    
    try:
        # Verifică dacă fișierul de credențiale există
        token_file = Path("gdrive_token.json")
        if token_file.exists():
            print("✅ Fișierul de credențiale Google Drive există")
        else:
            print("⚠️ Fișierul de credențiale Google Drive nu există")
            print("   Prima dată când rulezi backup-ul, se va deschide browserul pentru autentificare")
        
        # Testează import-ul modulelor
        try:
            from auto_backup import get_backup_system, gdrive_auth
            print("✅ Modulele Google Drive sunt disponibile")
        except ImportError as e:
            print(f"❌ Eroare la importul modulelor: {e}")
            print("   Rulează: pip install PyDrive2")
            return False
        
        # Testează autentificarea
        try:
            print("🔄 Testez autentificarea Google Drive...")
            drive = gdrive_auth()
            print("✅ Autentificarea Google Drive funcționează")
        except Exception as e:
            print(f"❌ Eroare la autentificare: {e}")
            return False
        
        # Testează sistemul de backup
        try:
            backup_system = get_backup_system()
            print("✅ Sistemul de backup este configurat")
            
            # Testează crearea folderului
            folder_id = backup_system.get_or_create_backup_folder()
            if folder_id:
                print(f"✅ Folder Google Drive: {folder_id}")
            else:
                print("❌ Nu s-a putut crea folderul pe Google Drive")
                return False
                
        except Exception as e:
            print(f"❌ Eroare la sistemul de backup: {e}")
            return False
        
        print("\n✅ Configurarea Google Drive este completă!")
        return True
        
    except Exception as e:
        print(f"❌ Eroare generală: {e}")
        return False

def test_backup_creation():
    """Testează crearea unui backup"""
    print("\n🔄 Testare creare backup")
    print("=" * 30)
    
    try:
        from auto_backup import get_backup_system
        
        backup_system = get_backup_system()
        
        # Creează un backup de test
        print("📦 Creez backup de test...")
        backup_filename = backup_system.create_backup(upload_to_gdrive_flag=True)
        
        print(f"✅ Backup creat: {backup_filename}")
        
        # Verifică dacă backup-ul există local
        backup_path = backup_system.backup_dir / backup_filename
        if backup_path.exists():
            print("✅ Backup-ul există local")
        else:
            print("❌ Backup-ul nu există local")
            return False
        
        # Verifică dacă backup-ul există pe Google Drive
        backups = backup_system.get_backup_list()
        gdrive_backups = [b for b in backups if b.get('gdrive_id')]
        
        if gdrive_backups:
            print(f"✅ Backup-ul există pe Google Drive (ID: {gdrive_backups[0]['gdrive_id']})")
        else:
            print("⚠️ Backup-ul nu există pe Google Drive")
        
        return True
        
    except Exception as e:
        print(f"❌ Eroare la crearea backup-ului: {e}")
        return False

def test_restore():
    """Testează restaurarea unui backup"""
    print("\n🔄 Testare restaurare backup")
    print("=" * 30)
    
    try:
        from auto_backup import get_backup_system
        
        backup_system = get_backup_system()
        backups = backup_system.get_backup_list()
        
        if not backups:
            print("❌ Nu există backup-uri pentru testare")
            return False
        
        # Alege primul backup
        test_backup = backups[0]
        print(f"📦 Testez restaurarea din: {test_backup['filename']}")
        
        # Creează backup al bazei curente înainte de test
        current_backup = backup_system.create_backup()
        print(f"💾 Backup curent salvat: {current_backup}")
        
        # Testează restaurarea
        success, message = backup_system.restore_backup(test_backup['filename'])
        
        if success:
            print(f"✅ Restaurare reușită: {message}")
        else:
            print(f"❌ Restaurare eșuată: {message}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Eroare la testarea restaurarei: {e}")
        return False

def main():
    """Funcția principală"""
    print("AI Finance App - Test Google Drive Backup")
    print("=" * 50)
    
    # Testează configurarea
    if not test_gdrive_setup():
        print("\n❌ Configurarea Google Drive a eșuat!")
        print("Verifică:")
        print("   - Conexiunea la internet")
        print("   - Credențialele Google Drive")
        print("   - Modulele instalate (pip install PyDrive2)")
        return
    
    # Testează crearea backup-ului
    if not test_backup_creation():
        print("\n❌ Testarea creării backup-ului a eșuat!")
        return
    
    # Testează restaurarea
    if not test_restore():
        print("\n❌ Testarea restaurarei a eșuat!")
        return
    
    print("\n🎉 Toate testele au trecut cu succes!")
    print("✅ Google Drive backup este configurat și funcțional!")
    print("\n📋 Următorii pași:")
    print("   1. Fă commit și push la cod")
    print("   2. Render va face deploy automat")
    print("   3. Aplicația va avea backup automat pe Google Drive")

if __name__ == "__main__":
    main() 