@echo off

:: Переходим в корень проекта
cd /d %~dp0
cd ..
echo Project directory: %cd%

:: Имя итогового файла
set BIN_NAME=nca

:: Запускаем PyInstaller
python -m PyInstaller ^
    --name %BIN_NAME% ^
    --onefile ^
    --windowed ^
    --noconfirm ^
    --clean ^
    --add-data=icons;icons ^
    --icon=icons/icon.ico ^
    main.py

:: Удаляем build и .spec-файл
rmdir /s /q build
del %BIN_NAME%.spec

echo Build successful
exit /b 0