#!/usr/bin/env python3
"""
Script pentru sincronizarea cu serverul online
Descarcă datele de pe serverul online și le sincronizează cu baza locală
"""

import requests
import json
import sqlite3
import os
from datetime import datetime

# URL-ul aplicației tale pe Render
ONLINE_URL = "https://ai-finance-app-f521.onrender.com"

def download_online_data():
    """Descarcă datele de pe serverul online"""
    print("=== Descărcare date de pe serverul online ===")
    
    try:
        # Încearcă să descarci datele
        response = requests.get(f"{ONLINE_URL}/api/export", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Date descărcate cu succes de pe {ONLINE_URL}")
            return data
        else:
            print(f"❌ Eroare la descărcare: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Eroare de conexiune: {e}")
        return None

def backup_local_db():
    """Creează backup al bazei locale înainte de sincronizare"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'finance_local_backup_{timestamp}.db'
    
    if os.path.exists('finance.db'):
        import shutil
        shutil.copy2('finance.db', f'backups/{backup_filename}')
        print(f"✅ Backup local creat: {backup_filename}")
        return backup_filename
    return None

def sync_with_online_data(online_data):
    """Sincronizează datele locale cu cele de pe serverul online"""
    print("=== Sincronizare cu datele online ===")
    
    # Creează backup local
    backup_filename = backup_local_db()
    
    # Conectare la baza locală
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    
    try:
        # Șterge datele existente
        cursor.execute("DELETE FROM tranzactii")
        cursor.execute("DELETE FROM obiecte")
        
        # Inserează tranzacțiile de pe serverul online
        if 'tranzactii' in online_data:
            for tranzactie in online_data['tranzactii']:
                cursor.execute("""
                    INSERT INTO tranzactii (data, suma, comentariu, operator, tip, obiect, persoana, categorie)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tranzactie.get('data', ''),
                    tranzactie.get('suma', 0),
                    tranzactie.get('comentariu', ''),
                    tranzactie.get('operator', ''),
                    tranzactie.get('tip', ''),
                    tranzactie.get('obiect', ''),
                    tranzactie.get('persoana', ''),
                    tranzactie.get('categorie', '')
                ))
        
        # Inserează obiectele de pe serverul online
        if 'obiecte' in online_data:
            for obiect in online_data['obiecte']:
                cursor.execute("""
                    INSERT INTO obiecte (nume, valoare, descriere, categorie)
                    VALUES (?, ?, ?, ?)
                """, (
                    obiect.get('nume', ''),
                    obiect.get('valoare', 0),
                    obiect.get('descriere', ''),
                    obiect.get('categorie', '')
                ))
        
        conn.commit()
        print("✅ Sincronizare completă cu serverul online")
        
        # Afișează statistici
        cursor.execute("SELECT COUNT(*) FROM tranzactii")
        tranzactii_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM obiecte")
        obiecte_count = cursor.fetchone()[0]
        
        print(f"📊 Statistici după sincronizare:")
        print(f"   - Tranzacții: {tranzactii_count}")
        print(f"   - Obiecte: {obiecte_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Eroare la sincronizare: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

def main():
    """Funcția principală"""
    print("🔄 Sincronizare cu serverul online")
    print(f"URL server: {ONLINE_URL}")
    print()
    
    # Descarcă datele de pe serverul online
    online_data = download_online_data()
    
    if online_data is None:
        print("❌ Nu s-au putut descărca datele de pe serverul online")
        print("Verifică:")
        print("1. URL-ul aplicației pe Render")
        print("2. Conexiunea la internet")
        print("3. Dacă aplicația rulează pe Render")
        return False
    
    # Sincronizează cu datele locale
    success = sync_with_online_data(online_data)
    
    if success:
        print("\n✅ Sincronizare completă!")
        print("Aplicația locală are acum aceleași date ca serverul online.")
    else:
        print("\n❌ Sincronizarea a eșuat!")
    
    return success

if __name__ == "__main__":
    main() 