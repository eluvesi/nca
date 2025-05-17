from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QDialog, QCompleter

from ui_remark_dialog import Ui_RemarkDialog


class RemarkDialog(QDialog):
    """
    Окно редактирования или создания замечания.

    Позволяет задать текст замечания, выбрать категорию и добить теги.
    Использует автодополнение тегов и предоставляет методы для получения введённых данных.

    Методы:
        __init__(parent=None, text="", category="", tags=None):
            Конструктор окна.
        get_data():
            Возвращает данные из полей ввода.
        eventFilter(source, event):
            Обрабатывает события клавиатуры для поля textEdit.
    """
    def __init__(self, parent=None, text="", category="", tags=None):
        """
        Конструктор окна RemarkDialog.

        Аргументы:
            parent (QWidget, optional): Родительский виджет (главное окно). По умолчанию None.
            text (str, optional): Текст замечания для редактирования. По умолчанию пустая строка.
            category (str, optional): Название выбранной категории. По умолчанию пустая строка.
            tags (list[str], optional): Список тегов для редактирования. По умолчанию None.
        """
        super().__init__(parent)  # Вызываем конструктор родительского класса
        self.ui = Ui_RemarkDialog()  # Подгружаем интерфейс
        self.ui.setupUi(self)  # Применяем его к текущему окну
        # Загружаем в выпадающий список категории из вкладок (кроме "Все")
        if parent:
            categories = [
                parent.ui.tabWidget.tabText(i)
                for i in range(parent.ui.tabWidget.count())
                if parent.ui.tabWidget.tabText(i) != "Все"
            ]
            self.ui.categoryComboBox.addItems(categories)
            # Собираем все теги из родителя для автодополнения
            all_tags = parent.get_tab_tags(0)  # tab_index = 0 -> собираем теги со вкладки "Все"
            # Создаём completer для подсказок при вводе
            completer = TagCompleter(all_tags, self.ui.tagsLineEdit)
            self.ui.tagsLineEdit.setCompleter(completer)
        # В поле textEdit загружаем текущий текст замечания
        self.ui.textEdit.setPlainText(text)
        # В качестве выбранной категории устанавливаем текущую
        self.ui.categoryComboBox.setCurrentText(category)
        # В поле tagsLineEdit загружаем теги через запятую
        self.ui.tagsLineEdit.setText(", ".join(tags) + (", " if tags else ""))
        # Подключаем кнопки
        self.ui.saveButton.clicked.connect(self.accept)
        self.ui.cancelButton.clicked.connect(self.reject)
        # Реакция на изменение тегов (ввод запятой)
        self.ui.tagsLineEdit.textChanged.connect(self.tags_changed)
        # Фильтр событий для поля textEdit (реакция на Enter)
        self.ui.textEdit.installEventFilter(self)

    def tags_changed(self):
        """
        Обрабатывает каждое изменение текста в поле ввода тегов.

        Автоматически приводит весь текст к нижнему регистру после каждого изменения. При вводе запятой проверяет
        список тегов на дубликаты и удаляет их, после чего перемещает курсор на ожидаемую позицию.
        """
        text = self.ui.tagsLineEdit.text()  # Считываем строку с тегами из tagsLineEdit
        # Исправляем регистр - всё переводим в нижний
        cursor_pos = self.ui.tagsLineEdit.cursorPosition()  # Получаем текущую позицию курсора в тесте
        self.ui.tagsLineEdit.setText(text.lower())  # Приводим к нижнему регистру
        self.ui.tagsLineEdit.setCursorPosition(cursor_pos)  # Возвращаем курсор на прежнее место
        # Избавляемся от повторов - удаляем дубликаты
        if cursor_pos == 0:
            return
        last_char = text[cursor_pos - 1]  # Узнаём последний введённый символ
        # Если последний символ - не запятая, то пользователь продолжает ввод тега
        if last_char != ",":
            return
        # Иначе только что целиком введён новый тег, проверяем всю строку тегов на регистр и дубликаты
        tags = [tag.strip() for tag in text.split(",") if tag.strip()]  # Разделяем на теги по запятым
        unique_tags = list(dict.fromkeys(tags))  # Убираем дубликаты
        if unique_tags == tags:
            return
        # Формируем исправленную строку
        new_text = ", ".join(unique_tags) + ", "  # Формируем новую строку
        self.ui.tagsLineEdit.setText(new_text)  # Меняем текст
        left_comma_pos = new_text.rfind(",", 0, cursor_pos)  # Вычисляем позицию последней запятой слева от курсора
        self.ui.tagsLineEdit.setCursorPosition(left_comma_pos + 2)  # Курсор на два символа (", ") вправо от неё

    def get_data(self):
        """
        Возвращает данные, введённые пользователем.

        Считывает текст замечания, выбранную категорию и список тегов из полей ввода.

        Возвращает:
            tuple[str, str, list[str]]: Текст замечания, категория и список тегов.
        """
        text = self.ui.textEdit.toPlainText().strip()  # Текст замечания считываем из поля textEdit
        category = self.ui.categoryComboBox.currentText().strip()  # Категорию считываем из categoryComboBox
        tags = [tag.strip().lower() for tag in self.ui.tagsLineEdit.text().split(",") if tag.strip()]  # Собираем теги
        tags = list(dict.fromkeys(tags))  # Убираем дубликаты тегов (они могут остаться несмотря на защиту при вводе)
        return text, category, tags

    def eventFilter(self, source, event):
        """
        Обрабатывает события для поля textEdit.

        Если нажата клавиша Enter в textEdit, сохраняет данные и закрывает окно, вместо вставки новой строки.

        Аргументы:
            source (QObject): Виджет-источник события.
            event (QEvent): Событие, которое произошло.

        Возвращает:
            bool: True, если событие было перехвачено и обработано. Если нет, то делегируем родительскому классу.
        """
        if source == self.ui.textEdit and event.type() == QEvent.KeyPress:
            # Если пользователь нажал Enter, вместо перехода на новую строку сохраняем замечание
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.accept()  # Имитируем нажатие кнопки "Сохранить"
                return True  # Перехватили событие, не передаем дальше
        return super().eventFilter(source, event)  # Иначе вызываем метод родительского класса

