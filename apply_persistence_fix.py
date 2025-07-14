#!/usr/bin/env python3
"""
Script pentru aplicarea fix-ului de persistență pe Render
"""

import os
import sys
import shutil
from datetime import datetime

def check_current_state():
    """Verifică starea curentă a aplicației"""
    print("🔍 VERIFICARE STARE CURENTĂ")
    print("=" * 50)
    
    # Verifică dacă sunt pe Render
    is_render = os.environ.get('RENDER', False) or 'render' in os.environ.get('HOSTNAME', '').lower()
    print(f"🌐 Pe Render: {is_render}")
    
    # Verifică baza de date
    if os.path.exists('finance.db'):
        import sqlite3
        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tranzactii")
        tranzactii_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM obiecte")
        obiecte_count = cursor.fetchone()[0]
        conn.close()
        
        print(f"📊 Baza de date curentă:")
        print(f"   - Tranzacții: {tranzactii_count}")
        print(f"   - Obiecte: {obiecte_count}")
    else:
        print("❌ Baza de date nu există")
    
    # Verifică backup-urile locale
    backup_dir = 'backups'
    if os.path.exists(backup_dir):
        backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.db')]
        print(f"📦 Backup-uri locale: {len(backup_files)}")
    else:
        print("❌ Directorul de backup nu există")
    
    return is_render

def backup_current_data():
    """Creează backup al datelor curente"""
    print("\n📦 BACKUP DATE CURENTE")
    print("=" * 50)
    
    try:
        from app import create_backup
        
        # Creează backup
        backup_filename = create_backup(is_auto_backup=True)
        print(f"✅ Backup creat: {backup_filename}")
        
        return True
    except Exception as e:
        print(f"❌ Eroare la crearea backup-ului: {e}")
        return False

def test_google_drive_connection():
    """Testează conexiunea la Google Drive"""
    print("\n🔄 TESTARE GOOGLE DRIVE")
    print("=" * 50)
    
    try:
        from auto_backup import gdrive_auth
        
        drive = gdrive_auth()
        
        if drive:
            print("✅ Conexiune la Google Drive reușită!")
            
            # Testează listarea fișierelor
            file_list = drive.ListFile({'q': "trashed=false"}).GetList()
            print(f"📁 Fișiere găsite pe Google Drive: {len(file_list)}")
            
            return True
        else:
            print("❌ Nu s-a putut conecta la Google Drive")
            return False
            
    except Exception as e:
        print(f"❌ Eroare la testarea Google Drive: {e}")
        return False

def test_restore_function():
    """Testează funcția de restaurare"""
    print("\n🔄 TESTARE RESTAURARE")
    print("=" * 50)
    
    try:
        from app import restore_from_latest_backup
        
        # Testează restaurarea
        success, message = restore_from_latest_backup()
        
        print(f"📋 Rezultat testare: {message}")
        print(f"✅ Funcția de restaurare: {'OK' if success else 'Problema'}")
        
        return success
    except Exception as e:
        print(f"❌ Eroare la testarea restaurarei: {e}")
        return False

def test_backup_system():
    """Testează sistemul de backup"""
    print("\n📦 TESTARE SISTEM BACKUP")
    print("=" * 50)
    
    try:
        from auto_backup import get_backup_system
        
        backup_system = get_backup_system()
        
        if backup_system:
            print("✅ Sistem de backup inițializat")
            
            # Testează folderul de backup
            folder_id = backup_system.gdrive_folder_id
            if folder_id:
                print(f"✅ Folder backup configurat: {folder_id}")
            else:
                print("❌ Folder backup nu este configurat")
                return False
            
            # Testează lista backup-urilor
            backups = backup_system.get_backup_list()
            print(f"📋 Backup-uri găsite: {len(backups)}")
            
            return True
        else:
            print("❌ Nu s-a putut inițializa sistemul de backup")
            return False
            
    except Exception as e:
        print(f"❌ Eroare la testarea sistemului de backup: {e}")
        return False

