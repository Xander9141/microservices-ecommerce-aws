@echo off
echo ================================
echo   AUTO PUSH A GITHUB
echo ================================
echo.

cd /d "C:\Users\Admin\Desktop\microservices-ecommerce-aws"

git status --short > temp_status.txt

for %%A in (temp_status.txt) do if %%~zA==0 (
    echo No hay cambios para subir.
    del temp_status.txt
    pause
    exit /b
)

del temp_status.txt

echo Agregando cambios...
git add .

echo Creando commit...
git commit -m "Auto update %date% %time%"

echo Subiendo a GitHub...
git push

echo.
echo Listo. Cambios subidos correctamente.
pause