from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='ajay@2005',
    database='electricbill'
)
cur = conn.cursor()

RATE_PER_KWH = {
    'low': 0,
    'medium': 2.25,
    'high': 6.00
}
FIXED_CHARGE = 20
ENERGY_DUTY = 0.15

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'POST':
        cur.execute("""CREATE TABLE IF NOT EXISTS electricbill (
            name VARCHAR(30),
            monyear VARCHAR(30),
            pu FLOAT,
            tamount FLOAT
        );""")
        conn.commit()
        return render_template('setup.html', message="Setup completed successfully.")
    return render_template('setup.html')

@app.route('/calculate', methods=['GET', 'POST'])
def calculate():
    if request.method == 'POST':
        name = request.form['name']
        appliances = int(request.form['appliances'])
        pu = 0.0
        for i in range(appliances):
            pr = float(request.form[f'power_rating_{i+1}'])
            t = int(request.form[f'usage_time_{i+1}'])
            pu += (pr * t / 1000)
        if pu <= 100:
            amount = 0
        elif pu <= 200:
            amount = (100* 0) +  (pu - 100) * 2.25
        else:
            amount =  (100 * 0) + (100 * 2.25) + (300 * 4.50) + ((pu - 500) * 6.00)
        tamount = amount + FIXED_CHARGE + (pu * ENERGY_DUTY)
        monyear = request.form['monyear']
        sql = "INSERT INTO electricbill (name, monyear, pu, tamount) VALUES (%s, %s, %s, %s)"
        cur.execute(sql, (name, monyear, pu, tamount))
        conn.commit()
        return render_template('calculate.html', tamount=tamount)
    return render_template('calculate.html')

@app.route('/find', methods=['GET', 'POST'])
def find():
    if request.method == 'POST':
        name = request.form['name']
        monyear = request.form['monyear']
        cur.execute("SELECT * FROM electricbill WHERE name = %s AND monyear = %s", (name, monyear))
        records = cur.fetchall()
        return render_template('find.html', records=records)
    return render_template('find.html')

@app.route('/findall', methods=['GET', 'POST'])
def findall():
    if request.method == 'POST':
        name = request.form['name']
        cur.execute("SELECT * FROM electricbill WHERE name = %s", (name,))
        records = cur.fetchall()
        return render_template('findall.html', records=records)
    return render_template('findall.html')

@app.route('/appliances')
def appliances():
    return render_template('appliances.html')

@app.route('/info')
def info():
    return render_template('info.html')

if __name__ == '__main__':
    app.run(debug=True, port=2000)
