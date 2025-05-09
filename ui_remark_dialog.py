from PyQt5 import QtCore, QtGui, QtWidgets

from utils import resource_path


class Ui_RemarkDialog(object):
    def setupUi(self, RemarkDialog):
        RemarkDialog.setObjectName("RemarkDialog")
        RemarkDialog.resize(475, 95)
        RemarkDialog.setMinimumSize(QtCore.QSize(475, 95))
        RemarkDialog.setMaximumSize(QtCore.QSize(475, 95))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resource_path("icons/edit.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        RemarkDialog.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(RemarkDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.textEditLine = QtWidgets.QLineEdit(RemarkDialog)
        self.textEditLine.setMinimumSize(QtCore.QSize(0, 32))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.textEditLine.setFont(font)
        self.textEditLine.setObjectName("textEditLine")
        self.verticalLayout.addWidget(self.textEditLine)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.categoryComboBox = QtWidgets.QComboBox(RemarkDialog)
        self.categoryComboBox.setMinimumSize(QtCore.QSize(200, 32))
        self.categoryComboBox.setObjectName("categoryComboBox")
        self.horizontalLayout.addWidget(self.categoryComboBox)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.cancelButton = QtWidgets.QPushButton(RemarkDialog)
        self.cancelButton.setMinimumSize(QtCore.QSize(0, 32))
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.saveButton = QtWidgets.QPushButton(RemarkDialog)
        self.saveButton.setMinimumSize(QtCore.QSize(0, 32))
        self.saveButton.setDefault(True)
        self.saveButton.setObjectName("saveButton")
        self.horizontalLayout.addWidget(self.saveButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(RemarkDialog)
        QtCore.QMetaObject.connectSlotsByName(RemarkDialog)

    def retranslateUi(self, RemarkDialog):
        _translate = QtCore.QCoreApplication.translate
        RemarkDialog.setWindowTitle(_translate("RemarkDialog", "Редактирование замечания"))
        self.textEditLine.setPlaceholderText(_translate("RemarkDialog", "Текст замечания"))
        self.categoryComboBox.setPlaceholderText(_translate("RemarkDialog", "Категория"))
        self.cancelButton.setText(_translate("RemarkDialog", "Отмена"))
        self.saveButton.setText(_translate("RemarkDialog", "Сохранить"))
