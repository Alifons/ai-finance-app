import os
import sqlite3
import json
import shutil
import io
import csv
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify
from flask_socketio import SocketIO, emit
import threading
import time
import hashlib
import requests
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import secrets

# Import opțional pentru auto_backup
try:
    from auto_backup import get_backup_system, auto_backup_task
    AUTO_BACKUP_AVAILABLE = True
except ImportError:
    AUTO_BACKUP_AVAILABLE = False
    print("⚠️ Auto backup nu este disponibil (lipsește auto_backup.py)")

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

def generate_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(16)
    return session['csrf_token']

def validate_csrf_token():
    if request.method == 'POST':
        token = request.form.get('csrf_token')
        if not token or token != session.get('csrf_token'):
            return False
    return True

DATABASE = 'finance.db'

# Configurare pentru sincronizare
SYNC_INTERVAL = 30  # secunde
BACKUP_INTERVAL = 43200  # secunde (12 ore) - pe local
BACKUP_INTERVAL_RENDER = 60  # secunde (1 minut) - pe Render
SYNC_ENABLED = True  # Activat pentru persistență

# Variabile pentru tracking backup-ului bazat pe modificări
last_backup_time = datetime.now()
last_transaction_count = 0
backup_threshold = 10  # Numărul de tranzacții pentru backup forțat

def get_backup_dir():
    """Creează și returnează directorul pentru backup-uri"""
    backup_dir = os.path.join(os.path.dirname(__file__), 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    return backup_dir

def is_render_environment():
    """Detectează dacă aplicația rulează pe Render"""
    # Multiple metode de detectare pentru Render
    render_indicators = [
        os.environ.get('RENDER', False),
        'render' in os.environ.get('HOSTNAME', '').lower(),
        'render' in os.environ.get('RENDER_EXTERNAL_HOSTNAME', '').lower(),
        'render' in os.environ.get('RENDER_SERVICE_NAME', '').lower(),
        os.environ.get('RENDER_SERVICE_NAME') is not None,
        os.environ.get('RENDER_EXTERNAL_HOSTNAME') is not None,
        os.environ.get('RENDER_SERVICE_ID') is not None,
        os.environ.get('RENDER_INSTANCE_ID') is not None
    ]
    
    is_render = any(render_indicators)
    
    # Debug info
    print(f"🔍 Detectare mediu Render:")
    print(f"   RENDER: {os.environ.get('RENDER', 'Not set')}")
    print(f"   HOSTNAME: {os.environ.get('HOSTNAME', 'Not set')}")
    print(f"   RENDER_EXTERNAL_HOSTNAME: {os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'Not set')}")
    print(f"   RENDER_SERVICE_NAME: {os.environ.get('RENDER_SERVICE_NAME', 'Not set')}")
    print(f"   RENDER_SERVICE_ID: {os.environ.get('RENDER_SERVICE_ID', 'Not set')}")
    print(f"   RENDER_INSTANCE_ID: {os.environ.get('RENDER_INSTANCE_ID', 'Not set')}")
    print(f"   Rezultat detectare: {is_render}")
    
    return is_render

def restore_from_latest_backup():
    """Restaurează datele din cel mai recent backup (local sau Google Drive)"""
    backup_dir = get_backup_dir()
    
    # Verifică dacă sunt pe Render
    is_render = is_render_environment()
    
    # Pe Render, forțează restaurarea din Google Drive întotdeauna
    if is_render and AUTO_BACKUP_AVAILABLE:
        print("🔄 Detectat mediul Render.com - forțez restaurarea din Google Drive...")
        try:
            backup_system = get_backup_system()
            
            # Obține lista backup-urilor din Google Drive
            backups = backup_system.get_backup_list()
            
            if backups:
                # Găsește cel mai recent backup cu Google Drive ID
                gdrive_backups = [b for b in backups if b.get('gdrive_id')]
                if gdrive_backups:
                    latest_gdrive_backup = gdrive_backups[0]
                    
                    # Descarcă backup-ul din Google Drive
                    from auto_backup import gdrive_auth
                    drive = gdrive_auth()
                    
                    # Descarcă fișierul
                    backup_file = drive.CreateFile({'id': latest_gdrive_backup['gdrive_id']})
                    backup_filename = f"gdrive_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                    backup_path = os.path.join(backup_dir, backup_filename)
                    
                    backup_file.GetContentFile(backup_path)
                    
                    # Restaurează din backup-ul descărcat
                    shutil.copy2(backup_path, DATABASE)
                    
                    print(f"✅ Date restaurate din Google Drive: {latest_gdrive_backup['filename']}")
                    return True, f"Date restaurate din Google Drive: {latest_gdrive_backup['filename']}"
                    
        except Exception as e:
            print(f"⚠️ Eroare la restaurare din Google Drive: {e}")
            # Fallback la backup local pe Render
            print("🔄 Încercare fallback la backup local...")
    
    # Încearcă să restaureze din backup local
    if os.path.exists(backup_dir):
        backup_files = []
        for filename in os.listdir(backup_dir):
            if filename.endswith('.db') and filename.startswith('finance_backup_'):
                backup_path = os.path.join(backup_dir, filename)
                backup_files.append((filename, os.path.getctime(backup_path)))
        
        if backup_files:
            # Sortează după data creării (cel mai recent primul)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            latest_backup = backup_files[0][0]
            latest_backup_path = os.path.join(backup_dir, latest_backup)
            
            try:
                # Pe Render, restaurarea se face întotdeauna
                # Pe local, verifică dacă baza de date are deja date
                if not is_render:
                    if os.path.exists(DATABASE):
                        conn = sqlite3.connect(DATABASE)
                        cursor = conn.cursor()
                        cursor.execute("SELECT COUNT(*) FROM tranzactii")
                        current_count = cursor.fetchone()[0]
                        conn.close()
                        
                        # Dacă baza de date are deja date, nu restaura (doar pe local)
                        if current_count > 0:
                            print(f"Baza de date are deja {current_count} tranzacții, nu se restaurează")
                            return True, "Baza de date are deja date"
                
                # Restaurează din backup local
                shutil.copy2(latest_backup_path, DATABASE)
                print(f"✅ Date restaurate din backup local: {latest_backup}")
                return True, f"Date restaurate din backup local: {latest_backup}"
                
            except Exception as e:
                print(f"⚠️ Eroare la restaurare din backup local: {e}")
    
    # Dacă nu există backup local și nu sunt pe Render, încearcă din Google Drive
    if not is_render and AUTO_BACKUP_AVAILABLE:
        try:
            backup_system = get_backup_system()
            
            # Obține lista backup-urilor din Google Drive
            backups = backup_system.get_backup_list()
            
            if backups:
                # Găsește cel mai recent backup cu Google Drive ID
                gdrive_backups = [b for b in backups if b.get('gdrive_id')]
                if gdrive_backups:
                    latest_gdrive_backup = gdrive_backups[0]
                    
                    # Descarcă backup-ul din Google Drive
                    from auto_backup import gdrive_auth
                    drive = gdrive_auth()
                    
                    # Descarcă fișierul
                    backup_file = drive.CreateFile({'id': latest_gdrive_backup['gdrive_id']})
                    backup_filename = f"gdrive_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                    backup_path = os.path.join(backup_dir, backup_filename)
                    
                    backup_file.GetContentFile(backup_path)
                    
                    # Restaurează din backup-ul descărcat
                    shutil.copy2(backup_path, DATABASE)
                    
                    print(f"✅ Date restaurate din Google Drive: {latest_gdrive_backup['filename']}")
                    return True, f"Date restaurate din Google Drive: {latest_gdrive_backup['filename']}"
                    
        except Exception as e:
            print(f"⚠️ Eroare la restaurare din Google Drive: {e}")
    elif is_render:
        print("ℹ️ Google Drive backup nu este disponibil pe Render")
    
    return False, "Nu există backup-uri disponibile (local sau Google Drive)"

def create_backup(is_auto_backup=False):
    """Creează un backup al bazei de date"""
    backup_dir = get_backup_dir()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'finance_backup_{timestamp}.db'
    backup_path = os.path.join(backup_dir, backup_filename)
    
    # Copiază baza de date
    shutil.copy2(DATABASE, backup_path)
    
    # Creează un fișier JSON cu informații despre backup
    if is_auto_backup:
        description = f'Backup automat înainte de restaurare creat la {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    else:
        description = f'Backup manual creat la {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    
    # Obține informații despre backup
    backup_size = os.path.getsize(backup_path)
    
    # Conectează la backup pentru a obține informații despre tabele
    backup_conn = sqlite3.connect(backup_path)
    backup_cursor = backup_conn.cursor()
    
    # Numără înregistrările din tabele
    tranzactii_count = backup_cursor.execute("SELECT COUNT(*) FROM tranzactii").fetchone()[0]
    obiecte_count = backup_cursor.execute("SELECT COUNT(*) FROM obiecte").fetchone()[0]
    backup_conn.close()
    
    backup_info = {
        'filename': backup_filename,
        'created_at': datetime.now().isoformat(),
        'timestamp': datetime.now().isoformat(),
        'size': backup_size,
        'tables': {
            'tranzactii': tranzactii_count,
            'obiecte': obiecte_count
        },
        'source': 'local_backup',
        'original_db': DATABASE,
        'description': description,
        'is_auto_backup': is_auto_backup
    }
    
    info_filename = backup_filename.replace('.db', '.json')
    info_path = os.path.join(backup_dir, info_filename)
    
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(backup_info, f, indent=2, ensure_ascii=False)
    
    return backup_filename

def init_db():
    """Creează tabelele în baza de date dacă nu există și restaurează datele"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Creează tabelul tranzactii
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tranzactii (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            suma REAL NOT NULL,
            comentariu TEXT NOT NULL,
            operator TEXT NOT NULL,
            tip TEXT NOT NULL,
            obiect TEXT NOT NULL,
            persoana TEXT NOT NULL,
            categorie TEXT NOT NULL
        )
    ''')
    
    # Creează tabelul obiecte
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS obiecte (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nume TEXT UNIQUE NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Verifică dacă sunt pe Render
    is_render = is_render_environment()
    
    if is_render:
        print("🔄 Detectat mediul Render.com - forțez restaurarea datelor...")
        success, message = restore_from_latest_backup()
        if success:
            print(f"✅ {message}")
        else:
            print(f"⚠️ {message}")
    else:
        # Pe local, verifică dacă baza de date are date
        has_data = check_database_has_data()
        
        if not has_data:
            print("⚠️ Baza de date este goală - încercare restaurare...")
            success, message = restore_from_latest_backup()
            if success:
                print(f"✅ {message}")
            else:
                print(f"ℹ️ {message}")
        else:
            print("✅ Baza de date are date - nu este necesară restaurarea")
    
    # Adaugă obiecte de bază doar dacă tabelul este gol
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM obiecte")
    if cursor.fetchone()[0] == 0:
        obiecte_baza = [
            'transport', 'mâncare', 'întreținere', 'divertisment', 
            'sănătate', 'educație', 'îmbrăcăminte', 'tehnologie',
            'servicii', 'taxe', 'transfer', 'venit', 'salariu'
        ]
        for obiect in obiecte_baza:
            cursor.execute("INSERT OR IGNORE INTO obiecte (nume) VALUES (?)", (obiect,))
        print("Obiecte de bază adăugate automat")
    else:
        print("Tabelul obiecte nu este gol, nu se adaugă obiecte automat")
    
    conn.commit()
    conn.close()

def check_database_has_data():
    """Verifică dacă baza de date are date"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tranzactii")
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    except Exception as e:
        print(f"⚠️ Eroare la verificarea bazei de date: {e}")
        return False

