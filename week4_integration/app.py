from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
pymysql.install_as_MySQLdb()
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from datetime import date, datetime
from MySQLdb.cursors import DictCursor 

load_dotenv()

app = Flask(__name__)
app.secret_key ='membuatLogin'

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT', 3306))


mysql = MySQL(app)

@app.route('/')
def home():
    cur = mysql.connection.cursor()
    cur.execute("SELECT dokter_id, nama_depan, nama_belakang, tanggal_masuk, status, foto FROM Dokter")
    doctors = cur.fetchall()
    cur.close()
    
    if 'email' in session:
        role = session.get('role')
        
        if role == 'resepsionis':
            # KHUSUS RESEPSIONIS: Pindah ke Dashboard Baru
            return redirect(url_for('homepageResepsionis'))
            
        elif role == 'dokter':
            # KHUSUS DOKTER: Pindah ke dashboard dokter (backend view)
            return redirect(url_for('dokter_dashboard'))
            
        elif role == 'pasien':
            # PASIEN: Tetap di halaman utama tapi mode login
            return render_template('home.html', email=session['email'], doctors=doctors)  
            
        # Default jika role tidak dikenali
        return render_template('home.html', email=session['email'], doctors=doctors)
    
    else:   
        # Jika belum login (Tamu)
        return render_template('home.html', doctors=doctors)
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        pwd = request.form['password']
        
        cur = mysql.connection.cursor()
        
        # --- 1. Pengecekan Pasien (Menggunakan HASH) ---
        cur.execute('SELECT pasien_id, email, password FROM Pasien WHERE email = %s', (email,))
        pasien = cur.fetchone()
        
        if pasien:
            # Pasien: Menggunakan check_password_hash karena didaftarkan melalui form /register
            if check_password_hash(pasien[2], pwd):
                session['email'] = pasien[1]
                session['role'] = 'pasien'
                session['id'] = pasien[0]
                cur.close()
                flash('Login successful!', 'success')
                return redirect(url_for('home')) 
        
        # --- 2. Pengecekan Resepsionis (Menggunakan PLAINTEXT) ---
        cur.execute('SELECT resepsionis_id, email, password FROM Resepsionis WHERE email = %s', (email,))
        resepsionis = cur.fetchone()
        
        if resepsionis:
            # Resepsionis: Menggunakan perbandingan string langsung (plaintext)
            if resepsionis[2] == pwd:
                session['email'] = resepsionis[1]
                session['role'] = 'resepsionis'
                session['id'] = resepsionis[0]
                cur.close()
                flash('Welcome Resepsionis!', 'success')
                return redirect(url_for('homepageResepsionis')) 

        # --- 3. Pengecekan Dokter (Menggunakan PLAINTEXT) ---
        cur.execute('SELECT dokter_id, email, password FROM Dokter WHERE email = %s', (email,))
        dokter = cur.fetchone()
        
        if dokter:
            # Dokter: Menggunakan perbandingan string langsung (plaintext)
            if dokter[2] == pwd:
                session['email'] = dokter[1]
                session['role'] = 'dokter'
                session['id'] = dokter[0]
                cur.close()
                flash('Welcome Doctor!', 'success')
                return redirect(url_for('dokter_dashboard'))

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
        cur.execute('insert into Pasien (email, password) values (%s, %s)', (email, hashed_password))
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
            
            cur.execute('SELECT pasien_id FROM Pasien WHERE email = %s', (email,))
            result = cur.fetchone()
            if not result:
                flash('User not found!', 'error')
                return redirect(url_for('login'))
            
            pasien_id = result[0]
            
            cur.execute('''
                UPDATE Pasien 
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


@app.route('/appointmentHistory', methods=['GET'])
def appointment_history():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    # 1. Ambil query pencarian dari parameter URL (misalnya: /appointmentHistory?search_query=flu)
    search_query = request.args.get('search_query', '').strip()
    
    email = session['email']
    cur = mysql.connection.cursor()
    
    # 2. Base SQL Query
    query = """
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
    """
    
    # List parameter untuk eksekusi query
    params = [email]
    
    # 3. Tambahkan filter pencarian jika query ada
    if search_query:
        search_term = f"%{search_query}%"
        # Mencari di Nama Dokter, Diagnosis, atau Deskripsi
        query += """
            AND (
                d.nama_depan LIKE %s OR 
                d.nama_belakang LIKE %s OR
                r.diagnosis LIKE %s OR
                r.description LIKE %s
            )
        """
        params.extend([search_term, search_term, search_term, search_term])
        
    # 4. Tambahkan pengurutan
    query += " ORDER BY a.tanggal DESC, a.waktu DESC"
    
    cur.execute(query, tuple(params))
    
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
        
    # 5. Kirim query pencarian kembali ke template untuk mempertahankan nilai input
    return render_template('appointmentHistory.html', appointments=appointments, search_query=search_query)
        
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


@app.route('/jadwal/edit/<int:id>', methods=['GET', 'POST'])
def edit_jadwal(id):
    if 'email' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    if request.method == 'POST':
        dokter_id = request.form['dokter_id']
        hari = request.form['hari']
        jam_mulai = request.form['waktu_mulai']
        jam_selesai = request.form['waktu_selesai']
        try:
            cur.execute("UPDATE Jadwal_dokter SET hari=%s, jam_mulai=%s, jam_selesai=%s WHERE jadwal_id=%s",
                        (hari, jam_mulai, jam_selesai, id))
            cur.execute("UPDATE Dijadwalkan SET dokter_id=%s WHERE jadwal_id=%s",
                        (dokter_id, id))
            mysql.connection.commit()
            flash('Jadwal berhasil diperbarui', 'success')
            return redirect(url_for('display_jadwal'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error updating schedule: {str(e)}', 'error')
            return redirect(url_for('display_jadwal'))

    # GET: fetch existing jadwal + dokter list
    cur.execute("SELECT j.jadwal_id, j.hari, j.jam_mulai, j.jam_selesai, d.dokter_id FROM Jadwal_dokter j JOIN Dijadwalkan dj ON j.jadwal_id = dj.jadwal_id JOIN Dokter d ON dj.dokter_id = d.dokter_id WHERE j.jadwal_id = %s", (id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        flash('Jadwal tidak ditemukan', 'error')
        return redirect(url_for('display_jadwal'))

    jadwal = {
        'jadwal_id': row[0],
        'hari': row[1],
        'jam_mulai': row[2],
        'jam_selesai': row[3],
        'dokter_id': row[4]
    }

    cur.execute("SELECT dokter_id, nama_depan, nama_belakang FROM Dokter")
    dokter_list = cur.fetchall()
    cur.close()

    return render_template('editJadwalDokter.html', jadwal=jadwal, dokter_list=dokter_list)

#Modul appoinment
HARI_MAP = {
    'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu', 
    'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'
}

# ---------------------------------------------------
# 1. ROUTE HALAMAN BOOKING (GET & POST)
# ---------------------------------------------------
@app.route('/booking', methods=['GET', 'POST'])
def book_appointment_form():
    # Cek Login Pasien
    if 'email' not in session or session.get('role') != 'pasien':
        flash('Silakan login sebagai pasien untuk membuat appointment.', 'error')
        return redirect(url_for('login'))

    pasien_id = session.get('id')

    # --- METHOD GET: TAMPILKAN FORM ---
    if request.method == 'GET':
        try:
            cur = mysql.connection.cursor(DictCursor)
            
            # Ambil List Dokter (Aktif)
            cur.execute("SELECT dokter_id, nama_depan, nama_belakang FROM Dokter")
            dokter_list = cur.fetchall()

            # Ambil List Jadwal (Join Dokter)
            cur.execute("""
                SELECT 
                    j.jadwal_id, j.hari, j.jam_mulai, j.jam_selesai, 
                    d.dokter_id, d.nama_depan, d.nama_belakang
                FROM Jadwal_dokter j
                JOIN Dijadwalkan dj ON j.jadwal_id = dj.jadwal_id
                JOIN Dokter d ON dj.dokter_id = d.dokter_id
                ORDER BY d.nama_depan, j.hari
            """)
            jadwal_list = cur.fetchall()
            cur.close()

            return render_template('bookAppointment.html', dokter_list=dokter_list, jadwal_list=jadwal_list)
        except Exception as e:
            flash(f'Error loading booking page: {str(e)}', 'error')
            return redirect(url_for('home'))

    # --- METHOD POST: PROSES BOOKING ---
    dokter_id = request.form.get('dokter_id')
    jadwal_id = request.form.get('jadwal_id') # Ini ID dari jadwal (Senin, 09:00)
    tanggal = request.form.get('tanggal')     # Ini Tanggal Kalender (2025-11-27)
    keluhan = request.form.get('complaint')   # Opsional

    # 1. Validasi Input Kosong
    if not dokter_id or not jadwal_id or not tanggal:
        flash('Dokter, jadwal, dan tanggal harus dipilih.', 'error')
        return redirect(url_for('book_appointment_form'))

    try:
        cur = mysql.connection.cursor(DictCursor)

        # 2. Ambil Info Jadwal berdasarkan ID
        cur.execute('SELECT hari, jam_mulai FROM Jadwal_dokter WHERE jadwal_id = %s', (jadwal_id,))
        jadwal_data = cur.fetchone()
        
        if not jadwal_data:
            flash('Jadwal tidak ditemukan.', 'error')
            return redirect(url_for('book_appointment_form'))

        jam_mulai = jadwal_data['jam_mulai']
        hari_praktek = jadwal_data['hari']

        # 3. Validasi: Apakah Tanggal yang dipilih sesuai dengan Hari Praktek?
        # Ubah string tanggal (YYYY-MM-DD) jadi object date
        date_obj = datetime.strptime(tanggal, '%Y-%m-%d')
        hari_dipilih_inggris = date_obj.strftime('%A') # Returns 'Monday'
        hari_dipilih_indo = HARI_MAP.get(hari_dipilih_inggris)

        if hari_dipilih_indo != hari_praktek:
            flash(f'Tanggal {tanggal} adalah hari {hari_dipilih_indo}, tapi jadwal dokter ini hari {hari_praktek}. Silakan pilih tanggal yang sesuai.', 'error')
            return redirect(url_for('book_appointment_form'))

        # 4. Validasi: Cek Slot Terisi (Double Booking Check)
        cur.execute("""
            SELECT appointment_id FROM Appointment 
            WHERE dokter_id = %s AND tanggal = %s AND waktu = %s AND status != 'cancelled'
        """, (dokter_id, tanggal, jam_mulai))
        
        if cur.fetchone():
            flash('Maaf, slot waktu/dokter tersebut sudah terisi di tanggal ini. Pilih tanggal lain.', 'warning')
            return redirect(url_for('book_appointment_form'))

        # 5. Insert ke Database
        # Status default 'scheduled' atau 'waiting' sesuai kesepakatan
        cur.execute("""
            INSERT INTO Appointment (pasien_id, dokter_id, jadwal_id, tanggal, waktu, status, keluhan) 
            VALUES (%s, %s, %s, %s, %s, 'waiting', %s)
        """, (pasien_id, dokter_id, jadwal_id, tanggal, jam_mulai, keluhan))
        
        mysql.connection.commit()
        cur.close()

        flash('Appointment berhasil dibuat!', 'success')
        return redirect(url_for('patient_dashboard')) # Lebih baik ke dashboard daripada form lagi

    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error saat membuat appointment: {str(e)}', 'error')
        return redirect(url_for('book_appointment_form'))


# ---------------------------------------------------
# 2. ROUTE DELETE APPOINTMENT (FIXED)
# ---------------------------------------------------
@app.route('/appointment/delete/<int:id>')
def delete_appointment(id):
    # Cek login
    if 'email' not in session:
        return redirect(url_for('login'))

    try:
        cur = mysql.connection.cursor()
        
        # OPSI A: Hard Delete (Hapus Permanen)
        cur.execute("DELETE FROM Appointment WHERE appointment_id=%s", (id,))
        
        # OPSI B: Soft Delete (Ubah Status jadi Cancelled) - Disarankan untuk Medis
        # cur.execute("UPDATE Appointment SET status='cancelled' WHERE appointment_id=%s", (id,))
        
        mysql.connection.commit()
        cur.close()

        flash("Appointment berhasil dibatalkan.", "success")
        
        # Redirect kembali ke halaman asal (Referrer)
        return redirect(request.referrer or url_for('display_appointment'))

    except Exception as e:
        flash(f"Gagal menghapus: {str(e)}", "error")
        return redirect(url_for('display_appointment'))


# ---------------------------------------------------
# 3. ROUTE DISPLAY ALL APPOINTMENTS (Admin/Debug)
# ---------------------------------------------------
@app.route('/appointment')
def display_appointment():
    # Sebaiknya gunakan DictCursor dan JOIN agar datanya terbaca manusia
    cur = mysql.connection.cursor(DictCursor)
    cur.execute("""
        SELECT 
            a.appointment_id, a.tanggal, a.waktu, a.status,
            CONCAT(p.nama_depan, ' ', p.nama_belakang) AS nama_pasien,
            CONCAT(d.nama_depan, ' ', d.nama_belakang) AS nama_dokter
        FROM Appointment a
        JOIN Pasien p ON a.pasien_id = p.pasien_id
        JOIN Dokter d ON a.dokter_id = d.dokter_id
        WHERE a.status IN ('booked', 'waiting', 'scheduled')
        ORDER BY a.tanggal DESC
    """)
    data = cur.fetchall()
    cur.close()
    return render_template('displayAppointment.html', app_list=data)

#Modul Rekam medis
# @app.route('/rekam/add/<int:appointment_id>', methods=['GET','POST'])
# def add_rekam(appointment_id):
#     if request.method == 'POST':
#         diagnosis = request.form['diagnosis']
#         desc = request.form['description']

#         cur = mysql.connection.cursor()
#         cur.execute("""
#             INSERT INTO Rekam_medis (appointment_id, diagnosis, description)
#             VALUES (%s, %s, %s)
#             ON DUPLICATE KEY UPDATE
#                 diagnosis=%s,
#                 description=%s
#         """, (appointment_id, diagnosis, desc, diagnosis, desc))

#         mysql.connection.commit()
#         cur.close()

#         flash("Rekam medis berhasil disimpan", "success")
#         return redirect(url_for('display_rekam'))

#     return render_template('dokterInputRekamMedis.html', appointment_id=appointment_id)

@app.route('/rekam')
def display_rekam():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Rekam_medis")
    data = cur.fetchall()
    cur.close()
    return render_template('displayRekam.html', rekam_list=data)

@app.route('/receptionist-dashboard')
@app.route('/receptionist-dashboard')
@app.route('/receptionist-dashboard')
def homepageResepsionis():
    # Cek keamanan: hanya role resepsionis yang boleh masuk
    if 'email' not in session or session.get('role') != 'resepsionis':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    # 1. Ambil Statistik: Appointment Hari Ini
    cur.execute("SELECT COUNT(*) FROM Appointment WHERE DATE(tanggal) = CURDATE()")
    today_appointments = cur.fetchone()[0]

    # ================= PERBAIKAN LOGIKA ACTIVE DOCTORS =================
    # Kita cari tahu hari ini hari apa dalam Bahasa Indonesia
    days_map = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    hari_ini = days_map[datetime.now().weekday()] # 0=Senin, 6=Minggu

    # Query: Hitung dokter yang punya jadwal di HARI INI
    query_active_docs = """
        SELECT COUNT(DISTINCT d.dokter_id)
        FROM Dokter d
        JOIN Dijadwalkan dj ON d.dokter_id = dj.dokter_id
        JOIN Jadwal_dokter j ON dj.jadwal_id = j.jadwal_id
        WHERE j.hari = %s
    """
    cur.execute(query_active_docs, (hari_ini,))
    active_doctors = cur.fetchone()[0]
    # ===================================================================

    # 3. Ambil Data Appointment Lengkap (Join Pasien & Dokter)
    query = """
        SELECT 
            a.appointment_id, 
            p.nama_depan AS pasien_depan, 
            p.nama_belakang AS pasien_belakang,
            p.email AS pasien_email,
            d.nama_depan AS dokter_depan, 
            d.nama_belakang AS dokter_belakang,
            a.tanggal, 
            a.waktu, 
            a.status
        FROM Appointment a
        JOIN Pasien p ON a.pasien_id = p.pasien_id
        JOIN Dokter d ON a.dokter_id = d.dokter_id
        WHERE a.tanggal >= CURDATE() -- Opsional: Hanya tampilkan hari ini ke depan
        ORDER BY a.tanggal ASC, a.waktu ASC
    """
    cur.execute(query)
    appointments_data = cur.fetchall()
    cur.close()

    # Format data untuk HTML
    appointments_list = []
    for row in appointments_data:
        appointments_list.append({
            'id': row[0],
            'patient_name': f"{row[1]} {row[2]}",
            'patient_contact': row[3],
            'doctor_name': f"Dr. {row[4]} {row[5]}",
            'date': row[6],
            'time': row[7],
            'status': row[8]
        })

    return render_template('homepageReceptionist.html', 
                           appointments=appointments_list,
                           today_count=today_appointments,
                           active_docs=active_doctors) # Kirim hasil hitungan baru
# --- ROUTE EDIT PROFIL RESEPSIONIS ---
# --- ROUTE KHUSUS EDIT PROFIL RESEPSIONIS ---
@app.route('/resepsionis/profile', methods=['GET', 'POST'])
def edit_resepsionis_profile():
    # 1. Cek Login & Role
    if 'email' not in session or session.get('role') != 'resepsionis':
        return redirect(url_for('login'))
    
    email = session['email']
    cur = mysql.connection.cursor()
    
    # 2. Handle Update Data (POST)
    if request.method == 'POST':
        nama_depan = request.form['nama_depan']
        nama_belakang = request.form['nama_belakang']
        
        try:
            # Update Nama ke Tabel Resepsionis
            cur.execute("""
                UPDATE Resepsionis 
                SET nama_depan = %s, nama_belakang = %s 
                WHERE email = %s
            """, (nama_depan, nama_belakang, email))
            mysql.connection.commit()
            
            # Update Session agar nama di pojok kanan dashboard langsung berubah
            session['nama_depan'] = nama_depan
            
            flash('Profile successfully updated!', 'success')
            return redirect(url_for('edit_resepsionis_profile'))
            
        except Exception as e:
            flash(f'Error updating profile: {str(e)}', 'error')

    # 3. Handle Tampilan Awal (GET)
    # Kita cari data di tabel RESEPSIONIS, bukan Pasien
    cur.execute("SELECT nama_depan, nama_belakang, tanggal_masuk FROM Resepsionis WHERE email = %s", (email,))
    data = cur.fetchone()
    cur.close()

    if data:
        resepsionis_data = {
            'nama_depan': data[0],
            'nama_belakang': data[1],
            'tanggal_masuk': data[2]
        }
        # Pastikan file HTML ini sudah kamu buat (editProfileResepsionis.html)
        return render_template('editProfileResepsionis.html', resepsionis=resepsionis_data)
    else:
        return redirect(url_for('login'))
    
    # --- FITUR BOOKING KHUSUS RESEPSIONIS ---
@app.route('/receptionist/book', methods=['GET', 'POST'])
@app.route('/receptionist/book', methods=['GET', 'POST'])
def receptionist_book_appointment():
    if 'email' not in session or session.get('role') != 'resepsionis':
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        # ... (Bagian POST Simpan Data TETAP SAMA seperti sebelumnya) ...
        pasien_id = request.form['pasien_id']
        jadwal_id = request.form['jadwal_id']
        
        cur.execute("""
            SELECT d.dokter_id, j.hari, j.jam_mulai
            FROM Dijadwalkan d
            JOIN Jadwal_dokter j ON d.jadwal_id = j.jadwal_id
            WHERE d.jadwal_id = %s
        """, (jadwal_id,))
        jadwal_data = cur.fetchone()
        
        if jadwal_data:
            dokter_id, hari, jam_mulai = jadwal_data
            
            cur.execute("""
                INSERT INTO Appointment (pasien_id, dokter_id, jadwal_id, tanggal, waktu, status)
                VALUES (%s, %s, %s, CURDATE(), %s, 'booked')
            """, (pasien_id, dokter_id, jadwal_id, jam_mulai))
            
            mysql.connection.commit()
            flash('Appointment successfully created for patient!', 'success')
            cur.close()
            return redirect(url_for('homepageResepsionis'))
            
    # --- BAGIAN INI YANG BERUBAH (GET) ---
    
    # 1. Ambil List Pasien
    cur.execute("SELECT pasien_id, nama_depan, nama_belakang, email FROM Pasien")
    patients = cur.fetchall()
    
    # 2. Ambil List Jadwal Dokter YANG TERSEDIA (Available)
    # Kita filter menggunakan 'NOT IN'
    # Artinya: Ambil jadwal yang ID-nya TIDAK ADA di tabel Appointment dengan tanggal hari ini
    cur.execute("""
        SELECT j.jadwal_id, d.nama_depan, d.nama_belakang, j.hari, j.jam_mulai, j.jam_selesai
        FROM Jadwal_dokter j
        JOIN Dijadwalkan dj ON j.jadwal_id = dj.jadwal_id
        JOIN Dokter d ON dj.dokter_id = d.dokter_id
        WHERE j.jadwal_id NOT IN (
            SELECT jadwal_id FROM Appointment WHERE tanggal = CURDATE()
        )
        ORDER BY j.hari, j.jam_mulai
    """)
    schedules = cur.fetchall()
    cur.close()

    return render_template('bookAppointmentResepsionis.html', patients=patients, schedules=schedules)

#Modul Dokter

@app.route('/dokter/dashboard')
def dokter_dashboard():
    # if 'email' not in session or session.get('role') != 'dokter':
    #     return redirect(url_for('login'))
    
    cur = mysql.connection.cursor(DictCursor)
    dokter_id_session = session.get('id')

    #ambil nama dokter
    cur.execute("""
        SELECT nama_depan AS nama 
        FROM Dokter 
        WHERE dokter_id = %s
    """, (dokter_id_session,))
    
    res_dokter = cur.fetchone()
    nama_dokter = res_dokter['nama'] if res_dokter else "Dokter"

    #for statistik
    stats = {}
    
    # Total
    cur.execute("""
        SELECT COUNT(*) AS total 
        FROM Appointment 
        WHERE dokter_id = %s
    """, (dokter_id_session,))
    stats['total_appointments'] = cur.fetchone()['total']

    # Hari Ini
    cur.execute("""
        SELECT COUNT(*) AS total 
        FROM Appointment 
        WHERE dokter_id = %s AND tanggal = CURDATE()
    """, (dokter_id_session,))
    stats['today_appointments'] = cur.fetchone()['total']

    # Upcoming
    cur.execute("""
        SELECT COUNT(*) AS total 
        FROM Appointment 
        WHERE dokter_id = %s AND tanggal > CURDATE()
    """, (dokter_id_session,))
    stats['upcoming_appointments'] = cur.fetchone()['total']

    #Jadwal Dokter
    query_jadwal = """
        SELECT 
            j.hari, 
            j.jam_mulai, 
            j.jam_selesai 
        FROM Jadwal_dokter j
        JOIN Dijadwalkan d ON j.jadwal_id = d.jadwal_id
        WHERE d.dokter_id = %s
        GROUP BY j.hari, j.jam_mulai, j.jam_selesai
        ORDER BY FIELD(j.hari, 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'), j.jam_mulai
    """
    cur.execute(query_jadwal, (dokter_id_session,))
    jadwal_saya = cur.fetchall()

    #Appointment Hari Ini
    query_appt = """
        SELECT 
            CONCAT(p.nama_depan, ' ', p.nama_belakang) AS nama, 
            a.waktu, 
            a.status, 
            a.appointment_id 
        FROM Appointment a
        JOIN Pasien p ON a.pasien_id = p.pasien_id
        WHERE a.dokter_id = %s AND a.tanggal = CURDATE()
        ORDER BY a.waktu ASC
    """
    cur.execute(query_appt, (dokter_id_session,))
    appointments_today = cur.fetchall()

    query = """
        SELECT jd.jadwal_id as jadwal_id, jd.hari, jd.jam_mulai, jd.jam_selesai
        FROM Jadwal_dokter jd
        JOIN Dijadwalkan dj ON jd.jadwal_id = dj.jadwal_id
        WHERE dj.dokter_id = %s
        ORDER BY FIELD(jd.hari, 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'), jd.jam_mulai
    """
    cur.execute(query, (dokter_id_session,))
    jadwal_data = cur.fetchall()
    jadwal_list = []
    if jadwal_data:
        for row in jadwal_data:
            jadwal_list.append({
                'jadwal_id': row['jadwal_id'],   
                'hari': row['hari'],
                'jam_mulai': str(row['jam_mulai']), 
                'jam_selesai': str(row['jam_selesai'])
            })

    cur.close()

    return render_template('newHomepageDokter.html', 
                           nama=nama_dokter,
                           stats=stats,
                           jadwal_saya=jadwal_saya,
                           appointments_today=appointments_today,
                           jadwal_list=jadwal_list)

#########################################################

@app.route('/dokter/jadwal')
def view_jadwal_dokter():
    if 'id' not in session:
        return redirect(url_for('login_dokter'))

    dokter_id_session = session.get('id')
    cur = mysql.connection.cursor()
    
    # Query tetap sama
    query = """
        SELECT jd.jadwal_id, jd.hari, jd.jam_mulai, jd.jam_selesai
        FROM Jadwal_dokter jd
        JOIN Dijadwalkan dj ON jd.jadwal_id = dj.jadwal_id
        WHERE dj.dokter_id = %s
        ORDER BY FIELD(jd.hari, 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'), jd.jam_mulai
    """
    cur.execute(query, (dokter_id_session,))
    jadwal_data = cur.fetchall()
    cur.close()

    jadwal_list = []
    if jadwal_data:
        for row in jadwal_data:
            jadwal_list.append({
                'jadwal_id': row[0],       
                'hari': row[1],            
                'jam_mulai': str(row[2]),  
                'jam_selesai': str(row[3]) 
            })

    return render_template('dokterJadwal.html', jadwal_list=jadwal_list)
################################################################
@app.route('/dokter/jadwal/add', methods=['POST'])
def dokter_add_jadwal():

    cur = mysql.connection.cursor()
    dokter_id_session = session.get('id')

    if request.method == 'POST':
        hari = request.form['hari']
        jam_mulai = request.form['jam_mulai']
        jam_selesai = request.form['jam_selesai']

        try:
            cur.execute("""
                INSERT INTO Jadwal_dokter (hari, jam_mulai, jam_selesai)
                VALUES (%s, %s, %s)
            """, (hari, jam_mulai, jam_selesai))
            jadwal_id = cur.lastrowid  

            # Insert ke Dijadwalkan
            cur.execute("""
                INSERT INTO Dijadwalkan (dokter_id, jadwal_id)
                VALUES (%s, %s)
            """, (dokter_id_session, jadwal_id))

            mysql.connection.commit()
            cur.close()

            flash('Jadwal berhasil ditambahkan!', 'success')
            return redirect(url_for('dokter_homepage'))

        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error menambahkan jadwal: {str(e)}', 'error')
    
    return redirect(url_for('dokter_dashboard'))

@app.route('/dokter/jadwal/delete', methods=['POST'])
def dokter_delete_jadwal():
    cur = mysql.connection.cursor()
    dokter_id_session = session.get('id')

    if request.method == 'POST':
        jadwal_id = request.form['jadwal_id']

        try:
            # Hapus dari Dijadwalkan terlebih dahulu
            cur.execute("""
                DELETE FROM Dijadwalkan 
                WHERE dokter_id = %s AND jadwal_id = %s
            """, (dokter_id_session, jadwal_id))

            # Hapus dari Jadwal_dokter
            cur.execute("""
                DELETE FROM Jadwal_dokter 
                WHERE jadwal_id = %s
            """, (jadwal_id,))

            mysql.connection.commit()
            cur.close()

            flash('Jadwal berhasil dihapus!', 'success')
            return redirect(url_for('dokter_homepage'))

        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error menghapus jadwal: {str(e)}', 'error')
    
    return redirect(url_for('dokter_dashboard'))

#############################################################
@app.route('/dokter/appoinment')
def dokter_appointment_list():
    if 'id' not in session:
        return redirect(url_for('login_dokter'))

    id_dokter = session.get('id')
    
    # 2. Ambil tanggal (Default hari ini)
    tanggal_pilih = request.args.get('date')
    if not tanggal_pilih:
        tanggal_pilih = date.today()

    cur = mysql.connection.cursor()

    query = """
        SELECT 
            a.appointment_id,                         
            a.waktu,                                   
            CONCAT(p.nama_depan, ' ', p.nama_belakang), 
            p.pasien_id,                              
            a.status                                   
        FROM Appointment a
        JOIN Pasien p ON a.pasien_id = p.pasien_id
        WHERE a.dokter_id = %s AND a.tanggal = %s
        ORDER BY a.waktu ASC
    """

    cur.execute(query, (id_dokter, tanggal_pilih))
    raw_appointments = cur.fetchall()
    cur.close()

    appointments_list = []
    
    if raw_appointments:
        for row in raw_appointments:
            appointments_list.append({
                'id': row[0],             
                'jam_janji': str(row[1]),
                'nama_pasien': row[2],    
                'no_rm': f"ID-{row[3]}",  
                'keluhan': "-",           
                'pasien_id': row[3],      
                'status': row[4]          
            })

    return render_template(
        'dokterAppointment.html', 
        appointments=appointments_list, 
        tanggal_hari_ini=tanggal_pilih
    )

@app.route('/dokter/pasien')
# def dokter_pasien_list():

#     return render_template('dokterPasien.html')

@app.route('/dokter/rekam_medis')
# def dokter_rekam_medis_list():

#     return render_template('dokterRekamMedis.html')

@app.route('/dokter/pasien/detail/<int:id_pasien>/<int:id_appt>')
def dokter_pasien_detail(id_pasien, id_appt):
    # 1. Cek Login
    if 'email' not in session or session.get('role') != 'dokter':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor(DictCursor)

    # --- A. QUERY DATA PASIEN (Profil) ---
    query_pasien = """
        SELECT 
            p.pasien_id,
            CONCAT(p.nama_depan, ' ', p.nama_belakang) AS nama_lengkap,
            p.gender,
            TIMESTAMPDIFF(YEAR, p.tanggal_lahir, CURDATE()) AS umur,
            p.Jalan,
            p.Kota,
            pt.telepon
        FROM Pasien p
        LEFT JOIN Pasien_telepon pt ON p.pasien_id = pt.pasien_id
        WHERE p.pasien_id = %s
    """
    cur.execute(query_pasien, (id_pasien,))
    pasien_data = cur.fetchone()

    # --- B. QUERY DETAIL APPOINTMENT ---
    # SAYA UBAH QUERY-NYA: Tambahkan DATE_FORMAT agar key 'tanggal_cantik' tersedia
    query_appt = """
        SELECT 
            appointment_id,
            tanggal as tanggal_cantik,  -- Biar key dictionary jalan
            waktu as waktu_cantik,        -- Biar key dictionary jalan
            status
        FROM Appointment
        WHERE appointment_id = %s
    """
    cur.execute(query_appt, (id_appt,))
    appointment_data = cur.fetchone()

    # --- C. QUERY RIWAYAT ---
    query_history = """
        SELECT 
            r.diagnosis, 
            r.description, 
            a.tanggal as tanggal,
            CONCAT(d.nama_depan, ' ', d.nama_belakang) AS nama_dokter
        FROM Rekam_medis r
        JOIN Appointment a ON r.appointment_id = a.appointment_id
        JOIN Dokter d ON a.dokter_id = d.dokter_id
        WHERE a.pasien_id = %s AND a.appointment_id != %s
        ORDER BY a.tanggal DESC
    """
    cur.execute(query_history, (id_pasien, id_appt))
    riwayat_medis = cur.fetchall()

    cur.close()

    if not pasien_data:
        return "Data Pasien tidak ditemukan."

    # --- D. PERBAIKAN DICTIONARY ---
    # Perhatikan: Saya ganti 'pasien' jadi 'pasien_data' dan 'appt' jadi 'appointment_data'
    detail_data = {
        'nama': pasien_data['nama_lengkap'],        
        'gender': pasien_data['gender'],            
        'umur': pasien_data['umur'], 
        'telepon': pasien_data.get('telepon', '-'), # Tambahan biar lengkap
        
        'status': appointment_data['status'],             
        'tgl_periksa': appointment_data['tanggal_cantik'], # Key ini sekarang ada karena query B diubah
        'waktu': appointment_data['waktu_cantik'],         
        
        'diagnosis': 'Belum Diperiksa',       
        'deskripsi': 'Silakan input rekam medis baru.' 
    }
    
    return render_template('dokterPasienDetail.html', 
                           detail=detail_data,
                           riwayat=riwayat_medis, 
                           id_pasien=id_pasien,
                           id_appt=id_appt)

##############################################################
@app.route('/dokter/input_rekam_medis/<int:id>', methods=['GET', 'POST'])
def dokter_input_rekam_medis(id):
    
    # 1. Cek Login
    if 'id' not in session:
        return redirect(url_for('login_dokter'))
    
    cur = mysql.connection.cursor()
    query = """
        SELECT 
            a.appointment_id,
            a.tanggal,
            p.nama_depan, 
            p.nama_belakang,
            p.gender,
            p.tanggal_lahir,
            p.pasien_id
        FROM Appointment a
        JOIN Pasien p ON a.pasien_id = p.pasien_id
        WHERE a.appointment_id = %s
    """
    cur.execute(query, (id,))
    data = cur.fetchone()

    # Validasi jika data tidak ada
    if not data:
        cur.close()
        flash('Data appointment tidak ditemukan.', 'error')
        return redirect(url_for('dokter_appointment_list'))

    # Hitung Umur
    tgl_lahir = data[5]
    umur = (date.today() - tgl_lahir).days // 365 if tgl_lahir else 0

    # Bungkus data ke dalam Dictionary
    pasien_data = {
        'id': data[0],              # appointment_id
        'tanggal': data[1],
        'nama_pasien': f"{data[2]} {data[3]}", 
        'gender': data[4],
        'umur': umur,
        'pasien_id': data[6]
    }

    # --- LANGKAH 2: LOGIKA SIMPAN (POST) ---
    if request.method == 'POST':
        diagnosis = request.form['diagnosis']
        description = request.form['description']
        
        try:
            # Insert ke Rekam Medis
            cur.execute("""
                INSERT INTO Rekam_medis (diagnosis, description, appointment_id)
                VALUES (%s, %s, %s)
            """, (diagnosis, description, id))
            
            # Update Status Appointment
            cur.execute("""
                UPDATE Appointment 
                SET status = 'Selesai' 
                WHERE appointment_id = %s
            """, (id,))
            
            mysql.connection.commit()
            cur.close()
            
            flash('Rekam medis berhasil disimpan!', 'success')
            return redirect(url_for('dokter_appointment_list'))
            
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Gagal menyimpan: {str(e)}', 'error')
            # Jika error, kode lanjut ke bawah (render_template)
            # Inputan dokter tidak hilang karena halaman tidak direfresh total

    # --- LANGKAH 3: RENDER TEMPLATE ---
    cur.close()
    
    # Pastikan nama file HTML sesuai dengan yang Anda buat
    return render_template('dokterInputRekamMedis.html', 
                           pasien=pasien_data, 
                           tanggal_skrg=date.today().strftime('%d %B %Y')
    )

###############################################################################
@app.route('/dokter/profile/edit', methods=['GET', 'POST'])
def dokter_edit_profile():
    if 'id' not in session:
        return redirect(url_for('login_dokter'))

    cur = mysql.connection.cursor()
    dokter_id_session = session.get('id')

    if request.method == 'GET':
        query = """
            SELECT 
                d.nama_depan, 
                d.nama_belakang, 
                d.status, 
                d.tanggal_masuk,
                dt.telepon
            FROM Dokter d
            LEFT JOIN Dokter_telepon dt ON d.dokter_id = dt.dokter_id
            WHERE d.dokter_id = %s
            LIMIT 1
        """
        cur.execute(query, (dokter_id_session,))
        data = cur.fetchone()
        cur.close()

        if data:
            dokter_data = {
                'nama_depan': data[0],
                'nama_belakang': data[1],
                'status': data[2],
                'tanggal_masuk': data[3],
                'telepon': data[4] if data[4] else '' 
            }
            return render_template('dokterEditProfile.html', dokter=dokter_data)
        else:
            return redirect(url_for('login_dokter'))

    if request.method == 'POST':
        nama_depan = request.form['nama_depan']
        nama_belakang = request.form['nama_belakang']
        telepon = request.form['telepon'] 
        
        try:
            cur.execute("""
                UPDATE Dokter 
                SET nama_depan = %s, nama_belakang = %s 
                WHERE dokter_id = %s
            """, (nama_depan, nama_belakang, dokter_id_session))
            
            cur.execute("DELETE FROM Dokter_telepon WHERE dokter_id = %s", (dokter_id_session,))

            if telepon:
                cur.execute("""
                    INSERT INTO Dokter_telepon (telepon, dokter_id)
                    VALUES (%s, %s)
                """, (telepon, dokter_id_session))

            mysql.connection.commit()
            cur.close()
            
            # 3. Update Session (Penting biar nama di navbar berubah)
            session['nama_depan'] = nama_depan
            
            flash('Profile successfully updated!', 'success')
            return redirect(url_for('dokter_edit_profile'))
            
        except Exception as e:
            mysql.connection.rollback()
            cur.close()
            flash(f'Error updating profile: {str(e)}', 'error')
            return redirect(url_for('dokter_edit_profile'))

if __name__ == '__main__':
    app.run(debug=True)
