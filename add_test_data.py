#!/usr/bin/env python3
"""
Script pentru adăugarea de date de test
"""

import sqlite3
from datetime import datetime

def add_test_data():
    """Adaugă date de test în baza de date"""
    print("🧪 Adăugare date de test...")
    
    try:
        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()
        
        # Verifică dacă există deja date
        cursor.execute("SELECT COUNT(*) FROM tranzactii")
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0:
            print(f"⚠️ Baza de date are deja {existing_count} tranzacții")
            response = input("Vrei să adaugi date de test oricum? (y/n): ")
            if response.lower() != 'y':
                print("❌ Operațiune anulată")
                return
        
        # Date de test
        test_transactions = [
            ('2025-07-11', 100.0, 'Salariu valerian', 'valerian', 'venit', 'salariu', 'valerian', 'salariu'),
            ('2025-07-11', 50.0, 'Transport bus', 'victor', 'cheltuiala', 'transport', 'victor', 'transport'),
            ('2025-07-11', 25.0, 'Mâncare prânz', 'valerian', 'cheltuiala', 'mâncare', 'valerian', 'mâncare'),
            ('2025-07-11', 200.0, 'Decontare transport', 'victor', 'venit', 'transport', 'victor', 'transport'),
            ('2025-07-11', 75.0, 'Întreținere mașină', 'valerian', 'cheltuiala', 'întreținere', 'valerian', 'întreținere'),
            ('2025-07-11', 150.0, 'Salariu victor', 'victor', 'venit', 'salariu', 'victor', 'salariu'),
            ('2025-07-11', 30.0, 'Taxe', 'valerian', 'cheltuiala', 'taxe', 'valerian', 'taxe'),
            ('2025-07-11', 45.0, 'Divertisment cinema', 'victor', 'cheltuiala', 'divertisment', 'victor', 'divertisment'),
            ('2025-07-11', 80.0, 'Transfer valerian -> victor', 'valerian', 'transfer', 'transfer', 'victor', 'transfer'),
            ('2025-07-11', 120.0, 'Servicii internet', 'valerian', 'cheltuiala', 'servicii', 'valerian', 'servicii')
        ]
        
        # Adaugă tranzacțiile
        for transaction in test_transactions:
            cursor.execute('''
                INSERT INTO tranzactii (data, suma, comentariu, operator, tip, obiect, persoana, categorie)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', transaction)
        
        conn.commit()
        print(f"✅ Adăugate {len(test_transactions)} tranzacții de test")
        
        # Verifică rezultatul
        cursor.execute("SELECT COUNT(*) FROM tranzactii")
        total_count = cursor.fetchone()[0]
        print(f"📊 Total tranzacții în baza de date: {total_count}")
        
        # Afișează câteva tranzacții
        cursor.execute("SELECT * FROM tranzactii ORDER BY id DESC LIMIT 5")
        recent_transactions = cursor.fetchall()
        
        print("\n📋 Ultimele tranzacții adăugate:")
        for transaction in recent_transactions:
            print(f"   • {transaction[1]} - {transaction[2]} lei - {transaction[3]} ({transaction[4]})")
        
        conn.close()
        print("\n✅ Datele de test au fost adăugate cu succes!")
        
    except Exception as e:
        print(f"❌ Eroare la adăugarea datelor de test: {e}")

def create_backup_after_test():
    """Creează un backup după adăugarea datelor de test"""
    print("\n🔄 Creare backup cu datele de test...")
    
    try:
        from auto_backup import get_backup_system
        backup_system = get_backup_system()
        backup_filename = backup_system.create_backup(upload_to_gdrive_flag=True)
        print(f"✅ Backup creat: {backup_filename}")
    except Exception as e:
        print(f"⚠️ Eroare la crearea backup-ului: {e}")

if __name__ == "__main__":
    add_test_data()
    create_backup_after_test() 