class Book:
    def __init__(self, title, author, year):
        self.title = title
        self.author = author
        self.year = year

    def get_info(self):
        print(f'{self.title} was written by {self.author} in {self.year}')

    def set_price(self, price):
        self.price = price
        print(f'{self.title} costs ${self.price}')
        self.author = author
        self.year = year

    def get_info(self):
        print(f'{self.title} was written by {self.author} in {self.year}')

    def set_price(self, price):
        self.price = price
        print(f'{self.title} costs ${self.price}')
