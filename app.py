from flask import Flask, render_template, request, jsonify
import MySQLdb
import Cookie
import os
import cgi, cgitb
import serial
import random
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta


db= MySQLdb.connect("127.0.0.1","root","root","library")
cursor = db.cursor()

app = Flask(__name__)


#serial


#Cookie
c = Cookie.SimpleCookie()

@app.route('/')
def main():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('register.html')

#Administrator Templates
@app.route('/administrator')
def administrator():
    return render_template('adminHome.html')

@app.route('/addBook')
def addbook_template():
    
    return render_template('addBook.html')

@app.route('/alertsAdmin')
def alertsadmin():
    sql = "select books.id,books.number,books.name,books.author,books.publisher,books.rack,books.row,books.position,bookissue.uid,bookissue.returndate from books inner join bookissue on books.id=bookissue.bookid "
    try:
        cursor.execute(sql)
        #fetch all books
        books = cursor.fetchall()                
    except:
         db.rollback()
    return render_template('alertsAdmin.html',books=books)


#Student Templates
@app.route('/students')
def studenthome():
    return render_template('studentHome.html',name=c['name'].value,idcard=c['id'].value)

@app.route('/searchBook')
def searchbook():
    sql = "SELECT * FROM books where status =1"              
    try:
        cursor.execute(sql)
        #fetch all books
        books = cursor.fetchall()                
    except:
         db.rollback()
    return render_template('searchBooks.html',name=c['name'].value,idcard=c['id'].value, books = books)

@app.route('/issueBook',methods=['GET'])
def issuebook():
    id=request.args.get('id')
    sql = "SELECT * FROM books WHERE id='%s'" % \
           (id)
    try:
        cursor.execute(sql)
        #fetch all books
        books = cursor.fetchall()
        date_1 = datetime.now().strftime('%d/%m/%Y')
        date_2 = datetime.now()+relativedelta(days=10)
        end_date = date_2.strftime('%d/%m/%Y')
    except:
         db.rollback()
    return render_template('issueBook.html',name=c['name'].value,idcard=c['id'].value,books = books,date_1 = date_1, end_date = end_date)


@app.route('/addissuebook',methods=['GET','POST'])
def addissuebook():
    uId = request.form['uid']
    bookId = request.form['bookid']
    returnDate = request.form['returndate']
    sql = "INSERT INTO bookissue (uid,bookid,returndate) VALUES ('%s', '%s', '%s')" % \
          (uId,bookId,returnDate)
    try:
        cursor.execute(sql)
        db.commit()
        return bookstatus(bookId)
    except:
        db.rollback()
    return ('error')

def bookstatus(bid):
    sql = "UPDATE books SET status= '0' WHERE id='%d' " % \
       (int(bid))
    try:
        cursor.execute(sql)
        db.commit()        
    except:
        db.rollback()
    return returnbook()

@app.route('/returnBookss',methods=['GET'])
def returnbookss():
    id=request.args.get('id')
    sql = "SELECT * FROM books WHERE number='%s'" % \
           (id)
    try:
        cursor.execute(sql)
        #fetch all books
        books = cursor.fetchall()
        date_1 = datetime.now().strftime('%d/%m/%Y')
    except:
         db.rollback()
    return render_template('returnBook.html',name=c['name'].value,idcard=c['id'].value,books = books,date_1 = date_1)




@app.route('/returnBook')
def returnbook():
    uid = c['id'].value
    sql = "select books.id,books.number,books.name,books.author,books.publisher,books.rack,books.row,books.position,bookissue.uid,bookissue.returndate from books inner join bookissue on books.id=bookissue.bookid where bookissue.uid='%s'"  %\
          (uid)
    try:
        cursor.execute(sql)
        #fetch all books
        books = cursor.fetchall()                
    except:
         db.rollback()
    return render_template('returnBooks.html',books=books)

@app.route('/returnBooks',methods=['GET'])
def returnbooks():
    bid=request.args.get('id')
    sql = "UPDATE books SET status= '1' WHERE id='%d' " % \
       (int(bid))
    try:
        cursor.execute(sql)
        db.commit()        
    except:
        db.rollback()
    return deleteissues(bid)

