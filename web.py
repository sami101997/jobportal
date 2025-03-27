from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = "your_secret_key"  # For flash messages

# ✅ Ensure the database and users table exist
def initialize_database():

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        job_type TEXT NOT NULL,
        salary INTEGER,
        location TEXT NOT NULL,
        description TEXT NOT NULL
    );
    ''')
    conn.commit()
    conn.close()

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL,
        user_type TEXT NOT NULL
    );
    ''')
    conn.commit()
    conn.close()


      
# 📝 Registration Page
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        print(request.form)  # Debug: Print received form data

        name = request.form['name']
        email = request.form['email']
        create_password = request.form['create_password']
        confirm_password = request.form['confirm_password']
        user_type = request.form.get('user_type', 'user')  # Default to 'user'

        if create_password != confirm_password:
            flash("❌ Passwords do not match!", "danger")
            return redirect(url_for('registration'))

        hashed_password = hashlib.sha256(create_password.encode()).hexdigest()

        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()

            cursor.execute("INSERT INTO users (name, email, password, user_type) VALUES (?, ?, ?, ?)",
                           (name, email, hashed_password, user_type))

            conn.commit()
            conn.close()

            flash("✅ Registration Successful!", "success")
            return redirect(url_for('signin'))

        except sqlite3.IntegrityError:
            flash("❌ Error: Email already exists!", "danger")
            return redirect(url_for('registration'))  # ✅ Added return statement

    return render_template('registration.html')


# 🔑 Signin Page
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Fetch user by email
        cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user:
            stored_password = user[0]
            entered_password = hashlib.sha256(password.encode()).hexdigest()

            if stored_password == entered_password:
                flash("✅ Signin Successful!", "success")
                return redirect(url_for('home_page'))
            else:
                flash("❌ Invalid Credentials!", "danger")
        else:
            flash("❌ No account found with this email!", "danger")

        return redirect(url_for('signin'))

    return render_template('signin.html')

@app.route('/post_job', methods=['GET', 'POST'])
def post_job():
    if request.method == 'POST':
        job_title = request.form['title']
        company = request.form['company']
        job_type = request.form['job_type']
        salary = request.form['salary']
        location = request.form['location']
        description = request.form['description']

        # Save job data into the database
        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO jobs (title, company, job_type, salary, location, description) VALUES (?, ?, ?, ?, ?, ?)", 
                           (job_title, company, job_type, salary, location, description))
            conn.commit()
            conn.close()

            flash("✅ Job Posted Successfully!", "success")
            return redirect(url_for('home_page'))  # Redirect to home or jobs page

        except sqlite3.Error as e:
            flash(f"❌ Error: {e}", "danger")

    return render_template('post_job.html')

@app.route('/apply')
def apply():
    return render_template('apply.html')


# 🏠 Home Page
@app.route('/')
def home_page():
    return render_template('welcome.html')


if __name__ == '__main__':
    initialize_database()  # ✅ Ensure the database is set up before running
    app.run(debug=True)
