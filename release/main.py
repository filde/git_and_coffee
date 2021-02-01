import sqlite3
import sys

from PyQt5.QtWidgets import QApplication, QTableWidgetItem
from PyQt5.QtWidgets import QMainWindow, QDialog, QMessageBox
from main_d import *
from addEditCoffeeForm import *


class AddCoffee(QDialog, Ui_Dialog):
    def __init__(self, self1, con, item_id, *coffee):
        super().__init__(self1)
        self.setupUi(self)
        self.con = con
        cur = con.cursor()
        res = cur.execute("""SELECT * FROM roastings WHERE id""").fetchall()
        self.obg.addItems([i[1] for i in res])
        self.types.addItems(['в зёрнах', 'молотый'])
        self.id = int(item_id)
        if coffee:
            self.setWindowTitle('Редактирование записи')
            self.title.setText(coffee[0])
            self.obg.setCurrentText(coffee[1])
            self.types.setCurrentText(coffee[2])
            self.description.setText(coffee[3])
            self.price.setValue(int(coffee[4]))
            self.vol.setValue(int(coffee[5]))
            self.btn.clicked.connect(self.update_item)
        else:
            self.setWindowTitle('Новая запись')
            self.btn.clicked.connect(self.create_new)

    def create_new(self):
        cur = self.con.cursor()
        title = self.title.text()
        obg = self.obg.currentIndex()
        types = self.types.currentIndex()
        description = self.description.text()
        price = self.price.value()
        vol = self.vol.value()
        cur.execute("""INSERT INTO coffee
                VALUES(?, ?, ?, ?, ?, ?, ?)""", (self.id, title, obg + 1,
                                                 types, description,
                                                 int(price), int(vol)))
        self.con.commit()
        self.close()

    def update_item(self):
        cur = self.con.cursor()
        title = self.title.text()
        obg = self.obg.currentIndex()
        types = self.types.currentIndex()
        description = self.description.text()
        price = self.price.value()
        vol = self.vol.value()
        cur.execute("""UPDATE coffee SET title = ?
                WHERE id = ?""", (title, self.id))
        cur.execute("""UPDATE coffee SET roasting = ?
                WHERE id = ?""", (obg + 1, self.id))
        cur.execute("""UPDATE coffee SET shredding = ?
                WHERE id = ?""", (types, self.id))
        cur.execute("""UPDATE coffee SET taste = ?
                WHERE id = ?""", (description, self.id))
        cur.execute("""UPDATE coffee SET price = ?
                        WHERE id = ?""", (int(price), self.id))
        cur.execute("""UPDATE coffee SET volume = ?
                        WHERE id = ?""", (int(vol), self.id))
        self.con.commit()
        self.close()


class Coffee(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.con = sqlite3.connect("data/coffee.sqlite")
        self.btn_new.clicked.connect(self.new_coffee)
        self.btn_change.clicked.connect(self.change_coffee)
        self.btn_remove.clicked.connect(self.remove_coffee)
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

    def new_coffee(self):
        cur = self.con.cursor()
        res = cur.execute("""SELECT MAX(id) FROM coffee""").fetchone()
        d = AddCoffee(self, self.con, res[0] + 1)
        d.show()
        d.exec()
        self.update_table()

    def change_coffee(self):
        if len(set([i.row() for i in self.tableWidget.selectedItems()])) != 1:
            return
        row = self.tableWidget.currentRow()
        d = AddCoffee(self, self.con, *[self.tableWidget.item(row, i).text()
                                        for i in range(7)])
        d.show()
        d.exec()
        self.update_table()

    def remove_coffee(self):
        rows = list(set([i.row() for i in self.tableWidget.selectedItems()]))
        ids = [self.tableWidget.item(i, 0).text() for i in rows]
        if len(ids) < 1:
            return
        valid = QMessageBox.question(self, '', "Действительно удалить элемент(ы)?",
                                     QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:
            cur = self.con.cursor()
            cur.execute("DELETE FROM coffee WHERE id IN (" + ", ".join(
                '?' * len(ids)) + ")", ids)
            self.con.commit()
        self.update_table()

    def closeEvent(self, event):
        self.con.close()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Coffee()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())

