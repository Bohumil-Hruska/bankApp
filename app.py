from flask import Flask, render_template, request, redirect, url_for,session, flash
from flaskext.mysql import MySQL
import random
import smtplib
import ssl
from datetime import datetime
import hashlib
from email.message import EmailMessage
import urllib
import re
import json

def current_course(currency1, currency2):#otestovano
    try:
        with urllib.request.urlopen('https://www.cnb.cz/cs/financni_trhy/devizovy_trh/kurzy_devizoveho_trhu/denni_kurz.txt?date={0:dd\.MM\.yyyy}') as response:
            if response.status == 200:
                url = 'https://www.cnb.cz/cs/financni_trhy/devizovy_trh/kurzy_devizoveho_trhu/denni_kurz.txt?date={0:dd\.MM\.yyyy}'
                req = urllib.request.Request(url)
                req.add_header('x-api-key', '45TzSCfYbT9SgA28vSO9rdxQHO3YKML6M4Qi045d')
                response = urllib.request.urlopen(req)
                data = str(response.read()).replace("\\n", "\n")
                with open('kursy.json', 'w') as f:
                    json.dump(data, f)
                if currency1 == currency2:
                    kurs1 = float(re.findall(f'{currency1}{{1}}[|]{{1}}[\\d,]*', data)[0].split("|")[1].replace(",", "."))
                    date = re.findall(r'\d{2}[.]\d{2}[.]\d{4}', data)[0]
                    return date, kurs1
                kurs1 = float(re.findall(f'{currency1}{{1}}[|]{{1}}[\\d,]*', data)[0].split("|")[1].replace(",", "."))
                kurs2 = float(re.findall(f'{currency2}{{1}}[|]{{1}}[\\d,]*', data)[0].split("|")[1].replace(",", "."))
                date = re.findall(r'\d{2}[.]\d{2}[.]\d{4}', data)[0]
                return date, kurs2/kurs1
            
    except urllib.error.HTTPError  as e:
        if e.code != 200:
            file = open('kursy.json')
            data = json.load(file)
            if currency1 == currency2:
                    kurs1 = float(re.findall(f'{currency1}{{1}}[|]{{1}}[\\d,]*', data)[0].split("|")[1].replace(",", "."))
                    date = re.findall(r'\d{2}[.]\d{2}[.]\d{4}', data)[0]
                    return date, kurs1
            kurs1 = float(re.findall(f'{currency1}{{1}}[|]{{1}}[\\d,]*', data)[0].split("|")[1].replace(",", "."))
            kurs2 = float(re.findall(f'{currency2}{{1}}[|]{{1}}[\\d,]*', data)[0].split("|")[1].replace(",", "."))
            date = re.findall(r'\d{2}[.]\d{2}[.]\d{4}', data)[0]
            file.close()
            return date, kurs2/kurs1

def get_data(day, month, year):
    today = day + "." + month + "." + year
    url = 'https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/vybrane.txt?od=01.01.' + str(
        year) + '&do=' + today + '&mena=EUR&format=txt'
    req = urllib.request.Request(url)
    req.add_header('x-api-key', '45TzSCfYbT9SgA28vSO9rdxQHO3YKML6M4Qi045d')
    response = urllib.request.urlopen(req)
    data = str(response.read()).split("\\n")
    del data[0]
    del data[0]
    del data[len(data) - 1]
    return data

def history_course(count_days=14):
    curr_year = datetime.now().strftime('%Y')
    curr_day = datetime.now().strftime('%d')
    curr_month = datetime.now().strftime('%m')
    data = get_data(curr_day, curr_month, curr_year)
    if len(data) < count_days:
        data = get_data(curr_day, curr_month, str(int(curr_year) - 1)) + data
    data = data[-count_days:]
    ret_data = "Kurz za poslednich " + str(count_days) + " dni:<br>"
    for day in data:
        ret_data += day.replace("|", " ") + ' CZE/EUR<br>'
    return ret_data

def send_verification(email):#otestovano
    verification_code = random.randint(1000,9999)
    email_sender = "benny.lpik@gmail.com"
    email_rec = email
    email_pass = "hnbhgqxycpucvogv"

    subject = 'Ověřovací kod!'
    body = """Váš ověřovací kod je: """ + str(verification_code)
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_rec
    em['Subject'] = subject
    em.set_content(body)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_pass)
        smtp.sendmail(email_sender, email_rec, em.as_string())
    return verification_code

