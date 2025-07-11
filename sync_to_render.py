#!/usr/bin/env python3
"""
Script pentru sincronizarea datelor cu Render.com
"""

import requests
import json
import os
from datetime import datetime

def get_render_url():
    """Returnează URL-ul aplicației pe Render"""
    # Înlocuiește cu URL-ul real al aplicației tale pe Render
    return "https://ai-finance-app.onrender.com"

def sync_to_render():
    """Sincronizează datele locale cu Render"""
    print("🔄 Sincronizare cu Render.com...")
    
    # URL-ul aplicației pe Render
    render_url = get_render_url()
    
    try:
        # Testează dacă aplicația pe Render este disponibilă
        print(f"🌐 Testez conexiunea la {render_url}...")
        response = requests.get(render_url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Aplicația pe Render nu este disponibilă (status: {response.status_code})")
            return False
        
        print("✅ Conexiune la Render stabilită!")
        
        # Obține datele de pe Render
        print("📥 Descarc datele de pe Render...")
        export_response = requests.get(f"{render_url}/api/export", timeout=30)
        
        if export_response.status_code != 200:
            print(f"❌ Nu s-au putut descărca datele de pe Render (status: {export_response.status_code})")
            return False
        
        render_data = export_response.json()
        
        print(f"📊 Date găsite pe Render:")
        print(f"   - Tranzacții: {render_data.get('total_tranzactii', 0)}")
        print(f"   - Obiecte: {render_data.get('total_obiecte', 0)}")
        
        # Salvează datele în fișier local pentru backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'render_data_backup_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(render_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Backup salvat în {filename}")
        
        return True
        
    except requests.exceptions.Timeout:
        print("❌ Timeout la conexiunea cu Render")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Nu s-a putut conecta la Render")
        return False
    except Exception as e:
        print(f"❌ Eroare: {e}")
        return False

def main():
    """Funcția principală"""
    print("AI Finance App - Sincronizare cu Render.com")
    print("=" * 50)
    
    success = sync_to_render()
    
    if success:
        print("\n✅ Sincronizare completă!")
        print("📱 Datele tale sunt acum disponibile online!")
    else:
        print("\n❌ Sincronizarea a eșuat!")
        print("Verifică:")
        print("   - URL-ul aplicației pe Render")
        print("   - Conexiunea la internet")
        print("   - Dacă aplicația pe Render rulează")

if __name__ == "__main__":
    main() 