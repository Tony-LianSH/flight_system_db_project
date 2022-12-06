from flask import Flask, render_template, request, redirect, url_for,session, flash
import pymysql
import mysql.connector
import hashlib
import datetime
import time

# initializing the server
app = Flask(__name__)
app.secret_key = "YOUR SECRET KEY"

#Configure MySQL
dbsql = mysql.connector.connect(host='localhost',
                        port = '8889',
                       user='root',
                       password='root',
                       database='final')
print('mysql connection ok')

#如果机场名字有空格，就这样处理
def convertair(airportname):
    cursor = dbsql.cursor()
    query = "SELECT airport_name FROM airport"
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    airportlist = {}
    for i in data:
        i = i[0]
        if ' ' in i:
            b = i.split()
            airportlist[b[0]] = i
        else:
            airportlist[i]=i
    print(airportlist)
    return airportlist[airportname]

def get_timestamp_from_formattime(format_time):
    struct_time = time.strptime(format_time, '%Y-%m-%d %H:%M:%S')
    return time.mktime(struct_time)

# define a home page
@app.route('/', methods = ['GET','POST'])
def home():
    if (session.get('isLogin') != None):
        session.pop('isLogin')
    if (session.get('airline_staff') != None):
        session.pop('airline_staff')
    return render_template("home.html", greet = "Hello!")

'''=====================LOGIN PART========================'''

#login page for three users
@app.route('/login')
def login(): 
    errorMessage = session.get('error')
    if errorMessage != None:
        session.pop('error')
        return render_template('login.html', errorMessage = errorMessage )
    else:
        return render_template('login.html')

#验证部分
@app.route('/loginpage', methods = ['GET','POST'])
def loginpage():
    email = request.form['email']
    password = request.form['password']
    usertype = request.form['usertype']
    pw = hashlib.md5(password.encode('utf-8')).hexdigest()
    print(pw)
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
    #login for airline staff
    if usertype == "airline_staff":
        cursor = dbsql.cursor()
        query = "SELECT * FROM airline_staff WHERE username = \'{}\' and password = \'{}\'"
        cursor.execute(query.format(email, pw))
        data = cursor.fetchone()
        cursor.close()
        if(data):
            session['isLogin'] = email
            session['airline_staff'] = email
            return redirect(url_for('ashome'))
        else:
            session['error'] = 'Invalid login or username'
            return redirect(url_for('login'))
    #login for booking agent
    if usertype == "booking_agent":
        cursor = dbsql.cursor()
        query = "SELECT * FROM booking_agent WHERE email = \'{}\' and password = \'{}\'"
        cursor.execute(query.format(email, pw))
        data = cursor.fetchone()
        cursor.close()
        if(data):
            session['isLogin'] = email
            return redirect(url_for('bahome'))
        else:
            session['error'] = 'Invalid login or username'
            return redirect(url_for('login'))
    
#logout
@app.route('/logout')
def logout():
    if (session.get('isLogin') != None):
        session.pop('isLogin')
    if (session.get('airline_staff') != None):
        session.pop('airline_staff')
    flash('You were successfully logged out')
    return redirect('/login')


'''=====================REG PART========================'''

#registration for all
@app.route('/register')
def register():
    return render_template('reg模板.html')

#customer registration
@app.route('/reg-cust')
def reg_cust():
    return render_template('reg-cust.html')

@app.route("/registerAuthCu", methods=["POST", "GET"])
def registerAuthCu():
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

    #if check_empty(email,username,building_number,street,city,state,passport_number,passport_country,passport_expiration,date_of_birth):
    #    return "Bad Form"

    pw_afterhash = hashlib.md5(password.encode('utf-8')).hexdigest()
    if date_of_birth > datetime.datetime.now().strftime('%Y-%m-%d'):
        return render_template('reg模板.html',errorMessage = 'wrong date')

    cursor = dbsql.cursor()
    # check email duplicate
    cursor.execute("SELECT * FROM customer")
    data = cursor.fetchall()
    for e in data:
        if email == e[0]:
            #return render_template("customerRegisterPage.html", error="email_duplicate")
            return redirect(url_for('reg_cust'))
            # insert user data into db
    query = "INSERT INTO customer VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    cursor.execute(query, (email, username, pw_afterhash, building_number,street, city,
                            state, phone_number, passport_number, passport_expiration,
                            passport_country, date_of_birth))
    dbsql.commit()
    cursor.close()
    return redirect(url_for("login"))

#airline staff registration
@app.route('/reg-as')
def reg_as():
    cursor = dbsql.cursor()
    query = "SELECT airline_name FROM airline "
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    alist = []
    for i in data:
        alist.append(i[0])
    return render_template('reg-as.html', airlines = alist)

@app.route("/registerAuthAs", methods=["POST", "GET"])
def registerAuthAs():
    # get info from form
    try:
        username = request.form["username"]
        password = request.form["password"]
        firstname = request.form["first_name"]
        lastname = request.form["last_name"]
        date_of_birth = request.form["date_of_birth"]
        airline_name = request.form['airline_name']
    except:
        return "Bad form"

    #if check_empty(email,username,building_number,street,city,state,passport_number,passport_country,passport_expiration,date_of_birth):
    #    return "Bad Form"

    pw_afterhash = hashlib.md5(password.encode('utf-8')).hexdigest()
    if date_of_birth > datetime.datetime.now().strftime('%Y-%m-%d'):
        return render_template('reg模板.html',errorMessage = 'wrong date')
    cursor = dbsql.cursor()
    # check email duplicate
    cursor.execute("SELECT * FROM airline_staff")
    data = cursor.fetchall()
    for e in data:
        if username == e[0]:
            #return render_template("customerRegisterPage.html", error="email_duplicate")
            return redirect(url_for('reg_as'))
            # insert user data into db
    query = "INSERT INTO airline_staff VALUES(%s,%s,%s,%s,%s,%s)"
    cursor.execute(query, (username, pw_afterhash,firstname, lastname, date_of_birth, airline_name))
    dbsql.commit()
    cursor.close()
    return redirect(url_for("login"))

#booking agent registration
@app.route('/reg-ba')
def reg_ba():
    return render_template('reg-ba.html')

