# Deploy pe Google Cloud Run

## Pași pentru deploy:

### 1. Instalează Google Cloud SDK
```bash
# Descarcă și instalează de la: https://cloud.google.com/sdk/docs/install
```

### 2. Autentifică-te în Google Cloud
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 3. Activează serviciile necesare
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 4. Deploy automat cu Cloud Build
```bash
gcloud builds submit --config cloudbuild.yaml
```

### 5. Sau deploy manual
```bash
# Build imaginea
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/ai-finance-app

# Deploy pe Cloud Run
gcloud run deploy ai-finance-app \
  --image gcr.io/YOUR_PROJECT_ID/ai-finance-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1
```

## Funcționalități PWA:
- ✅ Instalabilă pe telefon
- ✅ Funcționează offline
- ✅ Update automat
- ✅ Interfață nativă

## URL-ul aplicației:
După deploy, aplicația va fi disponibilă la:
`https://ai-finance-app-xxxxx-uc.a.run.app`

## Update-uri:
Pentru a face update, rulează din nou:
```bash
gcloud builds submit --config cloudbuild.yaml
``` 