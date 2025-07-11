#!/usr/bin/env python3
"""
Script pentru configurarea Google Drive pe Render
"""

import os
import json
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

def setup_gdrive_render():
    """Configurează Google Drive pentru Render"""
    print("🔧 Configurare Google Drive pentru Render")
    print("=" * 50)
    
    # Verifică dacă există fișierele de configurare
    if not os.path.exists('client_secrets.json'):
        print("❌ Fișierul client_secrets.json nu există!")
        print("💡 Trebuie să creezi un proiect pe Google Cloud Console și să descarci credentials.json")
        return False
    
    try:
        # Configurează Google Auth
        gauth = GoogleAuth()
        
        # Pentru Render, folosim autentificarea cu service account
        # sau cu credentials pre-configurate
        gauth.settings['get_refresh_token'] = True
        gauth.settings['client_config_file'] = 'client_secrets.json'
        
        # Încearcă să se autentifice
        gauth.LocalWebserverAuth()
        
        # Salvează token-ul
        gauth.SaveCredentialsFile("gdrive_token.json")
        
        print("✅ Google Drive configurat cu succes!")
        print("📁 Token salvat în gdrive_token.json")
        
        # Testează conexiunea
        drive = GoogleDrive(gauth)
        file_list = drive.ListFile({'q': "title='AI Finance App Backups' and mimeType='application/vnd.google-apps.folder'"}).GetList()
        
        if file_list:
            print(f"✅ Folder găsit pe Google Drive: {file_list[0]['title']}")
        else:
            print("ℹ️ Nu există folder de backup pe Google Drive (va fi creat automat)")
        
        return True
        
    except Exception as e:
        print(f"❌ Eroare la configurarea Google Drive: {e}")
        print("\n💡 Pentru a configura Google Drive pe Render:")
        print("1. Mergi la https://console.cloud.google.com")
        print("2. Creează un proiect nou")
        print("3. Activează Google Drive API")
        print("4. Creează credentials (OAuth 2.0)")
        print("5. Descarcă fișierul JSON și redenumește-l în client_secrets.json")
        print("6. Rulează din nou acest script")
        return False

def create_gdrive_folder():
    """Creează folderul de backup pe Google Drive"""
    try:
        gauth = GoogleAuth()
        gauth.LoadCredentialsFile("gdrive_token.json")
        
        if gauth.credentials is None:
            print("❌ Nu există token salvat. Rulează mai întâi setup_gdrive_render()")
            return False
        
        drive = GoogleDrive(gauth)
        
        # Caută folderul existent
        folder_name = "AI Finance App Backups"
        file_list = drive.ListFile({'q': f"title='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()
        
        if file_list:
            folder_id = file_list[0]['id']
            print(f"✅ Folder găsit: {folder_name} (ID: {folder_id})")
        else:
            # Creează folderul nou
            folder_metadata = {
                'title': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = drive.CreateFile(folder_metadata)
            folder.Upload()
            folder_id = folder['id']
            print(f"✅ Folder creat: {folder_name} (ID: {folder_id})")
        
        return folder_id
        
    except Exception as e:
        print(f"❌ Eroare la crearea folderului: {e}")
        return False

if __name__ == "__main__":
    print("AI Finance App - Configurare Google Drive pentru Render")
    print("=" * 60)
    
    # Configurare inițială
    if setup_gdrive_render():
        # Creează folderul de backup
        folder_id = create_gdrive_folder()
        if folder_id:
            print(f"\n✅ Configurare completă!")
            print(f"📁 Folder ID: {folder_id}")
            print("🚀 Google Drive este gata pentru backup-uri!")
        else:
            print("\n❌ Nu s-a putut crea folderul de backup")
    else:
        print("\n❌ Configurarea a eșuat!") 