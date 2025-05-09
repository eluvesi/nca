from PyQt5 import QtCore, QtGui, QtWidgets

from utils import resource_path


class Ui_TabDialog(object):
    def setupUi(self, TabDialog):
        TabDialog.setObjectName("TabDialog")
        TabDialog.resize(475, 95)
        TabDialog.setMinimumSize(QtCore.QSize(475, 95))
        TabDialog.setMaximumSize(QtCore.QSize(475, 95))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resource_path("icons/tab-edit.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        TabDialog.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(TabDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.nameEditLine = QtWidgets.QLineEdit(TabDialog)
        self.nameEditLine.setMinimumSize(QtCore.QSize(0, 32))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.nameEditLine.setFont(font)
        self.nameEditLine.setObjectName("nameEditLine")
        self.verticalLayout.addWidget(self.nameEditLine)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(TabDialog)
        self.label.setMinimumSize(QtCore.QSize(0, 32))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.positionSpinBox = QtWidgets.QSpinBox(TabDialog)
        self.positionSpinBox.setMinimumSize(QtCore.QSize(48, 32))
        self.positionSpinBox.setObjectName("positionSpinBox")
        self.horizontalLayout.addWidget(self.positionSpinBox)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.cancelButton = QtWidgets.QPushButton(TabDialog)
        self.cancelButton.setMinimumSize(QtCore.QSize(0, 32))
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.saveButton = QtWidgets.QPushButton(TabDialog)
        self.saveButton.setMinimumSize(QtCore.QSize(0, 32))
        self.saveButton.setDefault(True)
        self.saveButton.setObjectName("saveButton")
        self.horizontalLayout.addWidget(self.saveButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(TabDialog)
        QtCore.QMetaObject.connectSlotsByName(TabDialog)

    def retranslateUi(self, TabDialog):
        _translate = QtCore.QCoreApplication.translate
        TabDialog.setWindowTitle(_translate("TabDialog", "Редактирование вкладки"))
        self.nameEditLine.setPlaceholderText(_translate("TabDialog", "Имя вкладки"))
        self.label.setText(_translate("TabDialog", "Позиция вкладки:"))
        self.cancelButton.setText(_translate("TabDialog", "Отмена"))
        self.saveButton.setText(_translate("TabDialog", "Сохранить"))