def verifyUser(email,password):#otestovano
        conn = mysql.connect()
        cursor = conn.cursor()

        sql = ("SELECT * FROM uzivatele WHERE email = %s")
        val = email
        cursor.execute(sql,val)
        row = cursor.fetchall()
        cursor.close()
        conn.close()
        if  len(row) != 0:
            if str(row[0][4])==hashlib.md5(password.encode()).hexdigest():
                session['name'] = str(row[0][1]) + " "  + str(row[0][2])
                session['email'] = email
                session['userId'] = row[0][0]
                conn = mysql.connect()
                cursor = conn.cursor()
                sql = ("SELECT * FROM ucty WHERE ID_uzivatele = %s AND mena='CZK'")
                val = int(session['userId'])
                cursor.execute(sql,val)
                row = cursor.fetchall()[0]
                session['accountNum'] = row[0]
                session['accountType'] = row[2]
                session['balance'] = row[3]
                cursor.close()
                conn.close()
                return True
            else:
                return False
        else:
            return "Uživatel nenalezen!"

def createAccount(mena,userId,num):#otestovano
    acc_num = num
    conn = mysql.connect()
    cursor = conn.cursor()
    sql = ("SELECT * FROM ucty WHERE cislo = %s OR (mena=%s AND ID_uzivatele=%s)")
    val = (acc_num,mena,userId)
    cursor.execute(sql,val)
    row = cursor.fetchall()
    cursor.close()
    conn.close()
    if len(row)==0:
        conn = mysql.connect()
        cursor = conn.cursor()
        session.pop('_flashes', None)
        sql = "insert into ucty (cislo,ID_uzivatele,mena,zustatek) values (%s,%s,%s,%s)"
        val = (int(acc_num),userId,mena,int(0))
        cursor.execute(sql,val)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    else:
        return False

def withdrawMoney(form):#otestovano
    conn = mysql.connect()
    cursor = conn.cursor()
    sql = ("SELECT zustatek FROM ucty WHERE cislo = %s")
    val = session['accountNum']
    cursor.execute(sql,val)
    row = cursor.fetchall()[0]
    cursor.close()
    conn.close()
    if session['accountType'] == form['mena']:
        zustatek = float(row[0])-float(form['vyber'])
        vyber = float(form['vyber'])
    elif session['accountType'] != 'CZK' and form['mena'] == 'CZK': #pokud jiný učet nez CZK a vybirame v CZK
        date, kurz = current_course(session['accountType'],session['accountType'])
        newKurz = 1/kurz
        vyber = float(form['vyber'])*newKurz
        zustatek = float(row[0])-vyber
    elif session['accountType'] == 'CZK' and form['mena'] != 'CZK':
        date, kurz = current_course(form['mena'],form['mena'])
        vyber = float(form['vyber'])*kurz
        zustatek = float(row[0])-vyber
    else: # napríklad ucet v EUR a pridavame USD
        date, kurz = current_course(session['accountType'],form['mena'])
        vyber = float(form['vyber'])* kurz
        zustatek = float(row[0])-vyber
    if zustatek < 0:
        flash("Nedostatek financí na účtě",'notEnoughMoney')
    else:
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = ("UPDATE ucty SET zustatek = %s WHERE cislo = %s")
        val = (zustatek, session['accountNum'])
        session['balance'] = zustatek
        cursor.execute(sql,val)
        conn.commit()
        cursor.close()
        conn.close()
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = ("INSERT INTO platby (ID_odesilajici,ID_prijemce,typ_transakce,castka,datum) VALUES (%s,%s,%s,%s,%s)")
        val = (session['accountNum'],session['accountNum'],'Výběr hotovosti',vyber,datetime.now().strftime("%Y-%m-%d %H:%M"))
        cursor.execute(sql,val)
        conn.commit()
        cursor.close()
        conn.close()

