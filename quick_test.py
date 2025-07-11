#!/usr/bin/env python3
"""
Test rapid pentru pagina de backup
"""

import requests
import time

def test_backup_page():
    """Testează rapid pagina de backup"""
    print("🧪 Test rapid pagina backup")
    print("=" * 30)
    
    try:
        # Așteaptă puțin să pornească serverul
        time.sleep(2)
        
        # Testează pagina de backup
        response = requests.get("http://127.0.0.1:5000/backup", timeout=5)
        
        if response.status_code == 200:
            print("✅ Pagina de backup funcționează!")
            
            # Verifică dacă conține backup-uri
            content = response.text
            
            if "Backup-uri Disponibile" in content:
                print("✅ Secțiunea de backup-uri este prezentă")
                
                # Numără backup-urile din tabel
                if "finance_backup_" in content:
                    backup_count = content.count("finance_backup_")
                    print(f"📊 Găsite {backup_count} backup-uri în pagină")
                else:
                    print("⚠️ Nu s-au găsit backup-uri în pagină")
            else:
                print("❌ Secțiunea de backup-uri nu este găsită")
                
        else:
            print(f"❌ Eroare la accesarea paginii: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Nu s-a putut accesa serverul: {e}")
        print("💡 Asigură-te că aplicația rulează (python app.py)")

if __name__ == "__main__":
    test_backup_page() 