@echo off
echo 🔄 Commit și push pentru fix-urile de restaurare...
echo ================================================

echo.
echo 📝 Adăugare modificări...
git add .

echo.
echo 💬 Commit cu mesaj descriptiv...
git commit -m "Fix: Forțare restaurare din Google Drive pe Render după restart

- Modificat restore_from_google_drive() pentru a permite restaurarea chiar și dacă există date locale pe Render
- Modificat init_db() pentru a forța restaurarea din Google Drive pe Render
- Adăugat scripte de test pentru simularea restart-ului
- Îmbunătățit logica de restaurare pentru a evita pierderea datelor"

echo.
echo 🚀 Push către GitHub...
git push origin main

echo.
echo ✅ Commit și push complet!
echo 📊 Modificările vor fi disponibile pe Render după redeploy
echo.
echo 💡 Pentru a redeploy pe Render:
echo    1. Mergi la dashboard-ul Render
echo    2. Găsește serviciul ai-finance-app
echo    3. Apasă butonul "Manual Deploy"
echo    4. Selectează "Deploy latest commit"
echo.
pause 