#!/usr/bin/env python3
"""
Test pentru persistența datelor în timpul rulării
"""

import os
import sqlite3
import time
from datetime import datetime

def test_data_persistence():
    """Testează persistența datelor"""
    print("🧪 TEST PERSISTENȚĂ DATE")
    print("=" * 50)
    
    db_path = 'finance.db'
    
    # Verifică starea inițială
    print("1️⃣ Verificare stare inițială:")
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tranzactii")
        initial_count = cursor.fetchone()[0]
        conn.close()
        print(f"   Tranzacții existente: {initial_count}")
    else:
        print("   ❌ Baza de date nu există!")
        return False
    
    # Adaugă o tranzacție de test
    print("\n2️⃣ Adăugare tranzacție de test:")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Adaugă tranzacția
        cursor.execute('''
            INSERT INTO tranzactii (data, suma, comentariu, operator, tip, obiect, persoana, categorie)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('2024-12-01', 999.99, 'TEST PERSISTENȚĂ', 'Test', 'cheltuieli', 'test', 'Test', 'test'))
        
        conn.commit()
        conn.close()
        print("   ✅ Tranzacție adăugată")
        
    except Exception as e:
        print(f"   ❌ Eroare la adăugare: {e}")
        return False
    
    # Verifică dacă tranzacția a fost salvată
    print("\n3️⃣ Verificare salvare:")
    time.sleep(1)  # Așteaptă puțin
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tranzactii")
        new_count = cursor.fetchone()[0]
        conn.close()
        
        print(f"   Tranzacții după adăugare: {new_count}")
        
        if new_count > initial_count:
            print("   ✅ Tranzacția a fost salvată!")
        else:
            print("   ❌ Tranzacția nu a fost salvată!")
            return False
            
    except Exception as e:
        print(f"   ❌ Eroare la verificare: {e}")
        return False
    
    # Testează restaurarea din backup
    print("\n4️⃣ Testare restaurare din backup:")
    try:
        from app import restore_from_latest_backup
        
        success, message = restore_from_latest_backup()
        print(f"   Rezultat restaurare: {success}")
        print(f"   Mesaj: {message}")
        
        # Verifică dacă datele persistă după restaurare
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tranzactii")
        final_count = cursor.fetchone()[0]
        conn.close()
        
        print(f"   Tranzacții după restaurare: {final_count}")
        
        if final_count >= new_count:
            print("   ✅ Datele persistă după restaurare!")
        else:
            print("   ❌ Datele se pierd după restaurare!")
            return False
            
    except Exception as e:
        print(f"   ❌ Eroare la restaurare: {e}")
        return False
    
    return True

def test_database_locking():
    """Testează blocarea bazei de date"""
    print("\n🔒 TEST BLOCHARE BAZĂ DE DATE")
    print("=" * 50)
    
    db_path = 'finance.db'
    
    try:
        # Încearcă să deschizi baza de date de mai multe ori
        conn1 = sqlite3.connect(db_path)
        conn2 = sqlite3.connect(db_path)
        
        cursor1 = conn1.cursor()
        cursor2 = conn2.cursor()
        
        # Testează operații simultane
        cursor1.execute("SELECT COUNT(*) FROM tranzactii")
        count1 = cursor1.fetchone()[0]
        
        cursor2.execute("SELECT COUNT(*) FROM tranzactii")
        count2 = cursor2.fetchone()[0]
        
        print(f"   Citire 1: {count1} tranzacții")
        print(f"   Citire 2: {count2} tranzacții")
        
        conn1.close()
        conn2.close()
        
        print("   ✅ Baza de date nu este blocată")
        return True
        
    except Exception as e:
        print(f"   ❌ Eroare la testarea blocării: {e}")
        return False

def test_backup_creation():
    """Testează crearea backup-urilor"""
    print("\n📦 TEST CREARE BACKUP")
    print("=" * 50)
    
    try:
        from app import create_backup
        
        # Creează backup
        backup_filename = create_backup(is_auto_backup=True)
        print(f"   ✅ Backup creat: {backup_filename}")
        
        # Verifică dacă backup-ul există
        backup_path = os.path.join('backups', backup_filename)
        if os.path.exists(backup_path):
            print(f"   ✅ Backup există: {os.path.getsize(backup_path)} bytes")
        else:
            print("   ❌ Backup-ul nu există!")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Eroare la crearea backup-ului: {e}")
        return False

def main():
    """Funcția principală"""
    print("🔧 TEST PERSISTENȚĂ DATE ÎN TIMPUL RULĂRII")
    print("=" * 70)
    
    # Testează persistența datelor
    persistence_ok = test_data_persistence()
    
    # Testează blocarea bazei de date
    locking_ok = test_database_locking()
    
    # Testează crearea backup-urilor
    backup_ok = test_backup_creation()
    
    print("\n" + "=" * 70)
    print("📋 REZUMAT TESTE:")
    print(f"   Persistență date: {'✅ OK' if persistence_ok else '❌ Problema'}")
    print(f"   Blocare bază date: {'✅ OK' if locking_ok else '❌ Problema'}")
    print(f"   Creare backup: {'✅ OK' if backup_ok else '❌ Problema'}")
    
    if persistence_ok and locking_ok and backup_ok:
        print("\n🎉 Toate testele au trecut!")
        print("✅ Datele se salvează corect")
        print("✅ Baza de date nu este blocată")
        print("✅ Backup-urile se creează corect")
    else:
        print("\n⚠️ Există probleme cu persistența datelor")
        print("💡 Verifică permisiunile și configurația bazei de date")

if __name__ == "__main__":
    main() 