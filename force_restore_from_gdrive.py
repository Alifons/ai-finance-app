#!/usr/bin/env python3
"""
Script pentru forțarea restaurarei din Google Drive pe Render
"""

import os
import shutil
import sqlite3
from datetime import datetime

def force_restore_from_gdrive():
    """Forțează restaurarea din Google Drive chiar și dacă există date locale"""
    print("🔄 Forțare restaurare din Google Drive...")
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
        backup_name = f"finance_backup_before_force_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2('finance.db', backup_name)
        print(f"   💾 Copie de siguranță salvată: {backup_name}")
    
    # 3. Forțează restaurarea din Google Drive
    print("\n2️⃣ Forțare restaurare din Google Drive:")
    
    try:
        from app import restore_from_google_drive
        
        # Forțează restaurarea
        success, message = restore_from_google_drive()
        
        if success:
            print(f"   ✅ {message}")
            
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
                elif restored_count == initial_count:
                    print(f"   ✅ Restaurare completă: toate {restored_count} tranzacțiile sunt prezente")
                else:
                    print(f"   ⚠️ Restaurare parțială: {restored_count} din {initial_count} tranzacții")
            else:
                print("   ❌ Baza de date nu există după restaurare")
        else:
            print(f"   ❌ {message}")
            
    except Exception as e:
        print(f"   ❌ Eroare la restaurare: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. Rezumat
    print("\n3️⃣ Rezumat:")
    print("   🎯 Restaurarea forțată din Google Drive completă")
    print("   📊 Verifică dacă datele sunt actualizate")
    print("   🔄 Pentru a testa din nou, rulează acest script din nou")

if __name__ == "__main__":
    force_restore_from_gdrive() 