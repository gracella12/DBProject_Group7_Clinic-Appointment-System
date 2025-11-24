from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
pymysql.install_as_MySQLdb()
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key ='membuatLogin'

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT', 3306))

#if os.name != 'nt':
    #app.config['MYSQL_UNIX_SOCKET'] = '/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock'

mysql = MySQL(app)

@app.route('/')
def home():
    # Ambil data dokter dari database
    cur = mysql.connection.cursor()
    cur.execute("SELECT dokter_id, nama_depan, nama_belakang, tanggal_masuk, status, foto FROM Dokter")
    doctors = cur.fetchall()
    cur.close()
    
    # Kirim data 'doctors' ke template
    if 'email' in session:
        return render_template('home.html', email=session['email'], doctors=doctors)
    else:   
        return render_template('home.html', doctors=doctors)
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        pwd = request.form['password']
        
        cur = mysql.connection.cursor()
        
        cur.execute('SELECT pasien_id, email, password FROM Pasien WHERE email = %s', (email,))
        pasien = cur.fetchone()
        
        if pasien:
            if check_password_hash(pasien[2], pwd):
                session['email'] = pasien[1]
                session['role'] = 'pasien'
                session['id'] = pasien[0]
                cur.close()
                flash('Login successful!', 'success')
                return redirect(url_for('home')) 
        
        cur.execute('SELECT resepsionis_id, email, password FROM Resepsionis WHERE email = %s', (email,))
        resepsionis = cur.fetchone()
        
        if resepsionis:
            if check_password_hash(resepsionis[2], pwd):
                session['email'] = resepsionis[1]
                session['role'] = 'resepsionis'
                session['id'] = resepsionis[0]
                cur.close()
                flash('Welcome Resepsionis!', 'success')
                return redirect(url_for('homepageResepsionis')) 

        cur.execute('SELECT dokter_id, email, password FROM Dokter WHERE email = %s', (email,))
        dokter = cur.fetchone()
        
        if dokter:
            if check_password_hash(dokter[2], pwd):
                session['email'] = dokter[1]
                session['role'] = 'dokter'
                session['id'] = dokter[0]
                cur.close()
                flash('Welcome Dokter!', 'success')
                return redirect(url_for('homepageDokter'))

        cur.close()
        return render_template('login.html', error='Invalid email or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        pwd = request.form['password']
        hashed_password = generate_password_hash(pwd, method='pbkdf2:sha256')
        
        cur = mysql.connection.cursor()
        cur.execute('insert into pasien (email, password) values (%s, %s)', (email, hashed_password))
        mysql.connection.commit()
        cur.close()
        
        flash('Registration successful! Please login.', 'success') # Opsional: feedback user
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
            return redirect(url_for('profile'))
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
    

@app.route('/profile')
def profile():
    # 1. Cek Login
    if 'email' not in session:
        return redirect(url_for('login'))
    
    email = session['email']
    cur = mysql.connection.cursor()
    
    # 2. Ambil Data Diri Pasien
    # Mengambil: nama_depan, nama_belakang, email, gender, tgl_lahir, kota, jalan, tgl_daftar
    cur.execute("""
        SELECT nama_depan, nama_belakang, email, gender, 
               tanggal_lahir, Kota, Jalan, tanggal_daftar 
        FROM Pasien 
        WHERE email = %s
    """, (email,))
    user_data = cur.fetchone()
    
    if not user_data:
        flash('User data not found', 'error')
        return redirect(url_for('home'))

    # Dictionary agar mudah dipanggil di HTML (user.nama_depan, dll)
    user_info = {
        'nama_depan': user_data[0],
        'nama_belakang': user_data[1],
        'email': user_data[2],
        'gender': user_data[3],
        'tanggal_lahir': user_data[4],
        'kota': user_data[5],
        'jalan': user_data[6],
        'tanggal_daftar': user_data[7]
    }

    # 3. Ambil Data Telepon Pasien (Bisa lebih dari 1)
    cur.execute("""
        SELECT telepon 
        FROM Pasien_telepon 
        JOIN Pasien ON Pasien.pasien_id = Pasien_telepon.pasien_id 
        WHERE Pasien.email = %s
    """, (email,))
    phones_data = cur.fetchall()
    
    # Ubah list of tuples [('081',), ('082',)] menjadi list biasa ['081', '082']
    phone_list = [p[0] for p in phones_data]
    
    cur.close()
    return render_template('profile.html', user=user_info, phones=phone_list)


@app.route('/appointmentHistory')
def appointment_history():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    email = session['email']
    cur = mysql.connection.cursor()
    
    # Query kompleks untuk join Appointment, Dokter, dan Rekam Medis (Left Join agar history tetap muncul meski belum ada rekam medis)
    cur.execute("""
        SELECT 
            a.appointment_id, 
            a.tanggal, 
            a.waktu, 
            a.status, 
            d.nama_depan, 
            d.nama_belakang,
            r.diagnosis,
            r.description
        FROM Appointment a
        JOIN Pasien p ON a.pasien_id = p.pasien_id
        JOIN Dokter d ON a.dokter_id = d.dokter_id
        LEFT JOIN Rekam_medis r ON a.appointment_id = r.appointment_id
        WHERE p.email = %s
        ORDER BY a.tanggal DESC, a.waktu DESC
    """, (email,))
    
    history_data = cur.fetchall()
    cur.close()
    
    # Format data menjadi list of dictionaries
    appointments = []
    for row in history_data:
        appointments.append({
            'id': row[0],
            'tanggal': row[1],
            'waktu': row[2],
            'status': row[3],
            'nama_dokter': f"{row[4]} {row[5]}",
            'diagnosis': row[6],
            'deskripsi': row[7]
        })
        
    return render_template('appointmentHistory.html', appointments=appointments)
        
# Modul Dokter 
@app.route('/jadwal/add', methods=['GET', 'POST'])
def add_jadwal_dokter():
    if request.method == 'POST':
        dokter_id = request.form['dokter_id']
        hari = request.form['hari']
        jam_mulai = request.form['jam_mulai']
        jam_selesai = request.form['jam_selesai']

        cur = mysql.connection.cursor()
        try:
            cur.execute(
                "INSERT INTO Jadwal_dokter (hari, jam_mulai, jam_selesai) VALUES (%s, %s, %s)",
                (hari, jam_mulai, jam_selesai)
            )

            jadwal_id = cur.lastrowid

            cur.execute(
                "INSERT INTO Dijadwalkan (dokter_id, jadwal_id) VALUES (%s, %s)",
                (dokter_id, jadwal_id)
            )

            mysql.connection.commit()
            flash("Jadwal berhasil ditambahkan", "success")
            return redirect(url_for('display_jadwal'))

        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error menambahkan jadwal: {str(e)}', 'error')
            return redirect(url_for('add_jadwal'))

        finally:
            try:
                cur.close()
            except:
                pass

    cur = mysql.connection.cursor()
    cur.execute("SELECT dokter_id, nama_depan FROM Dokter")
    dokter_list = cur.fetchall()
    cur.close()

    return render_template('addJadwalDokter.html', dokter_list=dokter_list)

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

@app.route('/dokter/home')
def dokter_home():
    if 'email' not in session:
        return redirect(url_for('login'))
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT nama_depan FROM Dokter WHERE email = %s", (session['email'],))
        row = cur.fetchone()
        cur.close()

        if not row:
            flash('Doctor profile not found.', 'error')
            return redirect(url_for('home'))

        nama = row[0]
        return render_template('homepageDokter.html', nama=nama)

    except Exception as e:
        flash(f'Error fetching doctor profile: {str(e)}', 'error')
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

# Modul Jadwal Dokter

@app.route('/jadwal')
def display_jadwal():
    if 'email' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    try:
        cur = mysql.connection.cursor()
        # JOIN untuk mendapatkan informasi dokter
        cur.execute("""
            SELECT j.jadwal_id, j.hari, j.jam_mulai, j.jam_selesai, 
                   d.dokter_id, d.nama_depan, d.nama_belakang
            FROM Jadwal_dokter j
            JOIN Dijadwalkan dj ON j.jadwal_id = dj.jadwal_id
            JOIN Dokter d ON dj.dokter_id = d.dokter_id
            ORDER BY j.jadwal_id
        """)
        data = cur.fetchall()
        cur.close()
        return render_template('displayJadwal.html', jadwal_list=data)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('home'))

@app.route('/jadwal/delete/<int:id>')
def delete_jadwal(id):
    if 'email' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    try:
        cur = mysql.connection.cursor()
        # CASCADE akan otomatis hapus di tabel Dijadwalkan
        cur.execute("DELETE FROM Jadwal_dokter WHERE jadwal_id = %s", (id,))
        mysql.connection.commit()
        cur.close()
        flash("Jadwal berhasil dihapus", "success")
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
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


    cur.execute("""
        SELECT d.dokter_id, j.hari, j.jam_mulai
        FROM Dijadwalkan d
        JOIN Jadwal_dokter j ON d.jadwal_id = j.jadwal_id
        WHERE d.jadwal_id = %s
    """, (jadwal_id,))
    
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
