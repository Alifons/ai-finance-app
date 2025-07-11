# ☁️ Google Drive Backup Setup

## 🎯 Obiectiv
Configurarea unui sistem de backup automat pe Google Drive pentru a asigura persistența datelor pe Render.com

## 📋 Pași de Configurare

### 1. **Instalare Dependențe**
```bash
pip install PyDrive2
```

### 2. **Configurare Google Drive API**

#### Pasul 2.1: Creează Proiect Google Cloud
1. Mergi la [Google Cloud Console](https://console.cloud.google.com/)
2. Creează un proiect nou sau selectează unul existent
3. Activează Google Drive API

#### Pasul 2.2: Creează Credențiale
1. În Google Cloud Console, mergi la "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Alege "Desktop application"
4. Descarcă fișierul JSON cu credențialele
5. Redenumește-l în `client_secrets.json` și pune-l în directorul aplicației

### 3. **Prima Autentificare**
```bash
python test_gdrive_backup.py
```

La prima rulare:
- Se va deschide browserul pentru autentificare
- Autorizează aplicația să acceseze Google Drive
- Se va crea fișierul `gdrive_token.json`

### 4. **Testare Configurare**
```bash
python test_gdrive_backup.py
```

Ar trebui să vezi:
```
✅ Fișierul de credențiale Google Drive există
✅ Modulele Google Drive sunt disponibile
✅ Autentificarea Google Drive funcționează
✅ Sistemul de backup este configurat
✅ Folder Google Drive: [ID_FOLDER]
```

## 🔧 Funcționalități Implementate

### ✅ **Backup Automat pe Render**
- Backup la fiecare minut pe Render
- Upload automat pe Google Drive
- Backup înainte de sleep mode

### ✅ **Restaurare Automată**
- Restaurare din backup local
- Restaurare din Google Drive (dacă local nu există)
- Detectare automată a mediului Render

### ✅ **Sincronizare Manuală**
- Sincronizare toate backup-urile pe Google Drive
- Backup manual cu upload pe Google Drive
- Restaurare din orice backup disponibil

## 📁 Structura Backup-urilor

### Local (Render)
```
backups/
├── finance_backup_20241201_143022.db
├── finance_backup_20241201_143022.json
├── finance_backup_20241201_143125.db
└── finance_backup_20241201_143125.json
```

### Google Drive
```
AI Finance App Backups/
├── finance_backup_20241201_143022.db
├── finance_backup_20241201_143125.db
└── finance_backup_20241201_143230.db
```

## 🔄 Cum Funcționează

### La Pornirea Aplicației pe Render:
1. **Detectează** că rulează pe Render
2. **Caută** backup local
3. **Dacă nu există local**, caută pe Google Drive
4. **Descarcă** și restaurează din Google Drive
5. **Pornește** cu toate datele intacte

### Backup Automat:
1. **La fiecare minut** pe Render
2. **Upload automat** pe Google Drive
3. **Backup înainte** de sleep mode
4. **Sincronizare** între local și cloud

## 🛡️ Siguranță

### Backup-uri Multiple:
- ✅ Backup local pe Render
- ✅ Backup pe Google Drive
- ✅ Backup înainte de restaurare
- ✅ Backup la fiecare modificare

### Verificări:
- ✅ Verifică dacă baza de date are deja date
- ✅ Nu suprascrie datele existente
- ✅ Log-uri detaliate pentru debugging
- ✅ Gestionare erori robustă

## 📊 Monitorizare

### Log-uri Importante:
```
🔄 Detectat mediul Render.com - încerc restaurarea datelor...
✅ Date restaurate din Google Drive: finance_backup_20241201_143022.db
✅ Backup Google Drive creat la 14:30:25
```

### Verificare Status:
- Accesează `/backup` pentru status backup-uri
- Verifică log-urile pentru backup-uri Google Drive
- Testează cu date mici înainte de producție

## 🚀 Deploy pe Render

### 1. **Adaugă Dependențe**
În `requirements.txt`:
```
PyDrive2==1.17.0
```

### 2. **Adaugă Variabile de Mediu**
În `render.yaml`:
```yaml
envVars:
  - key: GOOGLE_DRIVE_ENABLED
    value: true
```

### 3. **Deploy**
```bash
git add .
git commit -m "Add Google Drive backup"
git push
```

## 🎯 Rezultatul

### Înainte:
- ❌ Datele se pierdeau la sleep mode
- ❌ Nu exista backup pe cloud
- ❌ Restaurarea era manuală

### După Configurare:
- ✅ Backup automat pe Google Drive
- ✅ Restaurare automată din cloud
- ✅ Persistență completă pe Render
- ✅ Sincronizare între local și cloud
- ✅ Siguranță cu backup-uri multiple

## 🚨 Troubleshooting

### Eroare: "Modulele Google Drive nu sunt disponibile"
```bash
pip install PyDrive2
```

### Eroare: "Nu s-a putut autentifica"
1. Verifică fișierul `client_secrets.json`
2. Șterge `gdrive_token.json` și reautentifică
3. Verifică permisiunile Google Drive API

### Eroare: "Nu s-a putut crea folderul"
1. Verifică permisiunile Google Drive
2. Verifică credențialele
3. Reautentifică cu `python test_gdrive_backup.py`

### Backup-urile nu se urcă pe Google Drive
1. Verifică conexiunea la internet
2. Verifică log-urile pentru erori
3. Testează manual cu `python test_gdrive_backup.py`

## 📱 Beneficii

- ✅ **Persistență completă** pe Render
- ✅ **Backup automat** pe Google Drive
- ✅ **Restaurare automată** din cloud
- ✅ **Sincronizare** între local și Render
- ✅ **Siguranță** cu backup-uri multiple
- ✅ **Monitorizare** cu log-uri detaliate

**Aplicația ta va avea backup automat pe Google Drive și va funcționa perfect pe Render!** 🚀 