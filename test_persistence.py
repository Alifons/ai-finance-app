#!/usr/bin/env python3
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
