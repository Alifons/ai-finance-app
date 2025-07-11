#!/usr/bin/env python3
"""
Test backup manual
"""

import requests

def test_backup_manual():
    """Testează backup-ul manual"""
    print("🧪 Test backup manual")
    print("=" * 30)
    
    try:
        # Testează pagina backup
        response = requests.get('http://127.0.0.1:5000/backup')
        print(f"GET /backup: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Pagina backup funcționează")
        else:
            print("❌ Pagina backup nu funcționează")
            return
        
        # Testează backup manual
        print("\n🔄 Testez backup manual...")
        response = requests.post('http://127.0.0.1:5000/backup', data={'action': 'create'})
        print(f"POST /backup: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 302:  # Redirect
            location = response.headers.get('Location', '')
            print(f"Redirect: {location}")
            
            if 'success' in location:
                print("✅ Backup creat cu succes!")
            elif 'error' in location:
                print("❌ Eroare la crearea backup-ului!")
        elif response.status_code == 200:
            print("📄 Răspuns HTML primit")
            print(f"Content length: {len(response.text)}")
        else:
            print(f"❌ Răspuns neașteptat: {response.status_code}")
            print(f"Content: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Eroare: {e}")

if __name__ == "__main__":
    test_backup_manual() 