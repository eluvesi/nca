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
            all_tags = parent.get_all_tags()
            # Создаём completer для подсказок при вводе
            completer = TagCompleter(all_tags, self.ui.tagsLineEdit)
            self.ui.tagsLineEdit.setCompleter(completer)
        # В поле textEdit загружаем текущий текст замечания
        self.ui.textEdit.setPlainText(text)
        # В качестве выбранной категории устанавливаем текущую
        self.ui.categoryComboBox.setCurrentText(category)
        # В поле tagsLineEdit загружаем теги через запятую
        self.ui.tagsLineEdit.setText(", ".join(tags))
        # Подключаем кнопки
        self.ui.saveButton.clicked.connect(self.accept)
        self.ui.cancelButton.clicked.connect(self.reject)
        # Устанавливаем фильтр событий для поля textEdit
        self.ui.textEdit.installEventFilter(self)

    def get_data(self):
        """
        Возвращает данные, введённые пользователем.

        Считывает текст замечания, выбранную категорию и список тегов из полей ввода.

        Возвращает:
            tuple[str, str, list[str]]: Текст замечания, категория и список тегов.
        """
        text = self.ui.textEdit.toPlainText().strip()  # Текст замечания считываем из поля textEdit
        category = self.ui.categoryComboBox.currentText().strip()  # Категорию считываем из categoryComboBox
        tags = [tag.strip() for tag in self.ui.tagsLineEdit.text().split(",") if tag.strip()]  # Теги - из tagsLineEdit
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

        Метод вызывается автоматически, когда пользователь выбирает элемент из списка автодополнения.
        Он подставляет выбранный тег вместо последнего фрагмента после запятой, сохраняя введённые ранее теги.

        Аргументы:
            index (QModelIndex): Индекс выбранного элемента из списка подсказок.

        Возвращает:
            str: Итоговая строка с учётом выбранной подсказки.
        """
        editor = self.widget()  # Узнаём виджет, с текстом из которого работаем
        current_text = editor.text()  # Получаем текущий текст в поле
        parts = current_text.rsplit(',', 1)  # Разделяем по последней запятой
        prefix = parts[0] + ', ' if len(parts) > 1 else ''  # Часть до запятой записываем в переменную prefix
        return prefix + index.data()  # Возвращаем строку, где заменён только последний незавершённый тег

    def splitPath(self, path):
        """
        Определяет часть строки, по которой искать совпадения.

        Метод вызывается автоматически при каждом вводе текста. Возвращает только последний фрагмент
        после запятой, чтобы QCompleter искал подсказки по нему, а не по всей строке.

        Аргументы:
            path (str): Текущий ввод пользователя.

        Возвращает:
            list[str]: Список из одного элемента — последнего слова для поиска совпадений.
        """
        parts = path.rsplit(',', 1)  # Разделяем по последней запятой
        last_tag = parts[-1].strip()  # Фрагмент после запятой
        return [last_tag]  # Будем искать подсказки только по этому фрагменту