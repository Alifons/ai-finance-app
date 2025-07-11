#!/usr/bin/env python3
"""
Script pentru sincronizarea datelor între local și Render.com
"""

import os
import sqlite3
import json
import shutil
from datetime import datetime
from pathlib import Path

def get_render_url():
    """Returnează URL-ul aplicației pe Render"""
    # Înlocuiește cu URL-ul real al aplicației tale pe Render
    return "https://ai-finance-app.onrender.com"

def export_local_data():
    """Exportă datele locale în format JSON"""
    db_path = 'finance.db'
    if not os.path.exists(db_path):
        print("❌ Baza de date locală nu există!")
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Exportă tranzacțiile
        tranzactii = cursor.execute("SELECT * FROM tranzactii").fetchall()
        tranzactii_data = []
        for row in tranzactii:
            tranzactii_data.append({
                'id': row[0],
                'data': row[1],
                'suma': row[2],
                'comentariu': row[3],
                'operator': row[4],
                'tip': row[5],
                'obiect': row[6],
                'persoana': row[7],
                'categorie': row[8]
            })
        
        # Exportă obiectele
        obiecte = cursor.execute("SELECT * FROM obiecte").fetchall()
        obiecte_data = []
        for row in obiecte:
            obiecte_data.append({
                'id': row[0],
                'nume': row[1]
            })
        
        conn.close()
        
        export_data = {
            'tranzactii': tranzactii_data,
            'obiecte': obiecte_data,
            'exported_at': datetime.now().isoformat(),
            'total_tranzactii': len(tranzactii_data),
            'total_obiecte': len(obiecte_data)
        }
        
        # Salvează în fișier
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'local_data_export_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Date exportate în {filename}")
        print(f"   - Tranzacții: {len(tranzactii_data)}")
        print(f"   - Obiecte: {len(obiecte_data)}")
        
        return export_data
        
    except Exception as e:
        print(f"❌ Eroare la export: {e}")
        return None

def import_to_render(data):
    """Importă datele pe Render prin API"""
    import requests
    
    render_url = get_render_url()
    api_url = f"{render_url}/api/import"
    
    try:
        response = requests.post(api_url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Date importate cu succes pe Render!")
            print(f"   - Tranzacții importate: {result.get('tranzactii_importate', 0)}")
            print(f"   - Obiecte importate: {result.get('obiecte_importate', 0)}")
            return True
        else:
            print(f"❌ Eroare la import pe Render: {response.status_code}")
            print(f"   Răspuns: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Eroare la comunicarea cu Render: {e}")
        return False

def sync_local_to_render():
    """Sincronizează datele locale cu Render"""
    print("🔄 Sincronizare date locale → Render.com")
    print("=" * 50)
    
    # Exportă datele locale
    data = export_local_data()
    if not data:
        return False
    
    # Importă pe Render
    success = import_to_render(data)
    
    if success:
        print("\n✅ Sincronizare completă!")
        print(f"🌐 Aplicația este disponibilă la: {get_render_url()}")
    else:
        print("\n❌ Sincronizarea a eșuat!")
    
    return success

def backup_before_sync():
    """Creează backup înainte de sincronizare"""
    backup_dir = Path('backups')
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'pre_sync_backup_{timestamp}.db'
    backup_path = backup_dir / backup_filename
    
    try:
        shutil.copy2('finance.db', backup_path)
        print(f"✅ Backup creat: {backup_filename}")
        return True
    except Exception as e:
        print(f"❌ Eroare la backup: {e}")
        return False

def main():
    """Funcția principală"""
    print("AI Finance App - Sincronizare cu Render.com")
    print("=" * 50)
    
    # Verifică dacă baza de date există
    if not os.path.exists('finance.db'):
        print("❌ Baza de date locală nu există!")
        print("Asigură-te că ești în directorul aplicației.")
        return
    
    # Creează backup înainte de sincronizare
    print("🔒 Creez backup înainte de sincronizare...")
    backup_before_sync()
    
    # Sincronizează
    success = sync_local_to_render()
    
    if success:
        print("\n🎉 Sincronizare finalizată cu succes!")
        print("📱 Aplicația ta este acum disponibilă online!")
    else:
        print("\n⚠️ Sincronizarea a eșuat!")
        print("Verifică conexiunea la internet și încearcă din nou.")

if __name__ == "__main__":
    main() 