@app.route("/registerAuthBa", methods=["POST", "GET"])
def registerAuthBa():
    # get info from form
    try:
        email = request.form["email"]
        password = request.form["password"]
        booking_id = request.form['booking_id']
    except:
        return "Bad form"

    #if check_empty(email,username,building_number,street,city,state,passport_number,passport_country,passport_expiration,date_of_birth):
    #    return "Bad Form"

    pw_afterhash = hashlib.md5(password.encode('utf-8')).hexdigest()

    cursor = dbsql.cursor()
    # check email duplicate
    cursor.execute("SELECT * FROM booking_agent")
    data = cursor.fetchall()
    for e in data:
        if email == e[0]:
            #return render_template("customerRegisterPage.html", error="email_duplicate")
            return redirect(url_for('reg_ba'))
            # insert user data into db
    query = "INSERT INTO booking_agent VALUES(%s,%s,%s)"
    cursor.execute(query, (email, pw_afterhash,booking_id))
    dbsql.commit()
    cursor.close()
    return redirect(url_for("login"))

'''=====================CUS PART========================'''

#customer function
#customer home page 
@app.route('/custhome')
def custhome():
    email = session.get('isLogin')
    if email != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM customer WHERE email = \'{}\' "
        cursor.execute(query.format(email))
        custinfo = cursor.fetchone()
        cursor.close()
        #return render_template('custhome.html', email = custinfo[1])
    else:
        return redirect(url_for(home))

    #show the customer's upcoming flight
    #date = datetime.datetime.now().strftime('%Y-%m-%d')
    cursor = dbsql.cursor()
    query = "SELECT * FROM ticket NATURAL JOIN purchases NATURAL JOIN flight where customer_email =\'{}\'  and status = 'Upcoming' "
    cursor.execute(query.format(custinfo[0]))
    custflight = cursor.fetchall()
    cursor.close()
    comingflight = []
    for i in custflight:
        comingflight.append(i)
    return render_template('custhome.html', email = custinfo[1], comingflight = comingflight)

#customer all flight
@app.route('/custallflight')
def custallflight():
    email = session.get('isLogin')
    if email != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM customer WHERE email = \'{}\' "
        cursor.execute(query.format(email))
        custinfo = cursor.fetchone()
        cursor.close()
        #return render_template('custhome.html', email = custinfo[1])
    else:
        return redirect(url_for(home))

    #show the customer's history flight
    #date = datetime.datetime.now().strftime('%Y-%m-%d')
    cursor = dbsql.cursor()
    query = "SELECT * FROM ticket NATURAL JOIN purchases NATURAL JOIN flight where customer_email =\'{}\'  "
    cursor.execute(query.format(custinfo[0]))
    custflight = cursor.fetchall()
    cursor.close()
    comingflight = []
    for i in custflight:
        comingflight.append(i)
    deptwhere = []
    for i in comingflight:
        if i[6] not in deptwhere:
            deptwhere.append(i[6])
    arrwhere = []
    for i in comingflight:
        if i[8] not in arrwhere:
            arrwhere.append(i[8])
    flightdate = []
    for i in comingflight:
        if i[7] not in flightdate:
            flightdate.append(i[7])
    return render_template('custflight.html', email = custinfo[1], comingflight = comingflight, deptwhere= deptwhere, arrwhere = arrwhere)

@app.route('/custhistorysearch', methods = ['GET','POST'])
def custhistorysearch():
    email = session.get('isLogin')
    if email != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM customer WHERE email = \'{}\' "
        cursor.execute(query.format(email))
        custinfo = cursor.fetchone()
        cursor.close()
        #return render_template('custhome.html', email = custinfo[1])
    else:
        return redirect(url_for(home))
    dep = request.form['depart']
    arr = request.form['arrival']
    dep = convertair(dep)
    arr = convertair(arr)

    date = request.form['date']
    cursor = dbsql.cursor()
    query = "SELECT * FROM ticket NATURAL JOIN purchases NATURAL JOIN flight where customer_email =%s and departure_time > %s and departure_airport = %s and arrival_airport = %s"
    print(email, date,dep,arr)
    cursor.execute(query, (email, date,dep,arr))
    data = cursor.fetchall()
    cursor.close()
    if(data):
        return render_template('cust_search_result.html', result = list(data))
        #return render_template("searchFlightResult.html", searchResult = list(data))
    else:
        #returns an error message to the html page
        #session['searchResult'] = ['Find no matched flight for you '+dep+arr+', please try with some other routes!']
        return render_template('cust_search_result.html', result = 'Find no matched flight from '+dep+' to '+arr+', please try with some other routes!')
        #return render_template("searchFlightResult.html", searchResult = 'Find no matched flight from '+dep+' to '+arr+', please try with some other routes!')

#customer search flight and buy homepage
@app.route('/custallflightbuy')
def custallflightbuy():
    email = session.get('isLogin')
    if email != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM customer WHERE email = \'{}\' "
        cursor.execute(query.format(email))
        custinfo = cursor.fetchone()
        cursor.close()
        #return render_template('custhome.html', email = custinfo[1])
    else:
        return redirect(url_for(home))
    
    cursor = dbsql.cursor()
    cursor.execute("SELECT * FROM flight where status = 'Upcoming'")
    allflight = cursor.fetchall()
    cursor.close()
    comingflight = []
    for i in allflight:
        comingflight.append(i)
    deptwhere = []
    for i in comingflight:
        if i[2] not in deptwhere:
            deptwhere.append(i[2])
    arrwhere = []
    for i in comingflight:
        if i[4] not in arrwhere:
            arrwhere.append(i[4])
    #flightdate = []
    #for i in comingflight:
        #flightdate.append(i[7])
    return render_template('custallflight.html', comingflight = comingflight, deptwhere= deptwhere, arrwhere = arrwhere)

@app.route('/custflightsearch', methods = ['GET','POST'])
def custflightsearch():
    email = session.get('isLogin')
    if email != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM customer WHERE email = \'{}\' "
        cursor.execute(query.format(email))
        custinfo = cursor.fetchone()
        cursor.close()
        #return render_template('custhome.html', email = custinfo[1])
    else:
        return redirect(url_for(home))
    dep = request.form['depart']
    arr = request.form['arrival']
    dep = convertair(dep)
    arr = convertair(arr)
    date = request.form['date']
    cursor = dbsql.cursor()
    query = "SELECT * FROM flight where departure_time > %s and departure_airport = %s and arrival_airport = %s"
    print(email, date,dep,arr)
    cursor.execute(query, ( date,dep,arr))
    data = cursor.fetchall()
    cursor.close()
    if(data):
        return render_template('cust_search_result2.html', result = list(data))
        #return render_template("searchFlightResult.html", searchResult = list(data))
    else:
        #returns an error message to the html page
        #session['searchResult'] = ['Find no matched flight for you '+dep+arr+', please try with some other routes!']
        return render_template('cust_search_result2.html', result = 'Find no matched flight from '+dep+' to '+arr+', please try with some other routes!')

