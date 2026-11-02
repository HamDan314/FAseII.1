@echo off
setlocal
cd /d "%~dp0"
where docker >nul 2>&1
if errorlevel 1 (
  echo No se encontro Docker. Instala Docker Desktop y activa contenedores Linux.
  goto :error
)
docker info >nul 2>&1
if errorlevel 1 (
  echo Abre Docker Desktop, espera a que indique que esta listo y ejecuta este archivo de nuevo.
  goto :error
)
docker compose version
if errorlevel 1 goto :error
docker compose config --quiet
if errorlevel 1 goto :error
docker compose up -d --build --wait --wait-timeout 180
if errorlevel 1 goto :logs
docker compose exec -T backend python -m pytest -q
if errorlevel 1 goto :logs
docker compose exec -T backend python tests/comprobar_integracion.py
if errorlevel 1 goto :logs
docker compose ps
echo.
echo Verificacion completa. Abre http://localhost:8080
echo Si cambiaste FRONTEND_PORT en .env, usa ese puerto.
echo Para detener el proyecto: docker compose down
pause
exit /b 0
:logs
docker compose logs --tail=80
:error
echo.
echo No se completo la comprobacion. Comparte el mensaje de esta ventana.
pause
exit /b 1