def addMoney(form):#otestovano
    conn = mysql.connect()
    cursor = conn.cursor()
    sql = ("SELECT zustatek FROM ucty WHERE cislo = %s")
    val = session['accountNum']
    cursor.execute(sql,val)
    row = cursor.fetchall()[0]
    cursor.close()
    conn.close()

    if session['accountType'] == form['mena']:
        zustatek = float(row[0])+float(form['vklad'])
        vklad = float(form['vklad'])
    elif session['accountType'] != 'CZK' and form['mena'] == 'CZK': #pokud jiný učet nez CZK a pridavame vklad v CZK
        date, kurz = current_course(session['accountType'],session['accountType'])
        newKurz = 1/kurz
        vklad = float(form['vklad'])*newKurz
        zustatek = float(row[0])+vklad
    elif session['accountType'] == 'CZK' and form['mena'] != 'CZK':
        date, kurz = current_course(form['mena'],form['mena'])
        vklad = float(form['vklad'])*kurz
        zustatek = float(row[0])+vklad
    else: # napríklad ucet v EUR a pridavame USD
        date, kurz = current_course(session['accountType'],form['mena'])
        vklad = float(form['vklad']) * kurz
        zustatek = float(row[0])+vklad
    
    conn = mysql.connect()
    cursor = conn.cursor()
    sql = ("UPDATE ucty SET zustatek = %s WHERE cislo = %s")
    val = (zustatek, session['accountNum'])
    session['balance'] = zustatek
    cursor.execute(sql,val)
    conn.commit()
    cursor.close()
    conn.close()

    conn = mysql.connect()
    cursor = conn.cursor()
    sql = ("INSERT INTO platby (ID_odesilajici,ID_prijemce,typ_transakce,castka,datum) VALUES (%s,%s,%s,%s,%s)")
    val = (session['accountNum'],session['accountNum'],'Vklad hotovosti',vklad,datetime.now().strftime("%Y-%m-%d %H:%M"))
    cursor.execute(sql,val)
    conn.commit()
    cursor.close()
    conn.close()

