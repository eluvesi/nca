import sys
import json
import os

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QListWidget, QListWidgetItem
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
        self.ui.tabRemoveButton.clicked.connect(self.remove_tab)
        # Подключаем реакции на взаимодействие пользователя со списками на вкладках (клики, выделения)
        self.set_tab_list_connects()  # На изначально открытой вкладке "Все"
        self.ui.tabWidget.currentChanged.connect(self.set_tab_list_connects)  # При переключении на другую вкладку тоже
        # Подключаем действия при нажатии на кнопки под списком
        self.ui.remarkAddButton.clicked.connect(self.add_remark)
        self.ui.remarkRemoveButton.clicked.connect(self.remove_remark)
        self.ui.remarkEditButton.clicked.connect(self.edit_remark)
        self.ui.remarkCopyButton.clicked.connect(self.copy_remark)
        self.ui.remarkListClearButton.clicked.connect(self.clear_tab_list)
        # Подключаем включение/выключение кнопок удаления и редактирования вкладки при переходе с/на "Все"
        self.toggle_tab_buttons()  # Изначально выключаем кнопки
        self.ui.tabWidget.currentChanged.connect(self.toggle_tab_buttons)  # Переключаем при переходах
        # Подключаем включение/выключение кнопок взаимодействия с замечаниями при перемещении между вкладками
        self.ui.tabWidget.currentChanged.connect(self.toggle_remark_buttons)  # Переключаем при переходах

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
        # Обновляем состояние
        self.current_file = None  # Обновляем текущий файл
        self.is_modified = False  # Создан новый файл, изменений больше нет
        self.update_window_title()  # Обновляем заголовок окна
        self.ui.allTabListWidget.clear()  # Очищаем общий список замечаний
        self.remove_all_tabs()  # Удаляем все вкладки
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
            self.current_file = filename  # Заменяем текущий файл на новый
            self.settings.setValue("last_file", self.current_file)  # Запоминаем в качестве последнего открытого файла
            self.load_file()  # Загружаем новый файл

    def load_file(self):
        """Загружает текущий файл и обновляет состояние."""
        self.is_modified = False  # Новый файл загружен, изменений нет
        self.update_window_title()  # Обновляем заголовок окна
        self.ui.allTabListWidget.clear()  # Очищаем общий список замечаний
        self.remove_all_tabs()  # Удаляем все вкладки
        # Загружаем по-разному в зависимости от формата
        if self.current_file.endswith(".txt"):  # Загружаем новый список замечаний из txt-файла
            self.load_from_txt()
        elif self.current_file.endswith(".json"):  # Загружаем новый список замечаний из json-файла
            self.load_from_json()

    def load_from_txt(self):
        """Загружает замечания из txt-файла и добавляет их в список."""
        try:
            with open(self.current_file, "r", encoding="utf-8") as file:
                remarks = file.read().splitlines()  # Каждую новую строку воспринимаем как отдельное замечание
                category = "Без категории" # так как .txt-файлы не поддерживают категории, всё заносим в "Без категории"
                tab_list_widget = QListWidget()
                self.ui.tabWidget.addTab(tab_list_widget, category)
                for text in remarks:
                    if not text.strip():
                        continue  # Не добавляем пустые замечания
                    # Создаём элемент списка
                    item = QListWidgetItem(text)  # Текст замечания (очередная строка .txt-файла)
                    item.setData(Qt.UserRole, category)  # Категория (в данном случае всегда "Без категории")
                    # Добавляем этот элемент в два списка
                    tab_list_widget.addItem(item)  # Добавляем в список на вкладке категории
                    self.ui.allTabListWidget.addItem(item.clone())  # Клона добавляем в список на вкладке "Все"
                self.statusBar().showMessage(f"Замечания загружены из {self.current_file}.", 3000)
        except FileNotFoundError:
            self.statusBar().showMessage(f"Не удалось найти файл {self.current_file}.", 3000)

    def load_from_json(self):
        """Загружает замечания и категории из json-файла, создаёт и заполняет вкладки."""
        try:
            with open(self.current_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                for category, remarks in data.items():
                    # Создаем вкладку со списком замечаний для каждой категории
                    tab_list_widget = QListWidget()
                    self.ui.tabWidget.addTab(tab_list_widget, category)
                    # Каждое замечание добавляем сразу в два списка
                    for text in remarks:
                        if not text.strip():
                            continue  # Не добавляем пустые замечания
                        # Создаём элемент списка
                        item = QListWidgetItem(text)  # Текст замечания
                        item.setData(Qt.UserRole, category)  # Категория
                        # Добавляем этот элемент в два списка
                        tab_list_widget.addItem(item)  # Добавляем в список на вкладке категории
                        self.ui.allTabListWidget.addItem(item.clone())  # Клона добавляем в список на вкладке "Все"
                self.statusBar().showMessage(f"Замечания загружены из {self.current_file}.", 3000)
        except (FileNotFoundError, json.JSONDecodeError):
            self.statusBar().showMessage(f"Не удалось найти файл {self.current_file}.", 3000)

    def save_file(self):
        """Сохраняет изменения в текущем файле. Если файл .txt и есть категории — предупреждает о потере категорий."""
        if self.current_file:  # Если не None, значит был открыт какой-то файл, сохраним изменения
            if self.current_file.endswith(".json"):  # Если .json - сохраняем в json
                self.save_to_json(self.current_file)
            elif self.current_file.endswith(".txt"):  # Если .txt, произойдёт потеря категорий, проверим их наличие
                has_categories = self.ui.tabWidget.tabBar().count() > 2  # Есть вкладки помимо "Все" и "Без категории"?
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
        """Открывает диалог для сохранения файла с новым именем. После сохранения загружает новый файл."""
        # Открытие диалога для выбора пути и формата файла
        filename, file_ext = QFileDialog.getSaveFileName(
            self, "Сохранить как", "", "JSON-файлы (*.json);;Текстовые файлы (*.txt)"
        )
        if filename:  # Если путь валидный, определяем формат, в который нужно сохранить
            if file_ext == "JSON-файлы (*.json)":
                # Если .json - сохраняем в json
                self.save_to_json(filename)
            elif file_ext == "Текстовые файлы (*.txt)":
                # Если .txt, может произойти потеря категорий, проверим их наличие
                has_categories = self.ui.tabWidget.tabBar().count() > 2  # Есть вкладки помимо "Все" и "Без категории"?
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
            self.current_file = filename  # Заменяем текущий файл на новый
            self.settings.setValue("last_file", self.current_file)  # Запоминаем в качестве последнего открытого файла
            self.load_file()  # Загружаем новый файл

    def save_to_txt(self, filename):
        """Сохраняет все замечания в .txt-файл. Информация о категориях не сохраняется."""
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
        """Сохраняет все замечания в .json-файл. Информация о категориях сохраняется."""
        # Будем заполнять data для сохранения в .json-файл
        data = {}
        # Проходимся по всем вкладкам (категориям), кроме вкладки "Все" (так как нет такой категории)
        for i in range(self.ui.tabWidget.count()):
            tab_name = self.ui.tabWidget.tabText(i)
            if tab_name == "Все":
                continue  # Вкладку "Все" не сохраняем отдельно
            # На каждой вкладке пройдёмся по списку замечаний заполняя массив remarks
            tab_list_widget = self.ui.tabWidget.widget(i)
            remarks = []
            for j in range(tab_list_widget.count()):
                text = tab_list_widget.item(j).text()
                remarks.append(text)
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
        if not dialog.exec():
            return
        text, category = dialog.get_data()
        if not text.strip():
            return  # Не добавляем пустые замечания
        if not category.strip():
            category = "Без категории"
        # Проверяем, существует ли вкладка с таким названием
        existing_categories = [self.ui.tabWidget.tabText(i) for i in range(self.ui.tabWidget.count())]
        tab_list_widget = None
        if category not in existing_categories:
            # Если нет, создаём новую вкладку со списком tab_list_widget
            tab_list_widget = QListWidget()
            self.ui.tabWidget.addTab(tab_list_widget, category)
        else:
            # Ищем среди вкладок нужную
            for i in range(self.ui.tabWidget.count()):
                if self.ui.tabWidget.tabText(i) == category:
                    # Когда нашли, в переменную tab_list_widget сохраняем список с этой вкладки
                    tab_list_widget = self.ui.tabWidget.widget(i)
                    break
        # Создаём элемент списка
        item = QListWidgetItem(text)  # Текст, введённый пользователем, сохраняем в качестве текста элемента
        item.setData(Qt.UserRole, category)  # Категорию, выбранную пользователем, сохраняем в data элемента
        # Добавляем этот элемент в два списка
        tab_list_widget.addItem(item)  # Добавляем в список на вкладке выбранной категории
        self.ui.allTabListWidget.addItem(item.clone())  # Клонируем и добавляем клона в список на вкладке "Все"
        # Обновляем состояние
        self.is_modified = True  # Файл изменился
        self.update_window_title()  # Обновляем заголовок
        self.statusBar().showMessage("Добавлено новое замечание.", 3000)

    def remove_remark(self):
        """Удаляет выбранное замечание из текущей вкладки и из всех соответствующих вкладок."""
        # Определяем текущую вкладку
        current_index = self.ui.tabWidget.currentIndex()
        tab_name = self.ui.tabWidget.tabText(current_index)
        # Определяем, с каким списком работаем
        tab_list_widget = self.ui.allTabListWidget if tab_name == "Все" else self.ui.tabWidget.widget(current_index)
        # Определяем, какие элементы выделены
        selected_items = tab_list_widget.selectedItems()
        if not selected_items:
            return
        # Для каждого выбранного замечания
        for item in selected_items:
            text = item.text()  # Запоминаем текст замечания
            category = item.data(Qt.UserRole)  # Запоминаем категорию замечания
            # Удаляем клона замечания со вкладки "Все"
            for i in reversed(range(self.ui.allTabListWidget.count())):
                all_tab_item = self.ui.allTabListWidget.item(i)
                if all_tab_item.text() == text and all_tab_item.data(Qt.UserRole) == category:
                    self.ui.allTabListWidget.takeItem(i)  # Удаляем клона на вкладке "Все"
                    break
            # Если мы на вкладке "Все", ищем и удаляем оригинал замечания
            if tab_name == "Все":
                for i in range(self.ui.tabWidget.count()):
                    # Ищем вкладку, на которой находится оригинал, по категории
                    if self.ui.tabWidget.tabText(i) == category:
                        tab_list_widget = self.ui.tabWidget.widget(i)
                        for j in reversed(range(tab_list_widget.count())):
                            # Ищем само замечание по тексту
                            if tab_list_widget.item(j).text() == text:
                                tab_list_widget.takeItem(j)  # Удаляем оригинал замечания
                                break
                        break
            # Иначе мы уже на нужной вкладке, просто удаляем оригинал
            else:
                tab_list_widget.takeItem(tab_list_widget.row(item))  # Удаляем оригинал замечания
        # Обновляем состояние
        self.is_modified = True  # Файл изменился
        self.update_window_title()  # Обновляем заголовок
        self.statusBar().showMessage("Выбранные замечания удалены.", 3000)

    def edit_remark(self):
        """Поочерёдно открывает окна для редактирования выбранных замечаний."""
        # Определяем текущую вкладку
        current_index = self.ui.tabWidget.currentIndex()
        tab_name = self.ui.tabWidget.tabText(current_index)
        # Определяем, с каким списком работаем
        tab_list_widget = self.ui.allTabListWidget if tab_name == "Все" else self.ui.tabWidget.widget(current_index)
        # Определяем, какие элементы выделены
        selected_items = tab_list_widget.selectedItems()
        if not selected_items:
            return
        # Для каждого выбранного замечания
        for item in selected_items:
            old_text = item.text()  # Запоминаем старый текст
            old_category = item.data(Qt.UserRole)  # Запоминаем старую категорию
            dialog = RemarkDialog(self, text=old_text, category=old_category)  # Открываем окно редактирования
            if not dialog.exec():
                continue  # Если пользователь нажал "Отмена" или просто закрыл окно, то ничего не делаем
            new_text, new_category = dialog.get_data()  # Иначе получаем новые данные
            if not new_text.strip():
                continue  # Не добавляем пустые замечания
            if not new_category.strip():
                new_category = "Без категории"
            # Находим клона замечания на вкладке "Все" и обновляем его данные
            for i in range(self.ui.allTabListWidget.count()):
                all_tab_item = self.ui.allTabListWidget.item(i)
                if all_tab_item.text() == old_text and all_tab_item.data(Qt.UserRole) == old_category:
                    all_tab_item.setText(new_text)  # Обновляем текст
                    all_tab_item.setData(Qt.UserRole, new_category)  # Обновляем категорию
                    break
            # Если мы на вкладке "Все", ищем и обновляем оригинал замечания
            if tab_name == "Все":
                for i in range(self.ui.tabWidget.count()):
                    # Ищем вкладку, на которой находится оригинал, и удаляем его оттуда, либо просто меняем текст
                    if self.ui.tabWidget.tabText(i) == old_category:
                        tab_list_widget = self.ui.tabWidget.widget(i)
                        for j in reversed(range(tab_list_widget.count())):
                            # Ищем само замечание по тексту
                            if tab_list_widget.item(j).text() == old_text:
                                if new_category == old_category:
                                    tab_list_widget.item(j).setText(new_text)  # Меняем текст оригинала замечания
                                else:
                                    tab_list_widget.takeItem(j)  # Удаляем оригинал замечания
                                break
                        break
                # Если категория изменилась, то добавляем в новую, иначе ничего
                if new_category != old_category:
                    for i in range(self.ui.tabWidget.count()):
                        # Ищем вкладку, куда нужно перенести оригинал, и добавляем его туда
                        if self.ui.tabWidget.tabText(i) == new_category:
                            new_item = QListWidgetItem(new_text)  # Создаём элемент списка, записываем текст
                            new_item.setData(Qt.UserRole, new_category)  # Записываем категорию
                            self.ui.tabWidget.widget(i).addItem(new_item)  # Добавляем элемент в список
                            break
            # Иначе мы уже на нужной вкладке, просто обновляем оригинал
            else:
                # Если категория не изменилась, то просто меняем текст
                if new_category == old_category:
                    item.setText(new_text)
                # Иначе удаляем из старой категории и добавляем в новую
                else:
                    tab_list_widget.takeItem(tab_list_widget.row(item))
                    for i in range(self.ui.tabWidget.count()):
                        # Ищем вкладку, куда нужно перенести замечание
                        if self.ui.tabWidget.tabText(i) == new_category:
                            new_item = QListWidgetItem(new_text)  # Создаём элемент списка, записываем текст
                            new_item.setData(Qt.UserRole, new_category)  # Записываем категорию
                            self.ui.tabWidget.widget(i).addItem(new_item)  # Добавляем элемент в список
                            break
        # Обновляем состояние
        self.is_modified = True  # Файл изменился
        self.update_window_title()  # Обновляем заголовок
        self.statusBar().showMessage("Замечание обновлено.", 3000)

    def copy_remark(self):
        """Копирует выбранные замечания в буфер обмена."""
        # Определяем текущую вкладку
        current_index = self.ui.tabWidget.currentIndex()
        tab_name = self.ui.tabWidget.tabText(current_index)
        # Определяем, с каким списком работаем
        tab_list_widget = self.ui.allTabListWidget if tab_name == "Все" else self.ui.tabWidget.widget(current_index)
        # Определяем, какие элементы выделены
        selected_items = tab_list_widget.selectedItems()
        if selected_items:
            remarks_text = "\n".join(item.text() for item in selected_items)
            QApplication.clipboard().setText(remarks_text)
            self.statusBar().showMessage("Выбранные замечания скопированы в буфер обмена.", 3000)

    def remove_tab(self):
        """Удаляет открытую вкладку и все замечания, которые на ней были, со вкладки "Все"."""
        current_index = self.ui.tabWidget.currentIndex()
        tab_name = self.ui.tabWidget.tabText(current_index)
        if tab_name != "Все":
            tab_list_widget = self.ui.tabWidget.widget(current_index)
            for i in range(tab_list_widget.count()):
                # Для каждого замечания на текущей вкладке
                text = tab_list_widget.item(i).text()
                for j in reversed(range(self.ui.allTabListWidget.count())):
                    # Ищем на вкладке "Все" это же самое замечание
                    if self.ui.allTabListWidget.item(j).text() == text:
                        self.ui.allTabListWidget.takeItem(j)  # И удаляем его с вкладки "Все"
                        break
            self.ui.tabWidget.removeTab(current_index) # Удаляем текущую вкладку
            # Обновляем состояние
            self.is_modified = True  # Файл изменился
            self.update_window_title()  # Обновляем заголовок
            self.statusBar().showMessage(f"Вкладка \"{tab_name}\" удалена.", 3000)

    def remove_all_tabs(self):
        """Удаляет все вкладки категорий, кроме вкладки "Все"."""
        for i in reversed(range(self.ui.tabWidget.count())):
            if self.ui.tabWidget.tabText(i) != "Все":
                self.ui.tabWidget.removeTab(i)

    def clear_all_lists(self):
        """Очищает списки замечаний на всех вкладках категорий, не удаляя сами вкладки."""
        # Очищаем общий список
        self.ui.allTabListWidget.clear()
        # Очищаем списки на остальных вкладках
        for i in reversed(range(self.ui.tabWidget.count())):
            if self.ui.tabWidget.tabText(i) != "Все":
                self.ui.tabWidget.widget(i).clear()

    def clear_tab_list(self):
        """Очищает список замечаний на текущей вкладке. На вкладке "Все" очищает списки на всех вкладках."""
        current_index = self.ui.tabWidget.currentIndex()
        tab_name = self.ui.tabWidget.tabText(current_index)
        if tab_name == "Все":
            # На вкладке "Все" - очищаем всё, что только можно
            self.clear_all_lists()
        else:
            # На других вкладках - очищаем список на этой вкладке, и удаляем эти замечания со вкладки "Все"
            tab_list_widget = self.ui.tabWidget.widget(current_index)
            for i in range(tab_list_widget.count()):
                # Для каждого замечания на текущей вкладке
                text = tab_list_widget.item(i).text()
                for j in reversed(range(self.ui.allTabListWidget.count())):
                    # Ищем на вкладке "Все" это же самое замечание
                    if self.ui.allTabListWidget.item(j).text() == text:
                        self.ui.allTabListWidget.takeItem(j)  # И удаляем его с вкладки "Все"
                        break
            tab_list_widget.clear()  # Когда замечания со вкладки "Все" удалили, очищаем список на текущей вкладке
        # Обновляем состояние
        self.is_modified = True  # Файл изменился
        self.update_window_title()  # Обновляем заголовок
        self.statusBar().showMessage(f"Список замечаний на вкладке \"{tab_name}\" очищен.", 3000)

    def set_tab_list_connects(self):
        """Подключает реакции на действия пользователя (клики, выделения) для виджета списка на открываемой вкладке."""
        # Определяем текущую вкладку
        current_index = self.ui.tabWidget.currentIndex()
        tab_name = self.ui.tabWidget.tabText(current_index)
        # Определяем, с каким списком работаем
        tab_list_widget = self.ui.allTabListWidget if tab_name == "Все" else self.ui.tabWidget.widget(current_index)
        # Подключаем реакции на действия пользователя для этого списка
        if isinstance(tab_list_widget, QListWidget):
            tab_list_widget.setSelectionMode(QListWidget.ExtendedSelection)  # Множественное выделение
            tab_list_widget.itemSelectionChanged.connect(self.toggle_remark_buttons)  # Вкл/выкл кнопки замечаний
            tab_list_widget.setContextMenuPolicy(Qt.CustomContextMenu)  # Включаем реакцию на ПКМ
            tab_list_widget.customContextMenuRequested.connect(
                lambda: self.copy_remark() if tab_list_widget.selectedItems() else None
            )  # Устанавливаем копирование в качестве реакции на ПКМ

    def toggle_remark_buttons(self):
        """Включает (отключает) кнопки взаимодействия с замечанием, если сейчас оно (не) выбрано."""
        # Определяем текущую вкладку
        current_index = self.ui.tabWidget.currentIndex()
        tab_name = self.ui.tabWidget.tabText(current_index)
        # Определяем, с каким списком работаем
        tab_list_widget = self.ui.allTabListWidget if tab_name == "Все" else self.ui.tabWidget.widget(current_index)
        # Если ничего не выбрано, то отключаем кнопки удаления и редактирования замечаний, иначе включаем
        has_selection = bool(tab_list_widget.selectedItems()) if isinstance(tab_list_widget, QListWidget) else False
        self.ui.remarkRemoveButton.setEnabled(has_selection)
        self.ui.remarkEditButton.setEnabled(has_selection)
        self.ui.remarkCopyButton.setEnabled(has_selection)

    def toggle_tab_buttons(self):
        """Отключает (включает) кнопки взаимодействия со вкладкой, если это (не) вкладка "Все"."""
        # Определяем текущую вкладку
        current_index = self.ui.tabWidget.currentIndex()
        tab_name = self.ui.tabWidget.tabText(current_index)
        # Вкладку "Все" нельзя переименовать и удалить, для неё отключаем эти кнопки, для остальных включаем
        self.ui.tabRemoveButton.setEnabled(bool(tab_name != "Все"))
        self.ui.tabEditButton.setEnabled(bool(tab_name != "Все"))

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