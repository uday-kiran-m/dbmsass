import eel

import mysql.connector as mc


def db_init(dbIP,user,passwd):
    ## Schema
    ## BookStars(username varchar(30),password varchar(30),staff TinyInt(1),borrowed_count INT,Logged_in TinyInt(1))
    ## BookShelf(bookid INT,bookname varchar(50),bookauthor varchar(50),stock INT)
    ## BookStash(username foreign key bookstars , bookid foreign key bookshelf, fromdate, todate)
    ##
    global mycurs
    
    mycurs.execute("""
                   CREATE DATABASE IF NOT EXISTS BookHub;
CREATE TABLE IF NOT EXISTS BookHub.BookStars (
    username VARCHAR(30) PRIMARY KEY,
    password VARCHAR(30) NOT NULL,
    staff TINYINT(1) DEFAULT 0, -- Assuming 0 means regular user, 1 means staff
    borrowed_count INT DEFAULT 0, -- To track how many books have been borrowed
    Logged_in TINYINT(1) DEFAULT 0 -- 0 means not logged in, 1 means logged in
);

CREATE TABLE IF NOT EXISTS BookHub.BookShelf (
    bookid INT PRIMARY KEY AUTO_INCREMENT, -- Auto increment the book ID
    bookname VARCHAR(50) NOT NULL,
    bookauthor VARCHAR(50) NOT NULL,
    book
    stock INT DEFAULT 0 -- Number of available books in stock
);

CREATE TABLE IF NOT EXISTS BookHub.BookStash (
    username VARCHAR(30),
    bookid INT,
    fromdate DATE NOT NULL, -- Starting date of the book borrowing
    todate DATE NOT NULL,   -- Ending date of the book borrowing
    PRIMARY KEY (username, bookid, fromdate), -- Composite primary key to ensure uniqueness
    FOREIGN KEY (username) REFERENCES BookStars(username) ON DELETE CASCADE, -- Foreign key from BookStars
    FOREIGN KEY (bookid) REFERENCES BookShelf(bookid) ON DELETE CASCADE -- Foreign key from BookShelf
);

                   """)


def dbConnect(dbIP,user,passwd):
    try:
        myconn = mc.connect(host=dbIP,user=user,passwd=passwd,database="BookHub")
        return myconn.cursor()
    except Exception as E:
        print("cannot connect to Database",E)
        if input("Recreate database?[y/n]: ").lower() == "y":
            db_init()
        

def loginStaff(username,password):
    global mycurs
    res = mycurs.execute(f"select * from BookStars where username='{username}' and password='{password}' and staff=1")
    if len(res) == 0:
        return False
    else:
        # set logged in status 1
        return True

def logoutStaff(username):
    global mycurs
    res = mycurs.execute(f"update BookStars set Logged_in=0 where username='{username}'")
    return True

def createBorrower(username):
    global mycurs
    res = mycurs.execute(f"insert into BookStars value ('{username}',null,0,0,0)")
    return True

def listBorrowers(username=None):
    global mycurs
    res = mycurs.execute(f"select * from BookStars where staff=0 {f"and username like '%{username}%'" if username else ""}")
    return res

def updateBorrowers(username,borrowed_count):
    global mycurs
    res = mycurs.execute(f"update BookStars set borrowed_count={borrowed_count} where username='{username}' and staff=0")
    return True

def deleteBorrowers(username):
    global mycurs
    res = mycurs.execute(f"delete from BookStars where username='{username}' and staff=0")
    return True

def creatStaff(username):
    global mycurs
    res = mycurs.execute(f"insert into BookStars value ('{username}',null,1,0,0)")
    return True

def listStaff(username=None):
    global mycurs
    res = mycurs.execute(f"select * from BookStars where staff=1 {f"and username like '%{username}%'" if username else ""}")
    return res

def updateStaff(username,password=None,borrowed_count=None):
    global mycurs
    if borrowed_count:
        res = mycurs.execute(f"update BookStars set borrowed_count={borrowed_count} where username='{username}' and staff=1")
    if password:
        res = mycurs.execute(f"update BookStars set password={password} where username='{username}' and staff=1")
    return True

def deleteStaff(username):
    global mycurs
    res = mycurs.execute(f"delete from BookStars where username='{username}' and staff=1")
    return True

def createBook(bookid,bookName,bookAuthor,stock):
    global mycurs
    res = mycurs.execute(f"insert into BookShelf value ('{bookName}','{bookAuthor}',{stock})")
    return True

def updateBook(bookid,bookName=None,bookAuthor=None,stock=None):
    global mycurs
    res = mycurs.execute(f"update BookShelf set {f"bookname='{bookName}'" if bookName else ""} {"and" if bookName and bookAuthor else ""} {f"bookauthor='{bookAuthor}'" if bookAuthor else ""} {"and" if bookAuthor and stock else ""} {f"stock={stock}" if stock!=None else ""} where bookid={bookid})")
    return True

def listBooks(bookName=None,bookAuthor=None):
    global mycurs
    res = mycurs.execute(f"select * from BookShelf where {f'bookname like "%{bookName}%"' if bookName else ""} {"and" if bookAuthor and bookName else ""} {f'bookauthor like "%{bookAuthor}%"' if bookAuthor else ""}")
    return res

def deleteBook(bookid):
    global mycurs
    res = mycurs.execute(f"delete from BookShelf where bookid={bookid})")
    return True


eel.init("gui")

eel.start("index.html")