import unittest
from app import verifyUser
from flask import Flask, session
from app import createAccount, send_verification,app, current_course,ver,switchAccount,home,createNewAccount,showHistory, addMoney,withdrawMoney,login,transferMoney,sendMoney
from datetime import datetime
from unittest.mock import patch
from flaskext.mysql import MySQL
from unittest.mock import MagicMock


class TestSendMoney(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['MYSQL_DATABASE_HOST'] = 'eu-cdbr-west-03.cleardb.net'
        app.config['MYSQL_DATABASE_USER'] = 'bea529bd809544'
        app.config['MYSQL_DATABASE_PASSWORD'] = 'a0538c80'
        app.config['MYSQL_DATABASE_DB'] = 'heroku_c2218c80d1e84ad'
        mysql = MySQL()
        mysql.init_app(app)
        self.app = app.test_client()
        self.conn = mysql.connect()
        self.cursor = self.conn.cursor()

    def  tearDown(self):
        self.cursor.close()
        self.conn.close()
    
    def test_accNotExists(self):
        with app.test_request_context('/sendMoney', method='POST',data={'ucet' : '69'}):
            response = sendMoney()
            self.assertNotIn(bytes('Číslo účtu neexistuje','utf-8'), response.data)

    def test_sendMoneyToSameAcc(self):
        with app.test_request_context('/sendMoney', method='POST',data={'ucet' : '113', 'castka':'400','mena':'CZK'}):
            self.cursor.execute("UPDATE ucty SET zustatek= 500.00 WHERE cislo = 111")
            self.conn.commit()
            self.cursor.execute("UPDATE ucty SET zustatek= 500.00 WHERE cislo = 113")
            self.conn.commit()

            session['accountNum'] = 111
            session['accountType'] = 'CZK'
            response = sendMoney()

            self.cursor.execute("SELECT zustatek FROM ucty WHERE cislo = 113")
            result = self.cursor.fetchall()
            self.assertEqual(result[0][0], 900.00)
            self.assertEqual(session['balance'], 100)

            self.cursor.execute("UPDATE ucty SET zustatek= 0.00 WHERE cislo = 111")
            self.conn.commit()
            self.cursor.execute("UPDATE ucty SET zustatek= 0.00 WHERE cislo = 113")
            self.conn.commit()

    def test_UsdToEurInEur(self):
        with app.test_request_context('/sendMoney', method='POST',data={'ucet' : '112', 'castka':'10','mena':'EUR'}):
            self.cursor.execute("UPDATE ucty SET zustatek= 500.00 WHERE cislo = 112")
            self.conn.commit()
            self.cursor.execute("UPDATE ucty SET zustatek= 1000.00 WHERE cislo = 114")
            self.conn.commit()
            self.cursor.execute("UPDATE ucty SET zustatek= 500.00 WHERE cislo = 115")
            self.conn.commit()

            session['accountNum'] = 114
            session['accountType'] = 'USD'
            session['userId'] = 112 
            response = sendMoney()

            self.cursor.execute("SELECT zustatek FROM ucty WHERE cislo = 115")
            result = self.cursor.fetchall()
            self.assertEqual(result[0][0], 490.00)

            self.cursor.execute("SELECT zustatek FROM ucty WHERE cislo = 112")
            result = self.cursor.fetchall()
            self.assertEqual(result[0][0], 510.00)

            self.cursor.execute("SELECT zustatek FROM ucty WHERE cislo = 114")
            result = self.cursor.fetchall()
            self.assertEqual(result[0][0], 1000.00)

            self.cursor.execute("UPDATE ucty SET zustatek= 0.00 WHERE cislo = 112")
            self.conn.commit()
            self.cursor.execute("UPDATE ucty SET zustatek= 0.00 WHERE cislo = 114")
            self.conn.commit()
            self.cursor.execute("UPDATE ucty SET zustatek= 0.00 WHERE cislo = 115")
            self.conn.commit()

    def test_UsdToEurInUsd(self):
        with app.test_request_context('/sendMoney', method='POST',data={'ucet' : '112', 'castka':'10','mena':'USD'}):
            self.cursor.execute("UPDATE ucty SET zustatek= 500.00 WHERE cislo = 112")
            self.conn.commit()
            self.cursor.execute("UPDATE ucty SET zustatek= 500.00 WHERE cislo = 114")
            self.conn.commit()

            session['accountNum'] = 114
            session['accountType'] = 'USD'
            response = sendMoney()

            date, kurz = current_course('EUR','USD')

            self.cursor.execute("SELECT zustatek FROM ucty WHERE cislo = 112")
            result = self.cursor.fetchall()

            celkem = 500+kurz*10.00

            self.assertEqual(result[0][0], float("%.2f" % celkem))
            self.assertEqual(session['balance'], 490)

            self.cursor.execute("UPDATE ucty SET zustatek= 0.00 WHERE cislo = 112")
            self.conn.commit()
            self.cursor.execute("UPDATE ucty SET zustatek= 0.00 WHERE cislo = 114")
            self.conn.commit()

    def test_sendMoneyToSameAccNotEnoughMoney(self):
        with app.test_request_context('/sendMoney', method='POST',data={'ucet' : '113', 'castka':'400','mena':'CZK'}):
            self.cursor.execute("UPDATE ucty SET zustatek= 400.00 WHERE cislo = 111")
            self.conn.commit()
            self.cursor.execute("UPDATE ucty SET zustatek= 500.00 WHERE cislo = 113")
            self.conn.commit()

            session['accountNum'] = 111
            session['accountType'] = 'CZK'
            response = sendMoney()

            self.cursor.execute("SELECT zustatek FROM ucty WHERE cislo = 113")
            result = self.cursor.fetchall()
            self.assertEqual(result[0][0], 500.00)
            self.cursor.execute("SELECT zustatek FROM ucty WHERE cislo = 111")
            result = self.cursor.fetchall()
            self.assertEqual(result[0][0], 400.00)

            self.cursor.execute("UPDATE ucty SET zustatek= 0.00 WHERE cislo = 111")
            self.conn.commit()
            self.cursor.execute("UPDATE ucty SET zustatek= 0.00 WHERE cislo = 113")
            self.conn.commit()

class TestWithdrawMoney(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['MYSQL_DATABASE_HOST'] = 'eu-cdbr-west-03.cleardb.net'
        app.config['MYSQL_DATABASE_USER'] = 'bea529bd809544'
        app.config['MYSQL_DATABASE_PASSWORD'] = 'a0538c80'
        app.config['MYSQL_DATABASE_DB'] = 'heroku_c2218c80d1e84ad'
        mysql = MySQL()
        mysql.init_app(app)
        self.app = app.test_client()
        self.conn = mysql.connect()
        self.cursor = self.conn.cursor()

    def  tearDown(self):
        self.cursor.close()
        self.conn.close()

    def test_withdrawSameAccount(self):
        with app.test_request_context('/withdraw', method='POST'):
            self.cursor.execute("UPDATE ucty SET zustatek= 500.00 WHERE cislo = 111")
            self.conn.commit()

            session['accountNum'] = 111
            session['accountType'] = 'CZK'
            form = {'mena': 'CZK', 'vyber': '250.0'}

            withdrawMoney(form)

            self.assertEqual(session['balance'], 250.00)

            self.cursor.execute("UPDATE ucty SET zustatek= 0.00 WHERE cislo = 111")
            self.conn.commit()

    def test_withdrawNotCzkCzkMoney(self):
        with app.test_request_context('/withdraw', method='POST'):
            self.cursor.execute("UPDATE ucty SET zustatek= 500.00 WHERE cislo = 112")
            self.conn.commit()

            session['accountNum'] = 112
            session['accountType'] = 'EUR'
            form = {'mena': 'CZK', 'vyber': '250.0'}

            date, kurz = current_course('EUR','EUR')
            newKurz = 1/kurz
            celkem = 500 - (float(newKurz)*250)

            withdrawMoney(form)

            self.assertEqual(float("%.2f" % session['balance']), float("%.2f" % celkem))

            self.cursor.execute("UPDATE ucty SET zustatek= 0.00 WHERE cislo = 112")
            self.conn.commit()

    def test_withdrawCzkNotCzkMoney(self):
        with app.test_request_context('/withdraw', method='POST'):
            self.cursor.execute("UPDATE ucty SET zustatek= 500.00 WHERE cislo = 111")
            self.conn.commit()

            session['accountNum'] = 111
            session['accountType'] = 'CZK'
            form = {'mena': 'EUR', 'vyber': '10.0'}

            date, kurz = current_course('EUR','EUR')
            celkem = 500 - (float(kurz)*10)

            withdrawMoney(form)

            self.assertEqual(float("%.2f" % session['balance']), float("%.2f" % celkem))

            self.cursor.execute("UPDATE ucty SET zustatek= 0.00 WHERE cislo = 111")
            self.conn.commit()

    def test_withdrawNotCzkNotCzkMoney(self):
        with app.test_request_context('/withdraw', method='POST'):
            self.cursor.execute("UPDATE ucty SET zustatek= 500.00 WHERE cislo = 112")
            self.conn.commit()

            session['accountNum'] = 112
            session['accountType'] = 'EUR'
            form = {'mena': 'USD', 'vyber': '10.0'}

            date, kurz = current_course('EUR','USD')
            celkem = 500 - (float(kurz)*10)

            withdrawMoney(form)

            self.assertEqual(float("%.2f" % session['balance']), float("%.2f" % celkem))

            self.cursor.execute("UPDATE ucty SET zustatek= 0.00 WHERE cislo = 112")
            self.conn.commit()

class TestShowHistoryRoute(unittest.TestCase):
    def test_showHistory(self):
        with app.test_request_context('/showHistory', method='POST'):
            session['accountNum'] = 18714500
            session['accountType'] = 'CZK'
            response = showHistory()
            self.assertIn("<title>Bank App - Transaction History</title>", response)
            self.assertNotIn("Žáadná historie", response)
    
    def test_other_acc(self):
        with app.test_request_context('/home', method='POST'):
            session['userId'] = 1
            session['accountType'] = 'CZK'
            session['balance'] = 1
            response = home()
            self.assertIn("<title>Bank App</title>", response)
            self.assertNotIn("Žádné další účty", response)

class TestAddMoney(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['MYSQL_DATABASE_HOST'] = 'eu-cdbr-west-03.cleardb.net'
        app.config['MYSQL_DATABASE_USER'] = 'bea529bd809544'
        app.config['MYSQL_DATABASE_PASSWORD'] = 'a0538c80'
        app.config['MYSQL_DATABASE_DB'] = 'heroku_c2218c80d1e84ad'
        mysql = MySQL()
        mysql.init_app(app)
        self.app = app.test_client()
        self.conn = mysql.connect()
        self.cursor = self.conn.cursor()

    def  tearDown(self):
        self.cursor.close()
        self.conn.close()

    def test_addMoneyToSameAccount(self):
        with app.test_request_context('/deposit', method='POST'):
            session['accountNum'] = 21
            session['accountType'] = 'CZK'
            form = {'mena': 'CZK', 'vklad': '500.0'}
            addMoney(form)
            self.cursor.execute("SELECT * FROM ucty WHERE cislo = 21")
            result = self.cursor.fetchall()
            self.assertEqual(result[0][3], 500.0)

            self.cursor.execute("UPDATE ucty SET zustatek= 0.00 WHERE cislo = 21")
            self.conn.commit()

    def test_addCZKtoNotCzech(self):
        with app.test_request_context('/deposit', method='POST'):
            session['accountNum'] = 31
            session['accountType'] = 'EUR'

            date, kurz = current_course('EUR','EUR')
            newKurz = 1/kurz
            celkem = (float(newKurz)*500)
            
            form = {'mena': 'CZK', 'vklad': '500.0'}
            addMoney(form)

            self.cursor.execute("SELECT * FROM ucty WHERE cislo = 31")
            result = self.cursor.fetchall()
            
            self.assertEqual(result[0][3], float("%.2f" % celkem))

            self.cursor.execute("UPDATE ucty SET zustatek= 0.00 WHERE (cislo = 31)")
            self.conn.commit()

    def test_addNotCzkToCZK(self):
        with app.test_request_context('/deposit', method='POST'):
            session['accountNum'] = 21
            session['accountType'] = 'CZK'

            date, kurz = current_course('EUR','EUR')
            celkem = (float(kurz)*10)
            
            form = {'mena': 'EUR', 'vklad': '10.0'}
            addMoney(form)

            self.cursor.execute("SELECT * FROM ucty WHERE cislo = 21")
            result = self.cursor.fetchall()
            
            self.assertEqual(result[0][3], float("%.2f" % celkem))

            self.cursor.execute("UPDATE ucty SET zustatek= 0.00 WHERE (cislo = 21)")
            self.conn.commit()

    def test_addMoneyToDifferent(self):
        with app.test_request_context('/deposit', method='POST'):
            session['accountNum'] = 31
            session['accountType'] = 'EUR'

            date, kurz = current_course('EUR','USD')
            celkem = (float(kurz)*10)
            
            form = {'mena': 'USD', 'vklad': '10.0'}
            addMoney(form)

            self.cursor.execute("SELECT * FROM ucty WHERE cislo = 31")
            result = self.cursor.fetchall()
            
            self.assertEqual(result[0][3], float("%.2f" % celkem))

            self.cursor.execute("UPDATE ucty SET zustatek= '0.00' WHERE (cislo = 31)")
            self.conn.commit()

class TestHome(unittest.TestCase):
    def test_no_other_acc(self):
        with app.test_request_context('/home', method='POST'):
            session['userId'] = 10
            session['accountType'] = 'PLN'
            session['balance'] = 1
            response = home()
            self.assertIn("<title>Bank App</title>", response)
            self.assertIn("Žádné další účty", response)
    
    def test_other_acc(self):
        with app.test_request_context('/home', method='POST'):
            session['userId'] = 1
            session['accountType'] = 'CZK'
            session['balance'] = 1
            response = home()
            self.assertIn("<title>Bank App</title>", response)
            self.assertNotIn("Žádné další účty", response)

class TestLoginAndVefify(unittest.TestCase):
    def test_goodCred(self):
        with app.test_request_context('/', method='POST',data={'login-username': 'BennyPear@seznam.cz', 'login-password': 'test'}):
                response = login()
                self.assertEqual(response.location, '/verification')

    def test_wrongCred(self):
        with app.test_request_context('/', method='POST',data={'login-username': 'BennyPear@seznam.cz', 'login-password': '1234'}):
                response = login()
                self.assertEqual(response.location, '/')
                
class TestCreateNewBankAcc(unittest.TestCase):
    def test_newAccountExist(self):
        with app.test_request_context('/createNewAccount', method='POST',data={'mena': 'USD'}):
            session['userId'] = 1
            response = createNewAccount()
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, '/home')
    def test_newAccountNotExists(self):
            with app.test_request_context('/createNewAccount', method='POST',data={'mena': 'PLN'}):
                session['userId'] = 1
                response = createNewAccount()
                self.assertEqual(response.location, '/home')
                self.assertNotIn(bytes('Účet v této měně již existuje','utf-8'), response.data)

class TestSwitchAccount(unittest.TestCase):
    def test_correct_code(self):
        with app.test_request_context('/switchAccount', method='POST', data={'account': 'USD'}):
            session['userId'] = 1
            response = switchAccount()
            self.assertEqual(session.get('accountNum'), 41537098)
            self.assertEqual(session.get('accountType'), 'USD')
            self.assertEqual(session.get('userId'), 1)
            self.assertEqual(response.location, '/home')

class TestVerificationCode(unittest.TestCase):
    def test_correct_code(self):
        with app.test_request_context('/verification', method='POST', data={'login-code': '1234'}):
            session['code'] = '1234'
            response = ver()
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, '/home')

    def test_incorrect_code(self):
        with app.test_request_context('/verification', method='POST', data={'login-code': '4321'}):
            session['code'] = '1234'
            response = ver()
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, '/verification')

