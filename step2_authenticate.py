#!/usr/bin/env python3
"""
Pasul 2: Autentificarea Google Drive
"""

import os
import json
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

def check_client_secrets():
    """Verifică dacă client_secrets.json este valid"""
    print("🔍 Verificare client_secrets.json...")
    
    try:
        with open('client_secrets.json', 'r', encoding='utf-8') as f:
            secrets = json.load(f)
        
        # Verifică structura
        if 'installed' in secrets:
            client_id = secrets['installed']['client_id']
            client_secret = secrets['installed']['client_secret']
        elif 'web' in secrets:
            client_id = secrets['web']['client_id']
            client_secret = secrets['web']['client_secret']
        else:
            print("❌ Structură invalidă în client_secrets.json")
            return False
        
        # Verifică dacă sunt valori reale
        if client_id == 'test' or client_secret == 'test':
            print("❌ client_secrets.json conține valori de test!")
            print("💡 Trebuie să descarci credențialele reale din Google Cloud Console")
            return False
        
        print("✅ client_secrets.json pare valid")
        print(f"   Client ID: {client_id[:20]}...")
        print(f"   Client Secret: {client_secret[:10]}...")
        return True
        
    except Exception as e:
        print(f"❌ Eroare la verificarea client_secrets.json: {e}")
        return False

def authenticate_google_drive():
    """Autentifică Google Drive"""
    print("\n🔄 Autentificare Google Drive...")
    print("=" * 50)
    
    try:
        # Configurează GoogleAuth
        gauth = GoogleAuth()
        
        # Setări pentru refresh token
        gauth.settings['access_type'] = 'offline'
        gauth.settings['approval_prompt'] = 'force'
        
        # Încearcă să încarce token-ul existent
        try:
            gauth.LoadCredentialsFile("gdrive_token.json")
        except:
            pass
        
        if gauth.credentials is None:
            print("🌐 Se deschide browserul pentru autentificare...")
            print("📝 Autentifică-te cu contul tău Google")
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            print("🔄 Reîmprospătare token...")
            gauth.Refresh()
        else:
            print("✅ Token valid găsit")
            gauth.Authorize()
        
        # Salvează credențialele
        gauth.SaveCredentialsFile("gdrive_token.json")
        
        # Testează conexiunea
        drive = GoogleDrive(gauth)
        
        # Lista fișiere pentru test
        file_list = drive.ListFile({'q': "trashed=false"}).GetList()
        print(f"✅ Conectare reușită! Găsite {len(file_list)} fișiere pe Google Drive")
        
        return True
        
    except Exception as e:
        print(f"❌ Eroare la autentificare: {e}")
        return False

def verify_token():
    """Verifică token-ul salvat"""
    print("\n🔍 Verificare token salvat...")
    
    try:
        with open('gdrive_token.json', 'r', encoding='utf-8') as f:
            token = json.load(f)
        
        if token.get('access_token') == 'test' or token.get('refresh_token') == 'test':
            print("❌ Token-ul conține valori de test!")
            return False
        
        print("✅ Token valid găsit")
        print(f"   Access Token: {token.get('access_token', 'N/A')[:20]}...")
        print(f"   Refresh Token: {token.get('refresh_token', 'N/A')[:20]}...")
        return True
        
    except Exception as e:
        print(f"❌ Eroare la verificarea token-ului: {e}")
        return False

def main():
    """Funcția principală"""
    print("🔐 PASUL 2: AUTENTIFICARE GOOGLE DRIVE")
    print("=" * 60)
    
    # Verifică credențialele
    if not check_client_secrets():
        print("\n❌ Trebuie să completezi Pasul 1 înainte!")
        return
    
    # Autentifică Google Drive
    if authenticate_google_drive():
        print("\n✅ Autentificare reușită!")
        
        # Verifică token-ul
        if verify_token():
            print("\n🎉 TOATE CREDENȚIALELE SUNT GATA!")
            print("✅ Poți continua cu Pasul 3")
        else:
            print("\n⚠️ Problema cu token-ul")
    else:
        print("\n❌ Autentificarea a eșuat")

if __name__ == "__main__":
    main() 