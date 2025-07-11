# Pasul 1: Obținerea credențialelor Google Drive

## 1.1. Accesează Google Cloud Console
- Mergi la: https://console.cloud.google.com/
- Fă login cu contul tău Google

## 1.2. Selectează proiectul
- În partea de sus, selectează proiectul: **"ai-finance-app-backup"**
- Dacă nu vezi proiectul, creează-l:
  - Apasă pe dropdown-ul proiectelor
  - Apasă "New Project"
  - Nume: "ai-finance-app-backup"
  - Apasă "Create"

## 1.3. Activează Google Drive API
- În meniul din stânga, mergi la "APIs & Services" → "Library"
- Caută "Google Drive API"
- Apasă pe "Google Drive API"
- Apasă "Enable"

## 1.4. Creează credențialele OAuth
- Mergi la "APIs & Services" → "Credentials"
- Apasă "Create Credentials" → "OAuth client ID"
- Dacă nu ai OAuth consent screen:
  - Selectează "External"
  - Completează informațiile de bază
  - Apasă "Save and Continue" pentru toate etapele

## 1.5. Configurează OAuth Client
- Application type: "Desktop application"
- Name: "AI Finance App Backup"
- Apasă "Create"

## 1.6. Descarcă credențialele
- Apasă pe clientul OAuth creat
- Apasă butonul de download (⬇️)
- Salvează fișierul ca `client_secrets.json` în folderul aplicației

## 1.7. Verifică fișierul
- Deschide `client_secrets.json`
- Ar trebui să conțină:
  - "client_id": o valoare lungă
  - "client_secret": o valoare lungă
  - "project_id": "ai-finance-app-backup" 