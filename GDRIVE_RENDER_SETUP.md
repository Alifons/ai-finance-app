# Configurare Google Drive pentru Render

## 🚀 Pași pentru configurarea Google Drive pe Render

### 1. Creează proiectul pe Google Cloud Console

1. **Mergi la:** https://console.cloud.google.com
2. **Creează un proiect nou** sau folosește unul existent
3. **Activează Google Drive API:**
   - Mergi la "APIs & Services" > "Library"
   - Caută "Google Drive API"
   - Click "Enable"

### 2. Creează credentials OAuth 2.0

1. **Mergi la:** "APIs & Services" > "Credentials"
2. **Click "Create Credentials"** > "OAuth 2.0 Client IDs"
3. **Configurează:**
   - Application type: "Desktop application"
   - Name: "AI Finance App"
4. **Click "Create"**
5. **Descarcă fișierul JSON** (va fi numit ceva de genul `client_secret_xxx.json`)

### 3. Configurează fișierele locale

1. **Redenumește fișierul descărcat** în `client_secrets.json`
2. **Mută-l în folderul aplicației** (`C:\Users\user\Desktop\Manus\ai_finance_app\`)
3. **Rulează scriptul de configurare:**
   ```bash
   python setup_gdrive_render.py
   ```

### 4. Urcă fișierele pe Render (fără GitHub)

**IMPORTANT:** Nu urca `client_secrets.json` și `gdrive_token.json` pe GitHub!

Pentru Render, trebuie să le urci manual prin dashboard:

1. **Intră pe Render.com** la serviciul tău
2. **Mergi la "Environment"** în setări
3. **Adaugă variabilele de mediu:**
   ```
   GDRIVE_CLIENT_SECRETS={"installed":{"client_id":"YOUR_CLIENT_ID","client_secret":"YOUR_CLIENT_SECRET",...}}
   GDRIVE_TOKEN={"access_token":"...","refresh_token":"...",...}
   ```

### 5. Modifică codul pentru Render

Să modific `auto_backup.py` să citească credentials din variabilele de mediu:

```python
def gdrive_auth():
    """Autentificare Google Drive cu suport pentru Render"""
    gauth = GoogleAuth()
    
    # Pentru Render, citește din variabilele de mediu
    if os.environ.get('RENDER'):
        client_secrets = json.loads(os.environ.get('GDRIVE_CLIENT_SECRETS', '{}'))
        token_data = json.loads(os.environ.get('GDRIVE_TOKEN', '{}'))
        
        # Salvează temporar fișierele
        with open('client_secrets.json', 'w') as f:
            json.dump(client_secrets, f)
        
        with open('gdrive_token.json', 'w') as f:
            json.dump(token_data, f)
    
    gauth.LoadCredentialsFile("gdrive_token.json")
    
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
        gauth.SaveCredentialsFile("gdrive_token.json")
    
    return GoogleDrive(gauth)
```

### 6. Testează configurarea

1. **Redeployează aplicația** pe Render
2. **Testează funcția de backup** din aplicația web
3. **Verifică pe Google Drive** dacă apare folderul "AI Finance App Backups"

## 🔧 Troubleshooting

### Eroare: "Invalid client secrets file"
- Verifică că `client_secrets.json` există și are formatul corect
- Asigură-te că ai descărcat credentials-ul corect de pe Google Cloud Console

### Eroare: "Access denied"
- Verifică că ai activat Google Drive API
- Asigură-te că ai dat permisiuni la aplicația ta

### Eroare: "Token expired"
- Rulează din nou `setup_gdrive_render.py` pentru a regenera token-ul

## 📝 Note importante

- **Nu urca niciodată** `client_secrets.json` sau `gdrive_token.json` pe GitHub
- **Folosește variabilele de mediu** pe Render pentru securitate
- **Backup-urile locale** funcționează oricum, Google Drive este opțional
- **Testează întotdeauna** configurarea înainte de a face deploy pe producție

## ✅ Verificare finală

După configurare, ar trebui să vezi:
- ✅ Folder "AI Finance App Backups" pe Google Drive
- ✅ Funcția "Sincronizare cu Google Drive" funcționează în aplicația web
- ✅ Backup-urile se urcă automat pe Google Drive 