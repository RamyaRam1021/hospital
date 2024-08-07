from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
from decimal import Decimal
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

# MySQL configuration
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'ladduhr@1021')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'hospital_management')

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

# Doctor routes
@app.route('/doctors')
def doctors():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM doctors')
    doctors = cursor.fetchall()
    return render_template('doctors.html', doctors=doctors)

@app.route('/add_doctor', methods=['GET', 'POST'])
def add_doctor():
    if request.method == 'POST':
        name = request.form['name']
        specialization = request.form['specialization']
        phone = request.form['phone']
        email = request.form['email']
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO doctors (name, specialization, phone, email) VALUES (%s, %s, %s, %s)', (name, specialization, phone, email))
        mysql.connection.commit()
        return redirect(url_for('doctors'))
    return render_template('add_doctor.html')

# Patient routes
@app.route('/patients')
def patients():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM patients')
    patients = cursor.fetchall()
    return render_template('patients.html', patients=patients)

@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO patients (name, age, gender, phone, email, address) VALUES (%s, %s, %s, %s, %s, %s)', (name, age, gender, phone, email, address))
        mysql.connection.commit()
        return redirect(url_for('patients'))
    return render_template('add_patient.html')

# Medicine routes
@app.route('/medicines')
def medicines():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM medicines')
        medicines = cursor.fetchall()
        return render_template('medicines.html', medicines=medicines)
    except Exception as e:
        print(f"Error fetching medicines: {e}")
        return "Error fetching medicines"

@app.route('/add_medicine', methods=['GET', 'POST'])
def add_medicine():
    if request.method == 'POST':
        try:
            name = request.form['name']
            manufacturer = request.form['manufacturer']
            price = request.form['price']
            stock = request.form['stock']
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO medicines (name, manufacturer, price, stock) VALUES (%s, %s, %s, %s)', (name, manufacturer, price, stock))
            mysql.connection.commit()
            return redirect(url_for('medicines'))
        except Exception as e:
            print(f"Error adding medicine: {e}")
            return "Error adding medicine"
    return render_template('add_medicine.html')

# Bill routes
@app.route('/bills')
def bills():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''SELECT bills.*, patients.name AS patient_name, doctors.name AS doctor_name, medicines.name AS medicine_name 
                      FROM bills 
                      JOIN patients ON bills.patient_id = patients.id 
                      JOIN doctors ON bills.doctor_id = doctors.id 
                      JOIN medicines ON bills.medicine_id = medicines.id''')
    bills = cursor.fetchall()
    return render_template('bills.html', bills=bills)

@app.route('/add_bill', methods=['GET', 'POST'])
def add_bill():
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        doctor_id = request.form['doctor_id']
        medicine_id = request.form['medicine_id']
        quantity = int(request.form['quantity'])
        consultation_fee = Decimal(request.form['consultation_fee'])
        date = request.form['date']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT price FROM medicines WHERE id = %s', (medicine_id,))
        medicine = cursor.fetchone()
        
        if medicine:
            medicine_price = Decimal(medicine['price'])  # Ensure this is Decimal
            total_amount = (medicine_price * quantity) + consultation_fee
            # Debug print
            print(f"Medicine Price: {medicine_price}, Quantity: {quantity}, Consultation Fee: {consultation_fee}, Total Amount: {total_amount}")
            
            cursor.execute('INSERT INTO bills (patient_id, doctor_id, medicine_id, quantity, consultation_fee, amount, date) VALUES (%s, %s, %s, %s, %s, %s, %s)', 
                           (patient_id, doctor_id, medicine_id, quantity, consultation_fee, total_amount, date))
            mysql.connection.commit()
            return redirect(url_for('bills'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT id, name FROM patients')
    patients = cursor.fetchall()
    cursor.execute('SELECT id, name FROM doctors')
    doctors = cursor.fetchall()
    cursor.execute('SELECT id, name, price FROM medicines')
    medicines = cursor.fetchall()
    
    return render_template('add_bill.html', patients=patients, doctors=doctors, medicines=medicines)

@app.route('/get_medicine_price/<int:medicine_id>')
def get_medicine_price(medicine_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT price FROM medicines WHERE id = %s', (medicine_id,))
    medicine = cursor.fetchone()
    if medicine:
        return jsonify({'price': medicine['price']})
    return jsonify({'price': 0})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
