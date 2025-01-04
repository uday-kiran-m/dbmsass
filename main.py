import eel
from datetime import date, timedelta
import base64
import json
import mysql.connector as mc


def db_init(dbIP,user,passwd):
    ## Schema
    ## BookStars(username varchar(30),password varchar(30),staff TinyInt(1),borrowed_count INT,Logged_in TinyInt(1))
    ## BookShelf(bookid INT,bookname varchar(50),bookauthor varchar(50),stock INT)
    ## BookStash(username foreign key bookstars , bookid foreign key bookshelf, fromdate, todate)
    ##
    myconn = mc.connect(host=dbIP,user=user,passwd=passwd)
    mycurs = myconn.cursor(buffered=True)
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
    stock INT DEFAULT 0, -- Number of available books in stock
    bookPic MEDIUMBLOB
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
    mycurs.close()
    if input("Recreate Load Demo data?[y/n]: ").lower() == "y":
        insert_demo_data(myconn)
    
def insert_demo_data(myconn):
    def read_image(file_path):
        with open(file_path, "rb") as file:
            return base64.b64encode(file.read()).decode("utf-8")
    myconn.reconnect()
    cursor = myconn.cursor(buffered=True)
    cursor.execute("use BookHub")

    # Insert demo data into BookStars
    bookstars_data = [
        ("user1", "password1", 0, 5, 0),
        ("user2", "password2", 0, 2, 0),
        ("staff1", "staffpass1", 1, 0, 1),
        ("user3", "password3", 0, 0, 0),
        ("user4", "password4", 0, 1, 0),
        ("staff2", "staffpass2", 1, 0, 1),
        ("user5", "password5", 0, 3, 0),
    ]
    cursor.executemany("""
        INSERT INTO BookStars (username, password, staff, borrowed_count, Logged_in)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE username=username;
    """, bookstars_data)

    # Insert demo data into BookShelf with image blobs
    bookshelf_data = [
        ("The Great Gatsby", "F. Scott Fitzgerald", 3, read_image("demoimg/gatsby.jpg")),
        ("1984", "George Orwell", 5, read_image("demoimg/1984.jpg")),
        ("To Kill a Mockingbird", "Harper Lee", 2, read_image("demoimg/mockingbird.jpg")),
        ("Pride and Prejudice", "Jane Austen", 4, read_image("demoimg/pride.jpg")),
        ("Moby Dick", "Herman Melville", 1, read_image("demoimg/moby.jpg")),
        ("War and Peace", "Leo Tolstoy", 3, read_image("demoimg/war.jpg")),
        ("The Odyssey", "Homer", 2, read_image("demoimg/odyssey.jpg")),
    ]
    cursor.executemany("""
        INSERT INTO BookShelf (bookname, bookauthor, stock, bookPic)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE bookname=bookname;
    """, bookshelf_data)

    # Insert demo data into BookStash
    today = date.today()
    bookstash_data = [
        ("user1", 1, today - timedelta(days=10), today),
        ("user2", 2, today - timedelta(days=5), today + timedelta(days=5)),
        ("user3", 3, today - timedelta(days=7), today - timedelta(days=1)),
        ("user4", 4, today - timedelta(days=15), today - timedelta(days=5)),
        ("user1", 5, today - timedelta(days=12), today - timedelta(days=2)),
        ("user5", 6, today - timedelta(days=20), today - timedelta(days=10)),
        ("user3", 7, today - timedelta(days=25), today - timedelta(days=15)),
    ]
    cursor.executemany("""
        INSERT INTO BookStash (username, bookid, fromdate, todate)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE username=username, bookid=bookid, fromdate=fromdate;
    """, bookstash_data)

    # Commit changes
    myconn.commit()

    # Close connection
    cursor.close()
    myconn.close()
    quit()

def dbConnect(dbIP,user,passwd):
    try:
        myconn = mc.connect(host=dbIP,user=user,passwd=passwd,database="BookHub")
        return myconn
    except mc.Error as E:
        # print("cannot connect to Database",E)
        if E.errno == 2003:
            print("Error: cannot reach server, check address and try again.")
        elif E.errno == 1049:
            print("Error: The database does not exist")
            if input("Recreate database?[y/n]: ").lower() == "y":
                db_init(dbIP,user,passwd)
        else:
            print("error:",E)
        
