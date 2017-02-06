# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design.ui'
#
# Created: Fri Oct 28 17:41:42 2016
#      by: PyQt4 UI code generator 4.10.4
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
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab_artists = QtGui.QWidget()
        self.tab_artists.setObjectName(_fromUtf8("tab_artists"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.tab_artists)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.splitter_2 = QtGui.QSplitter(self.tab_artists)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName(_fromUtf8("splitter_2"))
        self.treeArtists = QtGui.QTreeView(self.splitter_2)
        self.treeArtists.setMaximumSize(QtCore.QSize(300, 16777215))
        self.treeArtists.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.treeArtists.setObjectName(_fromUtf8("treeArtists"))
        self.treeArtists.header().setVisible(False)
        self.viewerArtists = QtGui.QTextBrowser(self.splitter_2)
        self.viewerArtists.setMinimumSize(QtCore.QSize(700, 0))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Courier New"))
        self.viewerArtists.setFont(font)
        self.viewerArtists.setObjectName(_fromUtf8("viewerArtists"))
        self.verticalLayout_2.addWidget(self.splitter_2)
        self.tabWidget.addTab(self.tab_artists, _fromUtf8(""))
        self.tab_tunings = QtGui.QWidget()
        self.tab_tunings.setObjectName(_fromUtf8("tab_tunings"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.tab_tunings)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.splitter = QtGui.QSplitter(self.tab_tunings)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.treeTunings = QtGui.QTreeView(self.splitter)
        self.treeTunings.setMaximumSize(QtCore.QSize(300, 16777215))
        self.treeTunings.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.treeTunings.setObjectName(_fromUtf8("treeTunings"))
        self.treeTunings.header().setVisible(False)
        self.viewerTunings = QtGui.QTextBrowser(self.splitter)
        self.viewerTunings.setMinimumSize(QtCore.QSize(700, 0))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Courier New"))
        self.viewerTunings.setFont(font)
        self.viewerTunings.setObjectName(_fromUtf8("viewerTunings"))
        self.verticalLayout_3.addWidget(self.splitter)
        self.tabWidget.addTab(self.tab_tunings, _fromUtf8(""))
        self.verticalLayout.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QtGui.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 998, 25))
        self.menuBar.setObjectName(_fromUtf8("menuBar"))
        MainWindow.setMenuBar(self.menuBar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.treeArtists, QtCore.SIGNAL(_fromUtf8("clicked(QModelIndex)")), MainWindow.onArtistClick)
        QtCore.QObject.connect(self.treeTunings, QtCore.SIGNAL(_fromUtf8("clicked(QModelIndex)")), MainWindow.onTuningClick)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Chord Explorer", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_artists), _translate("MainWindow", "Artists", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_tunings), _translate("MainWindow", "Tunings", None))

