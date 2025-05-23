import json
import os

from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QGuiApplication, QIcon, QKeySequence
from PyQt5.QtWidgets import (
    QMainWindow,
    QFileDialog,
    QMessageBox,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QShortcut,
    QTabBar,
)

from remark_dialog import RemarkDialog
from tab_dialog import TabDialog
from ui_main_window import Ui_MainWindow
from utils import resource_path


WAIT = 5000


class MainWindow(QMainWindow):
    """Главное окно приложения."""
    def __init__(self):
        """Конструктор класса MainWindow."""
        super().__init__(parent=None)  # Вызываем конструктор родительского класса QMainWindow
        self.ui = Ui_MainWindow()  # Подгружаем интерфейс
        self.ui.setupUi(self)  # Применяем его к текущему окну

        self.current_file = None # Инициализируем переменную, хранящую путь до текущего файла
        self.is_modified = False  # Инициализируем флаг несохранённых изменений в текущем файле
        self.settings = QSettings("eluvesi", "NCA")  # Загружаем сохранённые с помощью QSettings настройки
        last_file = self.settings.value("last_file", "")  # Из настроек узнаём путь к последнему файлу
        tag_panel_visible = self.settings.value("tag_panel_visible", False, type=bool)  # Видимость панели тегов
        self.tag_filter_mode = self.settings.value("tag_filter_mode", "AND")  # Режим фильтрации (И/ИЛИ)

        self.ui.tabWidget.setTabBar(LockedTabBar())  # Устанавливаем кастомный QTabBar с закреплёнными вкладками
        self.ui.tabWidget.setMovable(True)  # Включаем возможность перетаскивать вкладки

        self.summaryListWidget = QListWidget()  # Создаём список "Все"
        self.set_list_connects(self.summaryListWidget)  # Подключаем реакции на действия пользователя
        self.ui.tabWidget.insertTab(0, self.summaryListWidget, "Все")  # Создаём вкладку "Все"
        self.uncategorizedListWidget = QListWidget()  # Создаём список "Без категории"
        self.set_list_connects(self.uncategorizedListWidget)  # Подключаем реакции на действия пользователя
        self.ui.tabWidget.addTab(self.uncategorizedListWidget, "Без категории")  # Создаём вкладку "Без категории"

        # Работа с файлами
        self.ui.fileCreateButton.clicked.connect(self.create_file)  # Кнопка "Создать документ"
        self.ui.fileOpenButton.clicked.connect(self.open_file)  # Кнопка "Открыть документ"
        self.ui.fileSaveButton.clicked.connect(self.save_file)  # Кнопка "Сохранить документ"
        self.ui.fileSaveAsButton.clicked.connect(self.save_file_as)  # Кнопка "Сохранить документ как"
        self.ui.fileRevertButton.clicked.connect(self.revert_file)  # Кнопка "Отменить изменения"
        # Работа с вкладками
        self.ui.tabAddButton.clicked.connect(self.add_tab)  # Кнопка "Добавить вкладку"
        self.ui.tabRemoveButton.clicked.connect(self.remove_tab)  # Кнопка "Удалить вкладку"
        self.ui.tabEditButton.clicked.connect(self.edit_tab)  # Кнопка "Редактировать вкладку"
        self.ui.tabWidget.currentChanged.connect(self. tab_changed)  # При переходе на другую вкладку
        # Работа с замечаниями
        self.ui.remarkAddButton.clicked.connect(self.add_remark)  # Кнопка "Добавить замечание"
        self.ui.remarkRemoveButton.clicked.connect(self.remove_remark)  # Кнопка "Удалить выбранные замечания"
        self.ui.remarkEditButton.clicked.connect(self.edit_remark)  # Кнопка "Редактировать выбранные замечания"
        self.ui.remarkCopyButton.clicked.connect(self.copy_remark)  # Кнопка "Копировать выбранные замечания"
        self.ui.listClearButton.clicked.connect(self.clear_list)  # Кнопка "Очистить список"
        # Поиск
        self.ui.searchLineEdit.addAction(QIcon(resource_path("icons/find.png")), QLineEdit.LeadingPosition)  # Иконка
        self.ui.searchLineEdit.textChanged.connect(self.filter_remarks)  # Динамическая фильтрация при вводе запроса
        # Панель тегов
        self.ui.tagPanelWidget.setVisible(tag_panel_visible)  # Устанавливаем для панели состояние, взятое из настроек
        self.ui.tagPanelButton.setChecked(tag_panel_visible)  # И для кнопки панели тегов тоже
        self.ui.tagPanelButton.setToolTip("Скрыть панель тегов" if tag_panel_visible else "Показать панель тегов")
        self.ui.tagPanelButton.clicked.connect(self.toggle_tag_panel)  # Подключаем сворачивание/разворачивание панели
        self.ui.tagPanelAndButton.setChecked(self.tag_filter_mode == "AND")  # Устанавливаем состояние для кнопки "AND"
        self.ui.tagPanelAndButton.clicked.connect(lambda: self.set_tag_filter_mode("AND"))  # Переключение по нажатию
        self.ui.tagPanelOrButton.setChecked(self.tag_filter_mode == "OR")  # Устанавливаем состояние для кнопки "OR"
        self.ui.tagPanelOrButton.clicked.connect(lambda: self.set_tag_filter_mode("OR"))  # Переключение по нажатию
        self.ui.tagListWidget.itemPressed.connect(self.toggle_tag_checkbox)  # Установка чекбокса при клике на элемент
        self.ui.tagListWidget.itemChanged.connect(self.filter_remarks)  # Динамическая фильтрация при выборе тегов

        # Включаем шорткаты
        self.set_shortcuts()

        # Открываем последний редактируемый файл
        if last_file and os.path.exists(last_file):
            self.load_file(last_file)  # Если этот файл существует, то загружаем его
        else:
            self.create_file()  # Иначе создаём новый


    def load_file(self, filename):
        """Загружает переданный файл и обновляет состояние приложения."""
        # Очищаем интерфейс приложения перед загрузкой
        self.remove_user_tabs()  # Удаляем все вкладки, кроме вкладок "Все" и "Без категории"
        self.ui.tabWidget.setCurrentIndex(0)  # Переключаемся на вкладку "Все"
        # Загружаем файл по-разному в зависимости от формата
        load_success = False
        if filename.endswith(".txt"):  # Читаем список замечаний из txt-файла
            load_success = self.read_from_txt(filename)
        elif filename.endswith(".json"):  # Читаем список замечаний из json-файла
            load_success = self.read_from_json(filename)
        # Если успешно, то обновляем состояние
        if load_success:
            self.current_file = filename  # Устанавливаем файл в качестве текущего
            self.is_modified = False  # Файл только что загружен, изменений нет
            self.update_window_title()  # Обновляем заголовок окна
            self.update_tag_list()  # Обновляем список на панели тегов
            self.statusBar().showMessage(f"Замечания загружены из {self.current_file}.", WAIT)
        else:
            self.statusBar().showMessage(f"Не удалось загрузить файл {self.current_file}.", WAIT)

    def create_file(self):
        """Очищает интерфейс приложения и сбрасывает переменную, хранящую путь к текущему файлу."""
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
        self.remove_user_tabs()  # Удаляем все вкладки пользователя, и очищаем "Все" и "Без категории"
        self.is_modified = False  # Создан новый файл, изменений больше нет
        self.update_window_title()  # Обновляем заголовок окна
        self.update_tag_list()  # Обновляем список на панели тегов
        self.statusBar().showMessage("Создан новый файл. Не забудьте сохранить изменения.", WAIT)

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
        # Открываем диалог для выбора файла
        filename, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл с замечаниями", "", "Файлы замечаний (*.txt *.json)"
        )
        if filename and os.path.exists(filename):  # Если этот файл существует
            self.load_file(filename)  # Загружаем файл

    def read_from_txt(self, filename):
        """Считывает замечания из .txt-файла и добавляет их в единый список."""
        try:
            with open(filename, "r", encoding="utf-8") as file:
                remarks = file.read().splitlines()  # Каждую новую строку воспринимаем как отдельное замечание
                for text in remarks:
                    if not text.strip():
                        continue  # Не добавляем пустые замечания
                    # Создаём элемент списка
                    item = QListWidgetItem(text)  # Текст замечания (очередная строка .txt-файла)
                    item.setData(Qt.UserRole, "Без категории")  # Категория (для .txt всегда "Без категории")
                    item.setData(Qt.UserRole + 1, [])  # Теги (для .txt всегда пустой список)
                    # Добавляем этот элемент в два списка
                    self.uncategorizedListWidget.addItem(item)  # Добавляем в список на вкладке "Без категории"
                    self.summaryListWidget.addItem(item.clone())  # Клона добавляем в список на вкладке "Все"
            return True
        except FileNotFoundError:
            return False

    def read_from_json(self, filename):
        """Считывает замечания и категории из .json-файла, создаёт и заполняет вкладки."""
        try:
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)  # список словарей [{"category": ..., "text": ..., "tags": ...}]
                categories = {}  # Собираем категории
                for item in data:
                    category = item.get('category', "Без категории")  # Получаем категорию
                    text = item.get('text', "").strip()  # Получаем текст
                    tags = item.get('tags', [])  # Получаем теги
                    if not text:
                        continue  # Не добавляем пустые замечания
                    if category == "Без категории":  # Если в файле в качестве категории встретили "Без категории", то
                        list_widget = self.uncategorizedListWidget  # Берём в качестве list_widget уже имеющийся список
                    else:  # Для всех остальных категорий
                        if category not in categories:  # Если такую категорию встретили впервые
                            list_widget = QListWidget()  # Создаём новый список
                            self.set_list_connects(list_widget)  # Подключаем реакции для этого списка
                            self.ui.tabWidget.insertTab(self.ui.tabWidget.count() - 1, list_widget, category)  # Вкладка
                            categories[category] = list_widget  # Запоминаем список для повторных обращений
                        else:  # Если такую категорию уже встречали
                            list_widget = categories[category]  # Берём в качестве list_widget уже имеющийся список
                    # Создаём элемент списка
                    item = QListWidgetItem(text)  # Текст замечания
                    item.setData(Qt.UserRole, category)  # Категория
                    item.setData(Qt.UserRole + 1, tags)  # Теги
                    # Добавляем этот элемент в два списка
                    list_widget.addItem(item)  # Добавляем в список на вкладке категории
                    self.summaryListWidget.addItem(item.clone())  # Клона добавляем в список на вкладке "Все"
            return True
        except (FileNotFoundError, json.JSONDecodeError):
            return False

    def save_file(self):
        """Сохраняет изменения в текущем файле. Если файл .txt и есть категории — предупреждает о потере категорий."""
        if self.current_file:  # Если не None, значит был открыт какой-то файл, сохраним изменения
            if self.current_file.endswith(".json"):  # Если .json - сохраняем в json
                self.write_to_json(self.current_file)
            elif self.current_file.endswith(".txt"):  # Если .txt, произойдёт потеря категорий, проверим их наличие
                has_categories = self.ui.tabWidget.tabBar().count() > 2  # Есть вкладки помимо "Все" и "Без категории"?
                has_tags = bool(self.get_tab_tags(0))  # Есть ли теги? (bool: непустой список - True, [] - False)
                if not has_categories and not has_tags:  # Если вкладок и тегов нет, то записываем в .txt
                    self.write_to_txt(self.current_file)
                else:  # Если они были, спрашиваем пользователя, не хочет ли он сменить формат на .json
                    reply = QMessageBox.question(
                        self,
                        "Изменить формат?",
                        "В вашем документе есть категории и/или теги. При записи в .txt-файл они исчезнут.\n"
                        "Хотите изменить формат файла на .json?",
                        QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                        QMessageBox.Yes
                    )  # Окно с вариантами выбора: "да", "нет", "отмена"
                    if reply == QMessageBox.Yes:
                        new_filename = os.path.splitext(self.current_file)[0] + ".json"  # Имя файла с другим форматом
                        if os.path.exists(new_filename):
                            QMessageBox.critical(
                                self,
                                "Ошибка при сохранении файла",
                                f"В данной директории уже есть файл \"{os.path.basename(new_filename)}\".\n"
                                "Используйте опцию \"Сохранить как\" и выберите другое имя."
                            )
                            return  # Сохранить не удалось, выходим
                        os.rename(self.current_file, new_filename)  # Меняем расширение текущего файла на уровне ФС
                        self.current_file = new_filename  # Меняем на уровне приложения
                        self.write_to_json(self.current_file)  # Записываем в .json-файл
                    elif reply == QMessageBox.No:
                        self.write_to_txt(self.current_file)  # Записываем в .txt-файл
                    else:
                        return  # Пользователь отменил сохранение
            self.load_file(self.current_file)  # На всякий случай перезагрузим файл после сохранения
        else:  # Если None, значит был создан новый файл
            self.save_file_as()  # Предлагаем пользователю выбрать имя для сохранения

    def save_file_as(self):
        """Открывает диалог для сохранения файла с новым именем. После сохранения загружает новый файл."""
        # Открываем диалог для выбора пути и формата файла
        filename, file_ext = QFileDialog.getSaveFileName(
            self, "Сохранить как", "", "JSON-файлы (*.json);;Текстовые файлы (*.txt)"
        )
        if filename:  # Если путь валидный, определяем формат, в который нужно сохранить
            if file_ext == "JSON-файлы (*.json)":
                # Если .json - сохраняем в json
                self.write_to_json(filename)
            elif file_ext == "Текстовые файлы (*.txt)":
                # Если .txt, может произойти потеря категорий, проверим их наличие
                has_categories = self.ui.tabWidget.tabBar().count() > 2  # Есть вкладки помимо "Все" и "Без категории"?
                has_tags = bool(self.get_tab_tags(0))  # Есть ли теги? (bool: непустой список - True, [] - False)
                if not has_categories and not has_tags:  # Если таких вкладок нет, то записываем в .txt
                    self.write_to_txt(filename)
                else:  # Если они были, спрашиваем пользователя, не хочет ли он сменить формат на .json
                    reply = QMessageBox.question(
                        self,
                        "Изменить формат?",
                        "В вашем документе есть категории и/или теги. При записи в .txt-файл они исчезнут.\n"
                        "Хотите изменить формат файла на .json?",
                        QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                        QMessageBox.Yes
                    )  # Окно с вариантами выбора: "да", "нет", "отмена"
                    if reply == QMessageBox.Yes:
                        new_filename = os.path.splitext(filename)[0] + ".json"  # Имя файла с другим форматом
                        if os.path.exists(new_filename):
                            QMessageBox.critical(
                                self,
                                "Ошибка при сохранении файла",
                                f"В данной директории уже есть файл \"{os.path.basename(new_filename)}\".\n"
                                "Выберите другое имя или сначала удалите существующий файл."
                            )
                            return  # Сохранить не удалось, выходим
                        filename = new_filename
                        self.write_to_json(filename)  # Записываем в .json-файл
                    elif reply == QMessageBox.No:
                        self.write_to_txt(filename)  # Записываем в .txt-файл
                    else:
                        return  # Пользователь отменил сохранение
            self.load_file(filename)  # На всякий случай перезагрузим файл после сохранения

    def write_to_txt(self, filename):
        """Записывает все замечания в .txt-файл. Информация о категориях не сохраняется."""
        try:
            with open(filename, "w", encoding="utf-8") as file:
                for row in range(self.summaryListWidget.count()):  # Каждое замечание записываем с новой строки
                    file.write(self.summaryListWidget.item(row).text() + "\n")
            self.statusBar().showMessage(f"Замечания сохранены в {filename}.", WAIT)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка при сохранении файла", f"Не удалось сохранить файл:\n{str(e)}")

    def write_to_json(self, file_path):
        """Записывает все замечания в .json-файл. Информация о категориях сохраняется."""
        # Будем заполнять data для сохранения в .json-файл
        data = []
        # Проходимся по всем вкладкам (категориям), кроме вкладки "Все" (так как нет такой категории)
        for i in range(self.ui.tabWidget.count()):
            tab_name = self.ui.tabWidget.tabText(i)
            if tab_name == "Все":
                continue  # Вкладку "Все" не сохраняем отдельно
            # На каждой вкладке проходимся по списку замечаний заполняя массив remarks
            list_widget = self.ui.tabWidget.widget(i)
            for j in range(list_widget.count()):
                item = list_widget.item(j)  # Получаем элемент списка
                text = item.text()  # Получаем текст замечания
                tags = item.data(Qt.UserRole + 1) # Получаем теги
                data.append({
                    "category": tab_name,
                    "text": text,
                    "tags": tags
                })
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            self.statusBar().showMessage(f"Замечания сохранены в {file_path}.", WAIT)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка при сохранении файла", f"Не удалось сохранить файл:\n{str(e)}")

    def revert_file(self):
        """Отменяет все изменения в текущем файле, если у текущего файла есть сохранённая версия."""
        # Если пользователь работал с каким-то файлом на компьютере, и этот файл ещё на месте, то перезагружаем его
        if self.current_file and os.path.exists(self.current_file):
            self.load_file(self.current_file)  # Загружаем файл заново из сохранённой версии
            self.statusBar().showMessage(f"Восстановлено последнее сохранённое состояние файла.", WAIT)
        # Если пользователь работал с каким-то файлом на компьютере, и этого файла больше нет, то сообщаем об этом
        elif self.current_file and not os.path.exists(self.current_file):
            self.statusBar().showMessage(f"Файл не найден по старому пути, восстановить состояние не удалось.", WAIT)
        # Если пользователь создал новый файл и вносил изменения туда, то сообщаем пользователю об этом
        else:
            self.statusBar().showMessage(f"Вы работаете с новым файлом, у него нет сохранённой копии.", WAIT)


    def add_remark(self):
        """Открывает диалог для добавления нового замечания в список. В качестве категории предлагает текущую."""
        # Определяем текущую вкладку
        tab_name = self.ui.tabWidget.tabText(self.ui.tabWidget.currentIndex())
        if tab_name in ["Все", "Без категории"]:
            default_category = "Без категории"  # Для "Все" и "Без категории" по умолчанию предлагаем "Без категории"
        else:
            default_category = tab_name  # Для остальных вкладок по умолчанию предлагаем текущую вкладку
        dialog = RemarkDialog(self, category=default_category, tags=[])
        if not dialog.exec():
            return  # Если пользователь нажал "Отмена" или просто закрыл окно, то ничего не делаем
        text, category, tags = dialog.get_data()
        if not text:
            return  # Не добавляем пустые замечания
        # Ищем вкладку по категории
        for i in range(self.ui.tabWidget.count()):
            if self.ui.tabWidget.tabText(i) == category:
                # Когда нашли, в переменную list_widget сохраняем список с этой вкладки
                list_widget = self.ui.tabWidget.widget(i)
                break
        else:
            return  # Если не нашли (break не отработал), то выходим, но вообще такая ситуация невозможна
        # Создаём элемент списка
        item = QListWidgetItem(text)  # Текст, введённый пользователем, сохраняем в качестве текста элемента
        item.setData(Qt.UserRole, category)  # Категорию, выбранную пользователем, сохраняем в data элемента
        item.setData(Qt.UserRole + 1, tags)  # Теги, введённые пользователем, сохраняем в data элемента
        # Добавляем этот элемент в два списка
        list_widget.addItem(item)  # Добавляем в список на вкладке выбранной категории
        self.summaryListWidget.addItem(item.clone())  # Клонируем и добавляем клона в список на вкладке "Все"
        # Обновляем состояние
        self.is_modified = True  # Файл изменился
        self.update_window_title()  # Обновляем заголовок окна
        self.update_tag_list()  # Обновляем список на панели тегов
        self.statusBar().showMessage("Добавлено новое замечание.", 3000)

    def remove_remark(self):
        """Удаляет выбранное замечание из текущей вкладки и из всех соответствующих вкладок."""
        # Определяем текущую вкладку и список
        current_index = self.ui.tabWidget.currentIndex()
        tab_name = self.ui.tabWidget.tabText(current_index)
        list_widget = self.ui.tabWidget.widget(current_index)
        # Определяем, какие элементы выделены
        selected_items = list_widget.selectedItems()
        if not selected_items:
            return
        # Для каждого выбранного замечания
        for item in selected_items:
            text = item.text()  # Запоминаем текст замечания
            category = item.data(Qt.UserRole)  # Запоминаем категорию замечания
            # Удаляем клона замечания со вкладки "Все"
            for i in reversed(range(self.summaryListWidget.count())):
                clone = self.summaryListWidget.item(i)
                if clone.text() == text and clone.data(Qt.UserRole) == category:
                    self.summaryListWidget.takeItem(i)  # Удаляем клона на вкладке "Все"
                    break
            # Если мы на вкладке "Все", ищем и удаляем оригинал замечания
            if tab_name == "Все":
                for i in range(self.ui.tabWidget.count()):
                    # Ищем вкладку, на которой находится оригинал, по категории
                    if self.ui.tabWidget.tabText(i) == category:
                        list_widget = self.ui.tabWidget.widget(i)
                        for j in reversed(range(list_widget.count())):
                            # Ищем само замечание по тексту
                            if list_widget.item(j).text() == text:
                                list_widget.takeItem(j)  # Удаляем оригинал замечания
                                break
                        break
            # Иначе мы уже на нужной вкладке, просто удаляем оригинал
            else:
                list_widget.takeItem(list_widget.row(item))  # Удаляем оригинал замечания
        # Обновляем состояние
        self.is_modified = True  # Файл изменился
        self.update_window_title()  # Обновляем заголовок
        self.update_tag_list()  # Обновляем список на панели тегов
        self.statusBar().showMessage("Выбранные замечания удалены.", WAIT)

    def edit_remark(self):
        """Поочерёдно открывает диалоги для редактирования выбранных замечаний."""
        # Определяем текущую вкладку и список
        current_index = self.ui.tabWidget.currentIndex()
        tab_name = self.ui.tabWidget.tabText(current_index)
        list_widget = self.ui.tabWidget.widget(current_index)
        # Определяем, какие элементы выделены
        selected_items = list_widget.selectedItems()
        if not selected_items:
            return
        # Для каждого выбранного замечания
        for item in selected_items:
            old_text = item.text()  # Старый текст
            old_category = item.data(Qt.UserRole)  # Старая категория
            old_tags = item.data(Qt.UserRole + 1)  # Старые теги
            dialog = RemarkDialog(self, text=old_text, category=old_category, tags=old_tags)  # Окно редактирования
            if not dialog.exec():
                continue  # Если пользователь нажал "Отмена" или просто закрыл окно, то ничего не делаем
            new_text, new_category, new_tags = dialog.get_data()  # Получаем новые данные
            if not new_text:
                continue  # Не добавляем пустые замечания
            # Находим клона замечания на вкладке "Все" и обновляем его данные
            for i in range(self.summaryListWidget.count()):
                clone = self.summaryListWidget.item(i)
                if clone.text() == old_text and clone.data(Qt.UserRole) == old_category:
                    clone.setText(new_text)  # Обновляем текст
                    clone.setData(Qt.UserRole, new_category)  # Обновляем категорию
                    clone.setData(Qt.UserRole + 1, new_tags)  # Обновляем теги
                    break
            # Если мы на вкладке "Все", ищем и обновляем оригинал замечания
            if tab_name == "Все":
                for i in range(self.ui.tabWidget.count()):
                    # Ищем вкладку, на которой находится оригинал, и удаляем его оттуда, либо просто меняем текст
                    if self.ui.tabWidget.tabText(i) == old_category:
                        orig_list_widget = self.ui.tabWidget.widget(i)
                        for j in reversed(range(orig_list_widget.count())):
                            # Ищем само замечание по тексту
                            if orig_list_widget.item(j).text() == old_text:
                                if new_category == old_category:
                                    orig_list_widget.item(j).setText(new_text)  # Обновляем текст оригинала замечания
                                    orig_list_widget.item(j).setData(Qt.UserRole + 1, new_tags)  # Обновляем теги
                                else:
                                    orig_list_widget.takeItem(j)  # Удаляем оригинал замечания
                                break
                        break
                # Если категория изменилась, то добавляем в новую, иначе ничего
                if new_category != old_category:
                    for i in range(self.ui.tabWidget.count()):
                        # Ищем вкладку, куда нужно перенести оригинал, и добавляем его туда
                        if self.ui.tabWidget.tabText(i) == new_category:
                            new_item = QListWidgetItem(new_text)  # Создаём элемент списка, записываем текст
                            new_item.setData(Qt.UserRole, new_category)  # Записываем категорию
                            new_item.setData(Qt.UserRole + 1, new_tags)  # Записываем теги
                            self.ui.tabWidget.widget(i).addItem(new_item)  # Добавляем элемент в список
                            break
            # Иначе мы уже на нужной вкладке, просто обновляем оригинал
            else:
                # Если категория не изменилась, то просто меняем текст и теги
                if new_category == old_category:
                    item.setText(new_text)  # Обновляем текст
                    item.setData(Qt.UserRole + 1, new_tags)  # Обновляем теги
                # Иначе удаляем из старой категории и добавляем в новую
                else:
                    list_widget.takeItem(list_widget.row(item))
                    for i in range(self.ui.tabWidget.count()):
                        # Ищем вкладку, куда нужно перенести замечание
                        if self.ui.tabWidget.tabText(i) == new_category:
                            new_item = QListWidgetItem(new_text)  # Создаём элемент списка, записываем текст
                            new_item.setData(Qt.UserRole, new_category)  # Записываем категорию
                            new_item.setData(Qt.UserRole + 1, new_tags)  # Записываем теги
                            self.ui.tabWidget.widget(i).addItem(new_item)  # Добавляем элемент в список
                            break
            # Обновляем состояние
            self.is_modified = True  # Файл изменился
            self.update_window_title()  # Обновляем заголовок
            self.update_tag_list()  # Обновляем список на панели тегов
            self.statusBar().showMessage("Замечание обновлено.", WAIT)

    def copy_remark(self):
        """Копирует выбранные замечания в буфер обмена."""
        # Определяем текущую вкладку и список
        current_index = self.ui.tabWidget.currentIndex()
        list_widget = self.ui.tabWidget.widget(current_index)
        # Определяем, какие элементы выделены
        selected_items = list_widget.selectedItems()
        if selected_items:
            remarks_text = "\n".join(item.text() for item in selected_items)
            QGuiApplication.clipboard().setText(remarks_text)
            self.statusBar().showMessage("Выбранные замечания скопированы в буфер обмена.", WAIT)

    def add_tab(self):
        """Открывает диалог для добавления новой вкладки."""
        dialog = TabDialog(self, position=self.ui.tabWidget.count() - 1)  # По умолчанию добавляем в конец
        if not dialog.exec():
            return  # Если пользователь нажал "Отмена" или просто закрыл окно, то ничего не делаем
        name, position = dialog.get_data()
        if not name:
            return  # Не добавляем вкладки без имени
        # Проверка, существует ли уже вкладка с таким именем
        for i in range(self.ui.tabWidget.count()):
            if self.ui.tabWidget.tabText(i).lower() == name.lower():
                QMessageBox.warning(self, "Ошибка", f"Вкладка\"{name}\" уже существует.")
                return
        # Если не существует, создаём и открываем новую вкладку
        list_widget = QListWidget()  # Создаём виджет списка
        self.set_list_connects(list_widget)  # Подключаем для него реакции
        self.ui.tabWidget.insertTab(position, list_widget, name)  # Создаём новую вкладку с этим виджетом
        self.ui.tabWidget.setCurrentWidget(list_widget)  # Переключаемся на новую вкладку
        # Обновляем состояние
        self.is_modified = True
        self.update_window_title()
        self.statusBar().showMessage(f"Добавлена новая вкладка \"{name}\".", WAIT)

    def remove_tab(self):
        """Удаляет открытую вкладку со всеми замечаниями, а также клонов этих замечаний на вкладке "Все"."""
        # Определяем текущую вкладку
        current_index = self.ui.tabWidget.currentIndex()
        tab_name = self.ui.tabWidget.tabText(current_index)
        if tab_name in ["Все", "Без категории"]:
            return  # Эти вкладки нельзя удалить
        # Определяем, с каким списком работаем
        list_widget = self.ui.tabWidget.widget(current_index)
        for i in range(list_widget.count()):
            # Для каждого замечания из списка на текущей вкладке
            item = list_widget.item(i)
            text = item.text()  # Получаем текст замечания
            category = item.data(Qt.UserRole)  # И его категорию
            for j in reversed(range(self.summaryListWidget.count())):
                # Ищем клона этого замечания на вкладке "Все"
                clone = self.summaryListWidget.item(j)
                if clone.text() == text and clone.data(Qt.UserRole) == category:
                    self.summaryListWidget.takeItem(j)  # И удаляем его с вкладки "Все"
                    break
        self.ui.tabWidget.removeTab(current_index) # Удаляем текущую вкладку
        # Обновляем состояние
        self.is_modified = True  # Файл изменился
        self.update_window_title()  # Обновляем заголовок
        self.update_tag_list()  # Обновляем список на панели тегов
        self.statusBar().showMessage(f"Вкладка \"{tab_name}\" удалена.", WAIT)

    def edit_tab(self):
        """Открывает диалог для редактирования текущей вкладки."""
        # Определяем текущую вкладку
        current_index = self.ui.tabWidget.currentIndex()
        old_name = self.ui.tabWidget.tabText(current_index)
        if old_name in ["Все", "Без категории"]:
            return  # Эти вкладки нельзя редактировать
        dialog = TabDialog(self, name=old_name, position=current_index)
        if not dialog.exec():
            return  # Если пользователь нажал "Отмена" или просто закрыл окно, то ничего не делаем
        new_name, new_position = dialog.get_data()
        if not new_name or new_name == old_name and new_position == current_index:
            return  # Имя не менялось (или пустое) и позиция не менялась -> ничего не делаем
        existing_names = [self.ui.tabWidget.tabText(i).lower() for i in range(self.ui.tabWidget.count())]
        if new_name.lower() in existing_names and new_name.lower() != old_name.lower():
            # Вторая часть условия нужна, чтобы не было предупреждения когда пользователь хочет сменить только позицию
            QMessageBox.warning(self, "Ошибка", f"Вкладка \"{new_name}\" уже существует.")
            return
        # Обновляем название вкладки
        self.ui.tabWidget.setTabText(current_index, new_name)
        # Обновляем data у всех замечаний на этой вкладке и у всех их клонов на вкладке "Все"
        list_widget = self.ui.tabWidget.widget(current_index)
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            item.setData(Qt.UserRole, new_name)
            # Обновляем клонов этих замечаний со вкладки "Все"
            text = item.text()
            for j in range(self.summaryListWidget.count()):
                clone = self.summaryListWidget.item(j)
                if clone.text() == text and clone.data(Qt.UserRole) == old_name:
                    clone.setData(Qt.UserRole, new_name)
                    break
        # Если позиция изменилась, перемещаем вкладку и открываем её
        if new_position != current_index:
            widget = self.ui.tabWidget.widget(current_index)
            self.ui.tabWidget.removeTab(current_index)
            self.ui.tabWidget.insertTab(new_position, widget, new_name)
            self.ui.tabWidget.setCurrentIndex(new_position)
        # Обновляем состояние
        self.is_modified = True
        self.update_window_title()
        self.statusBar().showMessage(f"Вкладка \"{old_name}\" переименована в \"{new_name}\".", WAIT)

    def remove_user_tabs(self):
        """Удаляет все вкладки, созданные пользователем. Вкладки "Все" и "Без категории" просто очищает."""
        # Удаляем все вкладки, кроме вкладок "Все" и "Без категории"
        for i in reversed(range(1, self.ui.tabWidget.count() - 1)):
            self.ui.tabWidget.removeTab(i)
        # Очищаем списки на вкладках "Все" и "Без категории"
        self.summaryListWidget.clear()
        self.uncategorizedListWidget.clear()

    def clear_all_lists(self):
        """Очищает списки замечаний на всех вкладках категорий, не удаляя сами вкладки."""
        # Очищаем списки на всех вкладках, в том числе "Все" и "Без категории"
        for i in range(self.ui.tabWidget.count()):
            self.ui.tabWidget.widget(i).clear()

    def clear_list(self):
        """Очищает список замечаний на текущей вкладке. На вкладке "Все" очищает списки на всех вкладках."""
        # Определяем текущую вкладку
        current_index = self.ui.tabWidget.currentIndex()
        tab_name = self.ui.tabWidget.tabText(current_index)
        if tab_name == "Все":
            # Если мы на вкладке "Все", то очищаем вообще все списки
            self.clear_all_lists()
        else:
            # На других вкладках - очищаем список на текущей вкладке, и удаляем клонов этих замечаний со вкладки "Все"
            list_widget = self.ui.tabWidget.widget(current_index)
            for i in range(list_widget.count()):
                # Для каждого замечания на текущей вкладке
                text = list_widget.item(i).text()
                for j in reversed(range(self.summaryListWidget.count())):
                    # Ищем на вкладке "Все" клона этого замечания и удаляем
                    clone = self.summaryListWidget.item(j)
                    if clone.text() == text and clone.data(Qt.UserRole) == tab_name:
                        self.summaryListWidget.takeItem(j)
                        break
            list_widget.clear()  # Когда замечания со вкладки "Все" удалили, очищаем список на текущей вкладке
        # Обновляем состояние
        self.is_modified = True  # Файл изменился
        self.update_window_title()  # Обновляем заголовок
        self.statusBar().showMessage(f"Список замечаний на вкладке \"{tab_name}\" очищен.", WAIT)

    def set_list_connects(self, list_widget):
        """Подключает реакции на действия пользователя (клики, выделения) для указанного списка."""
        list_widget.itemDoubleClicked.connect(self.edit_remark)  # Редактирование двойным кликом
        list_widget.setSelectionMode(QListWidget.ExtendedSelection)  # Включаем множественное выделение
        list_widget.itemSelectionChanged.connect(self.toggle_remark_buttons)  # Вкл/выкл кнопки замечаний
        list_widget.setContextMenuPolicy(Qt.CustomContextMenu)  # Включаем контекстное меню (для реакции на ПКМ)
        list_widget.customContextMenuRequested.connect(
            lambda: self.copy_remark() if list_widget.selectedItems() else None
        )  # Устанавливаем копирование выделенных замечаний в качестве реакции на нажатие ПКМ

    def toggle_remark_buttons(self):
        """Выключает кнопки взаимодействия с замечаниями, если нет выбранных замечаний. И наоборот."""
        # Определяем текущую вкладку и список
        current_index = self.ui.tabWidget.currentIndex()
        list_widget = self.ui.tabWidget.widget(current_index)
        # Если ничего не выбрано, то отключаем кнопки удаления и редактирования замечаний, иначе - включаем
        has_selection = bool(list_widget.selectedItems())
        self.ui.remarkRemoveButton.setEnabled(has_selection)
        self.ui.remarkEditButton.setEnabled(has_selection)
        self.ui.remarkCopyButton.setEnabled(has_selection)

    def toggle_tab_buttons(self):
        """Выключает кнопки удаления и редактирования вкладки, если это "Все" или "Без категории". И наоборот."""
        # Определяем текущую вкладку
        current_index = self.ui.tabWidget.currentIndex()
        tab_name = self.ui.tabWidget.tabText(current_index)
        # Для вкладок "Все" и "Без категории" отключаем кнопки удаления и редактирования, для остальных включаем
        is_editable = bool(tab_name not in ["Все", "Без категории"])
        self.ui.tabRemoveButton.setEnabled(is_editable)
        self.ui.tabEditButton.setEnabled(is_editable)

    def toggle_tag_panel(self):
        """Переключает видимость панели тегов и обновляет состояние кнопки."""
        visible = not self.ui.tagPanelWidget.isVisible()  # Инвертируем текущее состояние
        self.ui.tagPanelWidget.setVisible(visible)  # Сворачиваем/разворачиваем панель тегов
        self.ui.tagPanelButton.setChecked(visible)  # Меняем состояние кнопки
        self.ui.tagPanelButton.setToolTip("Скрыть панель тегов" if visible else "Показать панель тегов")

    def toggle_tag_checkbox(self, item):
        """Переключает состояние чекбокса для элемента списка."""
        current_state = item.checkState()  # Считываем текущее состояние
        new_state = Qt.Unchecked if current_state == Qt.Checked else Qt.Checked  # Меняем на противоположное
        item.setCheckState(new_state)  # Устанавливаем новое состояние

    def set_tag_filter_mode(self, mode):
        """Переключает режим фильтрации по тегам ("AND"/"OR") и обновляет состояние кнопок."""
        self.tag_filter_mode = mode  # Режим фильтрации: "AND" или  "OR"
        self.ui.tagPanelAndButton.setChecked(mode == "AND")  # Меняем состояние кнопки "&&"
        self.ui.tagPanelOrButton.setChecked(mode == "OR")  # Меняем состояние кнопки "||"
        self.filter_remarks()  # Повторно применяем фильтр с новым режимом

    def tab_changed(self):
        self.toggle_tab_buttons()  # Вкл/выкл кнопки редактирования и удаления вкладки
        self.toggle_remark_buttons()  # Вкл/выкл кнопки взаимодействия с замечаниями
        self.ui.searchLineEdit.clear()  # Очищаем строку поискового запроса
        self.filter_remarks()  # Производим поиск с пустым поисковым запросом, чтобы отобразить скрытые элементы
        self.update_tag_list()  # Обновляем список тегов

    def filter_remarks(self):
        """Фильтрует замечания на текущей вкладке по поисковому запросу и по тегам."""
        # Определяем поисковый запрос и переводим его в нижний регистр
        query = self.ui.searchLineEdit.text().strip().lower()
        # Определяем список выбранных тегов
        selected_tags = [
            self.ui.tagListWidget.item(i).text()
            for i in range(self.ui.tagListWidget.count())
            if self.ui.tagListWidget.item(i).checkState() == Qt.Checked
        ]
        # Определяем список на текущей вкладке
        list_widget = self.ui.tabWidget.currentWidget()
        # Фильтруем список
        for i in range(list_widget.count()):
            item = list_widget.item(i)  # Очередной элемент списка
            item_text = item.text().lower()  # Текст замечания в нижнем регистре
            item_tags = item.data(Qt.UserRole + 1)  # Теги замечания
            # Проверяем, содержится ли в тексте замечания введённый пользователем поисковый запрос
            text_matches = query in item.text().lower() if query else True
            # Если режим "И", то проверяем содержатся ли в тегах замечания все теги, выбранные пользователем
            if self.tag_filter_mode == "AND":
                tag_matches = all(tag in item_tags for tag in selected_tags) if selected_tags else True
            # Если режим "ИЛИ", то проверяем содержится ли в тегах замечания хотя бы один тег, выбранный пользователем
            else:
                tag_matches = any(tag in item_tags for tag in selected_tags) if selected_tags else True
            # Скрываем элемент, если нет никаких совпадений
            item.setHidden(not (text_matches and tag_matches))

    def set_shortcuts(self):
        """Включает шорткаты для действий, не привязанных к кнопкам."""
        # Выделение всех замечаний на текущей вкладке при нажатии сочетания клавиш "Ctrl + A"
        QShortcut(QKeySequence("Ctrl+A"), self).activated.connect(
            lambda: self.ui.tabWidget.currentWidget().selectAll()
        )
        # Переключение фокуса на строку поиска при нажатии сочетания клавиш "Ctrl + F"
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(
            lambda: self.ui.searchLineEdit.setFocus()
        )
        # Обработка нажатия на "Esc" (разные действия в зависимости от текущего фокуса)
        QShortcut(QKeySequence("Esc"), self).activated.connect(
            self.esc_shortcut
        )

    def esc_shortcut(self):
        """Обрабатывает нажатие на "Esc" по-разному в зависимости от фокуса."""
        if self.ui.searchLineEdit.hasFocus():  # Если фокус на строке поиска
            self.ui.searchLineEdit.clear()  # Очищаем строку поиска
            self.ui.tabWidget.currentWidget().setFocus()  # Возвращаем фокус на список замечаний
        elif self.ui.tagListWidget.hasFocus():  # Если фокус на списке тегов
            self.ui.tagListWidget.clearSelection()  # Сбрасываем выделение в списке тегов
            for i in range(self.ui.tagListWidget.count()):  # Сбрасываем все чекбоксы в списке тегов
                item = self.ui.tagListWidget.item(i)
                item.setCheckState(Qt.Unchecked)
            self.ui.tabWidget.currentWidget().setFocus()  # Возвращаем фокус на список замечаний
        else:  # Во всех прочих случаях
            self.ui.tabWidget.currentWidget().clearSelection()  # Сбрасываем выделение в списке замечаний

    def update_window_title(self):
        """Обновляет заголовок окна, отображает название текущего файла и звёздочку."""
        base_title = "Помощник нормоконтролёра"
        file_name = os.path.basename(self.current_file) if self.current_file else "Новый документ"
        modify_marker = "*" if self.is_modified else ""
        self.setWindowTitle(f"{file_name}{modify_marker} – {base_title}")

    def get_tab_tags(self, tab_index):
        """Возвращает отсортированный список уникальных тегов для замечаний с текущей вкладки."""
        list_widget = self.ui.tabWidget.widget(tab_index)  # Виджет списка со вкладки с индексом tab_index
        tags = set()  # Используем set(), чтобы отбрасывать повторы
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            item_tags = item.data(Qt.UserRole + 1)
            if item_tags:
                tags.update(item_tags)
        return sorted(tags)

    def update_tag_list(self):
        """Обновляет список тегов на панели тегов (tagListWidget)."""
        tags = self.get_tab_tags(self.ui.tabWidget.currentIndex())  # Получаем отсортированный список уникальных тегов
        self.ui.tagListWidget.clear()   # Очищаем список перед обновлением
        for tag in tags:
            list_item = QListWidgetItem(tag)  # Создаём очередной элемент списка
            list_item.setFlags(list_item.flags() | Qt.ItemIsUserCheckable)  # Добавляем элементу списка чекбокс
            list_item.setCheckState(Qt.Unchecked)  # По умолчанию чекбокс не установлен
            self.ui.tagListWidget.addItem(list_item)

    def closeEvent(self, event):
        """Запрос подтверждения перед закрытием, если есть несохранённые изменения."""
        if self.is_modified:  # Проверяем, были ли изменения
            reply = QMessageBox.question(
                self,
                "Несохранённые изменения",
                "У вас есть несохранённые изменения. Сохранить их перед выходом?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Yes
            )  # Окно с вариантами выбора: "да", "нет", "отмена"
            if reply == QMessageBox.Yes:
                self.save_file()  # Сохраняем изменения
            elif reply == QMessageBox.Cancel:
                event.ignore()  # Отменяем закрытие окна
                return
        # Сохраняем необходимые данные в настройках
        self.settings.setValue("last_file", self.current_file)  # Сохраняем в настройках текущий файл как последний
        self.settings.setValue("tag_panel_visible", self.ui.tagPanelWidget.isVisible())  # Видимость панели тегов
        self.settings.setValue("tag_filter_mode", self.tag_filter_mode)  # Режим фильтрации по тегам: "AND" или "OR"
        # Закрываем окно
        event.accept()


class LockedTabBar(QTabBar):
    """
    Кастомный QTabBar, который гарантирует, что вкладки с именами "Все" и "Без категории" всегда остаются
    на первой и последней позициях соответственно после завершения перетаскивания вкладок.

    Переопределяет обработку отпускания кнопки мыши, чтобы автоматически
    вернуть эти вкладки на закреплённые позиции.

    Методы:
        mouseReleaseEvent(event):
            Обрабатывает отпускание кнопки мыши и перемещает закреплённые вкладки.
    """
    def mouseReleaseEvent(self, event):
        """
        Обработка события отпускания кнопки мыши.

        После выполнения базовой обработки перемещает вкладку с именем
        "Все" на первую позицию, а вкладку с именем "Без категории" — на последнюю.

        Аргументы:
            event (QMouseEvent): Событие отпускания кнопки мыши.
        """
        super().mouseReleaseEvent(event)
        count = self.count()
        # Возвращаем вкладку "Все" на первую позицию
        for i in range(count):
            if self.tabText(i) == "Все":
                self.moveTab(i, 0)
        # Возвращаем вкладку "Без категории" на последнюю позицию
        for i in range(count):
            if self.tabText(i) == "Без категории":
                self.moveTab(i, count - 1)