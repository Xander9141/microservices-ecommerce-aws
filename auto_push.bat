@echo off
color 0A

echo ==================================
echo        AUTO PUSH GITHUB
echo ==================================
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

echo.
set /p mensaje=Mensaje del commit: 

echo.
echo Agregando archivos...
git add .

echo.
echo Creando commit...
git commit -m "%mensaje%"

echo.
echo Subiendo cambios...
git push

echo.
echo ==================================
echo     PUSH COMPLETADO
echo ==================================

pause