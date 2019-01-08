import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
            QMessageBox, QAction, QTableWidget, QTableWidgetItem, QLineEdit,
            QVBoxLayout, QHBoxLayout, QInputDialog, QPlainTextEdit,
            QLabel)
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QIcon, QPixmap
from book_entry import *
from book_db import *

def stringListToCommaSeparatedString(str_list):
    output = ""
    if len(str_list) > 1:
        for str in str_list[:-1]:
            output += str + ", "
        else:
            output += str
        return output
    else:
        output += str_list[0]
        return output

class App(QWidget):
    def __init__(self, book_db):
        super().__init__()
        self.title = "My Library"
        self.left = 200
        self.top = 200
        self.width = 820
        self.height = 600
        self.book_db = book_db

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.createTableFromEntries(self.book_db.book_entries)
        table_layout = QVBoxLayout()
        table_layout.addWidget(self.tableWidget)
        self.add_button = QPushButton("Add", self)
        self.add_button.clicked.connect(self.add_on_click)
        self.del_button = QPushButton("Delete", self)
        self.del_button.clicked.connect(self.del_on_click)
        table_layout.addWidget(self.add_button)
        table_layout.addWidget(self.del_button)

        detail_layout = QVBoxLayout()
        self.cover_display = QLabel(self)
        self.cover_display.setAlignment(Qt.AlignCenter)
        self.desc_edit = QPlainTextEdit("")
        self.desc_edit.setReadOnly(True)
        detail_layout.addWidget(self.cover_display)
        detail_layout.addWidget(self.desc_edit)

        self.layout = QHBoxLayout()
        self.layout.addLayout(table_layout, 3)
        self.layout.addLayout(detail_layout, 1)
        self.setLayout(self.layout)

        self.show()

    def table_on_click(self, row, column):
        isbn_index = 5
        isbn = self.tableWidget.item(row, isbn_index).text()
        cover_file = self.book_db.getCoverFilename(isbn)
        self.cover_display.setPixmap(QPixmap(cover_file))
        desc = book_db.getDesc(isbn)
        if desc:
            desc = "Description: " + desc
            self.desc_edit.setPlainText(desc.replace("\n", ""))

    def createTableFromEntries(self, book_entries):
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(len(book_entries))
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setColumnWidth(0, 250)
        self.tableWidget.setColumnWidth(3, 50)
        self.tableWidget.setColumnWidth(4, 70)
        self.tableWidget.setHorizontalHeaderLabels(["Title", "Author", "Publisher", "Year", "Language", "ISBN"])
        self.tableWidget.cellClicked.connect(self.table_on_click)
        count = 0
        # Populate table
        for entry in book_db.book_entries:
            self.tableWidget.setItem(count,0, QTableWidgetItem(entry.title))
            authors = stringListToCommaSeparatedString(entry.authors)
            self.tableWidget.setItem(count,1, QTableWidgetItem(authors))
            self.tableWidget.setItem(count,2, QTableWidgetItem(entry.publisher))
            self.tableWidget.setItem(count,3, QTableWidgetItem(entry.publish_year))
            self.tableWidget.setItem(count,4, QTableWidgetItem(entry.language))
            self.tableWidget.setItem(count,5, QTableWidgetItem(entry.isbn))
            count += 1
        # Make table uneditable but selectable
        num_rows = self.tableWidget.rowCount()
        num_cols = self.tableWidget.columnCount()
        for i in range(num_rows):
            for j in range(num_cols):
                cell = self.tableWidget.item(i, j)
                if cell:
                    cell.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)


    @pyqtSlot()
    def add_on_click(self):
        new_index = len(self.book_db.book_entries)
        isbn, okPressed = QInputDialog.getText(self, "Add book", "ISBN:", QLineEdit.Normal, "")
        if okPressed and isbn != '':
            entry = BookEntry()
            entry.getInfo(isbn)
            self.tableWidget.insertRow(new_index)
            self.book_db.insert_book(entry)
            self.tableWidget.setItem(new_index,0, QTableWidgetItem(entry.title))
            authors = stringListToCommaSeparatedString(entry.authors)
            self.tableWidget.setItem(new_index,1, QTableWidgetItem(authors))
            self.tableWidget.setItem(new_index,2, QTableWidgetItem(entry.publisher))
            self.tableWidget.setItem(new_index,3, QTableWidgetItem(entry.publication_year))
            self.tableWidget.setItem(new_index,4, QTableWidgetItem(entry.language))
            self.tableWidget.setItem(new_index,5, QTableWidgetItem(entry.isbn))


    @pyqtSlot()
    def del_on_click(self):
        selected_items = self.tableWidget.selectedIndexes()
        rows = set()
        for item in selected_items:
            rows.add(item.row())
        rows = list(rows)
        rows.sort(reverse=True)
        for row in rows:
            isbn_index = 5
            isbn = self.tableWidget.item(row, isbn_index).text()
            self.book_db.delete_book(isbn)
            self.tableWidget.removeRow(row)

if __name__ == "__main__":
    book_db = BookDB()
    app = QApplication(sys.argv)
    ex = App(book_db)
    ex.initUI()
    sys.exit(app.exec_())
