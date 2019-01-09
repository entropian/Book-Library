import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
            QMessageBox, QAction, QTableWidget, QTableWidgetItem, QLineEdit,
            QVBoxLayout, QHBoxLayout, QInputDialog, QPlainTextEdit,
            QLabel, QLineEdit, QRadioButton, QMessageBox)
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QIcon, QPixmap
from book_entry import *
from book_db import *



class App(QWidget):
    def __init__(self, book_db):
        super().__init__()
        self.title = "My Library"
        self.left = 200
        self.top = 200
        self.width = 900
        self.height = 600
        self.book_db = book_db

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Table portion
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_bar = QLineEdit()
        self.search_bar.textChanged.connect(self.search_bar_on_click)
        search_by_title_button = QRadioButton("by title")
        search_by_title_button.setChecked(True)
        search_by_title_button.toggled.connect(self.by_title_on_toggle)
        search_by_author_button = QRadioButton("by author")
        search_by_author_button.toggled.connect(self.by_author_on_toggle)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(search_by_title_button)
        search_layout.addWidget(search_by_author_button)
        table_layout = QVBoxLayout()
        table_layout.addLayout(search_layout)
        self.createTable()
        table_layout.addWidget(self.tableWidget)
        self.add_button = QPushButton("Add", self)
        self.add_button.clicked.connect(self.add_on_click)
        self.del_button = QPushButton("Delete", self)
        self.del_button.clicked.connect(self.del_on_click)
        table_layout.addWidget(self.add_button)
        table_layout.addWidget(self.del_button)

        # Detail portion
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

    def by_title_on_toggle(self, checked):
        if checked:
            self.book_db.setSearchByTitle()

    def by_author_on_toggle(self, checked):
        if checked:
            self.book_db.setSearchByAuthor()

    def search_bar_on_click(self, text):
        self.book_db.search_str = text.lower()
        self.populateTable()

    def table_on_click(self, row, column):
        isbn_index = 5
        isbn = self.tableWidget.item(row, isbn_index).text()
        book_entry = self.book_db.getEntryFromISBN(isbn)
        self.cover_display.setPixmap(QPixmap(book_entry.cover))
        detail_text = ""
        detail_text += ("Authors: " if len(book_entry.authors) > 1 else "Author: ") + stringListToCommaSeparatedString(book_entry.authors) + "\n"
        detail_text += "Publisher: " + book_entry.publisher + "\n"
        detail_text += "ISBN: " + book_entry.isbn + "\n"
        desc = book_db.getDesc(isbn)
        if desc:
            detail_text += "Description: " + desc.replace("\n", " ")
        self.desc_edit.setPlainText(detail_text)

    def populateTable(self):
        book_entries = self.book_db.getBookEntries()
        self.tableWidget.clear()
        self.tableWidget.setRowCount(len(book_entries))
        self.tableWidget.cellClicked.connect(self.table_on_click)
        header_names = self.book_db.getDisplayColumnNames()
        self.tableWidget.setColumnCount(len(header_names))
        self.tableWidget.setHorizontalHeaderLabels(header_names)
        self.tableWidget.horizontalHeader().sectionClicked.connect(self.table_header_on_click)
        self.tableWidget.setColumnWidth(0, 250)
        self.tableWidget.setColumnWidth(3, 50)
        self.tableWidget.setColumnWidth(4, 70)
        count = 0
        # Populate table
        for entry in book_entries:
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

    def table_header_on_click(self, logicalIndex):
        self.book_db.sortByAttr(logicalIndex)
        self.populateTable()

    def createTable(self):
        self.tableWidget = QTableWidget()
        self.populateTable()

    @pyqtSlot()
    def add_on_click(self):
        new_index = len(self.book_db.getBookEntries())
        isbn, okPressed = QInputDialog.getText(self, "Add book", "ISBN:", QLineEdit.Normal, "")
        if okPressed and isbn != '':
            entry = BookEntry()
            if entry.getInfo(isbn):
                self.tableWidget.insertRow(new_index)
                self.book_db.insert_book(entry)
                self.tableWidget.setItem(new_index,0, QTableWidgetItem(entry.title))
                authors = stringListToCommaSeparatedString(entry.authors)
                self.tableWidget.setItem(new_index,1, QTableWidgetItem(authors))
                self.tableWidget.setItem(new_index,2, QTableWidgetItem(entry.publisher))
                self.tableWidget.setItem(new_index,3, QTableWidgetItem(entry.publication_year))
                self.tableWidget.setItem(new_index,4, QTableWidgetItem(entry.language))
                self.tableWidget.setItem(new_index,5, QTableWidgetItem(entry.isbn))
            else:
                alert = QMessageBox()
                alert.setStyleSheet("QLabel{min-width: 100px;}")
                alert.setWindowTitle("Error")
                alert.setText("Invalid ISBN")
                alert.exec_()

    @pyqtSlot()
    def del_on_click(self):
        selected_items = self.tableWidget.selectedIndexes()
        rows = set()
        for item in selected_items:
            rows.add(item.row())
        if len(rows) > 1:
            qm = QMessageBox()
            qm.setWindowTitle("My Library")
            ret = qm.question(self, '', "Delete multiple entries?", qm.Yes | qm.No)
            if ret == qm.No:
                return
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
