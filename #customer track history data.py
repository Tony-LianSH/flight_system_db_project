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
        return render_template('home.html', errorMessage = "spending is zero")
    
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