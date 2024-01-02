class Book: 
    def __init__(self, title, author, year): 
        self.title = title 
        self.author = author 
        self.year = year 


class Library: 
    def __init__(self): 
        self.books = [] 

    def add_book(self, book): 
        self.books.append(book) 

    def remove_book(self, book): 
        self.books.remove(book) 
    def get_book_by_title(self, title): 
        for book in self.books: 
            if book.title == title: 
                return book 

    def get_books_by_author(self, author): 
        books_by_author = [] 
        for book in self.books: 
            if book.author == author: 
                books_by_author.append(book) 
        return books_by_author
library = Library()

# Create two books
book_one = Book("The Cat in the Hat", "Dr. Seuss", 1957)
book_two = Book("The Lorax", "Dr. Seuss", 1971)

# Add the books to the library
library.add_book(book_one)
library.add_book(book_two)

# Get book by title
book = library.get_book_by_title("The Cat in the Hat")
print(book.title + " was written by " + book.author + " in " + str(book.year))

# Get books by author
books = library.get_books_by_author("Dr. Seuss")
for book in books:
    print(book.title + " was written by " + book.author + " in " + str(book.year))
