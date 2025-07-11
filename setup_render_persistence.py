#!/usr/bin/env python3
"""
Script pentru configurarea automată a persistenței datelor pe Render
"""

import os
import json
import shutil
from datetime import datetime

def check_render_environment():
    """Verifică și configurează mediul Render"""
    print("🔍 Verificare mediu Render...")
    print("=" * 50)
    
    # Verifică dacă sunt pe Render
    is_render = os.environ.get('RENDER', False) or 'render' in os.environ.get('HOSTNAME', '').lower()
    print(f"🌐 Pe Render: {is_render}")
    
    if not is_render:
        print("⚠️ Acest script este destinat doar pentru Render")
        return False
    
    # Verifică variabilele de mediu
    required_vars = ['GDRIVE_CLIENT_SECRETS', 'GDRIVE_TOKEN']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variabile de mediu lipsesc: {', '.join(missing_vars)}")
        print("💡 Configurează variabilele de mediu pe Render dashboard")
        return False
    else:
        print("✅ Toate variabilele de mediu sunt configurate")
        return True

def setup_google_drive_files():
    """Configurează fișierele Google Drive din variabilele de mediu"""
    print("\n🔧 Configurare fișiere Google Drive...")
    print("=" * 50)
    
    try:
        # Citește din variabilele de mediu
        client_secrets_str = os.environ.get('GDRIVE_CLIENT_SECRETS')
        token_str = os.environ.get('GDRIVE_TOKEN')
        
        if not client_secrets_str or not token_str:
            print("❌ Variabilele de mediu Google Drive lipsesc")
            return False
        
        # Salvează fișierele temporar
        with open('client_secrets.json', 'w') as f:
            f.write(client_secrets_str)
        
        with open('gdrive_token.json', 'w') as f:
            f.write(token_str)
        
        print("✅ Fișiere Google Drive configurate din variabilele de mediu")
        return True
        
    except Exception as e:
        print(f"❌ Eroare la configurarea fișierelor: {e}")
        return False

def test_google_drive_connection():
    """Testează conexiunea la Google Drive"""
    print("\n🔄 Testare conexiune Google Drive...")
    print("=" * 50)
    
    try:
        from auto_backup import gdrive_auth
        
        drive = gdrive_auth()
        
        if drive:
            print("✅ Conexiune la Google Drive reușită!")
            
            # Testează listarea fișierelor
            file_list = drive.ListFile({'q': "trashed=false"}).GetList()
            print(f"📁 Fișiere găsite pe Google Drive: {len(file_list)}")
            
            return True
        else:
            print("❌ Nu s-a putut conecta la Google Drive")
            return False
            
    except Exception as e:
        print(f"❌ Eroare la testarea Google Drive: {e}")
        return False

def setup_backup_folder():
    """Configurează folderul de backup pe Google Drive"""
    print("\n📁 Configurare folder backup Google Drive...")
    print("=" * 50)
    
    try:
        from auto_backup import get_backup_system
        
        backup_system = get_backup_system()
        folder_id = backup_system.gdrive_folder_id
        
        if folder_id:
            print(f"✅ Folder backup configurat: {folder_id}")
            return True
        else:
            print("❌ Nu s-a putut configura folderul de backup")
            return False
            
    except Exception as e:
        print(f"❌ Eroare la configurarea folderului: {e}")
        return False

def test_backup_and_restore():
    """Testează backup-ul și restaurarea"""
    print("\n🧪 Testare backup și restaurare...")
    print("=" * 50)
    
    try:
        from auto_backup import get_backup_system
        from app import restore_from_google_drive
        
        backup_system = get_backup_system()
        
        # Creează un backup de test
        print("📦 Creare backup de test...")
        backup_filename = backup_system.create_backup(upload_to_gdrive_flag=True)
        print(f"✅ Backup creat: {backup_filename}")
        
        # Testează restaurarea
        print("🔄 Testare restaurare...")
        success, message = restore_from_google_drive()
        
        if success:
            print(f"✅ Restaurare reușită: {message}")
            return True
        else:
            print(f"❌ Restaurare eșuată: {message}")
            return False
            
    except Exception as e:
        print(f"❌ Eroare la testarea backup/restore: {e}")
        return False

def create_persistence_script():
    """Creează un script pentru persistența automată"""
    print("\n📝 Creare script persistență automată...")
    print("=" * 50)
    
    script_content = '''#!/usr/bin/env python3
"""
Script pentru persistența automată a datelor pe Render
"""

import os
import time
from datetime import datetime

def ensure_persistence():
    """Asigură persistența datelor pe Render"""
    is_render = os.environ.get('RENDER', False) or 'render' in os.environ.get('HOSTNAME', '').lower()
    
    if is_render:
        print(f"🔄 Verificare persistență la {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            from app import init_db
            init_db()
            print("✅ Persistența verificată și asigurată")
        except Exception as e:
            print(f"⚠️ Eroare la verificarea persistenței: {e}")

if __name__ == "__main__":
    while True:
        ensure_persistence()
        time.sleep(300)  # Verifică la fiecare 5 minute
'''
    
    with open('render_persistence.py', 'w') as f:
        f.write(script_content)
    
    print("✅ Script persistență creat: render_persistence.py")

def main():
    """Funcția principală"""
    print("🚀 CONFIGURARE PERSISTENȚĂ RENDER")
    print("=" * 60)
    
    # Verifică mediul Render
    env_ok = check_render_environment()
    if not env_ok:
        return
    
    # Configurează fișierele Google Drive
    files_ok = setup_google_drive_files()
    if not files_ok:
        return
    
    # Testează conexiunea Google Drive
    gdrive_ok = test_google_drive_connection()
    if not gdrive_ok:
        return
    
    # Configurează folderul de backup
    folder_ok = setup_backup_folder()
    if not folder_ok:
        return
    
    # Testează backup și restaurare
    test_ok = test_backup_and_restore()
    
    # Creează scriptul de persistență
    create_persistence_script()
    
    print("\n" + "=" * 60)
    print("📋 REZUMAT CONFIGURARE:")
    print(f"   Mediu Render: {'✅ OK' if env_ok else '❌ Problema'}")
    print(f"   Fișiere GDrive: {'✅ OK' if files_ok else '❌ Problema'}")
    print(f"   Conexiune GDrive: {'✅ OK' if gdrive_ok else '❌ Problema'}")
    print(f"   Folder Backup: {'✅ OK' if folder_ok else '❌ Problema'}")
    print(f"   Test Backup/Restore: {'✅ OK' if test_ok else '❌ Problema'}")
    
    if env_ok and files_ok and gdrive_ok and folder_ok and test_ok:
        print("\n🎉 Configurarea este completă!")
        print("✅ Render va păstra datele între restart-uri")
        print("✅ Backup-urile se vor face automat pe Google Drive")
        print("✅ Restaurarea se va face automat la pornire")
    else:
        print("\n⚠️ Există probleme de configurare")
        print("💡 Verifică variabilele de mediu și conexiunea Google Drive")

if __name__ == "__main__":
    main() 