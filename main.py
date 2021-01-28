import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QTableWidgetItem
from PyQt5.QtWidgets import QMainWindow


class DBSample(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.con = sqlite3.connect("coffee.sqlite")
        self.update_table()

    def update_table(self):
        cur = self.con.cursor()
        res = cur.execute("""SELECT * FROM coffee
            WHERE id""").fetchall()
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            roasting = cur.execute("""SELECT title FROM roastings
                WHERE id = ?""", (row[2],)).fetchone()
            for j, elem in enumerate(row):
                if j == 2:
                    self.tableWidget.setItem(
                        i, j, QTableWidgetItem(roasting[0]))
                elif j == 3:
                    if elem == 1:
                        self.tableWidget.setItem(
                            i, j, QTableWidgetItem('молотый'))
                    else:
                        self.tableWidget.setItem(
                            i, j, QTableWidgetItem('в зёрнах'))
                else:
                    self.tableWidget.setItem(
                        i, j, QTableWidgetItem(str(elem)))

    def closeEvent(self, event):
        self.con.close()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DBSample()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())

