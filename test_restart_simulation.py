#!/usr/bin/env python3
"""
Test pentru simularea restart-ului serverului și verificarea restaurarei din Google Drive
"""

import os
import shutil
import sqlite3
from datetime import datetime

def simulate_server_restart():
    """Simulează restart-ul serverului prin ștergerea bazei de date locale"""
    print("🔄 Simulare restart server...")
    print("=" * 50)
    
    # 1. Verifică starea inițială
    print("1️⃣ Verificare starea inițială:")
    if os.path.exists('finance.db'):
        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tranzactii")
        initial_count = cursor.fetchone()[0]
        conn.close()
        print(f"   📊 Baza de date are {initial_count} tranzacții")
    else:
        print("   ❌ Baza de date nu există")
        initial_count = 0
    
    # 2. Salvează o copie de siguranță
    if os.path.exists('finance.db'):
        backup_name = f"finance_backup_before_restart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2('finance.db', backup_name)
        print(f"   💾 Copie de siguranță salvată: {backup_name}")
    
    # 3. Simulează restart-ul prin ștergerea bazei de date
    print("\n2️⃣ Simulare restart (ștergere baza de date):")
    if os.path.exists('finance.db'):
        os.remove('finance.db')
        print("   🗑️ Baza de date ștearsă (simulare restart)")
    else:
        print("   ℹ️ Baza de date nu există (deja simulat restart)")
    
    # 4. Testează inițializarea și restaurarea
    print("\n3️⃣ Testare inițializare și restaurare:")
    
    # Importează funcțiile din app.py
    import sys
    sys.path.append('.')
    
    try:
        from app import init_db, restore_from_google_drive, check_database_has_data
        
        # Inițializează baza de date
        print("   🔧 Inițializare baza de date...")
        init_db()
        
        # Verifică dacă restaurarea a funcționat
        if check_database_has_data():
            conn = sqlite3.connect('finance.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tranzactii")
            restored_count = cursor.fetchone()[0]
            conn.close()
            
            print(f"   ✅ Restaurare reușită! Baza de date are {restored_count} tranzacții")
            
            if restored_count > initial_count:
                print(f"   📈 Îmbunătățire: {restored_count - initial_count} tranzacții noi restaurate")
            elif restored_count == initial_count:
                print(f"   ✅ Restaurare completă: toate {restored_count} tranzacțiile sunt prezente")
            else:
                print(f"   ⚠️ Restaurare parțială: {restored_count} din {initial_count} tranzacții")
        else:
            print("   ❌ Restaurarea nu a funcționat - baza de date este goală")
            
    except Exception as e:
        print(f"   ❌ Eroare la testare: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. Rezumat
    print("\n4️⃣ Rezumat:")
    print("   🎯 Testul de simulare restart complet")
    print("   📊 Verifică dacă restaurarea din Google Drive funcționează")
    print("   🔄 Pentru a testa din nou, rulează acest script din nou")

if __name__ == "__main__":
    simulate_server_restart() 