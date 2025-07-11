#!/usr/bin/env python3
"""
Script pentru obținerea valorilor variabilelor de mediu pentru Render
"""

import json
import os

def get_client_secrets():
    """Obține conținutul client_secrets.json pentru Render"""
    try:
        with open('client_secrets.json', 'r', encoding='utf-8') as f:
            client_secrets = json.load(f)
        
        print("🔑 GDRIVE_CLIENT_SECRETS pentru Render:")
        print("=" * 50)
        print(json.dumps(client_secrets, indent=2))
        print("=" * 50)
        
        return client_secrets
    except Exception as e:
        print(f"❌ Eroare la citirea client_secrets.json: {e}")
        return None

def get_token():
    """Obține conținutul gdrive_token.json pentru Render"""
    try:
        with open('gdrive_token.json', 'r', encoding='utf-8') as f:
            token = json.load(f)
        
        print("\n🔑 GDRIVE_TOKEN pentru Render:")
        print("=" * 50)
        print(json.dumps(token, indent=2))
        print("=" * 50)
        
        return token
    except Exception as e:
        print(f"❌ Eroare la citirea gdrive_token.json: {e}")
        return None

def check_token_validity():
    """Verifică dacă token-ul este valid"""
    print("\n🔍 Verificare validitate token...")
    
    try:
        with open('gdrive_token.json', 'r', encoding='utf-8') as f:
            token = json.load(f)
        
        if token.get('access_token') == 'test' or token.get('refresh_token') == 'test':
            print("❌ Token-ul conține valori de test!")
            print("💡 Trebuie să autentifici Google Drive din nou")
            return False
        else:
            print("✅ Token-ul pare valid")
            return True
            
    except Exception as e:
        print(f"❌ Eroare la verificarea token-ului: {e}")
        return False

def instructions_for_render():
    """Instrucțiuni pentru configurarea Render"""
    print("\n📋 INSTRUCȚIUNI PENTRU RENDER:")
    print("=" * 50)
    print("1. Mergi la dashboard-ul Render")
    print("2. Selectează aplicația ta")
    print("3. Mergi la 'Environment' → 'Environment Variables'")
    print("4. Adaugă următoarele variabile:")
    print("\n   GDRIVE_CLIENT_SECRETS:")
    print("   (copiază conținutul de mai sus)")
    print("\n   GDRIVE_TOKEN:")
    print("   (copiază conținutul de mai sus)")
    print("\n5. Salvează și redeployează aplicația")

def main():
    """Funcția principală"""
    print("🔧 OBTINERE VARIABILE DE MEDIU PENTRU RENDER")
    print("=" * 60)
    
    # Obține credențialele
    client_secrets = get_client_secrets()
    token = get_token()
    
    # Verifică validitatea token-ului
    token_valid = check_token_validity()
    
    if client_secrets and token and token_valid:
        print("\n✅ Toate credențialele sunt disponibile!")
        instructions_for_render()
    elif client_secrets and not token_valid:
        print("\n⚠️ Client secrets sunt OK, dar token-ul trebuie reînnoit")
        print("💡 Rulează: python test_gdrive_auth.py")
    else:
        print("\n❌ Problema cu credențialele")
        print("💡 Verifică fișierele client_secrets.json și gdrive_token.json")

if __name__ == "__main__":
    main() 