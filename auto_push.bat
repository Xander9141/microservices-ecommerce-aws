@echo off
echo ================================
echo   AUTO PUSH A GITHUB
echo ================================
echo.

cd /d "C:\Users\Admin\Desktop\microservices-ecommerce-aws"

echo Revisando cambios...
git status

echo.
echo Agregando archivos...
git add .

echo.
echo Creando commit...
git commit -m "Auto update %date% %time%"

echo.
echo Subiendo a GitHub...
git push

echo.
echo ================================
echo   PROCESO TERMINADO
echo ================================
pause