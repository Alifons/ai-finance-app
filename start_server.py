#!/usr/bin/env python3
"""
Script pentru pornirea serverului local
"""

import subprocess
import sys
import os
from pathlib import Path

def start_server():
    """Pornește serverul local"""
    print("🚀 Pornire server local...")
    print("="*40)
    
    # Verifică dacă suntem în directorul corect
    current_dir = Path.cwd()
    app_file = current_dir / "app.py"
    
    if not app_file.exists():
        print("❌ Fișierul app.py nu a fost găsit!")
        print(f"Director curent: {current_dir}")
        print("Asigură-te că ești în directorul aplicației.")
        return False
    
    print(f"✅ Fișier app.py găsit în: {current_dir}")
    
    try:
        # Pornește serverul
        print("\n🔄 Pornesc serverul...")
        print("Serverul va fi disponibil la: http://127.0.0.1:5000")
        print("Apasă Ctrl+C pentru a opri serverul")
        print("-" * 40)
        
        # Rulează serverul
        result = subprocess.run([sys.executable, "app.py"], 
                              cwd=current_dir,
                              capture_output=False)
        
        if result.returncode == 0:
            print("✅ Serverul s-a oprit normal")
        else:
            print(f"❌ Serverul s-a oprit cu eroarea: {result.returncode}")
            
    except KeyboardInterrupt:
        print("\n⏹️ Serverul a fost oprit de utilizator")
    except Exception as e:
        print(f"❌ Eroare la pornirea serverului: {e}")
        return False
    
    return True

def main():
    """Funcția principală"""
    print("AI Finance App - Server Local")
    print("="*40)
    
    # Verifică dependențele
    print("🔍 Verific dependențele...")
    try:
        import flask
        import sqlite3
        print("✅ Dependențele sunt instalate")
    except ImportError as e:
        print(f"❌ Dependență lipsă: {e}")
        print("Rulează: pip install -r requirements.txt")
        return False
    
    # Pornește serverul
    success = start_server()
    
    if success:
        print("\n✅ Serverul a fost pornit cu succes!")
    else:
        print("\n❌ Nu s-a putut porni serverul!")

if __name__ == "__main__":
    main() 