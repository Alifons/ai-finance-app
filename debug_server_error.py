#!/usr/bin/env python3
"""
Debug script pentru a identifica cauza erorii de server
"""

import os
import sys
import traceback

def test_imports():
    """Testează importurile de bază"""
    print("🔍 Testare importuri...")
    
    try:
        import flask
        print("✅ Flask importat cu succes")
    except Exception as e:
        print(f"❌ Eroare la importul Flask: {e}")
        return False
    
    try:
        import sqlite3
        print("✅ SQLite3 importat cu succes")
    except Exception as e:
        print(f"❌ Eroare la importul SQLite3: {e}")
        return False
    
    try:
        import requests
        print("✅ Requests importat cu succes")
    except Exception as e:
        print(f"❌ Eroare la importul Requests: {e}")
        return False
    
    return True

def test_database():
    """Testează baza de date"""
    print("\n🔍 Testare bază de date...")
    
    try:
        import sqlite3
        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()
        
        # Testează dacă tabelele există
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"✅ Tabele găsite: {[table[0] for table in tables]}")
        
        # Testează numărul de înregistrări
        if 'tranzactii' in [table[0] for table in tables]:
            cursor.execute("SELECT COUNT(*) FROM tranzactii")
            count = cursor.fetchone()[0]
            print(f"✅ Tranzacții în baza de date: {count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Eroare la testarea bazei de date: {e}")
        return False

def test_auto_backup():
    """Testează modulul auto_backup"""
    print("\n🔍 Testare auto_backup...")
    
    try:
        from auto_backup import get_backup_system
        print("✅ Import auto_backup cu succes")
        
        backup_system = get_backup_system()
        print("✅ Sistem backup inițializat")
        
        # Testează lista de backup-uri
        backups = backup_system.get_backup_list()
        print(f"✅ Backup-uri găsite: {len(backups)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Eroare la testarea auto_backup: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_flask_app():
    """Testează aplicația Flask"""
    print("\n🔍 Testare aplicație Flask...")
    
    try:
        # Importează doar funcțiile de bază, nu întreaga aplicație
        from flask import Flask
        app = Flask(__name__)
        print("✅ Aplicație Flask creată")
        
        # Testează o rută simplă
        @app.route('/test')
        def test():
            return "OK"
        
        print("✅ Rută de test adăugată")
        return True
        
    except Exception as e:
        print(f"❌ Eroare la testarea Flask: {e}")
        return False

def test_google_drive():
    """Testează configurația Google Drive"""
    print("\n🔍 Testare Google Drive...")
    
    try:
        from auto_backup import gdrive_auth
        
        # Verifică dacă fișierele de credențiale există
        if os.path.exists('client_secrets.json'):
            print("✅ Fișier client_secrets.json găsit")
        else:
            print("⚠️ Fișier client_secrets.json nu există")
        
        if os.path.exists('gdrive_token.json'):
            print("✅ Fișier gdrive_token.json găsit")
        else:
            print("⚠️ Fișier gdrive_token.json nu există")
        
        # Testează autentificarea (doar dacă există credențialele)
        if os.path.exists('client_secrets.json'):
            try:
                drive = gdrive_auth()
                if drive:
                    print("✅ Autentificare Google Drive reușită")
                else:
                    print("⚠️ Autentificare Google Drive eșuată")
            except Exception as e:
                print(f"⚠️ Eroare la autentificarea Google Drive: {e}")
        else:
            print("ℹ️ Google Drive nu este configurat")
        
        return True
        
    except Exception as e:
        print(f"❌ Eroare la testarea Google Drive: {e}")
        return False

def main():
    """Funcția principală de debug"""
    print("🚀 Începe debug-ul aplicației...")
    print("=" * 50)
    
    tests = [
        ("Importuri de bază", test_imports),
        ("Baza de date", test_database),
        ("Auto backup", test_auto_backup),
        ("Aplicație Flask", test_flask_app),
        ("Google Drive", test_google_drive)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Eroare neașteptată în {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 REZULTATE DEBUG:")
    print("=" * 50)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    failed_tests = [name for name, result in results if not result]
    if failed_tests:
        print(f"\n⚠️ Teste eșuate: {', '.join(failed_tests)}")
        print("💡 Acestea pot fi cauza erorii de server")
    else:
        print("\n✅ Toate testele au trecut!")
        print("💡 Problema poate fi în altă parte")

if __name__ == "__main__":
    main() 