from PyQt5 import QtCore, QtGui, QtWidgets

from utils import resource_path


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setMinimumSize(QtCore.QSize(800, 600))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resource_path("icons/logo.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setStyleSheet("QListWidget::item:hover {\n"
"    background-color: #e5f3ff;\n"
"}\n"
"QListWidget::item:selected {\n"
"    background-color: #cce8ff;\n"
"    color: black;\n"
"}")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.fileCreateButton = QtWidgets.QPushButton(self.centralwidget)
        self.fileCreateButton.setMaximumSize(QtCore.QSize(32, 32))
        self.fileCreateButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.fileCreateButton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(resource_path("icons/document-new.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.fileCreateButton.setIcon(icon1)
        self.fileCreateButton.setIconSize(QtCore.QSize(24, 24))
        self.fileCreateButton.setObjectName("fileCreateButton")
        self.horizontalLayout.addWidget(self.fileCreateButton)
        self.fileOpenButton = QtWidgets.QPushButton(self.centralwidget)
        self.fileOpenButton.setMaximumSize(QtCore.QSize(32, 32))
        self.fileOpenButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.fileOpenButton.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(resource_path("icons/document-open.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.fileOpenButton.setIcon(icon2)
        self.fileOpenButton.setIconSize(QtCore.QSize(24, 24))
        self.fileOpenButton.setObjectName("fileOpenButton")
        self.horizontalLayout.addWidget(self.fileOpenButton)
        self.fileSaveButton = QtWidgets.QPushButton(self.centralwidget)
        self.fileSaveButton.setMaximumSize(QtCore.QSize(32, 32))
        self.fileSaveButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.fileSaveButton.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(resource_path("icons/document-save.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.fileSaveButton.setIcon(icon3)
        self.fileSaveButton.setIconSize(QtCore.QSize(24, 24))
        self.fileSaveButton.setObjectName("fileSaveButton")
        self.horizontalLayout.addWidget(self.fileSaveButton)
        self.fileSaveAsButton = QtWidgets.QPushButton(self.centralwidget)
        self.fileSaveAsButton.setMaximumSize(QtCore.QSize(32, 32))
        self.fileSaveAsButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.fileSaveAsButton.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(resource_path("icons/document-save-as.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.fileSaveAsButton.setIcon(icon4)
        self.fileSaveAsButton.setIconSize(QtCore.QSize(24, 24))
        self.fileSaveAsButton.setObjectName("fileSaveAsButton")
        self.horizontalLayout.addWidget(self.fileSaveAsButton)
        self.fileRevertButton = QtWidgets.QPushButton(self.centralwidget)
        self.fileRevertButton.setMaximumSize(QtCore.QSize(32, 32))
        self.fileRevertButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.fileRevertButton.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(resource_path("icons/document-revert.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.fileRevertButton.setIcon(icon5)
        self.fileRevertButton.setIconSize(QtCore.QSize(24, 24))
        self.fileRevertButton.setObjectName("fileRevertButton")
        self.horizontalLayout.addWidget(self.fileRevertButton)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setMinimumSize(QtCore.QSize(8, 32))
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout.addWidget(self.line)
        self.tabAddButton = QtWidgets.QPushButton(self.centralwidget)
        self.tabAddButton.setMaximumSize(QtCore.QSize(32, 32))
        self.tabAddButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.tabAddButton.setText("")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(resource_path("icons/tab-new.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabAddButton.setIcon(icon6)
        self.tabAddButton.setIconSize(QtCore.QSize(24, 24))
        self.tabAddButton.setObjectName("tabAddButton")
        self.horizontalLayout.addWidget(self.tabAddButton)
        self.tabRemoveButton = QtWidgets.QPushButton(self.centralwidget)
        self.tabRemoveButton.setEnabled(False)
        self.tabRemoveButton.setMaximumSize(QtCore.QSize(32, 32))
        self.tabRemoveButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.tabRemoveButton.setText("")
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(resource_path("icons/tab-remove.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabRemoveButton.setIcon(icon7)
        self.tabRemoveButton.setIconSize(QtCore.QSize(24, 24))
        self.tabRemoveButton.setObjectName("tabRemoveButton")
        self.horizontalLayout.addWidget(self.tabRemoveButton)
        self.tabEditButton = QtWidgets.QPushButton(self.centralwidget)
        self.tabEditButton.setEnabled(False)
        self.tabEditButton.setMaximumSize(QtCore.QSize(32, 32))
        self.tabEditButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.tabEditButton.setText("")
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(resource_path("icons/tab-edit.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabEditButton.setIcon(icon8)
        self.tabEditButton.setIconSize(QtCore.QSize(24, 24))
        self.tabEditButton.setObjectName("tabEditButton")
        self.horizontalLayout.addWidget(self.tabEditButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.searchLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.searchLineEdit.setMinimumSize(QtCore.QSize(320, 32))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.searchLineEdit.setFont(font)
        self.searchLineEdit.setClearButtonEnabled(True)
        self.searchLineEdit.setObjectName("searchLineEdit")
        self.horizontalLayout.addWidget(self.searchLineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.verticalLayout.addWidget(self.tabWidget)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.remarkAddButton = QtWidgets.QPushButton(self.centralwidget)
        self.remarkAddButton.setMaximumSize(QtCore.QSize(32, 32))
        self.remarkAddButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.remarkAddButton.setText("")
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(resource_path("icons/add.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.remarkAddButton.setIcon(icon9)
        self.remarkAddButton.setIconSize(QtCore.QSize(24, 24))
        self.remarkAddButton.setObjectName("remarkAddButton")
        self.horizontalLayout_2.addWidget(self.remarkAddButton)
        self.remarkRemoveButton = QtWidgets.QPushButton(self.centralwidget)
        self.remarkRemoveButton.setEnabled(False)
        self.remarkRemoveButton.setMaximumSize(QtCore.QSize(32, 32))
        self.remarkRemoveButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.remarkRemoveButton.setText("")
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(resource_path("icons/remove.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.remarkRemoveButton.setIcon(icon10)
        self.remarkRemoveButton.setIconSize(QtCore.QSize(24, 24))
        self.remarkRemoveButton.setObjectName("remarkRemoveButton")
        self.horizontalLayout_2.addWidget(self.remarkRemoveButton)
        self.remarkEditButton = QtWidgets.QPushButton(self.centralwidget)
        self.remarkEditButton.setEnabled(False)
        self.remarkEditButton.setMaximumSize(QtCore.QSize(32, 32))
        self.remarkEditButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.remarkEditButton.setText("")
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap(resource_path("icons/edit.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.remarkEditButton.setIcon(icon11)
        self.remarkEditButton.setIconSize(QtCore.QSize(24, 24))
        self.remarkEditButton.setObjectName("remarkEditButton")
        self.horizontalLayout_2.addWidget(self.remarkEditButton)
        self.remarkCopyButton = QtWidgets.QPushButton(self.centralwidget)
        self.remarkCopyButton.setEnabled(False)
        self.remarkCopyButton.setMaximumSize(QtCore.QSize(32, 32))
        self.remarkCopyButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.remarkCopyButton.setText("")
        icon12 = QtGui.QIcon()
        icon12.addPixmap(QtGui.QPixmap(resource_path("icons/copy.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.remarkCopyButton.setIcon(icon12)
        self.remarkCopyButton.setIconSize(QtCore.QSize(24, 24))
        self.remarkCopyButton.setObjectName("remarkCopyButton")
        self.horizontalLayout_2.addWidget(self.remarkCopyButton)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.listClearButton = QtWidgets.QPushButton(self.centralwidget)
        self.listClearButton.setEnabled(True)
        self.listClearButton.setMaximumSize(QtCore.QSize(32, 32))
        self.listClearButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.listClearButton.setText("")
        icon13 = QtGui.QIcon()
        icon13.addPixmap(QtGui.QPixmap(resource_path("icons/clear.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.listClearButton.setIcon(icon13)
        self.listClearButton.setIconSize(QtCore.QSize(24, 24))
        self.listClearButton.setObjectName("listClearButton")
        self.horizontalLayout_2.addWidget(self.listClearButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Помощник нормоконтролёра"))
        self.fileCreateButton.setToolTip(_translate("MainWindow", "Создать документ"))
        self.fileOpenButton.setToolTip(_translate("MainWindow", "Открыть документ"))
        self.fileSaveButton.setToolTip(_translate("MainWindow", "Сохранить документ"))
        self.fileSaveAsButton.setToolTip(_translate("MainWindow", "Сохранить документ как"))
        self.fileRevertButton.setToolTip(_translate("MainWindow", "Отменить изменения"))
        self.tabAddButton.setToolTip(_translate("MainWindow", "Добавить вкладку"))
        self.tabRemoveButton.setToolTip(_translate("MainWindow", "Удалить вкладку"))
        self.tabEditButton.setToolTip(_translate("MainWindow", "Переименовать вкладку"))
        self.searchLineEdit.setPlaceholderText(_translate("MainWindow", "Поиск на текущей вкладке"))
        self.remarkAddButton.setToolTip(_translate("MainWindow", "Добавить замечание"))
        self.remarkRemoveButton.setToolTip(_translate("MainWindow", "Удалить выбранные замечания"))
        self.remarkEditButton.setToolTip(_translate("MainWindow", "Редактировать выбранные замечания"))
        self.remarkCopyButton.setToolTip(_translate("MainWindow", "Копировать выбранные замечания"))
        self.listClearButton.setToolTip(_translate("MainWindow", "Очистить список на вкладке"))
