#!/usr/bin/env python3
"""
Script pentru sincronizarea datelor între local și Render
"""

import sqlite3
import json
import requests
from datetime import datetime
import os

def get_local_data():
    """Obține datele din baza locală"""
    try:
        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()
        
        # Obține tranzacțiile
        cursor.execute("SELECT * FROM tranzactii ORDER BY id")
        tranzactii = cursor.fetchall()
        
        # Obține obiectele
        cursor.execute("SELECT * FROM obiecte ORDER BY id")
        obiecte = cursor.fetchall()
        
        conn.close()
        
        return {
            'tranzactii': tranzactii,
            'obiecte': obiecte,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"❌ Eroare la citirea datelor locale: {e}")
        return None

def get_render_data():
    """Obține datele de pe Render prin API"""
    try:
        # URL-ul aplicației pe Render
        render_url = "https://ai-finance-app.onrender.com"
        
        # Obține datele prin API
        response = requests.get(f"{render_url}/api/export", timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Eroare la obținerea datelor de pe Render: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Eroare la conectarea la Render: {e}")
        return None

def compare_data(local_data, render_data):
    """Compară datele locale cu cele de pe Render"""
    print("📊 Comparare date:")
    print("=" * 40)
    
    if not local_data or not render_data:
        print("❌ Nu s-au putut obține datele")
        return False
    
    local_tranzactii = len(local_data.get('tranzactii', []))
    render_tranzactii = len(render_data.get('tranzactii', []))
    
    local_obiecte = len(local_data.get('obiecte', []))
    render_obiecte = len(render_data.get('obiecte', []))
    
    print(f"📈 Tranzacții:")
    print(f"   Local: {local_tranzactii}")
    print(f"   Render: {render_tranzactii}")
    print(f"   Diferență: {abs(local_tranzactii - render_tranzactii)}")
    
    print(f"\n📦 Obiecte:")
    print(f"   Local: {local_obiecte}")
    print(f"   Render: {render_obiecte}")
    print(f"   Diferență: {abs(local_obiecte - render_obiecte)}")
    
    if local_tranzactii == render_tranzactii and local_obiecte == render_obiecte:
        print("\n✅ Datele sunt sincronizate!")
        return True
    else:
        print("\n⚠️ Datele diferă între local și Render!")
        return False

def sync_to_render(local_data):
    """Sincronizează datele locale pe Render"""
    try:
        render_url = "https://ai-finance-app.onrender.com"
        
        # Trimite datele pe Render
        response = requests.post(
            f"{render_url}/api/import",
            json=local_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Datele au fost sincronizate pe Render!")
            return True
        else:
            print(f"❌ Eroare la sincronizarea pe Render: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Eroare la sincronizarea pe Render: {e}")
        return False

def main():
    """Funcția principală"""
    print("🔄 Sincronizare Local ↔ Render")
    print("=" * 50)
    
    # Obține datele locale
    print("📥 Obțin datele locale...")
    local_data = get_local_data()
    
    if not local_data:
        print("❌ Nu s-au putut obține datele locale!")
        return
    
    # Obține datele de pe Render
    print("📥 Obțin datele de pe Render...")
    render_data = get_render_data()
    
    if not render_data:
        print("❌ Nu s-au putut obține datele de pe Render!")
        print("💡 Verifică dacă aplicația pe Render este disponibilă")
        return
    
    # Compară datele
    are_sync = compare_data(local_data, render_data)
    
    if not are_sync:
        print("\n🔄 Sincronizez datele locale pe Render...")
        if sync_to_render(local_data):
            print("✅ Sincronizare completă!")
        else:
            print("❌ Sincronizarea a eșuat!")
    else:
        print("\n✅ Datele sunt deja sincronizate!")

if __name__ == "__main__":
    main() 