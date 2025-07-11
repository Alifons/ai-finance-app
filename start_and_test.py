#!/usr/bin/env python3
"""
Pornește serverul și testează pagina de backup
"""

import subprocess
import time
import requests
import sys

def start_server_and_test():
    """Pornește serverul și testează pagina de backup"""
    print("🚀 Pornesc serverul și testez backup-ul")
    print("=" * 50)
    
    try:
        # Pornește serverul în background
        print("🔄 Pornesc serverul...")
        server_process = subprocess.Popen([sys.executable, "app.py"], 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE)
        
        # Așteaptă să pornească serverul
        print("⏳ Aștept să pornească serverul...")
        time.sleep(3)
        
        # Testează pagina de backup
        print("🧪 Testez pagina de backup...")
        try:
            response = requests.get("http://127.0.0.1:5000/backup", timeout=10)
            if response.status_code == 200:
                print("✅ Pagina de backup funcționează!")
                print(f"   - Status: {response.status_code}")
                print(f"   - Lungime: {len(response.text)} caractere")
                
                # Verifică dacă conține backup-uri
                if "Backup-uri Disponibile" in response.text:
                    print("✅ Secțiunea de backup-uri este prezentă")
                else:
                    print("⚠️ Secțiunea de backup-uri nu este găsită")
                    
            else:
                print(f"❌ Eroare la accesarea paginii: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Nu s-a putut accesa serverul: {e}")
        
        # Oprește serverul
        print("⏹️ Oprește serverul...")
        server_process.terminate()
        server_process.wait()
        print("✅ Serverul oprit")
        
    except Exception as e:
        print(f"❌ Eroare: {e}")

if __name__ == "__main__":
    start_server_and_test() 