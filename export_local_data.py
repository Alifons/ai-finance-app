#!/usr/bin/env python3
"""
Script pentru exportul datelor locale
Creează un fișier JSON cu toate datele locale pentru sincronizare
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

def export_local_data():
    """Exportă datele locale în format JSON"""
    print("=== Export date locale ===")
    
    conn = sqlite3.connect('finance.db')
    conn.row_factory = sqlite3.Row
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
            'source': 'local_export'
        }
        
        export_filename = f'local_data_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(export_filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Export creat: {export_filename}")
        print(f"   - Tranzacții: {len(tranzactii_list)}")
        print(f"   - Obiecte: {len(obiecte_list)}")
        
        # Afișează ultimele tranzacții
        if tranzactii_list:
            print("\n📋 Ultimele tranzacții:")
            for i, tranzactie in enumerate(tranzactii_list[:5]):
                print(f"   {i+1}. {tranzactie['data']} - {tranzactie['suma']} RON - {tranzactie['comentariu']}")
        
        # Afișează obiectele
        if obiecte_list:
            print("\n🏷️ Obiecte:")
            for obiect in obiecte_list:
                print(f"   - {obiect['nume']}: {obiect['valoare']} RON")
        
        return export_filename
        
    except Exception as e:
        print(f"❌ Eroare la export: {e}")
        return None
        
    finally:
        conn.close()

def create_backup_with_export():
    """Creează backup cu datele exportate"""
    print("\n=== Creare backup cu datele exportate ===")
    
    # Export date
    export_filename = export_local_data()
    
    if export_filename:
        # Creează backup al bazei
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'finance_backup_{timestamp}.db'
        
        if os.path.exists('finance.db'):
            import shutil
            Path('backups').mkdir(exist_ok=True)
            shutil.copy2('finance.db', f'backups/{backup_filename}')
            print(f"✅ Backup baza de date: {backup_filename}")
        
        # Copiază export-ul în backups
        shutil.copy2(export_filename, f'backups/{export_filename}')
        print(f"✅ Export salvat în backups: {export_filename}")
        
        print(f"\n✅ Operație completă!")
        print(f"Datele sunt disponibile în:")
        print(f"   - Baza de date: finance.db")
        print(f"   - Export JSON: {export_filename}")
        print(f"   - Backup: backups/{backup_filename}")
        
        return True
    else:
        print("❌ Exportul a eșuat!")
        return False

def main():
    """Funcția principală"""
    print("📊 Export date locale")
    print("Această operație va:")
    print("1. Exporta toate datele locale în format JSON")
    print("2. Crea backup al bazei de date")
    print("3. Salva export-ul în folderul backups")
    print()
    
    success = create_backup_with_export()
    
    if success:
        print("\n🎉 Export complet!")
        print("Datele tale sunt salvate și disponibile pentru sincronizare.")
    else:
        print("\n❌ Exportul a eșuat!")

if __name__ == "__main__":
    main() 