class TestLogout(unittest.TestCase):
    def test_logout(self):
        with app.test_client().session_transaction() as session:
            session['user'] = 'testuser'
            response = app.test_client().get('/logout', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'<title>Bank App - Login</title>', response.data)

class TestVerification(unittest.TestCase):
    def test_verification(self):
        response = app.test_client().get('/verification') 
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<!DOCTYPE html>', response.data)
        self.assertIn(b'<title>Bank App - Verification</title>', response.data)
        self.assertIn(b'<div id="top-menu">', response.data)

class TestCourse(unittest.TestCase):
    def test_usd_eur(self):
        date, rate = current_course("USD", "EUR")
        self.assertIsInstance(datetime.strptime(date, '%d.%m.%Y'), datetime)
        self.assertIsInstance(rate, float)
        self.assertGreater(rate, 0)

    def test_czk_usd(self):
        date, rate = current_course("USD", "USD")
        self.assertIsInstance(datetime.strptime(date, '%d.%m.%Y'), datetime)
        self.assertIsInstance(rate, float)
        self.assertGreater(rate, 0)

class TestSendVerification(unittest.TestCase):
    @patch('smtplib.SMTP_SSL')
    def test_send_verification(self, mock_smtp):
        email = "example@test.com"
        code = send_verification(email)
        self.assertTrue(code >= 1000 and code <= 9999)
        mock_smtp.assert_called_once()

