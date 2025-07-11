#!/usr/bin/env python3
"""
Script pentru aplicarea automată a soluției de persistență pe Render
"""

import os
import subprocess
import sys
from datetime import datetime

def check_git_status():
    """Verifică statusul Git"""
    print("🔍 Verificare status Git...")
    print("=" * 50)
    
    try:
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git repository găsit")
            return True
        else:
            print("❌ Nu este un Git repository")
            return False
    except Exception as e:
        print(f"❌ Eroare la verificarea Git: {e}")
        return False

def commit_changes():
    """Comite modificările"""
    print("\n📝 Commit modificări...")
    print("=" * 50)
    
    try:
        # Adaugă toate fișierele
        subprocess.run(['git', 'add', '.'], check=True)
        print("✅ Fișiere adăugate la Git")
        
        # Comite modificările
        commit_message = f"Fix persistență date pe Render - restaurare forțată - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        print(f"✅ Commit creat: {commit_message}")
        
        return True
    except Exception as e:
        print(f"❌ Eroare la commit: {e}")
        return False

def push_changes():
    """Push modificările"""
    print("\n🚀 Push modificări...")
    print("=" * 50)
    
    try:
        subprocess.run(['git', 'push'], check=True)
        print("✅ Modificări push-uite la remote")
        return True
    except Exception as e:
        print(f"❌ Eroare la push: {e}")
        return False

def check_render_environment():
    """Verifică configurarea Render"""
    print("\n🌐 Verificare configurare Render...")
    print("=" * 50)
    
    # Verifică fișierul render.yaml
    if os.path.exists('render.yaml'):
        print("✅ render.yaml găsit")
        
        with open('render.yaml', 'r') as f:
            content = f.read()
            
        required_vars = ['RENDER', 'PERSIST_DATA', 'GOOGLE_DRIVE_ENABLED']
        missing_vars = []
        
        for var in required_vars:
            if var not in content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️ Variabile lipsesc din render.yaml: {', '.join(missing_vars)}")
            return False
        else:
            print("✅ Toate variabilele necesare sunt în render.yaml")
            return True
    else:
        print("❌ render.yaml nu există")
        return False

def create_deployment_script():
    """Creează un script de deployment"""
    print("\n📝 Creare script deployment...")
    print("=" * 50)
    
    script_content = '''#!/bin/bash
# Script pentru deployment automat pe Render

echo "🚀 Deploy pe Render..."

# Verifică Git status
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 Commit modificări..."
    git add .
    git commit -m "Fix persistență date pe Render - $(date)"
fi

# Push la remote
echo "🚀 Push modificări..."
git push

echo "✅ Deploy inițiat!"
echo "📊 Verifică statusul pe Render dashboard"
echo "⏱️ Deploy-ul va dura 2-3 minute"
'''
    
    with open('deploy_render.sh', 'w') as f:
        f.write(script_content)
    
    # Face scriptul executabil
    os.chmod('deploy_render.sh', 0o755)
    
    print("✅ Script deployment creat: deploy_render.sh")

def create_verification_script():
    """Creează un script de verificare"""
    print("\n📝 Creare script verificare...")
    print("=" * 50)
    
    script_content = '''#!/bin/bash
# Script pentru verificarea deployment-ului pe Render

echo "🔍 Verificare deployment Render..."

# Testează soluția local
echo "🧪 Testare soluție local..."
python test_persistence_solution.py

echo ""
echo "📋 Pași pentru verificare pe Render:"
echo "1. Intră pe Render dashboard"
echo "2. Verifică log-urile pentru mesajele:"
echo "   - 'Detectat mediul Render.com - forțez restaurarea din Google Drive...'"
echo "   - 'Date restaurate din Google Drive'"
echo "3. Adaugă câteva tranzacții și verifică că persistă"
echo "4. Așteaptă ca aplicația să intre în sleep mode"
echo "5. Accesează din nou - datele ar trebui să fie acolo!"
'''
    
    with open('verify_deployment.sh', 'w') as f:
        f.write(script_content)
    
    # Face scriptul executabil
    os.chmod('verify_deployment.sh', 0o755)
    
    print("✅ Script verificare creat: verify_deployment.sh")

def main():
    """Funcția principală"""
    print("🚀 APLICARE SOLUȚIE PERSISTENȚĂ RENDER")
    print("=" * 60)
    
    # Verifică Git
    git_ok = check_git_status()
    if not git_ok:
        print("❌ Nu este un Git repository. Inițializează Git înainte de a continua.")
        return
    
    # Verifică configurarea Render
    render_ok = check_render_environment()
    if not render_ok:
        print("⚠️ Configurarea Render nu este completă. Verifică render.yaml")
    
    # Comite modificările
    commit_ok = commit_changes()
    if not commit_ok:
        print("❌ Eroare la commit. Verifică Git status.")
        return
    
    # Push modificările
    push_ok = push_changes()
    if not push_ok:
        print("❌ Eroare la push. Verifică conexiunea la remote.")
        return
    
    # Creează scripturi utile
    create_deployment_script()
    create_verification_script()
    
    print("\n" + "=" * 60)
    print("📋 REZUMAT APLICARE:")
    print(f"   Git repository: {'✅ OK' if git_ok else '❌ Problema'}")
    print(f"   Configurare Render: {'✅ OK' if render_ok else '⚠️ Verifică'}")
    print(f"   Commit modificări: {'✅ OK' if commit_ok else '❌ Problema'}")
    print(f"   Push modificări: {'✅ OK' if push_ok else '❌ Problema'}")
    
    if commit_ok and push_ok:
        print("\n🎉 Soluția a fost aplicată cu succes!")
        print("✅ Modificările au fost push-uite la remote")
        print("✅ Render va detecta automat modificările")
        print("✅ Deploy-ul va începe automat")
        print("\n📋 Pași următori:")
        print("1. Așteaptă 2-3 minute pentru deploy")
        print("2. Verifică log-urile pe Render dashboard")
        print("3. Testează aplicația pentru a verifica persistența")
        print("4. Rulează: ./verify_deployment.sh pentru verificare")
    else:
        print("\n⚠️ Există probleme cu aplicarea soluției")
        print("💡 Verifică Git status și conexiunea la remote")

if __name__ == "__main__":
    main() 