#customer buy processing function
@app.route('/custbuyprocess', methods = ['GET', 'POST'])
def custbuyprocess():
    email = session.get('isLogin')
    if email != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM customer WHERE email = \'{}\' "
        cursor.execute(query.format(email))
        custinfo = cursor.fetchone()
        cursor.close()
        #return render_template('custhome.html', email = custinfo[1])
    else:
        return redirect(url_for(home))
    
    data = request.form["data"].replace("'", "").split(",")
    #print(data)
    airline_name = data[0][1:]
    flight_num = int(data[1][1:])
    
    '''airline_name = data[0]
    flight_num = data[1]'''
    
    print(airline_name,flight_num)
    cursor = dbsql.cursor()
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    #airline_name = %s AND flight_num = %d AND 

    query1 = "select ticket_id from ticket where airline_name = %s AND flight_num = %s AND ticket_id NOT IN (select ticket_id from purchases)"
    cursor.execute(query1, (airline_name, flight_num))
    #query1 = "SELECT ticket_id from ticket where ticket_id NOT IN (select ticket_id from purchases)"
    #cursor.execute(query1)
    ticketleft = cursor.fetchall()
    if (ticketleft == []) or (ticketleft == None):
        return render_template('custbuyfail.html', errorMessage = 'Sold out or you have already purchased it')
    cursor.close()
    
    cursor = dbsql.cursor()
    query2 = 'INSERT INTO purchases (ticket_id,customer_email,booking_agent_id,purchase_date) values (%s,%s,%s,%s)'
    cursor.execute(query2,(ticketleft[0][0],custinfo[0],None,date))
    dbsql.commit()
    cursor.close()
    return render_template('custbuysuccess.html')

#customer track history data
@app.route('/custtrack')
def custtrack():
    email = session.get('isLogin')
    if email != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM customer WHERE email = \'{}\' "
        cursor.execute(query.format(email))
        custinfo = cursor.fetchone()
        cursor.close()
        #return render_template('custhome.html', email = custinfo[1])
    else:
        return redirect(url_for(home))
    
    query = """SELECT price, ticket_id, purchase_date FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE customer_email = \'{}\' ORDER BY purchase_date ASC"""
    cursor = dbsql.cursor()
    cursor.execute(query.format(custinfo[0]))
    data = cursor.fetchall()
    cursor.close()
    if not data:
        return render_template('custhome.html', errorMessage = "spending is zero")
    
    months = []
    now = datetime.datetime.today().year*100 + datetime.datetime.today().month
    #print('now',now) 202012
    t = data[0][2].year*100 + data[0][2].month
    print('t',t) #202008
    months.append(t)
    while t < now:
        if t % 100 == 12:
            t += 88
        t += 1
        months.append(t)
    spendings = [0 for _ in range(len(months))]
    for row in data:
        price = row[0]
        month = row[2].year*100 + row[2].month
        m = months.index(month)
        spendings[m] += float(price)
    now = str(datetime.datetime.today().year) + "-" + str(datetime.datetime.today().month)
    past_year = datetime.datetime.today().year
    past_month = datetime.datetime.today().month - 5
    if past_month < 1:
        past_month += 12
        past_year -= 1
    past = str(past_year) + "-" + str(past_month)
    if len(now) < 7:
        now = now[:5] + "0" + now[-1]
    if len(past) < 7:
        past = past[:5] + "0" + past[-1]
    print(months, spendings, now, past)
    return render_template('custtrack.html',months = months, spendings = spendings, now = now, past =past)

'''=====================AS PART========================'''

#airline staff function
#airline staff home page 
@app.route('/ashome')
def ashome():
    username = session.get('airline_staff')
    if username != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM airline_staff WHERE username = \'{}\' "
        cursor.execute(query.format(username))
        data = cursor.fetchone()
        cursor.close()
        return render_template('ashome.html', username = username)
    else:
        return render_template('home.html', errorMessage = "Don't you cheat!!!")
    
@app.route('/asallflight')
def asallflight():
    username = session.get('airline_staff')
    if username != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM airline_staff WHERE username = \'{}\' "
        cursor.execute(query.format(username))
        asinfo = cursor.fetchone()
        cursor.close()
        #return render_template('custhome.html', email = custinfo[1])
    else:
        return render_template('home.html', errorMessage = "Don't you cheat!!!")

    #show the customer's history flight
    #date = datetime.datetime.now().strftime('%Y-%m-%d')
    cursor = dbsql.cursor()
    query = "SELECT * FROM flight where airline_name =\'{}\' AND status = 'Upcoming'  "
    cursor.execute(query.format(asinfo[5]))
    custflight = cursor.fetchall()
    cursor.close()
    comingflight = []
    for i in custflight:
        comingflight.append(list(i))
    return render_template('ashome.html', username = username, comingflight = comingflight)

@app.route('/asflightchange')
def asflightchange():
    username = session.get('airline_staff')
    if username != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM airline_staff WHERE username = \'{}\' "
        cursor.execute(query.format(username))
        asinfo = cursor.fetchone()
        cursor.close()
        #return render_template('custhome.html', email = custinfo[1])
    else:
        return render_template('home.html', errorMessage = "Don't you cheat!!!")
    
    airline_name = asinfo[5]
    cursor = dbsql.cursor()
    query = "SELECT * FROM flight where airline_name = \'{}\'"
    cursor.execute(query.format(airline_name))
    allflight = cursor.fetchall()
    cursor.close()
    comingflight = []
    for i in allflight:
        comingflight.append(i)
    '''deptwhere = []
    for i in comingflight:
        deptwhere.append(i[2])
    arrwhere = []
    for i in comingflight:
        arrwhere.append(i[4])'''
    #flightdate = []
    #for i in comingflight:
        #flightdate.append(i[7])
    return render_template('asflight.html', comingflight = comingflight)