class TestCreateAccount(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['MYSQL_DATABASE_HOST'] = 'eu-cdbr-west-03.cleardb.net'
        app.config['MYSQL_DATABASE_USER'] = 'bea529bd809544'
        app.config['MYSQL_DATABASE_PASSWORD'] = 'a0538c80'
        app.config['MYSQL_DATABASE_DB'] = 'heroku_c2218c80d1e84ad'
        mysql = MySQL()
        mysql.init_app(app)
        self.app = app.test_client()
        self.conn = mysql.connect()
        self.cursor = self.conn.cursor()

    def tearDown(self) :
        self.cursor.close()
        self.conn.close()

    def test_create_new_account(self):
        currency = 'USD'
        user_id = 11
        num = 11

        with app.test_request_context():
            createAccount(currency, user_id,num)

        self.cursor.execute("SELECT * FROM ucty WHERE cislo = 11")
        result = self.cursor.fetchall()
        self.assertEqual(result[0][2], currency)
        self.assertEqual(result[0][1], user_id)

        self.cursor.execute("DELETE FROM ucty WHERE cislo = 11")
        self.conn.commit()

    def test_create_existing_account(self):
        currency = 'USD'
        user_id = 10
        num = 10
        sql = "INSERT INTO ucty (cislo, ID_uzivatele, mena, zustatek) VALUES (10, %s, %s, 0)"
        val = (user_id, currency)
        self.cursor.execute(sql,val)
        self.conn.commit()

        with app.test_request_context():
            result = createAccount(currency, user_id,num) 

        self.assertEqual(result, False)

        self.cursor.execute("DELETE FROM ucty WHERE cislo = 10")
        self.conn.commit()

class TestVerifyUser(unittest.TestCase): 
    def test_correct_password(self):
        # Testování správného hesla.
        email = "bennypear@seznam.cz"
        password = "test"
        with app.test_request_context():
            result = verifyUser(email, password)
        self.assertEqual(result, True)
    def test_incorrect_password(self):
    # Testování nesprávného hesla.
        email = "bennypear@seznam.cz"
        password = "ahoj"
        result = verifyUser(email, password)
        self.assertEqual(result, False)
    def test_unknown_user(self):
    # Testování neexistujícího uživatele.
        email = "unknown@example.com"
        password = "password"
        result = verifyUser(email, password)
        self.assertEqual(result, "Uživatel nenalezen!")

if __name__ == '__main__':
    unittest.main()