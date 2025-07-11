#!/usr/bin/env python3
"""
Pasul 3: Obținerea valorilor pentru Render
"""

import json
import os

def get_client_secrets_for_render():
    """Obține client_secrets.json pentru Render"""
    print("🔑 GDRIVE_CLIENT_SECRETS pentru Render:")
    print("=" * 60)
    
    try:
        with open('client_secrets.json', 'r', encoding='utf-8') as f:
            secrets = json.load(f)
        
        # Convertește la format JSON pentru Render
        secrets_json = json.dumps(secrets, indent=2)
        print(secrets_json)
        print("=" * 60)
        
        return secrets_json
        
    except Exception as e:
        print(f"❌ Eroare la citirea client_secrets.json: {e}")
        return None

def get_token_for_render():
    """Obține gdrive_token.json pentru Render"""
    print("\n🔑 GDRIVE_TOKEN pentru Render:")
    print("=" * 60)
    
    try:
        with open('gdrive_token.json', 'r', encoding='utf-8') as f:
            token = json.load(f)
        
        # Convertește la format JSON pentru Render
        token_json = json.dumps(token, indent=2)
        print(token_json)
        print("=" * 60)
        
        return token_json
        
    except Exception as e:
        print(f"❌ Eroare la citirea gdrive_token.json: {e}")
        return None

def verify_credentials():
    """Verifică dacă credențialele sunt valide"""
    print("\n🔍 Verificare credențiale...")
    
    # Verifică client_secrets.json
    try:
        with open('client_secrets.json', 'r', encoding='utf-8') as f:
            secrets = json.load(f)
        
        if 'installed' in secrets:
            client_id = secrets['installed']['client_id']
            client_secret = secrets['installed']['client_secret']
        elif 'web' in secrets:
            client_id = secrets['web']['client_id']
            client_secret = secrets['web']['client_secret']
        else:
            print("❌ Structură invalidă în client_secrets.json")
            return False
        
        if client_id == 'test' or client_secret == 'test':
            print("❌ client_secrets.json conține valori de test!")
            return False
        
        print("✅ client_secrets.json valid")
        
    except Exception as e:
        print(f"❌ Eroare la verificarea client_secrets.json: {e}")
        return False
    
    # Verifică gdrive_token.json
    try:
        with open('gdrive_token.json', 'r', encoding='utf-8') as f:
            token = json.load(f)
        
        if token.get('access_token') == 'test' or token.get('refresh_token') == 'test':
            print("❌ gdrive_token.json conține valori de test!")
            return False
        
        print("✅ gdrive_token.json valid")
        
    except Exception as e:
        print(f"❌ Eroare la verificarea gdrive_token.json: {e}")
        return False
    
    return True

def render_instructions():
    """Instrucțiuni pentru configurarea Render"""
    print("\n📋 INSTRUCȚIUNI PENTRU RENDER:")
    print("=" * 60)
    print("1. Mergi la dashboard-ul Render:")
    print("   https://dashboard.render.com/")
    print("\n2. Selectează aplicația ta (ai-finance-app)")
    print("\n3. Mergi la 'Environment' → 'Environment Variables'")
    print("\n4. Adaugă următoarele variabile:")
    print("\n   GDRIVE_CLIENT_SECRETS:")
    print("   (copiază conținutul de mai sus)")
    print("\n   GDRIVE_TOKEN:")
    print("   (copiază conținutul de mai sus)")
    print("\n5. Apasă 'Save Changes'")
    print("\n6. Mergi la 'Manual Deploy' → 'Deploy latest commit'")
    print("\n7. Așteaptă să se termine deploy-ul")
    print("\n8. Testează aplicația - datele ar trebui să fie restaurate automat!")

def main():
    """Funcția principală"""
    print("🔧 PASUL 3: OBTINERE VALORI PENTRU RENDER")
    print("=" * 60)
    
    # Verifică credențialele
    if not verify_credentials():
        print("\n❌ Credențialele nu sunt valide!")
        print("💡 Completează Pasul 1 și Pasul 2 înainte")
        return
    
    # Obține valorile pentru Render
    client_secrets = get_client_secrets_for_render()
    token = get_token_for_render()
    
    if client_secrets and token:
        print("\n✅ Toate valorile sunt gata!")
        render_instructions()
    else:
        print("\n❌ Nu s-au putut obține valorile")

if __name__ == "__main__":
    main() 