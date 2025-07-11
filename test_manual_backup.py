#!/usr/bin/env python3
"""
Script pentru testarea backup-ului manual din aplicația web
"""

import requests
import json
from datetime import datetime

def test_manual_backup():
    """Testează backup-ul manual din aplicația web"""
    print("🧪 Testare backup manual din aplicația web")
    print("=" * 50)
    
    # URL-ul aplicației (local sau Render)
    app_url = "http://127.0.0.1:5000"  # Local
    # app_url = "https://ai-finance-app.onrender.com"  # Render
    
    try:
        # Simulează o cerere POST pentru backup manual
        backup_data = {
            'action': 'create'
        }
        
        print(f"🔄 Trimit cerere de backup la {app_url}/backup...")
        
        # Fă cererea POST
        response = requests.post(f"{app_url}/backup", data=backup_data, timeout=30)
        
        if response.status_code == 200:
            print("✅ Cererea de backup a fost procesată cu succes")
            print("📋 Răspunsul aplicației:")
            print(response.text)
        else:
            print(f"❌ Eroare la cererea de backup: {response.status_code}")
            print(f"Răspuns: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Nu s-a putut conecta la aplicație")
        print("Asigură-te că aplicația rulează la http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Eroare: {e}")

def check_backup_status():
    """Verifică statusul backup-urilor"""
    print("\n📊 Status backup-uri:")
    print("=" * 30)
    
    try:
        from auto_backup import get_backup_system
        
        backup_system = get_backup_system()
        backups = backup_system.get_backup_list()
        
        if not backups:
            print("📭 Nu există backup-uri")
            return
        
        # Găsește backup-urile din ultimele 24h
        from datetime import datetime, timedelta
        yesterday = datetime.now() - timedelta(days=1)
        
        recent_backups = []
        for backup in backups:
            created_at = backup.get('created_at', '')
            if created_at:
                try:
                    backup_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    if backup_date > yesterday:
                        recent_backups.append(backup)
                except:
                    pass
        
        print(f"📦 Backup-uri recente (24h): {len(recent_backups)}")
        
        for backup in recent_backups[:3]:  # Primele 3
            filename = backup['filename']
            created_at = backup.get('created_at', 'N/A')
            gdrive_id = backup.get('gdrive_id')
            
            status = "✅ Local + Google Drive" if gdrive_id else "📁 Doar local"
            
            print(f"\n- {filename}")
            print(f"  Creat: {created_at}")
            print(f"  Status: {status}")
            
            if gdrive_id:
                print(f"  Google Drive ID: {gdrive_id}")
        
    except Exception as e:
        print(f"❌ Eroare la verificarea statusului: {e}")

def main():
    """Funcția principală"""
    print("AI Finance App - Test Backup Manual")
    print("=" * 50)
    
    print("📋 Instrucțiuni:")
    print("1. Asigură-te că aplicația rulează (python app.py)")
    print("2. Deschide http://127.0.0.1:5000 în browser")
    print("3. Mergi la pagina /backup")
    print("4. Click 'Create Backup'")
    print("5. Verifică dacă backup-ul apare în lista de backup-uri")
    
    # Testează backup-ul manual
    test_manual_backup()
    
    # Verifică statusul backup-urilor
    check_backup_status()
    
    print("\n🎉 Testul complet!")
    print("✅ Backup-ul manual ar trebui să funcționeze din aplicația web")

if __name__ == "__main__":
    main() 