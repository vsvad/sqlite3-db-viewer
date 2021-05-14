#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from interface import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
import sqlite3


def list_tables(c):
    c.execute('SELECT name FROM sqlite_master WHERE type = "table";')
    return c.fetchone()


def column_list(c, table_name):
    c.execute('SELECT * FROM ' + table_name)
    return [description[0] for description in c.description]


def values(c, table_name):
    c.execute('SELECT * FROM ' + table_name)
    return c.fetchall()


class Table(list):

    def __init__(self, name, columns):
        super().__init__(self)
        self.columns = columns
        self.table_name = name


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setupEvents()
        self.db_tables = {}

    def setupEvents(self):
        self.open_b.clicked.connect(self.loadDB)
        self.view_b.clicked.connect(self.viewDB)

    def loadDB(self, event=None):
        fname = QtWidgets.QFileDialog.getOpenFileName(self,
                                                'Выберите базу данных',
                                                None,
                                                'SQLite DB (*.db *.sqlite *.sqlite3);All files (*)'
                                                )[0]
        if not fname:
            return
        try:
            self.openDB(fname)
        except sqlite3.Error:
            self.step1description.setText('<span style="color: #ff0000;">Ошибка!!!</span>')
        else:
            self.step1description.setText("1. Выберите таблицу.")
            self.view_b.setEnabled(True)

    def openDB(self, fname):
        db = sqlite3.connect(fname)
        cursor = db.cursor()
        tbls = list_tables(cursor)
        for tbl in tbls:
            col = column_list(cursor, tbl)
            self.db_tables[tbl] = Table(tbl, col)
            self.db_tables[tbl].extend(values(cursor, tbl))
            self.tablesList.addItem(tbl)
        db.close()

    def viewDB(self, event=None):
        items = self.tablesList.selectedItems()
        if not items:
            QtWidgets.QMessageBox.critical(self,
                                          'Ошибка',
                                          'Выберите таблицу',
                                          QtWidgets.QMessageBox.Ok,
                                          QtWidgets.QMessageBox.Ok)
            return
        it = items[0].text()
        table = self.db_tables[it]
        for n, cl in enumerate(table.columns):
            lbl = QtWidgets.QLabel('<b>' + cl + '</b>')
            lbl.setFrameShape(QtWidgets.QFrame.StyledPanel)
            lbl.setFrameShadow(QtWidgets.QFrame.Raised)
            self.tableContent.addWidget(lbl, 0, n)
        for i, row in enumerate(table, 1):
            for j, e in enumerate(row):
                lbl = QtWidgets.QLabel(str(e))
                lbl.setFrameShape(QtWidgets.QFrame.StyledPanel)
                lbl.setFrameShadow(QtWidgets.QFrame.Raised)
                self.tableContent.addWidget(lbl, i, j)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = MainWindow()
    win.show()
    app.exec_()