def transferMoney(form):
    conn = mysql.connect()
    cursor = conn.cursor()
    sql = ("SELECT cislo,zustatek,mena FROM ucty WHERE cislo = %s")
    val = int(form['ucet'])
    cursor.execute(sql,val)
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    if len(data) == 0:
        flash("Číslo účtu neexistuje",'notOtherAcc')
    else:
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = ("SELECT zustatek FROM ucty WHERE cislo = %s")
        val = session['accountNum']
        cursor.execute(sql,val)
        row = cursor.fetchall()[0]
        cursor.close()
        conn.close()


        if session['accountType'] == form['mena'] == data[0][2]: #posiláme platbu z uctu na ucet  (stejna mena pro oba)
            zustatek = float(row[0])-float(form['castka'])
            vyber = float(form['castka'])
            if zustatek > 0:
                conn = mysql.connect()
                cursor = conn.cursor()
                sql = ("UPDATE ucty SET zustatek = %s WHERE cislo = %s")
                val = (zustatek, session['accountNum'])
                session['balance'] = zustatek
                cursor.execute(sql,val)
                conn.commit()
                cursor.close()
                conn.close()


                conn = mysql.connect()
                cursor = conn.cursor()
                sql = ("UPDATE ucty SET zustatek = %s WHERE cislo = %s")
                val = (data[0][1]+vyber, data[0][0])
                session['balance'] = zustatek
                cursor.execute(sql,val)
                conn.commit()
                cursor.close()
                conn.close()


                conn = mysql.connect()
                cursor = conn.cursor()
                sql = ("INSERT INTO platby (ID_odesilajici,ID_prijemce,typ_transakce,castka,datum) VALUES (%s,%s,%s,%s,%s)")
                val = (session['accountNum'],data[0][0],'Odchozí platba',vyber,datetime.now().strftime("%Y-%m-%d %H:%M"))
                cursor.execute(sql,val)
                conn.commit()
                cursor.close()
                conn.close()


                conn = mysql.connect()
                cursor = conn.cursor()
                sql = ("INSERT INTO platby (ID_odesilajici,ID_prijemce,typ_transakce,castka,datum) VALUES (%s,%s,%s,%s,%s)")
                val = (data[0][0],session['accountNum'],'Příchozí platba',vyber,datetime.now().strftime("%Y-%m-%d %H:%M"))
                cursor.execute(sql,val)
                conn.commit()
                cursor.close()
                conn.close()

                msg = "Platba byla provedena z účtu: " + str(session['accountNum']) + " " + str(form['mena'])
                flash(msg,'notOtherAcc')
            else:
                flash('Nemáte dostatek financi na provedení platby, přidejte prostředky pro platbu nebo zvolte jiný účet s dostatkem peněz!','notEnoughMoneyTransfer')
        elif session['accountType'] == form['mena'] and form['mena'] != data[0][2]: #usd ucet, posíláme v usd , posíláme na EUR
            if(form['mena'] == 'CZK'): #czk ucet, posiláme v czk, na jinou menou
                date, kurz = current_course(data[0][2],data[0][2])
                moneyToSend = float(form['castka'])*kurz
                zustatek = float(row[0])-float(form['castka'])
            elif data[0][2] == 'CZK': #usd ucet, posiláme v usd, na czk ucet
                date, kurz = current_course(session['accountType'],session['accountType'])
                moneyToSend = float(form['castka'])*kurz
                zustatek = float(row[0])-float(form['castka'])
            else:
                date, kurz = current_course(data[0][2],session['accountType'])
                moneyToSend = float(form['castka'])* kurz
                zustatek = float(row[0])-float(form['castka'])

            if zustatek > 0:
                conn = mysql.connect()
                cursor = conn.cursor()
                sql = ("UPDATE ucty SET zustatek = %s WHERE cislo = %s")
                val = (zustatek, session['accountNum'])
                session['balance'] = zustatek
                cursor.execute(sql,val)
                conn.commit()
                cursor.close()
                conn.close()


                conn = mysql.connect()
                cursor = conn.cursor()
                sql = ("UPDATE ucty SET zustatek = %s WHERE cislo = %s")
                val = (data[0][1]+moneyToSend, data[0][0])
                cursor.execute(sql,val)
                conn.commit()
                cursor.close()
                conn.close()


                conn = mysql.connect()
                cursor = conn.cursor()
                sql = ("INSERT INTO platby (ID_odesilajici,ID_prijemce,typ_transakce,castka,datum) VALUES (%s,%s,%s,%s,%s)")
                val = (session['accountNum'],data[0][0],'Odchozí platba',float(form['castka']),datetime.now().strftime("%Y-%m-%d %H:%M"))
                cursor.execute(sql,val)
                conn.commit()
                cursor.close()
                conn.close()


                conn = mysql.connect()
                cursor = conn.cursor()
                sql = ("INSERT INTO platby (ID_odesilajici,ID_prijemce,typ_transakce,castka,datum) VALUES (%s,%s,%s,%s,%s)")
                val = (data[0][0],session['accountNum'],'Příchozí platba',moneyToSend,datetime.now().strftime("%Y-%m-%d %H:%M"))
                cursor.execute(sql,val)
                conn.commit()
                cursor.close()
                conn.close()


                msg = "Platba byla provedena z účtu: " + str(session['accountNum']) + " " + str(form['mena'])
                flash(msg,'notOtherAcc')
            else:
                flash('Nemáte dostatek financi na provedení platby, přidejte prostředky pro platbu nebo zvolte jiný účet s dostatkem peněz!','notEnoughMoneyTransfer')
        elif session['accountType'] != form['mena'] and form['mena'] == data[0][2]:
            conn = mysql.connect()
            cursor = conn.cursor()
            sql = ("SELECT cislo,zustatek FROM ucty WHERE mena = %s AND ID_uzivatele = %s")
            val = (form['mena'], session['userId'])
            cursor.execute(sql,val)
            row = cursor.fetchall()
            cursor.close()
            conn.close()


            if len(row) == 0:
                msg = "Nevedete žádný účet s potřebnou měnou " + form['mena'] + ". Vytvořte účet a proveďte platbu!"
                flash(msg,'notOtherAcc')
            else:
                moneyToSend = float(form['castka'])
                zustatek = float(row[0][1])-float(form['castka'])

                if zustatek > 0:
                    conn = mysql.connect()
                    cursor = conn.cursor()
                    sql = ("UPDATE ucty SET zustatek = %s WHERE cislo = %s")
                    val = (zustatek, row[0][0])
                    cursor.execute(sql,val)
                    conn.commit()
                    cursor.close()
                    conn.close()


                    conn = mysql.connect()
                    cursor = conn.cursor()
                    sql = ("UPDATE ucty SET zustatek = %s WHERE cislo = %s")
                    val = (data[0][1]+moneyToSend, data[0][0])
                    cursor.execute(sql,val)
                    conn.commit()
                    cursor.close()
                    conn.close()


                    conn = mysql.connect()
                    cursor = conn.cursor()
                    sql = ("INSERT INTO platby (ID_odesilajici,ID_prijemce,typ_transakce,castka,datum) VALUES (%s,%s,%s,%s,%s)")
                    val = (row[0][0],data[0][0],'Odchozí platba',float(form['castka']),datetime.now().strftime("%Y-%m-%d %H:%M"))
                    cursor.execute(sql,val)
                    conn.commit()
                    cursor.close()
                    conn.close()


                    conn = mysql.connect()
                    cursor = conn.cursor()
                    sql = ("INSERT INTO platby (ID_odesilajici,ID_prijemce,typ_transakce,castka,datum) VALUES (%s,%s,%s,%s,%s)")
                    val = (data[0][0],session['accountNum'],'Příchozí platba',moneyToSend,datetime.now().strftime("%Y-%m-%d %H:%M"))
                    cursor.execute(sql,val)
                    conn.commit()
                    cursor.close()
                    conn.close()


                    msg = "Platba byla provedena z účtu: " + str(row[0][0]) + " " + str(form['mena'])
                    flash(msg,'notOtherAcc')
                
            


        elif session['accountType'] != form['mena'] and form['mena'] != data[0][2] and data[0][2] != session['accountType'] or session['accountType'] != form['mena'] and session['accountType']== data[0][2]: #USD ucet, EUR platba, PLN ucet
            conn = mysql.connect()
            cursor = conn.cursor()
            sql = ("SELECT cislo,zustatek FROM ucty WHERE mena = %s AND ID_uzivatele = %s")
            val = (form['mena'], session['userId'])
            cursor.execute(sql,val)
            row = cursor.fetchall()
            cursor.close()
            conn.close()

            
            if len(row) == 0:
                msg = "Nevedete žádný účet s potřebnou měnou " + form['mena'] + ". Vytvořte účet a proveďte platbu!"
                flash(msg,'notOtherAcc')
            else:
                if form['mena'] == 'CZK': #usd ucet, posilame v czk, na jiny ucet nez czk a usd
                    date, kurz = current_course(data[0][2],data[0][2])
                    moneyToSend = float(form['castka'])*kurz
                    zustatek = float(row[0][1])-float(form['castka'])
                elif data[0][2] =='CZK':
                    date, kurz = current_course(form['mena'],form['mena'])
                    moneyToSend = float(form['castka'])*kurz #pricteni na cesky ucet
                    zustatek = float(row[0][1])-float(form['castka'])
                else:
                    date, kurz = current_course(data[0][2],form['mena'])
                    moneyToSend = float(form['castka'])* kurz
                    zustatek = float(row[0][1])-float(form['castka'])

                if zustatek > 0:
                    conn = mysql.connect()
                    cursor = conn.cursor()
                    sql = ("UPDATE ucty SET zustatek = %s WHERE cislo = %s")
                    val = (zustatek, row[0][0])
                    cursor.execute(sql,val)
                    conn.commit()
                    cursor.close()
                    conn.close()

                    conn = mysql.connect()
                    cursor = conn.cursor()
                    sql = ("UPDATE ucty SET zustatek = %s WHERE cislo = %s")
                    val = (data[0][1]+moneyToSend, data[0][0])
                    cursor.execute(sql,val)
                    conn.commit()
                    cursor.close()
                    conn.close()

                    conn = mysql.connect()
                    cursor = conn.cursor()
                    sql = ("INSERT INTO platby (ID_odesilajici,ID_prijemce,typ_transakce,castka,datum) VALUES (%s,%s,%s,%s,%s)")
                    val = (row[0][0],data[0][0],'Odchozí platba',float(form['castka']),datetime.now().strftime("%Y-%m-%d %H:%M"))
                    cursor.execute(sql,val)
                    conn.commit()
                    cursor.close()
                    conn.close()

                    conn = mysql.connect()
                    cursor = conn.cursor()
                    sql = ("INSERT INTO platby (ID_odesilajici,ID_prijemce,typ_transakce,castka,datum) VALUES (%s,%s,%s,%s,%s)")
                    val = (data[0][0],row[0][0],'Příchozí platba',moneyToSend,datetime.now().strftime("%Y-%m-%d %H:%M"))
                    cursor.execute(sql,val)
                    conn.commit()
                    cursor.close()
                    conn.close()


                    msg = "Platba byla provedena z účtu: " + str(row[0][0]) + " " + str(form['mena'])
                    flash(msg,'notOtherAcc')
                else:
                    flash('Nemáte dostatek financi na vedlejším účtě na provedení platby, přidejte prostředky pro platbu nebo zvolte jiný účet s dostatkem peněz!','notEnoughMoneyTransfer')
        else:
            flash('Pokud chcete posílat v této měně, zvolte jiný účet','notEnoughMoneyTransfer')
    

