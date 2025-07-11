#!/usr/bin/env python3
"""
Curăță backup-urile cu câmpuri goale
"""

import json
import os
from pathlib import Path
from datetime import datetime

def fix_backup_list():
    """Curăță backup-urile cu câmpuri goale"""
    print("🧹 Curăț backup-uri cu câmpuri goale")
    print("=" * 40)
    
    backup_dir = Path('backups')
    if not backup_dir.exists():
        print("❌ Folderul backups nu există")
        return
    
    fixed_count = 0
    deleted_count = 0
    
    for json_file in backup_dir.glob('finance_backup_*.json'):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                info = json.load(f)
            
            # Verifică dacă backup-ul are câmpuri goale
            needs_fix = False
            
            if not info.get('timestamp'):
                info['timestamp'] = datetime.now().isoformat()
                needs_fix = True
                print(f"✅ Adăugat timestamp pentru {json_file.name}")
            
            if not info.get('size'):
                db_file = json_file.with_suffix('.db')
                if db_file.exists():
                    info['size'] = os.path.getsize(db_file)
                    needs_fix = True
                    print(f"✅ Adăugat size pentru {json_file.name}")
            
            if not info.get('tables'):
                info['tables'] = {'tranzactii': 0, 'obiecte': 0}
                needs_fix = True
                print(f"✅ Adăugat tables pentru {json_file.name}")
            
            if not info.get('source'):
                info['source'] = 'local_backup'
                needs_fix = True
                print(f"✅ Adăugat source pentru {json_file.name}")
            
            # Salvează dacă s-a modificat ceva
            if needs_fix:
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(info, f, indent=2, ensure_ascii=False)
                fixed_count += 1
            
        except Exception as e:
            print(f"❌ Eroare la procesarea {json_file.name}: {e}")
            # Șterge fișierul JSON corupt
            try:
                json_file.unlink()
                db_file = json_file.with_suffix('.db')
                if db_file.exists():
                    db_file.unlink()
                deleted_count += 1
                print(f"🗑️ Șters {json_file.name} (corupt)")
            except Exception as del_e:
                print(f"❌ Nu s-a putut șterge {json_file.name}: {del_e}")
    
    print(f"\n📊 Rezultat:")
    print(f"   - Backup-uri reparate: {fixed_count}")
    print(f"   - Backup-uri șterse: {deleted_count}")
    print(f"   - Total procesate")

if __name__ == "__main__":
    fix_backup_list() 