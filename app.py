from flask import Flask, request 
import psycopg2
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://barber_user:QbehjfHWOePZgf8kuAczQsNI0sjed5RP@dpg-d7rr67n7f7vs73d78dgg-a/barbershop_db_0r9t')
conn = psycopg2.connect(DATABASE_URL)

with conn.cursor() as cur:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id SERIAL PRIMARY KEY,
            phone VARCHAR(20),
            name VARCHAR(100),
            booking DATE,
            time TIME,
            barber VARCHAR(30),
            service VARCHAR(30),
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    conn.commit()
    print("✅ Таблица clients готова")

app = Flask(__name__) 


gc = gspread.service_account(filename="barbershop-api-494914-1546df79a4ce.json")
sheet = gc.open("BarberShop записи").sheet1
def add_to_sheets(phone, name, booking, time, barber, service):
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(MAX(id), 0) FROM clients")
    max_id = cur.fetchone()[0]
    cur.close()
    new_id = max_id + 1
    sheet.append_row([new_id, phone, name, booking, time, barber, service])


@app.route('/') 
def home(): 
    return 'OK' 
 
@app.route('/submit', methods=['POST']) 
def submit(): 

    name = request.form.get('name') 
    phone = request.form.get('phone') 
    booking = request.form.get('booking_date') 
    time = request.form.get('time') 
    barber = request.form.get('barber') 
    service = request.form.get('service') 
 
    print(name, phone, booking, time, barber, service) 
 
    cur = conn.cursor() 
    cur.execute("INSERT INTO clients (phone, name, booking, time, barber, service) VALUES (%s, %s, %s, %s, %s, %s)", (phone, name, booking, time, barber, service)) 
    conn.commit() 
    cur.close() 

    add_to_sheets(phone, name, booking, time, barber, service)
    print(f"Запись добавлена: {name}, {phone}" )
 
    return 'OK' 
 
if __name__ == '__main__': 
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
