#!/usr/bin/env python3
"""
Testează funcția de listare backup-uri din aplicația web
"""

import requests
import json

def test_web_backup_list():
    """Testează funcția de listare backup-uri din aplicația web"""
    print("🧪 Test listare backup-uri din aplicația web")
    print("=" * 50)
    
    try:
        # Testează pagina backup
        response = requests.get('http://127.0.0.1:5000/backup')
        print(f"GET /backup: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Pagina backup funcționează")
            
            # Verifică dacă conține backup-uri
            content = response.text
            
            # Caută backup-uri în HTML
            if 'finance_backup_' in content:
                print("✅ Backup-uri găsite în HTML")
                # Extrage numele backup-urilor
                import re
                backup_files = re.findall(r'finance_backup_\d+_\d+\.db', content)
                print(f"📦 Backup-uri găsite: {len(backup_files)}")
                for backup in backup_files[:3]:  # Primele 3
                    print(f"   - {backup}")
            else:
                print("❌ Nu s-au găsit backup-uri în HTML")
                print("💡 Posibile cauze:")
                print("   1. Funcția get_backup_list() nu returnează backup-uri")
                print("   2. Template-ul nu afișează backup-urile")
                print("   3. Eroare în aplicația web")
                
                # Verifică dacă există erori în HTML
                if 'error' in content.lower():
                    print("⚠️ Găsite erori în HTML:")
                    error_lines = [line for line in content.split('\n') if 'error' in line.lower()]
                    for line in error_lines[:3]:
                        print(f"   {line.strip()}")
        else:
            print(f"❌ Pagina backup nu funcționează: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Eroare: {e}")

def test_backup_api():
    """Testează API-ul de backup"""
    print("\n🔄 Test API backup:")
    print("=" * 30)
    
    try:
        # Simulează o cerere POST pentru backup
        response = requests.post('http://127.0.0.1:5000/backup', data={'action': 'create'})
        print(f"POST /backup: {response.status_code}")
        
        if response.status_code == 302:  # Redirect
            location = response.headers.get('Location', '')
            print(f"Redirect: {location}")
            
            if 'success' in location:
                print("✅ Backup creat cu succes!")
            elif 'error' in location:
                print("❌ Eroare la crearea backup-ului!")
        else:
            print(f"❌ Răspuns neașteptat: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Eroare la API: {e}")

if __name__ == "__main__":
    test_web_backup_list()
    test_backup_api() 