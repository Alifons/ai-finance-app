#!/usr/bin/env python3
"""
Verifică lista de backup-uri
"""

import os
import json
from pathlib import Path
from datetime import datetime

def check_backup_list():
    """Verifică lista de backup-uri"""
    print("🔍 Verific lista de backup-uri")
    print("=" * 40)
    
    backup_dir = Path('backups')
    if not backup_dir.exists():
        print("❌ Folderul backups nu există")
        return
    
    # Găsește toate fișierele .db
    db_files = list(backup_dir.glob('finance_backup_*.db'))
    print(f"📦 Găsite {len(db_files)} fișiere .db:")
    
    for db_file in db_files:
        print(f"\n📄 {db_file.name}")
        
        # Verifică dacă există fișierul JSON asociat
        json_file = db_file.with_suffix('.json')
        if json_file.exists():
            print(f"   ✅ JSON există: {json_file.name}")
            
            # Încearcă să citească JSON-ul
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    info = json.load(f)
                
                print(f"   📊 Info:")
                print(f"      - Timestamp: {info.get('timestamp', 'N/A')}")
                print(f"      - Size: {info.get('size', 'N/A')}")
                print(f"      - Source: {info.get('source', 'N/A')}")
                print(f"      - GDrive ID: {info.get('gdrive_id', 'N/A')}")
                
                # Verifică tabelele
                tables = info.get('tables', {})
                if tables:
                    print(f"      - Tranzacții: {tables.get('tranzactii', 0)}")
                    print(f"      - Obiecte: {tables.get('obiecte', 0)}")
                
            except Exception as e:
                print(f"   ❌ Eroare la citirea JSON: {e}")
        else:
            print(f"   ❌ JSON NU există pentru {db_file.name}")
    
    # Testează funcția get_backup_list din auto_backup
    print("\n🔄 Testez funcția get_backup_list:")
    try:
        from auto_backup import get_backup_system
        backup_system = get_backup_system()
        backups = backup_system.get_backup_list()
        
        print(f"   📋 Funcția returnează {len(backups)} backup-uri:")
        for backup in backups[:3]:  # Primele 3
            print(f"      - {backup['filename']} ({backup.get('created_at', 'N/A')})")
            
    except Exception as e:
        print(f"   ❌ Eroare la funcția get_backup_list: {e}")

if __name__ == "__main__":
    check_backup_list() 