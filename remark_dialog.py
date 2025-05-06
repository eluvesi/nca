from PyQt5.QtWidgets import QDialog
from ui_remark_dialog import Ui_RemarkDialog

class RemarkDialog(QDialog):
    """Окно редактирования замечания."""
    def __init__(self, parent=None, text="", category = ""):
        super().__init__(parent)
        self.ui = Ui_RemarkDialog()
        self.ui.setupUi(self)
        # Загружаем в выпадающий список категории из вкладок (кроме "Все")
        if parent:
            categories = [
                parent.ui.tabWidget.tabText(i)
                for i in range(parent.ui.tabWidget.count())
                if parent.ui.tabWidget.tabText(i) != "Все"
            ]
            self.ui.categoryComboBox.addItems(categories)
        # В строку для редактирования загружаем текущий текст замечания
        self.ui.remarkEditLine.setText(text)
        # В качестве выбранной категории устанавливаем текущую
        self.ui.categoryComboBox.setCurrentText(category)
        # Подключаем кнопки
        self.ui.saveButton.clicked.connect(self.accept)
        self.ui.cancelButton.clicked.connect(self.reject)

    def get_data(self):
        """Возвращает текст замечания и выбранную категорию."""
        text = self.ui.remarkEditLine.text().strip()
        category = self.ui.categoryComboBox.currentText().strip()
        return text, category
