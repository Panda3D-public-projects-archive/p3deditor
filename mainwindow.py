# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created: Wed Nov 30 14:26:21 2011
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(267, 566)
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "P3D Editor", None, QtGui.QApplication.UnicodeUTF8))
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setMargin(4)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.treeWidget = QtGui.QTreeWidget(self.splitter)
        self.treeWidget.setAnimated(True)
        self.treeWidget.setObjectName(_fromUtf8("treeWidget"))
        self.treeWidget.headerItem().setText(0, QtGui.QApplication.translate("MainWindow", "Tools", None, QtGui.QApplication.UnicodeUTF8))
        item_0 = QtGui.QTreeWidgetItem(self.treeWidget)
        self.treeWidget.topLevelItem(0).setText(0, QtGui.QApplication.translate("MainWindow", "Lighting", None, QtGui.QApplication.UnicodeUTF8))
        item_1 = QtGui.QTreeWidgetItem(item_0)
        self.treeWidget.topLevelItem(0).child(0).setText(0, QtGui.QApplication.translate("MainWindow", "add PointLight", None, QtGui.QApplication.UnicodeUTF8))
        item_1 = QtGui.QTreeWidgetItem(item_0)
        self.treeWidget.topLevelItem(0).child(1).setText(0, QtGui.QApplication.translate("MainWindow", "add DirectionalLight", None, QtGui.QApplication.UnicodeUTF8))
        item_1 = QtGui.QTreeWidgetItem(item_0)
        self.treeWidget.topLevelItem(0).child(2).setText(0, QtGui.QApplication.translate("MainWindow", "add Spotlight", None, QtGui.QApplication.UnicodeUTF8))
        item_0 = QtGui.QTreeWidgetItem(self.treeWidget)
        self.treeWidget.topLevelItem(1).setText(0, QtGui.QApplication.translate("MainWindow", "Modifiers", None, QtGui.QApplication.UnicodeUTF8))
        item_1 = QtGui.QTreeWidgetItem(item_0)
        self.treeWidget.topLevelItem(1).child(0).setText(0, QtGui.QApplication.translate("MainWindow", "use model as Brush", None, QtGui.QApplication.UnicodeUTF8))
        self.eggPool = QtGui.QListWidget(self.splitter)
        self.eggPool.setObjectName(_fromUtf8("eggPool"))
        self.verticalLayout.addWidget(self.splitter)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 267, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuWorkspace = QtGui.QMenu(self.menubar)
        self.menuWorkspace.setTitle(QtGui.QApplication.translate("MainWindow", "Workspace", None, QtGui.QApplication.UnicodeUTF8))
        self.menuWorkspace.setObjectName(_fromUtf8("menuWorkspace"))
        self.menuSettings = QtGui.QMenu(self.menubar)
        self.menuSettings.setTitle(QtGui.QApplication.translate("MainWindow", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.menuSettings.setObjectName(_fromUtf8("menuSettings"))
        MainWindow.setMenuBar(self.menubar)
        self.actionScene = QtGui.QAction(MainWindow)
        self.actionScene.setText(QtGui.QApplication.translate("MainWindow", "Scene", None, QtGui.QApplication.UnicodeUTF8))
        self.actionScene.setObjectName(_fromUtf8("actionScene"))
        self.actionLoad = QtGui.QAction(MainWindow)
        self.actionLoad.setText(QtGui.QApplication.translate("MainWindow", "Load", None, QtGui.QApplication.UnicodeUTF8))
        self.actionLoad.setObjectName(_fromUtf8("actionLoad"))
        self.actionNew_2 = QtGui.QAction(MainWindow)
        self.actionNew_2.setText(QtGui.QApplication.translate("MainWindow", "New", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNew_2.setObjectName(_fromUtf8("actionNew_2"))
        self.actionSave_Scene = QtGui.QAction(MainWindow)
        self.actionSave_Scene.setText(QtGui.QApplication.translate("MainWindow", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave_Scene.setObjectName(_fromUtf8("actionSave_Scene"))
        self.actionExit = QtGui.QAction(MainWindow)
        self.actionExit.setText(QtGui.QApplication.translate("MainWindow", "Exit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.actionRefresh = QtGui.QAction(MainWindow)
        self.actionRefresh.setText(QtGui.QApplication.translate("MainWindow", "Refresh", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRefresh.setObjectName(_fromUtf8("actionRefresh"))
        self.menuFile.addAction(self.actionNew_2)
        self.menuFile.addAction(self.actionLoad)
        self.menuFile.addAction(self.actionSave_Scene)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuWorkspace.addAction(self.actionRefresh)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuWorkspace.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        __sortingEnabled = self.treeWidget.isSortingEnabled()
        self.treeWidget.setSortingEnabled(False)
        self.treeWidget.setSortingEnabled(__sortingEnabled)

