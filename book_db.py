import os
import mysql.connector
from mysql.connector import MySQLConnection, Error
from book_entry import *

class BookDB:
    def __init__(self):
        self.conn = MySQLConnection(host='localhost', user='root', password='qwe4ASD^',\
                                database='booklibrary')
        self.cursor = self.conn.cursor()
        rows = self.query_with_fetchall()
        self.book_entries = []
        # Sortable attributes: title, author, publisher, publish_year, language, isbn
        # TODO: add time_added
        # NOTE: serious semantic coupling
        self.sort_attr_order_flags = [False, False, False, False, False, False, False]
        for row in rows:
            book_entry = BookEntry()
            book_entry.title = row[0]
            book_entry.isbn = row[1]
            book_entry.authors = row[2].split(", ")
            book_entry.publisher = row[3]
            book_entry.publish_year = row[4]
            book_entry.language = row[5]
            book_entry.cover = row[6]
            self.book_entries.append(book_entry)
            book_entry.description = self.getDesc(book_entry.isbn)
            book_entry.time_added = row[7]

    def sortByAttr(self, index):
        if index == 0:
            self.book_entries.sort(key=lambda entry: entry.title, reverse=self.sort_attr_order_flags[index])
        elif index == 1:
            self.book_entries.sort(key=lambda entry: entry.authors, reverse=self.sort_attr_order_flags[index])
        elif index == 2:
            self.book_entries.sort(key=lambda entry: entry.publisher, reverse=self.sort_attr_order_flags[index])
        elif index == 3:
            self.book_entries.sort(key=lambda entry: entry.publish_year, reverse=self.sort_attr_order_flags[index])
        elif index == 4:
            self.book_entries.sort(key=lambda entry: entry.language, reverse=self.sort_attr_order_flags[index])
        elif index == 5:
            self.book_entries.sort(key=lambda entry: entry.isbn, reverse=self.sort_attr_order_flags[index])
        self.sort_attr_order_flags[index] = not self.sort_attr_order_flags[index]

    def getDisplayColumnNames(self):
        return ["Title", "Author", "Publisher", "Year", "Language", "ISBN"]

    def getCoverFilename(self, isbn):
        for entry in self.book_entries:
            if isbn == entry.isbn:
                return entry.cover

    def getDesc(self, isbn):
        query = "SELECT * FROM description WHERE isbn = " + isbn + ";"
        self.cursor.execute(query)
        entry = self.cursor.fetchone()
        if entry:
            return entry[1]

    def delDesc(self, isbn):
        query = "DELETE FROM description WHERE isbn = " + isbn + ";"
        self.cursor.execute(query)
        self.conn.commit()

    def insert_book(self, book_entry):
        # Download cover image
        local_cover = "img/" + book_entry.isbn + ".jpg"
        urllib.request.urlretrieve(book_entry.cover, local_cover)
        book_entry.cover = local_cover

        query1 = "INSERT INTO book(title, isbn, authors, publisher, year, language, cover, time_added) "\
                "VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
        authors = ""
        if len(book_entry.authors) > 1:
            for name in book_entry.authors[:-1]:
                authors += name + ", "
            else:
                authors += name
        else:
            authors += book_entry.authors[0]
        datetime_str = str(book_entry.time_added).split(".")[0]
        args1 = (book_entry.title, book_entry.isbn, authors, \
                book_entry.publisher, book_entry.publication_year, \
                book_entry.language, book_entry.cover, datetime_str)

        query2 = "INSERT INTO description(isbn, description) "\
                "VALUES(%s, %s)"
        args2 = (book_entry.isbn, book_entry.description)
        try:
            self.cursor.execute(query1, args1)
            if(book_entry.description):
                self.cursor.execute(query2, args2)
            self.conn.commit()
        except Error as error:
            print(error)
        finally:
            self.book_entries.append(book_entry)

    def delete_book(self, isbn):
        query = "DELETE FROM book WHERE isbn = " + isbn + ";"
        try:
            self.delDesc(isbn)
            cover_file = "img/" + isbn + ".jpg"
            if os.path.exists(cover_file):
                os.remove(cover_file)
            self.cursor.execute(query)
            self.conn.commit()
        except Error as error:
            print(error)
        finally:
            for entry in self.book_entries:
                if entry.isbn == isbn:
                    self.book_entries.remove(entry)


    def query_with_fetchall(self):
        try:
            self.cursor.execute("SELECT * FROM book;")
            rows = self.cursor.fetchall()
            return rows
        except Error as e:
            print(e)
