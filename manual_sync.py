#!/usr/bin/env python3
"""
Script pentru sincronizare manuală cu serverul online
Permite introducerea manuală a URL-ului corect
"""

import requests
import json
import sqlite3
import os
from datetime import datetime

def get_manual_url():
    """Cere utilizatorului să introducă URL-ul corect"""
    print("🔍 Pentru a sincroniza cu serverul online, trebuie să introduci URL-ul corect.")
    print()
    print("Pași pentru a găsi URL-ul:")
    print("1. Mergi la https://dashboard.render.com")
    print("2. Găsește aplicația ta 'ai-finance-app'")
    print("3. Copiază URL-ul din secțiunea 'URL'")
    print()
    
    while True:
        url = input("Introdu URL-ul aplicației tale pe Render (sau 'skip' pentru a sări peste): ").strip()
        
        if url.lower() == 'skip':
            return None
        
        if not url:
            print("❌ URL-ul nu poate fi gol!")
            continue
        
        if not url.startswith('http'):
            url = 'https://' + url
        
        # Testează URL-ul
        try:
            print(f"🔍 Testez URL-ul: {url}")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ URL-ul funcționează: {url}")
                return url
            else:
                print(f"❌ URL-ul nu funcționează (status: {response.status_code})")
                retry = input("Vrei să încerci din nou? (y/n): ").strip().lower()
                if retry != 'y':
                    return None
        except Exception as e:
            print(f"❌ Eroare la testarea URL-ului: {e}")
            retry = input("Vrei să încerci din nou? (y/n): ").strip().lower()
            if retry != 'y':
                return None

def download_online_data(url):
    """Descarcă datele de pe serverul online"""
    print(f"\n=== Descărcare date de pe {url} ===")
    
    try:
        # Testează endpoint-ul de export
        export_url = f"{url}/api/export"
        print(f"🔍 Testez endpoint: {export_url}")
        
        response = requests.get(export_url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Date descărcate cu succes!")
            print(f"   - Tranzacții: {data.get('total_tranzactii', 0)}")
            print(f"   - Obiecte: {data.get('total_obiecte', 0)}")
            return data
        else:
            print(f"❌ Endpoint-ul nu funcționează (status: {response.status_code})")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Eroare de conexiune: {e}")
        return None

def backup_local_db():
    """Creează backup al bazei locale"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'finance_local_backup_{timestamp}.db'
    
    if os.path.exists('finance.db'):
        import shutil
        Path('backups').mkdir(exist_ok=True)
        shutil.copy2('finance.db', f'backups/{backup_filename}')
        print(f"✅ Backup local creat: {backup_filename}")
        return backup_filename
    return None

def sync_with_online_data(online_data):
    """Sincronizează datele locale cu cele de pe serverul online"""
    print("\n=== Sincronizare cu datele online ===")
    
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
    print("🔄 Sincronizare manuală cu serverul online")
    print("="*50)
    
    # Cere URL-ul manual
    url = get_manual_url()
    
    if url is None:
        print("\n⏭️ Sincronizarea a fost sărită.")
        print("Poți rula din nou scriptul când ai URL-ul corect.")
        return
    
    # Descarcă datele de pe serverul online
    online_data = download_online_data(url)
    
    if online_data is None:
        print("\n❌ Nu s-au putut descărca datele de pe serverul online")
        print("Verifică:")
        print("1. URL-ul aplicației pe Render")
        print("2. Dacă aplicația rulează pe Render")
        print("3. Dacă endpoint-ul /api/export este disponibil")
        return
    
    # Sincronizează cu datele locale
    success = sync_with_online_data(online_data)
    
    if success:
        print("\n✅ Sincronizare completă!")
        print("Aplicația locală are acum aceleași date ca serverul online.")
        print("\n🔄 Pentru a aplica modificările, repornește serverul local.")
    else:
        print("\n❌ Sincronizarea a eșuat!")

if __name__ == "__main__":
    main() 