def deleteissues(bid):
    sql = "DELETE FROM bookissue WHERE bookid='%d' " % \
       (int(bid))
    try:
        cursor.execute(sql)
        db.commit()        
    except:
        db.rollback()
    return returnbook()

@app.route('/login',methods=['POST','GET'])
def login():
   
    email = request.form['email']
    password = request.form['password']
    if (email == "admin@gmail.com" and password == "admin"):
        return administrator() 
    else: 
        sql = "SELECT * FROM registration WHERE email='%s' AND password='%s' AND status='%d'" % \
                  (email,password,1)
        try:
            cursor.execute(sql)
            #fetch all results
            results = cursor.fetchall()
            for row in results:
                name = row[1]
                idcard = row[4]
                c['id'] = idcard
                c['name'] = name
                return render_template('studentHome.html',name=c['name'].value,idcard=c['id'].value)
                                    
        except:
            db.rollback()

    return main()
            
    
    
@app.route('/alertStudent')
def alertstudent():
    uid=c['id'].value
    date_1 = datetime.now().strftime('%d/%m/%Y')
    sql = "select books.id,books.number,books.name,books.author,books.publisher,books.rack,books.row,books.position,bookissue.uid,bookissue.returndate from books inner join bookissue on books.id=bookissue.bookid where bookissue.uid='%s' AND bookissue.returndate='%s'"  % \
           (uid,date_1)
    try:
        cursor.execute(sql)
        #fetch all books
        books = cursor.fetchall()
        for book in books:
            booknumber = book[1]
            bookname = book[2]
            date_return = book[9]
            #return jsonify(number = booknumber,name=bookname,date=date_return)
    except:
         db.rollback() 
    return render_template('alertStudent.html',books=books)

@app.route('/alertStudents')
def alertstudents():
    uid=c['id'].value
    date_1 = datetime.now().strftime('%d/%m/%Y')
    sql = "select books.id,books.number,books.name,books.author,books.publisher,books.rack,books.row,books.position,bookissue.uid,bookissue.returndate from books inner join bookissue on books.id=bookissue.bookid where bookissue.uid='%s' AND bookissue.returndate='%s'"  % \
           (uid,date_1)
    try:
        cursor.execute(sql)
        #fetch all books
        books = cursor.fetchall()
        for book in books:
            booknumber = book[1]
            bookname = book[2]
            date_return = book[9]
            return jsonify(number = booknumber,name=bookname,date=date_return)
    except:
         db.rollback() 
    return render_template('alertStudent.html',books=books)

@app.route('/signup',methods=['POST','GET'])
def register():

    fullname = request.form['fullname']
    branch = request.form['department']
    idcard = request.form['idcard']
    email = request.form['email']
    password = request.form['password']
    address = request.form['address']
    sql = "INSERT INTO registration (fullname,email,password,idcard,branch,address,status) \
       VALUES ('%s', '%s', '%s','%s', '%s', '%s', '%d')" % \
       (fullname,  email, password, idcard, branch, address , 0)
    try:
        cursor.execute(sql)
        db.commit()
        return main()
    except:
        db.rollback()
    return main()

#Administrator
@app.route('/addBooks',methods=['POST','GET'])
def addbooks():
    cardid=request.args.get('cardid')
    return render_template('addBooks.html',cardid=cardid)

@app.route('/addBook',methods=['POST','GET'])
def addbook():
    bookNumber = request.form['bookNumber']
    bookName = request.form['bookName']
    bookAuthor = request.form['bookAuthor']
    bookPublisher = request.form['bookPublisher']
    bookCopies = int(request.form['bookCopies'])
    bookPrice = int(request.form['bookPrice'])
    bookRack = int(request.form['bookRack'])
    bookRow = int(request.form['bookRow'])
    bookPosition = int(request.form['bookPosition'])
    bookAbstract = request.form['abstract']
    sql = "INSERT INTO books (number,name,author,publisher,copies,price,rack,row,position,abstract) VALUES ('%s', '%s', '%s','%s', '%d', '%d', '%d', '%d', '%d', '%s')" % \
       (bookNumber, bookName, bookAuthor, bookPublisher, bookCopies, bookPrice, bookRack, bookRow, bookPosition, bookAbstract)
    try:
        cursor.execute(sql)
        db.commit()
        return viewbooks()
    except:
        db.rollback()
    return error()