@app.route('/asflightdochange', methods = ['GET','POST'])
def asflightdochange():
    username = session.get('airline_staff')
    if username != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM airline_staff WHERE username = \'{}\' "
        cursor.execute(query.format(username))
        asinfo = cursor.fetchone()
        cursor.close()
        #return render_template('custhome.html', email = custinfo[1])
    else:
        return render_template('home.html', errorMessage = "Don't you cheat!!!")
    
    airline_name = asinfo[5]
    flight_num = int(request.form['num'])
    status = request.form['status']
    cursor = dbsql.cursor()
    query = "SELECT * FROM flight where airline_name = \'{}\'"
    query = "UPDATE `flight` SET `status` = \'{}\' WHERE `flight`.`airline_name` = \'{}\' AND `flight`.`flight_num` = \'{}\'; "
    cursor.execute(query.format(status, airline_name, flight_num))
    dbsql.commit()
    cursor.close()
    '''deptwhere = []
    for i in comingflight:
        deptwhere.append(i[2])
    arrwhere = []
    for i in comingflight:
        arrwhere.append(i[4])'''
    #flightdate = []
    #for i in comingflight:
        #flightdate.append(i[7])
    return render_template('ashome.html', errorMessage = 'Change Done!')

@app.route('/asaddflight')
def asaddflight():
    username = session.get('airline_staff')
    if username != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM airline_staff WHERE username = \'{}\' "
        cursor.execute(query.format(username))
        asinfo = cursor.fetchone()
        cursor.close()
        #return render_template('custhome.html', email = custinfo[1])
    else:
        return render_template('home.html', errorMessage = "Don't you cheat!!!")
    
    cursor = dbsql.cursor()
    query = "SELECT airport_name FROM airport "
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    alist = []
    for i in data:
        alist.append(i[0])
        
    cursor = dbsql.cursor()
    query = "SELECT airplane_id FROM airplane WHERE airline_name = \'{}\' "
    cursor.execute(query.format(asinfo[5]))
    data = cursor.fetchall()
    cursor.close()
    blist = []
    for i in data:
        blist.append(i[0])
        
    return render_template('asaddflight.html', airports = alist, airplanes = blist)

@app.route("/addflight", methods=["POST", "GET"])
def addflight():
    # get info from form
    
    username = session.get('airline_staff')
    if username != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM airline_staff WHERE username = \'{}\' "
        cursor.execute(query.format(username))
        asinfo = cursor.fetchone()
        cursor.close()
        #return render_template('custhome.html', email = custinfo[1])
    else:
        return render_template('home.html', errorMessage = "Don't you cheat!!!")

    airline_name= asinfo[5]
    try:
        flight_num = request.form["flight_num"]
        departure_airport = request.form["departure_airport"]
        departure_time = request.form["departure_time"]
        arrival_airport = request.form["arrival_airport"]
        arrival_time = request.form["arrival_time"]
        price = request.form['price']
        status = request.form['status']
        airplane_id = request.form['airplane_id']
    except:
        return "Bad form"

    #if check_empty(email,username,building_number,street,city,state,passport_number,passport_country,passport_expiration,date_of_birth):
    #    return "Bad Form"
    if departure_time >= arrival_time or departure_airport == arrival_airport:
        return render_template('ashome.html', errorMessage = 'wrong time or airport')
    cursor = dbsql.cursor()
    query = "SELECT * FROM flight WHERE airline_name = \'{}\' AND flight_num = \'{}\' "
    cursor.execute(query.format(airline_name, flight_num))
    existed_flight_num = cursor.fetchone()
    cursor.close()
    if (existed_flight_num != None):
        return render_template('ashome.html', errorMessage = "Occupied flight number!")
    if (arrival_airport == departure_airport):
        return render_template('ashome.html', errorMessage = "A cyclic flight!")
    if (arrival_time < departure_time):
        return render_template('ashome.html', errorMessage = "Impossible arrival time!")
    '''cursor = dbsql.cursor()
    query = "SELECT * FROM airplane WHERE airline_name = \'{}\' AND airplane_id = \'{}\' "
    cursor.execute(query.format(airline_name, airplane_id))
    existed_airplane = cursor.fetchone()
    cursor.close()
    if (existed_airplane == None):
        return render_template('asaddflight.html', errorMessage = "Non-existed airplane!")'''

    cursor = dbsql.cursor()    
    query = "INSERT INTO flight VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    cursor.execute(query, (airline_name, flight_num, departure_airport, departure_time, arrival_airport, arrival_time, price, status, airplane_id))
    query = "SELECT ticket_id FROM ticket"
    cursor.execute(query)
    ids = list(cursor.fetchall())
    max_id = int(max(ids)[0])
    for i in range(10):
        max_id += 1
        query = "INSERT INTO ticket VALUES(%s,%s,%s)"
        cursor.execute(query, (max_id, airline_name, flight_num))
    dbsql.commit()
    cursor.close()
    return render_template('ashome.html', errorMessage = 'Flight successfully created!')

@app.route("/asaddport", methods=["POST", "GET"])
def asaddport():
    username = session.get('airline_staff')
    if username != None:
        '''cursor = dbsql.cursor()
        query = "SELECT * FROM airline_staff WHERE username = \'{}\' "
        cursor.execute(query.format(username))
        #asinfo = cursor.fetchone()
        cursor.close()'''
        cursor = dbsql.cursor()
        query = 'select airport_name from airport '
        cursor.execute(query)
        airportlist = cursor.fetchall()
        print(airportlist[0][0],type(airportlist[0]))
        cursor.close()
        return render_template('asaddport.html')
    else:

        return render_template('home.html', errorMessage = "Don't you cheat!!!")
    
@app.route("/addairport", methods=["POST", "GET"])
def addairport():
    # get info from form
    try:
        airport_name = request.form["airport_name"]
        airport_city = request.form["airport_city"]
    except:
        return "Bad form"

    #if check_empty(email,username,building_number,street,city,state,passport_number,passport_country,passport_expiration,date_of_birth):
    #    return "Bad Form"
    cursor = dbsql.cursor()
    query = 'select airport_name from airport '
    cursor.execute(query)
    airportlist = cursor.fetchall()
    cursor.close()
    airportlist2 = []
    for i in airportlist:
        for j in i:
            airportlist2.append(j)
    if airport_name in airportlist2:
        return render_template('ashome.html', errorMessage = 'Airport already exists')

    cursor = dbsql.cursor()
    query = "INSERT INTO airport VALUES(%s,%s)"
    cursor.execute(query, (airport_name, airport_city))
    dbsql.commit()
    cursor.close()
    return render_template('ashome.html', errorMessage = 'Airport successfully added!')