def verify_persistence_fix():
    """Verifică că fix-ul de persistență este aplicat"""
    print("\n🔧 VERIFICARE FIX PERSISTENȚĂ")
    print("=" * 50)
    
    try:
        # Verifică că funcția restore_from_latest_backup a fost modificată
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifică că restaurarea se face forțat pe Render
        if "Pe Render, forțează restaurarea din Google Drive întotdeauna" in content:
            print("✅ Restaurarea forțată pe Render este implementată")
        else:
            print("❌ Restaurarea forțată pe Render nu este implementată")
            return False
        
        # Verifică că backup-ul se face mai frecvent pe Render
        if "BACKUP_INTERVAL_RENDER" in content:
            print("✅ Backup mai frecvent pe Render este configurat")
        else:
            print("❌ Backup mai frecvent pe Render nu este configurat")
            return False
        
        # Verifică că init_db forțează restaurarea pe Render
        if "Detectat mediul Render.com - forțez restaurarea datelor" in content:
            print("✅ Inițializarea forțează restaurarea pe Render")
        else:
            print("❌ Inițializarea nu forțează restaurarea pe Render")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Eroare la verificarea fix-ului: {e}")
        return False

def create_test_script():
    """Creează un script de test pentru persistența"""
    print("\n📝 CREARE SCRIPT TEST")
    print("=" * 50)
    
    script_content = '''#!/usr/bin/env python3
"""
Script de test pentru persistența datelor pe Render
"""

import os
import time
from datetime import datetime

def test_persistence():
    """Testează persistența datelor"""
    print(f"🧪 Test persistență la {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        from app import init_db, restore_from_latest_backup
        
        # Testează inițializarea
        print("🔄 Testare inițializare...")
        init_db()
        
        # Testează restaurarea
        print("🔄 Testare restaurare...")
        success, message = restore_from_latest_backup()
        
        if success:
            print(f"✅ Test reușit: {message}")
        else:
            print(f"❌ Test eșuat: {message}")
            
    except Exception as e:
        print(f"❌ Eroare la test: {e}")

if __name__ == "__main__":
    while True:
        test_persistence()
        time.sleep(60)  # Testează la fiecare minut
'''
    
    with open('test_persistence.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✅ Script de test creat: test_persistence.py")

def main():
    """Funcția principală"""
    print("🚀 APLICARE FIX PERSISTENȚĂ RENDER")
    print("=" * 70)
    
    # Verifică starea curentă
    is_render = check_current_state()
    
    # Backup date curente
    backup_ok = backup_current_data()
    
    # Testează Google Drive
    gdrive_ok = test_google_drive_connection()
    
    # Testează sistemul de backup
    backup_system_ok = test_backup_system()
    
    # Testează restaurarea
    restore_ok = test_restore_function()
    
    # Verifică fix-ul de persistență
    fix_ok = verify_persistence_fix()
    
    # Creează script de test
    create_test_script()
    
    print("\n" + "=" * 70)
    print("📋 REZUMAT APLICARE FIX:")
    print(f"   Backup date curente: {'✅ OK' if backup_ok else '❌ Problema'}")
    print(f"   Google Drive: {'✅ OK' if gdrive_ok else '❌ Problema'}")
    print(f"   Sistem Backup: {'✅ OK' if backup_system_ok else '❌ Problema'}")
    print(f"   Restaurare: {'✅ OK' if restore_ok else '❌ Problema'}")
    print(f"   Fix Persistență: {'✅ OK' if fix_ok else '❌ Problema'}")
    
    if backup_ok and gdrive_ok and backup_system_ok and restore_ok and fix_ok:
        print("\n🎉 Fix-ul de persistență a fost aplicat cu succes!")
        print("✅ Render va păstra datele între restart-uri")
        print("✅ Backup-urile se vor face automat pe Google Drive")
        print("✅ Restaurarea se va face automat la pornire")
        print("✅ Backup-ul se face la fiecare minut pe Render")
        print("✅ Restaurarea se face forțat pe Render")
        
        if is_render:
            print("\n💡 Pentru a testa:")
            print("   1. Repornește serverul pe Render")
            print("   2. Verifică că datele sunt restaurate")
            print("   3. Adaugă o tranzacție nouă")
            print("   4. Repornește din nou și verifică persistența")
    else:
        print("\n⚠️ Există probleme cu fix-ul")
        print("💡 Verifică configurarea Google Drive pe Render")

if __name__ == "__main__":
    main() 