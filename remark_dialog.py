from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QDialog

from ui_remark_dialog import Ui_RemarkDialog


class RemarkDialog(QDialog):
    """Окно редактирования замечания."""
    def __init__(self, parent=None, text="", category = ""):
        """Конструктор класса RemarkDialog."""
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
        # В поле textEdit загружаем текущий текст замечания
        self.ui.textEdit.setPlainText(text)
        # В качестве выбранной категории устанавливаем текущую
        self.ui.categoryComboBox.setCurrentText(category)
        # Подключаем кнопки
        self.ui.saveButton.clicked.connect(self.accept)
        self.ui.cancelButton.clicked.connect(self.reject)
        # Устанавливаем фильтр событий для поля textEdit
        self.ui.textEdit.installEventFilter(self)

    def get_data(self):
        """Возвращает текст замечания и выбранную категорию."""
        text = self.ui.textEdit.toPlainText().strip()
        category = self.ui.categoryComboBox.currentText().strip()
        return text, category

    def eventFilter(self, source, event):
        """Фильтр событий для textEdit."""
        if source == self.ui.textEdit and event.type() == QEvent.KeyPress:
            # Если пользователь нажал Enter, вместо перехода на новую строку сохраняем замечание
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.accept()  # Имитируем нажатие кнопки "Сохранить"
                return True  # Перехватили событие, не передаем дальше
        return super().eventFilter(source, event)  # Иначе вызываем метод родительского класса
