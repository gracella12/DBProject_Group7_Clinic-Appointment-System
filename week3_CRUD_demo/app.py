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
        telepon_list = request.form.getlist('telepon[]')  # Get all phone numbers
        email = session['email']
        
        try:
            cur = mysql.connection.cursor()
            
            # Get pasien_id
            cur.execute('SELECT pasien_id FROM pasien WHERE email = %s', (email,))
            result = cur.fetchone()
            if not result:
                flash('User not found!', 'error')
                return redirect(url_for('login'))
            
            pasien_id = result[0]
            
            # Update pasien data
            cur.execute('''
                UPDATE pasien 
                SET nama_depan = %s, nama_belakang = %s, gender = %s, 
                    tanggal_lahir = %s, Kota = %s, Jalan = %s 
                WHERE email = %s
            ''', (nama_depan, nama_belakang, gender, tanggal_lahir, kota, jalan, email))
            
            # Delete existing phone numbers
            cur.execute('DELETE FROM Pasien_telepon WHERE pasien_id = %s', (pasien_id,))
            
            # Insert new phone numbers (filter out empty values)
            for telepon in telepon_list:
                telepon = telepon.strip()
                if telepon:  # Only insert non-empty phone numbers
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
        cur.execute('DELETE FROM pasien WHERE pasien_id = (SELECT pasien_id FROM pasien WHERE email = %s)', (email,))
        cur.execute('DELETE FROM pasien WHERE email = %s', (email,))
        mysql.connection.commit()
        cur.close()

        session.pop('email', None)
        flash('Your account has been deleted successfully.', 'info')
        return redirect(url_for('home'))
    except Exception as e:
        flash(f'Error deleting account: {str(e)}', 'error')
        return redirect(url_for('editProfile'))

if __name__ == '__main__':
    app.run(debug=True)