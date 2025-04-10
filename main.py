import sys
import json
import os

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QListWidget
from PyQt5.QtCore import QSettings, Qt
from ui_main_window import Ui_MainWindow
from remark_dialog import RemarkDialog


class MainWindow(QMainWindow):
    """Главное окно приложения."""
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.is_modified = False  # Флаг несохранённых изменений в текущем файле

        settings = QSettings("eluvesi", "NCA")
        last_file = settings.value("last_file", "")  # Узнаём путь к последнему открытому файлу

        if last_file and os.path.exists(last_file):  # Если такой файл существует
            self.current_file = last_file  # В качестве текущего файла последний открытый файл
            self.load_from_file()  # Загружаем замечания из файла
            self.update_window_title()
            self.statusBar().showMessage( f"Открыт файл: {self.current_file}.", 5000)
        else:
            self.current_file = None  # В качестве текущего файла None - создан новый (ещё несохранённый) файл
            self.statusBar().showMessage(
                "Создан новый файл. Вы можете загрузить замечания из файла или добавить их по одному вручную.", 5000
            )

        self.ui.fileCreateButton.clicked.connect(self.create_new_file)
        self.ui.fileOpenButton.clicked.connect(self.open_file)
        self.ui.fileSaveButton.clicked.connect(self.save_file)
        self.ui.fileSaveAsButton.clicked.connect(self.save_file_as)

        self.ui.remarkListWidget.setSelectionMode(QListWidget.ExtendedSelection)  # Поддержка множественного выделения
        self.ui.remarkListWidget.itemClicked.connect(
            lambda: self.statusBar().showMessage("Замечание выбрано, ПКМ чтобы скопировать выбранные замечания.", 3000)
        )
        self.ui.remarkListWidget.setContextMenuPolicy(Qt.CustomContextMenu)  # Поддержка копирования с помощью ПКМ
        self.ui.remarkListWidget.customContextMenuRequested.connect(
            lambda: self.copy_remark() if self.ui.remarkListWidget.selectedItems() else None
        )
        self.ui.remarkListWidget.itemSelectionChanged.connect(self.toggle_remark_buttons)

        self.ui.remarkAddButton.clicked.connect(self.add_remark)
        self.ui.remarkRemoveButton.clicked.connect(self.remove_remark)
        self.ui.remarkEditButton.clicked.connect(self.edit_remark)
        self.ui.remarkCopyButton.clicked.connect(self.copy_remark)
        self.ui.remarkListClearButton.clicked.connect(self.clear_remark_list)

    def create_new_file(self):
        """Очищает список замечаний и сбрасывает переменную, хранящую путь к текущему файлу."""
        if self.is_modified:  # Проверяем, были ли изменения
            reply = QMessageBox.question(
                self,
                "Несохранённые изменения",
                "У вас есть несохранённые изменения. Сохранить их перед созданием нового файла?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Yes
            )  # Окно с вариантами выбора: "да", "нет", "отмена"
            if reply == QMessageBox.Yes:
                self.save_file()  # Сохраняем текущий файл перед созданием нового
            elif reply == QMessageBox.Cancel:
                return
        self.current_file = None  # Обновляем текущий файл
        self.is_modified = False  # Создан новый файл, изменений больше нет
        self.update_window_title()  # Обновляем заголовок окна
        self.ui.remarkListWidget.clear()  # Очищаем список замечаний
        self.statusBar().showMessage("Создан новый файл. Не забудьте сохранить изменения.", 3000)

    def open_file(self):
        """Открывает диалог выбора файла, запоминает открытый файл и переходит к загрузке замечаний."""
        if self.is_modified:  # Проверяем, были ли изменения
            reply = QMessageBox.question(
                self,
                "Сохранить изменения?",
                "У вас есть несохранённые изменения. Сохранить их перед открытием другого файла?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Yes
            )  # Окно с вариантами выбора: "да", "нет", "отмена"
            if reply == QMessageBox.Yes:
                self.save_file()  # Сохраняем текущий файл перед открытием другого
            elif reply == QMessageBox.Cancel:
                return
        filename, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл с замечаниями", "", "Текстовые файлы (*.txt)"
        )
        if filename:
            self.current_file = filename  # Обновляем текущий файл
            self.is_modified = False  # Открыт другой файл, изменений больше нет
            self.update_window_title()  # Обновляем заголовок окна
            settings = QSettings("eluvesi", "NCA")
            settings.setValue("last_file", self.current_file)  # Запоминаем в качестве последнего открытого файла
            self.ui.remarkListWidget.clear()  # Очищаем список замечаний
            self.load_from_file()  # Загружаем новый список замечаний из файла

    def load_from_file(self):
        """Загружает замечания из открытого файла и добавляет их в список."""
        try:
            with open(self.current_file, "r", encoding="utf-8") as file:
                self.ui.remarkListWidget.addItems(file.read().splitlines())
                self.statusBar().showMessage(f"Замечания загружены из {self.current_file}.", 3000)
        except FileNotFoundError:
            self.statusBar().showMessage(f"Не удалось найти файл {self.current_file}.", 3000)

    def save_file(self):
        """Сохраняет изменения в текущем файле или вызывает Save As, если никакой файл не открыт."""
        if self.current_file:  # Если не None, значит был открыт какой-то файл
            self.save_to_file(self.current_file)  # Сохраняем изменения в этом файле
        else:  # Если None, значит был создан новый файл
            self.save_file_as()  # Сохраняем файл как новый

    def save_file_as(self):
        """Открывает диалог для сохранения файла с новым именем."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Сохранить как", "", "Текстовые файлы (*.txt)"
        )
        if filename:
            self.save_to_file(filename)
            self.current_file = filename  # Обновляем текущий файл
            self.is_modified = False  # Файл сохранён, изменений больше нет
            self.update_window_title()  # Обновляем заголовок окна
            settings = QSettings("eluvesi", "NCA")
            settings.setValue("last_file", self.current_file)  # Запоминаем в качестве последнего открытого файла

    def save_to_file(self, filename):
        """Сохраняет список замечаний в файл."""
        with open(filename, "w", encoding="utf-8") as file:
            for row in range(self.ui.remarkListWidget.count()):
                file.write(self.ui.remarkListWidget.item(row).text() + "\n")
        self.statusBar().showMessage(f"Замечания сохранены в {filename}.", 3000)

    def add_remark(self):
        """Открывает окно для добавления нового замечания в список."""
        dialog = RemarkDialog(self)
        if dialog.exec():
            text = dialog.get_data() # text, category, tags
            if text:
                self.ui.remarkListWidget.addItem(text)
                self.is_modified = True  # Файл изменился
                self.update_window_title()  # Обновляем заголовок
                self.statusBar().showMessage("Добавлено новое замечание.", 3000)

    def remove_remark(self):
        """Удаляет выбранное замечание из списка."""
        selected_items = self.ui.remarkListWidget.selectedItems()
        if selected_items:
            for item in selected_items:
                self.ui.remarkListWidget.takeItem(self.ui.remarkListWidget.row(item))
            self.is_modified = True  # Файл изменился
            self.update_window_title()  # Обновляем заголовок
            self.statusBar().showMessage("Замечание удалено.", 3000)

    def edit_remark(self):
        """Открывает окно для редактирования выбранного замечания."""
        selected_item = self.ui.remarkListWidget.currentItem()
        if selected_item:
            dialog = RemarkDialog(self, remark_text=selected_item.text())
            if dialog.exec():
                text = dialog.get_data() # text, category, tags
                if text:
                    selected_item.setText(text)
                    self.is_modified = True  # Файл изменился
                    self.update_window_title()  # Обновляем заголовок
                    self.statusBar().showMessage("Замечание обновлено.", 3000)

    def copy_remark(self):
        """Копирует выбранные замечания в буфер обмена."""
        selected_items = self.ui.remarkListWidget.selectedItems()
        if selected_items:
            remarks_text = "\n".join(item.text() for item in selected_items)  # Собираем все выбранные замечания
            QApplication.clipboard().setText(remarks_text)  # Копируем их в буфер обмена
            self.statusBar().showMessage("Выбранные замечания скопированы в буфер обмена.", 3000)

    def clear_remark_list(self):
        """Очищает весь список замечаний."""
        if self.ui.remarkListWidget.count() > 0:  # Только если есть элементы
            self.ui.remarkListWidget.clear()
            self.is_modified = True  # Файл изменился
            self.update_window_title()  # Обновляем заголовок
            self.statusBar().showMessage("Список замечаний очищен.", 3000)

    def toggle_remark_buttons(self):
        """Включает (отключает) кнопки взаимодействия с замечанием, если сейчас оно (не) выбрано."""
        self.ui.remarkRemoveButton.setEnabled(bool(self.ui.remarkListWidget.selectedItems()))
        self.ui.remarkEditButton.setEnabled(bool(self.ui.remarkListWidget.selectedItems()))
        self.ui.remarkCopyButton.setEnabled(bool(self.ui.remarkListWidget.selectedItems()))

    def update_window_title(self):
        """Обновляет заголовок окна, отображает название текущего файла и звёздочку."""
        base_title = "Помощник нормоконтролёра"
        file_name = os.path.basename(self.current_file) if self.current_file else "Документ"
        modify_marker = "*" if self.is_modified else ""
        self.setWindowTitle(f"{file_name}{modify_marker} – {base_title}")

    def closeEvent(self, event):
        """Запрос подтверждения перед закрытием, если есть несохранённые изменения."""
        if self.is_modified:
            reply = QMessageBox.question(
                self,
                "Несохранённые изменения",
                "У вас есть несохранённые изменения. Сохранить их перед выходом?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                self.save_file()  # Сохраняем изменения
            elif reply == QMessageBox.Cancel:
                event.ignore()  # Отменяем закрытие окна
                return
        event.accept()  # Закрываем окно


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())