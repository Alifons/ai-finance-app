#!/usr/bin/env python3
"""
Test pentru a verifica dacă aplicația poate porni fără probleme
"""

import os
import sys
import traceback

def test_app_initialization():
    """Testează inițializarea aplicației Flask"""
    print("🚀 Testare inițializare aplicație...")
    
    try:
        # Importează aplicația
        print("📦 Import aplicație...")
        import app
        
        print("✅ Aplicația importată cu succes")
        
        # Verifică dacă aplicația Flask a fost creată
        if hasattr(app, 'app'):
            print("✅ Aplicația Flask găsită")
        else:
            print("❌ Aplicația Flask nu a fost găsită")
            return False
        
        # Verifică dacă baza de date a fost inițializată
        if hasattr(app, 'DATABASE'):
            print(f"✅ Baza de date configurată: {app.DATABASE}")
        else:
            print("❌ Baza de date nu este configurată")
            return False
        
        # Testează funcția init_db
        try:
            app.init_db()
            print("✅ Inițializarea bazei de date reușită")
        except Exception as e:
            print(f"❌ Eroare la inițializarea bazei de date: {e}")
            return False
        
        # Testează funcția get_db
        try:
            conn = app.get_db()
            if conn:
                print("✅ Conexiunea la baza de date funcționează")
                conn.close()
            else:
                print("❌ Nu s-a putut obține conexiunea la baza de date")
                return False
        except Exception as e:
            print(f"❌ Eroare la obținerea conexiunii la baza de date: {e}")
            return False
        
        # Testează auto_backup dacă este disponibil
        if hasattr(app, 'AUTO_BACKUP_AVAILABLE') and app.AUTO_BACKUP_AVAILABLE:
            try:
                backup_system = app.get_backup_system()
                print("✅ Sistemul de backup inițializat")
            except Exception as e:
                print(f"⚠️ Eroare la inițializarea sistemului de backup: {e}")
        else:
            print("ℹ️ Auto backup nu este disponibil")
        
        return True
        
    except Exception as e:
        print(f"❌ Eroare la testarea aplicației: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_render_environment():
    """Testează variabilele de mediu pentru Render"""
    print("\n🔍 Testare variabile de mediu Render...")
    
    # Simulează mediul Render
    os.environ['RENDER'] = 'true'
    os.environ['PORT'] = '10000'
    
    print("✅ Variabile de mediu Render setate")
    
    try:
        # Testează din nou aplicația cu variabilele Render
        import app
        
        print("✅ Aplicația funcționează cu variabilele Render")
        return True
        
    except Exception as e:
        print(f"❌ Eroare cu variabilele Render: {e}")
        return False

def test_google_drive_render():
    """Testează Google Drive cu variabilele Render"""
    print("\n🔍 Testare Google Drive cu Render...")
    
    try:
        # Simulează credențialele din variabilele de mediu
        client_secrets = '{"web": {"client_id": "test", "client_secret": "test"}}'
        token = '{"access_token": "test", "refresh_token": "test"}'
        
        os.environ['GDRIVE_CLIENT_SECRETS'] = client_secrets
        os.environ['GDRIVE_TOKEN'] = token
        
        from auto_backup import gdrive_auth
        
        # Testează autentificarea
        drive = gdrive_auth()
        if drive:
            print("✅ Google Drive funcționează cu variabilele Render")
        else:
            print("⚠️ Google Drive nu funcționează cu variabilele Render")
        
        return True
        
    except Exception as e:
        print(f"❌ Eroare la testarea Google Drive cu Render: {e}")
        return False

def main():
    """Funcția principală"""
    print("🧪 Testare aplicație pentru Render...")
    print("=" * 50)
    
    # Test 1: Aplicația normală
    print("Test 1: Aplicația normală")
    result1 = test_app_initialization()
    
    # Test 2: Cu variabilele Render
    print("\nTest 2: Cu variabilele Render")
    result2 = test_render_environment()
    
    # Test 3: Google Drive cu Render
    print("\nTest 3: Google Drive cu Render")
    result3 = test_google_drive_render()
    
    print("\n" + "=" * 50)
    print("📊 REZULTATE:")
    print("=" * 50)
    
    tests = [
        ("Aplicația normală", result1),
        ("Cu variabilele Render", result2),
        ("Google Drive cu Render", result3)
    ]
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    if all([result1, result2, result3]):
        print("\n✅ Toate testele au trecut!")
        print("💡 Aplicația ar trebui să funcționeze pe Render")
    else:
        print("\n⚠️ Unele teste au eșuat")
        print("💡 Verifică configurația pentru Render")

if __name__ == "__main__":
    main() 