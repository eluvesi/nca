from PyQt5.QtWidgets import QDialog
from ui_remark_dialog import Ui_RemarkDialog

class RemarkDialog(QDialog):
    """Окно редактирования замечания."""
    def __init__(self, parent=None, remark_text=""):
        super().__init__(parent)
        self.ui = Ui_RemarkDialog()
        self.ui.setupUi(self)

        self.ui.remarkEditLine.setText(remark_text)

        # Загружаем категории из вкладок (кроме "Все")
        if parent:
            categories = [
                parent.ui.tabWidget.tabText(i)
                for i in range(parent.ui.tabWidget.count())
                if parent.ui.tabWidget.tabText(i) != "Все"
            ]
            self.ui.categoryComboBox.addItems(categories)

        self.ui.saveButton.clicked.connect(self.accept)
        self.ui.cancelButton.clicked.connect(self.reject)

    def get_data(self):
        """Возвращает текст замечания и выбранную категорию."""
        text = self.ui.remarkEditLine.text()
        category = self.ui.categoryComboBox.currentText().strip()
        return text, category
