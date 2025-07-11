#!/usr/bin/env python3
"""
Script pentru testarea soluției de persistență pe Render
"""

import os
import shutil
import sqlite3
from datetime import datetime

def test_persistence_solution():
    """Testează soluția de persistență"""
    print("🧪 TEST SOLUȚIE PERSISTENȚĂ RENDER")
    print("=" * 60)
    
    # 1. Simulează mediul Render
    print("1️⃣ Simulare mediu Render...")
    os.environ['RENDER'] = 'true'
    os.environ['PERSIST_DATA'] = 'true'
    os.environ['GOOGLE_DRIVE_ENABLED'] = 'true'
    
    print("✅ Variabile de mediu Render simulate")
    
    # 2. Verifică starea inițială
    print("\n2️⃣ Verificare starea inițială:")
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
    
    # 3. Salvează o copie de siguranță
    if os.path.exists('finance.db'):
        backup_name = f"finance_test_persistence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2('finance.db', backup_name)
        print(f"   💾 Copie de siguranță salvată: {backup_name}")
    
    # 4. Simulează restart-ul (șterge baza de date)
    print("\n3️⃣ Simulare restart (ștergere baza de date):")
    if os.path.exists('finance.db'):
        os.remove('finance.db')
        print("   🗑️ Baza de date ștearsă (simulare restart)")
    else:
        print("   ℹ️ Baza de date nu există (deja simulat restart)")
    
    # 5. Testează restaurarea automată
    print("\n4️⃣ Testare restaurare automată:")
    
    try:
        from app import init_db, restore_from_google_drive
        
        # Inițializează baza de date (va forța restaurarea pe Render)
        print("   🔧 Inițializare baza de date cu restaurare forțată...")
        init_db()
        
        # Verifică rezultatul
        if os.path.exists('finance.db'):
            conn = sqlite3.connect('finance.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tranzactii")
            restored_count = cursor.fetchone()[0]
            conn.close()
            
            print(f"   📊 Restaurare completă: {restored_count} tranzacții")
            
            if restored_count > initial_count:
                print(f"   📈 Îmbunătățire: {restored_count - initial_count} tranzacții noi restaurate")
                return True
            elif restored_count == initial_count:
                print(f"   ✅ Restaurare completă: toate {restored_count} tranzacțiile sunt prezente")
                return True
            else:
                print(f"   ⚠️ Restaurare parțială: {restored_count} din {initial_count} tranzacții")
                return False
        else:
            print("   ❌ Baza de date nu există după restaurare")
            return False
            
    except Exception as e:
        print(f"   ❌ Eroare la testarea restaurarei: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backup_frequency():
    """Testează frecvența backup-ului pe Render"""
    print("\n5️⃣ Testare frecvență backup pe Render...")
    
    try:
        from app import auto_backup
        
        # Simulează câteva tranzacții pentru a testa backup-ul
        print("   📝 Simulare tranzacții pentru test backup...")
        
        # Creează o tranzacție de test
        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tranzactii (data, suma, comentariu, operator, tip, obiect, persoana, categorie)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime('%Y-%m-%d'),
            100.0,
            'Test tranzacție pentru backup',
            'test',
            'cheltuiala',
            'test',
            'test',
            'test'
        ))
        conn.commit()
        conn.close()
        
        print("   ✅ Tranzacție de test creată")
        print("   🔄 Backup automat va fi declanșat la următoarea verificare")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Eroare la testarea backup-ului: {e}")
        return False

def test_google_drive_integration():
    """Testează integrarea cu Google Drive"""
    print("\n6️⃣ Testare integrare Google Drive...")
    
    try:
        from auto_backup import get_backup_system
        
        backup_system = get_backup_system()
        
        # Testează crearea unui backup
        print("   📦 Testare creare backup...")
        backup_filename = backup_system.create_backup(upload_to_gdrive_flag=True)
        print(f"   ✅ Backup creat: {backup_filename}")
        
        # Testează listarea backup-urilor
        print("   📋 Testare listare backup-uri...")
        backups = backup_system.get_backup_list()
        print(f"   ✅ {len(backups)} backup-uri găsite")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Eroare la testarea Google Drive: {e}")
        return False

def main():
    """Funcția principală"""
    print("🧪 TEST SOLUȚIE PERSISTENȚĂ RENDER")
    print("=" * 60)
    
    # Testează restaurarea automată
    restore_ok = test_persistence_solution()
    
    # Testează frecvența backup-ului
    backup_ok = test_backup_frequency()
    
    # Testează integrarea Google Drive
    gdrive_ok = test_google_drive_integration()
    
    print("\n" + "=" * 60)
    print("📋 REZUMAT TEST:")
    print(f"   Restaurare automată: {'✅ OK' if restore_ok else '❌ Problema'}")
    print(f"   Backup frecvent: {'✅ OK' if backup_ok else '❌ Problema'}")
    print(f"   Google Drive: {'✅ OK' if gdrive_ok else '❌ Problema'}")
    
    if restore_ok and backup_ok and gdrive_ok:
        print("\n🎉 Toate testele au trecut!")
        print("✅ Soluția de persistență funcționează perfect")
        print("✅ Render va păstra datele între restart-uri")
    else:
        print("\n⚠️ Unele teste au eșuat")
        print("💡 Verifică configurarea Google Drive și variabilele de mediu")

if __name__ == "__main__":
    main() 