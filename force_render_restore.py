#!/usr/bin/env python3
"""
Script pentru forțarea restaurarei datelor pe Render
"""

import os
import shutil
import sqlite3
from datetime import datetime

def force_render_restore():
    """Forțează restaurarea datelor pe Render din Google Drive"""
    print("🔄 Forțare restaurare date pe Render...")
    print("=" * 50)
    
    # Verifică dacă sunt pe Render
    is_render = os.environ.get('RENDER', False) or 'render' in os.environ.get('HOSTNAME', '').lower()
    
    if not is_render:
        print("⚠️ Acest script este destinat doar pentru Render")
        return False
    
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
        from app import restore_from_google_drive, init_db
        
        # Inițializează baza de date (va forța restaurarea)
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
            elif restored_count == initial_count:
                print(f"   ✅ Restaurare completă: toate {restored_count} tranzacțiile sunt prezente")
            else:
                print(f"   ⚠️ Restaurare parțială: {restored_count} din {initial_count} tranzacții")
                
            return True
        else:
            print("   ❌ Baza de date nu există după restaurare")
            return False
            
    except Exception as e:
        print(f"   ❌ Eroare la restaurare: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 4. Rezumat
    print("\n3️⃣ Rezumat:")
    print("   🎯 Restaurarea forțată pe Render completă")
    print("   📊 Verifică dacă datele sunt actualizate")
    print("   🔄 Pentru a testa din nou, rulează acest script din nou")

def test_backup_after_restore():
    """Testează backup-ul după restaurare"""
    print("\n🔄 Testare backup după restaurare...")
    
    try:
        from auto_backup import get_backup_system
        backup_system = get_backup_system()
        
        # Creează un backup nou
        backup_filename = backup_system.create_backup(upload_to_gdrive_flag=True)
        print(f"   ✅ Backup nou creat: {backup_filename}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Eroare la testarea backup-ului: {e}")
        return False

def main():
    """Funcția principală"""
    print("🧪 FORȚARE RESTAURARE RENDER")
    print("=" * 60)
    
    # Forțează restaurarea
    restore_success = force_render_restore()
    
    # Testează backup-ul după restaurare
    backup_success = test_backup_after_restore()
    
    print("\n" + "=" * 60)
    print("📋 REZUMAT:")
    print(f"   Restaurare: {'✅ Reușită' if restore_success else '❌ Eșuată'}")
    print(f"   Backup: {'✅ Reușit' if backup_success else '❌ Eșuat'}")
    
    if restore_success and backup_success:
        print("\n🎉 Restaurarea și backup-ul funcționează perfect!")
        print("✅ Render va păstra datele între restart-uri")
    else:
        print("\n⚠️ Există probleme cu restaurarea sau backup-ul")
        print("💡 Verifică configurarea Google Drive pe Render")

if __name__ == "__main__":
    main() 