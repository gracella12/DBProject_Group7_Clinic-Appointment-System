from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
pymysql.install_as_MySQLdb()
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key ='membuatLogin'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'DBProject'
app.config['MYSQL_UNIX_SOCKET'] = '/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock'

mysql = MySQL(app)

@app.route('/')
def home():
    if 'email' in session:
        return render_template('home.html', email=session['email'])
    else:   
        return render_template('home.html')   

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        pwd = request.form['password']
        
        try:
            cur = mysql.connection.cursor()
            cur.execute('SELECT email, password FROM pasien WHERE email = %s', (email,))
            user = cur.fetchone()
            cur.close()
            
            if user and pwd == user[1]:
                session['email'] = user[0]
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                return render_template('login.html', error='Invalid email or password')
        except Exception as e:
            return render_template('login.html', error=f'Database error: {str(e)}')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        pwd = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute('insert into pasien (email, password) values (%s, %s)', (email, pwd))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/editProfile', methods=['GET', 'POST'])
def editProfile():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        nama_depan = request.form['nama_depan']
        nama_belakang = request.form['nama_belakang']
        gender = request.form['gender']
        tanggal_lahir = request.form['tanggal_lahir']
        kota = request.form['kota']
        jalan = request.form['jalan']
        telepon_list = request.form.getlist('telepon[]') 
        email = session['email']
        
        try:
            cur = mysql.connection.cursor()
            
            cur.execute('SELECT pasien_id FROM pasien WHERE email = %s', (email,))
            result = cur.fetchone()
            if not result:
                flash('User not found!', 'error')
                return redirect(url_for('login'))
            
            pasien_id = result[0]
            
            cur.execute('''
                UPDATE pasien 
                SET nama_depan = %s, nama_belakang = %s, gender = %s, 
                    tanggal_lahir = %s, Kota = %s, Jalan = %s 
                WHERE email = %s
            ''', (nama_depan, nama_belakang, gender, tanggal_lahir, kota, jalan, email))
            
            cur.execute('DELETE FROM Pasien_telepon WHERE pasien_id = %s', (pasien_id,))
            
            for telepon in telepon_list:
                telepon = telepon.strip()
                if telepon:  
                    cur.execute('INSERT INTO Pasien_telepon (telepon, pasien_id) VALUES (%s, %s)', 
                               (telepon, pasien_id))
            
            mysql.connection.commit()
            cur.close()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            flash(f'Error updating profile: {str(e)}', 'error')
            return render_template('editProfile.html', email=session['email'])
    
    return render_template('editProfile.html', email=session['email'])

@app.route('/deleteAccount', methods=['GET'])
def deleteAccount():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    email = session['email']
    
    try:
        cur = mysql.connection.cursor()
        
        cur.execute('SELECT pasien_id FROM pasien WHERE email = %s', (email,))
        result = cur.fetchone()
        
        if result:
            pasien_id = result[0]
            
            cur.execute('DELETE FROM Pasien_telepon WHERE pasien_id = %s', (pasien_id,))

            cur.execute('DELETE FROM pasien WHERE pasien_id = %s', (pasien_id,))
            
            mysql.connection.commit()
            
            session.clear()
            flash('Your account has been deleted successfully.', 'success')
        else:
            flash('Account not found.', 'error')
        
        cur.close()
        return redirect(url_for('home'))
        
    except Exception as e:
        flash(f'Error deleting account: {str(e)}', 'error')
        return redirect(url_for('editProfile'))
        
# Modul Dokter 
@app.route('/dokter/add', methods=['GET', 'POST'])
def add_dokter():
    if 'email' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        nama_depan = request.form['nama_depan']
        nama_belakang = request.form['nama_belakang']
        tanggal_masuk = request.form['tanggal_masuk']
        status = request.form['status']

        try:
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO Dokter (nama_depan, nama_belakang, tanggal_masuk, status) VALUES (%s, %s, %s, %s)",
                (nama_depan, nama_belakang, tanggal_masuk, status)
            )
            mysql.connection.commit()
            cur.close()

            flash('New doctor is successfully added!', 'success')
            return redirect(url_for('display_dokter'))
        
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('add_dokter'))

    return render_template('addDokter.html')

@app.route('/dokter')
def display_dokter():
    if 'email' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT dokter_id, nama_depan, nama_belakang, tanggal_masuk, status FROM Dokter")
        data_dokter = cur.fetchall()
        cur.close()
        return render_template('displayDokter.html', dokter_list=data_dokter)
    
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('home'))

