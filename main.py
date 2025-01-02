import eel

import mysql.connector as mc




def db_connect():
    myconn = mc.connect(host="localhost",user="root",passwd="root")
    return myconn.cursor()




eel.init("gui")

eel.start("index.html")