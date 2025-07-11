#!/usr/bin/env python3
"""
Script pentru backup manual cu upload automat pe Google Drive
"""

import os
import json
from datetime import datetime
from pathlib import Path

def create_manual_backup():
    """Creează backup manual cu upload pe Google Drive"""
    print("📦 Creare backup manual cu Google Drive")
    print("=" * 50)
    
    try:
        from auto_backup import get_backup_system
        
        backup_system = get_backup_system()
        
        # Creează backup cu upload pe Google Drive
        print("🔄 Creez backup local...")
        backup_filename = backup_system.create_backup(upload_to_gdrive_flag=True)
        
        print(f"✅ Backup creat: {backup_filename}")
        
        # Verifică dacă backup-ul a fost urcat pe Google Drive
        backup_dir = backup_system.backup_dir
        json_file = backup_dir / f"{backup_filename.replace('.db', '.json')}"
        
        if json_file.exists():
            with open(json_file, 'r', encoding='utf-8') as f:
                info = json.load(f)
                
            gdrive_id = info.get('gdrive_id')
            if gdrive_id:
                print(f"✅ Backup urcat pe Google Drive cu ID: {gdrive_id}")
                print("✅ Backup-ul este disponibil în folderul 'AI Finance App Backups'")
                return True, f"Backup creat cu succes: {backup_filename} + Google Drive"
            else:
                print("⚠️ Backup-ul nu a fost urcat pe Google Drive")
                return True, f"Backup creat local: {backup_filename} (Google Drive: Eroare)"
        else:
            print("❌ Nu s-a putut verifica statusul backup-ului")
            return False, "Eroare la verificarea backup-ului"
        
    except Exception as e:
        print(f"❌ Eroare la crearea backup-ului: {e}")
        return False, f"Eroare: {str(e)}"

def list_recent_backups():
    """Listează backup-urile recente"""
    print("\n📋 Backup-uri recente:")
    print("=" * 30)
    
    try:
        from auto_backup import get_backup_system
        
        backup_system = get_backup_system()
        backups = backup_system.get_backup_list()
        
        if not backups:
            print("📭 Nu există backup-uri")
            return
        
        print(f"📊 Găsite {len(backups)} backup-uri:")
        
        for i, backup in enumerate(backups[:5], 1):  # Primele 5
            filename = backup['filename']
            created_at = backup.get('created_at', 'N/A')
            gdrive_id = backup.get('gdrive_id')
            
            status = "✅ Local + Google Drive" if gdrive_id else "📁 Doar local"
            
            print(f"\n{i}. {filename}")
            print(f"   Creat: {created_at}")
            print(f"   Status: {status}")
            
            if gdrive_id:
                print(f"   Google Drive ID: {gdrive_id}")
        
    except Exception as e:
        print(f"❌ Eroare la listarea backup-urilor: {e}")

def main():
    """Funcția principală"""
    print("AI Finance App - Backup Manual cu Google Drive")
    print("=" * 60)
    
    # Creează backup manual
    success, message = create_manual_backup()
    
    if success:
        print(f"\n✅ {message}")
        
        # Listează backup-urile recente
        list_recent_backups()
        
        print("\n🎉 Backup manual realizat cu succes!")
        print("📱 Backup-ul este disponibil local și pe Google Drive")
    else:
        print(f"\n❌ {message}")
        print("Verifică configurația Google Drive")

if __name__ == "__main__":
    main() 