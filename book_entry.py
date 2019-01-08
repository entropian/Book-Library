from isbntools.app import *
import urllib, json, datetime


class BookEntry:
    def __init__(self):
        self.isbn = ""
        self.title = ""
        self.authors = []
        self.publisher = ""
        self.publication_year = ""
        self.language = ""
        self.descrption = ""
        self.cover = ""
        self.time_added = datetime.datetime(1, 1, 1)

    # isbn13 must be a valid ISBN
    def getInfo(self, isbn13):
        info = meta(isbn13)
        self.isbn = isbn13
        self.title = info['Title']
        self.authors = info['Authors']
        self.publisher = info['Publisher']
        self.publication_year = info['Year']
        self.language = info['Language']
        self.description = desc(isbn13)
        address = "https://www.googleapis.com/books/v1/volumes?q=isbn:" + self.isbn
        with urllib.request.urlopen(address) as url:
            data = json.loads(url.read().decode())
            self.cover = data['items'][0]['volumeInfo']['imageLinks']['thumbnail']
        self.time_added = datetime.datetime.now()

    def __str__(self):
        output = "Title: " + self.title + "\n"
        if len(self.authors) > 1:
            output += "Authors: "
            for name in self.authors[:-1]:
                output += name + ", "
            else:
                output += name + "\n"
        else:
            output += "Author: " + self.authors[0] + "\n"
        output += ("Publisher: " + self.publisher + "\n"
        + "Year: " + self.publication_year + "\n"
        + "Language: " + self.language + "\n")
        return output