def get_db():
    # Inițializează baza de date dacă nu există
    init_db()
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    
    # Pe Render, forțează salvarea la fiecare operație
    is_render = is_render_environment()
    if is_render:
        # Activează WAL mode pentru performanță și siguranță
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=MEMORY")
    
    return conn

def get_db_hash():
    """Calculează hash-ul bazei de date pentru detectarea modificărilor"""
    conn = get_db()
    c = conn.cursor()
    
    # Obține toate tranzacțiile pentru hash
    tranzactii = c.execute("SELECT * FROM tranzactii ORDER BY id").fetchall()
    obiecte = c.execute("SELECT * FROM obiecte ORDER BY id").fetchall()
    
    # Creează un string cu toate datele
    data_string = ""
    for row in tranzactii:
        data_string += str(row['id']) + str(row['data']) + str(row['suma']) + str(row['comentariu']) + str(row['operator']) + str(row['tip']) + str(row['obiect']) + str(row['persoana']) + str(row['categorie'])
    
    for row in obiecte:
        data_string += str(row['id']) + str(row['nume'])
    
    # Calculează hash-ul
    return hashlib.md5(data_string.encode()).hexdigest()

def reset_backup_tracking():
    """Resetează tracking-ul pentru backup-ul automat"""
    global last_transaction_count
    try:
        conn = get_db()
        cursor = conn.cursor()
        last_transaction_count = cursor.execute("SELECT COUNT(*) FROM tranzactii").fetchone()[0]
        conn.close()
        print(f"📊 Tracking backup resetat: {last_transaction_count} tranzacții")
    except Exception as e:
        print(f"⚠️ Eroare la resetarea tracking-ului: {e}")

def force_save_on_render():
    """Forțează salvarea datelor pe Render"""
    is_render = is_render_environment()
    if is_render:
        try:
            # Forțează backup după fiecare operație pe Render
            from app import create_backup
            backup_filename = create_backup(is_auto_backup=True)
            print(f"💾 Backup forțat pe Render: {backup_filename}")
            
            # Forțează sincronizarea cu Google Drive dacă este disponibil
            if AUTO_BACKUP_AVAILABLE:
                try:
                    from auto_backup import get_backup_system
                    backup_system = get_backup_system()
                    backup_system.create_backup(upload_to_gdrive_flag=True)
                    print("☁️ Backup Google Drive forțat pe Render")
                except Exception as e:
                    print(f"⚠️ Eroare la backup Google Drive: {e}")
                    
        except Exception as e:
            print(f"⚠️ Eroare la forțarea backup-ului pe Render: {e}")

def auto_backup():
    """Backup automat în background cu Google Drive - la 12 ore pe local, 1 minut pe Render"""
    global last_backup_time, last_transaction_count
    
    while True:
        try:
            if SYNC_ENABLED:
                # Verifică dacă sunt pe Render
                is_render = is_render_environment()
                
                # Alege intervalul de backup în funcție de mediu
                backup_interval = BACKUP_INTERVAL_RENDER if is_render else BACKUP_INTERVAL
                
                # Verifică dacă trebuie să facă backup
                should_backup = False
                backup_reason = ""
                
                # Verifică timpul
                time_since_last_backup = (datetime.now() - last_backup_time).total_seconds()
                if time_since_last_backup >= backup_interval:
                    should_backup = True
                    if is_render:
                        backup_reason = f"Timp ({(time_since_last_backup/60):.1f} minute)"
                    else:
                        backup_reason = f"Timp ({(time_since_last_backup/3600):.1f} ore)"
                
                # Verifică numărul de tranzacții
                try:
                    conn = get_db()
                    cursor = conn.cursor()
                    current_transaction_count = cursor.execute("SELECT COUNT(*) FROM tranzactii").fetchone()[0]
                    conn.close()
                    
                    transaction_diff = current_transaction_count - last_transaction_count
                    if transaction_diff >= backup_threshold:
                        should_backup = True
                        backup_reason = f"Modificări ({transaction_diff} tranzacții noi)"
                    
                except Exception as e:
                    print(f"⚠️ Eroare la verificarea tranzacțiilor: {e}")
                
                # Dacă trebuie să facă backup
                if should_backup:
                    print(f"🔄 Backup automat: {backup_reason}")
                    
                    # Creează backup local
                    if 'create_backup' in globals():
                        create_backup(is_auto_backup=True)
                        print(f"✅ Backup local automat creat la {datetime.now().strftime('%H:%M:%S')}")
                    
                    # Încearcă backup pe Google Drive (doar pe Render și dacă este disponibil)
                    if is_render and AUTO_BACKUP_AVAILABLE:
                        try:
                            backup_system = get_backup_system()
                            backup_system.create_backup(upload_to_gdrive_flag=True)
                            print(f"✅ Backup Google Drive creat la {datetime.now().strftime('%H:%M:%S')}")
                        except Exception as e:
                            print(f"⚠️ Eroare la backup Google Drive: {e}")
                    elif is_render:
                        print(f"ℹ️ Google Drive backup nu este disponibil pe Render")
                    
                    # Actualizează variabilele de tracking
                    last_backup_time = datetime.now()
                    last_transaction_count = current_transaction_count
                    
                    if is_render:
                        print(f"📊 Backup completat. Următorul backup: la 1 minut sau la {backup_threshold} tranzacții noi")
                    else:
                        print(f"📊 Backup completat. Următorul backup: la 12 ore sau la {backup_threshold} tranzacții noi")
                
        except Exception as e:
            print(f"Eroare la backup automat: {e}")
        
        # Așteaptă 5 minute înainte de următoarea verificare
        time.sleep(300)  # 5 minute