app = Flask(__name__)
app.secret_key = "key"
app.config['MYSQL_DATABASE_USER'] = 'bea529bd809544'
app.config['MYSQL_DATABASE_PASSWORD'] = 'a0538c80'
app.config['MYSQL_DATABASE_DB'] = 'heroku_c2218c80d1e84ad'
app.config['MYSQL_DATABASE_HOST'] = 'eu-cdbr-west-03.cleardb.net'
mysql = MySQL(app)


@app.route('/', methods=['POST'])#otestovano
def login():
    email = request.form['login-username']
    password = request.form['login-password']
    if(verifyUser(email,password)):
        code = send_verification(email)
        session['code'] = code
        return redirect(url_for("verification"))
    else:
        flash("Špatné přihlašovací údaje!",'badCred')
        return redirect(url_for("login"))


@app.route('/verification',)#otestovano
def verification():
    return render_template('verification.html')

@app.route('/showHistory', methods=['GET','POST'])#otestovano
def showHistory():
    conn = mysql.connect()
    cursor = conn.cursor()
    sql = ("SELECT * FROM platby WHERE ID_odesilajici = %s  ORDER BY ID_platby DESC")
    val = session['accountNum']
    cursor.execute(sql,val)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    if len(data) == 0:
        data = "Žáadná historie"
    return render_template('history.html',data=data)

