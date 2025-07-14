#!/usr/bin/env python3
"""
Script pentru forțarea restaurarei datelor pe Render
"""

import os
import sys
import shutil
from datetime import datetime

def force_restore_on_render():
    """Forțează restaurarea datelor pe Render"""
    print("🚀 FORȚARE RESTAURARE PE RENDER")
    print("=" * 50)
    
    # Verifică dacă sunt pe Render
    is_render = os.environ.get('RENDER', False) or 'render' in os.environ.get('HOSTNAME', '').lower()
    
    if not is_render:
        print("⚠️ Acest script este destinat doar pentru Render")
        return False
    
    print("✅ Detectat mediul Render.com")
    
    try:
        # Importă funcțiile necesare
        from app import restore_from_latest_backup, DATABASE
        from auto_backup import get_backup_system
        
        print("🔄 Forțez restaurarea din Google Drive...")
        
        # Forțează restaurarea
        success, message = restore_from_latest_backup()
        
        if success:
            print(f"✅ Restaurare reușită: {message}")
            
            # Verifică datele restaurate
            import sqlite3
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tranzactii")
            tranzactii_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM obiecte")
            obiecte_count = cursor.fetchone()[0]
            conn.close()
            
            print(f"📊 Date restaurate:")
            print(f"   - Tranzacții: {tranzactii_count}")
            print(f"   - Obiecte: {obiecte_count}")
            
            return True
        else:
            print(f"❌ Restaurare eșuată: {message}")
            return False
            
    except Exception as e:
        print(f"❌ Eroare la restaurare: {e}")
        return False

def create_backup_before_restore():
    """Creează un backup înainte de restaurare"""
    print("\n📦 Creare backup înainte de restaurare...")
    
    try:
        from app import create_backup, DATABASE
        
        # Creează backup
        backup_filename = create_backup(is_auto_backup=True)
        print(f"✅ Backup creat: {backup_filename}")
        
        return True
    except Exception as e:
        print(f"⚠️ Eroare la crearea backup-ului: {e}")
        return False

def test_google_drive_connection():
    """Testează conexiunea la Google Drive"""
    print("\n🔄 Testare conexiune Google Drive...")
    
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

def main():
    """Funcția principală"""
    print("🔧 SCRIPT FORȚARE RESTAURARE RENDER")
    print("=" * 60)
    
    # Testează conexiunea Google Drive
    gdrive_ok = test_google_drive_connection()
    
    if not gdrive_ok:
        print("⚠️ Google Drive nu este disponibil")
        print("💡 Verifică variabilele de mediu pe Render")
        return
    
    # Creează backup înainte de restaurare
    backup_ok = create_backup_before_restore()
    
    # Forțează restaurarea
    restore_ok = force_restore_on_render()
    
    print("\n" + "=" * 60)
    print("📋 REZUMAT:")
    print(f"   Google Drive: {'✅ OK' if gdrive_ok else '❌ Problema'}")
    print(f"   Backup pre-restaurare: {'✅ OK' if backup_ok else '❌ Problema'}")
    print(f"   Restaurare forțată: {'✅ OK' if restore_ok else '❌ Problema'}")
    
    if restore_ok:
        print("\n🎉 Restaurarea a fost reușită!")
        print("✅ Datele au fost restaurate din Google Drive")
        print("✅ Aplicația va funcționa cu datele actualizate")
    else:
        print("\n⚠️ Restaurarea a eșuat")
        print("💡 Verifică log-urile pentru detalii")

if __name__ == "__main__":
    main() 