class TagCompleter(QCompleter):
    """
    Кастомный QCompleter для автодополнения тегов через запятую.

    Предлагает подсказки только для последнего, неполного тега.
    При автозаполнении ранее введённые теги остаются нетронутыми.

    Методы:
        __init__(tags, parent=None):
            Конструктор класса.
        pathFromIndex(index):
            Формирует итоговую строку после выбора подсказки.
        splitPath(path):
            Определяет часть строки для поиска подсказок.
    """
    def __init__(self, tags, parent=None):
        """
        Конструктор класса TagCompleter.

        Аргументы:
            tags (list[str]): Список возможных тегов для автодополнения.
            parent (QWidget, optional): Родительский виджет (например, QLineEdit). По умолчанию None.
        """
        super().__init__(tags, parent)  # Вызываем конструктор родительского класса QCompleter
        self.setCaseSensitivity(Qt.CaseInsensitive)  # Игнорируем регистр при поиске совпадений

    def pathFromIndex(self, index):
        """
        Формирует итоговую строку после выбора подсказки.

        Метод вызывается автоматически, когда пользователь выбирает элемент из списка автодополнения. Заменяет
        редактируемую часть строки на выбранный тег, даже если пользователь вставляет его в середину списка тегов.

        Аргументы:
            index (QModelIndex): Индекс выбранного элемента из списка подсказок.

        Возвращает:
            str: Итоговая строка с учётом выбранной подсказки.
        """
        editor = self.widget()  # Узнаём виджет, с текстом из которого работаем
        current_text = editor.text()  # Получаем текущий текст в поле
        cursor_pos = editor.cursorPosition()  # Узнаём текущую позицию курсора
        left_comma_pos = current_text.rfind(",", 0, cursor_pos)  # Узнаём позицию последней запятой слева от курсора
        start = left_comma_pos + 1 if left_comma_pos != -1 else 0  # Запятой слева может не быть, если это первый тег
        new_text = (
                current_text[:start].rstrip() + " " + # Левый кусок до тега (без лишних пробелов справа)
                index.data() + # Подсказка, выбранная пользователем
                ", " + current_text[cursor_pos:].lstrip()  # Запятая и хвост после редактируемого тега (без пробелов)
        )
        tags = [tag.strip() for tag in new_text.split(",") if tag.strip()]  # Разбиваем строку на теги по запятым
        unique_tags = list(dict.fromkeys(tags))  # Убираем дубликаты
        result_text = ", ".join(unique_tags) + ", "  # Собираем обратно в строку с запятыми и пробелами
        return result_text

    def splitPath(self, path):
        """
        Определяет часть строки для поиска совпадений, исходя из позиции курсора.

        Метод вызывается автоматически при каждом вводе текста. Возвращает фрагмент тега, который пользователь
        редактирует в данный момент, даже если он добавляет новый тег в середину строки.

        Аргументы:
            path (str): Текущий ввод пользователя.

        Возвращает:
            list[str]: Список из одного элемента — последнего слова для поиска совпадений.
        """
        editor = self.widget()  # Узнаём виджет, с текстом из которого работаем
        cursor_pos = editor.cursorPosition()  # Узнаём текущую позицию курсора
        left_comma_pos = path[:cursor_pos].rfind(',')  # Узнаём позицию последней запятой слева от курсора
        start = left_comma_pos + 1 if left_comma_pos != -1 else 0  # Запятой слева может не быть, если это первый тег
        current_tag = path[start:cursor_pos].strip()  # Будем искать подсказки только по этому фрагменту
        return [current_tag]