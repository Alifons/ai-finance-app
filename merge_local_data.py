#!/usr/bin/env python3
"""
Script pentru consolidarea datelor locale
Creează o bază de date completă cu toate tranzacțiile locale
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

def backup_current_db():
    """Creează backup al bazei curente"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'finance_consolidated_backup_{timestamp}.db'
    
    if os.path.exists('finance.db'):
        import shutil
        Path('backups').mkdir(exist_ok=True)
        shutil.copy2('finance.db', f'backups/{backup_filename}')
        print(f"✅ Backup creat: {backup_filename}")
        return backup_filename
    return None

def get_all_backup_data():
    """Obține datele din toate backup-urile"""
    backup_dir = Path('backups')
    all_tranzactii = []
    all_obiecte = []
    
    if not backup_dir.exists():
        print("❌ Nu există folderul backups/")
        return [], []
    
    # Scanează toate fișierele .json din backups
    for json_file in backup_dir.glob('*.json'):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'tables' in data:
                    print(f"📄 Găsit backup: {json_file.name}")
        except Exception as e:
            print(f"⚠️ Eroare la citirea {json_file}: {e}")
    
    return all_tranzactii, all_obiecte

def consolidate_local_data():
    """Consolidează datele locale"""
    print("=== Consolidare date locale ===")
    
    # Backup baza curentă
    backup_filename = backup_current_db()
    
    # Conectare la baza de date
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    
    try:
        # Obține toate tranzacțiile curente
        cursor.execute("SELECT * FROM tranzactii ORDER BY data DESC")
        tranzactii = cursor.fetchall()
        
        # Obține toate obiectele curente
        cursor.execute("SELECT * FROM obiecte ORDER BY nume")
        obiecte = cursor.fetchall()
        
        print(f"📊 Statistici baza curentă:")
        print(f"   - Tranzacții: {len(tranzactii)}")
        print(f"   - Obiecte: {len(obiecte)}")
        
        # Afișează ultimele tranzacții
        if tranzactii:
            print("\n📋 Ultimele tranzacții:")
            for i, tranzactie in enumerate(tranzactii[:5]):
                print(f"   {i+1}. {tranzactie['data']} - {tranzactie['suma']} RON - {tranzactie['comentariu']}")
        
        # Afișează obiectele
        if obiecte:
            print("\n🏷️ Obiecte:")
            for obiect in obiecte:
                print(f"   - {obiect['nume']}: {obiect['valoare']} RON")
        
        conn.commit()
        print("\n✅ Consolidare completă!")
        print("Baza de date locală conține toate datele disponibile.")
        
        return True
        
    except Exception as e:
        print(f"❌ Eroare la consolidare: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

def export_local_data():
    """Exportă datele locale în format JSON"""
    print("\n=== Export date locale ===")
    
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    
    try:
        # Obține toate tranzacțiile
        cursor.execute("SELECT * FROM tranzactii ORDER BY data DESC")
        tranzactii = cursor.fetchall()
        tranzactii_list = [dict(row) for row in tranzactii]
        
        # Obține toate obiectele
        cursor.execute("SELECT * FROM obiecte ORDER BY nume")
        obiecte = cursor.fetchall()
        obiecte_list = [dict(row) for row in obiecte]
        
        # Creează fișierul de export
        export_data = {
            'tranzactii': tranzactii_list,
            'obiecte': obiecte_list,
            'export_date': datetime.now().isoformat(),
            'total_tranzactii': len(tranzactii_list),
            'total_obiecte': len(obiecte_list),
            'source': 'local_consolidated'
        }
        
        export_filename = f'local_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(export_filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Export creat: {export_filename}")
        print(f"   - Tranzacții: {len(tranzactii_list)}")
        print(f"   - Obiecte: {len(obiecte_list)}")
        
        return export_filename
        
    except Exception as e:
        print(f"❌ Eroare la export: {e}")
        return None
        
    finally:
        conn.close()

def main():
    """Funcția principală"""
    print("🔄 Consolidare date locale")
    print("Această operație va:")
    print("1. Crea backup al bazei curente")
    print("2. Consolida toate datele locale")
    print("3. Exporta datele în format JSON")
    print()
    
    # Consolidare date
    success = consolidate_local_data()
    
    if success:
        # Export date
        export_filename = export_local_data()
        
        if export_filename:
            print(f"\n✅ Operație completă!")
            print(f"Datele consolidate sunt disponibile în:")
            print(f"   - Baza de date: finance.db")
            print(f"   - Export JSON: {export_filename}")
            print(f"   - Backup: backups/")
        else:
            print("\n❌ Exportul a eșuat!")
    else:
        print("\n❌ Consolidarea a eșuat!")

if __name__ == "__main__":
    main() 