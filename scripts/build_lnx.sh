#!/usr/bin/env bash

# Переходим в директорию проекта
cd "$(dirname "$0")" || exit 1;
cd ..;
echo "Project directory: $PWD";

# Имя итогового файла
BIN_NAME="nca";

# Запускаем PyInstaller
python3 -m PyInstaller \
    --name $BIN_NAME \
    --onefile \
    --windowed \
    --noconfirm \
    --clean \
    --add-data=icons:icons \
    --icon=icons/icon.ico \
    main.py;

# Удаляем build и .spec-файл
rm -rf build;
rm -f $BIN_NAME.spec;

echo "Build successful";
exit 0;