@app.route("/asaddplane", methods=["POST", "GET"])
def asaddplane():
    username = session.get('airline_staff')
    if username != None:
        '''cursor = dbsql.cursor()
        query = "SELECT * FROM airline_staff WHERE username = \'{}\' "
        cursor.execute(query.format(username))
        #asinfo = cursor.fetchone()
        cursor.close()'''
        return render_template('asaddplane.html')
    else:
        return render_template('home.html', errorMessage = "Don't you cheat!!!")
    
@app.route("/addairplane", methods=["POST", "GET"])
def addairplane():
    username = session.get('airline_staff')
    if username != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM airline_staff WHERE username = \'{}\' "
        cursor.execute(query.format(username))
        asinfo = cursor.fetchone()
        cursor.close()
    else:
        return render_template('home.html', errorMessage = "Don't you cheat!!!")
    
    airline_name = asinfo[5]
    # get info from form
    try:
        airplane_id = request.form["airplane_id"]
        seats = request.form["seats"]
    except:
        return "Bad form"

    #if check_empty(email,username,building_number,street,city,state,passport_number,passport_country,passport_expiration,date_of_birth):
    #    return "Bad Form"
    cursor = dbsql.cursor()
    query = 'select airplane_id from airplane '
    cursor.execute(query)
    airlinelist = cursor.fetchall()
    cursor.close()
    airlinelist2 = []
    for i in airlinelist:
        for j in i:
            airlinelist2.append(j)
    if airplane_id in airlinelist2:
        return render_template('ashome.html', errorMessage = 'Airplane already exists')
  
    cursor = dbsql.cursor()
    query = "INSERT INTO airplane VALUES(%s,%s,%s)"
    cursor.execute(query, (airline_name, airplane_id, seats))
    dbsql.commit()
    cursor.close()
    return render_template('ashome.html', errorMessage = 'Airplane successfully added!')

@app.route('/asba', methods = ['GET', 'POST'])
def asba(start = 0, end = 0):
    username = session.get('airline_staff')
    if username != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM airline_staff WHERE username = \'{}\' "
        cursor.execute(query.format(username))
        asinfo = cursor.fetchone()
        cursor.close()
    else:
        return render_template('home.html', errorMessage = "Don't you cheat!!!")
    
    query = """SELECT booking_agent_id, COUNT(booking_agent_id) FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE DATE_SUB(CURDATE(), INTERVAL 30 DAY) <= date(purchase_date) GROUP BY booking_agent_id ORDER BY COUNT(booking_agent_id) DESC"""
    cursor = dbsql.cursor()
    cursor.execute(query)
    counts = cursor.fetchall()
    if len(counts)>5:
        counts = counts[:5]
    counts_ba = [c[0] for c in counts if c[0] != None]
    counts_times = [c[1] for c in counts if c[0] != None]
    cursor.close()
    
    query = """SELECT booking_agent_id, SUM(price) FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE DATE_SUB(CURDATE(), INTERVAL 365 DAY) <= date(purchase_date) GROUP BY booking_agent_id ORDER BY SUM(price) DESC"""
    cursor = dbsql.cursor()
    cursor.execute(query)
    price = cursor.fetchall()
    if len(price)>5:
        price = price[:5]
    price_ba = [c[0] for c in price if c[0] != None]
    price_com = [float(c[1])/10 for c in price if c[0] != None]
    cursor.close()
    return render_template('asba.html', counts_cust = counts_ba, counts_times = counts_times, price_cust = price_ba, price_com = price_com)

@app.route('/ascust', methods = ['GET', 'POST'])
def ascust():
    username = session.get('airline_staff')
    if username != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM airline_staff WHERE username = \'{}\' "
        cursor.execute(query.format(username))
        asinfo = cursor.fetchone()
        cursor.close()
    else:
        return render_template('home.html', errorMessage = "Don't you cheat!!!")
    
    query = """SELECT name FROM purchases JOIN customer ON customer_email = email GROUP BY name ORDER BY COUNT(name) DESC"""
    cursor = dbsql.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    if not data:
        return render_template('ashome.html', errorMessage = "No customer in the database!")
    
    return render_template('ascust.html', cust = [d[0] for d in data])


@app.route('/ascusttrace', methods = ['GET', 'POST'])
def ascusttrace():
    username = session.get('airline_staff')
    if username != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM airline_staff WHERE username = \'{}\' "
        cursor.execute(query.format(username))
        asinfo = cursor.fetchone()
        cursor.close()
    else:
        return render_template('home.html', errorMessage = "Don't you cheat!!!")
    
    query = """SELECT name FROM purchases JOIN customer ON customer_email = email GROUP BY name ORDER BY COUNT(name) DESC"""
    cursor = dbsql.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    if not data:
        return render_template('ashome.html', errorMessage = "No customer in the database!")
    cust = [d[0] for d in data]
    
    custn = request.form['cust']
    cursor = dbsql.cursor()
    query = "SELECT DISTINCT flight_num FROM ticket NATURAL JOIN purchases NATURAL JOIN flight JOIN customer ON customer_email = email WHERE name = \'{}\' and airline_name = \'{}\'"
    cursor.execute(query.format(custn, asinfo[5]))
    data = cursor.fetchall()
    cursor.close()
    return render_template('ascust.html', cust = cust, custn = custn, trace = [d[0] for d in data], an=asinfo[5])
    
@app.route('/asrevcom', methods = ['GET', 'POST'])
def asrevcom(start = 0, end = 0):
    username = session.get('airline_staff')
    if username != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM airline_staff WHERE username = \'{}\' "
        cursor.execute(query.format(username))
        asinfo = cursor.fetchone()
        cursor.close()
    else:
        return render_template('home.html', errorMessage = "Don't you cheat!!!")
    
    query = """SELECT SUM(price) FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE airline_name = \'{}\' AND booking_agent_id is null AND DATE_SUB(CURDATE(), INTERVAL 30 DAY) <= purchase_date"""
    cursor = dbsql.cursor()
    cursor.execute(query.format(asinfo[5]))
    data = cursor.fetchone()
    direct = data[0]
    cursor.close()
    
    query = """SELECT SUM(price) FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE airline_name = \'{}\' AND booking_agent_id is NOT null AND DATE_SUB(CURDATE(), INTERVAL 30 DAY) <= purchase_date"""
    cursor = dbsql.cursor()
    cursor.execute(query.format(asinfo[5]))
    data = cursor.fetchone()
    indirect = round(float(data[0])*0.9,2)
    cursor.close()
    
    end = str(datetime.datetime.today().year) + "-" + str(datetime.datetime.today().month) + "-" + str(datetime.datetime.today().day)
    return render_template('asrevcom.html', direct = direct, indirect = indirect, start = start, end = end)
    
