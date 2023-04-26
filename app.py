from flask import Flask, render_template, request, redirect, url_for,session
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
                return True
            else:
                return False
        else:
            return "Uživatel nenalezen!"



def addUser(id,name,email,prijmeni,heslo):
    sql = "insert into uzivatel (cisdod,jmeno,prijmeni,email,heslo) values (%s,%s,%s,%s,%s)"
    val = (int(id),name,email,prijmeni,int(heslo))
    cursor.execute(sql,val)

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
        code = send_verification(email)
        session['code'] = code
        return redirect(url_for("verification"))
    else:
        return "Špatné přihlášení!"

@app.route('/verification',)
def verification():
    return render_template('verification.html')

@app.route('/verification',methods=['POST'] )
def ver():
    if str(session.get('code')) == request.form['login-code']:
        return redirect('/home')
    else:
        return 1

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/')
def index():
    return render_template('login.html')

if __name__ == '__main__':
    app.run()    