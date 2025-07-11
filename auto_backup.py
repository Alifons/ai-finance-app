import os
import shutil
import json
from datetime import datetime
import requests
import sqlite3
from pathlib import Path
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# ID-ul folderului de backup pe Google Drive (va fi creat automat)
GDRIVE_BACKUP_FOLDER_ID = None

class AutoBackup:
    def __init__(self, db_path='finance.db'):
        self.db_path = db_path
        self.backup_dir = Path('backups')
        self.backup_dir.mkdir(exist_ok=True)
        self.gdrive_folder_id = self.get_or_create_backup_folder()
        
    def get_or_create_backup_folder(self):
        """Creează sau găsește folderul de backup pe Google Drive"""
        global GDRIVE_BACKUP_FOLDER_ID
        
        if GDRIVE_BACKUP_FOLDER_ID:
            return GDRIVE_BACKUP_FOLDER_ID
            
        try:
            drive = gdrive_auth()
            
            # Caută folderul existent
            folder_name = "AI Finance App Backups"
            file_list = drive.ListFile({'q': f"title='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()
            
            if file_list:
                folder_id = file_list[0]['id']
                print(f"✅ Folder găsit pe Google Drive: {folder_name}")
            else:
                # Creează folderul nou
                folder_metadata = {
                    'title': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                folder = drive.CreateFile(folder_metadata)
                folder.Upload()
                folder_id = folder['id']
                print(f"✅ Folder creat pe Google Drive: {folder_name}")
            
            GDRIVE_BACKUP_FOLDER_ID = folder_id
            return folder_id
            
        except Exception as e:
            print(f"❌ Eroare la crearea folderului Google Drive: {e}")
            return None
        
    def create_backup(self, upload_to_gdrive_flag=True):
        """Creează backup local și pe Google Drive"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'finance_backup_{timestamp}.db'
        backup_path = self.backup_dir / backup_filename
        
        # Copiază baza de date
        shutil.copy2(self.db_path, backup_path)
        
        # Creează fișierul de informații
        info_filename = f'finance_backup_{timestamp}.json'
        info_path = self.backup_dir / info_filename
        
        info = {
            'timestamp': datetime.now().isoformat(),
            'filename': backup_filename,
            'size': os.path.getsize(backup_path),
            'tables': self.get_table_info(),
            'source': 'local_backup'
        }
        
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
        
        print(f"Backup creat local: {backup_filename}")
        
        # Urcă pe Google Drive dacă este solicitat
        if upload_to_gdrive_flag and self.gdrive_folder_id:
            try:
                gdrive_id = upload_to_gdrive(str(backup_path), self.gdrive_folder_id)
                info['gdrive_id'] = gdrive_id
                info['source'] = 'local_and_gdrive'
                
                # Actualizează fișierul de informații cu ID-ul de pe Google Drive
                with open(info_path, 'w', encoding='utf-8') as f:
                    json.dump(info, f, indent=2, ensure_ascii=False)
                print(f"✅ Backup urcat pe Google Drive cu ID: {gdrive_id}")
            except Exception as e:
                print(f"❌ Eroare la upload pe Google Drive: {e}")
        
        return backup_filename
    
    def sync_all_backups_to_gdrive(self):
        """Sincronizează toate backup-urile locale pe Google Drive"""
        print("=== Sincronizare toate backup-urile pe Google Drive ===")
        
        if not self.gdrive_folder_id:
            print("❌ Nu s-a putut crea folderul pe Google Drive")
            return False
        
        backup_files = list(self.backup_dir.glob('finance_backup_*.db'))
        uploaded_count = 0
        
        for backup_file in backup_files:
            try:
                # Verifică dacă backup-ul există deja pe Google Drive
                info_file = backup_file.with_suffix('.json')
                if info_file.exists():
                    with open(info_file, 'r', encoding='utf-8') as f:
                        info = json.load(f)
                        if 'gdrive_id' in info:
                            print(f"⏭️ Backup există deja pe Google Drive: {backup_file.name}")
                            continue
                
                # Urcă backup-ul pe Google Drive
                gdrive_id = upload_to_gdrive(str(backup_file), self.gdrive_folder_id)
                
                # Actualizează fișierul de informații
                if info_file.exists():
                    with open(info_file, 'r', encoding='utf-8') as f:
                        info = json.load(f)
                    info['gdrive_id'] = gdrive_id
                    info['source'] = 'local_and_gdrive'
                    with open(info_file, 'w', encoding='utf-8') as f:
                        json.dump(info, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Backup urcat: {backup_file.name}")
                uploaded_count += 1
                
            except Exception as e:
                print(f"❌ Eroare la upload {backup_file.name}: {e}")
        
        print(f"\n📊 Sincronizare completă!")
        print(f"   - Backup-uri urcate: {uploaded_count}")
        print(f"   - Total backup-uri: {len(backup_files)}")
        
        return True
    
    def get_table_info(self):
        """Obține informații despre tabele"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Informații despre tranzacții
        cursor.execute("SELECT COUNT(*) FROM tranzactii")
        tranzactii_count = cursor.fetchone()[0]
        
        # Informații despre obiecte
        cursor.execute("SELECT COUNT(*) FROM obiecte")
        obiecte_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'tranzactii': tranzactii_count,
            'obiecte': obiecte_count
        }
    
    def restore_backup(self, backup_filename):
        """Restaurează backup-ul"""
        backup_path = self.backup_dir / backup_filename
        
        if not backup_path.exists():
            return False, "Backup-ul nu există!"
        
        try:
            # Creează backup al bazei curente înainte de restaurare
            self.create_backup()
            
            # Restaurează backup-ul
            shutil.copy2(backup_path, self.db_path)
            
            return True, f"Backup-ul {backup_filename} a fost restaurat cu succes!"
        except Exception as e:
            return False, f"Eroare la restaurare: {str(e)}"
    
    def sync_with_local(self, local_db_path):
        """Sincronizează cu baza de date locală"""
        if not os.path.exists(local_db_path):
            return False, "Baza de date locală nu există!"
        
        try:
            # Creează backup înainte de sincronizare
            self.create_backup()
            
            # Copiază baza locală
            shutil.copy2(local_db_path, self.db_path)
            
            return True, "Sincronizare cu baza locală realizată cu succes!"
        except Exception as e:
            return False, f"Eroare la sincronizare: {str(e)}"
    
    def get_backup_list(self):
        """Obține lista backup-urilor"""
        backups = []
        
        for file in self.backup_dir.glob('finance_backup_*.db'):
            info_file = file.with_suffix('.json')
            
            if info_file.exists():
                with open(info_file, 'r', encoding='utf-8') as f:
                    info = json.load(f)
                    backups.append({
                        'filename': file.name,
                        'created_at': info.get('timestamp', ''),
                        'size': info.get('size', 0),
                        'tables': info.get('tables', {'tranzactii': 0, 'obiecte': 0}),
                        'gdrive_id': info.get('gdrive_id', None),
                        'source': info.get('source', 'local')
                    })
        
        # Sortează după data creării (cel mai recent primul)
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        return backups

# Funcții pentru integrarea cu aplicația Flask
def get_backup_system():
    """Returnează instanța sistemului de backup"""
    return AutoBackup()

def auto_backup_task():
    """Task pentru backup automat"""
    backup_system = get_backup_system()
    
    # Creează backup la fiecare 6 ore
    backup_system.create_backup(upload_to_gdrive_flag=True)
    print(f"Backup automat creat la {datetime.now().strftime('%H:%M:%S')}")

def gdrive_auth():
    """Autentificare Google Drive cu suport pentru Render"""
    gauth = GoogleAuth()
    
    # Pentru Render, citește din variabilele de mediu
    is_render = os.environ.get('RENDER', False) or 'render' in os.environ.get('HOSTNAME', '').lower()
    
    if is_render:
        try:
            # Încearcă să citească din variabilele de mediu
            client_secrets_str = os.environ.get('GDRIVE_CLIENT_SECRETS')
            token_str = os.environ.get('GDRIVE_TOKEN')
            
            if client_secrets_str and token_str:
                # Salvează temporar fișierele
                with open('client_secrets.json', 'w') as f:
                    f.write(client_secrets_str)
                
                with open('gdrive_token.json', 'w') as f:
                    f.write(token_str)
                
                print("✅ Credentials încărcate din variabilele de mediu Render")
            else:
                print("⚠️ Nu sunt configurate variabilele de mediu pentru Google Drive pe Render")
                return None
        except Exception as e:
            print(f"❌ Eroare la încărcarea credentials din Render: {e}")
            return None
    
    # Configurează setările pentru refresh token
    gauth.settings['access_type'] = 'offline'
    gauth.settings['approval_prompt'] = 'force'
    
    # Încearcă să încarce credențialele salvate
    try:
        gauth.LoadCredentialsFile("gdrive_token.json")
    except:
        pass
    
    if gauth.credentials is None:
        if is_render:
            print("❌ Nu s-au putut încărca credentials pentru Render")
            return None
        
        # Prima dată: va deschide browserul pentru autentificare
        print("Se deschide browserul pentru autentificare Google...")
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    
    gauth.SaveCredentialsFile("gdrive_token.json")
    return GoogleDrive(gauth)

def upload_to_gdrive(filepath, folder_id=None):
    """Urcă un fișier pe Google Drive"""
    drive = gdrive_auth()
    filename = os.path.basename(filepath)
    
    if folder_id:
        file_drive = drive.CreateFile({
            'title': filename, 
            'parents': [{'id': folder_id}]
        })
    else:
        file_drive = drive.CreateFile({'title': filename})
    
    file_drive.SetContentFile(filepath)
    file_drive.Upload()
    print(f"Backup urcat pe Google Drive: {filename}")
    return file_drive['id']

# Exemplu de utilizare:
# upload_to_gdrive('backups/finance_backup_20250710_143403.db')

if __name__ == "__main__":
    # Testează sistemul de backup
    backup_system = AutoBackup()
    
    print("=== Testare sistem backup ===")
    print(f"Baza de date: {backup_system.db_path}")
    print(f"Director backup: {backup_system.backup_dir}")
    print(f"Google Drive folder ID: {backup_system.gdrive_folder_id}")
    
    # Sincronizează toate backup-urile pe Google Drive
    backup_system.sync_all_backups_to_gdrive()
    
    # Creează backup nou
    filename = backup_system.create_backup(upload_to_gdrive_flag=True)
    print(f"Backup creat: {filename}")
    
    # Lista backup-uri
    backups = backup_system.get_backup_list()
    print(f"Total backup-uri: {len(backups)}")
    
    for backup in backups[:3]:  # Primele 3
        source = backup.get('source', 'local')
        gdrive_id = backup.get('gdrive_id')
        status = "✅ Local + Google Drive" if gdrive_id else "📁 Doar local"
        print(f"- {backup['filename']} ({backup['created_at']}) - {status}") 