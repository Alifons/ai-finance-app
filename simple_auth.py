#!/usr/bin/env python3
"""
Script simplu pentru autentificarea Google Drive
"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scopuri pentru Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate():
    """Autentifică și obține token-ul"""
    print("🔄 Autentificare Google Drive...")
    
    creds = None
    
    # Verifică dacă există token-ul salvat
    if os.path.exists('gdrive_token.json'):
        try:
            creds = Credentials.from_authorized_user_file('gdrive_token.json', SCOPES)
            print("✅ Token găsit, verificare validitate...")
        except Exception as e:
            print(f"⚠️ Token invalid: {e}")
    
    # Dacă nu există credențiale valide, autentifică
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Reîmprospătare token...")
            creds.refresh(Request())
        else:
            print("🌐 Deschidere browser pentru autentificare...")
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Salvează credențialele
        with open('gdrive_token.json', 'w') as token:
            token.write(creds.to_json())
        print("✅ Token salvat în gdrive_token.json")
    
    return creds

def main():
    """Funcția principală"""
    print("🔐 AUTENTIFICARE GOOGLE DRIVE")
    print("=" * 40)
    
    try:
        # Autentifică
        creds = authenticate()
        
        # Testează conexiunea
        from googleapiclient.discovery import build
        service = build('drive', 'v3', credentials=creds)
        
        # Lista fișiere pentru test
        results = service.files().list(pageSize=10).execute()
        files = results.get('files', [])
        
        print(f"✅ Conectare reușită! Găsite {len(files)} fișiere pe Google Drive")
        
        # Afișează conținutul token-ului pentru Render
        print("\n📋 Conținutul pentru GOOGLE_DRIVE_TOKEN pe Render:")
        with open('gdrive_token.json', 'r') as f:
            token_content = f.read()
        print(token_content)
        
        return True
        
    except Exception as e:
        print(f"❌ Eroare: {e}")
        return False

if __name__ == "__main__":
    main() 