@eel.expose
def loginStaff(username,password):
    global myconn
    mycurs = myconn.cursor(buffered=True)
    res = mycurs.execute(f"select * from BookStars where username='{username}' and password='{password}' and staff=1")
    if len(res) == 0:
        return False
    else:
        # set logged in status 1
        return True
    
@eel.expose
def logoutStaff(username):
    global myconn
    mycurs = myconn.cursor(buffered=True)
    res = mycurs.execute(f"update BookStars set Logged_in=0 where username='{username}'")
    return True

@eel.expose
def createBorrower(username):
    global myconn
    mycurs = myconn.cursor(buffered=True)
    res = mycurs.execute(f"insert into BookStars value ('{username}',null,0,0,0)")
    return True

@eel.expose
def listBorrowers(username=None):
    global myconn
    mycurs = myconn.cursor(buffered=True)
    res = mycurs.execute(f"select * from BookStars where staff=0 {f"and username like '%{username}%'" if username else ""}")
    return res

def updateBorrowers(username,borrowed_count):
    global myconn
    mycurs = myconn.cursor(buffered=True)
    res = mycurs.execute(f"update BookStars set borrowed_count={borrowed_count} where username='{username}' and staff=0")
    return True

def deleteBorrowers(username):
    global myconn
    mycurs = myconn.cursor(buffered=True)
    res = mycurs.execute(f"delete from BookStars where username='{username}' and staff=0")
    return True

def creatStaff(username):
    global myconn
    mycurs = myconn.cursor(buffered=True)
    res = mycurs.execute(f"insert into BookStars value ('{username}',null,1,0,0)")
    return True

def listStaff(username=None):
    global myconn
    mycurs = myconn.cursor(buffered=True)
    res = mycurs.execute(f"select * from BookStars where staff=1 {f"and username like '%{username}%'" if username else ""}")
    return res

def updateStaff(username,password=None,borrowed_count=None):
    global myconn
    mycurs = myconn.cursor(buffered=True)
    if borrowed_count:
        res = mycurs.execute(f"update BookStars set borrowed_count={borrowed_count} where username='{username}' and staff=1")
    if password:
        res = mycurs.execute(f"update BookStars set password={password} where username='{username}' and staff=1")
    return True

def deleteStaff(username):
    global myconn
    mycurs = myconn.cursor(buffered=True)
    res = mycurs.execute(f"delete from BookStars where username='{username}' and staff=1")
    return True

def createBook(bookName,bookAuthor,stock):
    global myconn
    mycurs = myconn.cursor(buffered=True)
    res = mycurs.execute(f"insert into BookShelf value ('{bookName}','{bookAuthor}',{stock})")
    return True

def updateBook(bookid,bookName=None,bookAuthor=None,stock=None):
    global myconn
    mycurs = myconn.cursor(buffered=True)
    res = mycurs.execute(f"update BookShelf set {f"bookname='{bookName}'" if bookName else ""} {"and" if bookName and bookAuthor else ""} {f"bookauthor='{bookAuthor}'" if bookAuthor else ""} {"and" if bookAuthor and stock else ""} {f"stock={stock}" if stock!=None else ""} where bookid={bookid})")
    return True

@eel.expose
def listBooks(bookName=None,bookAuthor=None):
    global myconn
    mycurs = myconn.cursor(buffered=True)
    mycurs.execute(f'select bookid,bookname,bookauthor,stock,CONVERT(bookPic USING utf8) from BookShelf {"where" if bookAuthor or bookName else ""} {f'bookname like "%{bookName}%"' if bookName else ""} {"and" if bookAuthor and bookName else ""} {f'bookauthor like "%{bookAuthor}%"' if bookAuthor else ""}')
    res = mycurs.fetchall()
    return res

def deleteBook(bookid):
    global myconn
    mycurs = myconn.cursor(buffered=True)
    res = mycurs.execute(f"delete from BookShelf where bookid={bookid})")
    return True


eel.init("gui")

myconn = dbConnect("localhost","root","root")


eel.start("index.html")
