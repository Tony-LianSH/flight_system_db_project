# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 12:32:30 2020

@author: Tony Lian
"""

from flask import Flask, render_template, request, redirect, url_for,session, flash
import pymysql
import mysql.connector
import hashlib

# initializing the server
app = Flask(__name__)
app.secret_key = "YOUR SECRET KEY"

#Configure MySQL
dbsql = mysql.connector.connect(host='localhost',
                       user='root',
                       password='',
                       database='airair')
print('mysql connection ok')

# define a home page
@app.route('/', methods = ['GET','POST'])
def home():
    #email = session.get('isLogin')
    '''if email != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM customer WHERE email = \'{}\' "
        cursor.execute(query.format(email))
        data = cursor.fetchone()
        cursor.close()
        return render_template('home.html', greet = "Hello!", username = data[1])
    else:'''
    return render_template("home.html", greet = "Hello!")

@app.route('/login')
def login(): 
    errorMessage = session.get('error')
    if errorMessage != None:
        session.pop('error')
        return render_template('login.html', errorMessage = errorMessage )
    return render_template('login.html')

@app.route('/custhome')
def custhome():
    return render_template('custhome.html')

@app.route('/loginpage', methods = ['GET','POST'])
def loginpage():
    email = request.form['email']
    password = request.form['password']
    usertype = request.form['usertype']
    pw = hashlib.md5(password.encode()).hexdigest()
    #login for customer
    if usertype == "customer":
        #cursor used to send queries
        cursor = dbsql.cursor()
        #executes query
        query = "SELECT * FROM customer WHERE email = \'{}\' and password = \'{}\'"
        cursor.execute(query.format(email, pw))
        #stores the results in a variable
        data = cursor.fetchone()
        #use fetchall() if you are expecting more than 1 data row
        cursor.close()
        if(data):
            #creates a session for the the user
            #session is a built in
            session['isLogin'] = email
            return redirect(url_for('custhome'))
        else:
            #returns an error message to the html page
            session['error'] = 'Invalid login or username'
            return redirect(url_for('login'))
    #login for booking agent
    if usertype == "booking_agent":
        #cursor used to send queries
        cursor = dbsql.cursor()
        #executes query
        query = "SELECT * FROM booking_agent WHERE email = \'{}\' and password = \'{}\'"
        cursor.execute(query.format(email, password))
        #stores the results in a variable
        data = cursor.fetchone()
        #use fetchall() if you are expecting more than 1 data row
        cursor.close()
        if(data):
            #creates a session for the the user
            #session is a built in
            session['isLogin'] = email
            return redirect(url_for('bahome'))
        else:
            #returns an error message to the html page
            session['error'] = 'Invalid login or username'
            return redirect(url_for('login'))
    #login for airline staff
    if usertype == "airline_staff":
        #cursor used to send queries
        cursor = dbsql.cursor()
        #executes query
        query = "SELECT * FROM airline_staff WHERE username = \'{}\' and password = \'{}\'"
        cursor.execute(query.format(email, password))
        #stores the results in a variable
        data = cursor.fetchone()
        #use fetchall() if you are expecting more than 1 data row
        cursor.close()
        if(data):
            #creates a session for the the user
            #session is a built in
            session['isLogin'] = email
            return redirect(url_for('ashome'))
        else:
            #returns an error message to the html page
            session['error'] = 'Invalid login or username'
            return redirect(url_for('login'))
    
@app.route('/custhome')
def custhome():
    email = session.get('isLogin')

@app.route('/logout')
def logout():
    session.pop('isLogin')
    flash('You were successfully logged out')
    return redirect('/')

@app.route('/searchFlight')
def searchFlight(): 
    result = session.get('searchResult')
    if result == 0:
        cursor = dbsql.cursor()
        query = "SELECT * FROM airport"
        cursor.execute(query)
        airportList = cursor.fetchall()
        cursor.close()
        return render_template('searchFlight.html', airportList = airportList)
    
@app.route('/searchFlightFunc', methods = ['GET','POST'])
def searchFlightFunc(): 
    dep = request.form['depart']
    arr = request.form['arrival']
    cursor = dbsql.cursor()
    query = "SELECT * FROM flight WHERE departure_airport = \'{}\' and arrival_airport = \'{}\'"
    cursor.execute(query.format(dep, arr))
    data = cursor.fetchall()
    cursor.close()
    if(data):
        #creates a session for the the user
        #session is a built in
        session['searchResult'] = data
        return redirect(url_for('searchFlight'))
    else:
        #returns an error message to the html page
        session['searchResult'] = 0
        return redirect(url_for('searchFlight'))

#registration
@app.route("/register", methods=["POST", "GET"])
def register():
    try:
        user_type = request.form["user_type"]
    except:
        return "Bad form"

    if user_type == "Customer": 

        # get info from form
        try:
            email = request.form["email"]
            username = request.form["username"]
            password = request.form["password"]
            building_number = request.form["building_number"]
            street = request.form["street"]
            city = request.form["city"]
            state = request.form["state"]
            phone_number = int(request.form["phone_number"])
            passport_number = request.form["passport_number"]
            passport_expiration = request.form["passport_expiration"]
            passport_country = request.form["passport_country"]
            date_of_birth = request.form["date_of_birth"]
        except:
            return "Bad form"

        if check_empty(email,username,building_number,street,city,state,passport_number,passport_country,passport_expiration,date_of_birth):
            return "Bad Form"
        m = hashlib.md5()
        m.update(password.encode(encoding="UTF-8"))
        hashed_pwd = m.hexdigest()

        cursor = dbsql.cursor()
        # check email duplicate
        cursor.execute("SELECT * FROM customer")
        data = cursor.fetchall()
        for e in data:
            if email == e["email"]:
                return render_template("customerRegisterPage.html", error="email_duplicate")
                # insert user data into db
        query = "INSERT INTO customer VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(query, (email, username, hashed_pwd, building_number, street, city,
                               state, phone_number, passport_number, passport_expiration,
                               passport_country, date_of_birth))
        conn.commit()
        cursor.close()
        return redirect(url_for("customerLoginPage"))

    elif user_type == "Booking Agent":
        try:
            email = request.form["email"]
            password = request.form["password"]
            ba_id = int(request.form["booking_agent_id"])
        except:
            return "Bad form"

        if check_empty(email,password,ba_id):
            return "Bad Form"

        m = hashlib.md5()
        m.update(password.encode(encoding="UTF-8"))
        hashed_pwd = m.hexdigest()

        cursor = conn.cursor()
        # check email duplicate
        cursor.execute("SELECT * FROM booking_agent")
        data = cursor.fetchall()
        for e in data:
            if email == e["email"]:
                return render_template("baRegisterPage.html", error="email_duplicate")
            if ba_id == int(e["booking_agent_id"]):
                return render_template("baRegisterPage.html", error="ID_duplicate")

        query = "INSERT INTO booking_agent VALUES(%s,%s,%s)"
        cursor.execute(query, (email, hashed_pwd, ba_id))
        conn.commit()
        cursor.close()
        return render_template("baLoginPage.html")

    elif user_type == "Airline Staff":
        try:
            username = request.form["username"]
            password = request.form["password"]
            first_name = request.form["first_name"]
            last_name = request.form["last_name"]
            date_of_birth = request.form["date_of_birth"]
            airline_name = request.form["airline_name"]
        except:
            return "Bad form"

        if check_empty(username,password,first_name,last_name,date_of_birth,airline_name):
            return "Bad Form"

        m = hashlib.md5()
        m.update(password.encode(encoding="UTF-8"))
        hashed_pwd = m.hexdigest()

        cursor = conn.cursor()
        # check username duplicate
        cursor.execute("SELECT * FROM airline_staff")
        data = cursor.fetchall()

        #get airline options
        cursor.execute("SELECT * FROM airline")
        data2 = cursor.fetchall()
        airlines = [e["airline_name"] for e in data2]
        for e in data:
            if username == e["username"]:
                return render_template("staffRegisterPage.html", error="username_duplicate", airlines=airlines)

        query = "INSERT INTO airline_staff VALUES(%s,%s,%s,%s,%s,%s)"
        cursor.execute(query, (username, hashed_pwd, first_name, last_name,
                               date_of_birth, airline_name))
        conn.commit()
        cursor.close()
        return render_template("staffLoginPage.html")
    else:
        return "Bad form"

    

if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)