@app.route('/dokter/edit/<int:id>', methods=['GET', 'POST'])
def edit_dokter(id):
    if 'email' not in session:
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()

    if request.method == 'POST':
       nama_depan = request.form['nama_depan']
       nama_belakang = request.form['nama_belakang']
       status = request.form['status']
       telepon_list = request.form.getlist('telepon[]')
       
       try:
           cur.execute(
               "UPDATE Dokter SET nama_depan = %s, nama_belakang = %s, status = %s WHERE dokter_id = %s",
                (nama_depan, nama_belakang, status, id)
           )

           cur.execute("DELETE FROM Dokter_telepon WHERE dokter_id = %s", (id,))
           for telepon in telepon_list:
                telepon = telepon.strip()
                if telepon:
                    cur.execute("INSERT INTO Dokter_telepon (telepon, dokter_id) VALUES (%s, %s)",
                               (telepon, id))
            
           mysql.connection.commit()
           cur.close()
           flash('The doctor record is successfully updated!', 'success')
           return redirect(url_for('display_dokter'))
       
       except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('edit_dokter', id=id)) 

    cur.execute("SELECT nama_depan, nama_belakang, status FROM Dokter WHERE dokter_id = %s", (id,))
    dokter = cur.fetchone()
    
    if not dokter:
        cur.close()
        flash('Doctor not found!', 'error')
        return redirect(url_for('display_dokter'))
    
    cur.execute("SELECT telepon FROM Dokter_telepon WHERE dokter_id = %s", (id,))
    telepon_dokter = cur.fetchall()
    
    cur.close()
    
    return render_template('editDokter.html', dokter=dokter, telepon_list=telepon_dokter, dokter_id=id)

@app.route('/dokter/delete/<int:id>')
def delete_dokter(id):
    if 'email' not in session: 
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM Dokter WHERE dokter_id = %s", (id,))
        
        mysql.connection.commit()
        cur.close()
        
        flash('Data dokter berhasil dihapus.', 'success')
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        
    return redirect(url_for('display_dokter'))

# Modul Resepsionis
@app.route('/resepsionis/add', methods=['GET', 'POST'])
def add_resepsionis():
    if 'email' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        nama_depan = request.form['nama_depan']
        nama_belakang = request.form['nama_belakang']
        tanggal_masuk = request.form['tanggal_masuk']
        status = request.form['status']

        try:
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO Resepsionis (nama_depan, nama_belakang, tanggal_masuk, status) VALUES (%s, %s, %s, %s)",
                (nama_depan, nama_belakang, tanggal_masuk, status)
            )
            mysql.connection.commit()
            cur.close()

            flash('New receptionist is successfully added!', 'success')
            return redirect(url_for('display_resepsionis'))
        
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('add_resepsionis'))

    return render_template('addResepsionis.html')

@app.route('/resepsionis')
def display_resepsionis():
    if 'email' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT resepsionis_id, nama_depan, nama_belakang, tanggal_masuk, status FROM Resepsionis")
        data_resepsionis = cur.fetchall()
        cur.close()
        return render_template('displayResepsionis.html', resepsionis_list=data_resepsionis)
    
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('home'))
    
@app.route('/resepsionis/edit/<int:id>', methods=['GET', 'POST'])
def edit_resepsionis(id):
    if 'email' not in session:
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()

    if request.method == 'POST':
       nama_depan = request.form['nama_depan']
       nama_belakang = request.form['nama_belakang']
       status = request.form['status']
       telepon_list = request.form.getlist('telepon[]')
       
       try:
           cur.execute(
               "UPDATE Resepsionis SET nama_depan = %s, nama_belakang = %s, status = %s WHERE resepsionis_id = %s",
                (nama_depan, nama_belakang, status, id)
           )

           cur.execute("DELETE FROM Resepsionis_telepon WHERE resepsionis_id = %s", (id,))
           for telepon in telepon_list:
                telepon = telepon.strip()
                if telepon:
                    cur.execute("INSERT INTO Resepsionis_telepon (telepon, resepsionis_id) VALUES (%s, %s)",
                               (telepon, id))
            
           mysql.connection.commit()
           cur.close()
           flash('The receptionist record is successfully updated!', 'success')
           return redirect(url_for('display_resepsionis'))
       
       except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('edit_resepsionis', id=id)) 

    cur.execute("SELECT nama_depan, nama_belakang, status FROM Resepsionis WHERE resepsionis_id = %s", (id,))
    resepsionis = cur.fetchone()
    
    cur.execute("SELECT telepon FROM Resepsionis_telepon WHERE resepsionis_id = %s", (id,))
    telepon_resepsionis = cur.fetchall()
    
    cur.close()
    
    return render_template('editResepsionis.html', resepsionis=resepsionis, telepon_list=telepon_resepsionis, resepsionis_id=id)

