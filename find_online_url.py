#!/usr/bin/env python3
"""
Script pentru a găsi URL-ul real al aplicației pe Render
"""

import requests
import time

def test_url(url):
    """Testează dacă URL-ul funcționează"""
    try:
        print(f"🔍 Testez: {url}")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✅ URL funcționează: {url}")
            return True
        else:
            print(f"❌ Status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Eroare: {e}")
        return False

def main():
    """Testează diferite URL-uri posibile"""
    print("🔍 Căutare URL-ul real al aplicației pe Render")
    print()
    
    # Lista de URL-uri posibile
    possible_urls = [
        "https://ai-finance-app.onrender.com",
        "https://ai-finance-app-xxxxx-uc.a.run.app",  # Google Cloud Run
        "https://ai-finance-app.herokuapp.com",  # Heroku
        "https://ai-finance-app.vercel.app",  # Vercel
        "https://ai-finance-app.netlify.app",  # Netlify
    ]
    
    working_urls = []
    
    for url in possible_urls:
        if test_url(url):
            working_urls.append(url)
        time.sleep(1)  # Pauză între teste
    
    print("\n" + "="*50)
    if working_urls:
        print("✅ URL-uri care funcționează:")
        for url in working_urls:
            print(f"   - {url}")
        
        # Testează endpoint-ul de export
        for url in working_urls:
            print(f"\n🔍 Testez endpoint export: {url}/api/export")
            try:
                response = requests.get(f"{url}/api/export", timeout=10)
                if response.status_code == 200:
                    print(f"✅ Endpoint export funcționează: {url}/api/export")
                    data = response.json()
                    print(f"   - Tranzacții: {data.get('total_tranzactii', 0)}")
                    print(f"   - Obiecte: {data.get('total_obiecte', 0)}")
                    return url
                else:
                    print(f"❌ Endpoint export nu funcționează: {response.status_code}")
            except Exception as e:
                print(f"❌ Eroare la testarea endpoint-ului: {e}")
    else:
        print("❌ Nu s-a găsit niciun URL care funcționează")
        print("\nSugestii:")
        print("1. Verifică dashboard-ul Render.com pentru URL-ul corect")
        print("2. Verifică dacă aplicația este deployată")
        print("3. Verifică dacă ai făcut commit și push la ultimele modificări")
    
    return None

if __name__ == "__main__":
    main() 