@app.route('/ascomrev', methods = ['GET', 'POST'])
def ascomrev():
    username = session.get('airline_staff')
    if username != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM airline_staff WHERE username = \'{}\' "
        cursor.execute(query.format(username))
        asinfo = cursor.fetchone()
        cursor.close()
    else:
        return render_template('home.html', errorMessage = "Don't you cheat!!!")
    
    start = request.form["start"]
    end = request.form['end']
        
    query = """SELECT SUM(price) FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE airline_name = \'{}\' AND booking_agent_id is null AND purchase_date >= \'{}\' AND purchase_date <= \'{}\'"""
    cursor = dbsql.cursor()
    cursor.execute(query.format(asinfo[5],start,end))
    data = cursor.fetchone()
    direct = data[0]
    cursor.close()
    
    query = """SELECT SUM(price) FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE airline_name = \'{}\' AND booking_agent_id is NOT null AND purchase_date >= \'{}\' AND purchase_date <= \'{}\'"""
    cursor = dbsql.cursor()
    cursor.execute(query.format(asinfo[5],start,end))
    data = cursor.fetchone()
    indirect = round(float(data[0])*0.9,2)
    cursor.close()
    return render_template('asrevcom.html', direct = direct, indirect = indirect, start = start, end = end)

@app.route('/astopdes', methods = ['GET', 'POST'])
def astopdes():
    username = session.get('airline_staff')
    if username != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM airline_staff WHERE username = \'{}\' "
        cursor.execute(query.format(username))
        asinfo = cursor.fetchone()
        cursor.close()
    else:
        return render_template('home.html', errorMessage = "Don't you cheat!!!")
    
    query = """SELECT arrival_airport, COUNT(arrival_airport) FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE DATE_SUB(CURDATE(), INTERVAL 91 DAY) <= date(purchase_date) GROUP BY arrival_airport ORDER BY COUNT(arrival_airport) DESC"""
    cursor = dbsql.cursor()
    cursor.execute(query)
    counts = cursor.fetchall()
    if len(counts)>3:
        counts = counts[:3]
    threemon = [c[0] for c in counts if c[0] != None]
    cursor.close()
        
    query = """SELECT arrival_airport, COUNT(arrival_airport) FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE DATE_SUB(CURDATE(), INTERVAL 365 DAY) <= date(purchase_date) GROUP BY arrival_airport ORDER BY COUNT(arrival_airport) DESC"""
    cursor = dbsql.cursor()
    cursor.execute(query)
    counts = cursor.fetchall()
    if len(counts)>3:
        counts = counts[:3]
    year = [c[0] for c in counts if c[0] != None]
    cursor.close()
    return render_template('astopdes.html', threemon = threemon, year = year)

@app.route('/asreport')
def asreport():
    username = session.get('airline_staff')
    if username != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM airline_staff WHERE username = \'{}\' "
        cursor.execute(query.format(username))
        asinfo = cursor.fetchone()
        cursor.close()
    else:
        return render_template('home.html', errorMessage = "Don't you cheat!!!")
    
    query = """SELECT price, ticket_id, purchase_date FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE airline_name = \'{}\' ORDER BY purchase_date ASC"""
    cursor = dbsql.cursor()
    cursor.execute(query.format(asinfo[5]))
    data = cursor.fetchall()
    cursor.close()
    if not data:
        return render_template('ashome.html', errorMessage = "Revenue is zero")
    
    months = []
    now = datetime.datetime.today().year*100 + datetime.datetime.today().month
    #print('now',now) 202012
    t = data[0][2].year*100 + data[0][2].month
    print('t',t) #202008
    months.append(t)
    while t < now:
        if t % 100 == 12:
            t += 88
        t += 1
        months.append(t)
    spendings = [0 for _ in range(len(months))]
    for row in data:
        price = row[0]
        month = row[2].year*100 + row[2].month
        m = months.index(month)
        spendings[m] += float(price)
    now = str(datetime.datetime.today().year) + "-" + str(datetime.datetime.today().month)
    past_year = datetime.datetime.today().year
    past_month = datetime.datetime.today().month - 5
    if past_month < 1:
        past_month += 12
        past_year -= 1
    past = str(past_year) + "-" + str(past_month)
    if len(now) < 7:
        now = now[:5] + "0" + now[-1]
    if len(past) < 7:
        past = past[:5] + "0" + past[-1]
    print(months, spendings, now, past)
    return render_template('asreport.html',months = months, spendings = spendings, now = now, past =past)
    

'''=====================BA PART========================'''

#booking agent function
#booking agent homepage
@app.route('/bahome')
def bahome():
    email = session.get('isLogin')
    if email != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM booking_agent WHERE email = \'{}\' "
        cursor.execute(query.format(email))
        bainfo = cursor.fetchone()
        cursor.close()
        #return render_template('bahome.html', email = bainfo[1])
    else:
        return redirect(url_for(home))

    #show the baomer's upcoming flight
    cursor = dbsql.cursor()
    query = "SELECT * FROM ticket NATURAL JOIN purchases NATURAL JOIN flight where booking_agent_id = \'{}\'  AND status = 'Upcoming' "
    cursor.execute(query.format(bainfo[2]))
    baflight = cursor.fetchall()
    cursor.close()
    comingflight = []
    for i in baflight:
        comingflight.append(i)
    #print(comingflight)
    return render_template('bahome.html', email = bainfo[0], comingflight = comingflight)

