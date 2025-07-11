#!/usr/bin/env python3
"""
Testează crearea unui backup nou
"""

import json
import os
from pathlib import Path

def test_backup_creation():
    """Testează crearea unui backup nou"""
    print("🧪 Test creare backup nou")
    print("=" * 40)
    
    # Importă funcția de creare backup
    import sys
    sys.path.append('.')
    
    try:
        from app import create_backup
        
        # Creează un backup
        backup_filename = create_backup(is_auto_backup=False)
        print(f"✅ Backup creat: {backup_filename}")
        
        # Verifică fișierul JSON
        backup_dir = Path('backups')
        json_filename = backup_filename.replace('.db', '.json')
        json_path = backup_dir / json_filename
        
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                info = json.load(f)
            
            print(f"📄 Fișier JSON: {json_filename}")
            print(f"   - filename: {info.get('filename')}")
            print(f"   - created_at: {info.get('created_at')}")
            print(f"   - timestamp: {info.get('timestamp')}")
            print(f"   - size: {info.get('size')}")
            print(f"   - tables: {info.get('tables')}")
            print(f"   - source: {info.get('source')}")
            print(f"   - is_auto_backup: {info.get('is_auto_backup')}")
            
            # Verifică dacă toate câmpurile sunt prezente
            required_fields = ['filename', 'created_at', 'timestamp', 'size', 'tables', 'source']
            missing_fields = [field for field in required_fields if not info.get(field)]
            
            if missing_fields:
                print(f"❌ Câmpuri lipsă: {missing_fields}")
            else:
                print("✅ Toate câmpurile sunt prezente!")
                
        else:
            print(f"❌ Fișierul JSON nu există: {json_path}")
            
    except Exception as e:
        print(f"❌ Eroare la testare: {e}")

if __name__ == "__main__":
    test_backup_creation() 