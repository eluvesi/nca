from PyQt5.QtWidgets import QDialog

from ui_tab_dialog import Ui_TabDialog


class TabDialog(QDialog):
    """Окно редактирования вкладки."""
    def __init__(self, parent=None, name="", position=0):
        """Конструктор класса TabDialog."""
        super().__init__(parent)  # Вызываем конструктор родительского класса
        self.ui = Ui_TabDialog()  # Подгружаем интерфейс
        self.ui.setupUi(self)  # Применяем его к текущему окну
        # Вычисляем минимальную и максимальную возможные позиции
        tab_count = parent.ui.tabWidget.count()
        self.ui.positionSpinBox.setMinimum(1)  # [0] это всегда вкладка "Все"
        # Определяем, добавляем ли мы новую вкладку или редактируем имеющуюся
        if name:  # Если name не пусто, значит редактируем, тогда максимальный индекс [tab_count - 2]
            self.ui.positionSpinBox.setMaximum(tab_count - 2)  # ведь [tab_count - 1] это вкладка "Без категории"
        else:  # Иначе добавляем новую, тогда, так как после добавления tab_count увеличится на 1
            self.ui.positionSpinBox.setMaximum(tab_count - 1)  # то максимальный индекс [tab_count - 2 + 1]
        # В строку для редактирования загружаем текущий текст замечания
        self.ui.nameEditLine.setText(name)
        # В качестве выбранной позиции устанавливаем текущую
        self.ui.positionSpinBox.setValue(position)
        # Подключаем кнопки
        self.ui.saveButton.clicked.connect(self.accept)
        self.ui.cancelButton.clicked.connect(self.reject)

    def get_data(self):
        """Возвращает имя вкладки и выбранную позицию."""
        name = self.ui.nameEditLine.text().strip()
        position = self.ui.positionSpinBox.value()
        return name, position