#baomer all flight
@app.route('/baflight')
def baflight():
    email = session.get('isLogin')
    if email != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM booking_agent WHERE email = \'{}\' "
        cursor.execute(query.format(email))
        bainfo = cursor.fetchone()
        cursor.close()
        #return render_template('bahome.html', email = bainfo[1])
    else:
        return redirect(url_for(home))

    #show the baomer's history flight
    #date = datetime.datetime.now().strftime('%Y-%m-%d')
    cursor = dbsql.cursor()
    query = "SELECT * FROM ticket NATURAL JOIN purchases NATURAL JOIN flight where booking_agent_id =\'{}\'  "
    cursor.execute(query.format(bainfo[2]))
    baflight = cursor.fetchall()
    cursor.close()
    comingflight = []
    for i in baflight:
        comingflight.append(i)
    deptwhere = []
    for i in comingflight:
        if i[6] not in deptwhere:
            deptwhere.append(i[6])
    arrwhere = []
    for i in comingflight:
        if i[8] not in arrwhere:
            arrwhere.append(i[8])
    flightdate = []
    for i in comingflight:
        if i[7] not in flightdate:
            flightdate.append(i[7])
    return render_template('baflight.html', email = bainfo[0], comingflight = comingflight, deptwhere= deptwhere, arrwhere = arrwhere)

@app.route('/bahistorysearch', methods = ['GET','POST'])
def bahistorysearch():
    email = session.get('isLogin')
    if email != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM booking_agent WHERE email = \'{}\' "
        cursor.execute(query.format(email))
        bainfo = cursor.fetchone()
        cursor.close()
        #return render_template('bahome.html', email = bainfo[1])
    else:
        return redirect(url_for(home))
    
    dep = request.form['depart']
    arr = request.form['arrival']
    dep = convertair(dep)
    arr = convertair(arr)
    date = request.form['date']
    cursor = dbsql.cursor()
    query = "SELECT * FROM ticket NATURAL JOIN purchases NATURAL JOIN flight where booking_agent_id = %s and departure_time > %s and departure_airport = %s and arrival_airport = %s"
    #print(email, date,dep,arr)
    cursor.execute(query, (bainfo[2], date,dep,arr))
    data = cursor.fetchall()
    cursor.close()
    if(data):
        return render_template('ba_search_result.html', result = list(data))
        #return render_template("searchFlightResult.html", searchResult = list(data))
    else:
        #returns an error message to the html page
        #session['searchResult'] = ['Find no matched flight /Users/punchmeharder/Downloads/Document/Fall 2020/DB/Final/Tonywhere/templates/cust_search_result copy.htmlfor you '+dep+arr+', please try with some other routes!']
        return render_template('ba_search_result.html', result = 'Find no matched flight from '+dep+' to '+arr+', please try with some other routes!')
        #return render_template("searchFlightResult.html", searchResult = 'Find no matched flight from '+dep+' to '+arr+', please try with some other routes!')

#baomer search flight and buy homepage
@app.route('/baallflightbuy')
def baallflightbuy():
    email = session.get('isLogin')
    if email != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM booking_agent WHERE email = \'{}\' "
        cursor.execute(query.format(email))
        bainfo = cursor.fetchone()
        cursor.close()
        #return render_template('bahome.html', email = bainfo[1])
    else:
        return redirect(url_for(home))
    
    cursor = dbsql.cursor()
    cursor.execute("SELECT * FROM flight where status = 'Upcoming'")
    allflight = cursor.fetchall()
    cursor.close()
    comingflight = []
    for i in allflight:
        comingflight.append(i)
    deptwhere = []
    for i in comingflight:
        if i[2] not in deptwhere:
            deptwhere.append(i[2])
    arrwhere = []
    for i in comingflight:
        if i[4] not in arrwhere:
            arrwhere.append(i[4])
    #flightdate = []
    #for i in comingflight:
        #flightdate.append(i[7])
    cursor = dbsql.cursor()
    query = "SELECT email FROM customer"
    cursor.execute(query)
    custlist = cursor.fetchall()
    cursor.close()
    custlist2 = []
    for i in custlist:
        if i not in custlist2:
            newstr = ''
            for j in i:
                if j not in custlist2:
                    '''if j in ['(',')',',','\'',' ']:
                        pass
                    else:
                        newstr += j
                        '''
                    custlist2.append(j)
    return render_template('baallflight.html', comingflight = comingflight, deptwhere= deptwhere, arrwhere = arrwhere, custlist = custlist2)

@app.route('/baflightsearch', methods = ['GET','POST'])
def baflightsearch():
    email = session.get('isLogin')
    if email != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM booking_agent WHERE email = \'{}\' "
        cursor.execute(query.format(email))
        bainfo = cursor.fetchone()
        cursor.close()
        #return render_template('bahome.html', email = bainfo[1])
    else:
        return redirect(url_for(home))
    dep = request.form['depart']
    arr = request.form['arrival']
    dep = convertair(dep)
    arr = convertair(arr)
    date = request.form['date']
    cursor = dbsql.cursor()
    query = "SELECT * FROM flight where departure_time > %s and departure_airport = %s and arrival_airport = %s"
    #print(email, date,dep,arr)
    cursor.execute(query, ( date,dep,arr))
    data = cursor.fetchall()
    cursor.close()
    if(data):
        return render_template('ba_search_result2.html', result = list(data))
        #return render_template("searchFlightResult.html", searchResult = list(data))
    else:
        #returns an error message to the html page
        #session['searchResult'] = ['Find no matched flight for you '+dep+arr+', please try with some other routes!']
        return render_template('ba_search_result2.html', result = 'Find no matched flight from '+dep+' to '+arr+', please try with some other routes!')

#baomer buy processing function
@app.route('/babuyprocess', methods = ['GET', 'POST'])
def babuyprocess():
    email = session.get('isLogin')
    if email != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM booking_agent WHERE email = \'{}\' "
        cursor.execute(query.format(email))
        bainfo = cursor.fetchone()
        cursor.close()
        #return render_template('bahome.html', email = bainfo[1])
    else:
        return redirect(url_for(home))
    
    data = request.form["data"].replace("'", "").split(",")
    airline_name = data[0][1:]
    flight_num = int(data[1][1:])
    customer_email = request.form["customer_email"]
    
    '''airline_name = data[0]
    flight_num = data[1]'''
    
    #print(airline_name,flight_num)
    cursor = dbsql.cursor()
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    #airline_name = %s AND flight_num = %d AND 

    query1 = "select ticket_id from ticket where airline_name = %s AND flight_num = %s AND ticket_id NOT IN (select ticket_id from purchases)"
    cursor.execute(query1, (airline_name, flight_num))
    #query1 = "SELECT ticket_id from ticket where ticket_id NOT IN (select ticket_id from purchases)"
    #cursor.execute(query1)
    ticketleft = cursor.fetchall()
    if (ticketleft == []) or (ticketleft == None):
        return render_template('babuyfail.html', errorMessage = 'Sold out or you have already purchased it')
    cursor.close()
    #print(ticketleft)
    
    cursor = dbsql.cursor()
    query2 = 'INSERT INTO purchases (ticket_id,customer_email,booking_agent_id,purchase_date) values (%s,%s,%s,%s)'
    cursor.execute(query2,(ticketleft[0][0],customer_email,bainfo[2],date))
    dbsql.commit()
    cursor.close()
    return render_template('babuysuccess.html')
