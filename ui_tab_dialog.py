from PyQt5 import QtCore, QtGui, QtWidgets

from utils import resource_path


class Ui_TabDialog(object):
    def setupUi(self, TabDialog):
        TabDialog.setObjectName("TabDialog")
        TabDialog.resize(450, 90)
        TabDialog.setMinimumSize(QtCore.QSize(450, 90))
        TabDialog.setMaximumSize(QtCore.QSize(450, 90))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resource_path("icons/edit.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        TabDialog.setWindowIcon(icon)
        self.nameEditLine = QtWidgets.QLineEdit(TabDialog)
        self.nameEditLine.setGeometry(QtCore.QRect(10, 10, 431, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.nameEditLine.setFont(font)
        self.nameEditLine.setText("")
        self.nameEditLine.setObjectName("nameEditLine")
        self.horizontalLayoutWidget = QtWidgets.QWidget(TabDialog)
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
        self.positionSpinBox = QtWidgets.QSpinBox(TabDialog)
        self.positionSpinBox.setGeometry(QtCore.QRect(160, 50, 61, 31))
        self.positionSpinBox.setObjectName("positionSpinBox")
        self.label = QtWidgets.QLabel(TabDialog)
        self.label.setGeometry(QtCore.QRect(10, 50, 151, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")

        self.retranslateUi(TabDialog)
        QtCore.QMetaObject.connectSlotsByName(TabDialog)

    def retranslateUi(self, TabDialog):
        _translate = QtCore.QCoreApplication.translate
        TabDialog.setWindowTitle(_translate("TabDialog", "Редактирование вкладки"))
        self.nameEditLine.setPlaceholderText(_translate("TabDialog", "Имя вкладки"))
        self.cancelButton.setText(_translate("TabDialog", "Отмена"))
        self.saveButton.setText(_translate("TabDialog", "Сохранить"))
        self.label.setText(_translate("TabDialog", "Позиция вкладки:"))
