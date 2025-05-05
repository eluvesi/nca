import sys
import json
import os

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QListWidget
from PyQt5.QtCore import QSettings, Qt
from ui_main_window import Ui_MainWindow
from remark_dialog import RemarkDialog
import traceback
import sys
sys.excepthook = lambda exctype, value, tb: traceback.print_exception(exctype, value, tb)


class MainWindow(QMainWindow):
    """Главное окно приложения."""
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.is_modified = False  # Флаг несохранённых изменений в текущем файле
        self.settings = QSettings("eluvesi", "NCA")  # Используем QSettings для хранения последнего открытого файла
        last_file = self.settings.value("last_file", "")  # Узнаём путь к последнему открытому файлу

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

        # Подключаем действия при нажатии на кнопки в верхнем меню
        self.ui.fileCreateButton.clicked.connect(self.create_new_file)
        self.ui.fileOpenButton.clicked.connect(self.open_file)
        self.ui.fileSaveButton.clicked.connect(self.save_file)
        self.ui.fileSaveAsButton.clicked.connect(self.save_file_as)
        # Подключаем реакции на взаимодействие пользователя со списками (клики, выделения)
        self.update_tab_connections()  # На изначально открытой вкладке "Все"
        self.ui.tabWidget.currentChanged.connect(self.update_tab_connections)  # И на других вкладках при переходе
        # Подключаем действия при нажатии на кнопки под списком
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
        self.clear_all_lists()  # Очищаем список замечаний
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
            # Обновляем состояние
            self.current_file = filename  # Обновляем текущий файл
            self.is_modified = False  # Открыт другой файл, изменений больше нет
            self.update_window_title()  # Обновляем заголовок окна
            self.settings.setValue("last_file", self.current_file)  # Запоминаем в качестве последнего открытого файла
            self.clear_all_lists()  # Очищаем список замечаний
            # Загружаем по-разному в зависимости от формата
            if filename.endswith(".txt"):  # Загружаем новый список замечаний из txt-файла
                self.load_from_txt()
            elif filename.endswith(".json"):  # Загружаем новый список замечаний из json-файла
                self.load_from_json()

    def load_from_txt(self):
        """Загружает замечания из txt-файла и добавляет их в список."""
        try:
            with open(self.current_file, "r", encoding="utf-8") as file:
                # Так как .txt-файлы не поддерживают категории, все замечания заносим в "Без категории"
                tab_list_widget = QListWidget()
                self.ui.tabWidget.addTab(tab_list_widget, "Без категории")
                # Каждое замечание добавляем сразу в два списка
                remarks = file.read().splitlines()
                tab_list_widget.addItems(remarks)  # В список на вкладке "Без категории"
                self.ui.allTabListWidget.addItems(remarks)  # В список на вкладке "Все"
                self.statusBar().showMessage(f"Замечания загружены из {self.current_file}.", 3000)
        except FileNotFoundError:
            self.statusBar().showMessage(f"Не удалось найти файл {self.current_file}.", 3000)

    def load_from_json(self):
        """Загружает замечания и категории из json-файла, создаёт и заполняет вкладки."""
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
        """Сохраняет изменения в текущем файле. Если файл .txt и есть категории — предупреждает о потере категорий."""
        if self.current_file:  # Если не None, значит был открыт какой-то файл, сохраним изменения
            if self.current_file.endswith(".json"):  # Если .json - сохраняем в json
                self.save_to_json(self.current_file)
            elif self.current_file.endswith(".txt"):  # Если .txt, произойдёт потеря категорий, проверим их наличие
                has_categories = self.ui.tabWidget.tabBar().count() > 1  # Проверка наличия вкладок помимо "Все"
                if has_categories:  # Если они были, спрашиваем пользователя, готов ли он их потерять
                    reply = QMessageBox.warning(
                        self,
                        "Потеря категорий",
                        "Формат файла .txt не поддерживает категории.\n"
                        "Если вы сохраните в этом формате, структура категорий будет потеряна.\n"
                        "Вы уверены, что хотите продолжить?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if reply == QMessageBox.No:
                        return  # Пользователь отменил сохранение
                # Если пользователь подтвердил сохранение, либо категорий не было, то сохраняем в .txt
                self.save_to_txt(self.current_file)
            # Обновляем состояние
            self.is_modified = False  # Файл сохранён, изменений больше нет
            self.update_window_title()  # Обновляем заголовок окна
        else:  # Если None, значит был создан новый файл
            self.save_file_as()  # Предлагаем пользователю сохранить файл как (выбрать имя для сохранения)

    def save_file_as(self):
        """Открывает диалог для сохранения файла с новым именем."""
        # Открытие диалога для выбора пути и формата файла
        filename, file_ext = QFileDialog.getSaveFileName(
            self, "Сохранить как", "", "Текстовые файлы (*.txt);;JSON-файлы (*.json)"
        )
        if filename:  # Если путь валидный, определяем формат, в который нужно сохранить
            if file_ext == "JSON-файлы (*.json)":
                # Если .json - сохраняем в json
                self.save_to_json(filename)
            elif file_ext == "Текстовые файлы (*.txt)":
                # Если .txt, может произойти потеря категорий, проверим их наличие
                has_categories = self.ui.tabWidget.tabBar().count() > 1  # Проверка наличия вкладок помимо "Все"
                if has_categories:  # Если они были, спрашиваем пользователя, готов ли он их потерять
                    reply = QMessageBox.warning(
                        self,
                        "Потеря категорий",
                        "Формат файла .txt не поддерживает категории.\n"
                        "Если вы сохраните в этом формате, структура категорий будет потеряна.\n"
                        "Вы уверены, что хотите продолжить?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if reply == QMessageBox.No:
                        return  # Пользователь отменил сохранение
                # Если пользователь подтвердил сохранение, либо категорий не было, то сохраняем в .txt
                self.save_to_txt(filename)
            # Обновляем состояние
            self.current_file = filename  # Обновляем текущий файл
            self.is_modified = False  # Файл сохранён, изменений больше нет
            self.update_window_title()  # Обновляем заголовок окна
            self.settings.setValue("last_file", self.current_file)  # Запоминаем в качестве последнего открытого файла

    def save_to_txt(self, filename):
        """Сохраняет список замечаний со вкладки "Все" в txt-файл."""
        try:
            with open(filename, "w", encoding="utf-8") as file:
                for row in range(self.ui.allTabListWidget.count()):
                    file.write(self.ui.allTabListWidget.item(row).text() + "\n")
            self.statusBar().showMessage(f"Замечания сохранены в {filename}.", 3000)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка при сохранении",
                f"Не удалось сохранить файл:\n{str(e)}"
            )

    def save_to_json(self, file_path):
        """Сохраняет замечания из всех вкладок (кроме 'Все') в JSON-формате."""
        # Будем заполнять data для сохранения в .json-файл
        data = {}
        # Проходимся по всем вкладкам (категориям), кроме вкладки "Все" (т.к. нет такой категории)
        for i in range(self.ui.tabWidget.count()):
            tab_name = self.ui.tabWidget.tabText(i)
            if tab_name == "Все":
                continue  # Вкладку "Все" не сохраняем отдельно
            # На каждой вкладке пройдёмся по списку замечаний заполняя массив remarks
            tab_list_widget = self.ui.tabWidget.widget(i)
            remarks = []
            for j in range(tab_list_widget.count()):
                item_text = tab_list_widget.item(j).text()
                remarks.append(item_text)
            data[tab_name] = remarks  # Используем категорию как ключ в data
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            self.statusBar().showMessage(f"Замечания сохранены в {file_path}.", 3000)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка при сохранении",
                f"Не удалось сохранить файл:\n{str(e)}"
            )

    def add_remark(self):
        """Открывает окно для добавления нового замечания в список."""
        dialog = RemarkDialog(self)
        if dialog.exec():
            text, category = dialog.get_data()
            if not text.strip():
                return  # Не добавляем пустые замечания
            if not category.strip():
                category = "Без категории"
            # Проверим, существует ли вкладка с таким названием
            existing_categories = [self.ui.tabWidget.tabText(i) for i in range(self.ui.tabWidget.count())]
            if category not in existing_categories:
                # Если нет, создаём новую вкладку со списком
                tab_list_widget = QListWidget()
                self.ui.tabWidget.addTab(tab_list_widget, category)
            else:
                # Иначе ищем среди всех вкладок нужную
                for i in range(self.ui.tabWidget.count()):
                    if self.ui.tabWidget.tabText(i) == category:
                        # Когда нашли, в tab_list_widget заносим список с этой вкладки
                        tab_list_widget = self.ui.tabWidget.widget(i)
                        break
            tab_list_widget.addItem(text)  # Добавляем замечание в список на вкладке выбранной категории
            self.ui.allTabListWidget.addItem(text)  # Добавляем замечание в список на вкладке "Все"
            # Обновим состояние
            self.is_modified = True  # Файл изменился
            self.update_window_title()  # Обновляем заголовок
            self.statusBar().showMessage("Добавлено новое замечание.", 3000)

    def remove_remark(self):
        """Удаляет выбранное замечание из текущей вкладки и из всех соответствующих вкладок."""
        current_index = self.ui.tabWidget.currentIndex()
        current_tab = self.ui.tabWidget.widget(current_index)
        current_tab_name = self.ui.tabWidget.tabText(current_index)

        selected_items = current_tab.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            text = item.text()

            # Удалить из текущей вкладки
            current_tab.takeItem(current_tab.row(item))

            # Удалить из вкладки "Все", если мы не на ней
            if current_tab_name != "Все":
                for i in range(self.ui.allTabListWidget.count()):
                    if self.ui.allTabListWidget.item(i).text() == text:
                        self.ui.allTabListWidget.takeItem(i)
                        break
            else:
                # Если мы на вкладке "Все", удалить из всех остальных вкладок
                for i in range(self.ui.tabWidget.count()):
                    tab_name = self.ui.tabWidget.tabText(i)
                    if tab_name != "Все":
                        tab_widget = self.ui.tabWidget.widget(i)
                        for j in range(tab_widget.count()):
                            if tab_widget.item(j).text() == text:
                                tab_widget.takeItem(j)
                                break

        self.is_modified = True
        self.update_window_title()
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
        current_index = self.ui.tabWidget.currentIndex()
        tab_name = self.ui.tabWidget.tabText(current_index)
        if tab_name == "Все":
            tab_list_widget = self.ui.allTabListWidget
        else:
            tab_list_widget = self.ui.tabWidget.widget(current_index)
        if isinstance(tab_list_widget, QListWidget):
            selected_items = tab_list_widget.selectedItems()
            if selected_items:
                remarks_text = "\n".join(item.text() for item in selected_items)
                QApplication.clipboard().setText(remarks_text)
                self.statusBar().showMessage("Выбранные замечания скопированы в буфер обмена.", 3000)

    def clear_all_lists(self):
        """Удаляет все замечания и сбрасывает вкладки категорий"""
        # Очищаем общий список
        self.ui.allTabListWidget.clear()
        # Удаляем все вкладки категорий, кроме "Все"
        for i in reversed(range(self.ui.tabWidget.count())):
            if self.ui.tabWidget.tabText(i) != "Все":
                self.ui.tabWidget.removeTab(i)

    def clear_remark_list(self):
        """Очищает весь список замечаний."""
        #TODO: Очищать список замечаний на открытой вкладке, а не "Все". Если открыта "Все", то очищать все списки.
        if self.ui.allTabListWidget.count() > 0:  # Только если есть элементы
            self.ui.allTabListWidget.clear()
            self.is_modified = True  # Файл изменился
            self.update_window_title()  # Обновляем заголовок
            self.statusBar().showMessage("Список замечаний очищен.", 3000)

    def update_tab_connections(self):
        """Подключает реакции на действия пользователя (клики, выделения) для виджета списка на открываемой вкладке."""
        current_index = self.ui.tabWidget.currentIndex()
        tab_name = self.ui.tabWidget.tabText(current_index)
        if tab_name == "Все":
            tab_list_widget = self.ui.allTabListWidget
        else:
            tab_list_widget = self.ui.tabWidget.widget(current_index)
        if isinstance(tab_list_widget, QListWidget):
            tab_list_widget.setSelectionMode(QListWidget.ExtendedSelection)
            tab_list_widget.itemSelectionChanged.connect(self.toggle_remark_buttons)
            tab_list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
            tab_list_widget.customContextMenuRequested.connect(
                lambda: self.copy_remark() if tab_list_widget.selectedItems() else None
            )

    def toggle_remark_buttons(self):
        """Включает (отключает) кнопки взаимодействия с замечанием, если сейчас оно (не) выбрано."""
        current_index = self.ui.tabWidget.currentIndex()
        tab_name = self.ui.tabWidget.tabText(current_index)
        # Так как виджет на вкладке "Все" - особенный, то к нему требуется особое отношение :)
        if tab_name == "Все":
            tab_list_widget = self.ui.allTabListWidget
        else:
            tab_list_widget = self.ui.tabWidget.widget(current_index)
        has_selection = bool(tab_list_widget.selectedItems()) if isinstance(tab_list_widget, QListWidget) else False
        self.ui.remarkRemoveButton.setEnabled(has_selection)
        self.ui.remarkEditButton.setEnabled(has_selection)
        self.ui.remarkCopyButton.setEnabled(has_selection)

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