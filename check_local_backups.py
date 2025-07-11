#!/usr/bin/env python3
"""
Script pentru verificarea backup-urilor locale
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

def check_local_backups():
    """Verifică backup-urile locale"""
    print("📁 Verificare backup-uri locale")
    print("=" * 40)
    
    backup_dir = Path('backups')
    if not backup_dir.exists():
        print("❌ Directorul de backup nu există")
        return False
    
    # Găsește toate backup-urile
    backup_files = list(backup_dir.glob('finance_backup_*.db'))
    
    if not backup_files:
        print("📭 Nu există backup-uri locale")
        return True
    
    print(f"📊 Găsite {len(backup_files)} backup-uri locale:")
    
    # Sortează după data modificării
    backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    for i, backup_file in enumerate(backup_files, 1):
        # Obține informațiile despre backup
        json_file = backup_file.with_suffix('.json')
        info = {}
        
        if json_file.exists():
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    info = json.load(f)
            except:
                pass
        
        # Informații de bază
        file_size = backup_file.stat().st_size
        modified_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
        
        # Informații din JSON
        created_at = info.get('timestamp', info.get('created_at', 'N/A'))
        source = info.get('source', 'local')
        gdrive_id = info.get('gdrive_id', None)
        
        print(f"\n{i}. {backup_file.name}")
        print(f"   Mărime: {file_size} bytes")
        print(f"   Modificat: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Creat: {created_at}")
        print(f"   Sursă: {source}")
        
        if gdrive_id:
            print(f"   Google Drive ID: {gdrive_id}")
            print(f"   Status: ✅ Local + Google Drive")
        else:
            print(f"   Status: 📁 Doar local")

def check_recent_backups():
    """Verifică backup-urile recente (ultimele 24h)"""
    print("\n📅 Backup-uri recente (ultimele 24h):")
    print("=" * 40)
    
    backup_dir = Path('backups')
    if not backup_dir.exists():
        return
    
    yesterday = datetime.now() - timedelta(days=1)
    recent_backups = []
    
    for backup_file in backup_dir.glob('finance_backup_*.db'):
        modified_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
        if modified_time > yesterday:
            recent_backups.append(backup_file)
    
    if not recent_backups:
        print("📭 Nu există backup-uri în ultimele 24h")
        return
    
    print(f"📊 Găsite {len(recent_backups)} backup-uri recente:")
    
    for backup_file in sorted(recent_backups, key=lambda x: x.stat().st_mtime, reverse=True):
        modified_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
        file_size = backup_file.stat().st_size
        
        # Verifică dacă există în Google Drive
        json_file = backup_file.with_suffix('.json')
        gdrive_id = None
        if json_file.exists():
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    info = json.load(f)
                    gdrive_id = info.get('gdrive_id', None)
            except:
                pass
        
        status = "✅ Local + Google Drive" if gdrive_id else "📁 Doar local"
        
        print(f"\n- {backup_file.name}")
        print(f"  Mărime: {file_size} bytes")
        print(f"  Modificat: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Status: {status}")

def check_backup_stats():
    """Statistici despre backup-uri"""
    print("\n📊 Statistici backup-uri:")
    print("=" * 30)
    
    backup_dir = Path('backups')
    if not backup_dir.exists():
        return
    
    backup_files = list(backup_dir.glob('finance_backup_*.db'))
    
    if not backup_files:
        print("📭 Nu există backup-uri")
        return
    
    # Statistici generale
    total_backups = len(backup_files)
    total_size = sum(f.stat().st_size for f in backup_files)
    
    # Backup-uri cu Google Drive
    gdrive_backups = 0
    for backup_file in backup_files:
        json_file = backup_file.with_suffix('.json')
        if json_file.exists():
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    info = json.load(f)
                    if info.get('gdrive_id'):
                        gdrive_backups += 1
            except:
                pass
    
    # Backup-uri recente (ultimele 7 zile)
    week_ago = datetime.now() - timedelta(days=7)
    recent_backups = sum(1 for f in backup_files 
                        if datetime.fromtimestamp(f.stat().st_mtime) > week_ago)
    
    print(f"📦 Total backup-uri: {total_backups}")
    print(f"💾 Mărime totală: {total_size / 1024:.1f} KB")
    print(f"☁️  Backup-uri Google Drive: {gdrive_backups}")
    print(f"📅 Backup-uri recente (7 zile): {recent_backups}")
    
    if total_backups > 0:
        gdrive_percentage = (gdrive_backups / total_backups) * 100
        print(f"📊 Procent Google Drive: {gdrive_percentage:.1f}%")

def main():
    """Funcția principală"""
    print("AI Finance App - Verificare Backup-uri Locale")
    print("=" * 50)
    
    # Verifică backup-urile locale
    check_local_backups()
    
    # Verifică backup-urile recente
    check_recent_backups()
    
    # Statistici
    check_backup_stats()
    
    print("\n🎉 Verificarea completă!")
    print("✅ Backup-urile locale sunt disponibile")
    print("📋 Pentru Google Drive, urmează ghidul din SETUP_GOOGLE_DRIVE.md")

if __name__ == "__main__":
    main() 