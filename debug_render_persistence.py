#!/usr/bin/env python3
"""
Debug script pentru persistența datelor pe Render
"""

import os
import sqlite3
from datetime import datetime

def debug_render():
    """Debug mediul Render"""
    print("🔍 DEBUG RENDER")
    print("=" * 50)
    
    is_render = os.environ.get('RENDER', False) or 'render' in os.environ.get('HOSTNAME', '').lower()
    print(f"Pe Render: {is_render}")
    print(f"RENDER env: {os.environ.get('RENDER', 'Not set')}")
    print(f"HOSTNAME: {os.environ.get('HOSTNAME', 'Not set')}")
    
    return is_render

def debug_database():
    """Debug baza de date"""
    print("\n💾 DEBUG BAZĂ DE DATE")
    print("=" * 50)
    
    if os.path.exists('finance.db'):
        print("✅ Baza de date există")
        print(f"Dimensiune: {os.path.getsize('finance.db')} bytes")
        
        try:
            conn = sqlite3.connect('finance.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tranzactii")
            tranzactii = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM obiecte")
            obiecte = cursor.fetchone()[0]
            conn.close()
            
            print(f"Tranzacții: {tranzactii}")
            print(f"Obiecte: {obiecte}")
            return True
        except Exception as e:
            print(f"❌ Eroare: {e}")
            return False
    else:
        print("❌ Baza de date nu există")
        return False

def debug_backups():
    """Debug backup-uri"""
    print("\n📦 DEBUG BACKUP-URI")
    print("=" * 50)
    
    if os.path.exists('backups'):
        files = [f for f in os.listdir('backups') if f.endswith('.db')]
        print(f"Backup-uri găsite: {len(files)}")
        
        for file in files[:3]:
            path = os.path.join('backups', file)
            print(f"  - {file}: {os.path.getsize(path)} bytes")
        
        return len(files) > 0
    else:
        print("❌ Directorul backups nu există")
        return False

def test_restore():
    """Testează restaurarea"""
    print("\n🔄 TEST RESTAURARE")
    print("=" * 50)
    
    try:
        from app import restore_from_latest_backup
        success, message = restore_from_latest_backup()
        print(f"Rezultat: {success}")
        print(f"Mesaj: {message}")
        return success
    except Exception as e:
        print(f"❌ Eroare: {e}")
        return False

def main():
    print("🔧 DEBUG PERSISTENȚĂ")
    print("=" * 50)
    
    render = debug_render()
    db = debug_database()
    backups = debug_backups()
    restore = test_restore()
    
    print(f"\nRezumat:")
    print(f"Render: {render}")
    print(f"Baza de date: {db}")
    print(f"Backup-uri: {backups}")
    print(f"Restaurare: {restore}")

if __name__ == "__main__":
    main() 