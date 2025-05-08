from PyQt5 import QtCore, QtGui, QtWidgets

from utils import resource_path


class Ui_RemarkDialog(object):
    def setupUi(self, RemarkDialog):
        RemarkDialog.setObjectName("RemarkDialog")
        RemarkDialog.resize(450, 90)
        RemarkDialog.setMinimumSize(QtCore.QSize(450, 90))
        RemarkDialog.setMaximumSize(QtCore.QSize(450, 90))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resource_path("icons/edit.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        RemarkDialog.setWindowIcon(icon)
        self.textEditLine = QtWidgets.QLineEdit(RemarkDialog)
        self.textEditLine.setGeometry(QtCore.QRect(10, 10, 431, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.textEditLine.setFont(font)
        self.textEditLine.setText("")
        self.textEditLine.setObjectName("textEditLine")
        self.categoryComboBox = QtWidgets.QComboBox(RemarkDialog)
        self.categoryComboBox.setGeometry(QtCore.QRect(10, 50, 211, 31))
        self.categoryComboBox.setObjectName("categoryComboBox")
        self.horizontalLayoutWidget = QtWidgets.QWidget(RemarkDialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(230, 50, 211, 31))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.buttonsLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.buttonsLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonsLayout.setObjectName("buttonsLayout")
        self.cancelButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.cancelButton.setObjectName("cancelButton")
        self.buttonsLayout.addWidget(self.cancelButton)
        self.saveButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.saveButton.setDefault(True)
        self.saveButton.setObjectName("saveButton")
        self.buttonsLayout.addWidget(self.saveButton)

        self.retranslateUi(RemarkDialog)
        QtCore.QMetaObject.connectSlotsByName(RemarkDialog)

    def retranslateUi(self, RemarkDialog):
        _translate = QtCore.QCoreApplication.translate
        RemarkDialog.setWindowTitle(_translate("RemarkDialog", "Редактирование замечания"))
        self.textEditLine.setPlaceholderText(_translate("RemarkDialog", "Текст замечания"))
        self.categoryComboBox.setPlaceholderText(_translate("RemarkDialog", "Категория"))
        self.cancelButton.setText(_translate("RemarkDialog", "Отмена"))
        self.saveButton.setText(_translate("RemarkDialog", "Сохранить"))