@app.route('/logout',methods=['GET','POST']) #otestovano
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route('/createNewAccount',methods=['GET','POST'])#otestovano
def createNewAccount():
    succes = createAccount(request.form['mena'],session['userId'],random.randint(10000000,99999999))
    if succes:
        None
    else:
        flash("Účet v této měně již existuje",'accountExists')
    return redirect('/home')

@app.route('/sendMoney',methods=['GET','POST'])
def sendMoney():
    transferMoney(request.form)
    return redirect('/home')

@app.route('/switchAccount',methods=['GET','POST'])#otestovano
def switchAccount():
    conn = mysql.connect()
    cursor = conn.cursor()
    sql = ("SELECT * FROM ucty WHERE ID_uzivatele =%s AND mena=%s")
    val = (session['userId'],request.form['account'])
    cursor.execute(sql,val)
    row = cursor.fetchall()[0]
    cursor.close()
    conn.close()
    session['accountNum'] = row[0]
    session['accountType'] = row[2]
    session['balance'] = row[3]
    return redirect('/home')

@app.route('/withdraw',methods=['GET','POST'])
def withdraw():
    withdrawMoney(request.form)
    return redirect('/home')

@app.route('/deposit',methods=['GET','POST'])
def deposit():
    addMoney(request.form)
    return redirect('/home')

@app.route('/verification',methods=['POST'] ) # otestovano
def ver():
    if str(session.get('code')) == request.form['login-code']:
        return redirect('/home')
    else:
        flash("Špatně zadaný kod!",'wrongCode')
        return redirect(url_for("verification"))

@app.route('/home',methods=['GET','POST'])#otestovano
def home():
    conn = mysql.connect()
    cursor = conn.cursor()
    sql = ("SELECT * FROM ucty WHERE ID_uzivatele = %s AND NOT mena=%s")
    val = (session['userId'],session['accountType'])
    cursor.execute(sql,val)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    if len(data) == 0:
        data = "Žádné další účty"
    return render_template('index.html',data=data)

@app.route('/')
def index():
    return render_template('login.html')

if __name__ == '__main__':
    app.run()