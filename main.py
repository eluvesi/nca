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
            if last_file.endswith(".txt"):  # Загружаем новый список замечаний из txt-файла
                self.load_from_txt()
            elif last_file.endswith(".json"):  # Загружаем новый список замечаний из json-файла
                self.load_from_json()
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

        self.ui.allTabListWidget.setSelectionMode(QListWidget.ExtendedSelection)  # Поддержка множественного выделения
        self.ui.allTabListWidget.itemClicked.connect(
            lambda: self.statusBar().showMessage("Замечание выбрано, ПКМ чтобы скопировать выбранные замечания.", 3000)
        )
        self.ui.allTabListWidget.setContextMenuPolicy(Qt.CustomContextMenu)  # Поддержка копирования с помощью ПКМ
        self.ui.allTabListWidget.customContextMenuRequested.connect(
            lambda: self.copy_remark() if self.ui.allTabListWidget.selectedItems() else None
        )
        self.ui.allTabListWidget.itemSelectionChanged.connect(self.toggle_remark_buttons)

        self.ui.remarkAddButton.clicked.connect(self.add_remark)
        self.ui.remarkRemoveButton.clicked.connect(self.remove_remark)
        self.ui.remarkEditButton.clicked.connect(self.edit_remark)
        self.ui.remarkCopyButton.clicked.connect(self.copy_remark)
        self.ui.remarkListClearButton.clicked.connect(self.clear_remark_list)

    def create_new_file(self):
        """Очищает список замечаний и сбрасывает переменную, хранящую путь к текущему файлу."""
        # TODO: Исправить баг: очищается только список на вкладке "Все". Остальные вкладки остаются прежними.
        # TODO: Это связано с тем, что очистка на данный момент представляет из себя "self.ui.allTabListWidget.clear()"
        # TODO: Т.е. очистку списка на вкладке "Все". Это прекрасно работало, пока вкладок не было и список был всего
        # TODO: один. Теперь нужно также закрывать все вкладки. Такая очистка происходит не только в этой функции,
        # TODO: но и в open_file(), и, возможно, где-то ещё. Исправить нужно, разумеется, везде.
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
        self.ui.allTabListWidget.clear()  # Очищаем список замечаний
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
            self, "Выберите файл с замечаниями", "", "Файлы замечаний (*.txt *.json)"
        )
        if filename:
            self.current_file = filename  # Обновляем текущий файл
            self.is_modified = False  # Открыт другой файл, изменений больше нет
            self.update_window_title()  # Обновляем заголовок окна
            settings = QSettings("eluvesi", "NCA")
            settings.setValue("last_file", self.current_file)  # Запоминаем в качестве последнего открытого файла
            self.ui.allTabListWidget.clear()  # Очищаем список замечаний
            if filename.endswith(".txt"):  # Загружаем новый список замечаний из txt-файла
                self.load_from_txt()
            elif filename.endswith(".json"):  # Загружаем новый список замечаний из json-файла
                self.load_from_json()

    def load_from_txt(self):
        """Загружает замечания из txt-файла и добавляет их в список."""
        try:
            with open(self.current_file, "r", encoding="utf-8") as file:
                self.ui.allTabListWidget.addItems(file.read().splitlines())
                self.statusBar().showMessage(f"Замечания загружены из {self.current_file}.", 3000)
        except FileNotFoundError:
            self.statusBar().showMessage(f"Не удалось найти файл {self.current_file}.", 3000)

    def load_from_json(self):
        """Загружает замечания и категории из json-файла, создаёт и заполняет вкладки."""
        # TODO: Вероятно, потребуются изменения для реализации функционала, описанного в TODO для remove_remark().
        # TODO: Если вы посчитаете, что для тех или иных целей необходимо изменить формат самого json-файла, то это не
        # TODO: воспрещается. Однако, в таком случае поставьте меня в известность.
        try:
            with open(self.current_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                # Для каждой категории создаём вкладку и добавляем туда замечания
                for category, remarks in data.items():
                    # Создаем вкладку со списком замечаний для каждой категории
                    tab_list_widget = QListWidget()
                    self.ui.tabWidget.addTab(tab_list_widget, category)
                    # Каждое замечание добавляем сразу в два списка
                    for remark in remarks:
                        tab_list_widget.addItem(remark)  # В список на вкладке категории
                        self.ui.allTabListWidget.addItem(remark)  # И в список на вкладке "Все"
                self.statusBar().showMessage(f"Замечания загружены из {self.current_file}.", 3000)
        except (FileNotFoundError, json.JSONDecodeError):
            self.statusBar().showMessage(f"Не удалось найти файл {self.current_file}.", 3000)

    def save_file(self):
        """Сохраняет изменения в текущем файле или вызывает Save As, если никакой файл не открыт."""
        # TODO: Добавить возможность сохранения в json. Сохранение в txt работает по списку "Все", таким образом потеря
        # TODO: самих замечаний не происходит. Но информация о категоризации исчезает. Если категорий не было, а была
        # TODO: только вкладка "Все", то всё нормально. Если категории были, то стоит либо предупреждать пользователя
        # TODO: о том, что произойдёт потеря категорий, либо не давать возможности сохранить в txt, только json.
        # TODO: Первый вариант предпочтительнее, потому что он более гибкий и оставляет выбор за пользователем.
        if self.current_file:  # Если не None, значит был открыт какой-то файл
            self.save_to_txt(self.current_file)  # Сохраняем изменения в этом файле
        else:  # Если None, значит был создан новый файл
            self.save_file_as()  # Сохраняем файл как новый

    def save_file_as(self):
        """Открывает диалог для сохранения файла с новым именем."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Сохранить как", "", "Текстовые файлы (*.txt)"
        )
        if filename:
            self.save_to_txt(filename)
            self.current_file = filename  # Обновляем текущий файл
            self.is_modified = False  # Файл сохранён, изменений больше нет
            self.update_window_title()  # Обновляем заголовок окна
            settings = QSettings("eluvesi", "NCA")
            settings.setValue("last_file", self.current_file)  # Запоминаем в качестве последнего открытого файла

    def save_to_txt(self, filename):
        """Сохраняет список замечаний со вкладки "Все" в txt-файл."""
        with open(filename, "w", encoding="utf-8") as file:
            for row in range(self.ui.allTabListWidget.count()):
                file.write(self.ui.allTabListWidget.item(row).text() + "\n")
        self.statusBar().showMessage(f"Замечания сохранены в {filename}.", 3000)

    def add_remark(self):
        """Открывает окно для добавления нового замечания в список."""
        # TODO: Сейчас работает только на вкладке "Все". Распространить и на остальные вкладки.
        # TODO: При добавлении замечания открывается новое окно RemarkDialog, там есть выпадающий список
        # TODO: куда должны парситься все имеющиеся категории. Для успешного сохранения пользователь должен
        # TODO: выбрать в списке какую-то категорию. Замечание должно появиться на вкладке этой кагории и на
        # TODO: вкладке "Все". Если никакая категория не была выбрана, то замечание попадает на вкладку "Без категории"
        # TODO: и на вкладку "Все". Либо (если по каким-то причинам реализовать "Без категории" окажется трудно)
        # TODO: добавление не происходит. Например, сейчас, если текст замечания пуст, то добавление не происходит.
        dialog = RemarkDialog(self)
        if dialog.exec():
            text = dialog.get_data()
            if text:
                self.ui.allTabListWidget.addItem(text)
                self.is_modified = True  # Файл изменился
                self.update_window_title()  # Обновляем заголовок
                self.statusBar().showMessage("Добавлено новое замечание.", 3000)

    def remove_remark(self):
        """Удаляет выбранное замечание из списка."""
        # TODO: Сейчас работает только на вкладке "Все". Распространить и на остальные вкладки.
        # TODO: Замечание должно удаляться со списка на открытой вкладке и со списка на вкладке "Все". Если открыта
        # TODO: вкладка "Все", то замечание должно удалиться ещё и из списка на вкладке своей катгории. Подумайте, как
        # TODO: можно связать одно и то же замечание в списках на разных вкладках. Сейчас это по сути два независимых
        # TODO: объекта. Вообще, список может хранить не только строки, но и объекты QListWidgetItem, которые могут
        # TODO: содержать некоторую информацию. Можно в этой информации хранить для каждого замечания уникальный ID.
        # TODO: Вероятно, имеет смысл также хранить там имя категории, чтобы не искать по всем вкладкам. Думайте.
        selected_items = self.ui.allTabListWidget.selectedItems()
        if selected_items:
            for item in selected_items:
                self.ui.allTabListWidget.takeItem(self.ui.allTabListWidget.row(item))
            self.is_modified = True  # Файл изменился
            self.update_window_title()  # Обновляем заголовок
            self.statusBar().showMessage("Замечание удалено.", 3000)

    def edit_remark(self):
        """Поочерёдно открывает окна для редактирования выбранных замечаний."""
        # TODO: Сейчас работает только на вкладке "Все". Распространить и на остальные вкладки.
        # TODO: При редактировании замечания открывается то же самое окно RemarkDialog, как и при добавлении нового.
        # TODO: Там есть выпадающий список выбора категории. Соответственно, если пользователь выбрал другую категорию,
        # TODO: то замечание удаляется из списка на вкладке старой категории и добавляется в список на вкладке новой.
        # TODO: Со вкладки "Все", разумеется, ничего не удаляется. Если пользователь изменил текст замечания, то он
        # TODO: меняется и в списке на вкладке категории, и в списке на вкладке "Все".
        selected_items = self.ui.allTabListWidget.selectedItems()
        for item in selected_items:
            dialog = RemarkDialog(self, remark_text=item.text())
            if dialog.exec():
                text = dialog.get_data()
                if text:
                    item.setText(text)
                    self.is_modified = True  # Файл изменился
                    self.update_window_title()  # Обновляем заголовок
                    self.statusBar().showMessage("Замечание обновлено.", 3000)

    def copy_remark(self):
        """Копирует выбранные замечания в буфер обмена."""
        # TODO: Сейчас работает только на вкладке "Все". Распространить и на остальные вкладки. Не забывайте про
        # TODO: необходимость возможности множественного копирования.
        selected_items = self.ui.allTabListWidget.selectedItems()
        if selected_items:
            remarks_text = "\n".join(item.text() for item in selected_items)  # Собираем все выбранные замечания
            QApplication.clipboard().setText(remarks_text)  # Копируем их в буфер обмена
            self.statusBar().showMessage("Выбранные замечания скопированы в буфер обмена.", 3000)

    def clear_remark_list(self):
        """Очищает весь список замечаний."""
        #TODO: Очищать список замечаний на открытой вкладке, а не "Все". Если открыта "Все", то очищать все списки.
        if self.ui.allTabListWidget.count() > 0:  # Только если есть элементы
            self.ui.allTabListWidget.clear()
            self.is_modified = True  # Файл изменился
            self.update_window_title()  # Обновляем заголовок
            self.statusBar().showMessage("Список замечаний очищен.", 3000)

    def toggle_remark_buttons(self):
        """Включает (отключает) кнопки взаимодействия с замечанием, если сейчас оно (не) выбрано."""
        # TODO: Сейчас работает только на вкладке "Все". Распространить логику работы и на остальные вкладки.
        # TODO: Соответственно, при переключении между вкладками, кнопки могут то включаться, то выключаться,
        # TODO: если на какой-то вкладке в текущий момент есть выбранные замечания, а на другой нет. Если по каким-то
        # TODO: причинам настроить это включение/выключение при переходе по вкладкам окажется сложно, можно убрать его
        # TODO: вообще. В таком случае тщательно проверить, что не возникает багов при нажатии на эти кнопки в тех
        # TODO: случаях, когда никакие замечания не выбраны.
        self.ui.remarkRemoveButton.setEnabled(bool(self.ui.allTabListWidget.selectedItems()))
        self.ui.remarkEditButton.setEnabled(bool(self.ui.allTabListWidget.selectedItems()))
        self.ui.remarkCopyButton.setEnabled(bool(self.ui.allTabListWidget.selectedItems()))

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