from PyQt5 import QtCore, QtGui, QtWidgets

from utils import resource_path


class Ui_RemarkDialog(object):
    def setupUi(self, RemarkDialog):
        RemarkDialog.setObjectName("RemarkDialog")
        RemarkDialog.resize(600, 200)
        RemarkDialog.setMinimumSize(QtCore.QSize(600, 200))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resource_path("icons/edit.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        RemarkDialog.setWindowIcon(icon)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(RemarkDialog)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.textEdit = QtWidgets.QPlainTextEdit(RemarkDialog)
        self.textEdit.setMinimumSize(QtCore.QSize(370, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.textEdit.setFont(font)
        self.textEdit.setObjectName("textEdit")
        self.horizontalLayout_2.addWidget(self.textEdit)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.categoryComboBox = QtWidgets.QComboBox(RemarkDialog)
        self.categoryComboBox.setMinimumSize(QtCore.QSize(200, 32))
        self.categoryComboBox.setObjectName("categoryComboBox")
        self.verticalLayout.addWidget(self.categoryComboBox)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
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
        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(RemarkDialog)
        QtCore.QMetaObject.connectSlotsByName(RemarkDialog)

    def retranslateUi(self, RemarkDialog):
        _translate = QtCore.QCoreApplication.translate
        RemarkDialog.setWindowTitle(_translate("RemarkDialog", "Редактирование замечания"))
        self.textEdit.setPlaceholderText(_translate("RemarkDialog", "Текст замечания"))
        self.cancelButton.setText(_translate("RemarkDialog", "Отмена"))
        self.saveButton.setText(_translate("RemarkDialog", "Сохранить"))
