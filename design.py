# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(998, 600)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setTabShape(QtGui.QTabWidget.Rounded)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab_artists = QtGui.QWidget()
        self.tab_artists.setObjectName(_fromUtf8("tab_artists"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.tab_artists)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.splitterArtists = QtGui.QSplitter(self.tab_artists)
        self.splitterArtists.setOrientation(QtCore.Qt.Horizontal)
        self.splitterArtists.setObjectName(_fromUtf8("splitterArtists"))
        self.treeArtists = QtGui.QTreeView(self.splitterArtists)
        self.treeArtists.setMaximumSize(QtCore.QSize(300, 16777215))
        self.treeArtists.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.treeArtists.setObjectName(_fromUtf8("treeArtists"))
        self.treeArtists.header().setVisible(False)
        self.viewerArtists = QtGui.QTextBrowser(self.splitterArtists)
        self.viewerArtists.setMinimumSize(QtCore.QSize(700, 0))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Courier New"))
        self.viewerArtists.setFont(font)
        self.viewerArtists.setObjectName(_fromUtf8("viewerArtists"))
        self.verticalLayout_2.addWidget(self.splitterArtists)
        self.tabWidget.addTab(self.tab_artists, _fromUtf8(""))
        self.tab_tunings = QtGui.QWidget()
        self.tab_tunings.setObjectName(_fromUtf8("tab_tunings"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.tab_tunings)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.splitterTunings = QtGui.QSplitter(self.tab_tunings)
        self.splitterTunings.setOrientation(QtCore.Qt.Horizontal)
        self.splitterTunings.setObjectName(_fromUtf8("splitterTunings"))
        self.treeTunings = QtGui.QTreeView(self.splitterTunings)
        self.treeTunings.setMaximumSize(QtCore.QSize(300, 16777215))
        self.treeTunings.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.treeTunings.setObjectName(_fromUtf8("treeTunings"))
        self.treeTunings.header().setVisible(False)
        self.viewerTunings = QtGui.QTextBrowser(self.splitterTunings)
        self.viewerTunings.setMinimumSize(QtCore.QSize(700, 0))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Courier New"))
        self.viewerTunings.setFont(font)
        self.viewerTunings.setObjectName(_fromUtf8("viewerTunings"))
        self.verticalLayout_3.addWidget(self.splitterTunings)
        self.tabWidget.addTab(self.tab_tunings, _fromUtf8(""))
        self.tab_search = QtGui.QWidget()
        self.tab_search.setObjectName(_fromUtf8("tab_search"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.tab_search)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.lineEdit = QtGui.QLineEdit(self.tab_search)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.verticalLayout_5.addWidget(self.lineEdit)
        self.verticalLayout_7 = QtGui.QVBoxLayout()
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.splitterSearch = QtGui.QSplitter(self.tab_search)
        self.splitterSearch.setOrientation(QtCore.Qt.Horizontal)
        self.splitterSearch.setObjectName(_fromUtf8("splitterSearch"))
        self.treeSearch = QtGui.QTreeView(self.splitterSearch)
        self.treeSearch.setMaximumSize(QtCore.QSize(300, 16777215))
        self.treeSearch.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.treeSearch.setObjectName(_fromUtf8("treeSearch"))
        self.treeSearch.header().setVisible(False)
        self.viewerSearch = QtGui.QTextBrowser(self.splitterSearch)
        self.viewerSearch.setObjectName(_fromUtf8("viewerSearch"))
        self.verticalLayout_7.addWidget(self.splitterSearch)
        self.verticalLayout_5.addLayout(self.verticalLayout_7)
        self.tabWidget.addTab(self.tab_search, _fromUtf8(""))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.tab)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.importEdit = QtGui.QLineEdit(self.tab)
        self.importEdit.setObjectName(_fromUtf8("importEdit"))
        self.verticalLayout_4.addWidget(self.importEdit)
        self.splitter = QtGui.QSplitter(self.tab)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.treeImport = QtGui.QTreeView(self.splitter)
        self.treeImport.setHeaderHidden(True)
        self.treeImport.setObjectName(_fromUtf8("treeImport"))
        self.viewerImport = QtGui.QTextBrowser(self.splitter)
        self.viewerImport.setObjectName(_fromUtf8("viewerImport"))
        self.verticalLayout_4.addWidget(self.splitter)
        self.verticalLayout_6.addLayout(self.verticalLayout_4)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.verticalLayout.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QtGui.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 998, 25))
        self.menuBar.setObjectName(_fromUtf8("menuBar"))
        MainWindow.setMenuBar(self.menuBar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.treeArtists, QtCore.SIGNAL(_fromUtf8("clicked(QModelIndex)")), MainWindow.treeIndexClicked)
        QtCore.QObject.connect(self.treeTunings, QtCore.SIGNAL(_fromUtf8("clicked(QModelIndex)")), MainWindow.treeIndexClicked)
        QtCore.QObject.connect(self.treeSearch, QtCore.SIGNAL(_fromUtf8("clicked(QModelIndex)")), MainWindow.treeIndexClicked)
        QtCore.QObject.connect(self.treeImport, QtCore.SIGNAL(_fromUtf8("clicked(QModelIndex)")), MainWindow.treeIndexClicked)
        QtCore.QObject.connect(self.viewerArtists, QtCore.SIGNAL(_fromUtf8("anchorClicked(QUrl)")), MainWindow.viewerLinkClicked)
        QtCore.QObject.connect(self.viewerImport, QtCore.SIGNAL(_fromUtf8("anchorClicked(QUrl)")), MainWindow.viewerLinkClicked)
        QtCore.QObject.connect(self.viewerSearch, QtCore.SIGNAL(_fromUtf8("anchorClicked(QUrl)")), MainWindow.viewerLinkClicked)
        QtCore.QObject.connect(self.viewerTunings, QtCore.SIGNAL(_fromUtf8("anchorClicked(QUrl)")), MainWindow.viewerLinkClicked)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Chord Explorer", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_artists), _translate("MainWindow", "Artists", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_tunings), _translate("MainWindow", "Tunings", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_search), _translate("MainWindow", "Search", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Import", None))