@app.route('/readNFC')
def nfcreader(): 
    ser = serial.Serial ("/dev/ttyAMA0")    #Open named port 
    ser.baudrate = 9600                     #Set baud rate to 9600
    data = ser.readline()                     #Read ten characters from serial port to data
    ser.close()
    return jsonify(data=data)
   



@app.route('/viewBooks')
def viewbooks():
    sql = "SELECT * FROM books "              
    try:
        cursor.execute(sql)
        #fetch all books
        books = cursor.fetchall()                
    except:
         db.rollback()        
    return render_template('viewBooks.html',books =books )

@app.route('/removeBook',methods=['GET'])
def removebook():
    id=request.args.get('id')    
    sql = "DELETE FROM books WHERE id='%d' " % \
       (int(id))              
    try:
        cursor.execute(sql)
        db.commit()                
    except:
         db.rollback()        
    return viewbooks()


@app.route('/viewStudentRequest')
def viewstudentrequest():
    sql = "SELECT * FROM registration WHERE status='%d'" % \
              (0)
    try:
        cursor.execute(sql)
        #fetch all requests
        requests = cursor.fetchall()                
    except:
         db.rollback()       
    return render_template('viewStudentRequest.html',requests =requests )

@app.route('/approveStudent',methods=['GET'])
def approvestudent():
    id=request.args.get('id')    
    sql = "UPDATE registration SET status= '%d' WHERE id='%d' " % \
       (1,int(id))
    try:
        cursor.execute(sql)
        db.commit()  
    except:
        db.rollback()     
    return viewstudentrequest()


@app.route('/viewAllStudents')
def viewallstudents():
    sql = "SELECT * FROM registration WHERE status='%d'"  % \
          (1)
    try:
        cursor.execute(sql)
        #fetch all students
        students = cursor.fetchall()
    except:
        db.rollback()        
    return render_template('viewStudents.html', students = students)

@app.route('/removeStudent',methods=['GET'])
def removestudent():
    id=request.args.get('id')    
    sql = "DELETE  FROM registration WHERE id='%d' " % \
       (int(id))
    try:
        cursor.execute(sql)
        db.commit()        
    except:
        db.rollback()
    return viewallstudents()


@app.route('/404')
def error():
    return render_template('404.html')

@app.route('/issuebooktag')
def isssuebooktag():
    booktag = request.args.get('id')
    sql = "SELECT * FROM books WHERE number='%s'" % \
           (booktag)
    try:
        cursor.execute(sql)
        #fetch all books
        books = cursor.fetchall()
        date_1 = datetime.now().strftime('%d/%m/%Y')
        date_2 = datetime.now()+relativedelta(days=10)
        end_date = date_2.strftime('%d/%m/%Y')
    except:
         db.rollback()
    return render_template('issueBook.html',name=c['name'].value,idcard=c['id'].value,books = books,date_1 = date_1, end_date = end_date)

@app.route('/returnDate')
def returndate():
    uid=c['id'].value
    date_1 = datetime.now().strftime('%d/%m/%Y')
    sql = "select books.id,books.number,books.name,books.author,books.publisher,books.rack,books.row,books.position,bookissue.uid,bookissue.returndate from books inner join bookissue on books.id=bookissue.bookid where bookissue.uid='%s' AND bookissue.returndate='%s'"  % \
           (uid,date_1)
    try:
        cursor.execute(sql)
        #fetch all books
        books = cursor.fetchall()
        for book in books:
            booknumber = book[1]
            bookname = book[2]
            date_return = book[9]
            return jsonify(number = booknumber,name=bookname,date=date_return)
    except:
         db.rollback() 
    return ('query not executed')

if __name__ == '__main__':
    app.run(debug=True,host='192.168.0.16')
