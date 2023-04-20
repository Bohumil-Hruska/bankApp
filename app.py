from flask import Flask, render_template
from flaskext.mysql import MySQL

def sum(a,b):
    return a+b


def addUser(id,name,email,prijmeni,heslo):
    sql = "insert into uzivatel (cisdod,jmeno,prijmeni,email,heslo) values (%s,%s,%s,%s,%s)"
    val = (int(id),name,email,prijmeni,int(heslo))
    cursor.execute(sql,val)



app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '123456'
app.config['MYSQL_DATABASE_DB'] = 'bank'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql = MySQL(app)

conn = mysql.connect()
cursor = conn.cursor()



@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    addUser(2,"test","test","test","123456")
    cursor.execute("SELECT * FROM uzivatel")
    data = cursor.fetchall()
    print(data)
    app.run(debug=True)
    