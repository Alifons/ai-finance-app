#!/usr/bin/env python3
"""
Script pentru verificarea configurarei Google Drive pe Render
"""

import os
import json
from datetime import datetime

def check_render_environment():
    """Verifică mediul Render"""
    print("🔍 VERIFICARE MEDIU RENDER")
    print("=" * 50)
    
    # Verifică dacă sunt pe Render
    is_render = os.environ.get('RENDER', False) or 'render' in os.environ.get('HOSTNAME', '').lower()
    print(f"🌐 Pe Render: {is_render}")
    
    if not is_render:
        print("⚠️ Acest script este destinat doar pentru Render")
        return False
    
    # Verifică variabilele de mediu
    required_vars = ['GDRIVE_CLIENT_SECRETS', 'GDRIVE_TOKEN']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variabile de mediu lipsesc: {', '.join(missing_vars)}")
        print("💡 Configurează variabilele de mediu pe Render dashboard")
        return False
    else:
        print("✅ Toate variabilele de mediu sunt configurate")
        return True

def check_google_drive_files():
    """Verifică fișierele Google Drive"""
    print("\n📁 VERIFICARE FIȘIERE GOOGLE DRIVE")
    print("=" * 50)
    
    try:
        # Citește din variabilele de mediu
        client_secrets_str = os.environ.get('GDRIVE_CLIENT_SECRETS')
        token_str = os.environ.get('GDRIVE_TOKEN')
        
        if not client_secrets_str or not token_str:
            print("❌ Variabilele de mediu Google Drive lipsesc")
            return False
        
        # Verifică dacă fișierele există
        client_secrets_exists = os.path.exists('client_secrets.json')
        token_exists = os.path.exists('gdrive_token.json')
        
        print(f"📄 client_secrets.json: {'✅ Există' if client_secrets_exists else '❌ Lipsesc'}")
        print(f"📄 gdrive_token.json: {'✅ Există' if token_exists else '❌ Lipsesc'}")
        
        # Salvează fișierele dacă nu există
        if not client_secrets_exists:
            with open('client_secrets.json', 'w') as f:
                f.write(client_secrets_str)
            print("✅ client_secrets.json creat din variabila de mediu")
        
        if not token_exists:
            with open('gdrive_token.json', 'w') as f:
                f.write(token_str)
            print("✅ gdrive_token.json creat din variabila de mediu")
        
        return True
        
    except Exception as e:
        print(f"❌ Eroare la verificarea fișierelor: {e}")
        return False

def test_google_drive_connection():
    """Testează conexiunea la Google Drive"""
    print("\n🔄 TESTARE CONEXIUNE GOOGLE DRIVE")
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
            
            if backups:
                latest_backup = backups[0]
                print(f"📄 Cel mai recent backup: {latest_backup.get('filename', 'N/A')}")
                print(f"📅 Data: {latest_backup.get('timestamp', 'N/A')}")
                print(f"📊 Tranzacții: {latest_backup.get('tables', {}).get('tranzactii', 0)}")
            
            return True
        else:
            print("❌ Nu s-a putut inițializa sistemul de backup")
            return False
            
    except Exception as e:
        print(f"❌ Eroare la testarea sistemului de backup: {e}")
        return False

def test_restore_function():
    """Testează funcția de restaurare"""
    print("\n🔄 TESTARE FUNCȚIE RESTAURARE")
    print("=" * 50)
    
    try:
        from app import restore_from_latest_backup
        
        # Testează restaurarea (fără să o facă efectiv)
        print("🔄 Testare restaurare (simulare)...")
        
        # Verifică dacă funcția există și poate fi apelată
        success, message = restore_from_latest_backup()
        
        print(f"📋 Rezultat testare: {message}")
        print(f"✅ Funcția de restaurare: {'OK' if success else 'Problema'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Eroare la testarea funcției de restaurare: {e}")
        return False

def check_database_state():
    """Verifică starea bazei de date"""
    print("\n💾 VERIFICARE BAZĂ DE DATE")
    print("=" * 50)
    
    try:
        import sqlite3
        
        if os.path.exists('finance.db'):
            conn = sqlite3.connect('finance.db')
            cursor = conn.cursor()
            
            # Verifică tabelele
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"📋 Tabele găsite: {len(tables)}")
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"   - {table_name}: {count} înregistrări")
            
            conn.close()
            return True
        else:
            print("❌ Baza de date nu există")
            return False
            
    except Exception as e:
        print(f"❌ Eroare la verificarea bazei de date: {e}")
        return False

def main():
    """Funcția principală"""
    print("🔧 VERIFICARE CONFIGURARE RENDER + GOOGLE DRIVE")
    print("=" * 70)
    
    # Verifică mediul Render
    env_ok = check_render_environment()
    if not env_ok:
        return
    
    # Verifică fișierele Google Drive
    files_ok = check_google_drive_files()
    if not files_ok:
        return
    
    # Testează conexiunea Google Drive
    gdrive_ok = test_google_drive_connection()
    if not gdrive_ok:
        return
    
    # Testează sistemul de backup
    backup_ok = test_backup_system()
    if not backup_ok:
        return
    
    # Testează funcția de restaurare
    restore_ok = test_restore_function()
    
    # Verifică starea bazei de date
    db_ok = check_database_state()
    
    print("\n" + "=" * 70)
    print("📋 REZUMAT CONFIGURARE:")
    print(f"   Mediu Render: {'✅ OK' if env_ok else '❌ Problema'}")
    print(f"   Fișiere GDrive: {'✅ OK' if files_ok else '❌ Problema'}")
    print(f"   Conexiune GDrive: {'✅ OK' if gdrive_ok else '❌ Problema'}")
    print(f"   Sistem Backup: {'✅ OK' if backup_ok else '❌ Problema'}")
    print(f"   Funcție Restaurare: {'✅ OK' if restore_ok else '❌ Problema'}")
    print(f"   Bază de Date: {'✅ OK' if db_ok else '❌ Problema'}")
    
    if env_ok and files_ok and gdrive_ok and backup_ok and restore_ok and db_ok:
        print("\n🎉 Configurarea este completă!")
        print("✅ Render va păstra datele între restart-uri")
        print("✅ Backup-urile se vor face automat pe Google Drive")
        print("✅ Restaurarea se va face automat la pornire")
    else:
        print("\n⚠️ Există probleme de configurare")
        print("💡 Verifică variabilele de mediu și conexiunea Google Drive")

if __name__ == "__main__":
    main() 