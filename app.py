from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'printer_toner_db'
app.config['MYSQL_UNIX_SOCKET'] = '/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock'

# Session config
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

mysql = MySQL(app)


# ---------- AUTH ROUTES ---------- #

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # Generate hashed password using pbkdf2:sha256 (since scrypt not supported on your Python build)
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Insert user into database
        cur.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                    (username, hashed_password, role))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('login'))

    return render_template('signup.html')


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Fetch user by username
        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            return redirect(url_for('home'))
        else:
            return "Invalid credentials"

    return render_template('login.html')



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ---------- MAIN ROUTES ---------- #

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')


@app.route('/request-toner', methods=['GET', 'POST'])
def request_toner():
    # if 'role' not in session or session['role'] != 'user':
    #     return "Unauthorized Access", 403

    if request.method == 'POST':
        department = request.form['department']
        printer_model = request.form['printerModel']
        toner_type = request.form['tonerType']
        requested_by = request.form['requestedBy']

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO toner_requests (department, printer_model, toner_type, requested_by)
            VALUES (%s, %s, %s, %s)
        """, (department, printer_model, toner_type, requested_by))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('home'))

    return render_template('request_toner.html')


@app.route('/view-requests')
def view_requests():
    if 'role' not in session or session['role'] != 'admin':
        return "Unauthorized Access", 403
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM toner_requests ORDER BY request_date DESC")
    requests = cur.fetchall()
    cur.close()
    return render_template('view_requests.html', requests=requests)


@app.route('/view-stock')
def view_stock():
    if 'role' not in session or session['role'] != 'admin':
        return "Unauthorized Access", 403
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM cartridge_stock")
    stock = cur.fetchall()

    cur.execute("SELECT DISTINCT printer_model_no FROM cartridge_stock")
    models_data = cur.fetchall()
    models = [model[0] for model in models_data]

    cur.close()
    return render_template('view_stock.html', stock=stock, models=models)


@app.route('/add-stock', methods=['GET', 'POST'])
def add_stock():
    if 'role' not in session or session['role'] != 'admin':
        return "Unauthorized Access", 403
    if request.method == 'POST':
        printer_model_no = request.form['printerModel']
        cartridge_no = request.form['cartridgeNo']
        quantity = int(request.form['quantity'])
        issue_to = request.form.get('issueTo', 'None')
        damaged = int(request.form['damaged'])

        cur = mysql.connection.cursor()

        cur.execute("""
            INSERT INTO cartridge_stock 
            (printer_model_no, cartridge_no, quantity, issue_to, damaged, total_stock)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                quantity = quantity + VALUES(quantity),
                total_stock = total_stock + VALUES(total_stock)
        """, (printer_model_no, cartridge_no, quantity, issue_to, damaged, quantity))

        mysql.connection.commit()
        cur.close()

        return redirect(url_for('view_stock'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT DISTINCT printer_model_no FROM cartridge_stock")
    printer_models = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT DISTINCT cartridge_no FROM cartridge_stock")
    cartridge_nos = [row[0] for row in cur.fetchall()]

    cur.close()
    return render_template('add_stock.html', printer_models=printer_models, cartridge_nos=cartridge_nos)


@app.route('/issue-cartridge', methods=['GET', 'POST'])
def issue_cartridge():
    if 'role' not in session or session['role'] != 'admin':
        return "Unauthorized Access", 403
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        employee_name = request.form['employeeName']
        printer_model_no = request.form['printerModel']
        cartridge_no = request.form['cartridgeNo']
        quantity = int(request.form['quantity'])

        cur.execute("""
            INSERT INTO cartridge_issue 
            (employee_name, printer_model_no, cartridge_no, quantity_issued)
            VALUES (%s, %s, %s, %s)
        """, (employee_name, printer_model_no, cartridge_no, quantity))

        cur.execute("""
            UPDATE cartridge_stock 
            SET total_stock = total_stock - %s
            WHERE printer_model_no = %s AND cartridge_no = %s AND total_stock >= %s
        """, (quantity, printer_model_no, cartridge_no, quantity))

        mysql.connection.commit()
        cur.close()

        return redirect(url_for('view_stock'))

    cur.execute("SELECT DISTINCT printer_model_no FROM cartridge_stock")
    printer_models = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT DISTINCT cartridge_no FROM cartridge_stock")
    cartridge_nos = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT employee_name FROM employees")
    employees = [row[0] for row in cur.fetchall()]

    cur.close()
    return render_template('issue_cartridge.html',
                           printer_models=printer_models,
                           cartridge_nos=cartridge_nos,
                           employees=employees)


@app.route('/issued-cartridges')
def issued_cartridges():
    if 'role' not in session or session['role'] != 'admin':
        return "Unauthorized Access", 403
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT id, employee_name, printer_model_no, cartridge_no, quantity_issued, issue_date 
        FROM cartridge_issue
        ORDER BY issue_date DESC
    """)
    issued_list = cur.fetchall()

    cur.close()
    return render_template('issued_cartridges.html', issued_list=issued_list)


if __name__ == "__main__":
    app.run(debug=True, port=5002)
