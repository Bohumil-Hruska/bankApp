from flask import Flask, render_template, request, redirect, url_for,session, flash
from flaskext.mysql import MySQL
import random
import smtplib
import ssl
from email.message import EmailMessage


def send_verification(email):
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

def verifyUser(email,password):
        sql = ("SELECT * FROM uzivatel WHERE email = %s")
        val = email
        cursor.execute(sql,val)
        row = cursor.fetchall()[0]

        if  len(row) != 0:
            if str(row[4])==password:
                session['name'] = str(row[1]) + " "  + str(row[2])
                session['email'] = email
                return True
            else:
                return False
        else:
            return "Uživatel nenalezen!"

def addUser(id,name,email,prijmeni,heslo):
    sql = "insert into uzivatel (cisdod,jmeno,prijmeni,email,heslo) values (%s,%s,%s,%s,%s)"
    val = (int(id),name,email,prijmeni,int(heslo))
    cursor.execute(sql,val)

def createAccount(mena):
    acc_num = random.randint(10000000,99999999)
    sql = ("SELECT * FROM ucet WHERE cislo = %s")
    val = acc_num
    cursor.execute(sql,val)
    row = cursor.fetchall()
    if row:
        print('ucet nepridan')
    else:
        print('ucet asi pridan')
        sql = "insert into ucet (id,cislo,vlastnik,mena,zustatek) values (%s,%s,%s,%s,%s)"
        val = (int(acc_num),int(acc_num),session['email'],mena,int(0))
        cursor.execute(sql,val)
        conn.commit()

def withdrawMoney(vyber):
    session['accountNum'] = 26465341
    sql = ("SELECT zustatek FROM ucet WHERE cislo = %s")
    val = session['accountNum']
    cursor.execute(sql,val)
    row = cursor.fetchall()[0]

    zustatek =  float(row[0])- float(vyber)
    if zustatek < 0:
        print("nic")
    else:
        sql = ("UPDATE ucet SET zustatek = %s WHERE cislo = %s")
        val = (zustatek, session['accountNum'])
        cursor.execute(sql,val)
        conn.commit()

def addMoney(vklad):
    session['accountNum'] = 26465341
    sql = ("SELECT zustatek FROM ucet WHERE cislo = %s")
    val = session['accountNum']
    cursor.execute(sql,val)
    row = cursor.fetchall()[0]

    zustatek = float(row[0])+float(vklad)
    sql = ("UPDATE ucet SET zustatek = %s WHERE cislo = %s")
    val = (zustatek, session['accountNum'])
    cursor.execute(sql,val)
    conn.commit()

app = Flask(__name__)
app.secret_key = "key"
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '123456'
app.config['MYSQL_DATABASE_DB'] = 'bank'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql = MySQL(app)

conn = mysql.connect()
cursor = conn.cursor()

@app.route('/', methods=['POST'])
def login():
    email = request.form['login-username']
    password = request.form['login-password']
    if(verifyUser(email,password)):
        #code = send_verification(email)
        #session['code'] = code
        return redirect(url_for("home"))
    else:
        flash("Špatné přihlašovací údaje!")
        return redirect(url_for("login"))


@app.route('/verification',)
def verification():
    return render_template('verification.html')

@app.route('/logout',)
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route('/createNewAccount',methods=['GET','POST'])
def createNewAccount():
    createAccount(request.form['mena'])
    return redirect('/home')

@app.route('/withdraw',methods=['GET','POST'])
def withdraw():
    withdrawMoney(request.form['vyber'])
    return redirect('/home')

@app.route('/deposit',methods=['GET','POST'])
def deposit():
    addMoney(request.form['vklad'])
    return redirect('/home')

@app.route('/verification',methods=['POST'] )
def ver():
    if str(session.get('code')) == request.form['login-code']:
        return redirect('/home')
    else:
        flash("Špatně zadaný kod!")
        return redirect(url_for("verification"))

@app.route('/home',methods=['GET','POST'])
def home():
    return render_template('index.html')

@app.route('/')
def index():
    return render_template('login.html')

if __name__ == '__main__':
    app.run()    