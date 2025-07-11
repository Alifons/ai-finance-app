# 🔧 Setup Google Drive API - Ghid Pas cu Pas

## 🎯 Obiectiv
Configurarea Google Drive API pentru backup-uri automate

## 📋 Pași de Configurare

### 1. **Creează Proiect Google Cloud**

1. Mergi la [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" > "New Project"
3. Nume proiect: `AI Finance App Backup`
4. Click "Create"

### 2. **Activează Google Drive API**

1. În Google Cloud Console, mergi la "APIs & Services" > "Library"
2. Caută "Google Drive API"
3. Click pe "Google Drive API"
4. Click "Enable"

### 3. **Creează Credențiale OAuth2**

1. Mergi la "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Dacă ești întrebat să configurezi OAuth consent screen:
   - User Type: External
   - App name: AI Finance App
   - User support email: email-ul tău
   - Developer contact information: email-ul tău
   - Click "Save and Continue" pentru toate secțiunile

4. Pentru OAuth 2.0 Client ID:
   - Application type: Desktop application
   - Name: AI Finance App Desktop Client
   - Click "Create"

5. **Descarcă fișierul JSON** cu credențialele

### 4. **Configurează Credențialele**

1. Redenumește fișierul descărcat în `client_secrets.json`
2. Pune-l în directorul aplicației: `C:\Users\user\Desktop\Manus\ai_finance_app\`

### 5. **Testează Configurația**

```bash
python test_gdrive_auth.py
```

La prima rulare:
- Se va deschide browserul
- Autorizează aplicația să acceseze Google Drive
- Se va crea fișierul `gdrive_token.json`

### 6. **Creează Backup de Test**

```bash
python create_test_backup.py
```

## 🔍 Verificare în Google Drive

1. Deschide [Google Drive](https://drive.google.com)
2. Caută folderul **"AI Finance App Backups"**
3. Verifică dacă conține backup-urile

## 🚨 Troubleshooting

### Eroare: "No refresh_token found"
**Soluție:** 
1. Șterge fișierul `gdrive_token.json`
2. Rulează din nou `python test_gdrive_auth.py`
3. Autorizează din nou aplicația

### Eroare: "client_secrets.json not found"
**Soluție:**
1. Verifică dacă fișierul există în directorul aplicației
2. Verifică dacă numele este exact `client_secrets.json`

### Eroare: "Google Drive API not enabled"
**Soluție:**
1. Mergi la Google Cloud Console
2. Activează Google Drive API
3. Așteaptă câteva minute

### Eroare: "OAuth consent screen not configured"
**Soluție:**
1. Configurează OAuth consent screen
2. Adaugă email-ul tău ca test user
3. Așteaptă validarea (poate dura 24h)

## 📁 Structura Fișierelor

```
ai_finance_app/
├── client_secrets.json     # Credențiale Google Drive
├── gdrive_token.json       # Token salvat (se creează automat)
├── settings.yaml           # Configurare aplicație
└── backups/               # Backup-uri locale
```

## ✅ Verificare Finală

După configurare, ar trebui să vezi:

1. **În Google Drive:**
   - Folder: "AI Finance App Backups"
   - Backup-uri cu nume: `finance_backup_YYYYMMDD_HHMMSS.db`

2. **În aplicație:**
   - Backup-uri automate la fiecare minut
   - Restaurare automată din Google Drive
   - Sincronizare între local și cloud

## 🎉 Rezultatul

- ✅ Backup automat pe Google Drive
- ✅ Restaurare automată din cloud
- ✅ Persistență completă pe Render
- ✅ Siguranță cu backup-uri multiple

**Aplicația ta va avea backup automat pe Google Drive!** 🚀 