def sync_data():
    """Sincronizare automată în background"""
    last_hash = get_db_hash()
    
    while True:
        try:
            if SYNC_ENABLED:
                current_hash = get_db_hash()
                if current_hash != last_hash:
                    # Datele s-au modificat, notifică toți clienții
                    socketio.emit('data_changed', {
                        'timestamp': datetime.now().isoformat(),
                        'hash': current_hash
                    })
                    last_hash = current_hash
                    print(f"Sincronizare la {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"Eroare la sincronizare: {e}")
        
        time.sleep(SYNC_INTERVAL)

# Pornește thread-urile pentru backup și sincronizare
backup_thread = threading.Thread(target=auto_backup, daemon=True)
sync_thread = threading.Thread(target=sync_data, daemon=True)

backup_thread.start()
sync_thread.start()

# WebSocket events
@socketio.on('connect')
def handle_connect():
    print(f"Client conectat: {request.sid}")
    emit('connected', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client deconectat: {request.sid}")

@socketio.on('request_sync')
def handle_sync_request():
    """Trimite datele curente la client"""
    try:
        conn = get_db()
        c = conn.cursor()
        
        # Obține toate datele necesare
        tranzactii = c.execute("SELECT * FROM tranzactii ORDER BY id DESC LIMIT 50").fetchall()
        obiecte = c.execute("SELECT * FROM obiecte ORDER BY id").fetchall()
        
        # Convertește în format JSON
        data = {
            'tranzactii': [dict(row) for row in tranzactii],
            'obiecte': [dict(row) for row in obiecte],
            'hash': get_db_hash(),
            'timestamp': datetime.now().isoformat()
        }
        
        emit('sync_data', data)
        print(f"Date sincronizate pentru client: {request.sid}")
        
    except Exception as e:
        emit('sync_error', {'error': str(e)})
        print(f"Eroare la sincronizare: {e}")

@app.route('/sync/status')
def sync_status():
    """Endpoint pentru verificarea statusului sincronizării"""
    if 'user' not in session:
        return jsonify({'error': 'Nu ești autentificat'})
    
    return jsonify({
        'status': 'online',
        'sync_enabled': SYNC_ENABLED,
        'last_backup': datetime.now().isoformat(),
        'connected_clients': len(socketio.server.manager.rooms),
        'database_hash': get_db_hash()
    })


def classify_entry(comment):
    comment = comment.lower().strip()
    tip = 'cheltuiala'
    persoane = ['valerian', 'victor', 'transport', 'bus']
    categorie = 'alte cheltuieli'
    # preluăm lista reală de obiecte din baza de date
    conn = get_db()
    c = conn.cursor()
    lista_obiecte = [row['nume'] for row in c.execute("SELECT nume FROM obiecte").fetchall()]
    obiect = next((o for o in lista_obiecte if o in comment), 'necunoscut')

    # Dacă există 'salariu' sau 'salariul', e cheltuială
    if 'salariu' in comment or 'salariul' in comment:
        categorie = 'salariu'
        # extrag persoana și obiectul dacă există
        import re
        match = re.match(r"(salariu|salariul)\s+(\w+)(?:\s+(la|pentru)\s+(\w+))?", comment)
        persoana = match.group(2) if match else 'necunoscut'
        if match and match.group(3) and match.group(4):
            obiect = match.group(4)
        return tip, obiect, persoana, categorie

    # Cuvinte cheie pentru venit
    venit_keywords = ['decontare', 'scos bani', 'primit', 'venit', 'am primit']
    for kw in venit_keywords:
        if comment.startswith(kw):
            tip = 'venit'
            rest = comment[len(kw):].strip()
            
            # Încearcă să identifice de la cine este venitul
            persoane_posibile = ['valerian', 'victor', 'transport', 'bus']
            persoana = 'necunoscut'
            
            # Caută persoana în restul comentariului
            for pers in persoane_posibile:
                if pers in rest.lower():
                    persoana = pers
                    break
            
            # Dacă nu găsește persoana, încearcă să extragă din context
            if persoana == 'necunoscut' and rest:
                # Încearcă să găsească un nume după "de la" sau "de la"
                import re
                match = re.search(r'(?:de la|de la)\s+(\w+)', rest.lower())
                if match:
                    persoana = match.group(1)
                else:
                    # Dacă nu găsește, ia primul cuvânt din rest ca persoană
                    words = rest.strip().split()
                    if words:
                        persoana = words[0]
            
            # Determină categoria
            for cat in ['salariu', 'material', 'transport']:
                if cat in comment:
                    categorie = cat
                    break
            
            return tip, obiect, persoana, categorie

    # Reguli speciale pentru Achitat, Avans
    import re
    match = re.match(r"(achitat|avans)\s+(\w+)(?:\s+(la|pentru)\s+(\w+))?", comment)
    if match:
        persoana = match.group(2)
        if match.group(3) and match.group(4):
            obiect = match.group(4)
        categorie = 'salariu'
        return tip, obiect, persoana, categorie

    # Regulă specială pentru "Am primit"
    if comment.startswith('am primit'):
        tip = 'venit'
        rest = comment[10:].strip()  # Elimină "am primit"
        
        # Încearcă să identifice de la cine este venitul
        persoane_posibile = ['valerian', 'victor', 'transport', 'bus']
        persoana = 'necunoscut'
        
        # Caută persoana în restul comentariului
        for pers in persoane_posibile:
            if pers in rest.lower():
                persoana = pers
                break
        
        # Dacă nu găsește persoana, încearcă să extragă din context
        if persoana == 'necunoscut' and rest:
            # Încearcă să găsească un nume după "de la" sau "de la"
            match = re.search(r'(?:de la|de la)\s+(\w+)', rest.lower())
            if match:
                persoana = match.group(1)
            else:
                # Dacă nu găsește, ia primul cuvânt din rest ca persoană
                words = rest.strip().split()
                if words:
                    persoana = words[0]
        
        # Determină categoria
        for cat in ['salariu', 'material', 'transport']:
            if cat in comment:
                categorie = cat
                break
        
        return tip, obiect, persoana, categorie

    # Reguli speciale pentru transport
    match = re.match(r"transport\s+(\w+)", comment)
    if match:
        tip = 'cheltuiala'
        categorie = 'transport'
        persoana = match.group(1)
        return tip, obiect, persoana, categorie

    # fallback vechi
    if any(x in comment for x in ['venit', 'incasare']):
        tip = 'venit'
    persoana = next((p for p in persoane if p in comment), 'necunoscut')
    for cat in ['salariu', 'material', 'transport']:
        if cat in comment:
            categorie = cat
    return tip, obiect, persoana, categorie


def calculeaza_raport():
    conn = get_db()
    c = conn.cursor()

    # Lista completă de operatori cunoscuți
    operatori_cunoscuti = ['valerian', 'victor']

    # Exclude transferurile din calculul total (transferurile se anulează reciproc)
    total_venituri = c.execute("SELECT SUM(suma) FROM tranzactii WHERE tip='venit' AND obiect != 'transfer'").fetchone()[0] or 0
    total_cheltuieli = c.execute("SELECT SUM(suma) FROM tranzactii WHERE tip='cheltuiala' AND obiect != 'transfer'").fetchone()[0] or 0
    balanta = total_venituri - total_cheltuieli

    # Include transferurile în calculul pe operator (pentru sold)
    venituri_op = c.execute("SELECT operator, SUM(suma) FROM tranzactii WHERE tip='venit' GROUP BY operator").fetchall()
    cheltuieli_op = c.execute("SELECT operator, SUM(suma) FROM tranzactii WHERE tip='cheltuiala' GROUP BY operator").fetchall()

    # Transform în dict pentru calcul sold
    venituri_dict = {row['operator']: row['SUM(suma)'] for row in venituri_op}
    cheltuieli_dict = {row['operator']: row['SUM(suma)'] for row in cheltuieli_op}
    
    # Include toți operatorii cunoscuți, chiar dacă nu au tranzacții
    operatori = set(operatori_cunoscuti + list(venituri_dict.keys()) + list(cheltuieli_dict.keys()))
    sold_pe_operator = {op: (venituri_dict.get(op, 0) or 0) - (cheltuieli_dict.get(op, 0) or 0) for op in operatori}

    # Pentru afișare în rapoartele separate, exclude transferurile
    venituri_afisare = c.execute("SELECT operator, SUM(suma) FROM tranzactii WHERE tip='venit' AND obiect != 'transfer' GROUP BY operator").fetchall()
    cheltuieli_afisare = c.execute("SELECT operator, SUM(suma) FROM tranzactii WHERE tip='cheltuiala' AND obiect != 'transfer' GROUP BY operator").fetchall()

    # Transform în dict pentru afișare
    venituri_afisare_dict = {row['operator']: row['SUM(suma)'] for row in venituri_afisare}
    cheltuieli_afisare_dict = {row['operator']: row['SUM(suma)'] for row in cheltuieli_afisare}

    # Creează liste complete pentru venituri și cheltuieli, inclusiv operatorii fără tranzacții
    venituri_complete = []
    for op in operatori:
        suma = venituri_afisare_dict.get(op, 0) or 0
        if suma > 0:  # Include doar operatorii cu venituri
            venituri_complete.append({'operator': op, 'SUM(suma)': suma})
    
    cheltuieli_complete = []
    for op in operatori:
        suma = cheltuieli_afisare_dict.get(op, 0) or 0
        if suma > 0:  # Include doar operatorii cu cheltuieli
            cheltuieli_complete.append({'operator': op, 'SUM(suma)': suma})

    return {
        'total_venituri': total_venituri,
        'total_cheltuieli': total_cheltuieli,
        'balanta': balanta,
        'venituri_pe_operator': venituri_complete,
        'cheltuieli_pe_operator': cheltuieli_complete,
        'sold_pe_operator': sold_pe_operator
    }

def get_backup_list():
    """Returnează lista tuturor backup-urilor disponibile"""
    backup_dir = get_backup_dir()
    backups = []
    
    if os.path.exists(backup_dir):
        for filename in os.listdir(backup_dir):
            if filename.endswith('.db') and filename.startswith('finance_backup_'):
                backup_path = os.path.join(backup_dir, filename)
                info_filename = filename.replace('.db', '.json')
                info_path = os.path.join(backup_dir, info_filename)
                
                backup_info = {
                    'filename': filename,
                    'created_at': datetime.fromtimestamp(os.path.getctime(backup_path)).isoformat(),
                    'size': os.path.getsize(backup_path),
                    'description': f'Backup din {datetime.fromtimestamp(os.path.getctime(backup_path)).strftime("%Y-%m-%d %H:%M:%S")}'
                }
                
                # Încearcă să citească informațiile din JSON
                if os.path.exists(info_path):
                    try:
                        with open(info_path, 'r', encoding='utf-8') as f:
                            json_info = json.load(f)
                            backup_info.update(json_info)
                    except:
                        pass
                
                backups.append(backup_info)
    
    # Sortează după data creării (cel mai recent primul)
    backups.sort(key=lambda x: x['created_at'], reverse=True)
    
    # Șterge backup-urile automate vechi (păstrează doar ultimele 5 backup-uri automate)
    auto_backups = [b for b in backups if b.get('is_auto_backup', False)]
    if len(auto_backups) > 5:
        auto_backups_to_delete = auto_backups[5:]
        for backup in auto_backups_to_delete:
            try:
                backup_path = os.path.join(backup_dir, backup['filename'])
                info_filename = backup['filename'].replace('.db', '.json')
                info_path = os.path.join(backup_dir, info_filename)
                
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                if os.path.exists(info_path):
                    os.remove(info_path)
            except:
                pass
    
    # Șterge backup-urile vechi (păstrează doar ultimele 200 backup-uri manuale)
    manual_backups = [b for b in backups if not b.get('is_auto_backup', False)]
    if len(manual_backups) > 200:
        manual_backups_to_delete = manual_backups[200:]
        for backup in manual_backups_to_delete:
            try:
                backup_path = os.path.join(backup_dir, backup['filename'])
                info_filename = backup['filename'].replace('.db', '.json')
                info_path = os.path.join(backup_dir, info_filename)
                
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                if os.path.exists(info_path):
                    os.remove(info_path)
            except:
                pass
    
    # Reîncarcă lista finală
    backups = [b for b in backups if os.path.exists(os.path.join(backup_dir, b['filename']))]
    
    return backups

def restore_backup(backup_filename):
    """Restaurează baza de date din backup"""
    backup_dir = get_backup_dir()
    backup_path = os.path.join(backup_dir, backup_filename)
    
    if not os.path.exists(backup_path):
        return False, "Backup-ul nu există"
    
    try:
        # Creează un backup al bazei actuale înainte de restaurare
        current_backup = create_backup(is_auto_backup=True)
        
        # Restaurează din backup
        shutil.copy2(backup_path, DATABASE)
        
        return True, f"Restaurare reușită. Backup-ul anterior a fost salvat ca {current_backup}"
    except Exception as e:
        return False, f"Eroare la restaurare: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        # Verifică CSRF token
        if not validate_csrf_token():
            return redirect(url_for('index', error='Eroare de securitate. Încearcă din nou.'))
        
        try:
            suma = float(request.form['suma'])
            comentariu = request.form['comentariu'].strip()
            data = datetime.now().strftime('%Y-%m-%d')
            operator = session['user']

            # Verificare îmbunătățită pentru duplicate
            # Verifică tranzacții similare din ultimele 5 minute
            existing = cursor.execute('''
                SELECT id FROM tranzactii 
                WHERE data=? AND suma=? AND comentariu=? AND operator=? 
                ORDER BY id DESC LIMIT 1
            ''', (data, suma, comentariu, operator)).fetchone()
            
            if existing:
                print(f"Tranzacție duplicată detectată și ignorată: {comentariu}")
                return redirect(url_for('index', error='Această tranzacție a fost deja adăugată!'))

            tip, obiect, persoana, categorie = classify_entry(comentariu)

            cursor.execute('''
                INSERT INTO tranzactii (data, suma, comentariu, operator, tip, obiect, persoana, categorie)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (data, suma, comentariu, operator, tip, obiect, persoana, categorie))
            conn.commit()
            
            # Pe Render, forțează salvarea după fiecare tranzacție
            force_save_on_render()
            
            # Generează un nou CSRF token după fiecare tranzacție
            session['csrf_token'] = secrets.token_hex(16)
            
            return redirect(url_for('index', success='Tranzacție adăugată cu succes!'))
            
        except ValueError:
            return redirect(url_for('index', error='Suma trebuie să fie un număr valid!'))
        except Exception as e:
            print(f"Eroare la adăugarea tranzacției: {e}")
            return redirect(url_for('index', error='Eroare la adăugarea tranzacției!'))

    # Obține doar ultimele 15 tranzacții pentru pagina principală
    tranzactii = cursor.execute('SELECT * FROM tranzactii ORDER BY data DESC, id DESC LIMIT 15').fetchall()
    raport = calculeaza_raport()
    error = request.args.get('error')
    success = request.args.get('success')
    return render_template('index.html', 
                         tranzactii=tranzactii, 
                         user=session['user'], 
                         raport=raport, 
                         error=error,
                         success=success,
                         csrf_token=generate_csrf_token())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username'].lower()
        if user in ['valerian', 'victor']:
            session['user'] = user
            # Adaugă un identificator unic pentru sesiune
            session['session_id'] = str(hash(f"{user}_{datetime.now().timestamp()}"))
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/editare/<int:id>', methods=['GET', 'POST'])
def editare(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    c = conn.cursor()

    # Verifică dacă tranzacția aparține operatorului curent
    tranzactie = c.execute("SELECT * FROM tranzactii WHERE id=?", (id,)).fetchone()
    if not tranzactie:
        return redirect(url_for('index', error='Tranzacția nu există'))
    
    if tranzactie['operator'] != session['user']:
        return redirect(url_for('index', error='Nu poți modifica tranzacții ale altor operatori'))

    if request.method == 'POST':
        suma = float(request.form['suma'])
        comentariu = request.form['comentariu']
        data = datetime.now().strftime('%Y-%m-%d')
        operator = session['user']
        tip, obiect, persoana, categorie = classify_entry(comentariu)

        c.execute('''
            UPDATE tranzactii SET data=?, suma=?, comentariu=?, operator=?, tip=?, obiect=?, persoana=?, categorie=?
            WHERE id=?
        ''', (data, suma, comentariu, operator, tip, obiect, persoana, categorie, id))
        conn.commit()
        
        # Pe Render, forțează salvarea după fiecare editare
        force_save_on_render()
        
        return redirect(url_for('index'))

    return render_template("editare.html", tranzactie=tranzactie)

@app.route('/editare-istoric/<int:id>', methods=['GET', 'POST'])
def editare_istoric(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    c = conn.cursor()

    # Verifică dacă tranzacția aparține operatorului curent
    tranzactie = c.execute("SELECT * FROM tranzactii WHERE id=?", (id,)).fetchone()
    if not tranzactie:
        pagina = request.args.get('page', 1, type=int)
        return redirect(url_for('istoric', page=pagina, error='Tranzacția nu există'))
    
    if tranzactie['operator'] != session['user']:
        pagina = request.args.get('page', 1, type=int)
        return redirect(url_for('istoric', page=pagina, error='Nu poți modifica tranzacții ale altor operatori'))

    if request.method == 'POST':
        suma = float(request.form['suma'])
        comentariu = request.form['comentariu']
        data = datetime.now().strftime('%Y-%m-%d')
        operator = session['user']
        tip, obiect, persoana, categorie = classify_entry(comentariu)

        c.execute('''
            UPDATE tranzactii SET data=?, suma=?, comentariu=?, operator=?, tip=?, obiect=?, persoana=?, categorie=?
            WHERE id=?
        ''', (data, suma, comentariu, operator, tip, obiect, persoana, categorie, id))
        conn.commit()
        
        # Pe Render, forțează salvarea după fiecare editare
        force_save_on_render()
        
        # Redirecționează înapoi în istoric cu pagina curentă
        pagina = request.form.get('page', request.args.get('page', 1, type=int), type=int)
        return redirect(url_for('istoric', page=pagina))

    pagina = request.args.get('page', 1, type=int)
    return render_template("editare.html", tranzactie=tranzactie, pagina=pagina)

@app.route('/sterge/<int:id>', methods=['POST', 'GET'])
def sterge(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    c = conn.cursor()
    
    # Verifică dacă tranzacția aparține operatorului curent
    tranzactie = c.execute("SELECT operator FROM tranzactii WHERE id=?", (id,)).fetchone()
    if not tranzactie:
        return redirect(url_for('index', error='Tranzacția nu există'))
    
    if tranzactie['operator'] != session['user']:
        return redirect(url_for('index', error='Nu poți șterge tranzacții ale altor operatori'))
    
    c.execute("DELETE FROM tranzactii WHERE id=?", (id,))
    conn.commit()
    
    # Pe Render, forțează salvarea după fiecare ștergere
    force_save_on_render()
    
    return redirect(url_for('index'))

@app.route('/sterge-istoric/<int:id>', methods=['POST', 'GET'])
def sterge_istoric(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    c = conn.cursor()
    
    # Verifică dacă tranzacția aparține operatorului curent
    tranzactie = c.execute("SELECT operator FROM tranzactii WHERE id=?", (id,)).fetchone()
    if not tranzactie:
        pagina = request.args.get('page', 1, type=int)
        return redirect(url_for('istoric', page=pagina, error='Tranzacția nu există'))
    
    if tranzactie['operator'] != session['user']:
        pagina = request.args.get('page', 1, type=int)
        return redirect(url_for('istoric', page=pagina, error='Nu poți șterge tranzacții ale altor operatori'))
    
    c.execute("DELETE FROM tranzactii WHERE id=?", (id,))
    conn.commit()
    
    # Pe Render, forțează salvarea după fiecare ștergere
    force_save_on_render()
    
    # Redirecționează înapoi în istoric cu pagina curentă
    pagina = request.args.get('page', 1, type=int)
    return redirect(url_for('istoric', page=pagina))

@app.route('/sterge-multiple', methods=['POST'])
def sterge_multiple():
    if 'user' not in session:
        return {'success': False, 'error': 'Nu ești autentificat'}, 401

    try:
        data = request.get_json()
        ids = data.get('ids', [])
        
        if not ids:
            return {'success': False, 'error': 'Nu au fost furnizate ID-uri'}

        conn = get_db()
        c = conn.cursor()
        
        # Verifică dacă toate tranzacțiile aparțin operatorului curent
        placeholders = ','.join(['?' for _ in ids])
        tranzactii = c.execute(f"SELECT id, operator FROM tranzactii WHERE id IN ({placeholders})", ids).fetchall()
        
        # Filtrează doar tranzacțiile care aparțin operatorului curent
        tranzactii_permise = [t['id'] for t in tranzactii if t['operator'] == session['user']]
        
        if not tranzactii_permise:
            return {'success': False, 'error': 'Nu ai permisiunea să ștergi aceste tranzacții'}
        
        # Șterge doar tranzacțiile permise
        placeholders_permise = ','.join(['?' for _ in tranzactii_permise])
        c.execute(f"DELETE FROM tranzactii WHERE id IN ({placeholders_permise})", tranzactii_permise)
        conn.commit()
        
        # Pe Render, forțează salvarea după ștergerea multiplă
        force_save_on_render()
        
        deleted_count = c.rowcount
        
        return {
            'success': True, 
            'deleted_count': deleted_count,
            'message': f'Șterse cu succes {deleted_count} tranzacții'
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.route('/obiecte', methods=['GET', 'POST'])
def obiecte():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    c = conn.cursor()

    if request.method == 'POST':
        nume = request.form['nume'].strip().lower()
        if nume:
            try:
                # Verifică dacă obiectul există deja
                existing = c.execute("SELECT id FROM obiecte WHERE nume=?", (nume,)).fetchone()
                if existing:
                    return render_template("obiecte.html", obiecte=c.execute("SELECT * FROM obiecte").fetchall(), 
                                        error=f"Obiectul '{nume}' există deja!")
                
                c.execute("INSERT INTO obiecte (nume) VALUES (?)", (nume,))
                conn.commit()
                
                # Pe Render, forțează salvarea după adăugarea obiectului
                force_save_on_render()
                
                return render_template("obiecte.html", obiecte=c.execute("SELECT * FROM obiecte").fetchall(), 
                                    success=f"Obiectul '{nume}' a fost adăugat cu succes!")
            except Exception as e:
                print(f"Eroare la adăugarea obiectului: {e}")
                return render_template("obiecte.html", obiecte=c.execute("SELECT * FROM obiecte").fetchall(), 
                                    error=f"Eroare la adăugarea obiectului: {str(e)}")
        else:
            return render_template("obiecte.html", obiecte=c.execute("SELECT * FROM obiecte").fetchall(), 
                                error="Denumirea obiectului nu poate fi goală!")

    lista = c.execute("SELECT * FROM obiecte").fetchall()
    error = request.args.get('error')
    success = request.args.get('success')
    return render_template("obiecte.html", obiecte=lista, error=error, success=success)

@app.route('/obiect/<nume>')
def obiect_detalii(nume):
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    c = conn.cursor()
    cheltuieli = c.execute("SELECT * FROM tranzactii WHERE tip='cheltuiala' AND obiect=? ORDER BY data DESC", (nume,)).fetchall()
    suma_totala = sum(row['suma'] for row in cheltuieli)
    return render_template('obiect_detalii.html', nume=nume, cheltuieli=cheltuieli, suma_totala=suma_totala)

@app.route('/venituri')
def lista_venituri():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    c = conn.cursor()
    
    # Obține toate veniturile grupate pe operatori (exclude transferurile)
    venituri_pe_operator = {}
    venituri_totale = c.execute("SELECT * FROM tranzactii WHERE tip='venit' AND obiect != 'transfer' ORDER BY data DESC").fetchall()
    
    for venit in venituri_totale:
        operator = venit['operator']
        if operator not in venituri_pe_operator:
            venituri_pe_operator[operator] = []
        venituri_pe_operator[operator].append(venit)
    
    # Calculează suma totală
    suma_totala = sum(row['suma'] for row in venituri_totale)
    
    return render_template('venituri.html', venituri_pe_operator=venituri_pe_operator, suma_totala=suma_totala)

@app.route('/venituri/<operator>')
def venituri_operator(operator):
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    c = conn.cursor()
    venituri = c.execute("SELECT * FROM tranzactii WHERE tip='venit' AND operator=? AND obiect != 'transfer' ORDER BY data DESC", (operator,)).fetchall()
    suma_totala = sum(row['suma'] for row in venituri)
    return render_template('venituri.html', venituri=venituri, suma_totala=suma_totala, operator=operator)

@app.route('/agent', methods=['GET', 'POST'])
def agent():
    raspuns = ""
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        intrebare = request.form['intrebare'].lower()
        conn = get_db()
        c = conn.cursor()

        persoana = ""
        obiect = ""
        actiune = ""

        if "pavel" in intrebare:
            persoana = "pavel"
        elif "garstea" in intrebare:
            persoana = "garstea"
        elif "mihai" in intrebare:
            persoana = "mihai"

        if "colonita" in intrebare:
            obiect = "colonita"
        elif "durlesti" in intrebare:
            obiect = "durlesti"
        elif "bubuieci" in intrebare:
            obiect = "bubuieci"

        if "cheltuieli" in intrebare or "cheltuit" in intrebare:
            actiune = "cheltuiala"
        elif "venituri" in intrebare or "incasari" in intrebare:
            actiune = "venit"
        elif "balanta" in intrebare or "sold" in intrebare:
            actiune = "balanta"

        if actiune == "cheltuiala" and persoana:
            suma = c.execute("SELECT SUM(suma) FROM tranzactii WHERE tip='cheltuiala' AND persoana=?", (persoana,)).fetchone()[0] or 0
            raspuns = f"Cheltuielile pentru {persoana.capitalize()} sunt {suma} lei."

        elif actiune == "cheltuiala" and obiect:
            suma = c.execute("SELECT SUM(suma) FROM tranzactii WHERE tip='cheltuiala' AND obiect=?", (obiect,)).fetchone()[0] or 0
            raspuns = f"Cheltuielile pentru obiectul {obiect.capitalize()} sunt {suma} lei."

        elif actiune == "venit":
            operator = session['user']
            suma = c.execute("SELECT SUM(suma) FROM tranzactii WHERE tip='venit' AND operator=? AND obiect != 'transfer'", (operator,)).fetchone()[0] or 0
            raspuns = f"Veniturile tale ({operator}) sunt {suma} lei."

        elif actiune == "balanta":
            venituri = c.execute("SELECT SUM(suma) FROM tranzactii WHERE tip='venit' AND obiect != 'transfer'").fetchone()[0] or 0
            cheltuieli = c.execute("SELECT SUM(suma) FROM tranzactii WHERE tip='cheltuiala' AND obiect != 'transfer'").fetchone()[0] or 0
            raspuns = f"Balanța totală este {venituri - cheltuieli} lei."

        else:
            raspuns = "Încă nu înțeleg întrebarea. Încearcă să folosești cuvinte cheie."

    return render_template("agent.html", raspuns=raspuns)

@app.route('/export/csv')
def export_csv():
    conn = get_db()
    c = conn.cursor()
    tranzactii = c.execute('SELECT * FROM tranzactii ORDER BY data DESC').fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(tranzactii[0].keys() if tranzactii else [])
    for row in tranzactii:
        writer.writerow([row[k] for k in row.keys()])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='tranzactii.csv')

@app.route('/export/excel')
def export_excel():
    try:
        import pandas as pd
    except ImportError:
        return 'Pandas nu este instalat', 500
    
    conn = get_db()
    c = conn.cursor()
    
    # Toate tranzacțiile
    tranzactii = c.execute('SELECT * FROM tranzactii ORDER BY data DESC').fetchall()
    df_tranzactii = pd.DataFrame([dict(row) for row in tranzactii])
    
    # Obține lista obiectelor
    obiecte = c.execute('SELECT * FROM obiecte ORDER BY nume').fetchall()
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Foaia 1: Toate tranzacțiile
        df_tranzactii.to_excel(writer, sheet_name='Toate Tranzacțiile', index=False)
        
        # Foi separate pentru fiecare obiect
        for obiect in obiecte:
            nume_obiect = obiect['nume']
            # Tranzacții pentru acest obiect
            tranzactii_obiect = c.execute('''
                SELECT * FROM tranzactii 
                WHERE obiect = ? 
                ORDER BY data DESC
            ''', (nume_obiect,)).fetchall()
            
            if tranzactii_obiect:  # Doar dacă există tranzacții pentru acest obiect
                df_obiect = pd.DataFrame([dict(row) for row in tranzactii_obiect])
                # Numele foii nu poate conține caractere speciale
                sheet_name = f'Obiect_{nume_obiect}'[:31]  # Excel limitează la 31 caractere
                df_obiect.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Foaia pentru obiecte fără tranzacții
        obiecte_fara_tranzactii = []
        for obiect in obiecte:
            nume_obiect = obiect['nume']
            count = c.execute('SELECT COUNT(*) FROM tranzactii WHERE obiect = ?', (nume_obiect,)).fetchone()[0]
            if count == 0:
                obiecte_fara_tranzactii.append({
                    'nume_obiect': nume_obiect,
                    'tranzactii': 0,
                    'status': 'Fără tranzacții'
                })
        
        if obiecte_fara_tranzactii:
            df_fara_tranzactii = pd.DataFrame(obiecte_fara_tranzactii)
            df_fara_tranzactii.to_excel(writer, sheet_name='Obiecte Fără Tranzacții', index=False)
    
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='tranzactii_complete.xlsx')

@app.route('/export/pdf')
def export_pdf():
    try:
        from fpdf import FPDF
    except ImportError:
        return 'FPDF nu este instalat', 500
    conn = get_db()
    c = conn.cursor()
    tranzactii = c.execute('SELECT * FROM tranzactii ORDER BY data DESC').fetchall()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 10)
    # Header
    if tranzactii:
        for col in tranzactii[0].keys():
            pdf.cell(25, 8, str(col), 1)
        pdf.ln()
        pdf.set_font('Arial', '', 8)
        for row in tranzactii:
            for val in row:
                pdf.cell(25, 8, str(val), 1)
            pdf.ln()
    else:
        pdf.cell(40, 10, 'Nu există tranzacții.')
    output = io.BytesIO()
    pdf.output(output)
    output.seek(0)
    return send_file(output, mimetype='application/pdf', as_attachment=True, download_name='tranzactii.pdf')

@app.route('/api/export')
def export_json():
    """Export JSON pentru sincronizare cu aplicația locală"""
    conn = get_db()
    c = conn.cursor()
    
    # Obține toate tranzacțiile
    tranzactii = c.execute('SELECT * FROM tranzactii ORDER BY data DESC').fetchall()
    tranzactii_list = [dict(row) for row in tranzactii]
    
    # Obține toate obiectele
    obiecte = c.execute('SELECT * FROM obiecte ORDER BY nume').fetchall()
    obiecte_list = [dict(row) for row in obiecte]
    
    # Creează răspunsul JSON
    response_data = {
        'tranzactii': tranzactii_list,
        'obiecte': obiecte_list,
        'export_date': datetime.now().isoformat(),
        'total_tranzactii': len(tranzactii_list),
        'total_obiecte': len(obiecte_list)
    }
    
    return jsonify(response_data)

@app.route('/api/import', methods=['POST'])
def import_json():
    """Importă datele din format JSON"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Nu s-au primit date'})
        
        conn = get_db()
        cursor = conn.cursor()
        
        tranzactii_importate = 0
        obiecte_importate = 0
        
        # Importă obiectele
        if 'obiecte' in data:
            for obiect in data['obiecte']:
                try:
                    cursor.execute("INSERT OR IGNORE INTO obiecte (id, nume) VALUES (?, ?)", 
                                 (obiect['id'], obiect['nume']))
                    obiecte_importate += 1
                except Exception as e:
                    print(f"Eroare la import obiect {obiect['nume']}: {e}")
        
        # Importă tranzacțiile
        if 'tranzactii' in data:
            for tranzactie in data['tranzactii']:
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO tranzactii 
                        (id, data, suma, comentariu, operator, tip, obiect, persoana, categorie)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        tranzactie['id'],
                        tranzactie['data'],
                        tranzactie['suma'],
                        tranzactie['comentariu'],
                        tranzactie['operator'],
                        tranzactie['tip'],
                        tranzactie['obiect'],
                        tranzactie['persoana'],
                        tranzactie['categorie']
                    ))
                    tranzactii_importate += 1
                except Exception as e:
                    print(f"Eroare la import tranzacție {tranzactie['id']}: {e}")
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'tranzactii_importate': tranzactii_importate,
            'obiecte_importate': obiecte_importate,
            'imported_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/istoric')
def istoric():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Parametri de paginare
    pagina = request.args.get('page', 1, type=int)
    tranzactii_per_pagina = 50
    offset = (pagina - 1) * tranzactii_per_pagina
    
    conn = get_db()
    c = conn.cursor()
    
    # Numărul total de tranzacții
    total_tranzactii = c.execute("SELECT COUNT(*) FROM tranzactii").fetchone()[0]
    total_pagini = (total_tranzactii + tranzactii_per_pagina - 1) // tranzactii_per_pagina
    
    # Obține tranzacțiile pentru pagina curentă
    tranzactii = c.execute("""
        SELECT * FROM tranzactii 
        ORDER BY data DESC, id DESC 
        LIMIT ? OFFSET ?
    """, (tranzactii_per_pagina, offset)).fetchall()
    
    error = request.args.get('error')
    return render_template('istoric.html', 
                         tranzactii=tranzactii, 
                         pagina_curenta=pagina,
                         total_pagini=total_pagini,
                         tranzactii_per_pagina=tranzactii_per_pagina,
                         total_tranzactii=total_tranzactii,
                         user=session['user'],
                         error=error)

@app.route('/obiecte/sterge/<int:id>', methods=['POST', 'GET'])
def sterge_obiect(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    try:
        conn = get_db()
        c = conn.cursor()
        
        # Verifică dacă obiectul există
        obiect = c.execute("SELECT * FROM obiecte WHERE id=?", (id,)).fetchone()
        if not obiect:
            return redirect(url_for('obiecte', error='Obiectul nu există!'))
        
        # Verifică dacă obiectul este folosit în tranzacții
        tranzactii_count = c.execute("SELECT COUNT(*) FROM tranzactii WHERE obiect=?", (obiect['nume'],)).fetchone()[0]
        if tranzactii_count > 0:
            return redirect(url_for('obiecte', error=f'Nu poți șterge obiectul "{obiect["nume"]}" deoarece este folosit în {tranzactii_count} tranzacții!'))
        
        # Șterge obiectul
        c.execute("DELETE FROM obiecte WHERE id=?", (id,))
        conn.commit()
        
        return redirect(url_for('obiecte', success=f'Obiectul "{obiect["nume"]}" a fost șters cu succes!'))
        
    except Exception as e:
        print(f"Eroare la ștergerea obiectului: {e}")
        return redirect(url_for('obiecte', error=f'Eroare la ștergerea obiectului: {str(e)}'))

@app.route('/obiecte/modifica/<int:id>', methods=['GET', 'POST'])
def modifica_obiect(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    c = conn.cursor()
    
    # Verifică dacă obiectul există
    obiect = c.execute("SELECT * FROM obiecte WHERE id=?", (id,)).fetchone()
    if not obiect:
        return redirect(url_for('obiecte'))
    
    if request.method == 'POST':
        nume_nou = request.form['nume'].strip().lower()
        if nume_nou:
            try:
                # Verifică dacă numele nou nu există deja (excluzând obiectul curent)
                existing = c.execute("SELECT id FROM obiecte WHERE nume=? AND id!=?", (nume_nou, id)).fetchone()
                if existing:
                    print(f"Numele '{nume_nou}' există deja")
                    return render_template('editare_obiect.html', obiect=obiect, error="Această denumire există deja!")
                
                c.execute("UPDATE obiecte SET nume=? WHERE id=?", (nume_nou, id))
                conn.commit()
                print(f"Obiect modificat: ID={id}, nume nou={nume_nou}")
                return redirect(url_for('obiecte'))
            except Exception as e:
                print(f"Eroare la modificarea obiectului: {e}")
                conn.rollback()
                return render_template('editare_obiect.html', obiect=obiect, error=f"Eroare la salvarea modificărilor: {str(e)}")
        else:
            print("Numele obiectului este gol")
            return render_template('editare_obiect.html', obiect=obiect, error="Denumirea obiectului nu poate fi goală!")
    
    return render_template('editare_obiect.html', obiect=obiect)

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        suma = float(request.form['suma'])
        operator_from = request.form['operator_from']
        operator_to = request.form['operator_to']
        comentariu = request.form['comentariu']
        data = datetime.now().strftime('%Y-%m-%d')
        
        # Verifică că operatorul logat este cel care transferă
        if operator_from != session['user']:
            return redirect(url_for('transfer', error='Poți transfera doar din contul tău!'))
        
        if operator_from == operator_to:
            return redirect(url_for('transfer', error='Nu poți transfera bani către același operator'))
        
        if suma <= 0:
            return redirect(url_for('transfer', error='Suma trebuie să fie mai mare decât 0'))
        
        conn = get_db()
        c = conn.cursor()
        
        try:
            # Creează două tranzacții: o cheltuială pentru operatorul care transferă și un venit pentru cel care primește
            comentariu_from = f"Transfer către {operator_to}: {comentariu}"
            comentariu_to = f"Transfer de la {operator_from}: {comentariu}"
            
            # Tranzacție pentru operatorul care transferă (cheltuială)
            tip_from, obiect_from, persoana_from, categorie_from = classify_entry(comentariu_from)
            c.execute('''
                INSERT INTO tranzactii (data, suma, comentariu, operator, tip, obiect, persoana, categorie)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (data, suma, comentariu_from, operator_from, 'cheltuiala', 'transfer', operator_to, 'transfer'))
            
            # Tranzacție pentru operatorul care primește (venit)
            tip_to, obiect_to, persoana_to, categorie_to = classify_entry(comentariu_to)
            c.execute('''
                INSERT INTO tranzactii (data, suma, comentariu, operator, tip, obiect, persoana, categorie)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (data, suma, comentariu_to, operator_to, 'venit', 'transfer', operator_from, 'transfer'))
            
            conn.commit()
            return redirect(url_for('transfer', success=f'Transfer realizat cu succes: {suma} lei de la {operator_from} către {operator_to}'))
            
        except Exception as e:
            conn.rollback()
            return redirect(url_for('transfer', error=f'Eroare la transfer: {str(e)}'))
    
    # Obține lista operatorilor pentru dropdown
    conn = get_db()
    c = conn.cursor()
    
    # Lista completă de operatori cunoscuți
    operatori_cunoscuti = ['valerian', 'victor']
    
    # Obține operatorii din baza de date
    operatori_db = c.execute("SELECT DISTINCT operator FROM tranzactii ORDER BY operator").fetchall()
    operatori_db = [op['operator'] for op in operatori_db]
    
    # Combină operatorii din baza de date cu cei cunoscuți
    operatori = list(set(operatori_cunoscuti + operatori_db))
    operatori.sort()  # Sortează alfabetic
    
    return render_template('transfer.html', operatori=operatori, user=session['user'])

@app.route('/backup', methods=['GET', 'POST'])
def backup():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Verifică dacă Google Drive este disponibil
    if not AUTO_BACKUP_AVAILABLE:
        return render_template('backup.html', 
                             backups=[], 
                             gdrive_info={'error': 'Google Drive nu este configurat. Funcționalitatea de backup Google Drive nu este disponibilă pe acest server.'})
    
    try:
        backup_system = get_backup_system()
    except Exception as e:
        print(f"DEBUG: Eroare la inițializarea sistemului de backup: {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template('backup.html', 
                             backups=[], 
                             gdrive_info={'error': f'Eroare la inițializarea sistemului de backup: {str(e)}'})
    
    try:
        if request.method == 'POST':
            action = request.form.get('action')
            
            if action == 'create':
                try:
                    backup_filename = backup_system.create_backup(upload_to_gdrive_flag=True)
                    gdrive_status = ""
                    try:
                        backup_dir = backup_system.backup_dir
                        json_file = backup_dir / f"{backup_filename.replace('.db', '.json')}"
                        if json_file.exists():
                            with open(json_file, 'r', encoding='utf-8') as f:
                                info = json.load(f)
                            if info.get('gdrive_id'):
                                gdrive_status = " + Google Drive"
                            else:
                                gdrive_status = " (Google Drive: Eroare)"
                        else:
                            gdrive_status = " (Google Drive: Eroare)"
                    except Exception as e:
                        gdrive_status = f" (Google Drive: {str(e)})"
                    return redirect(url_for('backup', success=f'Backup creat cu succes: {backup_filename}{gdrive_status}'))
                except Exception as e:
                    return render_template('backup.html', backups=[], gdrive_info={'error': f'Eroare la crearea backup-ului: {str(e)}'})
            
            elif action == 'restore':
                backup_filename = request.form.get('backup_file')
                if backup_filename:
                    try:
                        backup_system.create_backup(upload_to_gdrive_flag=True)
                        success, message = backup_system.restore_backup(backup_filename)
                        if success:
                            return redirect(url_for('backup', success=message))
                        else:
                            return redirect(url_for('backup', error=message))
                    except Exception as e:
                        return render_template('backup.html', backups=[], gdrive_info={'error': f'Eroare la restaurare: {str(e)}'})
                else:
                    return render_template('backup.html', backups=[], gdrive_info={'error': 'Nu a fost selectat niciun backup'})
            
            elif action == 'delete':
                backup_filename = request.form.get('backup_file')
                if backup_filename:
                    try:
                        # Șterge din local
                        backup_path = backup_system.backup_dir / backup_filename
                        info_path = backup_system.backup_dir / f"{backup_filename.replace('.db', '.json')}"
                        
                        # Verifică dacă backup-ul există pe Google Drive și îl șterge
                        gdrive_deleted = False
                        if info_path.exists():
                            with open(info_path, 'r', encoding='utf-8') as f:
                                info = json.load(f)
                                if info.get('gdrive_id'):
                                    try:
                                        from auto_backup import gdrive_auth
                                        drive = gdrive_auth()
                                        if drive:
                                            file_drive = drive.CreateFile({'id': info['gdrive_id']})
                                            file_drive.Delete()
                                            gdrive_deleted = True
                                            print(f"✅ Backup șters de pe Google Drive: {backup_filename}")
                                    except Exception as e:
                                        print(f"⚠️ Eroare la ștergerea de pe Google Drive: {e}")
                        
                        # Șterge fișierele locale
                        if backup_path.exists():
                            backup_path.unlink()
                        if info_path.exists():
                            info_path.unlink()
                        
                        success_msg = f'Backup șters: {backup_filename}'
                        if gdrive_deleted:
                            success_msg += ' (local + Google Drive)'
                        else:
                            success_msg += ' (doar local)'
                        
                        return redirect(url_for('backup', success=success_msg))
                    except Exception as e:
                        return render_template('backup.html', backups=[], gdrive_info={'error': f'Eroare la ștergerea backup-ului: {str(e)}'})
                else:
                    return render_template('backup.html', backups=[], gdrive_info={'error': 'Nu a fost selectat niciun backup'})
            
            elif action == 'sync_local':
                local_db_path = request.form.get('local_db_path', 'C:/Users/user/Desktop/Manus/ai_finance_app/finance.db')
                try:
                    success, message = backup_system.sync_with_local(local_db_path)
                    if success:
                        return redirect(url_for('backup', success=message))
                    else:
                        return redirect(url_for('backup', error=message))
                except Exception as e:
                    return render_template('backup.html', backups=[], gdrive_info={'error': f'Eroare la sincronizarea cu local: {str(e)}'})
            
            elif action == 'sync_gdrive':
                if not AUTO_BACKUP_AVAILABLE:
                    return redirect(url_for('backup', error='Google Drive nu este configurat pe acest server. Funcționalitatea de backup Google Drive nu este disponibilă.'))
                try:
                    backup_system.sync_all_backups_to_gdrive()
                    return redirect(url_for('backup', success='Sincronizare cu Google Drive realizată cu succes!'))
                except Exception as e:
                    return render_template('backup.html', backups=[], gdrive_info={'error': f'Eroare la sincronizarea cu Google Drive: {str(e)}'})
        
        # Obține lista backup-urilor
        try:
            backups = backup_system.get_backup_list()
            if not backups:
                print("DEBUG: Nu există backup-uri de afișat!")
            else:
                print(f"DEBUG: Sunt {len(backups)} backup-uri:")
                for backup in backups:
                    print(f"DEBUG: {backup['filename']} | {backup.get('created_at', 'N/A')} | {backup.get('size', 0)} bytes")
        except Exception as e:
            print(f"DEBUG: Eroare la get_backup_list(): {e}")
            backups = []
            return render_template('backup.html', backups=[], gdrive_info={'error': f'Eroare la obținerea listei de backup-uri: {str(e)}'})
        
        # Obține informații despre Google Drive
        gdrive_info = None
        try:
            gdrive_backups = [b for b in backups if b.get('gdrive_id')]
            gdrive_info = {
                'total_backups': len(gdrive_backups),
                'latest_backup': gdrive_backups[0] if gdrive_backups else None
            }
            print(f"DEBUG: GDrive info: {gdrive_info}")
        except Exception as e:
            gdrive_info = {'error': str(e)}
            print(f"DEBUG: Eroare la GDrive info: {e}")
        
        print(f"DEBUG: Trimit {len(backups)} backup-uri către template")
        print(f"DEBUG: Trimit {len(backups)} backup-uri către template")
        try:
            return render_template('backup.html', 
                                 backups=backups, 
                                 gdrive_info=gdrive_info)
        except Exception as template_error:
            print(f"DEBUG: Eroare la template: {template_error}")
            return render_template('backup.html', backups=[], gdrive_info={'error': f'Eroare la template: {str(template_error)}'})
    except Exception as e:
        print(f"DEBUG: Exceptie generală în backup(): {str(e)}")
        return render_template('backup.html', backups=[], gdrive_info={'error': f'Exceptie generală: {str(e)}'})

if __name__ == '__main__':
    try:
        port = int(os.environ.get('PORT', 5000))
        print(f"Starting AI Finance App on port {port}")
        print("Database will be initialized automatically")
        
        # Inițializează baza de date înainte de pornire
        init_db()
        print("Database initialized successfully")
        
        # Resetează tracking-ul pentru backup automat
        reset_backup_tracking()
        
        socketio.run(app, debug=False, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