# search flight
    
@app.route('/bacommission', methods = ['GET', 'POST'])
def bacommission(start = 0, end = 0):
    email = session.get('isLogin')
    if email != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM booking_agent WHERE email = \'{}\' "
        cursor.execute(query.format(email))
        bainfo = cursor.fetchone()
        cursor.close()
        #return render_template('bahome.html', email = bainfo[1])
    else:
        return redirect(url_for(home))
    
    query = """SELECT SUM(price), COUNT(*) FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE booking_agent_id = \'{}\' AND DATE_SUB(CURDATE(), INTERVAL 30 DAY) <= purchase_date"""
    cursor = dbsql.cursor()
    cursor.execute(query.format(bainfo[2]))
    data = cursor.fetchone()
    price = data[0]
    counts = data[1]
    cursor.close()
    if (counts == None) or (price == None):
        price = 0;
        counts = 0;
        ave_com =0;
    else:
        ave_com = str(round(0.1*float(price)/counts,2))
    end = str(datetime.datetime.today().year) + "-" + str(datetime.datetime.today().month) + "-" + str(datetime.datetime.today().day)
    return render_template('bacommission.html',ave_com = ave_com, price = price, counts = counts, start = start, end = end)
    
@app.route('/bacomview', methods = ['GET', 'POST'])
def bacomview():
    email = session.get('isLogin')
    if email != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM booking_agent WHERE email = \'{}\' "
        cursor.execute(query.format(email))
        bainfo = cursor.fetchone()
        cursor.close()
        #return render_template('bahome.html', email = bainfo[1])
    else:
        return redirect(url_for(home))
    
    start = request.form["start"]
    end = request.form['end']
    query = """SELECT SUM(price), COUNT(*) FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE booking_agent_id = \'{}\' AND purchase_date >= \'{}\' AND purchase_date <= \'{}\' """
    cursor = dbsql.cursor()
    cursor.execute(query.format(bainfo[2], start, end))
    data = cursor.fetchone()
    price = data[0]
    counts = data[1]
    cursor.close()
    if (counts == None) or (price == None):
        price = 0;
        counts = 0;
        ave_com =0;
    else:
        ave_com = str(round(0.1*float(price)/counts,2))
    
    return render_template('bacommission.html', ave_com = ave_com, price = price, counts = counts, start = start, end = end)


@app.route('/bacust', methods = ['GET', 'POST'])
def bacust(start = 0, end = 0):
    email = session.get('isLogin')
    if email != None:
        cursor = dbsql.cursor()
        query = "SELECT * FROM booking_agent WHERE email = \'{}\' "
        cursor.execute(query.format(email))
        bainfo = cursor.fetchone()
        cursor.close()
        #return render_template('bahome.html', email = bainfo[1])
    else:
        return redirect(url_for(home))
    
    query = """SELECT name, COUNT(name) FROM purchases NATURAL JOIN ticket NATURAL JOIN flight JOIN customer ON customer_email = email WHERE booking_agent_id = \'{}\' AND DATE_SUB(CURDATE(), INTERVAL 183 DAY) <= date(purchase_date) GROUP BY name ORDER BY COUNT(name) DESC"""
    cursor = dbsql.cursor()
    cursor.execute(query.format(bainfo[2]))
    counts = cursor.fetchall()
    if len(counts)>5:
        counts = counts[:5]
    counts_cust = [c[0] for c in counts]
    counts_times = [c[1] for c in counts]
    cursor.close()
    
    query = """SELECT name, SUM(price) FROM purchases NATURAL JOIN ticket NATURAL JOIN flight JOIN customer ON customer_email = email WHERE booking_agent_id = \'{}\' AND DATE_SUB(CURDATE(), INTERVAL 365 DAY) <= date(purchase_date) GROUP BY name ORDER BY SUM(price) DESC"""
    cursor = dbsql.cursor()
    cursor.execute(query.format(bainfo[2]))
    price = cursor.fetchall()
    if len(price)>5:
        price = price[:5]
    price_cust = [c[0] for c in price]
    price_com = [float(c[1])/10 for c in price]
    cursor.close()
    return render_template('bacust.html', counts_cust = counts_cust, counts_times = counts_times, price_cust = price_cust, price_com = price_com)
    










'''==========================Damaged Coda========================='''
@app.route('/searchFlight')
def searchFlight(): 
    cursor = dbsql.cursor()
    query = "SELECT * FROM airport"
    cursor.execute(query)
    airportList = cursor.fetchall()
    cursor.close()
    return render_template('searchFlight.html', airportList = airportList)

@app.route('/searchFlightFunc', methods = ['GET','POST'])
def searchFlightFunc(): 
    dep = request.form['depart']
    #dep = dep[dep.find(',')+2:]
    arr = request.form['arrival']
    #arr = arr[arr.find(',')+2:]
    cursor = dbsql.cursor()
    if '\'' in dep:
        newarr = ''
        for i in dep:
            if i != '\'':
                newarr += i
            else:
                newarr += '\''
                newarr += '\''
        dep = newarr
    else:
        dep = convertair(dep)

    if '\'' in arr:
        newarr = ''
        for i in arr:
            if i != '\'':
                newarr += i
            else:
                newarr += '\''
                newarr += '\''
        arr = newarr
    else:
        arr = convertair(arr)
    #print('zhendelan',arr)
    query = "SELECT * FROM flight WHERE departure_airport = \'{}\' and arrival_airport = \'{}\'"
    cursor.execute(query.format(dep, arr))
    data = cursor.fetchall()
    cursor.close()
    if(data):
        #creates a session for the the user
        #session is a built in
        return render_template("searchFlightResult.html", searchResult = list(data))
    else:
        #returns an error message to the html page
        #session['searchResult'] = ['Find no matched flight for you '+dep+arr+', please try with some other routes!']
        return render_template("searchFlightResult.html")

if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)