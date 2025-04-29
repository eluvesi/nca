from PyQt5.QtWidgets import QDialog
from ui_remark_dialog import Ui_RemarkDialog


class RemarkDialog(QDialog):
    """Окно редактирования замечания."""
    def __init__(self, parent=None, remark_text=""):
        super().__init__(parent)
        self.ui = Ui_RemarkDialog()
        self.ui.setupUi(self)

        self.ui.remarkEditLine.setText(remark_text)
        #self.ui.categoryComboBox.setCurrentText(category)

        self.ui.saveButton.clicked.connect(self.accept)
        self.ui.cancelButton.clicked.connect(self.reject)

    def get_data(self):
        """Возвращает введённые данные: текст замечания, категорию, теги"""
        text = self.ui.remarkEditLine.text()
        #category = self.ui.categoryComboBox.currentText()
        return text