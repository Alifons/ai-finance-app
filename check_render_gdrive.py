#!/usr/bin/env python3
"""
Script pentru verificarea și configurarea Google Drive pe Render
"""

import os
import json

def check_render_environment():
    """Verifică mediul Render și variabilele de mediu"""
    print("🔍 Verificare mediu Render...")
    print("=" * 50)
    
    # Verifică dacă sunt pe Render
    is_render = os.environ.get('RENDER', False) or 'render' in os.environ.get('HOSTNAME', '').lower()
    print(f"🌐 Pe Render: {is_render}")
    
    if is_render:
        print("✅ Detectat mediul Render")
    else:
        print("ℹ️ Nu sunt pe Render (mediu local)")
    
    # Verifică variabilele de mediu Google Drive
    gdrive_secrets = os.environ.get('GDRIVE_CLIENT_SECRETS')
    gdrive_token = os.environ.get('GDRIVE_TOKEN')
    
    print(f"\n🔑 Variabile de mediu Google Drive:")
    print(f"   GDRIVE_CLIENT_SECRETS: {'✅ Setat' if gdrive_secrets else '❌ Lipsă'}")
    print(f"   GDRIVE_TOKEN: {'✅ Setat' if gdrive_token else '❌ Lipsă'}")
    
    if gdrive_secrets and gdrive_token:
        print("✅ Toate variabilele Google Drive sunt configurate!")
        return True
    else:
        print("❌ Variabilele Google Drive lipsesc!")
        return False

def test_gdrive_connection():
    """Testează conexiunea la Google Drive"""
    print("\n🔄 Testare conexiune Google Drive...")
    print("=" * 50)
    
    try:
        from auto_backup import gdrive_auth
        
        # Simulează variabilele de mediu dacă nu sunt setate
        if not os.environ.get('GDRIVE_CLIENT_SECRETS'):
            print("⚠️ Simulare variabile de mediu pentru test...")
            # Aici ar trebui să setezi variabilele reale
            pass
        
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

def check_backup_folder():
    """Verifică folderul de backup pe Google Drive"""
    print("\n📁 Verificare folder backup Google Drive...")
    print("=" * 50)
    
    try:
        from auto_backup import get_backup_system
        
        backup_system = get_backup_system()
        folder_id = backup_system.gdrive_folder_id
        
        if folder_id:
            print(f"✅ Folder backup găsit: {folder_id}")
            
            # Lista backup-urile din folder
            backups = backup_system.get_backup_list()
            gdrive_backups = [b for b in backups if b.get('gdrive_id')]
            
            print(f"📦 Backup-uri pe Google Drive: {len(gdrive_backups)}")
            
            for backup in gdrive_backups[:3]:  # Primele 3
                print(f"   • {backup['filename']} (ID: {backup['gdrive_id']})")
            
            return True
        else:
            print("❌ Folder backup nu a fost găsit")
            return False
            
    except Exception as e:
        print(f"❌ Eroare la verificarea folderului: {e}")
        return False

def main():
    """Funcția principală"""
    print("🧪 VERIFICARE CONFIGURARE RENDER + GOOGLE DRIVE")
    print("=" * 60)
    
    # Verifică mediul Render
    render_ok = check_render_environment()
    
    # Testează Google Drive
    gdrive_ok = test_gdrive_connection()
    
    # Verifică folderul backup
    folder_ok = check_backup_folder()
    
    print("\n" + "=" * 60)
    print("📋 REZUMAT:")
    print(f"   Render: {'✅ OK' if render_ok else '❌ Problema'}")
    print(f"   Google Drive: {'✅ OK' if gdrive_ok else '❌ Problema'}")
    print(f"   Folder Backup: {'✅ OK' if folder_ok else '❌ Problema'}")
    
    if render_ok and gdrive_ok and folder_ok:
        print("\n🎉 Toate componentele funcționează!")
        print("✅ Render va putea restaura datele din Google Drive")
    else:
        print("\n⚠️ Există probleme de configurare")
        print("💡 Verifică variabilele de mediu pe Render")

if __name__ == "__main__":
    main() 