@app.route('/resepsionis/hapus/<int:id>')
def delete_resepsionis(id):
    if 'email' not in session: 
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM Resepsionis WHERE resepsionis_id = %s", (id,))
        
        mysql.connection.commit()
        cur.close()
        
        flash('Data resepsionis berhasil dihapus.', 'success')
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        
    return redirect(url_for('display_resepsionis'))

#Modul Jadwal Dokter
@app.route('/jadwal/add', methods=['GET','POST'])
def add_jadwal():
    if request.method == 'POST':
        dokter_id = request.form['dokter_id']
        hari = request.form['hari']
        jam_mulai = request.form['jam_mulai']
        jam_selesai = request.form['jam_selesai']

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO Jadwal_dokter (dokter_id, hari, jam_mulai, jam_selesai)
            VALUES (%s, %s, %s, %s)
        """, (dokter_id, hari, jam_mulai, jam_selesai))
        mysql.connection.commit()
        cur.close()

        flash("Jadwal berhasil ditambahkan", "success")
        return redirect(url_for('display_jadwal'))
    
    return render_template('addJadwal.html')

@app.route('/jadwal')
def display_jadwal():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Jadwal_dokter")
    data = cur.fetchall()
    cur.close()
    return render_template('displayJadwal.html', jadwal_list=data)

@app.route('/jadwal/delete/<int:id>')
def delete_jadwal(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Jadwal_dokter WHERE jadwal_id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash("Jadwal berhasil dihapus", "success")
    return redirect(url_for('display_jadwal'))

#Modul appoinment
@app.route('/appointment/book/<int:jadwal_id>')
def book_appointment(jadwal_id):
    if 'email' not in session:
        return redirect(url_for('login'))

    email = session['email']

    cur = mysql.connection.cursor()
    cur.execute("SELECT pasien_id FROM pasien WHERE email=%s", (email,))
    pasien_id = cur.fetchone()[0]

    # Ambil dokter_id dari jadwal
    cur.execute("SELECT dokter_id, hari, jam_mulai FROM Jadwal_dokter WHERE jadwal_id=%s", (jadwal_id,))
    dokter_id, hari, jam_mulai = cur.fetchone()

    cur.execute("""
        INSERT INTO Appointment (pasien_id, dokter_id, jadwal_id, tanggal, waktu, status)
        VALUES (%s, %s, %s, CURDATE(), %s, 'booked')
    """, (pasien_id, dokter_id, jadwal_id, jam_mulai))

    mysql.connection.commit()
    cur.close()

    flash("Appointment berhasil dibuat!", "success")
    return redirect(url_for('display_appointment'))

@app.route('/appointment')
def display_appointment():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Appointment WHERE status='booked'")
    data = cur.fetchall()
    cur.close()
    return render_template('displayAppointment.html', app_list=data)

@app.route('/appointment/delete/<int:id>')
def delete_appointment(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Appointment WHERE appointment_id=%s", (id,))
    mysql.connection.commit()
    cur.close()

    flash("Appointment dibatalkan.", "success")
    return redirect(url_for('display_appointment'))

#Modul Rekam medis
@app.route('/rekam/add/<int:appointment_id>', methods=['GET','POST'])
def add_rekam(appointment_id):
    if request.method == 'POST':
        diagnosis = request.form['diagnosis']
        desc = request.form['description']

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO Rekam_medis (appointment_id, diagnosis, description)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                diagnosis=%s,
                description=%s
        """, (appointment_id, diagnosis, desc, diagnosis, desc))

        mysql.connection.commit()
        cur.close()

        flash("Rekam medis berhasil disimpan", "success")
        return redirect(url_for('display_rekam'))

    return render_template('addRekam.html', appointment_id=appointment_id)

@app.route('/rekam')
def display_rekam():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Rekam_medis")
    data = cur.fetchall()
    cur.close()
    return render_template('displayRekam.html', rekam_list=data)

if __name__ == '__main__':
    app.run(debug=True)
