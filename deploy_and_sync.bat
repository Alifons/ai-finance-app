@echo off
cd /d %~dp0

REM Commit & push automat
set MESSAGE=Update automat

git add .
git commit -m "%MESSAGE%"
git push origin clean-main

REM Sincronizează datele locale cu Render
python sync_local_render.py

pause 