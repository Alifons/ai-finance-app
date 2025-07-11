#!/usr/bin/env python3
"""
Script simplu pentru testarea autentificării Google Drive
"""

import os
import yaml
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

def test_gdrive_auth():
    """Testează autentificarea Google Drive"""
    print("🔐 Testare autentificare Google Drive")
    print("=" * 40)
    
    try:
        # Încarcă setările
        with open('settings.yaml', 'r', encoding='utf-8') as f:
            settings = yaml.safe_load(f)
        
        # Configurează autentificarea
        gauth = GoogleAuth()
        
        # Setări pentru OAuth
        gauth.settings['client_config_file'] = settings['google_drive']['client_secrets_file']
        gauth.settings['save_credentials_file'] = settings['google_drive']['token_file']
        gauth.settings['oauth_scope'] = ['https://www.googleapis.com/auth/drive']
        
        # Setări pentru refresh token
        gauth.settings['access_type'] = 'offline'
        gauth.settings['approval_prompt'] = 'force'
        
        print("✅ Configurația încărcată")
        
        # Încearcă să încarce credențialele salvate
        try:
            gauth.LoadCredentialsFile(settings['google_drive']['token_file'])
            print("✅ Credențialele salvate încărcate")
        except:
            print("⚠️ Nu există credențiale salvate")
        
        # Autentificare
        if gauth.credentials is None:
            print("🔄 Se deschide browserul pentru autentificare...")
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            print("🔄 Token expirat, se reînnoiește...")
            gauth.Refresh()
        else:
            print("✅ Token valid")
            gauth.Authorize()
        
        # Salvează credențialele
        gauth.SaveCredentialsFile(settings['google_drive']['token_file'])
        print("✅ Credențialele salvate")
        
        # Testează conexiunea
        drive = GoogleDrive(gauth)
        
        # Lista fișierele din rădăcina Google Drive
        file_list = drive.ListFile({'q': "trashed=false"}).GetList()
        print(f"✅ Conexiunea funcționează! Găsite {len(file_list)} fișiere în Google Drive")
        
        # Testează crearea unui folder de test
        folder_name = "Test AI Finance App"
        folder_metadata = {
            'title': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        folder = drive.CreateFile(folder_metadata)
        folder.Upload()
        folder_id = folder['id']
        
        print(f"✅ Folder de test creat: {folder_name} (ID: {folder_id})")
        
        # Șterge folderul de test
        folder.Delete()
        print("🧹 Folderul de test a fost șters")
        
        print("\n🎉 Autentificarea Google Drive funcționează perfect!")
        return True
        
    except Exception as e:
        print(f"❌ Eroare la autentificare: {e}")
        print("\n🔧 Soluții posibile:")
        print("1. Verifică dacă fișierul client_secrets.json există")
        print("2. Verifică dacă Google Drive API este activat")
        print("3. Verifică credențialele OAuth2")
        return False

def main():
    """Funcția principală"""
    print("AI Finance App - Test Autentificare Google Drive")
    print("=" * 50)
    
    success = test_gdrive_auth()
    
    if success:
        print("\n✅ Testul de autentificare a trecut!")
        print("Acum poți rula backup-urile pe Google Drive")
    else:
        print("\n❌ Testul de autentificare a eșuat!")
        print("Verifică configurația Google Drive")

if __name__ == "__main__":
    main() 