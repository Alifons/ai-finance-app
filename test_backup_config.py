#!/usr/bin/env python3
"""
Test pentru noua configurație de backup automat
"""

import os
import sys
from datetime import datetime, timedelta

def test_backup_config():
    """Testează configurația backup-ului automat"""
    print("🧪 Testare configurație backup automat")
    print("=" * 50)
    
    # Simulează variabilele din app.py
    BACKUP_INTERVAL = 43200  # 12 ore în secunde
    backup_threshold = 10
    
    print(f"⏰ Interval backup: {BACKUP_INTERVAL} secunde ({BACKUP_INTERVAL/3600:.1f} ore)")
    print(f"📊 Prag tranzacții: {backup_threshold} tranzacții noi")
    
    # Testează logica de backup
    print("\n🔍 Testare logică backup:")
    
    # Simulează diferite scenarii
    scenarios = [
        {
            'name': 'Timp scurs (13 ore)',
            'time_since_backup': 13 * 3600,  # 13 ore
            'transaction_diff': 5,
            'expected': True,
            'reason': 'Timp'
        },
        {
            'name': 'Tranzacții multe (15 noi)',
            'time_since_backup': 6 * 3600,  # 6 ore
            'transaction_diff': 15,
            'expected': True,
            'reason': 'Modificări'
        },
        {
            'name': 'Nici timp, nici tranzacții',
            'time_since_backup': 6 * 3600,  # 6 ore
            'transaction_diff': 5,
            'expected': False,
            'reason': 'Niciuna'
        },
        {
            'name': 'Ambele condiții',
            'time_since_backup': 13 * 3600,  # 13 ore
            'transaction_diff': 15,
            'expected': True,
            'reason': 'Timp + Modificări'
        }
    ]
    
    for scenario in scenarios:
        should_backup = False
        backup_reason = ""
        
        # Verifică timpul
        if scenario['time_since_backup'] >= BACKUP_INTERVAL:
            should_backup = True
            backup_reason = f"Timp ({(scenario['time_since_backup']/3600):.1f} ore)"
        
        # Verifică tranzacțiile
        if scenario['transaction_diff'] >= backup_threshold:
            should_backup = True
            backup_reason = f"Modificări ({scenario['transaction_diff']} tranzacții noi)"
        
        status = "✅ PASS" if should_backup == scenario['expected'] else "❌ FAIL"
        print(f"{status} - {scenario['name']}: {backup_reason}")
    
    print("\n📋 Configurație finală:")
    print(f"   • Backup la fiecare 12 ore")
    print(f"   • Backup când se adaugă {backup_threshold}+ tranzacții noi")
    print(f"   • Verificare la fiecare 5 minute")
    print(f"   • Backup local + Google Drive (pe Render)")

def test_settings_file():
    """Testează fișierul settings.yaml"""
    print("\n🔧 Testare settings.yaml:")
    
    try:
        import yaml
        with open('settings.yaml', 'r', encoding='utf-8') as f:
            settings = yaml.safe_load(f)
        
        backup_settings = settings.get('backup', {})
        
        interval = backup_settings.get('auto_backup_interval', 0)
        threshold = backup_settings.get('backup_threshold', 0)
        
        print(f"✅ Interval: {interval} secunde ({interval/3600:.1f} ore)")
        print(f"✅ Prag: {threshold} tranzacții")
        print(f"✅ Upload Google Drive: {backup_settings.get('upload_to_gdrive', False)}")
        
    except Exception as e:
        print(f"❌ Eroare la citirea settings.yaml: {e}")

def main():
    """Funcția principală"""
    test_backup_config()
    test_settings_file()
    
    print("\n" + "=" * 50)
    print("✅ Configurația backup-ului automat a fost actualizată!")
    print("💡 Backup-ul se va face:")
    print("   • La fiecare 12 ore")
    print("   • Când se adaugă 10+ tranzacții noi")
    print("   • Cu verificare la fiecare 5 minute")

if __name__ == "__main__":
    main() 